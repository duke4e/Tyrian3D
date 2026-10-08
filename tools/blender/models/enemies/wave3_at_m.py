"""Batch AT of wave 3 (the second animation pass), sheet M: two objects whose frames change shape, for frame lines,
built by batch AH's own builders (wave3_ah_dome.py, wave3_ah_rig.py; imported as they are, their output unchanged)
and posed as the frames draw them (models.cfg: as their first frame's models, yaw=0).

- armour_dome_<sprite> (M 85, 7, 9, 11; enemy 540 or 1086, the armoured dome's lower middle piece, armour_dome_bm):
  when the dome fires, the gun band in its front opens and shuts again, 85 7 9 11 9 9 7 7 85: two doors slide apart
  from the seam in its middle (85 shut; a slot 6, 12 and 16 pixels wide) on a dark slot in which a fire grows (a
  small ember, a ball, a blazing ball with flames). wave3_ah_dome's dome shows the slot half open with a flat ember
  in it (between 7 and 9); here its slot and ember are replaced by the doors, the slot and the fire as each frame
  draws them, and the whole dome is cut as armour_dome_bm is. 85, the band shut, is the dome as it is when it doesn't
  fire (a frame line on 85 itself).
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

ad = kit.quiet_import("wave3_ah_dome")
ar = kit.quiet_import("wave3_ah_rig")
kit.forget()
ak = ad.kit                       # wave3_ah_kit
w = kit.w
pal = kit.pal


# --- The armoured dome's gun port --------------------------------------------------------------------------------

BAND_X = (ad.PLATE_X[0] + 1.7, ad.PLATE_X[1] - 1.7)   # between the band's end bezels
BAND_Y = (ad.BAND[0] + 0.3, ad.BAND[1] - 0.3)          # inside the plates over and under it
SEAM_X = 0.5                                             # the seam the doors meet at (column 12 of 85)


def rect(x0, x1, y0, y1):
    return [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]


def dome_port(gap, fire, flames=True):
    """wave3_ah_dome's dome with its gun band as a frame draws it: the slot `gap` pixels wide round the seam (0:
    the doors shut), the fire (None, or its centre's (dx, dy) from the slot's middle, its radii and heat) in it."""
    ad.dome_whole()
    kit.remove(("slot", "ember", "ember_core"))
    surface = ad.shell_z
    dark = pal("dm_slot", 0x01, metallic=0.1, roughness=0.8)
    door_mat = pal("dm_door", 0x68, metallic=0.55, roughness=0.3)
    door_edge = pal("dm_door_edge", 0x63, metallic=0.5, roughness=0.35)
    x0, x1 = BAND_X
    y0, y1 = BAND_Y
    a, b = SEAM_X - gap / 2, SEAM_X + gap / 2
    if gap > 0:
        # The slot: a dark well between the doors (under them where they still cover it).
        slot = ak.heightfield("slot", rect(max(x0, a - 1.0), min(x1, b + 1.0), y0, y1),
                              lambda x, y: surface(x, y) + 0.15, dark, spacing=0.7)
        kit.paint_faces(slot, lambda c, nrm: dark)
    # The doors: grey plates over the band, drawn back into its ends as they open; a dark seam where they meet.
    for name, (p, q) in (("door_l", (x0, a - (0.15 if gap == 0 else 0.0))),
                         ("door_r", (b + (0.15 if gap == 0 else 0.0), x1))):
        if q - p < 0.4:
            continue
        door = ak.heightfield(name, rect(p, q, y0, y1), lambda x, y, e: surface(x, y) + 0.3 + 0.35 * e, door_mat,
                              spacing=0.6, smooth_angle=45, edge=0.5)
        kit.paint_faces(door, lambda c, nrm: door_mat if nrm.z > 0.6 else door_edge)
    if gap == 0:
        ak.groove("door_seam", [(SEAM_X, y1), (SEAM_X, (y0 + y1) / 2), (SEAM_X, y0)],
                  lambda x, y: surface(x, y) + 0.2, dark, radius=0.3, sink=0.1)
    if fire:
        (dx, dy), radii, heat = fire
        cx, cy = SEAM_X + dx, (y0 + y1) / 2 + dy
        kit.fireball("dm_port", (cx, cy, surface(cx, cy) + 0.15 + radii[2] * 0.35), radii, heat, seed=5,
                     flames=flames)


# (sprite: the slot's width, the fire: its offset, radii, heat) -- from the frames' pixels (columns 9-14, 6-17 and
# 4-19 of the piece dark; the fire in columns 10-13, 8-15, 7-17).
DOME_FRAMES = {85: (0.0, None),
               7: (6.0, ((0.0, -0.6), (1.9, 3.1, 1.3), 0.15)),
               9: (12.0, ((0.0, -0.6), (3.6, 3.3, 2.0), 0.6)),
               11: (16.0, ((1.0, -0.2), (4.9, 4.0, 2.6), 1.0))}
for s, (gap, fire) in DOME_FRAMES.items():
    # The lower middle piece only (the others don't change), cut as armour_dome_bm is.
    _, box, centre, _ = ak.quarter(f"armour_dome_{s}", ad.DOME, 24, 28)
    kit.n.pieced(f"armour_dome_port_{s}", lambda gap=gap, fire=fire: dome_port(gap, fire), (72, 56),
                 [(f"armour_dome_{s}", box, centre, lambda s=s: kit.sheet_mask("enemy_M", s))])


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
