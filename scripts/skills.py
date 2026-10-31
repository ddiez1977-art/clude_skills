#!/usr/bin/env python3
"""Mantenimiento de skills/.

  python3 scripts/skills.py validar   # comprueba frontmatter, nombre, longitud y categoría
  python3 scripts/skills.py indice    # regenera skills/README.md desde los SKILL.md
  python3 scripts/skills.py faltas    # lista ficheros citados que no existen -> FALTAN.md

Requiere PyYAML. Sale con código 1 si la validación falla.
"""
import json
import pathlib
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent / "skills"
MAX_DESC = 1024


def leer(carpeta):
    t = (carpeta / "SKILL.md").read_text(encoding="utf-8")
    partes = t.split("---\n", 2)
    if len(partes) < 3:
        raise ValueError("falta el bloque frontmatter")
    return yaml.safe_load(partes[1])


def carpetas():
    return sorted(p for p in RAIZ.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def categorias():
    datos = json.loads((RAIZ / "categorias.json").read_text(encoding="utf-8"))
    mapa = {}
    for cat, nombres in datos["categorias"].items():
        for n in nombres:
            mapa[n] = cat
    return datos, mapa


def validar():
    errores = []
    _, mapa = categorias()
    vistos = set()
    for c in carpetas():
        try:
            d = leer(c)
        except Exception as e:
            errores.append(f"{c.name}: frontmatter no válido ({str(e).splitlines()[0]})")
            continue
        nombre = d.get("name")
        desc = d.get("description") or ""
        vistos.add(c.name)
        if nombre != c.name:
            errores.append(f"{c.name}: name «{nombre}» no coincide con la carpeta")
        if not desc:
            errores.append(f"{c.name}: falta description")
        if len(desc) > MAX_DESC:
            errores.append(f"{c.name}: description de {len(desc)} caracteres (máx. {MAX_DESC})")
        if c.name not in mapa:
            errores.append(f"{c.name}: no está en skills/categorias.json")
    for n in mapa:
        if n not in vistos:
            errores.append(f"categorias.json cita «{n}», que no existe en skills/")
    for e in errores:
        print("ERROR", e)
    print(f"{len(vistos)} skills, {len(errores)} errores")
    return 1 if errores else 0


def indice():
    datos, mapa = categorias()
    info = {}
    for c in carpetas():
        info[c.name] = leer(c)
    out = [
        "# Skills del equipo",
        "",
        "Índice por categoría. Se genera con `python3 scripts/skills.py indice`: no lo edites a mano.",
        "Cada skill vive en su carpeta `skills/<nombre>/` (plana, para que Claude Code la cargue).",
        "Las marcadas **solo si la invocas** no se activan solas: hay que pedirlas por su nombre.",
        "",
    ]
    for cat in datos["orden"]:
        out += [f"## {cat}", ""]
        for n in datos["categorias"].get(cat, []):
            if n not in info:
                continue
            d = info[n]
            marca = " · **solo si la invocas**" if d.get("disable-model-invocation") else ""
            out += [f"### {n}{marca}", "", d["description"], ""]
    sin = [n for n in info if n not in mapa]
    if sin:
        out += ["## Sin categoría", ""] + [f"- {n}" for n in sin] + [""]
    (RAIZ / "README.md").write_text("\n".join(out), encoding="utf-8")
    print(f"índice escrito: {len(info)} skills")
    return 0


def faltas():
    """Referencias a ficheros en SKILL.md que no existen dentro de la skill.
    Heurística: algunas son ejemplos o rutas de proyecto, no dependencias reales."""
    import re
    res = []
    for c in carpetas():
        t = (c / "SKILL.md").read_text(encoding="utf-8")
        refs = set(re.findall(r"`((?:[\w\-./]+/)?[\w\-]+\.(?:md|py|js|cjs|sh|json|csv|txt|html))`", t))
        existentes = {p.name for p in c.rglob("*") if p.is_file()}
        miss = sorted(r for r in refs if "*" not in r and pathlib.PurePosixPath(r).name not in existentes)
        if miss:
            res.append((c.name, miss))
    lineas = ["# Referencias que faltan en las skills", "",
              "Generado con `python3 scripts/skills.py faltas`. Cada fila es un fichero que el SKILL.md cita y que no está en su carpeta.",
              "Algunas son ejemplos o rutas de proyecto y no hacen falta; las demás son dependencias reales.", "",
              "| Skill | Nº | Ficheros citados que no están |", "|---|---|---|"]
    for n, m in res:
        lineas.append(f"| {n} | {len(m)} | {', '.join(m[:15])}{' …' if len(m) > 15 else ''} |")
    (RAIZ.parent / "FALTAN.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(res)} skills con referencias que faltan -> FALTAN.md")
    return 0


if __name__ == "__main__":
    orden = sys.argv[1] if len(sys.argv) > 1 else ""
    if orden == "validar":
        sys.exit(validar())
    if orden == "indice":
        sys.exit(indice())
    if orden == "faltas":
        sys.exit(faltas())
    print(__doc__)
    sys.exit(2)
