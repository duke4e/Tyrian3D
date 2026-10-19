"""The red furnace of the asteroid levels (sheet D sprite 267, 2x2: 24 x 28 pixels; ground layer; ASTEROID1,
ASTEROID2, ASTCITY, AST. CITY and AST ROCK, enemies 269 and 1043; its animation 267 267 269 269 271 271 273 273 271
271 269 269 267 x 8: it heats up and cools down), polished (2026-10-19; it replaces wave3_j.py's red_furnace(), a
pillow inflated from its outline with a tube for a rim and boxes in its holes). models.cfg: sprite d 267 red_furnace
yaw=0, frame d 269 red_furnace_269, frame d 271 red_furnace_271, frame d 273 red_furnace_273 (no other enemy shows
sheet D's 269, 271 or 273).

As the sprites and their 4x upscales draw it: a red housing (the sprite's ramp 4) standing on the floor (columns 2-18
of rows 0-25; the grey tiles round it are the map's, drawn into the sprite, and left out here), its top edge rounded,
lit at its upper left; on it a raised rim like a racetrack (columns 6-14 of rows 2-21), its long sides dipping in
their middles (rows 9-14 darker), round a deep well (columns 8-12 of rows 5-18, near black, ramp 7's 70); in the well
a heating element, a rod lying along it (columns 9-10 of rows 7-17), copper while it is cold (267). Either side of
the rim a deep slot down into the housing (columns 3-5 and 15-17 of rows 7-17), black, with two steel pins across
each (rows 8 and 15, lit); along the housing's sides two red rails (columns 0 and 20 of rows 6-17) clamped to it by
bronze bolts (rows 7 and 16). The frames heat the element: red (269, 72-77), orange-yellow (271, 7a-7c, the well's
walls warming, 71-72), white-hot (273, 7e-7f, the well glowing orange round it, 74-79).

Built as a CAD modeller would: the housing a block whose plan is a superellipse (long straight sides, its ends a
pixel narrower, as the sprite's), its top edge bevelled, the slots and the well cut into it with exact booleans and
their edges softened; the rim a loop lofted round the well, its cross-section a rounded
crest whose height dips along the long sides, its inner wall running down to the well's floor (so it is the well's
wall); the element a rod on two posts, the pins, rails and clamps turned parts. One model per frame, the same
shapes: only the element's and the well's colours and glow change. The model is symmetric about the sprite's column 10
(x = -1.5).

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the ground (z = 0); column c's
left edge is x = c - 12, row r's top edge y = 14 - r. Tall enough (the rim's ends at RIM_TOP, more than 7.4) for the
game to set it on the ground (it centres ground models in height on the ground enemies' layer, 4, and lifts them to
0.3 when they would reach lower).

Replaces wave3_j.py's red_furnace() and rounded_rect() (its @model("red_furnace", [(D, 267, True)]) registration;
wave3_j_art.py's D267 is not used by it): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the furnace's own pixels, the map's tiles round it left out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402

AXIS_X = -1.5
# The housing: its plan (a superellipse: centre, half-sizes, power), height, top edge's bevel.
HOUSING = ((AXIS_X, 1.0), 8.5, 13.0, 6.0)        # columns 2-18, rows 0-25 (3-17 near its ends, 4-16 at them)
HOUSING_Z, HOUSING_BEVEL = 5.8, 1.3
# The slots (left one; mirrored): plan, floor's height.
SLOT = ((AXIS_X - 6.0, 1.5), 1.5, 5.5, 0.9)       # columns 3-5, rows 7-17
SLOT_FLOOR = 1.3
# The steel pins across each slot: y, height, radius.
PINS = [(5.5, 3.1, 0.85), (-1.5, 3.1, 0.85)]     # rows 8 and 15
# The well: its opening (the rim's inner edge), floor's height; the rim's outer edge, its crest's height at the
# ends, how far the crest dips along the long sides (deepest round y = DIP_Y, out to DIP_REACH from there).
WELL = ((AXIS_X, 2.0), 2.5, 7.0, 1.0)            # columns 8-12, rows 5-18
WELL_FLOOR = 1.2
RIM_OUT = ((AXIS_X, 2.0), 4.5, 10.0, 2.6)         # columns 6-14, rows 2-21
RIM_TOP, DIP, DIP_Y, DIP_FLAT, DIP_REACH = 7.6, 1.15, 2.0, 2.0, 5.2
RIM_SEGMENTS = 112
# The element: x, from y to y, height, radius; its posts.
ELEMENT = (AXIS_X - 0.5, -4.0, 7.5, 2.5, 0.88)   # columns 9-10, rows 7-17
# The rails along the sides (left one; mirrored): x, from y to y, height, radius; the clamps' y.
RAIL = (AXIS_X - 9.9, -4.3, 8.0, 1.1, 0.9)       # column 0, rows 6-17
CLAMPS = [6.5, -2.5]                              # rows 7 and 16

# The frames: (model, sprite, the element's (palette index, glow), its ends', the well's walls', its floor's).
FRAMES = [
    ("red_furnace", 267, (0x48, 0.0), (0x45, 0.0), (0x70, 0.0), (0x70, 0.0)),
    ("red_furnace_269", 269, (0x77, 1.25), (0x74, 0.8), (0x70, 0.2), (0x71, 0.4)),
    ("red_furnace_271", 271, (0x7b, 1.7), (0x77, 1.15), (0x71, 0.45), (0x73, 0.75)),
    ("red_furnace_273", 273, (0x7f, 2.6), (0x7b, 1.8), (0x75, 1.0), (0x78, 1.5)),
]

# The furnace's own pixels (the map's tiles round it left out), by rows: (first row, last row, [(first column, last
# column), ...]).
OWN = [(0, 0, [(4, 16)]), (1, 2, [(3, 17)]), (3, 5, [(2, 18)]), (6, 17, [(0, 20)]), (18, 20, [(2, 18)]),
       (21, 24, [(3, 17)]), (25, 25, [(4, 16)])]


def rrect(plan, inset=0.0, segments=64):
    """A rounded rectangle's outline (x, y), counter-clockwise, inset by `inset` (negative: grown)."""
    (cx, cy), hw, hh, r = plan
    ring = mk.rounded_rect_ring((cx, cy), hw - inset, hh - inset, max(0.05, r - inset), 0.0, segments)
    return [(p.x, p.y) for p in ring]


def superellipse(plan, segments=96):
    """A superellipse's outline (x, y), counter-clockwise."""
    (cx, cy), hw, hh, power = plan
    out = []
    for j in range(segments):
        u, v = mk.superellipse_point(2 * math.pi * j / segments, power)
        out.append((cx + hw * u, cy + hh * v))
    return out


def mirror(plan):
    (cx, cy), hw, hh, r = plan
    return ((2 * AXIS_X - cx, cy), hw, hh, r)


def materials(frame):
    glow = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.35, strength=0.0):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow[index],
                              emission_strength=strength)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    _, _, element, ends, well, floor = frame
    m = {
        "body": mat("furnace_body", 0x46),
        "top": mat("furnace_top", 0x48, roughness=0.32),
        "rim": mat("furnace_rim", 0x4a, roughness=0.3),
        "rim_in": mat("furnace_rim_in", 0x44, roughness=0.4),
        "slot": mat("furnace_slot", 0x01, metallic=0.2, roughness=0.7),
        "slot_wall": mat("furnace_slot_wall", 0x42, roughness=0.5),
        "pin": mat("furnace_pin", 0x0a, metallic=0.8, roughness=0.22),
        "rail": mat("furnace_rail", 0x48, roughness=0.3),
        "clamp": mat("furnace_clamp", 0x17, metallic=0.6, roughness=0.32),
        "post": mat("furnace_post", 0x43, roughness=0.45),
    }
    hot = element[1] > 0
    m["element"] = mat(f"furnace_element_{element[0]:x}", element[0], 0.1 if hot else 0.6, 0.3, element[1])
    m["element_end"] = mat(f"furnace_element_end_{ends[0]:x}", ends[0], 0.1 if hot else 0.6, 0.35, ends[1])
    m["well"] = mat(f"furnace_well_{well[0]:x}", well[0], 0.1, 0.6, well[1])
    m["floor"] = mat(f"furnace_floor_{floor[0]:x}", floor[0], 0.1, 0.55, floor[1])
    return m


# --- The housing --------------------------------------------------------------------------------------------------

def in_plan(plan, x, y, grow=0.0):
    (cx, cy), hw, hh, r = plan
    return mk.rounded_rect_distance(x - cx, y - cy, hw, hh, r) < grow


def housing(m):
    """The housing: a block of its plan, its top edge bevelled; the slots and the well cut into it, their edges
    softened; the slots dark, the well's floor taking the frame's heat."""
    body = mk.prism("housing", superellipse(HOUSING), 0.0, HOUSING_Z, m["body"])
    mk.bevel(body, HOUSING_BEVEL, 4, 30)
    cutters = [mk.prism("slot_l", rrect(SLOT), SLOT_FLOOR, 30.0, m["slot_wall"]),
               mk.prism("slot_r", rrect(mirror(SLOT)), SLOT_FLOOR, 30.0, m["slot_wall"]),
               mk.prism("well_cut", rrect(WELL, -0.15), WELL_FLOOR, 30.0, m["floor"])]
    mk.boolean(body, cutters, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.22, 2, 50)
    mk.shade(body, 35)

    def pick(c, n):
        if in_plan(SLOT, c.x, c.y, 0.05) or in_plan(mirror(SLOT), c.x, c.y, 0.05):
            return m["slot"] if n.z > 0.8 and c.z < SLOT_FLOOR + 0.3 else m["slot_wall"]
        if in_plan(WELL, c.x, c.y, 0.3) and c.z < HOUSING_Z - 0.4:
            return m["floor"] if n.z > 0.8 else m["well"]
        if n.z > 0.3:
            return m["top"]
        return None
    mk.paint(body, pick)
    return body


# --- The rim ------------------------------------------------------------------------------------------------------

def plan_reach(plan, theta):
    (cx, cy), hw, hh, r = plan
    return mk.ray_to(lambda x, y: mk.rounded_rect_distance(x, y, hw, hh, r), theta, hw + hh)


def crest(y):
    """The rim's crest at y: RIM_TOP at the ends, dipping by DIP along the long sides' middles."""
    d = abs(y - DIP_Y)
    return RIM_TOP - DIP * smoothstep(DIP_REACH, DIP_FLAT, d)


def rim(m):
    """The rim: a loop lofted round the well, from its inner edge (the well's opening) out to its outer edge, its
    cross-section a rounded crest; its inner wall runs down below the well's floor."""
    (cx, cy) = RIM_OUT[0]
    # The cross-section from the inner edge (u 0) to the outer one (u 1): z below the crest, or z itself at the feet.
    section = [(0.0, None, WELL_FLOOR - 0.2), (0.0, -0.95, None), (0.05, -0.5, None), (0.16, -0.17, None),
               (0.32, 0.0, None), (0.5, -0.02, None), (0.68, -0.12, None), (0.84, -0.4, None), (0.95, -0.95, None),
               (1.0, None, HOUSING_Z - 0.4)]
    rings = []
    for j in range(RIM_SEGMENTS):
        theta = 2 * math.pi * j / RIM_SEGMENTS
        d = Vector((math.cos(theta), math.sin(theta)))
        inner = Vector((cx, cy)) + d * plan_reach(WELL, theta)
        outer = Vector((cx, cy)) + d * plan_reach(RIM_OUT, theta)
        top = crest((inner.y + outer.y) / 2)
        ring = []
        for u, below, z in section:
            p = inner.lerp(outer, u)
            ring.append(Vector((p.x, p.y, top + below if z is None else z)))
        rings.append(ring)
    n = len(section)
    vertices = [p for ring in rings for p in ring]
    faces = []
    for j in range(RIM_SEGMENTS):
        a, b = j * n, ((j + 1) % RIM_SEGMENTS) * n
        for i in range(n):
            i2 = (i + 1) % n
            faces.append((a + i, a + i2, b + i2, b + i))
    obj = k.mesh_object("rim", [tuple(v) for v in vertices], faces, m["rim"])
    k.recalc_normals(obj)
    k.smooth(obj, 50)

    def pick(c, nrm):
        inward = (Vector((cx, cy)) - Vector((c.x, c.y))).normalized()
        facing_in = Vector((nrm.x, nrm.y)).dot(inward) > 0.5
        if facing_in and c.z < HOUSING_Z - 0.6:
            return m["well"]
        if facing_in and nrm.z < 0.55:
            return m["rim_in"]
        return None
    mk.paint(obj, pick)
    return obj


# --- The parts in the holes, the rails ----------------------------------------------------------------------------

def rod(name, a, b, radius, mat, segments=16):
    """A round bar from a to b with rounded ends."""
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    pts = [a - axis * radius * 0.2, a + axis * radius * 0.5, b - axis * radius * 0.5, b + axis * radius * 0.2]
    radii = [radius * 0.55, radius, radius, radius * 0.55]
    obj = mk.tube(name, [tuple(p) for p in pts], radius, mat, segments, radii=radii)
    return k.smooth(obj, 50)


def element(m):
    """The heating element: a rod along the well on two posts; its ends (where the posts hold it) cooler."""
    x, y0, y1, z, r = ELEMENT
    rod("element", (x, y0, z), (x, y1, z), r, m["element"], 20)
    obj = bpy.data.objects["element"]
    mk.paint(obj, lambda c, n: m["element_end"] if c.y < y0 + 1.6 or c.y > y1 - 1.6 else None)
    for i, y in enumerate((y0 + 0.6, y1 - 0.6)):
        post = mk.box(f"post{i}", x - 0.75, x + 0.75, y - 0.55, y + 0.55, WELL_FLOOR - 0.1, z, m["post"])
        mk.bevel(post, 0.2, 2, 35)
        mk.shade(post, 35)


def pins(m):
    for side, plan in (("l", SLOT), ("r", mirror(SLOT))):
        (cx, _), hw, _, _ = plan
        for i, (y, z, r) in enumerate(PINS):
            rod(f"pin_{side}{i}", (cx - hw - 0.2, y, z), (cx + hw + 0.2, y, z), r, m["pin"], 14)


def rails(m):
    for side in (-1, 1):
        x, y0, y1, z, r = RAIL
        x = AXIS_X + side * (x - AXIS_X)
        rod(f"rail{side}", (x, y0, z), (x, y1, z), r, m["rail"], 16)
        edge = AXIS_X + math.copysign(HOUSING[1] - 0.2, x - AXIS_X)
        for i, y in enumerate(CLAMPS):
            clamp = mk.box(f"clamp{side}{i}", min(x, edge), max(x, edge), y - 0.5, y + 0.5, z - 0.6, z + 0.75,
                           m["clamp"])
            mk.bevel(clamp, 0.2, 2, 35)
            mk.shade(clamp, 35)
            bolt = mk.lathe(f"bolt{side}{i}", [(0.55, z + 1.0), (0.55, z + 1.25), (0.35, z + 1.4), (0.01, z + 1.45)],
                            (x, y), m["clamp"], 12)
            k.smooth(bolt, 50)


def own_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r0, r1, spans in OWN:
        for r in range(r0, r1 + 1):
            for c0, c1 in spans:
                for c in range(c0, c1 + 1):
                    mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for frame in FRAMES:
        name, sprite = frame[0], frame[1]
        if only and name not in only:
            continue
        k.reset()
        m = materials(frame)
        housing(m)
        rim(m)
        element(m)
        pins(m)
        rails(m)
        parts = mk.meshes()
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (D %d, its own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), own_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
