"""GYGES' and MISTAKES' violet shell (sheet G sprite 55, 2x2: its 23 x 20 pixels at the top of the 24 x 28 cell; not
animated), polished (2026-10-22, round 34; it replaces wave3_r_beasts.py's violet_shell(), a relief inflated from the
sprite and painted by its shades). models.cfg: model violet_shell enemies/violet_shell.glb and sprite g 55
violet_shell yaw=0 (both unchanged: drawn centred in height, no origin). No other enemy, launched ones included, shows
G 55; it is no other sprite's pixels mirrored, turned or in other ramps (no upscale exists: built from the sprite).

Where the levels put it: custom events (enemy 0 with the event's sprite, armour 10, link 201, then event 60 makes it
special: shooting it sets global flag 1): GYGES' event 51 (the top layer, moving with background 3) at t1280, 3080,
3480 (x 220, 60, 160) and MISTAKES' event 49 (the ground) at t180 and 480 (x 40, 220). No episode 6 level makes it.

As the sprite draws it (columns and rows): a violet carapace (ramp 5, outlined in 0x50), symmetric about column 11: a
ribbed dome at its back (columns 6-16, rows 0-9; two light ribs either side of a groove down its middle, darker ones
at its sides), shoulder plates at its sides (1-5 and 17-21, rows 3-12) with a light ridge and a little dark horn on
top, a dark band across its middle with three red dots (0x43) over the front plate, in it a blue gem (ramp 9, columns
9-13, rows 13-15) in a dark socket, and two front lobes (rows 16-19) parted by a notch under the gem.

Built for the game's camera (polish_gyges_wall's picture-plane heightfield and its shear, y - z tan 20, so that the
camera sees each point where the sprite draws it): one solid over the sprite's outline, its top the shell's shapes
joined by a smooth maximum (a low rim all round, the dome highest at the back, the shoulders, the band, the front
plate, the lobes) cut down to the outline, the sprite's shading as a little relief (the dome's ribs, the ridges), the
dark lines between the back's plates sunk; painted by the sprite's shades (LIFT lighter, and lighter where the game's
sun lights a face less: the drawn light and the game's don't add up), its outline and the gem's socket dark; the gem
a lens glowing blue (0x93, 0.45) with a hotter core (0x96, 0.6), the dots small glowing lenses (0x43, 0.3). Its
finish is polish_violet_pincer's violet (metallic 0.3). 7.97 pixels tall with its bottom at z 0: drawn centred on the
ground enemies' layer (4 pixels up) it rests on the ground (the game lifts what reaches below it to 0.3); on GYGES'
top layer it flies as its top enemies do.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; origin at the sprite's centre
(pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave3_r_beasts.py (all of it: the shell is the last model it builds: delete it) and with it wave3_r_kit.py and
wave3_r_art.py (only wave3_r_beasts.py imports the kit, only the kit the pixels; the art's other pictures, BUNKER,
BUNKER_OPEN, TOWER and MORPH_*, have no reader left).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its outline as the camera sees
it against the sprite in enemy_G.png), --preview <prefix>.
"""
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (the picture-plane heightfields, painting and shear of GYGES' wall)
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402

# The sprite (G 55): each pixel its palette index as two hex digits ('..' none), its rows 0-19 (the rest is empty).
PIXELS = """
....................505050......................
................50505a5c5a5050..................
..............50575b5c585c5b5950................
......50....5059585d5a575a5d585950....50........
....505250505a57575c5a575a5c57575a50505250......
....505c5a545957575c5b575b5c575759545a5c50......
..505a5c58535756565a5b595b5a56565653585b5950....
5057545a5753565659565555555659565653575a545750..
5053575b5752555853545556555453585552575b575350..
5056555b58505353535456435654535353..585b555650..
5054555854535152535543564355535251535458555450..
5052555654535252525254585452525252535456555250..
..505254525251545152545654525154515252545250....
5053505451515156535592579155535650505054505350..
5054505651545558509491959093505855545156515450..
5053515254515356505093949250505653515452515350..
5053525152545153545050505050545351545251525350..
..505252515253515350......505351535251525250....
....505252515252515250..505251525251525250......
......50505050505050......50505050505050........
"""
AXIS = 11                         # the column it is drawn symmetric about (x -0.5)
# Its shapes over the ground (z 0): middle (column, row), radii, height, angle, power.
BODY = ((11.0, 10.2), (11.7, 9.9), 4.2, 0.0, 0.5)         # the shell's rim, low all round
DOME = ((11.0, 4.8), (6.2, 5.4), 7.8, 0.0, 0.55)          # the ribbed dome at its back
SHOULDERS = ((2.9, 7.6), (2.9, 5.3), 5.6, 4.0, 0.5)       # the left shoulder plate (the right one its mirror image)
BAND = ((11.0, 10.6), (8.6, 2.8), 5.4, 0.0, 0.5)          # the band across its middle, the red dots on it
FRONT = ((11.0, 14.2), (9.8, 3.4), 4.8, 0.0, 0.5)         # the plate in front, the gem in it
LOBES = ((5.4, 16.9), (4.6, 2.6), 3.8, -8.0, 0.5)         # the left front lobe (the right one its mirror image)
RIBS = (0.16, 0.55)               # the sprite's shading as relief (ribs, ridges, grooves): per shade, limit (pixels)
GROOVE = 0.8                      # the sprite's darkest lines between its back's plates sunk this deep
GROOVE_ROWS = 12                  # (its rows 0-12: lower down they are its front's dark shading)
GEM = ((11.0, 14.0), (2.5, 1.5, 0.95))       # the gem's middle and radii; its socket sunk SOCKET round it
SOCKET = 0.9
DOTS = [(11.0, 9.0), (10.0, 10.0), (12.0, 10.0)]     # the three red dots
VIOLET = [0x51, 0x53, 0x55, 0x57, 0x59, 0x5b, 0x5d]
FINISH = (0.3, 0.26)              # polish_violet_pincer's violet: metallic, roughness
LIFT, COMP = 2.0, 1.6


def P(c, r):
    return c + 0.5 - 12.0, 13.5 - r


def shapes(X, Y):
    def d(spec, mirror=False):
        (c, r), radii, height, angle, power = spec
        if mirror:
            c, angle = 2 * AXIS - c, -angle
        return gw.dome(X, Y, P(c, r), radii, height, angle, power)
    out = d(BODY)
    for spec in (BAND, FRONT):
        out = gw.smax(out, d(spec), 1.0)
    for spec in (SHOULDERS, LOBES):
        out = gw.smax(out, gw.smax(d(spec), d(spec, True), 0.5), 0.8)
    out = gw.smax(out, d(DOME), 1.2)
    (gc, gr), (gx, gy, _) = GEM
    return out - SOCKET * gw.dome(X, Y, P(gc, gr), (gx + 0.5, gy + 0.5), 1.0)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    pic = gw.Pic(gw.parse(PIXELS), -12.0, 14.0)
    opaque = pic.a >= 0
    dark = pic.any(0x50)
    violet = pic.ramp(5) & ~dark
    region = gw.Region(pic, opaque, sigma=0.5)
    soft = gw.blur(gw.fill(pic.shade(), violet), 0.6)
    broad = gw.blur(gw.fill(pic.shade(), violet), 2.0)
    rows = np.arange(pic.h)[:, None] + np.zeros((1, pic.w), int)
    outline = dark & ~gw.erode(opaque, 1)
    (gc, gr), (gx, gy, _) = GEM
    cols = np.arange(pic.w)[None, :] + np.zeros((pic.h, 1), int)
    socket = dark & (((cols - gc) / (gx + 1.6)) ** 2 + ((rows - gr) / (gy + 1.6)) ** 2 < 1.0)
    groove = gw.blur((dark & gw.erode(opaque, 1) & (rows <= GROOVE_ROWS)).astype(float), 0.5)

    def top(X, Y):
        h = shapes(X, Y) * gw.smoothstep(0.0, 1.0, region.depth(X, Y))
        rel = np.clip(RIBS[0] * (pic.sample(soft, X, Y) - pic.sample(broad, X, Y)), -RIBS[1], RIBS[1])
        h = h + rel * gw.smoothstep(1.0, 3.0, h)
        h = h - GROOVE * pic.sample(groove, X, Y) * np.clip(h / 3.0, 0.0, 1.0)
        return np.maximum(h, 0.05)
    plate = gw.Plate((-12.0, 12.0, -6.5, 14.0), top, None, lambda X, Y: region.inside(X, Y))
    mesh_obj, kinds, _ = plate.mesh("violet_shell", lambda X, Y: np.ones_like(X, dtype=bool))
    # Painted by the sprite's shades (lifted, lighter where the sun lights it less), its dark lines dark.
    mats = {s: gw.pal("violet_shell", s, *FINISH) for s in VIOLET}
    mats[0x50] = gw.pal("violet_shell", 0x50, *FINISH)
    centres, normals = gw.face_data(mesh_obj)
    X, Y = centres[:, 0], centres[:, 1]
    s = pic.sample(soft, X, Y) + LIFT + COMP * (gw.LIT_MEAN - gw.sun_on(normals))
    shade_keys = gw.nearest(s, VIOLET)
    line = pic.sample(gw.blur((outline | socket).astype(float), 0.75), X, Y)
    keys = []
    for i in range(len(X)):
        keys.append(0x50 if kinds[i] != 0 or line[i] > 0.42 else int(shade_keys[i]))
    gw.set_materials(mesh_obj, keys, mats)
    parts = [mesh_obj]
    # The gem in its socket, glowing blue, a lighter core; the three red dots, glowing a little.
    (gc, gr), (gx, gy, gz) = GEM
    x, y = P(gc, gr)
    z = float(top(np.array([x]), np.array([y]))[0])
    gem = gw.pal("violet_shell_gem", 0x93, 0.1, 0.12, 0.45)
    hot = gw.pal("violet_shell_gem", 0x96, 0.0, 0.1, 0.6)
    parts.append(gw.ellipsoid("gem", (x, y, z - 0.3), (gx, gy, gz), gem, count=8, around=28))
    parts.append(gw.ellipsoid("gem_hot", (x - 0.5, y + 0.3, z + 0.35), (gx * 0.4, gy * 0.42, 0.3), hot, count=6,
                              around=20))
    dot = gw.pal("violet_shell_dot", 0x43, 0.1, 0.3, 0.3)
    for i, (c, r) in enumerate(DOTS):
        x, y = P(c, r)
        z = float(top(np.array([x]), np.array([y]))[0])
        parts.append(gw.ellipsoid("dot%d" % i, (x, y, z - 0.15), (0.62, 0.62, 0.42), dot, count=6, around=16))
    for o in parts[1:]:
        k.smooth(o, 80)
    gw.shear_to_camera(parts)
    triangulate(parts)
    model = join(parts, "violet_shell")
    drop_unused([model])
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_G.png") if os.path.isdir(sheets) else sheets
        mk.compare("violet_shell (G 55, the camera's view)",
                   gw.own_coverage(lambda X, Y: region.inside(X, Y) & (top(X, Y) > 0.3), 24, 28, -12.0, 14.0),
                   k.sprite_mask(sheet, 55))
    mk.report("violet_shell", [model], os.path.join(out, "violet_shell.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "violet_shell", [model])


if __name__ == "__main__":
    build()
