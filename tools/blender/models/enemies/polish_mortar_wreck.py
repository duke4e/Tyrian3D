"""What is left of the mortar of TORM, BONUS and BOTANY A once it is destroyed, under its barrel (stage 4 of the clean
ground: the wreck model that stands in for the maps' painting of it; sheet G sprite 203, the mechanical hand),
built on polish_mortar.py (2026-10-25). models.cfg: model mortar_mount_wreck enemies/mortar_mount_wreck.glb origin;
wreck g 203 mortar_mount_wreck. The game draws it where the maps paint the wreck (TORM and BONUS: 11 places), with
203's sprite line's options (yaw=0 height=-4), at 203's place; above it the barrel's damaged looks (G 169, 207: the
game's own) and to its right the leaves (205, the live model) stand as the stand-ins of the others.

The painting (the same tile on every map: TORM's places match it pixel for pixel, BONUS's lie one or two rows lower
than the sprites; rows 28-55 of the 48 x 56 picture the four sprites make): the hand as the live sprite draws it, its
outline exactly the same (no part of it missing), burnt: its black outline (0x01) brown-black soot (0x10), its greys
one to four shades darker (most on the neck's top, the fist and the block's outer side), red-hot gashes torn into it
(ramp 7, 0x70-0x78): across the barrel's breech end (columns 20-23 of rows 28-31), down the neck into the fist's back
(columns 8-14 of rows 37-44, the brightest, 0x74-0x78), in the fist (columns 14-17 of rows 45-49); the neck's top
burnt through to black (columns 18-22 of rows 32-34), the slot's glow out (its lower part black, its top end a dull
red, 0x70-0x71), the hook's edge sooted.

The model: polish_mortar.py's mortar in its damaged state (its barrel burnt as G 169 and 207 draw it, so the wreck's
barrel meets the damaged barrel's pieces above it), its hand (palm, neck, thumb, hook, block, slot bar, fist and
knuckles) as the live one, then burnt as the painting is (PaintedBurns: the painting's pixels where they differ from
the live sprites', WRECK below, as fields over the picture, blurred a little, sampled at the faces' plan points): the
faces split along the fields' contours, then each grey face its own shade made darker by as many shades as the
painting darkens it there (the even greys of the live model's bands, 0x02-0x0c), brown-black soot (0x10) where the
painting is, glowing embers where it turned red (EMBER_BANDS: 0x73, 0x75, 0x77, 0x7a at the live slot's emissions
0.23-0.36, under the bloom's white; the measure EMBER_GAIN stronger than polish_mortar's: blurred, single red pixels
would read dark); the slot's glowing bar gone (its glow is out: the slot's dark floor shows), a dull ember (0x71, 0.16)
left at its top end; the plating torn in where the gashes (0.45 deep) and the burnt-through holes (1.1) are (pressed
in along its normals by noise, TORN); a few charred shards and a dull ember on the ground at the fist's and the
block's foot, where the painting's soot spreads. The palm under the barrel is left as it is (hidden). (The faces are
split along one contour of the embers and of the soot only, so that the piece stays near the live one's size.) Cut along x = 0, y = 0 as the live mortar
(polish_coral_manta.cut, the barrel's parts leaned after the cut as polish_mortar.export_state leans them), moved so
that 203's centre is its origin.

Also here, for polish_field_gun_wreck.py: PaintedBurns, burn_part(), tear(), shards() (the field gun's painting is
this one mirrored, so the same method serves it).

Coordinates as polish_mortar.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0);
the whole's origin is the corner where the four sprites meet: column c is x = c + 0.5 - 24, row r is y = 27.5 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix> (the uncut
wreck too, <prefix>mortar_wreck.glb).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_mortar as live  # noqa: E402


# --- Painted burns (shared with polish_field_gun_wreck.py) -----------------------------------------------------------

def blur(a, sigma=0.6, rad=2):
    """polish_mortar.damage_fields' blur (separable Gaussian, edges held)."""
    import numpy as np
    kernel = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
    kernel /= kernel.sum()
    for axis in (0, 1):
        p = np.pad(a, [(rad, rad) if ax == axis else (0, 0) for ax in (0, 1)], mode="edge")
        a = sum(w * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i, w in enumerate(kernel))
    return a


class PaintedBurns:
    """The painting's burns, from its pixels where they differ from the live sprites' ("row col:live>painted ...",
    rows and columns of a w x h picture whose column c's middle is x = c + 0.5 - x0 and row r's is y = y0 - 0.5 - r),
    as fields blurred a little and sampled at plan points:
    - drop: how many shades darker the painting's grey is (to the brown-black 0x10: all of its shade);
    - soot: 1 where the painting is the brown-black 0x10;
    - hole: the soot where the live pixel was not the outline (0x01): burnt through;
    - ember: red where the live pixel was not ((shade / 4) + 0.25, polish_mortar's measure);
    - hot: red still where the live pixel was red too (the same measure);
    - out: 1 where the live pixel was red and the painting's is not (a glow gone out)."""

    def __init__(self, text, w, h, x0, y0):
        import numpy as np
        self.w, self.h, self.x0, self.y0 = w, h, x0, y0
        f = {n: np.zeros((h, w)) for n in ("drop", "soot", "hole", "ember", "hot", "out")}
        for line in text.strip().splitlines():
            row, *cells = line.split()
            r = int(row)
            for cell in cells:
                c, change = cell.split(":")
                a, b = (int(v, 16) for v in change.split(">"))
                c = int(c)
                red_a, red_b = a >> 4 == 7, b >> 4 == 7
                if red_b and not red_a:
                    f["ember"][r, c] = ((b & 15) / 4.0 + 0.25) * EMBER_GAIN
                elif red_b:
                    f["hot"][r, c] = (b & 15) / 4.0 + 0.25
                elif red_a:
                    f["out"][r, c] = 1.0
                elif b == 0x10:
                    f["soot"][r, c] = 1.0
                    f["drop"][r, c] = a & 15
                    if a != 0x01:
                        f["hole"][r, c] = 1.0
                elif b >> 4 == 0:
                    f["drop"][r, c] = max(0, (a & 15) - (b & 15))
        self.fields = {n: blur(v, 0.6 if n != "ember" else 0.5) for n, v in f.items()}

    def __call__(self, name, x, y):
        a = self.fields[name]
        u, v = x + self.x0 - 0.5, self.y0 - 0.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def px(r, c):
            if 0 <= r < self.h and 0 <= c < self.w:
                return a[r, c]
            return 0.0
        return float((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) +
                     (1 - fu) * fv * px(r0 + 1, c0) + fu * fv * px(r0 + 1, c0 + 1))


# How much stronger the embers are than polish_mortar's measure (blurred, single red pixels would read dark).
EMBER_GAIN = 1.25
# The embers' bands of the ember field (lowest value, palette index, glow: the live slots' own materials) and the
# greys a darkened face snaps to.
EMBER_BANDS = [(0.22, 0x73, 0.23), (0.45, 0x75, 0.27), (0.8, 0x77, 0.31), (1.3, 0x7a, 0.36)]
GREY_SHADES = (0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c)
DROP_CUTS = ()                         # the drop's contours the faces are split along (none: the faces are small)
EMBER_CUTS = (0.22,)                   # the ember field's
TORN = (0.45, 1.1)                     # how deep the gashes and the burnt-through holes are pressed in


def palette_index(mat):
    if mat is None or "@" not in mat.name:
        return None
    try:
        return int(mat.name.rsplit("@", 1)[1])
    except ValueError:
        return None


def glowing(mat):
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat is not None and mat.use_nodes else None
    return bsdf is not None and bsdf.inputs["Emission Strength"].default_value > 0


def darkened(index, drop):
    """A grey (ramp 0) made `drop` shades darker, snapped to the live bands' even greys (not below 0x02)."""
    target = max(1, (index & 15) - drop)
    return min(GREY_SHADES, key=lambda s: (abs(s - target), s))


def tear(obj, burns, seed=0.0, depth=TORN):
    """The plating pressed in where the painting's gashes and burnt-through holes are (its faces turned up, which the
    camera sees), raggedly."""
    obj.data.update()
    for v in obj.data.vertices:
        if v.normal.z < 0.1:
            continue
        g = max(depth[0] * smoothstep(0.35, 1.2, burns("ember", v.co.x, v.co.y)),
                depth[1] * smoothstep(0.35, 0.9, burns("hole", v.co.x, v.co.y)))
        if g > 0.0:
            rag = 0.6 + 0.4 * noise.noise(Vector((v.co.x * 0.9 + seed, v.co.y * 0.9, v.co.z * 0.9)))
            v.co -= v.normal * g * rag
    obj.data.update()
    return obj


def burn_part(obj, burns, m, angle=40.0, torn=True, seed=0.0, embers=EMBER_BANDS):
    """A part burnt as the painting is: torn where its gashes and holes are, its faces that the camera sees split along
    the fields' contours, then painted: embers (embers: bands of the ember field, (lowest, palette index, glow)), the
    brown-black soot, its greys darker by the painting's drop; a glow gone out dark or a dull red (m: the live
    script's Mats, get(index, glow))."""
    if torn:
        tear(obj, burns, seed)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    names = ("ember", "drop", "soot", "out", "hot")
    vals = {n: {v: burns(n, v.co.x, v.co.y) for v in bm.verts} for n in names}

    def seen():
        return [f for f in bm.faces if f.normal.z > 0.05]
    for t in EMBER_CUTS:
        split_contour(bm, vals, "ember", t, seen())
    for t in DROP_CUTS:
        split_contour(bm, vals, "drop", t, seen())
    split_contour(bm, vals, "soot", 0.3, seen())
    mats = list(obj.data.materials)
    slots = {}

    def slot(mat):
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        return slots[mat.name]
    for f in bm.faces:
        mean = {n: sum(vals[n][v] for v in f.verts) / len(f.verts) for n in names}
        src = mats[f.material_index] if f.material_index < len(mats) else None
        index = palette_index(src)
        if index is None:
            continue
        new = None
        band = [b for b in embers if mean["ember"] >= b[0]]
        if glowing(src):
            if mean["out"] > 0.05 or mean["hot"] > 0.05:
                hot = [b for b in embers if mean["hot"] >= b[0]]
                new = m.get(hot[-1][1], hot[-1][2]) if hot else m.get(0x01)   # a dull red left, or out
        elif band:
            new = m.get(band[-1][1], band[-1][2])
        elif index >> 4 == 0:
            if mean["soot"] > 0.3 and (f.normal.z < 0.6 or mean["drop"] > 3.0):
                new = m.get(0x10)
            else:
                drop = int(mean["drop"] + 0.3)
                if drop > 0:
                    new = m.get(darkened(index, drop))
        if new is not None and new is not src:
            f.material_index = slot(new)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if obj.data.has_custom_normals:
        with bpy.context.temp_override(object=obj, active_object=obj, selected_editable_objects=[obj]):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    k.smooth(obj, angle)
    return obj


def shards(specs, m, prefix="wreck_shard"):
    """Charred shards and dull embers on the ground: (x, y, size, heading (degrees), palette index, glow)."""
    from polish_jaw_gun_wreck import rock
    parts = []
    for i, (x, y, size, heading, index, glow) in enumerate(specs):
        mat = m.get(index, glow) if glow else m.get(index)
        obj = rock(f"{prefix}{i}", (x, y, 0.0), (size, size * 0.7, size * 0.45), mat, 3.0 + 1.7 * i, flat=-0.4)
        obj.data.transform(Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(math.radians(heading), 4, "Z") @
                           Matrix.Translation((-x, -y, 0.0)))
        parts.append(obj)
    return parts


# --- The mortar's wreck ---------------------------------------------------------------------------------------------

# The painting's pixels where they differ from the live sprites' (165 167 above 203 205), rows 28-55 of the picture,
# the hand's own pixels only (TORM at 492, 4046: the picture's top left at 480, 4004).
WRECK = """
28 19:0a>08 20:05>03 21:04>72 22:05>73 23:05>73 24:05>08 25:05>08
29 18:09>08 19:0a>08 20:03>71 21:04>74 22:05>74 23:05>72 24:05>09 25:05>06
30 13:01>10 18:07>05 19:09>04 20:09>02 21:04>74 22:04>73 23:05>01 24:05>0a
31 13:01>10 16:01>10 17:02>01 18:04>02 19:05>10 20:07>70 21:09>73 22:05>10 23:04>03 24:05>0b
32 12:01>10 16:09>08 17:04>03 18:04>10 19:06>10 20:05>10 21:07>10 22:0a>04 23:07>09 24:08>07 25:09>08 26:01>70
33 11:01>10 15:09>08 16:08>05 17:05>02 18:08>04 19:01>10 20:05>10 21:05>10 22:06>10 23:0a>04 24:09>05 25:01>10
34 10:01>10 15:07>06 16:05>02 17:09>07 18:03>02 19:01>10 20:01>10 21:01>10 22:01>10 23:01>10 24:01>10
35 6:01>10 7:01>10 8:01>10 9:01>10 10:07>04 11:07>06 13:09>08 14:07>06 15:05>02 16:09>05 17:04>03 18:01>10
36 5:01>10 8:01>10 9:07>05 10:09>04 11:0a>07 12:09>08 13:07>04 14:05>10 15:09>04 16:04>10 17:01>10
37 4:01>10 7:01>10 9:09>07 10:0a>03 11:08>02 12:07>05 13:05>72 14:04>71 15:09>04 16:01>70
38 3:01>10 9:0b>08 10:08>70 11:07>73 12:04>76 13:04>77 14:03>75 15:09>05 16:01>72
39 2:01>10 3:08>04 4:0a>08 6:01>10 8:09>07 9:0a>06 10:07>70 11:05>74 12:04>74 13:03>75 14:02>72 15:09>07 16:06>03 17:01>70 18:01>10 19:01>10 21:01>10
40 1:01>10 2:07>02 3:0a>03 4:08>01 5:01>10 7:08>07 8:07>01 9:08>71 10:05>74 11:04>74 12:03>74 13:02>71 14:01>70 15:09>07 16:08>07 19:01>10 20:01>10 21:01>10
41 0:01>10 1:05>03 2:0a>06 3:08>10 4:05>10 5:01>10 6:06>05 7:06>03 8:06>70 9:07>73 10:05>74 11:03>78 12:02>01 14:04>02 21:01>10 22:01>10
42 0:01>10 1:05>03 2:0a>04 3:04>10 4:07>10 5:01>10 6:09>07 7:72>70 8:72>10 9:06>71 10:05>73 11:01>75 13:06>05 14:07>06 15:06>04 16:04>03 23:01>10 24:01>10
43 0:01>10 1:05>04 2:09>07 3:01>10 4:09>10 5:01>10 6:0a>08 7:74>70 8:73>71 9:08>70 10:05>72 11:01>74 14:07>04 15:06>02 16:09>07 17:08>07
44 0:01>10 2:07>04 3:01>10 4:05>10 5:01>70 6:08>07 7:7a>71 8:75>10 9:0a>05 10:05>70 11:02>01 13:07>06 14:06>02 15:0a>05 16:08>05 17:05>03 18:04>03 23:01>10
45 1:01>10 2:01>10 3:01>10 4:03>10 5:01>10 6:07>06 7:75>10 8:75>10 9:07>06 10:05>04 12:09>08 13:05>03 14:09>04 15:08>03 16:05>01 17:06>70 18:07>03 19:06>05 23:01>10
46 2:01>10 3:01>10 4:01>10 5:01>10 6:07>06 7:74>10 8:74>10 11:02>01 12:09>05 13:0a>04 14:07>10 15:05>72 16:07>01 17:07>71 18:06>01 19:04>03 22:01>10 23:01>10 24:01>10
47 3:01>10 6:06>05 7:71>10 8:73>10 11:01>10 12:05>10 13:08>10 14:03>70 15:07>73 16:06>75 17:06>71 18:03>01 23:01>10 24:01>10
48 7:71>10 8:74>10 11:01>10 12:04>10 13:08>05 14:04>70 15:08>01 16:06>73 17:03>70 18:02>10 20:01>10 23:01>10
49 6:01>10 7:71>10 8:74>10 11:01>10 12:04>01 13:07>06 14:03>01 15:05>70 16:04>70 17:02>10 18:02>01
50 6:01>10 7:72>10 13:05>04 14:04>03 15:05>10 16:04>10 17:02>10
51 12:01>10 13:01>10 14:01>10 15:05>01 16:04>10
52 12:01>10 15:01>10 16:01>10
53 12:01>10
54 12:01>10
"""
# The charred shards and dull embers at the hand's foot: (x, y, size, heading, palette index, glow).
SHARDS = [(live.PX(13.6), live.PY(52.2), 1.1, 20.0, 0x10, 0.0), (live.PX(16.2), live.PY(51.4), 0.8, -35.0, 0x02, 0.0),
          (live.PX(4.2), live.PY(49.6), 0.9, 60.0, 0x10, 0.0), (live.PX(15.0), live.PY(50.6), 0.45, 0.0, 0x71, 0.16),
          (live.PX(22.6), live.PY(46.8), 0.7, 110.0, 0x02, 0.0)]
# The slot's glow is out: its bar goes (the slot's floor dark), a dull ember left at its top end (column, row, radii,
# how far over the slot's floor).
SLOT_EMBER = (7.9, 43.2, (0.75, 1.3, 0.35), 0.25)
HAND = ("neck", "thumb", "hook", "block", "fist", "knuckle")   # (the palm, under the barrel, as it is)


def build_whole():
    """The damaged mortar, its hand and its barrel's breech end burnt as the painting is; the shards at its foot."""
    whole, m = live.build_whole("damaged")
    m.get(0x10, 0.0, 0.2, 0.75)            # the brown-black soot: dull
    burns = PaintedBurns(WRECK, 48, 56, 24.0, 28.0)
    bar = next(o for o in whole if o.name == "slot_bar")
    whole.remove(bar)
    bpy.data.objects.remove(bar)
    for i, obj in enumerate(whole):
        mk.apply(obj)
        if obj.name.startswith(HAND) or obj.name == "barrel":
            burn_part(obj, burns, m, 60 if obj.name.startswith(("hook", "knuckle", "neck", "thumb")) else 40,
                      seed=1.3 * i)
    whole += shards(SHARDS, m)
    c, r, radii, lift = SLOT_EMBER
    outline, back, front, _ = live.BLOCK
    ys = [live.YE(rr) for _, rr in outline]
    t = (live.PY(r) - min(ys)) / (max(ys) - min(ys))
    floor = front + (back - front) * t - live.SLOT[4]
    from polish_jaw_gun_wreck import lump
    ember = lump("slot_ember", (live.PX(c), live.PY(r), floor + lift), radii, m.get(0x71, 0.16), 4.2, 0.3, 1)
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
    print("== whole mortar wreck: %d triangles" % mk.triangles(whole))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "whole" in options or "preview" in options:
        shown = live.leaned_whole(whole)
        if "whole" in options:
            mk.export(shown, options["whole"] + "mortar_wreck.glb")
        if "preview" in options:
            mk.preview(options["preview"] + "mortar_wreck_whole", shown, size=(48, 56), scale=8, distance=1.6)
        for obj in shown:
            if obj not in whole:
                bpy.data.objects.remove(obj)
    name, box = "mortar_mount_wreck", live.BOXES["mount"]
    cap = m.get(live.CAP)
    parts = []
    for src in whole:
        p = cut(src, box, cap)
        if p is not None:
            parts.append(live.lean(p) if src.get("lean") else p)
    drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    parts = [join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
