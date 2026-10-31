#!/usr/bin/env python3
"""
with_server.py — Gestor de ciclo de vida de servidores para automatizaciones Playwright.

Arranca uno o varios servidores, espera a que cada puerto esté escuchando, ejecuta el
comando que le pases (normalmente tu script Playwright) y, al terminar, apaga TODOS los
servidores limpiamente — pase lo que pase (éxito, fallo o Ctrl-C).

Pensado para usarse como CAJA NEGRA: no hace falta leer el código, solo `--help`.

USO
────────────────────────────────────────────────────────────────────────────
Un servidor:
  python scripts/with_server.py --server "npm run dev" --port 5173 -- python mi_automatizacion.py

Varios servidores (backend + frontend):
  python scripts/with_server.py \
    --server "cd backend && python server.py" --port 3000 \
    --server "cd frontend && npm run dev"     --port 5173 \
    -- python mi_automatizacion.py

Todo lo que va DESPUÉS de `--` es el comando a ejecutar con los servidores ya listos.

OPCIONES
────────────────────────────────────────────────────────────────────────────
  --server CMD     Comando de arranque del servidor (repetible). Se ejecuta con shell,
                   así que admite `cd x && ...`, pipes, variables de entorno, etc.
  --port N         Puerto que ese servidor debe abrir (repetible, 1 por --server, en orden).
  --host H         Host donde comprobar los puertos (default: 127.0.0.1).
  --timeout SEG    Segundos máximos de espera a que cada puerto abra (default: 60).
  --ready-path P   Ruta HTTP opcional (p.ej. /health) que debe devolver <500 antes de
                   considerar el server listo. Si se omite, basta con que el puerto escuche.
  -- CMD...        Comando a ejecutar una vez todos los servidores están listos.

CÓDIGO DE SALIDA
────────────────────────────────────────────────────────────────────────────
  Devuelve el código de salida del comando envuelto. Si un servidor no llega a
  escuchar en su puerto dentro de --timeout, sale con código 1 sin lanzar el comando.

NOTA (entorno cloud): para HTML estáticos / monolitos NO necesitas este script —
usa file:// directamente con Playwright. Este helper es solo para apps dinámicas
(npm run dev, vite, servidores Python, Supabase local, etc.).
"""
import argparse
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request


def log(msg):
    print(f"[with_server] {msg}", file=sys.stderr, flush=True)


def port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


def http_ready(host, port, path):
    url = f"http://{host}:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status < 500
    except urllib.error.HTTPError as e:
        # Un 4xx significa que el server responde: está vivo.
        return e.code < 500
    except Exception:
        return False


def wait_ready(host, port, timeout, ready_path, proc):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            log(f"❌ El servidor murió antes de abrir el puerto {port} (exit {proc.returncode}).")
            return False
        if port_open(host, port):
            if ready_path is None or http_ready(host, port, ready_path):
                return True
        time.sleep(0.4)
    return False


def start_server(cmd):
    # start_new_session=True → grupo de procesos propio, para matar hijos (vite lanza subprocesos).
    return subprocess.Popen(
        cmd, shell=True, start_new_session=True,
        stdout=sys.stderr, stderr=sys.stderr,
    )


def stop_server(proc, label):
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        log(f"{label} no cerró con SIGTERM → SIGKILL.")
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass


def main():
    # Ayuda: mostrar el docstring y salir limpio (el SKILL.md pide correr --help primero).
    if any(a in ("-h", "--help") for a in sys.argv[1:]) and "--" not in sys.argv:
        print(__doc__)
        return 0

    # Separar en '--' manualmente: todo lo posterior es el comando envuelto.
    if "--" not in sys.argv:
        print(__doc__)
        log("Falta el separador '--' seguido del comando a ejecutar.")
        return 2
    split = sys.argv.index("--")
    own_args, wrapped = sys.argv[1:split], sys.argv[split + 1:]

    ap = argparse.ArgumentParser(add_help=True, description="Gestiona servidores y ejecuta un comando.")
    ap.add_argument("--server", action="append", default=[], metavar="CMD")
    ap.add_argument("--port", action="append", default=[], type=int, metavar="N")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--ready-path", default=None)
    args = ap.parse_args(own_args)

    if len(args.server) != len(args.port):
        log(f"Nº de --server ({len(args.server)}) ≠ nº de --port ({len(args.port)}).")
        return 2
    if not wrapped:
        log("No hay comando tras '--'.")
        return 2

    procs = []
    try:
        for cmd, port in zip(args.server, args.port):
            log(f"▶ Arrancando: {cmd}  (puerto {port})")
            proc = start_server(cmd)
            procs.append((proc, cmd, port))
            if not wait_ready(args.host, port, args.timeout, args.ready_path, proc):
                log(f"❌ Timeout: el puerto {port} no abrió en {args.timeout}s.")
                return 1
            log(f"✓ Puerto {port} listo.")

        log(f"▶ Ejecutando comando: {' '.join(wrapped)}")
        result = subprocess.run(wrapped)
        log(f"Comando terminó con código {result.returncode}.")
        return result.returncode
    except KeyboardInterrupt:
        log("Interrumpido (Ctrl-C).")
        return 130
    finally:
        for proc, cmd, port in reversed(procs):
            log(f"■ Deteniendo servidor del puerto {port}…")
            stop_server(proc, f"puerto {port}")


if __name__ == "__main__":
    sys.exit(main())
