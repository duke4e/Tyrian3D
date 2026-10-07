#!/usr/bin/env python3
"""Builds the enemy catalogue page from a TYR3D_EXTRACT export.

usage: tools/catalog_html.py <extract_dir> <out.html> [models.cfg]

The page embeds the sprite sheets, so it is a single self-contained file.
"""
import base64
import json
import os
import sys


def read_model_rules(path):
    """Enemy overrides from models.cfg: {(sheet, index): model}."""
    overrides = {}
    if not path or not os.path.exists(path):
        return overrides
    with open(path) as f:
        for line in f:
            tokens = line.split("#", 1)[0].split()
            if len(tokens) >= 4 and tokens[0] == "sprite":
                overrides[(tokens[1].lower(), int(tokens[2]))] = tokens[3]
    return overrides


def main():
    extract_dir, out_path = sys.argv[1], sys.argv[2]
    models_cfg = sys.argv[3] if len(sys.argv) > 3 else None

    with open(os.path.join(extract_dir, "catalog.json")) as f:
        catalog = json.load(f)
    overrides = read_model_rules(models_cfg)

    sheets_dir = os.path.join(extract_dir, "sheets")
    used = {e["sheet_file"] for e in catalog["enemies"] if e["sheet_file"]} | {s["sheet"] for s in catalog["ships"]}
    sheet_css = []
    for name in sorted(used):
        path = os.path.join(sheets_dir, name + ".png")
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        sheet_css.append(f".sh-{name}{{background-image:url(data:image/png;base64,{data})}}")

    for enemy in catalog["enemies"]:
        enemy["model"] = overrides.get((enemy["sheet"].lower(), enemy["frames"][0] if enemy["frames"] else 0))
    for ship in catalog["ships"]:
        ship["name"] = " ".join(ship["name"].split())

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog_template.html")) as f:
        template = f.read()

    page = (template
            .replace("/*SHEETS*/", "\n".join(sheet_css))
            .replace("/*DATA*/null", json.dumps(catalog, separators=(",", ":"))))
    with open(out_path, "w") as f:
        f.write(page)
    print(f"wrote {out_path} ({len(page) // 1024} KB, {len(catalog['enemies'])} enemies)")


if __name__ == "__main__":
    main()
