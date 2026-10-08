"""Batch AT of wave 3 (the second animation pass), sheet D: two machines of the asteroid levels whose frames change
shape, for frame lines. Built by batch J's own builders (wave3_j.py, imported as it is, its output unchanged) and
posed as the frames draw them (models.cfg: as their first frame's models, yaw=0).

- eye_tub_<sprite> (D 193, 195, 197, 201, 205, 207; enemy 273 of the asteroid levels, eye_tub): the tub's iris opens
  on its red eye and shuts again, 193 195 197 199 201 203 205 207 169 207 ... 195 193 193 193 193. wave3_j's tub
  shows 169 (the iris drawn back, its four petals leaning against the rim, the eye and the front light glowing).
  Here: 193 (the iris shut, the tub as it is most of the time: four grey petals meeting in a low dome, a cross of
  seams between them), 195 and 197 (the petals sliding out along the diagonals into the rim, the cross widening to
  show the dark inside), 201 (for 199, 201 and 203: the petals drawn back as in 169, the eye dark), 205 and 207 (the
  eye lighting up, small and dim, then brighter; the front light with it).
- shell_ship_<sprite> (D 159, 161; enemy 285 of the asteroid levels, shell_ship): its two dark shells close over the
  eye and open again, 157 159 159 161 161 159 159 157: 159 the shells 2 pixels apart round the hub, 161 meeting in one
  egg (each a little narrower); in both the frames draw the ship a pixel to the left of 157, as the models are.

usage: Blender -b --factory-startup -P wave3_at_d.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402
import wave3_q_kit as q  # noqa: E402

wj = kit.quiet_import("wave3_j")
kit.forget()
w = kit.w
pal = kit.pal
D = "enemy_D"


# --- The eye tub's iris ------------------------------------------------------------------------------------------

TUB = (-0.5, 3.4)     # the tub's axis (wave3_j's cx, cy)
TUB_H = 8.4           # its height (the rim's top)
IRIS_R = 9.2          # the petals slide under the rim beyond this radius


def petal_poly(i, t, seam=0.18, count=24):
    """The outline of petal i (its quadrant round the diagonal 45 + 90 i degrees) slid out by t along its diagonal,
    clipped to the circle of IRIS_R: [(x, y)] or None when nothing of it is left inside."""
    cx, cy = TUB
    a = math.radians(45 + 90 * i)
    d = Vector((math.cos(a), math.sin(a)))
    # The quadrant's two edges run along these axis directions from its corner.
    e1 = Vector((math.copysign(1.0, d.x), 0.0))
    e2 = Vector((0.0, math.copysign(1.0, d.y)))
    corner = Vector((cx, cy)) + d * t + (e1 + e2) * seam
    c = Vector((cx, cy))
    if (corner - c).length >= IRIS_R - 0.3:
        return None

    def hit(direction):
        # corner + s * direction on the circle (s > 0)
        f = corner - c
        b = f.dot(direction)
        disc = b * b - (f.dot(f) - IRIS_R ** 2)
        return corner + direction * (-b + math.sqrt(disc))
    p1, p2 = hit(e1), hit(e2)
    a1 = math.atan2(p1.y - cy, p1.x - cx)
    a2 = math.atan2(p2.y - cy, p2.x - cx)
    # The arc from p1 to p2 the short way round (through the diagonal).
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    arc = [(cx + IRIS_R * math.cos(a1 + da * j / count), cy + IRIS_R * math.sin(a1 + da * j / count))
           for j in range(count + 1)]
    pts = [tuple(corner)] + arc
    # Counter-clockwise.
    area = sum(pts[j][0] * pts[(j + 1) % len(pts)][1] - pts[(j + 1) % len(pts)][0] * pts[j][1] for j in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def iris(t):
    """The four petals slid out by t: grey plates domed over the tub's opening (low at the rim, highest where the
    petals meet), their sides dark."""
    cx, cy = TUB
    top = pal("tub_petal_top", 0x08, metallic=0.7, roughness=0.3)
    petal = pal("tub_petal", 0x06, metallic=0.7, roughness=0.3)
    dark = pal("tub_inside", 0x01, metallic=0.3, roughness=0.6)
    for i in range(4):
        poly = petal_poly(i, t)
        if poly is None:
            continue
        a = math.radians(45 + 90 * i)
        ox, oy = cx + math.cos(a) * t, cy + math.sin(a) * t

        def z_of(x, y, e, ox=ox, oy=oy):
            rq = math.hypot(x - ox, y - oy) / IRIS_R
            return TUB_H - 1.5 + 1.9 * max(0.0, 1.0 - rq * rq) + 0.25 * e
        obj = q.heightfield(f"iris{i}", [poly], z_of, petal, spacing=0.5, smooth_angle=40, edge=0.5)
        kit.paint_faces(obj, lambda c, nrm: top if nrm.z > 0.8 else petal if nrm.z > 0.4 else dark)


def eye_tub(t, eye, light):
    """wave3_j's tub with its iris at t (None: drawn back as wave3_j builds it), its eye (None: dark; or its
    material's (index, glow) and the core's) and the front light ((index, glow); glow None: unlit)."""
    wj.eye_tub()
    if t is not None:
        kit.remove(["petal0", "petal1", "petal2", "petal3"])
        iris(t)
    eye_obj, core_obj, light_obj = (bpy.data.objects[nm] for nm in ("eye", "eye_core", "front_light"))
    if eye is None:
        eye_obj.data.materials[0] = pal("tub_eye_dark", 0x70, metallic=0.2, roughness=0.3)
        kit.remove(["eye_core"])
    else:
        (ei, eg), core = eye
        eye_obj.data.materials[0] = pal(f"tub_eye_{ei:x}_{int(eg * 10)}", ei, metallic=0.0, roughness=0.2, glow=eg)
        if core is None:
            kit.remove(["eye_core"])
        else:
            ci, cg = core
            core_obj.data.materials[0] = pal(f"tub_eye_core_{ci:x}_{int(cg * 10)}", ci, metallic=0.0, roughness=0.2,
                                             glow=cg)
    li, lg = light
    light_obj.data.materials[0] = pal(f"tub_light_{li:x}_{int((lg or 0) * 10)}", li, metallic=0.0 if lg else 0.3,
                                      roughness=0.3, glow=lg)


# (sprite: the iris's slide (None: drawn back), the eye, the front light) -- 195's cross is 3 pixels wide, 197's 5
# (each petal slid out by the gap's half width times the square root of 2).
TUB_FRAMES = {193: (0.0, None, (0x71, None)),
              195: (2.1, None, (0x71, None)),
              197: (3.5, None, (0x71, None)),
              201: (None, None, (0x71, None)),
              205: (None, ((0x74, 0.6), None), (0x73, 0.5)),
              207: (None, ((0x76, 0.9), (0x79, 1.2)), (0x74, 0.8))}
for s, (t, eye, light) in TUB_FRAMES.items():
    w.model(f"eye_tub_{s}", [(D, s, True)])(lambda t=t, eye=eye, light=light: eye_tub(t, eye, light))


# --- The shell ship ----------------------------------------------------------------------------------------------

def shell_ship(left, right, narrow, dx):
    """wave3_j's shell ship with its shells' inner faces moved to x = left and right (from 157's -3.6 and 3.6), each
    shell `narrow` of its width, the hub and eye moved by dx."""
    wj.shell_ship()
    for side, x_in in ((-1, left), (1, right)):
        objs = kit.objects((f"shell{side}", f"rim{side}"))
        old = side * 3.6
        m = Matrix.Translation((x_in, 0.0, 0.0)) @ Matrix.Diagonal((narrow, 1.0, 1.0, 1.0)) @ \
            Matrix.Translation((-old, 0.0, 0.0))
        w.transform(objs, m)
    w.transform(kit.objects(("hub", "neck", "eye_ring", "eye")), Matrix.Translation((dx, 0.0, 0.0)))


# 159: the shells' inner faces at x -2 and 0 (columns 2-9 and 12-19); 161: both at -1, each 7 pixels wide (columns 4-10
# and 11-17).
SHELL_FRAMES = {159: (-2.0, 0.0, 1.0, -1.0), 161: (-1.0, -1.0, 0.95, -1.0)}
for s, args in SHELL_FRAMES.items():
    w.model(f"shell_ship_{s}", [(D, s, True)])(lambda args=args: shell_ship(*args))


if __name__ == "__main__":
    w.run()
