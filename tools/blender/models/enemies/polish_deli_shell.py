"""The purple shells DELI's towers lob (sheet C sprite 19, 1x1: 12 x 14 pixels; enemy 556 of episodes 1 and 3, on ground
2, where a ground launcher's launches go; DELIANI (the DELI of the timed battles) and New Deli; one frame, not
animated), modelled (2026-10-22; until now it had no model and was drawn as a flat volume).

What it is: the capsule at the right end of either of DELI's towers (U 43 of tower A, U 55 of tower B: enemies 250
and 257, DELIANI's and New Deli's events 3072, 3548, 3772 and 3800, ground) launches one every 50 game frames from its
own place. It starts out to the right and up ((1, -1); with the ground's scroll it moves across the screen level), and
its cyclic accelerations (xcaccel -16, ycaccel 10, no limits) bend that into a fall: its x speed drops by one every 16
game frames, its y speed grows by one every 10, so it arcs out to the right, then falls down the screen and back to the
left faster and faster: a lobbed shell. Armour 3. No other enemy shows the sprite (catalog.json); it is no other
sprite's pixels mirrored or turned. Not in episode 6 (no level there takes DELI's tower waves).

As the sprite draws it (ramp 5, the purple of DELI's tower capsules and the tank pods' coils; lit from the upper left,
its highlight down column 4): a shell lying along the screen, its blunt nose down the screen. At its back (rows 0-5) a
broad cap, the full 12 pixels wide over rows 2-5 and domed over rows 0-1, its left side mid purple (0x55), its middle
lighter (0x57, 0x59-0x5b, a white glint 0x5f at row 4) and its right side dark (0x52-0x54); a dark band across its
lower edge (row 5); under it a bright collar (row 6, 0x5b-0x5e); then the body (rows 7-12), 7 pixels wide with its
outline narrowing to 4 at the nose (row 12, 0x58), its middle 0x57 with a light line (0x5a) left of it.

Built as a turned body lying along y (lathed about the screen's y axis, its section an ellipse 0.62 times as high as it
is wide, so it stays low under DELI's background 2): the cap (a cylinder of radius 6 with a flattened dome, an
elliptical arc of 3.2 over its last pixels, and a rounded rim curling under it), the collar a polished bead, the body
tapering in a smooth convex line to a blunt rounded nose, its point a shade darker. Each part is painted by its facets
(polish_orb_red.band_split: smooth borders) in the sprite's own shades of ramp 5: lighter towards the camera and on
the sun's side, darker underneath, the rim curling under the cap (seen by the game's slanted camera as the sprite's
dark band) dark; glossy, glowing a little in its own purple so that the camera's side of it doesn't read black.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the axis is x = 0 (the outline is
columns 0-11). The game centres the model in height (its axis lies at z = 0).

models.cfg (new): model deli_shell enemies/deli_shell.glb; sprite c 19 deli_shell yaw=0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_C.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import vertex_normals  # noqa: E402

NAME = "deli_shell"
SQUASH = 0.62          # the sections' height over their width
SEGMENTS = 40          # points round each ring

# The cap: its radius, where its cylinder ends and its dome begins (y), the dome's length (an elliptical arc to the
# apex), the rim under it ((y, radius) from the inside out, curling under: dark where it faces down the screen, below
# RIM_DARK).
CAP_R = 6.05
CAP_DOME_Y, CAP_DOME_B = 3.75, 3.2
CAP_RIM = [(0.45, 4.2), (0.47, 5.0), (0.55, 5.45), (0.7, 5.75), (0.9, 5.94), (1.12, 6.03)]
RIM_DARK = 1.2
# The collar: a bead round the body between the cap and the body, (y, radius) from bottom to top.
COLLAR = [(-0.22, 4.15), (-0.14, 4.55), (0.0, 4.82), (0.2, 4.92), (0.4, 4.82), (0.54, 4.5), (0.6, 4.1)]
# The body, from inside the collar down to the nose's point: (y, radius).
BODY = [(0.35, 4.55), (0.0, 4.68), (-0.6, 4.8), (-1.4, 4.72), (-2.2, 4.45), (-3.0, 4.05), (-3.8, 3.62), (-4.6, 3.22),
        (-5.25, 2.95), (-5.7, 2.75), (-6.05, 2.45), (-6.4, 2.05), (-6.65, 1.6), (-6.85, 1.0), (-6.97, 0.45),
        (-7.02, 0.0)]
NOSE_Y, TIP_Y = -5.85, -6.93   # the nose's lighter cap below NOSE_Y, its darker point below TIP_Y

# The shades (palette index, emission strength).
SHADES = {"dark": (0x52, 0.03), "under": (0x53, 0.04), "low": (0x54, 0.05), "mid": (0x57, 0.07),
          "nose": (0x58, 0.08), "top": (0x59, 0.09), "crest": (0x5a, 0.11), "collar": (0x5c, 0.14),
          "glint": (0x5e, 0.18)}


def materials():
    pal = k.level_palette()
    return {key: k.material(f"shell_{key}", palette=index, metallic=0.4 if key not in ("dark", "under") else 0.3,
                            roughness=0.3 if key not in ("dark", "under") else 0.45, emission=pal[index],
                            emission_strength=glow)
            for key, (index, glow) in SHADES.items()}


def lathe_y(name, profile):
    """A body turned about the y axis: profile [(y, radius), ...] in increasing y; the ends close on the axis."""
    return k.lathe(name, [(y, max(r, 0.0)) for y, r in profile], None, segments=SEGMENTS, squash=SQUASH)


def light(n):
    """A facet's lightness: towards the camera (and a little the sun's side, as the sprite's highlight left of the
    middle) light, underneath dark."""
    return n.z - 0.18 * n.x


def cap(m):
    profile = list(CAP_RIM)
    # The cylinder, then the dome (an elliptical arc to the apex).
    profile += [(y, CAP_R) for y in (1.25, 1.6, 2.0, 2.6, 3.2, CAP_DOME_Y)]
    steps = 14
    for i in range(1, steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((CAP_DOME_Y + CAP_DOME_B * math.sin(t), CAP_R * math.cos(t) if i < steps else 0.0))
    obj = lathe_y("cap", profile)
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        if v.co.y < RIM_DARK and n.y < -0.18:
            values.append(-9.0)                          # the rim curling under: dark (the sprite's row 5)
        else:
            values.append(light(n))
    band_split(obj, values, [(-99.0, m["under"]), (-1.5, m["low"]), (-0.35, m["mid"]), (0.45, m["top"]),
                             (0.86, m["crest"])])
    return k.smooth(obj, 55)


def collar(m):
    obj = lathe_y("collar", COLLAR)
    values = [light(n) for n in vertex_normals(obj)]
    band_split(obj, values, [(-99.0, m["low"]), (-0.3, m["crest"]), (0.35, m["collar"]), (0.82, m["glint"])])
    return k.smooth(obj, 60)


def body(m):
    obj = lathe_y("body", BODY)
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        y = v.co.y
        if y < TIP_Y:
            values.append(-0.3)                          # the nose's darker point
        elif y < NOSE_Y:
            values.append(9.0 if light(n) > -0.4 else -2.0)  # the nose's lighter cap
        else:
            values.append(light(n))
    band_split(obj, values, [(-99.0, m["under"]), (-6.0, m["dark"]), (-0.6, m["low"]), (-0.1, m["mid"]),
                             (0.55, m["top"]), (0.9, m["crest"]), (5.0, m["nose"])])
    return k.smooth(obj, 55)


def build():
    options = k.args()
    k.reset()
    m = materials()
    parts = triangulate([cap(m), collar(m), body(m)])
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_C.png")
        mk.compare("deli_shell (C 19)", mk.coverage(parts, 12, 14), k.sprite_mask(sheet, 19, large=False))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
