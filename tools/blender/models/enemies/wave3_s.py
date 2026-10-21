"""Enemies of wave 3, batch S (sheet F: SAVARA, SAVARA IV, SAVARA Y), modelled as their sprites look
(models.cfg: yaw=0). SAVARA's boss is polish_savara_boss.py's; the kit is wave3_s_kit.py, the pixels
wave3_s_art.py. (The gun silo, F 43 / 81 / 119, is built by polish_gun_silo.py, the jet with twin tails, F 55,
by polish_jet_twin_tail.py.)

- jet_emerald (F 53): the big green jet of SAVARA and SAVARA Y, nose down the screen: a long fuselage
  with the cockpit near the nose, big wings swept back towards the top, tail planes and a fin.

usage: Blender -b --factory-startup -P wave3_s.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_s_kit as s  # noqa: E402
from wave3_s_kit import art, k, sh, w, n, pal  # noqa: E402


# --- F 53: the big green jet --------------------------------------------------------------------------

def jet_plate(name, frame, mat, skip_rows=(), axis_x=0.0, height=1.1, dihedral=0.05):
    """The wings and tail planes: a thin part over the sprite's outline (rows in skip_rows left out),
    rounded over its edges above and below, rising a little towards the tips."""
    rows = s.regions(frame.g, lambda v, c, r: "." if r in skip_rows else "#")
    polys = sh.outlines(rows, "#", (frame.ox, frame.oy), smooth=2, epsilon=0.3, min_area=1.0)
    obj = sh.inflate(name, polys, mat, sh.round_profile(0.45, max_height=height, min_height=0.2), bottom=0.55,
                     base=-0.1, rim=0.12, spacing=0.55,
                     z_fn=lambda x, y, z: z + dihedral * abs(x - axis_x))
    # The underside follows the dihedral too.
    for v in obj.data.vertices:
        if v.co.z < -0.1:
            v.co.z += dihedral * abs(v.co.x - axis_x)
    return [k.smooth(obj, 50)]


def jet_fuselage(name, prof, mat, axis_x, nose_y, squash=0.75, z=0.0):
    """A round fuselage along y from the nose (nose_y) up the screen: prof [(distance from the nose,
    radius)]."""
    return w.lathe_axis(name, k.profile(prof, 0.5), mat, (axis_x, nose_y, z), (0, 1, 0), 24, squash=squash)


def jet_fin(name, x, profile, mat, thickness=1.2):
    """An upright fin at x: profile [(y, z)], counter-clockwise seen from +x."""
    return s.prism_x(name, profile, x - thickness / 2, x + thickness / 2, mat, bevel=min(0.4, thickness * 0.3),
                     segments=2, angle=35)


J53 = s.Frame(art.JET53, 24, (12, 14))
J53_PAINT = s.Frame(art.JET53, 24, (12, 14)).fill({0x22})


@s.model("jet_emerald", mask=lambda: J53.mask())
def jet_emerald():
    """The big green jet of SAVARA and SAVARA Y, nose down the screen: a long round fuselage, big wings
    swept back towards the top of the screen, small tail planes and an upright fin along the top, a
    dark canopy near the nose."""
    f = J53
    ax = 0.5
    p = s.Painter("jet53", shades={2: (2, 4, 6, 8, 10, 12)}, metallic=0.45, roughness=0.35)
    green = p(0x27)
    dark = p(0x22)
    glass = pal("jet53_glass", 0x22, metallic=0.3, roughness=0.05)
    glint = pal("jet53_glint", 0x2b, metallic=0.1, roughness=0.1, glow=0.5)
    plate = jet_plate("wing", f, green, skip_rows=(0, 1), axis_x=ax)
    body = jet_fuselage("fuselage", [(0.0, 0.05), (0.5, 0.8), (1.0, 1.2), (3.0, 2.0), (5.0, 2.7), (8.0, 3.1),
                                     (14.0, 3.2), (18.0, 2.4), (20.0, 2.0), (23.0, 1.3), (24.4, 0.7), (24.8, 0.05)],
                        green, ax, f.bottom(26) + 0.4, squash=0.72)
    fin = jet_fin("fin", ax, [(4.0, 0.6), (13.7, 0.6), (13.9, 1.4), (13.3, 4.4), (12.2, 4.6), (7.0, 1.9)], green,
                  thickness=1.2)
    w.sphere("canopy", (ax, f.Y(17.4), 1.65), (1.4, 2.4, 1.2), glass, 20, 10)
    w.sphere("glint", (ax - 0.3, f.Y(16.6), 2.65), (0.4, 0.7, 0.2), glint, 10, 5)
    for obj in plate:
        s.paint_sprite(obj, J53_PAINT, p, wall_steps=2, under=dark, probe=0.4, blur=1)
    s.paint_sprite(body, J53_PAINT, p, wall_steps=1, under=dark, blur=1)
    s.paint_sprite(fin, f, p, wall_steps=1, under=dark)
    n.merge_by_material()


s.run()
