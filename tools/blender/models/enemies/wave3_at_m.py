"""Batch AT of wave 3 (the second animation pass), sheet M: an object whose frames change shape, for frame lines,
built by batch AH's own builders (wave3_ah_rig.py; imported as it is, its output unchanged)
and posed as the frames draw them (models.cfg: as their first frame's models, yaw=0).

- rig_hatch_<sprite> (M 199, 237; enemy 1181, MINERS' hatch, rig_hatch): its doors slide open on a red light and
  shut again, 197 199 199 237 237 199 199 197: wave3_ah_rig's hatch with its doors drawn back to the frames' gap (5
  and 9 pixels), a dark well between them and the red light in it, larger and brighter as they open.

usage: Blender -b --factory-startup -P wave3_at_m.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

ar = kit.quiet_import("wave3_ah_rig")
kit.forget()
ak = ar.kit                       # wave3_ah_kit
w = kit.w
pal = kit.pal


# --- The rig's hatch ---------------------------------------------------------------------------------------------

def hatch_open(left, right, light):
    """wave3_ah_rig's hatch (at its place in the rig, as rig_hatch is built) with its doors drawn back: the gap
    from x = left to right (from the hatch's centre), a dark well in it and the red light (its radii (rx, ry), its
    brightness)."""
    hx, hy = ar.HATCH_AT[0]
    ar.hatch_parts(ar.HATCH_AT[0], -1)
    old = [bpy.data.objects[nm] for nm in ("hatch_door0", "hatch_door1", "hatch_slit", "hatch_light")]
    # The doors' height, depth and outer ends as wave3_ah_rig makes them.
    d0, d1 = old[0], old[1]
    zs = [v.co.z for v in d0.data.vertices]
    ys = [v.co.y for v in d0.data.vertices]
    door_z, door_h = (min(zs) + max(zs)) / 2, max(zs) - min(zs)
    y_mid, depth = (min(ys) + max(ys)) / 2, max(ys) - min(ys)
    outer_l = min(v.co.x for v in d0.data.vertices)
    outer_r = max(v.co.x for v in d1.data.vertices)
    door = d0.data.materials[0]
    dark = old[2].data.materials[0]
    kit.remove([o.name for o in old])
    a, b = hx + left, hx + right
    for i, (p, q) in enumerate(((outer_l, a), (b, outer_r))):
        if q - p > 0.3:
            w.rounded_box(f"hatch_door{i}", ((p + q) / 2, y_mid, door_z), (q - p, depth, door_h), door,
                          bevel=min(0.25, (q - p) * 0.3))
    # The well: dark, a little under the doors, a rim of the cabinet's dark round it.
    w.rounded_box("hatch_slit", ((a + b) / 2, y_mid, door_z - 0.35), (b - a + 0.4, depth, 1.0), dark, bevel=0.2)
    (rx, ry), glow = light
    red = pal(f"hatch_red_{int(glow * 10)}", 0x46 if glow < 1.9 else 0x48, metallic=0.0, roughness=0.4, glow=glow)
    deep = pal("hatch_red_deep", 0x42, metallic=0.0, roughness=0.5, glow=0.6)
    w.sphere("hatch_glow", ((a + b) / 2, y_mid, door_z + 0.05), ((b - a) / 2 - 0.3, depth / 2 - 0.4, 0.35), deep,
             16, 6)
    w.sphere("hatch_light", ((a + b) / 2 - 0.2, y_mid - 0.4, door_z + 0.3), (rx, ry, 0.55), red, 14, 8)


# (sprite: the gap's ends from the hatch's centre, the light's radii and glow): 199's gap is columns 8-12, 237's
# columns 6-14, round 197's slit (columns 10, 11, which rig_hatch has at x = 0): x -3 .. 2 and -5 .. 4; the light
# brightens.
HATCH_FRAMES = {199: (-3.0, 2.0, ((1.2, 1.9), 1.6)), 237: (-5.0, 4.0, ((1.6, 2.2), 2.0))}
for s, (left, right, light) in HATCH_FRAMES.items():
    kit.n.model(f"rig_hatch_{s}", mask=lambda s=s: kit.sheet_mask("enemy_M", s))(
        ar.at_origin(lambda left=left, right=right, light=light: hatch_open(left, right, light), ar.HATCH_AT[0]))


if __name__ == "__main__":
    ak.run()
