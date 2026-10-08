"""Batch AP of wave 3 (sheet L): the damaged look of the station of STATION and TIME WAR (wave3_z_station.py) and of
its axle ends (wave2_e.py), modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels
wave3_ap_art.py (STATION_DMG, in wave3_z_art.STATION's frame).

Each of the station's ten pieces switches to its damaged sprite when hit hard and stays so (dlevel -1): the left
half (enemies 664-668) L 24 -> 100, 7 -> 83, 9 -> 85, 45 -> 121, 47 -> 123, the right half (659-663) L 11 -> 87,
13 -> 89, 49 -> 125, 51 -> 127, 34 -> 110. The damaged station is as symmetric as the intact one.

- station_l_tl_damaged ... station_r_br_damaged (L 83, 85, 121, 123, 87, 89, 125, 127): wave3_z_station's whole
  station (station_whole), wrecked and cut as station_l_tl ... station_r_br are (origin): the solar panels shot
  away, a bent shard of the straight panel and a scrap of the diagonal one left on the upper struts, the lower
  straight panel broken, the lower diagonal panel gone with the end of its strut; the docking block torn off to a
  stub; the axle housing burnt and pressed in.
- station_end_left_damaged, station_end_right_damaged (L 100, 110): wave2_e's axle ends (station_end), burnt,
  their knob and flanges blackened and dented (stand-alone, as station_end_left and _right).

usage: Blender -b --factory-startup -P wave3_ap_station.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal, Painter  # noqa: E402

orig = kit.load("wave3_z_station")
ends = kit.load("wave2_e")
z = orig.kit
n = z.n
kit.forget(n.MODELS, n.OBJECTS)

ORIGIN = (72, 28)
STATION = z.frame("STATION", 144, ORIGIN)
DAMAGED = kit.frame("STATION_DMG", 144, ORIGIN)


def painter():
    return Painter("station_dmg", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)}, metallic=0.4, roughness=0.4,
                   finish={7: (0.3, 0.4)}, glow={0x74: 0.3, 0x75: 0.35, 0x76: 0.4})


def station_damaged():
    orig.station_whole()
    w.bake()
    dmg = kit.Damage(STATION, DAMAGED, keep=lambda c, r: 24 <= c < 120)
    p = painter()
    # The panels and the docking blocks: shot away (their remnants below).
    kit.remove(["panel_", "dock"])
    # The struts, the webs and the stems lose what the damaged sprite leaves out (the lower diagonal strut's end).
    thin = [o for o in w.meshes() if o.name.startswith(("strut", "web", "stem", "knuckle", "red_rod"))]
    kit.delete_over(thin, dmg.gone)
    parts = w.meshes()
    kit.repaint(parts, dmg, p, walls=2, blur=0, probe=0.4, soot=1, soot_radius=1.5, soot_chance=0.6)
    kit.sink([o for o in parts if o.name.startswith(("axle", "blue_band", "red_clamp"))], dmg, 0.9, min_z=-8.0,
             seed=1.0, min_nz=0.2)
    # The remnants on the left half, mirrored to the right (the damaged sprites are symmetric).
    f = DAMAGED
    rem = []
    shard = kit.remnant("shard_up", f, lambda c, r: 33 <= c <= 46 and 3 <= r <= 11, -0.3, 1.5, p, seed=1.0)
    kit.tilt(shard, (f.X(40.0), f.Y(11.5), 0.0), "X", -24.0)   # bent up off the stem
    rem += shard
    rem += kit.remnant("shard_diag", f, lambda c, r: 49 <= c <= 60 and 6 <= r <= 13, -0.3, 1.4, p, seed=2.0)
    rem += kit.remnant("shard_low", f, lambda c, r: 33 <= c <= 46 and 43 <= r <= 54, -0.6, 1.3, p, seed=3.0,
                       crumple=0.35)
    rem += kit.remnant("dock_stub", f, lambda c, r: 59 <= c <= 68 and 23 <= r <= 33, -3.2, 6.6, p, seed=4.0,
                       edge=1.4, crumple=0.45)
    kit.s.mirror_copies(rem, 0.0, "_r")
    for obj in w.meshes():
        k.smooth(obj, 40)


z.pieced("station_damaged", station_damaged, (144, 56),
         [z.quarter(nm + "_damaged", DAMAGED, c, r) for nm, c, r in orig.STATION_PIECES])


# --- The axle ends -------------------------------------------------------------------------------------------

def end_damaged(mirror):
    """wave2_e's axle end (L 24, or mirrored 34), burnt where the damaged sprite (100, 110) is."""
    ends.station_end(mirror)
    w.bake()
    origin = (12, 28) if not mirror else (132, 28)
    c0 = 0 if not mirror else 120
    dmg = kit.Damage(z.Frame(z.art.STATION, 144, origin), kit.frame("STATION_DMG", 144, origin),
                     keep=lambda c, r: c0 <= c < c0 + 24)
    p = painter()
    kit.repaint(w.meshes(), dmg, p, walls=2, blur=0, probe=0.4, soot=1, soot_radius=1.5, soot_chance=0.6)
    kit.sink(w.meshes(), dmg, 0.7, min_z=-12.0, seed=5.0, min_nz=0.2)
    for obj in w.meshes():
        k.smooth(obj, 50)


n.model("station_end_left_damaged", mask=lambda: DAMAGED.mask((0, 24, 14, 42)))(lambda: end_damaged(False))
n.model("station_end_right_damaged", mask=lambda: DAMAGED.mask((120, 144, 14, 42)))(lambda: end_damaged(True))


if __name__ == "__main__":
    z.run()
