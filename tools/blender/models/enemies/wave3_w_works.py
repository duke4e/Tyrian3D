"""Enemies of wave 3, batch W, continued (sheet P: the asteroid levels): the works built on the block house
of wave3_w.py, modelled as their sprites look (models.cfg: yaw=0), each built whole and cut into the
sprites the level events place (origin); the kit is wave3_w_kit.py, the pixels wave3_w_art.py.

- pump_dome (P 115) and bronze_pump_tl, bronze_pump_tr, bronze_pump_bl, bronze_pump_br (P 229, 231 above
  267, 269): the bronze pump of ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY and AST. CITY (enemies 338-342:
  event 12 places 267, 269, 229, 231 as the sheet arranges them, another event puts the dome 115 above
  229). On the house's roof a bronze cross: a long arm across it, a tower with a gold inset at its right
  and a golden cabinet behind that, a leg down its front to the floor ending in a gold band; from the
  arm a dark shaft with a slot of light leans up the screen to the golden onion dome of three tiers that
  the dome's sprite draws above the house (its frames move the dome's highlights: the model is polished
  gold). The dome is an enemy of its own: its piece holds the dome and the shaft's top.
- cargo_pod_tl, cargo_pod_tr, cargo_pod_ml, cargo_pod_mr, cargo_pod_bl, cargo_pod_br (P 165, 167 above
  203, 205 above 241, 243): the cargo pod of ASTEROID1, ASTEROID2, ASTCITY, AST. CITY and AST ROCK
  (enemies 343-348 and 1035-1040): a long grey container lying on the house, its sides chamfered and
  ribbed, its top a light panel with "812" across it, its back end reaching past the house onto a dark
  cradle; in front of it a dark dock with two vents.
- asteroid_rig_crane_l, asteroid_rig_crane_r, asteroid_rig_tl, asteroid_rig_tr, asteroid_rig_bl,
  asteroid_rig_br (P 9, 11 above 1, 3 above 39, 41): the drilling rig of ASTEROID1 and AST ROCK (enemies
  332-337 and 1024-1029: event 12 places 39, 41, 1, 3, two more put the crane's halves 9 and 11 above
  them): on the house a gold collar round the bore hole, gold lugs and anchors; a mast leaning up the
  screen from the house's back to the crane's brown head, a bent pipe beside it, dark stays from the
  head to the anchors and the drill string from the head down into the hole (1 and 3 animate the drill
  going in and out: the model shows it in the hole).

usage: Blender -b --factory-startup -P wave3_w_works.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

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


def along(start, angle):
    """A point function along an axis from `start` leaning up the screen `angle` degrees from upright."""
    a = math.radians(angle)
    d = Vector((0.0, math.sin(a), math.cos(a)))
    s = Vector(start)
    return (lambda t: s + d * t), d


# --- P 115 above 229 231 / 267 269: the bronze pump and its golden dome ----------------------------------

PUMP = kit.Frame(art.PUMP, 48, (24, 42))
PUMP_LEAN = 63.0


def pump_whole():
    f = PUMP
    X, Y = f.X, f.Y
    m = bronze_mats("pump")
    hm = kit.house_mats("pump")
    kit.house("pump", f, 28, hatches=False, m=hm)
    kit.house_floor("pump", f, 28, extra=lambda c, r: r < 28 or (11 <= c <= 19 and r <= 81))
    roof = 10.0

    # The arm across the roof (rows 45-56) and its lower left lobe (rows 55-62).
    arm = kit.slab("arm", kit.rrect(f.left(6), f.right(38), f.bottom(56), f.top(45), (2.5, 2.0, 2.0, 2.5)),
                   roof - 0.5, roof + 5.0, m["bronze"], bevel=1.1, segments=3)
    paint_lit(arm, m["bronze"], m["bronze_lit"], m["bronze_dark"])
    lobe = kit.slab("lobe", kit.rrect(f.left(6), f.right(27), f.bottom(62), f.top(52), (3.0, 3.0, 0.0, 0.0)),
                    roof - 0.5, roof + 4.0, m["bronze"], bevel=1.0, segments=3)
    paint_lit(lobe, m["bronze"], m["bronze_lit"], m["bronze_dark"])
    # Ribs across the arm's top and a gold plate at its right end.
    for c in (24.5, 27.5, 30.5):
        kit.rounded_box(f"arm_rib{c}", (X(c), Y(50.5), roof + 5.0), (1.0, 9.0, 0.7), m["bronze_dark"], bevel=0.3)
    gold = kit.slab("arm_gold", kit.rrect(f.left(33), f.right(36), f.bottom(55), f.top(52)), roof + 4.6,
                    roof + 5.5, m["gold"], bevel=0.35, segments=2)
    paint_lit(gold, m["gold"], m["gold_lit"], m["gold_dark"])

    # The tower at the right (rows 36-46) with a gold inset, the golden cabinet behind it (rows 28-36).
    tower = kit.slab("tower", kit.rrect(f.left(24), f.right(38), f.bottom(46), f.top(36), (1.5, 1.5, 1.5, 1.5)),
                     roof - 0.5, roof + 8.0, m["bronze"], bevel=1.0, segments=3)
    paint_lit(tower, m["bronze"], m["bronze_lit"], m["bronze_dark"])
    inset = kit.slab("tower_gold", kit.rrect(f.left(28), f.right(32), f.bottom(43), f.top(37)), roof + 7.6,
                     roof + 8.5, m["gold"], bevel=0.4, segments=2)
    paint_lit(inset, m["gold"], m["gold_lit"], m["gold_dark"])
    cabinet = kit.slab("cabinet", kit.rrect(f.left(24), f.right(33), f.bottom(37), f.top(28) - 0.4,
                                            (0.0, 0.0, 1.5, 1.5)), roof - 0.5, roof + 10.0, m["gold"], bevel=0.9,
                       segments=3)
    paint_lit(cabinet, m["gold"], m["gold_lit"], m["gold_dark"])
    for c in (26.5, 30.5):
        kit.rounded_box(f"cabinet_seam{c}", (X(c) + 0.5, Y(32.0), roof + 10.0), (0.6, 6.5, 0.5), m["gold_dark"],
                        bevel=0.2)

    # The leg down the front: over the roof (rows 56-69), down the house's front, along the floor to row 81.
    y_front = f.bottom(70)
    leg = kit.prism_x("leg", [(f.top(56), roof - 0.5), (y_front + 0.6, roof - 0.5), (y_front + 0.6, 0.2),
                              (f.bottom(81), 0.2), (f.bottom(81), 1.9), (y_front - 5.0, 2.4), (y_front - 2.6, 4.2),
                              (y_front - 0.6, 9.0), (y_front + 1.5, roof + 2.6), (f.top(56), roof + 2.6)],
                      f.left(11), f.right(19), m["bronze"], bevel=0.8, segments=3)

    def paint_leg(c, nrm):
        if f.bottom(78) < c.y < f.top(76) and nrm.z > -0.5:
            return m["gold"] if nrm.z > 0.5 else m["gold_dark"]
        if nrm.z > 0.9:
            return m["bronze"]
        if nrm.z < -0.5:
            return m["bronze_deep"]
        if nrm.z > 0.3:
            return m["bronze_lit"] if (nrm.x < -0.25 or nrm.y > 0.25) else m["bronze_dark"]
        return m["bronze_dark"]
    kit.paint_faces(leg, paint_leg)
    leg_gold = kit.slab("leg_gold", kit.rrect(f.left(13), f.right(17), f.bottom(67), f.top(57)), roof + 2.2,
                        roof + 3.1, m["gold"], bevel=0.4, segments=2)
    paint_lit(leg_gold, m["gold"], m["gold_lit"], m["gold_dark"])

    # The shaft from the arm up the screen to the dome: a square bronze column leaning back, a dark slot
    # down its top with a lamp in it.
    at, d = along((X(14.0), Y(47.0), roof + 3.0), PUMP_LEAN)
    t_top = (Y(26.5) - Y(47.0)) / d.y
    length = t_top + 1.5
    shaft = kit.rounded_box("shaft", (0.0, length / 2, 0.0), (7.6, length, 5.6), m["bronze"], bevel=0.8,
                            segments=2)
    slot = kit.rounded_box("shaft_slot", (0.0, length * 0.55, 2.7), (3.4, length * 0.55, 0.6), m["slot"], bevel=0.2)
    lamp = w.sphere("shaft_lamp", (0.0, length * 0.62, 2.9), (1.0, 1.1, 0.5),
                    pal("pump_lamp", 0x1c, metallic=0.2, roughness=0.3, glow=1.4), 12, 6)
    for obj in (shaft, slot, lamp):
        sh.apply_modifiers(obj)
    kit.rotate_about([shaft, slot, lamp], "X", math.radians(90.0 - PUMP_LEAN), (0.0, 0.0, 0.0))
    sh.move([shaft, slot, lamp], at(0.0).x, at(0.0).y, at(0.0).z)
    paint_lit(shaft, m["bronze"], m["bronze_lit"], m["bronze_dark"])

    # The golden onion dome: three tiers and a knob along the shaft's axis.
    base = at(t_top)
    # The tiers where the sprite draws them: the widest of each at rows 22, 14.5 and 8 (t = distance along
    # the axis from the shaft's top; seen from above a tier of radius r spans r cos(lean) up and down).
    prof = [(0.0, 3.6), (1.2, 6.5), (2.8, 8.8), (5.1, 9.6), (7.4, 9.0), (9.2, 7.2), (10.1, 6.4), (11.2, 6.9),
            (13.5, 7.6), (15.3, 6.6), (16.8, 5.0), (18.2, 5.4), (20.8, 5.6), (22.6, 4.2), (23.6, 2.4), (24.2, 2.2),
            (25.2, 2.1), (26.0, 1.0), (26.3, 0.0)]
    dome_gold = pal("pump_dome", 0x1b, metallic=0.6, roughness=0.22)
    dome = w.lathe_axis("dome", k.profile(prof, 0.6), dome_gold, tuple(base), tuple(d), 32)
    waist = pal("pump_dome_waist", 0x17, metallic=0.6, roughness=0.3)

    def paint_dome(c, nrm):
        t = (Vector(c) - base).dot(d)
        for t0, t1 in ((9.5, 10.7), (16.2, 17.4), (23.2, 24.0)):
            if t0 <= t <= t1:
                return waist
        return None
    kit.paint_faces(dome, paint_dome)
    # A collar where the shaft meets the dome.
    w.lathe_axis("dome_collar", [(-1.6, 4.4), (-1.4, 5.2), (0.2, 5.2), (0.4, 4.4)], m["bronze_dark"], tuple(base),
                 tuple(d), 32)


kit.pieced("bronze_pump", pump_whole, (48, 84), [
    kit.quarter("pump_dome", PUMP, 0, 0),
    kit.quarter("bronze_pump_tl", PUMP, 0, 28), kit.quarter("bronze_pump_tr", PUMP, 24, 28),
    kit.quarter("bronze_pump_bl", PUMP, 0, 56), kit.quarter("bronze_pump_br", PUMP, 24, 56)])



# --- P 165 167 / 203 205 / 241 243: the cargo pod ------------------------------------------------------

CRATE = kit.Frame(art.CRATE, 48, (24, 42))


def crate_ring(y, z0, ztop, inset, xl=-18.0, xr=18.0, tl=-11.0, tr=9.0, knee=4.0):
    """The pod's cross-section at y: a flat bottom from xl to xr (moved in by inset), upright sides `knee`
    high, sides sloping in to the top face from tl to tr at ztop. Counter-clockwise seen from +y."""
    zk = min(z0 + knee, ztop - 0.3)
    pts = [(xr - inset, z0), (xr - inset, zk), (tr - inset * 0.5, ztop), (tl + inset * 0.5, ztop), (xl + inset, zk),
           (xl + inset, z0)]
    return [Vector((x, y, z)) for x, z in pts]


def crate_whole():
    f = CRATE
    X, Y = f.X, f.Y
    hm = kit.house_mats("crate")
    g = hm["grey"]
    kit.house("crate", f, 28, m=hm, plain=True)
    kit.house_floor("crate", f, 28, extra=lambda c, r: r < 28)
    roof = 10.0
    z0, top = roof + 0.4, roof + 11.0
    # The pod, lofted along y from its front end (row 55) to its back end (row 14).
    stations = [(f.bottom(55) + 0.05, z0 + 2.4, 0.9), (f.bottom(55) + 0.6, z0 + 3.6, 0.3), (f.bottom(53), z0 + 5.5, 0.0),
                (f.bottom(48), top - 0.4, 0.0), (f.bottom(47), top, 0.0), (f.top(19), top, 0.0),
                (f.top(18), top - 0.5, 0.0), (f.top(15), z0 + 6.0, 0.0), (f.top(14) - 0.6, z0 + 4.5, 0.3),
                (f.top(14) - 0.05, z0 + 3.4, 0.9)]
    rings = [crate_ring(y, z0, zt, i) for y, zt, i in stations]
    pod = k.loft("pod", rings, g[9])
    k.smooth(pod, 30)
    # Painted pixel for pixel: the label with its number, the ribs along the sides.
    painter = kit.Painter("crate", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.35,
                          roughness=0.5)
    paint = kit.Frame(art.CRATE, 48, (24, 42)).fill({0x01})
    kit.pixelate(pod, paint)
    kit.paint_sprite(pod, paint, painter, wall_steps=1, under=g[3], probe=0.5)
    kit.merge_flat(pod)
    # Ribs along the sloping sides (the sprite's stripes).
    for i, x in enumerate((-16.4, -14.4, -12.4)):
        zt = z0 + 4.0 + (top - z0 - 4.0) * (-18.0 - x) / (-18.0 + 11.0) if x < -11 else top
        w.tube(f"rib_l{i}", [(x, f.bottom(51), zt - 0.1), (x, f.top(17), zt - 0.1)], 0.45, g[0xa if i % 2 else 8], 8)
    for i, x in enumerate((10.5, 12.5, 14.5, 16.5)):
        zt = top + (z0 + 4.0 - top) * (x - 9.0) / (18.0 - 9.0)
        w.tube(f"rib_r{i}", [(x, f.bottom(51), zt - 0.1), (x, f.top(17), zt - 0.1)], 0.45, g[7 if i % 2 else 6], 8)
    # The cradle under its back end, past the house.
    kit.slab("cradle", kit.rrect(-15.0, 15.0, f.top(28) - 1.0, f.top(15)), 0.0, z0 + 0.2, g[3], bevel=0.6)
    for x in (-13.0, 13.0):
        kit.rounded_box(f"cradle_foot{x:.0f}", (x, f.top(21), 0.6), (4.0, 12.0, 1.2), g[4], bevel=0.4)
    # The dock in front of it: a dark frame let into the roof with two vents, a light lip at its front.
    dock = kit.slab("dock", kit.rrect(f.left(6), f.right(41), f.bottom(68), f.top(56), (1.0, 1.0, 0.0, 0.0)),
                    roof - 0.4, roof + 0.5, g[2], bevel=0.3, segments=2)
    kit.paint_faces(dock, lambda c, nrm: g[2] if nrm.z > 0.9 else g[4])
    for name, c0, c1 in (("vent_l", 9, 21), ("vent_r", 23, 35)):
        kit.slab(name, kit.rrect(f.left(c0), f.right(c1), f.bottom(64), f.top(58)), roof + 0.3, roof + 0.9, g[4],
                 bevel=0.25)
        kit.slab(name + "_hole", kit.rrect(f.left(c0) + 0.8, f.right(c1) - 0.8, f.bottom(64) + 0.8, f.top(58) - 0.8),
                 roof + 0.85, roof + 0.95, g[1], bevel=0.05, segments=1)
        kit.rounded_box(name + "_bar", ((f.left(c0) + f.right(c1)) / 2, Y(61.0), roof + 1.15),
                        (f.right(c1) - f.left(c0) - 2.4, 1.1, 0.6), g[6], bevel=0.25)
    lip = kit.slab("dock_lip", kit.rrect(f.left(7), f.right(40), f.bottom(68), f.top(66)), roof + 0.3, roof + 1.0,
                   g[5], bevel=0.3)
    kit.paint_faces(lip, lambda c, nrm: g[6] if nrm.z > 0.9 else g[4])


kit.pieced("cargo_pod", crate_whole, (48, 84), [
    kit.quarter("cargo_pod_tl", CRATE, 0, 0), kit.quarter("cargo_pod_tr", CRATE, 24, 0),
    kit.quarter("cargo_pod_ml", CRATE, 0, 28), kit.quarter("cargo_pod_mr", CRATE, 24, 28),
    kit.quarter("cargo_pod_bl", CRATE, 0, 56), kit.quarter("cargo_pod_br", CRATE, 24, 56)])


# --- P 9 11 / 1 3 / 39 41: the drilling rig ------------------------------------------------------------

RIG = kit.Frame(art.RIG, 48, (24, 42))
RIG_HEAD_Z = 26.0


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
    kit.house("rig", f, 28, hatches=False, m=hm)
    kit.house_floor("rig", f, 28, extra=lambda c, r: r < 28)
    roof = 10.8
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

    # The head: a brown plank across the top (rows 1-5) on a dark hub (rows 6-11) where the stays meet.
    # The plank: its top (rows 1-4) and its front (rows 5-6 right of the bent pipe), its right end slanting.
    plank = [(f.left(10), f.bottom(4)), (f.left(16), f.bottom(4)), (f.left(16), f.bottom(6)), (f.right(30), f.bottom(6)),
             (f.right(31), f.bottom(5)), (f.right(31), f.top(4)), (f.right(28), f.top(2) - 0.2), (f.right(25), f.top(1)),
             (f.left(11), f.top(1)), (f.left(10), f.top(2))]
    head = kit.slab("head", plank, RIG_HEAD_Z, RIG_HEAD_Z + 2.4, wood[9], bevel=0.6, segments=2)
    paint_lit(head, wood[7], wood[0xa], wood[5], wall=wood[5], under=wood[5])
    hub_c = Vector((X(20.5), Y(9.0), RIG_HEAD_Z - 1.4))
    kit.rounded_box("hub", tuple(hub_c), (8.0, 5.0, 3.6), g[3], bevel=0.8)
    post = kit.prism_x("post", [(f.top(5), RIG_HEAD_Z + 0.4), (f.top(5), RIG_HEAD_Z - 0.6), (Y(11.0), RIG_HEAD_Z - 3.4),
                                (Y(11.0), RIG_HEAD_Z - 1.6)], f.left(18), f.right(23), wood[7], bevel=0.4)
    paint_lit(post, wood[7], wood[0xa], wood[5], wall=wood[5], under=wood[5])

    # The stays: thick dark pipes from the hub down to the anchors, gold collars round them where they
    # pass the house's back; the drill string from the hub into the hole.
    top_z = RIG_HEAD_Z - 2.6
    stays = [("l", 17.5, "l"), ("ml", 20.0, "bl"), ("mr", 27.0, "br"), ("r", 29.5, "r")]
    ends = {}
    for name, c_top, anchor in stays:
        c, r, _, _ = anchors[anchor]
        a_ = Vector((X(c_top), Y(9.5), top_z))
        b_ = Vector((X(c), Y(r), roof + 1.2))
        ends[name] = (a_, b_)
        w.tube(f"stay_{name}", [a_, b_], 1.65, steel, 12)
        w.tube(f"stay_{name}_hi", [a_ + Vector((-0.7, 0.3, 1.25)), b_ + Vector((-0.7, 0.3, 1.25))], 0.38, steel_lit,
               6)
        # The collar where the stay crosses row 34.
        t = (Y(34.0) - a_.y) / (b_.y - a_.y)
        pc = a_ + (b_ - a_) * t
        d = (b_ - a_).normalized()
        w.lathe_axis(f"stay_{name}_collar", [(-1.3, 1.9), (-1.1, 2.5), (1.1, 2.5), (1.3, 1.9)], m["gold"],
                     tuple(pc), tuple(d), 20)
    a_ = Vector((X(23.5), Y(10.0), top_z - 0.4))
    b_ = Vector((hx, hy, roof - 1.5))
    w.tube("drill", [a_, b_], 1.9, steel, 14)
    w.tube("drill_hi", [a_ + Vector((-0.8, 0.3, 1.4)), b_ + Vector((-0.8, 0.3, 1.4))], 0.42, steel_lit, 6)
    d = (b_ - a_).normalized()
    for i, frac in enumerate((0.28, 0.55, 0.8)):
        pc = a_ + (b_ - a_) * frac
        w.lathe_axis(f"drill_joint{i}", [(-0.9, 2.0), (-0.6, 2.5), (0.6, 2.5), (0.9, 2.0)], g[6], tuple(pc), tuple(d), 16)

    # The bent pipe down the head's left: from the plank's end along the left of the stays, curving in to
    # the outer stay.
    a_, b_ = ends["l"]
    t = (Y(24.0) - a_.y) / (b_.y - a_.y)
    join = a_ + (b_ - a_) * t
    start = Vector((X(11.5), Y(3.5), RIG_HEAD_Z + 0.6))
    path = w.catmull([start, Vector((X(11.5), Y(5.5), RIG_HEAD_Z - 2.0)), Vector((X(11.6), Y(16.0), RIG_HEAD_Z - 7.5)),
                      Vector((X(12.0), Y(21.5), join.z + 1.5)), join], 0.8)
    w.tube("bent_pipe", path, 1.6, g[5], 12)
    w.tube("bent_pipe_hi", [v + Vector((-0.5, 0.2, 0.9)) for v in path[1:-1]], 0.3, g[8], 6)


kit.pieced("asteroid_rig", rig_whole, (48, 84), [
    kit.quarter("asteroid_rig_crane_l", RIG, 0, 0), kit.quarter("asteroid_rig_crane_r", RIG, 24, 0),
    kit.quarter("asteroid_rig_tl", RIG, 0, 28), kit.quarter("asteroid_rig_tr", RIG, 24, 28),
    kit.quarter("asteroid_rig_bl", RIG, 0, 56), kit.quarter("asteroid_rig_br", RIG, 24, 56)])

kit.run()
