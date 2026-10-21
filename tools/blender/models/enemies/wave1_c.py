"""Enemies of wave 1, batch C, facing the way their sprites do (models.cfg: yaw=0 unless noted; the claw gate
is polish_claw_gate.py):

- purple_pod (sheet 5 47): a purple pod with a red strap and a golden clasp (HARVEST, LAVA RUN).
(The teal spiked mine, A 167, is polish_spike_mine.py's chrome mine in the sprite's colours: models.cfg color=sprite.)
(The crimson orb, K 195: polish_orb_crimson.py; DELI's gun arms, T 39 and 49: polish_deli_boss.py.)
(SAVARA's boss, with its outer fins F 153 and 163: polish_savara_boss.py.)

Run: Blender -b --factory-startup -P wave1_c.py -- [--only name,name] [--preview <dir>]
     [--sheets <TYR3D_EXTRACT sheets dir>] [--stats 1]
     (--sheets prints each model's silhouette overlap with its sprite, --stats the faces per part)
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")


# --- Round ones ------------------------------------------------------------------------------------

def ellipsoid_part(name, centre, radii, mat, y0, y1, segments=40, rings_count=14):
    """The part of an ellipsoid between y0 and y1 (absolute), closed at the cut."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    rings = []
    for i in range(rings_count + 1):
        y = y0 + (y1 - y0) * i / rings_count
        f = max(0.0, 1 - ((y - cy) / ry) ** 2) ** 0.5
        if f > 1e-3:
            rings.append(k.ring(y, rx * f, rz * f, segments, z=cz, x=cx))
    return k.smooth(k.loft(name, rings, mat, start_point=(cx, y0, cz), end_point=(cx, y1, cz)), 70)


def purple_pod():
    k.reset()
    shell = k.material("pod_shell", palette=87, metallic=0.3, roughness=0.28)
    lower = k.material("pod_lower", palette=85, metallic=0.3, roughness=0.3)
    strap = k.material("pod_strap", palette=243, metallic=0.25, roughness=0.35)
    edge = k.material("pod_edge", palette=82, metallic=0.3, roughness=0.4)
    gold = k.material("pod_gold", palette=250, metallic=0.85, roughness=0.22)
    c = (0.0, 0.5, 0.0)
    radii = (12.0, 13.5, 9.0)
    ellipsoid_part("upper", c, radii, shell, 0.0, c[1] + radii[1])
    ellipsoid_part("lower", c, radii, lower, c[1] - radii[1], 0.0)

    def half_width(y):
        return radii[0] * max(0.0, 1 - ((y - c[1]) / radii[1]) ** 2) ** 0.5

    squash = radii[2] / radii[0]
    profile = [(-2.6, half_width(-2.6) - 0.1), (-2.3, half_width(-2.3) + 0.5), (2.3, half_width(2.3) + 0.5),
               (2.6, half_width(2.6) - 0.1)]
    k.smooth(k.lathe("strap", profile, strap, segments=64, squash=squash), 50)
    for y in (-2.9, 2.9):
        k.smooth(k.lathe(f"edge{y}", [(y - 0.35, half_width(y) - 0.1), (y, half_width(y) + 0.3),
                                      (y + 0.35, half_width(y) - 0.1)], edge, segments=64, squash=squash), 60)
    # The golden clasp on top (and its twin underneath).
    for z, name in ((radii[2] + 0.35, "clasp"), (-radii[2] - 0.35, "clasp_under")):
        clasp = k.box(name, (0.0, 0.0, z), (2.4, 6.4, 1.2), gold)
        k.bevel(clasp, 0.4, 2)
    k.smooth(k.ellipsoid("stud", (0.0, 0.0, radii[2] + 1.0), (0.8, 1.2, 0.5), gold, 12, 6), 60)


# --- Running ---------------------------------------------------------------------------------------

# name: (builder, sheet, sprite used for the silhouette check)
MODELS = {
    "purple_pod": (purple_pod, "5", 47),
}


def main():
    options = k.args()
    only = options.get("only", "").split(",") if "only" in options else None
    for name, (build, sheet, sprite) in MODELS.items():
        if only and name not in only:
            continue
        build()
        if "stats" in options:
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
                    print("  ", name, obj.name, len(mesh.polygons), "faces")
        if "sheets" in options:
            print("model", name)
            k.check_silhouette(os.path.join(options["sheets"], f"enemy_{sheet.upper()}.png"), sprite)
        k.export(os.path.join(OUT, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(os.path.join(options["preview"], name))


main()
