"""Enemies of wave 3, batch W, continued (sheet P: the asteroid levels): the works built on the block house
of wave3_w.py, modelled as their sprites look (models.cfg: yaw=0), each built whole and cut into the
sprites the level events place (origin); the kit is wave3_w_kit.py, the pixels wave3_w_art.py.

- pump_dome (P 115) and bronze_pump_tl, bronze_pump_tr, bronze_pump_bl, bronze_pump_br (P 229, 231 above
  267, 269): the bronze pump of ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY and AST. CITY (enemies 338-342:
  event 12 places 267, 269, 229, 231 as the sheet arranges them, another event puts the dome 115 above
  229). On the house's roof a bronze cross: a long arm across it, a tower with a gold inset at its right
  and a golden cabinet behind that, a leg down its front to the ground ending in a gold band; on the
  arm a dark shaft with a slot of light standing upright under the golden onion dome of three tiers (the
  sprites draw the tower in the game's oblique view, the shaft leaning up the screen to the dome drawn
  above the house: modelled upright, batch AV; its frames move the dome's highlights: the model is
  polished gold). The dome is an enemy of its own: its piece holds the dome and its collar, standing on
  the shaft over the house's top left piece (Drawn, drawn_pieced).
- asteroid_rig_crane_l, asteroid_rig_crane_r, asteroid_rig_tl, asteroid_rig_tr, asteroid_rig_bl,
  asteroid_rig_br (P 9, 11 above 1, 3 above 39, 41): the drilling rig of ASTEROID1 and AST ROCK (enemies
  332-337 and 1024-1029: event 12 places 39, 41, 1, 3, two more put the crane's halves 9 and 11 above
  them): on the house a gold collar round the bore hole, gold lugs and anchors; a derrick standing upright
  over the hole, the crane's brown head on four dark stays down to the anchors, a bent pipe beside them
  and the drill string straight down from the head into the hole (the sprites draw it in the game's
  oblique view, the stays leaning up the screen to the head drawn above the house: modelled upright,
  batch AV; 1 and 3 animate the drill going in and out: the model shows it in the hole). The crane's
  halves hold the head and the stays' upper parts, over the house's top pieces (Drawn, drawn_pieced).

The asteroid floor the sprites draw round the house is the map's ground, which the game draws under it: the
models have none of it (batch AV); the house and the pump's leg stand on the ground (z 0).

usage: Blender -b --factory-startup -P wave3_w_works.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_w_kit as kit  # noqa: E402
from wave3_w_kit import art, k, sh, w, p, pal  # noqa: E402


def bronze_mats(prefix):
    return {
        "bronze": pal(f"{prefix}_bronze", 0xa8, metallic=0.6, roughness=0.35),
        "bronze_lit": pal(f"{prefix}_bronze_lit", 0xaa, metallic=0.6, roughness=0.32),
        "bronze_dark": pal(f"{prefix}_bronze_dark", 0xa5, metallic=0.55, roughness=0.4),
        "bronze_deep": pal(f"{prefix}_bronze_deep", 0xa3, metallic=0.5, roughness=0.45),
        "gold": pal(f"{prefix}_gold", 0x19, metallic=0.8, roughness=0.25),
        "gold_lit": pal(f"{prefix}_gold_lit", 0x1b, metallic=0.8, roughness=0.22),
        "gold_dark": pal(f"{prefix}_gold_dark", 0x15, metallic=0.75, roughness=0.3),
        "slot": pal(f"{prefix}_slot", 0x02, metallic=0.2, roughness=0.6),
    }


def paint_lit(obj, top, lit, dark, wall=None, under=None):
    """Top faces `top`, slopes facing the upper left `lit`, the others `dark`, steep sides `wall` (default:
    dark), faces looking down `under` (default: dark)."""
    def pick(c, nrm):
        if nrm.z > 0.9:
            return top
        if nrm.z < -0.5:
            return under or dark
        if nrm.z > 0.3:
            return lit if (nrm.x < -0.25 or nrm.y > 0.25) else dark
        return wall or dark
    return kit.paint_faces(obj, pick)


# --- Upright structures and the sprites' oblique view -----------------------------------------------------

class Drawn:
    """How the sprites draw an upright structure in the game's oblique view: a point at height z is drawn
    shift(z) pixels further up the screen, shift interpolated between knots (height, shift) (the first's
    below them, the last's above). The models stand upright (batch AV: modelled as drawn they leaned up the
    screen); their pieces are still cut where the sprites draw them (the cut boxes in drawn space), so a
    tower's top belongs to the sprite drawn above the house even though it now stands over the house, and
    wrecks are damaged where their sprites draw the damage."""

    def __init__(self, *knots):
        self.knots = knots

    def shift(self, z):
        knots = self.knots
        if z <= knots[0][0]:
            return knots[0][1]
        for (za, sa), (zb, sb) in zip(knots, knots[1:]):
            if z <= zb:
                return sa + (sb - sa) * (z - za) / (zb - za)
        return knots[-1][1]

    def drawn(self, objects, sign=1.0):
        """Moves the objects' vertices to where the sprites draw them (sign -1: back upright)."""
        for obj in objects:
            sh.apply_modifiers(obj)
            obj.data.transform(obj.matrix_world)
            obj.matrix_world = Matrix.Identity(4)
            for v in obj.data.vertices:
                v.co.y += sign * self.shift(v.co.z)
            obj.data.update()
        return objects

    def upright(self, objects):
        return self.drawn(objects, -1.0)


def drawn_pieced(name, builder, size, pieces, drawn):
    """As kit.pieced, the pieces (kit.quarter) cut where the sprites draw them (see Drawn): each piece a model
    of its own, built whole, moved to drawn space, cut, stood upright again and moved to its sprite's centre.
    The whole object stays registered for --whole."""
    kit.pieced(name, builder, size, [])

    def build(box, centre):
        builder()
        w.bake()
        kept = sh.cut_box(drawn.drawn(w.meshes()), *box)
        drawn.upright(kept)
        sh.move(kept, -centre[0], -centre[1])
        for obj in kept:
            k.smooth(obj, 40)
    for piece_name, box, centre, mask in pieces:
        kit.model(piece_name, mask=mask)(lambda box=box, centre=centre: build(box, centre))


# --- P 9 11 / 1 3 / 39 41: the drilling rig ------------------------------------------------------------

RIG = kit.Frame(art.RIG, 48, (24, 42))
RIG_ROOF = 10.8
RIG_HEAD_Z = 33.0                          # the head plank's underside, high over the bore hole
RIG_RISE = RIG.Y(10.0) - RIG.Y(46.5)       # the sprites draw the hub this far up the screen from the hole
RIG_PLANK_RISE = 4.5                       # and the plank on it this much further (its top seen from above)
# The derrick stands upright over the bore hole (the sprites draw it in the oblique view, its stays leaning up
# the screen from the anchors to the head drawn above the house: batch AV); drawn space leans it back, from the
# anchors' tops up to the stays' tops under the head, and the plank's top a little further.
RIG_DRAWN = Drawn((RIG_ROOF + 1.2, 0.0), (RIG_HEAD_Z - 2.6, RIG_RISE), (RIG_HEAD_Z + 2.4, RIG_RISE + RIG_PLANK_RISE))


def side_offset(direction, v, length):
    """`v` without its part along `direction`, `length` long: a highlight along a pipe, on its lit side."""
    d = Vector(direction).normalized()
    v = Vector(v)
    v = v - d * v.dot(d)
    return v.normalized() * length


def torus(name, centre, major, minor, mat, segments=40, sides=12, scale_y=1.0):
    section = [(major + minor * math.cos(2 * math.pi * i / sides), minor * math.sin(2 * math.pi * i / sides))
               for i in range(sides)]
    return w.hoop(name, centre, section, mat, segments, scale_y=scale_y)


def rig_whole():
    f = RIG
    X, Y = f.X, f.Y
    m = bronze_mats("rig")
    hm = kit.house_mats("rig")
    g = hm["grey"]
    # No floor round the house: the sprites' floor is the map's ground, which the game draws under it (batch AV).
    kit.house("rig", f, 28, hatches=False, m=hm)
    roof = RIG_ROOF
    steel = pal("rig_steel", 0x04, metallic=0.6, roughness=0.35)
    steel_lit = pal("rig_steel_lit", 0x07, metallic=0.6, roughness=0.3)
    wood = {s_: pal(f"rig_head{s_:x}", 0x10 + s_, metallic=0.15, roughness=0.6) for s_ in (5, 7, 9, 0xa)}

    # The collar round the bore hole and the dark hole in it.
    hx, hy = X(23.5), Y(46.5)
    torus("collar", (hx, hy, roof + 0.9), 5.4, 1.45, m["gold"], 40, 12, scale_y=0.88)
    kit.slab("collar_foot", sh.ellipse(hx, hy, 6.6, 5.9, count=32), roof - 0.3, roof + 0.5, m["gold_dark"], bevel=0.3)
    kit.slab("hole", sh.ellipse(hx, hy, 4.3, 3.8, count=28), roof - 0.2, roof + 0.62, pal("rig_hole", 0x01,
                                                                                        metallic=0.0, roughness=0.9),
             bevel=0.05, segments=1)

    # The anchors: gold cups on the roof that the stays run into.
    anchors = {"l": (6.5, 46.0, 3.9, 3.2), "r": (39.2, 46.3, 3.6, 2.8), "bl": (14.5, 59.0, 4.6, 3.4),
               "br": (33.5, 59.2, 4.4, 2.9)}
    for name, (c, r, rx, ry) in anchors.items():
        cup = kit.slab(f"anchor_{name}", sh.ellipse(X(c), Y(r), rx, ry, count=28), roof - 0.3, roof + 1.6, m["gold"],
                       bevel=0.6, segments=2)
        paint_lit(cup, m["gold"], m["gold_lit"], m["gold_dark"])
        kit.slab(f"anchor_{name}_hole", sh.ellipse(X(c), Y(r), rx * 0.5, ry * 0.5, count=20), roof + 1.2, roof + 1.7,
                 m["gold_dark"], bevel=0.1, segments=1)

    def up(c, r, z):
        """The upright point the sprites draw at pixel (c, r) at height z (see RIG_DRAWN)."""
        return Vector((X(c), Y(r) - RIG_DRAWN.shift(z), z))

    # The head over the bore hole: a brown plank across the top (rows 1-5) on a dark hub (rows 6-11) where
    # the stays meet. The plank: its top (rows 1-4) and its front (rows 5-6 right of the bent pipe), its right
    # end slanting. Built where the sprites draw it, moved down the screen over the hole, the plank onto the hub.
    plank = [(f.left(10), f.bottom(4)), (f.left(16), f.bottom(4)), (f.left(16), f.bottom(6)), (f.right(30), f.bottom(6)),
             (f.right(31), f.bottom(5)), (f.right(31), f.top(4)), (f.right(28), f.top(2) - 0.2), (f.right(25), f.top(1)),
             (f.left(11), f.top(1)), (f.left(10), f.top(2))]
    head = kit.slab("head", plank, RIG_HEAD_Z, RIG_HEAD_Z + 2.4, wood[9], bevel=0.6, segments=2)
    paint_lit(head, wood[7], wood[0xa], wood[5], wall=wood[5], under=wood[5])
    hub_c = Vector((X(20.5), Y(9.0), RIG_HEAD_Z - 1.4))
    hub = kit.rounded_box("hub", tuple(hub_c), (8.0, 5.0, 3.6), g[3], bevel=0.8)
    post = kit.prism_x("post", [(f.top(5), RIG_HEAD_Z + 0.4), (f.top(5), RIG_HEAD_Z - 0.6), (Y(11.0), RIG_HEAD_Z - 3.4),
                                (Y(11.0), RIG_HEAD_Z - 1.6)], f.left(18), f.right(23), wood[7], bevel=0.4)
    paint_lit(post, wood[7], wood[0xa], wood[5], wall=wood[5], under=wood[5])
    sh.move([hub, post], 0.0, -RIG_RISE)
    sh.move([head], 0.0, -RIG_RISE - RIG_PLANK_RISE)

    # The stays: thick dark pipes from the hub down to the anchors, gold collars round them where the sprites
    # draw them passing the house's back; the drill string straight down from the hub into the hole.
    top_z = RIG_HEAD_Z - 2.6
    stays = [("l", 17.5, "l"), ("ml", 20.0, "bl"), ("mr", 27.0, "br"), ("r", 29.5, "r")]
    ends = {}
    for name, c_top, anchor in stays:
        c, r, _, _ = anchors[anchor]
        a_ = up(c_top, 9.5, top_z)
        b_ = Vector((X(c), Y(r), roof + 1.2))
        ends[name] = (a_, b_)
        w.tube(f"stay_{name}", [a_, b_], 1.65, steel, 12)
        hi = side_offset(b_ - a_, (-0.7, 0.3, 1.25), 1.45)
        w.tube(f"stay_{name}_hi", [a_ + hi, b_ + hi], 0.38, steel_lit, 6)
        # The collar where the sprites draw the stay crossing row 34 (as far along it).
        t = (Y(34.0) - Y(9.5)) / (b_.y - Y(9.5))
        pc = a_ + (b_ - a_) * t
        d = (b_ - a_).normalized()
        w.lathe_axis(f"stay_{name}_collar", [(-1.3, 1.9), (-1.1, 2.5), (1.1, 2.5), (1.3, 1.9)], m["gold"],
                     tuple(pc), tuple(d), 20)
    a_ = Vector((hx, hy, top_z - 0.4))
    b_ = Vector((hx, hy, roof - 1.5))
    w.tube("drill", [a_, b_], 1.9, steel, 14)
    hi = side_offset(b_ - a_, (-0.8, 0.3, 1.4), 1.6)
    w.tube("drill_hi", [a_ + hi, b_ + hi], 0.42, steel_lit, 6)
    d = (b_ - a_).normalized()
    for i, frac in enumerate((0.28, 0.55, 0.8)):
        pc = a_ + (b_ - a_) * frac
        w.lathe_axis(f"drill_joint{i}", [(-0.9, 2.0), (-0.6, 2.5), (0.6, 2.5), (0.9, 2.0)], g[6], tuple(pc), tuple(d), 16)

    # The bent pipe down the head's left: from the plank's end along the left of the stays, curving in to
    # the outer stay where the sprites draw it meeting it (row 24); upright, it drops from under the plank.
    a_, b_ = ends["l"]
    t = (Y(24.0) - Y(9.5)) / (b_.y - Y(9.5))
    join = a_ + (b_ - a_) * t
    z_start = RIG_HEAD_Z + 0.6

    def drop(r):  # its height where the sprites draw it at row r
        return z_start + (join.z - z_start) * (r - 3.5) / (24.0 - 3.5)
    path = w.catmull([up(11.5, 3.5, z_start), up(11.5, 5.5, RIG_HEAD_Z - 2.0), up(11.6, 16.0, drop(16.0)),
                      up(12.0, 21.5, drop(21.5)), join], 0.8)
    w.tube("bent_pipe", path, 1.6, g[5], 12)
    w.tube("bent_pipe_hi", [v + side_offset(path[i + 2] - path[i], (-0.5, 0.2, 0.9), 1.03)
                            for i, v in enumerate(path[1:-1])], 0.3, g[8], 6)


# The crane's halves (enemies of their own, drawn above the house) hold the head and the stays' upper parts,
# standing over the house's top pieces.
drawn_pieced("asteroid_rig", rig_whole, (48, 84), [
    kit.quarter("asteroid_rig_crane_l", RIG, 0, 0), kit.quarter("asteroid_rig_crane_r", RIG, 24, 0),
    kit.quarter("asteroid_rig_tl", RIG, 0, 28), kit.quarter("asteroid_rig_tr", RIG, 24, 28),
    kit.quarter("asteroid_rig_bl", RIG, 0, 56), kit.quarter("asteroid_rig_br", RIG, 24, 56)], RIG_DRAWN)

kit.run()
