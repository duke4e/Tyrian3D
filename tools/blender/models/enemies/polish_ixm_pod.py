"""IXMUCANE's and SAWBLADES' red pod lying on the ground, its nose up the screen (sheet 8 sprites 153 above 191, 2x2
each: one 24 x 56 picture, its pixels in rows 4-51; ground layer; enemies 100 (153 155 157) and 101 (191 193 195),
both animated (ani 3: a frame each in turn); the events put 153 28 pixels above 191 at the same x (IXMUCANE's events
at t 450-970 (type 6) and 3550-3570 (type 10), SAWBLADES' at 820-3570 (type 10)), and the two move together; it lays
the glossy red balls, 8 102, polish_red_ball.py). Polished (2026-10-21; it replaces wave3_y_boss.py's build_pod(): an
egg for a sack under a brown skirt, a grey drum with a sphere for a lamp).

Its pixels are the pink torpedo's (8 125 beside 127, polish_pink_torpedo.py) transposed, shade for shade: the pod's
row r is the torpedo's column r - 4, its column c the torpedo's row c (all 754 pixels of 153 above 191 agree with 125
beside 127). A transposition is a turn and a mirror image at once, and it keeps the light at the upper left, so the
torpedo's model laid out the same way is the pod: (x, y) = (2 - y_torpedo, -x_torpedo), its faces turned back to face
out. The model is built from the torpedo's parts (polish_pink_torpedo's muzzle(), receiver(), collar(), fins() and
body(): a body of revolution lying on the ground, its axis at x -0.5: the lamp on its nose, the grey head with the
dark window in its top, the olive collar with its two swept fins tipped pink, the pink-red sack with a raised band
round its front), with three changes the pod's frames and its family ask for:
- the lamp (the torpedo's muzzle cap; the pod's rows 4-9: a dark tip, a hot band (rows 5-6), a red ring (7), a hot
  band (8), a red ring (9)) is painted in those bands, and its frames run the light back along it: 153 the front band
  blazing and the back one glowing, 155 the other way round, 157 the front one dim and the back one blazing (frame
  models ixm_pod_top_155 and _157: the same geometry, the bands' materials changed);
- the two glowing slits across the sack's band (rows 33 and 35, 6 pixels long: columns 8-13; the torpedo's slits run
  right round its body) are short slots set into the band, dark red lips round a glowing core, and a light runs along
  each: 191 at the upper one's left end and the lower one's right end, 193 both near the middle, 195 the upper one's
  right end and the lower one's left end (the light circles round behind them; frame models ixm_pod_body_193, _195);
- the sack is painted with the sprite's own shades of ramp 4 (SACK: its lit lobes either side of the crease along its
  top, the folds of its lower half; the outline and the slits filled from their neighbours), the broad shading lifted
  (the game's light adds it again), the fine shading kept, each band glowing faintly in its own colour as the red balls
  it lays do (polish_red_ball.py: 0.06-0.34, more in the lighter bands), glossy as they are, and laid out for the game's
  camera (VIEW_TILT: a point higher than the sack's widest part takes the sprite's colour from further up the screen,
  so that the lobes sit where the sprite draws them in the game's view); the bands' borders are smooth contours
  (polish_orb_red.band_split).
Every emission stays well under 1 (the game's bloom and the glow halo add to it).

The whole is built in the torpedo's coordinates, laid out as the pod (transposed), then cut along the sprites' common
edge (y 0; polish_savara_boss.cut: the halves keep the whole's shading, the cut capped, the faces' winding kept),
each half moved so that its sprite's centre is its origin; every mesh triangulated before export (polish_k_pod).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (the pod lies on
it); the whole's origin at the picture's centre (between 153 and 191), the pieces' at their sprites' centres (y 14
and -14).

models.cfg (the model lines stay): add model ixm_pod_top_155 enemies/ixm_pod_top_155.glb origin, model
ixm_pod_top_157 ..., model ixm_pod_body_193 ..., model ixm_pod_body_195 ... (origin), and frame 8 155 ixm_pod_top_155,
frame 8 157 ixm_pod_top_157, frame 8 193 ixm_pod_body_193, frame 8 195 ixm_pod_body_195; sprite 8 153 ixm_pod_top yaw=0
height=-4 glow=12:0.3:120 and sprite 8 191 ixm_pod_body yaw=0 height=-4 glow=10:0.15:121 (height=-4: the pod lies on
z = 0 and is drawn at its origin on the ground layer, so without it it floats 4 pixels over the terrain; the red balls
it lays have it). No other enemy shows 153-157 or 191-195 (catalog.json), and none of them is another single sprite's
pixels mirrored, turned or in other ramps.

Replaces wave3_y_boss.py's pod: remove POD, build_pod() and its y.pieced("ixm_pod", ...) registration (and the
ixm_pod lines of its docstring), and wave3_y_art.py's POD, which only wave3_y_boss.py reads.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_8.png), --preview <prefix> (each model's top and 3/4 view, the whole's), --only
<model,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_pink_torpedo as pt  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping the faces' winding)
from polish_squid_ship import tube  # noqa: E402

# The torpedo's (x, y) -> the pod's (2 - y, -x), z kept (a mirror image: the faces are turned back afterwards).
TRANSPOSE = Matrix(((0.0, -1.0, 0.0, 2.0), (-1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

# The pieces: name, its sprite in each frame, the box it covers in the pod's coordinates (x0, x1, y0, y1).
PIECES = [("ixm_pod_top", (153, 155, 157), (-12.0, 12.0, 0.0, 28.0)),
          ("ixm_pod_body", (191, 193, 195), (-12.0, 12.0, -28.0, 0.0))]

# The lamp (the torpedo's muzzle cap, x -23.72 .. -18.2): its bands along the torpedo's x (the pod's y = -x; its rows
# 4-9): the dark tip, the front hot band, a red ring, the back hot band, a red ring (up to the grey ring).
LAMP_BANDS = [(-99.0, "tip"), (-23.2, "front"), (-21.05, "ring"), (-20.1, "back"), (-19.05, "ring")]
# Each frame's light in the two hot bands: ((palette index, emission strength) of the front band, of the back band).
LAMP_FRAMES = {153: ((0x7d, 0.6), (0x7b, 0.4)),
               155: ((0x7b, 0.4), (0x7d, 0.6)),
               157: ((0x78, 0.24), (0x7e, 0.65))}
# The bands are hot along the lamp's top (within LAMP_HOT of its radius from the axis, seen from above) and orange on
# its flanks (the sprite's columns 8-9 and 13-15 of rows 5-8), whatever the frame.
LAMP_HOT = 0.5

# The slits: their x along the torpedo (the pod's rows 33 and 35), their half-length across (the pod's columns
# 8-13), and where the light is along each in every frame (-1 at the pod's left end, 1 at its right end).
SLITS = (5.5, 7.5)
SLIT_HALF = 3.1
SLIT_FRAMES = {191: (-1.0, 1.0), 193: (-0.3, 0.3), 195: (1.0, -1.0)}

# The sack's painting (see sack_values): the broad shading (a blur of BROAD pixels) lifted towards LIFT (KEEP of it
# kept), DETAIL of the fine shading over it; the bands (lowest shade, palette index of ramp 4, emission strength).
VIEW_TILT = 20.0
FINE, BROAD, LIFT, KEEP, DETAIL = 0.85, 2.6, 7.4, 0.5, 0.75
SACK_BANDS = [(-99.0, 0x43, 0.06), (4.6, 0x45, 0.08), (6.0, 0x47, 0.1), (7.4, 0x48, 0.13), (8.7, 0x4a, 0.19),
              (10.2, 0x4c, 0.3)]
SACK_FINISH = dict(metallic=0.12, roughness=0.24)
# The sack's lathe: stations along it, segments round it (the torpedo's body is finer: 61 x 40; band_split cuts these
# faces again along the bands' borders).
STATIONS, SEGMENTS = 36, 36

# The sack's shades (ramp 4, 0-f) as the sprite draws them, its rows 24-50 and columns 0-23; '.' where it has none of
# them (its outline, the slits, the transparent border): filled from the neighbours.
SACK = """
......68beb765543.......
.....556ada8655334......
....153bccba89b2341.....
....154477876421341.....
.....5678565532334......
.....5666cef992334......
.....566cbef668234......
....156acacd6667241.....
...7c6a7665434466496....
...66596......343345....
...6b794677655343395....
...69466......331165....
...538b6754323343115....
...269aada5836543312....
...5889cfb5b36543342....
...5889cfe6d46543244....
...3688cfd6f46543145....
...2447aba7f66432255....
....5547988e7643123.....
....4873777a6542386.....
....2a92566954248b5.....
.....5a546674225a7......
.....2432554412585......
......32144431188.......
......22133211366.......
.......212212166........
........4667925.........
"""
SACK_ROW0 = 24


def materials():
    pal = k.level_palette()

    def hot(name, index, strength, rough=0.35):
        return k.material(name, palette=index, metallic=0.0, roughness=rough, emission=pal[index],
                          emission_strength=strength)
    sack = {index: k.material(f"pod_sack_{index:02x}", palette=index, emission=pal[index], emission_strength=glow,
                              **SACK_FINISH) for _, index, glow in SACK_BANDS}
    ring = hot("pod_lamp_ring", 0x73, 0.15, 0.3)
    frame = k.material("pod_frame", palette=0x41, metallic=0.3, roughness=0.5)
    inside = k.material("pod_inside", palette=0x14, metallic=0.2, roughness=0.6)
    m = {
        # (polish_pink_torpedo's muzzle() paints its cap with the first three; paint_lamp repaints it in LAMP_BANDS)
        "muzzle_core": ring,
        "muzzle_band": ring,
        "muzzle_ring": ring,
        "knob": sack[0x45],                 # the red knobs either side of the lamp
        "grey": k.material("pod_grey", palette=0x07, metallic=0.55, roughness=0.3),
        "grey_light": k.material("pod_grey_light", palette=0x0b, metallic=0.55, roughness=0.25),
        "frame": frame,
        "inside": inside,
        "olive_dark": inside,               # the collar's dark back edge
        "olive": k.material("pod_olive", palette=0x16, metallic=0.4, roughness=0.3),
        "pink": sack[0x47],
        "pink_light": sack[0x4a],           # the fins' tips
        "flank": hot("pod_lamp_flank", 0x76, 0.2, 0.3),
        "cut": frame,                       # the cut's caps (inside, where the pieces meet)
        "lips": hot("pod_slit_lips", 0x72, 0.12, 0.3),
        "slit_dim": hot("pod_slit_dim", 0x75, 0.22),
        "slit_warm": hot("pod_slit_warm", 0x78, 0.38),
        "slit_hot": hot("pod_slit_hot", 0x7e, 0.6),
        "sack": sack,
    }
    for f, ((fi, fs), (bi, bs)) in LAMP_FRAMES.items():
        m[f"front{f}"] = hot(f"pod_lamp_front{f}", fi, fs)
        m[f"back{f}"] = hot(f"pod_lamp_back{f}", bi, bs)
    return m


# --- The sack's shades ----------------------------------------------------------------------------------------------

def sack_art():
    """SACK on the pod's 56 x 24 grid (NaN where unknown), its gaps filled from the neighbours, step by step."""
    a = np.full((56, 24), np.nan)
    for r, line in enumerate(SACK.strip("\n").split("\n")):
        for c, ch in enumerate(line):
            if ch != ".":
                a[SACK_ROW0 + r, c] = int(ch, 16)
    for _ in range(40):
        known = ~np.isnan(a)
        if known.all():
            break
        v = np.pad(np.where(known, a, 0.0), 1)
        kn = np.pad(known.astype(float), 1)
        acc = v[:-2, 1:-1] + v[2:, 1:-1] + v[1:-1, :-2] + v[1:-1, 2:]
        cnt = kn[:-2, 1:-1] + kn[2:, 1:-1] + kn[1:-1, :-2] + kn[1:-1, 2:]
        new = ~known & (cnt > 0)
        a[new] = acc[new] / cnt[new]
    return a


def blur(a, sigma):
    r = int(math.ceil(3 * sigma))
    kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    kern /= kern.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(kern):
            acc += w * (p[i:i + out.shape[0], :] if axis == 0 else p[:, i:i + out.shape[1]])
        out = acc
    return out


def sample(a, x, y):
    """Bilinear sample of a pod-grid array at the pod's (x, y) (pixel centres at x = c + 0.5 - 12, y = 27.5 - r)."""
    u, v = x + 12.0 - 0.5, 27.5 - y
    rows, cols = a.shape
    c0, r0 = int(math.floor(u)), int(math.floor(v))
    fu, fv = u - c0, v - r0

    def at(r, c):
        return a[min(max(r, 0), rows - 1), min(max(c, 0), cols - 1)]
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def sack_values(obj, fine, broad):
    """The shade (0-15) at each vertex of a part in the torpedo's coordinates: the sprite's under the point as the
    game's camera sees it (its height over the axis moves it up the screen), broad shading lifted, fine kept."""
    tilt = math.tan(math.radians(VIEW_TILT))
    out = []
    for v in obj.data.vertices:
        xt, yt, z = v.co
        x, y = 2.0 - yt, -xt
        y += (z - pt.AXIS_Z) * tilt
        f, b = sample(fine, x, y), sample(broad, x, y)
        lifted = LIFT + (b - LIFT) * KEEP
        out.append(lifted + DETAIL * (f - b))
    return out


# --- The parts ------------------------------------------------------------------------------------------------------

def sack(m):
    """The sack: polish_pink_torpedo.body()'s body of revolution (its profile BODY, the crease along its top, the raised
    band round its front) on a coarser lathe (STATIONS x SEGMENTS), without the torpedo's slits."""
    x0, x1 = pt.BODY_X
    b0, b1 = pt.BAND
    xs = [x0 + (x1 - x0) * i / (STATIONS - 1) for i in range(STATIONS)]
    xs = sorted(set([round(x, 3) for x in xs] + [b0 - 0.3, b0, b1, b1 + 0.3]))

    def crease(x):
        t = min(1.0, max(0.0, (x - 8.6) / 2.0)) * min(1.0, max(0.0, (22.0 - x) / 6.0))
        return pt.CREASE_DEPTH * t * t * (3 - 2 * t)
    body = pt.lathe_x("body", [(x, pt.BODY(x)) for x in xs], m["pink"], segments=SEGMENTS, crease=crease)
    band = [(b0 - 0.1, pt.BODY(b0) * 0.98), (b0 + 0.3, pt.BODY(b0 + 0.3) + 0.35), (b1 - 0.3, pt.BODY(b1 - 0.3) + 0.35),
            (b1 + 0.1, pt.BODY(b1) * 0.98)]
    return body, pt.lathe_x("band", band, m["pink_light"], segments=SEGMENTS)


def paint_lamp(cap, m, frame):
    """The lamp's bands along the torpedo's x in a frame's light: hot along its top, orange on its flanks; the tip and
    the rings dark red, and so is its underside."""
    names = {"tip": m["muzzle_ring"], "ring": m["muzzle_ring"], "front": m[f"front{frame}"], "back": m[f"back{frame}"]}
    profile = k.profile(pt.MUZZLE, 0.25)

    def radius(x):
        for (xa, ra), (xb, rb) in zip(profile, profile[1:]):
            if xa <= x <= xb:
                return ra + (rb - ra) * (x - xa) / max(xb - xa, 1e-6)
        return profile[-1][1]
    for mat in list(names.values()) + [m["flank"]]:
        mk.slot_of(cap, mat)
    for poly in cap.data.polygons:
        c = poly.center
        key = None
        for x0, band in LAMP_BANDS:
            if c.x >= x0:
                key = band
        mat = names[key]
        if key in ("front", "back"):
            if c.z < pt.AXIS_Z - 0.2:
                mat = m["muzzle_ring"]
            elif abs(c.y - pt.AXIS_Y) > LAMP_HOT * radius(c.x):
                mat = m["flank"]
        poly.material_index = mk.slot_of(cap, mat)


def slit(m, i, spot):
    """One slit (the i-th, at SLITS[i]): a dark red lip round a short glowing core, both following the band's top
    round the axis; the core's light falls off from spot (-1 .. 1 along the pod's x: hot, warm, dim)."""
    x = SLITS[i]
    r = pt.BODY(x) + 0.35

    def arc(half, lift, n):
        half_angle = math.degrees(math.asin(min(0.95, half / r)))
        out = []
        for j in range(n + 1):
            a = math.radians(90.0 - half_angle + 2 * half_angle * j / n)
            out.append(Vector((x, pt.AXIS_Y + r * math.cos(a), pt.AXIS_Z + pt.SQUASH * r * math.sin(a) + lift)))
        return out
    # The lips: a flattened tube a little longer than the core, sunk into the band.
    pts = arc(SLIT_HALF + 0.55, -0.18, 12)
    lips = tube(f"slit_lips{i}", pts, [0.62] * len(pts), m["lips"], segments=12, squash=0.62)
    # The core: one tube, its faces lit by where they are along it (the torpedo's y is 2 - the pod's x).
    pts = arc(SLIT_HALF, 0.05, 16)
    core = tube(f"slit{i}", pts, [0.4] * len(pts), m["slit_dim"], segments=10, squash=0.75)
    for mat in (m["slit_dim"], m["slit_warm"], m["slit_hot"]):
        mk.slot_of(core, mat)
    for poly in core.data.polygons:
        along = max(-1.0, min(1.0, (pt.AXIS_Y - poly.center.y) / SLIT_HALF))   # -1 the pod's left end, 1 its right
        d = abs(along - spot)
        mat = m["slit_hot"] if d < 0.4 else m["slit_warm"] if d < 0.85 else m["slit_dim"]
        poly.material_index = mk.slot_of(core, mat)
    return [lips, core]


def build_whole(m):
    """The torpedo's parts (polish_pink_torpedo) with the pod's lamp, slits and sack: in the torpedo's coordinates."""
    pt.muzzle(m)
    pt.receiver(m)
    pt.collar(m)
    pt.fins(m)
    art = sack_art()
    fine, broad = blur(art, FINE), blur(art, BROAD)
    for obj in sack(m):
        band_split(obj, sack_values(obj, fine, broad), [(lowest, m["sack"][index]) for lowest, index, _ in SACK_BANDS])
        k.smooth(obj, 50)
    return bpy.data.objects["muzzle"]


def transpose(objects, back=False):
    """Lays the parts out as the pod (the torpedo's (x, y) -> (2 - y, -x)), or back (the inverse), the faces turned
    back to face out (a mirror image turns them in)."""
    matrix = TRANSPOSE.inverted() if back else TRANSPOSE
    for obj in objects:
        obj.data.transform(matrix)
        obj.data.flip_normals()
        obj.data.update()


def frame_parts(m, frame_top, frame_body, cap, slits):
    """Gives the whole a frame's lights (the lamp's bands, the slits' cores); returns the slit objects."""
    paint_lamp(cap, m, frame_top)
    for obj in slits:
        bpy.data.objects.remove(obj)
    new = []
    for i, spot in enumerate(SLIT_FRAMES[frame_body]):
        new += slit(m, i, spot)
    return new


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    cap = build_whole(m)
    slits = []
    sheet = os.path.join(options["check"], "enemy_8.png") if "check" in options else None
    for f in range(3):
        top_frame, body_frame = PIECES[0][1][f], PIECES[1][1][f]
        # Build the frame's lights in the torpedo's coordinates, then lay everything out as the pod.
        whole = mk.meshes()
        if f > 0:
            transpose(whole, back=True)
        slits = frame_parts(m, top_frame, body_frame, cap, slits)
        whole = mk.meshes()
        transpose(whole)
        bpy.context.view_layer.update()
        if f == 0:
            print("whole pod: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
            if sheet:
                both = k.sprite_mask(sheet, 153) + k.sprite_mask(sheet, 191)
                mk.compare("whole (8 153 above 191)", mk.coverage(whole, 24, 56), both)
            if "preview" in options:
                mk.preview(options["preview"] + "ixm_pod_whole", whole, size=(24, 56), scale=8, distance=1.6)
        for (name, sprites, box), frame in zip(PIECES, (top_frame, body_frame)):
            model = name if f == 0 else "%s_%d" % (name, frame)
            if only and model not in only and not (f == 0 and name in only):
                continue
            parts = [p for p in (cut(src, box, m["cut"]) for src in whole) if p is not None]
            mk.transform(parts, Matrix.Translation((0.0, -(box[2] + box[3]) / 2, 0.0)))
            triangulate(parts)
            parts = [join(parts, model)]
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if sheet and f == 0:
                mk.compare("%s (8 %d)" % (model, frame), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, frame))
            mk.report(model, parts, os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, parts)
            for obj in parts:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
