"""The ground pod of DELI, New Deli and BONUS (sheet C sprite 163, 2x2: 24 x 28 pixels; ground layer; enemy 514, which
drives about the ground in groups; not animated), polished (2026-10-19; it replaces wave2_f_more.py's pod_dome(), two
blue ellipsoids behind a grey bar with ring cups and a slotted cowl). models.cfg: sprite c 163 pod_dome yaw=0. It is
the ground relative of DELI's flying pod machine (pod_turret, C 191, polish_pod_turret.py), built from its parts:
its blue shells, steel cups and slotted grey cowl, in their materials, laid out as this sprite draws them.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 picture), symmetric about the edge between
columns 11 and 12: at the back two blue shells side by side (columns 0-11 and 12-23 of rows 2-9, a groove between
them, lit on their tops); across their front a light steel bar (rows 10-12, columns 2-21) whose ends are two steel
cups (columns 1-7 and 16-22 of rows 11-17), their dark bores looking down the screen (rows 14-16); between the cups,
apart from them (a gap at row 14), the grey cowl lying down the screen (columns 7-16 of rows 13-24): two dark slots
either side of a light middle rib, its rounded end at the bottom; at its tip two small light blue prongs (columns 10
and 13 of rows 25-26). Nothing round it is ground (it moves; every pixel outside its outline is transparent).

The flying machine's parts are reused as they are (its shell(), cup() and cowl() with their sizes set for this one):
the shells without the green fins (they are all blue here), the cups turned to look down the screen and out, the
cowl turned round to point down the screen and stretched to the sprite's length; the bar and the prongs are this
model's own. The model carries a speck at PIN_Z (a triangle a thousandth of a pixel across, invisible), so that it is
tall enough for the game to set it on the ground (it centres ground models in height on the ground enemies' layer, 4,
and lifts them to 0.3 when they would reach lower: half of PIN_Z is more than 3.7).

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the ground (z = 0); column c is
x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave2_f_more.py's pod_dome() (its @model("pod_dome", "enemy_C", 163) registration): remove it so that it
doesn't overwrite this model (pod_parts() and pod_materials() go with it if nothing else uses them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_C.png), --preview <prefix>.
"""
import math
import os
import sys
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_pod_turret as pt  # noqa: E402

# The flying machine's sizes, set for this one while its parts are built (names as in polish_pod_turret.py).
SHELL = dict(SHELL_CENTRE=Vector((-5.85, 5.4)), SHELL_RADII=(6.05, 6.6), PLAN_POWER=3.0, SHELL_RIM=1.6,
             SHELL_CROWN=4.3, DOME_POWER=2.2, SHELL_TUCK=1.2)
CUP = dict(CUP_MOUTH=Vector((-7.15, -1.35)), CUP_Z=5.3, CUP_TILT=-52.0, CUP_LEAN=14.0, CUP_R=3.0, CUP_LENGTH=5.4,
           CUP_LIP=0.46, CUP_BORE=1.25)
COWL = dict(COWL_BASE=0.35)
COWL_HEIGHT = 0.82        # its height, against the flying machine's
COWL_STRETCH = 1.12       # the cowl along its length (rows 13-24 against the flying machine's rows 3-12)
COWL_BACK = 0.9           # where its back end is (y), after it is turned round
# The bar across the shells' front, from cup to cup: its axis (y, z), half-length, radius.
BAR = (2.45, 5.0, 8.4, 1.5)
# The prongs at the cowl's tip: x, from (y, z), to (y, z), radius; their tips' radius.
PRONGS = [(-1.55, (-9.6, 2.4), (-12.3, 2.0), 0.32, 0.55), (1.55, (-9.6, 2.4), (-12.3, 2.0), 0.32, 0.55)]
PIN_Z = 7.6


@contextmanager
def turret_sizes(values):
    """polish_pod_turret's module constants set to values while its part builders run."""
    old = {name: getattr(pt, name) for name in values}
    for name, value in values.items():
        setattr(pt, name, value)
    try:
        yield
    finally:
        for name, value in old.items():
            setattr(pt, name, value)


def materials():
    glow = k.level_palette()
    # The flying machine's materials (its fins unused: the shells are all blue here).
    m = pt.materials({"fin": (0x3a, 0.0), "fin_edge": (0x3a, 0.0)})
    m["fin"] = m["fin_edge"] = m["shell"]
    m["bar"] = k.material("podd_bar", palette=0x6b, metallic=0.45, roughness=0.24)
    m["bar_top"] = k.material("podd_bar_top", palette=0x6d, metallic=0.45, roughness=0.22)
    m["prong"] = k.material("podd_prong", palette=0x64, metallic=0.45, roughness=0.3)
    m["prong_tip"] = k.material("podd_prong_tip", palette=0x3b, metallic=0.1, roughness=0.2, emission=glow[0x3b],
                                emission_strength=0.6)
    m["seam"] = k.material("podd_seam", palette=0x32, metallic=0.3, roughness=0.5)
    return m


def shells(m):
    # Built without the fins' borders cut into its faces (they are the shell's blue here).
    with turret_sizes(dict(SHELL, split_along=lambda *args, **kwargs: None)):
        left = pt.shell(m)
    right = k.mirror_x(left, "shell_r")
    right.data.name = right.name
    k.smooth(right, 50)
    return [left, right]


def cups(m):
    with turret_sizes(CUP):
        left = pt.cup(m)
    right = k.mirror_x(left, "cup_r")
    right.data.name = right.name
    k.smooth(right, 50)
    return [left, right]


def cowl(m):
    """The flying machine's cowl turned round (its rounded end down the screen), stretched, moved to its place."""
    with turret_sizes(COWL):
        parts = pt.cowl(m)
    y_back = pt.COWL_Y[0]
    turn = Matrix.Translation((0, COWL_BACK, 0)) @ Matrix.Scale(COWL_STRETCH, 4, (0, 1, 0)) @ \
        Matrix.Scale(COWL_HEIGHT, 4, (0, 0, 1)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((0, -y_back, 0))
    for obj in parts:
        obj.data.transform(turn)
        obj.data.update()
    return parts


def bar(m):
    """The steel bar across the shells' front from cup to cup: a capsule along x, lighter on top."""
    y, z, half, r = BAR
    rings = []
    xs = [-half + 2 * half * i / 16 for i in range(17)]
    for x in xs:
        rings.append([Vector((x, y + r * math.cos(2 * math.pi * j / 20), z + r * math.sin(2 * math.pi * j / 20)))
                      for j in range(20)])
    obj = k.loft("bar", rings, m["bar"], start_point=(-half - r * 0.6, y, z), end_point=(half + r * 0.6, y, z))
    k.smooth(obj, 50)
    # Collars where it enters the cups.
    for side in (-1, 1):
        x = side * (half - 1.6)
        prof = [(x - 0.45 * side, r * 0.98), (x - 0.25 * side, r + 0.3), (x + 0.25 * side, r + 0.3),
                (x + 0.45 * side, r * 0.98)]
        if side < 0:
            prof.reverse()
        collar = k.loft(f"bar_collar{side}", [[Vector((px, y + pr * math.cos(2 * math.pi * j / 20),
                                                        z + pr * math.sin(2 * math.pi * j / 20))) for j in range(20)]
                                               for px, pr in prof], m["bar_top"], cap_start=False, cap_end=False)
        k.smooth(collar, 50)
    return obj


def prongs(m):
    made = []
    for i, (x, (ya, za), (yb, zb), r, tip) in enumerate(PRONGS):
        rod = mk.tube(f"prong{i}", [(x, ya, za), (x, (ya + yb) / 2, (za + zb) / 2 + 0.1), (x, yb, zb)], r, m["prong"],
                      10)
        k.smooth(rod, 50)
        made.append(rod)
        made.append(mk.ball(f"prong_tip{i}", (x, yb, zb), (tip, tip, tip), m["prong_tip"], 14, 7))
    return made


def dedupe_slots(obj):
    """Material slots holding the same material merged into the first of them (the flying machine's painter gives
    the fins' keys slots of their own, here the shells' material again)."""
    mats = list(obj.data.materials)
    first = {}
    remap = {}
    for i, mat in enumerate(mats):
        key = mat.name if mat else None
        first.setdefault(key, i)
        remap[i] = first[key]
    if len(first) == len(mats):
        return
    for poly in obj.data.polygons:
        poly.material_index = remap[poly.material_index]
    for i in reversed(range(len(mats))):
        if remap[i] != i:
            obj.data.materials.pop(index=i)


def pin(m):
    e = 0.001
    return k.mesh_object("pin", [(0, 0, PIN_Z), (e, 0, PIN_Z), (0, e, PIN_Z)], [(0, 1, 2)], m["shell"])


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    shells(m)
    cups(m)
    cowl(m)
    bar(m)
    prongs(m)
    pin(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        dedupe_slots(obj)
        if min(v.co.z for v in obj.data.vertices) < -1e-4:  # nothing below the ground
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_C.png")
        mk.compare("pod_dome (C 163)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 163))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("pod_dome", parts, os.path.join(out, "pod_dome.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "pod_dome", parts)


if __name__ == "__main__":
    build()
