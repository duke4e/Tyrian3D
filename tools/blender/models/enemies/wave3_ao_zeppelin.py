"""Batch AO of wave 3, sheet I: the damaged look of SAVARA's grey airship (SAVARA, SAVARA V, SAVARA Y), built by
wave3_k.py's own builder (imported as it is, its output unchanged) and damaged as the damaged sprites show, cut
into the same 17 pieces, drawn at their own origins (origin) so that each swaps in place (models.cfg: yaw=0, as
the intact pieces). The kit is wave3_ao_kit.py, the pixels wave3_ao_art.py (ZEP, ZEP_DMG).

Each piece's damaged sprite (the enemy data's dgr) is the sprite 8 further on: zeppelin_11, 13 (of 3, 5), 47, 49,
51, 53 (of 39-45), 85, 87, 89, 91 (of 77-83), 123, 125, 127, 129 (of 115-121), 162, 164, 166 (of 154-158).

What the damage is: the envelope torn open in three wounds (a small one on its upper right, one on its left, a
long one down its lower middle), the burnt framework inside glowing red in places, and a bite taken out of its
lower left edge; the fan's blades gone from the duct, the duct scorched and holed on both sides; a burn beside
the hub dome on the stern's right; the red frames on the back holed; the right gun pod torn off below its band
(its barrel and muzzle gone), the left one burnt; soot round the wounds and on the gun mounts. The wounds are deep
craters in the envelope (its net broken over them) painted by the damaged sprite: the burnt framework, its red
pixels glowing; the bite squeezes the envelope's left side in so that its outline follows the damaged sprite's.

usage: Blender -b --factory-startup -P wave3_ao_zeppelin.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ao_kit as kit  # noqa: E402

zk = kit.quiet_import("wave3_k")
fk = zk.w  # wave2_f_kit
kit.forget()

ORIGIN = (48, 70)
ZEP = kit.frame("ZEP", 96, ORIGIN)
ZEP_DMG = kit.frame("ZEP_DMG", 96, ORIGIN)


def wound(dv, iv):
    """Where the envelope is torn open: the damaged sprite's black, its burnt framework (the darkest shades of
    the reds and browns) and its embers, over the intact envelope."""
    if dv is None or iv is None or dv == iv:
        return False
    ramp, shade = dv >> 4, dv & 15
    return (ramp == 0 and shade <= 2) or ramp == 7 or (ramp in (1, 4, 5, 0xa) and shade <= 3)


def on_hull(x, y, margin=1.0):
    """Whether (x, y) lies over the envelope's top (inside its outline), clear of the stern's works."""
    r = zk.hull_radius(y)
    return r > 0 and abs(x - zk.ZX) < r - margin and y < 22.0


def left_edge(f, row):
    """The envelope's left edge (a column) in a row of frame f: walking left from the axis to the first
    transparent pixel."""
    c = 48
    while c > 0 and f.g[row][c - 1] is not None:
        c -= 1
    return c


def left_squeeze(fi, fd):
    """y -> how much the envelope's left half is squeezed towards the axis there: the damaged sprite's left edge
    over the intact one's (1 where they agree), smoothed along the envelope."""
    rows = {}
    for r in range(84, 125):
        di, dd = left_edge(fi, r), left_edge(fd, r)
        wi, wd = 48 - di, 48 - dd
        rows[r] = min(1.0, wd / wi) if wi > 0 else 1.0
    smooth = {}
    for r in rows:
        vals = [rows.get(r + d, 1.0) for d in (-2, -1, 0, 1, 2)]
        smooth[r] = sum(vals) / len(vals)

    def at(y):
        row = fi.oy - y - 0.5
        r0 = int(math.floor(row))
        t = row - r0
        a, b = smooth.get(r0, 1.0), smooth.get(r0 + 1, 1.0)
        return a + (b - a) * t
    return at


def zeppelin_damaged():
    zk.zeppelin_whole()
    fk.bake()
    fi, fd = ZEP, ZEP_DMG
    p = kit.hot_painter("aozep", {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), 4: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                                  1: (0, 1, 2), 5: (0,), 0xa: (0, 1, 2, 3)},
                        metallic=0.35, roughness=0.5, finish={4: (0.4, 0.35)}, ember=1.3)
    gone = kit.removed(fi, fd)

    def torn(x, y):
        c, r = int(math.floor(x + fi.ox)), int(math.floor(fi.oy - y))
        if not (0 <= r < len(fi.g) and 0 <= c < fi.width):
            return False
        return wound(fd.g[r][c], fi.g[r][c]) and on_hull(x, y)

    # The fan's blades are gone.
    for obj in kit.meshes():
        if obj.name.startswith("blade"):
            bpy.data.objects.remove(obj)

    # The envelope: the bite out of its lower left edge (its sections there squeezed in towards its axis on
    # that side, so that its outline follows the damaged sprite's), the wounds torn into it (deep craters down
    # to the burnt framework, painted by the damaged sprite), their edges crumpled.
    hull = kit.find("hull")[0]
    wounds_box = (fi.left(10), fi.right(85), fi.bottom(119), fi.top(56))
    kit.pixelate(hull, fi, 1.0, wounds_box)
    squeeze = left_squeeze(fi, fd)
    net = [o for o in kit.meshes() if o.name.startswith(("girder", "hoop"))]
    for obj in [hull] + net:
        for vt in obj.data.vertices:
            if vt.co.x < zk.ZX:
                vt.co.x = zk.ZX + (vt.co.x - zk.ZX) * squeeze(vt.co.y)
        obj.data.update()
    crater = kit.field(fi, fd, lambda dv, iv: wound(dv, iv), blur=0)
    kit.sink(hull, lambda x, y: crater(x, y) if on_hull(x, y) else 0.0, 7.0, min_z=zk.ZC + 0.5, seed=1.0,
             roughness=0.3)
    edge = kit.field(fi, fd, lambda dv, iv: wound(dv, iv), blur=2)
    kit.sink(hull, lambda x, y: edge(x, y) if on_hull(x, y, -2.0) else 0.0, 1.4, min_z=zk.ZC + 0.5, seed=2.0,
             roughness=0.6)
    kit.repaint(hull, fi, fd, p, walls=1, pixel=False)
    # The net over it: broken where it crosses the tears.
    for obj in net:
        kit.delete_over(obj, lambda c, nrm: torn(c.x, c.y) or edge(c.x, c.y) > 0.45)
    # The right gun pod torn off below its band (the damaged sprite ends it at row 80), its end ragged.
    cut_y = fi.bottom(80)
    for obj in kit.meshes():
        if obj.name.startswith("gun_") and obj.name.endswith("_m"):
            if min(v.co.y for v in obj.data.vertices) < cut_y:
                kit.cut_plane(obj, (0.0, cut_y, 0.0), (0.0, -1.0, 0.0))
                if obj.data.polygons:
                    kit.jag(obj, (0.0, cut_y, 0.0), (0.0, -1.0, 0.0), 1.6, scale=0.8, seed=len(obj.name))
                else:
                    bpy.data.objects.remove(obj)
    # Everything else: what the damage took away removed (the right gun pod's lower half), the rest painted
    # as the damaged sprite draws it (soot, holes in the duct and the frames, the burnt mounts).
    others = [o for o in kit.meshes() if o.name != "hull" and not o.name.startswith(("girder", "hoop"))]
    kit.wreck(others, fi, fd, p, (fi.left(0), fi.right(95), fi.bottom(139), fi.top(0)), walls=2, keep_floor=None,
              delete=False)
    # The holes in the duct and the burn on the stern pushed in a little.
    holes = kit.field(fi, fd, lambda dv, iv: dv != iv and kit.is_dark(dv), blur=1)
    for obj in kit.meshes():
        if obj.name.startswith(("duct", "stern_fin", "clamp", "gate", "bracket", "gun_mount", "gun_body")):
            kit.sink(obj, lambda x, y: holes(x, y) if y > -5.0 else 0.0, 1.2, mode="normal", seed=4.0)


DAMAGED_PIECES = [(sprite + 8, x0, x1, y0, y1) for sprite, x0, x1, y0, y1 in zk.ZEPPELIN_PIECES]

_piece = fk.piece


def budgeted_piece(objects, x0, x1, y0, y1):
    """wave2_f_kit.piece, the piece kept under about 4800 triangles (the wounds are cut along the pixel grid)."""
    kept = _piece(objects, x0, x1, y0, y1)
    kit.n.budget(4800, kept)
    return kept


fk.piece = budgeted_piece

# wave3_k's build loop, given the damaged airship in place of its objects (the pieces named zeppelin_<sprite>).
zk.OBJECTS = {"zeppelin": (zeppelin_damaged, (96, 140), "enemy_I", DAMAGED_PIECES,
                           (("side", (-230, -10, 30), (0, -5, 14)), ("stern", (-70, 120, 75), (0, 30, 18))))}


if __name__ == "__main__":
    zk.main()
