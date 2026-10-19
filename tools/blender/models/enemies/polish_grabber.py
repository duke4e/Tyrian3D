"""The grey grabber of TYRIAN, FLEET, ASSASSIN, BONUS, TYRIAN X and SAVARA, drawn from two sprites of sheet 2 side
by side (2x2 each): its left half, 123, and its right half, 125, 24 pixels right of it (enemies 8 and 9 of episodes
1, 3 and 5; ground2, ground and top layers; not animated), polished (2026-10-19; it replaces wave2_f_more.py's
grabber_whole(), pillows inflated from the outline with tubes laid on). models.cfg: model grabber_left /
grabber_right ... origin; sprite 2 123 grabber_left yaw=0, sprite 2 125 grabber_right yaw=0.

The levels usually put it 16 pixels below the walker (2 85 and 87, polish_walker.py; 24 pixels in BONUS) as the
machine's lower half, and draw it over the walker: its neck hides the walker's eye dome (the walker's DOME, 3.75
pixels round the walker's column 23, row 21.6, 4.6 high, its lens up to 5.0). The neck therefore stands where the
sprite draws it, 7.6 high over the dome's whole plan, the collar in front of it 5.6-6.4 high and the dark hip beam
under the collar 4.9 high, so that the dome stays inside the grabber in 3D too (checked in the game camera with the
walker placed above it).

As the sprites draw it (the whole 48 x 28 picture, columns 12-34; symmetric about the edge between its columns 22
and 23, the walker's axis):
- a grey neck (columns 18-27 of rows 0-5), a glowing blue window in its top (columns 21-24 of rows 1-4), lit along
  its left edge;
- the neck's base flaring into a collar (rows 5-6, columns 16-29), lit on the left, its back band running across;
- the glowing blue bar from under the collar down between the shoulders to a point (columns 21-24 of rows 6-13),
  its highlight left of its middle (column 22), its right side dark steel blue (column 24);
- a dark hip beam across under the collar (rows 7-8, columns 14-31);
- grey shoulders either side of the bar (columns 15-19 and 26-30 of rows 9-10), lit on top;
- a light blue strap across each leg's top (row 11), teal at its ends, bending down the leg's outer side as a
  steel-blue rail (column 13, rows 12-16), a dark gap between it and the leg;
- two legs (columns 12-18 and 27-34 of rows 11-26): grey, a dark seam across them (row 14), their inner edge light
  grey then teal down to the foot, and a blue hooked shoe round the foot's outer side and under it (rows 20-26), dark
  blue in front;
- a dark keel hanging between the legs (columns 19-26 of rows 13-20), a grey ridge down it.

Built as a hard-surface machine in the walker's style (they make one machine): solids over outlines traced from the
sprite (relief(): neck, collar, hip beam, shoulders, legs, the webs under the rails, keel), bars lofted along paths
(polish_walker.blade(): the glowing bar, the straps, strips, shoes, the ridge), boxes (the window). The whole is cut
along the sprites' edge (x = 0 here) into the two halves (polish_arch.py's cut(): the halves keep the whole's shading
across the cut), each moved so that its sprite's centre is its origin. The bar and the window glow in their blue.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0). The
whole's x = 0 is the edge between the sprites (column 24 of the picture), y = 0 its middle (row 14's top edge): a
point (column, row) of the picture's pixel grid is (c - 24, 14 - r) (px()). The grabber is built about x = AXIS (the
picture's column 23's left edge), its right half mirroring its left.

Replaces wave2_f_more.py's grabber (X(), Y(), GRABBER, grabber_whole(), grabber_left(), grabber_right(), WHOLE and
whole()): with them gone nothing is left in that file; remove it. wave3_p_art.py's GRABBER (the same pixels, which
nothing reads) can go too.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_2.png), --preview <prefix> (the whole's and each half's views).
"""
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_walker import blade  # noqa: E402

AXIS = -1.0
PIECES = [("grabber_left", 123, (-24.0, 0.0, -14.0, 14.0)), ("grabber_right", 125, (0.0, 24.0, -14.0, 14.0))]


def px(c, r):
    """A point of the whole picture's pixel grid (column, row) in the whole's coordinates."""
    return (c - 24.0, 14.0 - r)


def mirror_c(c):
    """The column mirrored about the grabber's axis (the edge between columns 22 and 23)."""
    return 46.0 - c


def symmetric(left, smooth=2):
    """A closed outline from its left half (column, row), from the top middle round to the bottom middle."""
    full = list(left) + [(mirror_c(c), r) for c, r in reversed(left[1:-1])]
    return ccw(chaikin([px(c, r) for c, r in full], smooth))


def outline(points, mirrored=False, smooth=1):
    """An outline given by its left side's points (column, row), or their mirror image."""
    pts = [px(mirror_c(c), r) for c, r in reversed(points)] if mirrored else [px(c, r) for c, r in points]
    return ccw(chaikin(pts, smooth) if smooth else pts)


def path3(points, mirrored=False):
    """3D points (column, row, height), optionally mirrored about the axis."""
    out = []
    for c, r, z in points:
        x, y = px(mirror_c(c) if mirrored else c, r)
        out.append(Vector((x, y, z)))
    return out


# --- The parts' outlines and heights (column, row of the picture) --------------------------------------------------
NECK = [(23.0, 0.35), (19.9, 0.35), (18.85, 0.75), (18.4, 1.6), (18.35, 4.2), (18.5, 5.4), (23.0, 5.4)]
NECK_TOP, NECK_RIM, NECK_CROWN = 7.6, 1.1, 0.3
WINDOW = (20.95, 25.05, 0.95, 4.7)     # columns from, to, rows from, to
# The collar: the neck's flared base, notched in front where the bar comes out from under its back band.
COLLAR = [(23.0, 4.5), (18.4, 4.5), (17.2, 5.25), (16.45, 6.2), (16.35, 7.25), (20.55, 7.25), (20.65, 5.95),
          (23.0, 5.95)]
COLLAR_TOP, COLLAR_FALL, COLLAR_RIM = 6.35, 0.012, 0.8  # its height at the axis, falling off to the sides
BEAM = [(23.0, 6.65), (14.7, 6.65), (14.25, 7.1), (14.25, 9.25), (14.7, 9.65), (19.95, 9.65), (19.95, 12.95),
        (23.0, 12.95)]
BEAM_TOP = 4.9
SHOULDER = [(15.2, 8.75), (19.9, 8.75), (20.4, 9.25), (20.4, 11.9), (19.9, 12.55), (18.7, 12.55), (18.45, 11.35),
            (14.75, 11.35), (14.75, 9.2)]
SHOULDER_TOP, SHOULDER_RIM = 5.7, 0.8
# The bracket over each leg's top and down its outer side (the sprite's row 11 and column 13): a flat strap
# (column, row, height), light blue across the top (HIP_LIGHT: columns), teal at its ends, steel blue down the side.
BRACKET = [(19.1, 11.5, 4.75), (17.0, 11.5, 4.8), (14.6, 11.5, 4.75), (13.55, 11.75, 4.6), (13.45, 12.9, 4.35),
           (13.45, 15.0, 4.1), (13.45, 16.95, 3.8)]
BRACKET_W = [0.62, 0.66, 0.66, 0.62, 0.55, 0.55, 0.5]
HIP_LIGHT = (15.4, 18.6)
BRACKET_DOWN = 12.15                           # steel blue below this row
WEB = [(12.95, 11.2), (14.95, 11.2), (14.95, 17.3), (12.95, 17.3)]  # the dark web between the strap and the leg
# The leg: a boot-shaped block, widening at the foot; its height along it (row, top).
LEG = [(14.95, 11.9), (18.35, 11.9), (18.35, 24.35), (17.8, 24.75), (14.1, 24.45), (13.2, 23.7), (12.95, 20.5),
       (13.4, 19.65), (14.95, 19.2)]
LEG_TOPS = [(11.9, 4.5), (16.0, 4.35), (20.0, 4.0), (24.7, 3.45)]
LEG_RIM, LEG_CROWN = 0.75, 0.3          # its rounded edge, its middle raised a little
LEG_SEAM = 14.55                               # the dark seam across the leg (the sprite's row 14)
STRIP = (17.65, 12.2, 24.1, 0.42)              # the inner strip: column, rows from, to, half-width
STRIP_TEAL = 14.6                              # teal below this row, light grey above
# The shoe: blue, round the foot's outer side and under it (column, row, height) and its half-widths.
SHOE = [(12.85, 19.7, 2.95), (12.8, 21.6, 2.85), (13.0, 23.4, 2.65), (13.85, 25.0, 2.35), (15.2, 25.55, 2.2),
        (16.8, 25.6, 2.15), (18.0, 25.5, 2.1)]
SHOE_W = [0.72, 0.88, 1.0, 1.15, 1.22, 1.22, 1.05]
KEEL = [(23.0, 12.45), (18.6, 12.45), (18.6, 16.8), (19.4, 18.4), (20.3, 19.6), (21.4, 20.45), (23.0, 20.45)]
KEEL_TOPS = [(12.45, 3.6), (16.0, 3.2), (20.45, 1.7)]
KEEL_FALL = 0.32                               # the facets' fall per pixel from the ridge
RIDGE = [(23.45, 13.6, 3.6), (23.45, 15.9, 3.25), (23.45, 17.9, 2.8), (23.45, 19.8, 2.0)]
RIDGE_W = [0.4, 0.5, 0.45, 0.15]
# The glowing bar: from under the collar's back band down between the shoulders to its point.
BAR = [(23.0, 5.0, 6.75), (23.0, 6.6, 6.45), (23.0, 8.6, 6.15), (23.0, 10.8, 5.95), (23.0, 12.6, 5.7),
       (23.0, 13.5, 5.45), (23.0, 14.15, 5.15)]
BAR_W = [1.8, 1.8, 1.78, 1.74, 1.55, 1.05, 0.25]
BOLTS = [(16.0, 9.7), (18.9, 9.7)]             # rivets on the left shoulder's top


def interp(table, v):
    """Piecewise linear through (key, value) rows, clamped."""
    if v <= table[0][0]:
        return table[0][1]
    for (a, za), (b, zb) in zip(table, table[1:]):
        if v <= b:
            return za + (zb - za) * (v - a) / (b - a)
    return table[-1][1]


def row_of(y):
    return 14.0 - y


# --- Materials -----------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    steel = dict(metallic=0.55, roughness=0.3)
    return {
        "grey": k.material("grabber_grey", palette=0x08, **steel),
        "grey_mid": k.material("grabber_grey_mid", palette=0x06, **steel),
        "grey_light": k.material("grabber_grey_light", palette=0x0a, **steel),
        "grey_dark": k.material("grabber_grey_dark", palette=0x04, **steel),
        "dark": k.material("grabber_dark", palette=0x02, metallic=0.45, roughness=0.45),
        "glow": k.material("grabber_glow", palette=0x9b, metallic=0.1, roughness=0.18, emission=pal[0x9b],
                           emission_strength=0.9),
        "glow_light": k.material("grabber_glow_light", palette=0x9d, metallic=0.1, roughness=0.15, emission=pal[0x9d],
                                 emission_strength=1.0),
        "glow_side": k.material("grabber_glow_side", palette=0x38, metallic=0.4, roughness=0.25),
        "strap_light": k.material("grabber_strap_light", palette=0x9e, metallic=0.3, roughness=0.2, emission=pal[0x9d],
                          emission_strength=0.45),
        "teal": k.material("grabber_teal", palette=0x84, metallic=0.45, roughness=0.25),
        "blue": k.material("grabber_blue", palette=0x3a, metallic=0.5, roughness=0.28),
        "blue_dark": k.material("grabber_blue_dark", palette=0x65, metallic=0.45, roughness=0.36),
        "seam": k.material("grabber_seam", palette=0x01, metallic=0.4, roughness=0.5),
    }


# --- The parts -----------------------------------------------------------------------------------------------------

def neck(m):
    def height(x, y, d):
        crown = NECK_CROWN * max(0.0, 1.0 - ((x - AXIS) / 4.8) ** 2)
        return NECK_TOP - NECK_RIM + NECK_RIM * round_edge(d, NECK_RIM) + crown
    body = relief("neck", [symmetric(NECK)], height, m, paint=lambda x, y, d: "grey_dark" if d < 0.3 else "grey",
                  side="grey_dark", bottom=0.3, spacing=0.45, band=1.4, borders=[(lambda x, y, d: d, 0.3)])
    # The window: a glowing blue glass panel in a dark frame, a light glint down its left edge.
    c0, c1, r0, r1 = WINDOW
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    top = NECK_TOP + NECK_CROWN * 0.6
    frame = mk.box("window_frame", x0 - 0.35, x1 + 0.35, y0 - 0.35, y1 + 0.35, top - 1.0, top + 0.12, m["dark"])
    mk.bevel(frame, 0.22, 2, 35.0)
    glass = mk.box("window", x0, x1, y0, y1, top - 0.6, top + 0.3, m["glow"])
    mk.bevel(glass, 0.32, 3, 35.0)
    mk.shade(glass, 40.0)
    glint = mk.box("window_glint", x0 + 0.12, x0 + 0.85, y0 + 0.35, y1 - 0.2, top - 0.2, top + 0.42, m["glow_light"])
    mk.bevel(glint, 0.2, 2, 35.0)
    return [body, frame, glass, glint]


def collar(m):
    def height(x, y, d):
        z = COLLAR_TOP - COLLAR_FALL * (x - AXIS) ** 2
        return z - COLLAR_RIM + COLLAR_RIM * round_edge(d, COLLAR_RIM)
    return relief("collar", [symmetric(COLLAR, 1)], height, m,
                  paint=lambda x, y, d: "grey_dark" if d < 0.28 else "grey_light" if y > px(0, 5.4)[1] else "grey",
                  side="grey_dark", bottom=0.3, spacing=0.4, band=1.3,
                  borders=[(lambda x, y, d: d, 0.28), (lambda x, y, d: y, px(0, 5.4)[1])])


def beam(m):
    return relief("beam", [symmetric(BEAM, 1)], lambda x, y, d: BEAM_TOP - 0.5 + 0.5 * round_edge(d, 0.5), m,
                  paint=lambda x, y, d: "dark", side="dark", bottom=0.2, spacing=0.5, band=1.0)


def shoulders(m):
    out = []
    for mirrored in (False, True):
        def height(x, y, d):
            return SHOULDER_TOP - SHOULDER_RIM + SHOULDER_RIM * round_edge(d, SHOULDER_RIM) + 0.15 * min(1.0, d / 1.5)
        s = relief("shoulder", [outline(SHOULDER, mirrored)], height, m,
                   paint=lambda x, y, d: "grey" if d < 0.32 else "grey_light", side="grey_dark", bottom=0.3,
                   spacing=0.4, band=1.2, borders=[(lambda x, y, d: d, 0.32)])
        out.append(s)
        for c, r in BOLTS:
            x, y = px(mirror_c(c) if mirrored else c, r)
            out.append(mk.dome("bolt", (x, y), (0.42, 0.42, 0.3), SHOULDER_TOP + 0.05, m["grey_dark"], 10, 3))
    return out


def brackets(m):
    """The strap over each leg's top and down its outer side, and the dark web under its side, between it and the
    leg."""
    out = []
    lo, hi = HIP_LIGHT
    for mirrored in (False, True):
        strap = blade("bracket", path3(BRACKET, mirrored), BRACKET_W, 0.5, m["teal"], power=3.2, segments=14,
                      flat=0.8, step=0.35)
        light = sorted((px(mirror_c(hi), 0)[0], px(mirror_c(lo), 0)[0])) if mirrored else (px(lo, 0)[0], px(hi, 0)[0])
        down = px(0, BRACKET_DOWN)[1]
        mk.paint(strap, lambda cc, n, light=light, down=down: m["blue"] if cc.y < down else
                 m["strap_light"] if light[0] < cc.x < light[1] and n.z > 0.3 else None)
        out.append(strap)
        web = relief("web", [outline(WEB, mirrored, 0)], lambda x, y, d: 2.4, m, paint=lambda x, y, d: "dark",
                     side="dark", bottom=0.0, spacing=0.5)
        out.append(web)
    return out


def legs(m):
    out = []
    for mirrored in (False, True):
        # The leg block.
        def height(x, y, d):
            top = interp(LEG_TOPS, row_of(y))
            return top - LEG_RIM + LEG_RIM * round_edge(d, LEG_RIM) + LEG_CROWN * mk.smoothstep(0.7, 1.7, d)
        leg = relief("leg", [outline(LEG, mirrored)], height, m,
                     paint=lambda x, y, d: "grey_dark" if d < 0.3 else "grey_mid" if row_of(y) > 20.2 else "grey",
                     side="grey_dark", bottom=0.0, spacing=0.4, band=1.3,
                     borders=[(lambda x, y, d: d, 0.3), (lambda x, y, d: y, px(0, 20.2)[1])])
        out.append(leg)
        # The seam across it.
        sx0, sx1 = (mirror_c(18.2), mirror_c(15.1)) if mirrored else (15.1, 18.2)
        (xa, y), (xb, _) = px(sx0, LEG_SEAM), px(sx1, LEG_SEAM)
        zt = interp(LEG_TOPS, LEG_SEAM)
        seam = mk.tube("leg_seam", [Vector((xa + (xb - xa) * i / 6, y, zt + 0.02)) for i in range(7)], 0.2,
                       m["seam"], 8)
        out.append(k.smooth(seam, 50))
        # The inner strip: light grey at the top, teal down to the foot.
        c, r0, r1, hw = STRIP
        pts = []
        for i in range(9):
            r = r0 + (r1 - r0) * i / 8
            pts.append((mirror_c(c) if mirrored else c, r, interp(LEG_TOPS, r) - 0.12))
        strip = blade("strip", path3(pts), [hw] * 9, 0.45, m["teal"], power=3.0, segments=12)
        mk.paint(strip, lambda cc, n: m["grey_light"] if row_of(cc.y) < STRIP_TEAL else None)
        out.append(strip)
        # The shoe round the foot's outer side and under it: a blue plate, dark blue in front.
        shoe = blade("shoe", path3(SHOE, mirrored), SHOE_W, 1.25, m["blue"], power=3.2, segments=16, flat=0.85,
                     step=0.35)
        for v in shoe.data.vertices:  # it stands on the ground
            v.co.z = max(v.co.z, 0.0)
        shoe.data.update()
        mk.paint(shoe, lambda cc, n: m["blue_dark"] if n.z < 0.45 and n.y < -0.3 else None)
        out.append(shoe)
    return out


def keel(m):
    """A dark wedge hanging between the legs: two facets falling away from a ridge (a little right of the axis, as
    the sprite's grey column 23 draws it), its outer edges rounded; a grey strip along the ridge."""
    ridge_x = px(RIDGE[0][0], 0)[0]

    def height(x, y, d):
        top = interp(KEEL_TOPS, row_of(y))
        z = top - KEEL_FALL * abs(x - ridge_x)
        return z - 0.55 + 0.55 * round_edge(d, 0.55)
    body = relief("keel", [symmetric(KEEL, 1)], height, m, paint=lambda x, y, d: "dark", side="dark", bottom=0.0,
                  spacing=0.35, band=None, smooth_angle=30.0)
    ridge = blade("ridge", path3(RIDGE), RIDGE_W, 0.4, m["grey"], power=2.4, segments=10)
    return [body, ridge]


def bar(m):
    """The glowing blue bar: a glass rod, lit along its top left, its right side dark steel blue."""
    rod = blade("bar", path3(BAR), BAR_W, 0.95, m["glow"], power=2.3, segments=24, flat=0.7, step=0.4)
    mk.paint(rod, lambda c, n: m["glow_side"] if n.x > 0.55 and n.z < 0.62 else
             m["glow_light"] if AXIS - 0.95 < c.x < AXIS - 0.3 and n.z > 0.85 and c.y < px(0, 5.8)[1] else None)
    return [rod]


# --- Build ---------------------------------------------------------------------------------------------------------

def build_whole():
    k.reset()
    m = materials()
    neck(m)
    collar(m)
    beam(m)
    shoulders(m)
    brackets(m)
    legs(m)
    keel(m)
    bar(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole, m


def whole_mask(sheet):
    left, right = k.sprite_mask(sheet, 123), k.sprite_mask(sheet, 125)
    return [a + b for a, b in zip(left, right)]


def build():
    options = k.args()
    outdir = mk.outdir(options)
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_2.png") if os.path.isdir(sheets) else sheets) if sheets else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole grabber (2 123 | 125): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f "
          "z %.2f..%.2f" % (mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y,
                            low.z, high.z))
    if sheet:
        mk.compare("whole (2 123 | 125)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "grabber_whole", whole, size=(48, 28), scale=10, distance=1.6)
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0.0, 0.0)))
        for o in whole:
            o.hide_render = True
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.view_layer.update()
        mk.report(name, pieces, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for o in pieces:
            bpy.data.objects.remove(o)
        for o in whole:
            o.hide_render = False


if __name__ == "__main__":
    build()
