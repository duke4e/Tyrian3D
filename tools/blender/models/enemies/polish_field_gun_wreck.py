"""What is left of the heavy field gun of TORM, BONUS and BOTANY A once it is destroyed, under its barrel (stage 4 of
the clean ground: the wreck models that stand in for the maps' painting of it; sheet J sprites 127, the breech's neck
and foot, and 129, the upright block and the arm), built on polish_field_gun.py (2026-10-25). models.cfg: model
field_gun_breech_wreck enemies/field_gun_breech_wreck.glb origin, model field_gun_mount_wreck
enemies/field_gun_mount_wreck.glb origin; wreck j 127 field_gun_breech_wreck, wreck j 129 field_gun_mount_wreck. The
game draws them where the maps paint the wreck (TORM, BONUS and BOTANY A: 13 places each), with 127's and 129's
sprite lines' options (yaw=0 height=-4; 129's glow= is not drawn for stand-ins), at their places; above them the
barrel's damaged look (J 273, the game's own) stands as 89's stand-in.

The painting (the same tile on every map: TORM's and BOTANY A's places match it pixel for pixel, BONUS's lie one or
two rows lower than the sprites; rows 28-55 of the 72 x 56 picture the four sprites make): the base as the live sprites
draw it, its outline exactly the same, burnt as the mortar's hand is (the two are one drawing mirrored): its black
outline brown-black soot (0x10), its greys darker, red-hot gashes torn into it (ramp 7, 0x70-0x78): across the barrel's
breech end (columns 38-41 of rows 28-31), down the neck into the foot's back (columns 44-52 of rows 37-44, the
brightest), in the foot (columns 44-47 of rows 45-49); the neck's top burnt through to black (columns 39-42 of rows
31-34), the slot's glow out (black, its top end a dull red, 0x70-0x71), the arm's prong sooted.

The model: polish_field_gun.py's gun in its damaged state (its barrel burnt as J 273 draws it, so that the wreck's
breech meets the damaged barrel above it), the base (neck, foot, block, arm and prong) as the live one, then burnt as
the painting is with polish_mortar_wreck.py's PaintedBurns and burn_part() (WRECK below: the painting's pixels where
they differ from the live sprites'): greys darker by the painting's drop, the brown-black soot, embers (0x75, 0x77,
0x78, 0x79 at polish_field_gun's glows, 0.29-0.42), the plating torn in at the gashes and the burnt-through holes; the
slot's bar gone (its floor dark) with a dull ember at its top end; a few charred shards on the ground at the foot.
Cut along x = 12, y = 0 as the live gun (polish_coral_manta.cut, the barrel's parts leaned after the cut as
polish_field_gun.export_state leans them), each piece moved so that its sprite's centre is its origin.

Coordinates as polish_field_gun.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the
whole's origin is the middle of 89's and 127's column at the row between them: column c is x = c + 0.5 - 36, row r is
y = 27.5 - r. The pieces' centres: 127 (0, -14), 129 (24, -14).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix> (the uncut
wreck too, <prefix>field_gun_wreck.glb).
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_mortar_wreck import PaintedBurns, burn_part, shards  # noqa: E402
import polish_field_gun as live  # noqa: E402

# The painting's pixels where they differ from the live sprites' (119 89 above 127 129), rows 28-55 of the picture,
# the gun's own pixels only (BOTANY A at 660, 3626: the picture's top left at 624, 3584).
WRECK = """
28 36:05>08 37:05>08 38:05>73 39:05>73 40:04>72 41:05>03 42:0a>08
29 36:05>06 37:05>09 38:05>72 39:05>74 40:04>74 41:03>71 42:0a>08 43:09>08
30 37:05>0a 38:05>01 39:04>73 40:04>74 41:09>02 42:09>04 43:07>05 48:01>10
31 37:05>0b 38:04>03 39:05>10 40:09>73 41:07>70 42:05>10 43:04>02 44:02>01 45:01>10 48:01>10
32 35:01>70 36:09>08 37:08>07 38:07>09 39:0a>04 40:07>10 41:05>10 42:06>10 43:04>10 44:04>03 45:09>08 49:01>10
33 36:01>10 37:09>05 38:0a>04 39:06>10 40:05>10 41:05>10 42:01>10 43:08>04 44:05>02 45:08>05 46:09>08 50:01>10
34 37:01>10 38:01>10 39:01>10 40:01>10 41:01>10 42:01>10 43:03>02 44:09>07 45:05>02 46:07>06 51:01>10
35 43:01>10 44:04>03 45:09>05 46:05>02 47:07>06 48:09>08 50:07>06 51:07>04 52:01>10 53:01>10 54:01>10 55:01>10
36 44:01>10 45:04>10 46:09>04 47:05>10 48:07>04 49:09>08 50:0a>07 51:09>04 52:07>05 53:01>10 56:01>10
37 45:01>70 46:09>04 47:04>71 48:05>72 49:07>05 50:08>02 51:0a>03 52:09>07 54:01>10 57:01>10
38 45:01>72 46:09>05 47:03>75 48:04>77 49:04>76 50:07>73 51:08>70 52:0b>08 58:01>10
39 42:01>10 43:01>10 44:01>70 45:06>03 46:09>07 47:02>72 48:03>75 49:04>74 50:05>74 51:07>70 52:0a>06 53:09>07 55:01>10 57:0a>08 58:08>04 59:01>10
40 40:01>10 41:01>10 42:01>10 45:08>07 46:09>07 47:01>70 48:02>71 49:03>74 50:04>74 51:05>74 52:08>71 53:07>01 54:08>07 56:01>10 57:08>01 58:0a>03 59:07>02 60:01>10
41 39:01>10 40:01>10 47:04>02 49:02>01 50:03>78 51:05>74 52:07>73 53:06>70 54:06>03 55:06>05 56:01>10 57:05>10 58:08>10 59:0a>06 60:05>03 61:01>10
42 45:04>03 46:06>04 47:07>06 48:06>05 50:01>75 51:05>73 52:06>71 53:72>10 54:72>70 55:09>07 56:01>10 57:07>10 58:04>10 59:0a>04 60:05>03 61:01>10
43 44:08>07 45:09>07 46:06>02 47:07>04 50:01>74 51:05>72 52:08>70 53:73>71 54:74>70 55:0a>08 56:01>10 57:09>10 58:01>10 59:09>07 60:05>04 61:01>10
44 38:01>10 43:04>03 44:05>03 45:08>05 46:0a>05 47:06>02 48:07>06 50:02>01 51:05>70 52:0a>05 53:75>10 54:7a>71 55:08>07 56:01>70 57:05>10 58:01>10 59:07>04 61:01>10
45 42:06>05 43:07>03 44:06>70 45:05>01 46:08>03 47:09>04 48:05>03 49:09>08 51:05>04 52:07>06 53:75>10 54:75>10 55:07>06 56:01>10 57:03>10 58:01>10 59:01>10 60:01>10
46 39:01>10 42:04>03 43:06>01 44:07>71 45:07>01 46:05>72 47:07>10 48:0a>04 49:09>05 50:02>01 53:74>10 54:74>10 55:07>06 56:01>10 57:01>10 58:01>10 59:01>10
47 43:03>01 44:06>71 45:06>75 46:07>73 47:03>70 48:08>10 49:05>10 50:01>10 53:73>10 54:71>10 55:06>05 58:01>10
48 41:01>10 43:02>10 44:03>70 45:06>73 46:08>01 47:04>70 48:08>05 49:04>10 50:01>10 53:74>10 54:71>10
49 43:02>01 44:02>10 45:04>70 46:05>70 47:03>01 48:07>06 49:04>01 50:01>10 53:74>10 54:71>10 55:01>10
50 44:02>10 45:04>10 46:05>10 47:04>03 48:05>04 54:72>10 55:01>10
51 45:04>10 46:05>01 47:01>10 48:01>10 49:01>10
"""
# The embers' bands (polish_field_gun's glow per shade: 0.23-0.39).
EMBERS = [(0.22, 0x75, live.GLOW[0x75]), (0.45, 0x77, live.GLOW[0x77]), (0.8, 0x78, live.GLOW[0x78]),
          (1.3, 0x79, live.GLOW[0x79])]
# The slot's dull ember left at its top end (column, row, radii, how far over the slot's floor).
SLOT_EMBER = (53.9, 43.2, (0.75, 1.3, 0.35), 0.25)
# The charred shards and dull embers at the foot: (x, y, size, heading, palette index, glow).
SHARDS = [(live.PX(45.4), live.PY(52.0), 1.1, -20.0, 0x10, 0.0), (live.PX(42.6), live.PY(51.0), 0.8, 35.0, 0x02, 0.0),
          (live.PX(51.6), live.PY(51.8), 0.9, -60.0, 0x10, 0.0), (live.PX(44.2), live.PY(50.4), 0.45, 0.0, 0x73, 0.2),
          (live.PX(38.4), live.PY(47.0), 0.7, 70.0, 0x02, 0.0)]
BASE = ("neck", "foot", "arm", "prong", "block")
PIECES = [("breech", "field_gun_breech_wreck"), ("mount", "field_gun_mount_wreck")]


class WreckMats:
    """polish_field_gun's Mats as polish_mortar_wreck.burn_part calls them (get(index, glow)): glowing reds at the live
    glows, the brown-black soot dull, the dark 0x01 the slots' dark, the rest its greys."""

    def __init__(self, m):
        self.m = m

    def get(self, index, glow=0.0, **_):
        if glow > 0:
            return self.m.glow(index)
        if index == 0x10:
            return self.m.soot(index)
        if index == 0x01:
            return self.m.dark(index)
        return self.m.grey(index)


def build_whole():
    """The damaged gun, its base and its barrel's breech end burnt as the painting is; the shards at its foot."""
    whole, m = live.build_whole("damaged")
    wm = WreckMats(m)
    burns = PaintedBurns(WRECK, 72, 56, 36.0, 28.0)
    bar = next(o for o in whole if o.name == "slot_bar")
    whole.remove(bar)
    bpy.data.objects.remove(bar)
    for i, obj in enumerate(whole):
        mk.apply(obj)
        if obj.name.startswith(BASE) or obj.name == "barrel":
            burn_part(obj, burns, wm, 60 if obj.name.startswith(("arm", "prong", "neck")) else 40, seed=1.3 * i,
                      embers=EMBERS)
    whole += shards(SHARDS, wm, "fgun_shard")
    c, r, radii, lift = SLOT_EMBER
    outline, back, front, _ = live.BLOCK
    ys = [live.YE(rr) for _, rr in outline]
    t = (live.PY(r) - min(ys)) / (max(ys) - min(ys))
    floor = front + (back - front) * t - live.SLOT[4]
    from polish_jaw_gun_wreck import lump
    ember = lump("slot_ember", (live.PX(c), live.PY(r), floor + lift), radii, m.glow(0x73), 4.2, 0.3, 1)
    k.smooth(ember, 70)
    whole.append(ember)
    for obj in whole:
        k.recalc_normals(obj)
    return whole, m


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    whole, m = build_whole()
    triangulate(whole)
    print("== whole field gun wreck: %d triangles" % mk.triangles(whole))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "whole" in options or "preview" in options:
        shown = live.leaned_whole(whole)
        if "whole" in options:
            mk.export(shown, options["whole"] + "field_gun_wreck.glb")
        if "preview" in options:
            mk.preview(options["preview"] + "field_gun_wreck_whole", shown, size=(72, 56), scale=8, distance=2.0)
        for obj in shown:
            if obj not in whole:
                bpy.data.objects.remove(obj)
    cap = m.grey(live.CAP)
    for part, name in PIECES:
        box, centre = live.BOXES[part]
        parts = []
        for src in whole:
            p = cut(src, box, cap)
            if p is not None:
                parts.append(live.lean(p) if src.get("lean") else p)
        drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
