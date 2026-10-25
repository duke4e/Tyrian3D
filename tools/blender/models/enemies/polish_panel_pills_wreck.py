"""The three red capsules' wreck (sheet S sprite 191's stand-in: what the asteroid maps paint where panel_pills stands
once it is destroyed, before it comes and where none comes; 247 of them in ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY,
AST. CITY, AST ROCK and GREY MOON), built on polish_panel_pills.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 340, the most common of its paintings; ASTEROID? 3ea5fc307b8e3f67 at
540, 6342): the three sockets and their light rims as the live panel has them, a little sooted (the rims' pixels
0x07-0x0a where the sprite has 0x0b-0x0e); the glass of all three smashed: each socket full of dark red (0x70, nearly
black) with sweeping streaks of bright red (0x73-0x77, the light caught on broken panes), the glass's smooth edge left
only round the socket's foot.

The model: the live rims (polish_panel_pills.rim) with soot laid over them in patches (0x09, 0x07); each capsule the
live glass (polish_panel_pills.glass, its dark state) with its top broken away along a jagged fracture about half way
up (an exact boolean with a noisy cutter: the fracture is the glass's dark inside, 0x70, crazed with lighter cracks,
0x72), the glass's low smooth edge kept round it; shards of the broken panes lying tilted in the hollow (0x73-0x76; a
few of them with an ember's faint glow, 0x76 at 0.3), one leaning up against the middle socket's upper end to the live
glass's height (1.8), so the wreck's bounds in height are the live model's and the game, which centres these models in
height on the ground enemies' layer, places the two alike.

The section "Wreck kit" holds the helpers the other wreck scripts of this round share (polish_panel_gems_wreck.py,
polish_redgem_panel_wreck.py, polish_green_lamp_bunker_wreck.py, polish_red_furnace_wreck.py,
polish_cage_turret_wreck.py).

The same frame as panel_pills: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); drawn as the live model (models.cfg: model panel_pills_wreck enemies/panel_pills_wreck.glb; wreck s 191
panel_pills_wreck, so the game draws it with sprite s 191's options, yaw=0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402


# --- Wreck kit ------------------------------------------------------------------------------------------------------

def perlin(x, y, z=0.0):
    """Perlin noise, -1 to 1 (mathutils' original basis: the same numbers every run)."""
    return noise.noise(Vector((x, y, z)), noise_basis="PERLIN_ORIGINAL")


def fbm(x, y, z=0.0, octaves=3):
    """Perlin noise summed over octaves, about -1 to 1."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * perlin(x * freq, y * freq, z * freq)
        norm += amp
        amp *= 0.5
        freq *= 2.03
    return total / norm


def mat(name, index, metallic=0.3, roughness=0.5, glow=0.0):
    """A palette material; glow > 0 makes it glow faintly in its own colour (an ember: kept well under 0.5, the
    game's bloom burns stronger emission white)."""
    if glow > 0:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def heightfield_cutter(name, x0, x1, y0, y1, step, bottom, top, mat_=None):
    """A closed solid over the plan [x0, x1] x [y0, y1]: its underside the surface z = bottom(x, y) (a grid of step),
    its top flat at `top`: cut out of a body with an exact boolean (DIFFERENCE), it breaks the body away above the
    surface, the fracture taking the cutter's material."""
    nx, ny = max(1, int(math.ceil((x1 - x0) / step))), max(1, int(math.ceil((y1 - y0) / step)))
    xs = [x0 + (x1 - x0) * i / nx for i in range(nx + 1)]
    ys = [y0 + (y1 - y0) * j / ny for j in range(ny + 1)]
    bm = bmesh.new()
    lo = [[bm.verts.new((x, y, bottom(x, y))) for x in xs] for y in ys]
    hi = [[bm.verts.new((x, y, top)) for x in xs] for y in ys]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((lo[j][i], lo[j + 1][i], lo[j + 1][i + 1], lo[j][i + 1]))
            bm.faces.new((hi[j][i], hi[j][i + 1], hi[j + 1][i + 1], hi[j + 1][i]))
    ring = ([(0, i) for i in range(nx)] + [(j, nx) for j in range(ny)] + [(ny, i) for i in range(nx, 0, -1)] +
            [(j, 0) for j in range(ny, 0, -1)])
    for a, b in zip(ring, ring[1:] + ring[:1]):
        bm.faces.new((lo[a[0]][a[1]], lo[b[0]][b[1]], hi[b[0]][b[1]], hi[a[0]][a[1]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat_ is not None:
        obj.data.materials.append(mat_)
    return obj


def break_away(obj, cutter):
    """obj with what lies above the cutter's underside broken away (exact boolean), the fracture faces the cutter's
    material, cleaned up (shading left to the caller)."""
    mk.apply(obj)
    mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    return obj


def paint_field(obj, field, bands, only=None):
    """Gives faces the material of the band their centre's field value falls in: bands [(lowest value, material)],
    ascending (the first band's lowest value is ignored). only(face) limits it to some faces."""
    slots = [mk.slot_of(obj, m) for _, m in bands]
    for poly in obj.data.polygons:
        if only is not None and not only(poly):
            continue
        v = field(poly.center)
        slot = slots[0]
        for (t, _), s in zip(bands[1:], slots[1:]):
            if v >= t:
                slot = s
        poly.material_index = slot
    return obj


def split_off(obj, material, name):
    """Moves the faces of `material` out of obj into an object of their own (so they can be banded alone)."""
    slot = [m.name for m in obj.data.materials].index(material.name)
    new = obj.copy()
    new.data = obj.data.copy()
    new.name = name
    bpy.context.scene.collection.objects.link(new)
    for o, keep in ((obj, lambda f: f.material_index != slot), (new, lambda f: f.material_index == slot)):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if not keep(f)], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
    return new


def bands(obj, field, levels, angle=35.0):
    """Paints obj in bands of a field over its points (levels: [(lowest value, material)], ascending), cut along the
    field's smooth contours (polish_orb_red.band_split), shaded smooth up to angle."""
    from polish_orb_red import band_split
    band_split(obj, [field(v.co) for v in obj.data.vertices], levels)
    return k.smooth(obj, angle)


def grid_cut(obj, step, min_nz=0.5, box=None, min_z=None):
    """Cuts the faces of obj that face up (normal z over min_nz; and whose middle is above min_z, if given) along a
    grid of lines step apart (within box (x0, x1, y0, y1) if given), so that soot painted face by face can follow a
    field over large flat faces."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    x0, x1, y0, y1 = box if box is not None else (min(xs), max(xs), min(ys), max(ys))
    for axis, lo, hi in ((0, x0, x1), (1, y0, y1)):
        t = math.floor(lo / step) * step + step
        while t < hi:
            up = [f for f in bm.faces if f.normal.z > min_nz and (min_z is None or f.calc_center_median().z > min_z)]
            geom = list({v for f in up for v in f.verts}) + list({e for f in up for e in f.edges}) + up
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(t, 0, 0) if axis == 0 else (0, t, 0),
                                   plane_no=(1, 0, 0) if axis == 0 else (0, 1, 0))
            t += step
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def split_piece(obj, co, no, cap_mat, name):
    """obj cut in two by the plane through co with normal no: obj keeps what lies behind the plane, a new object (name)
    what lies in front; both closed over the cut (and over any opening they had) by flat caps of cap_mat (the
    fracture). Returns the new object (None if nothing lies in front)."""
    other = obj.copy()
    other.data = obj.data.copy()
    other.name = name
    bpy.context.scene.collection.objects.link(other)
    for o, outer in ((obj, True), (other, False)):
        slot = mk.slot_of(o, cap_mat)
        bm = bmesh.new()
        bm.from_mesh(o.data)
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                        plane_no=no, clear_outer=outer, clear_inner=not outer)
        del result
        edges = [e for e in bm.edges if len(e.link_faces) == 1]   # (an open shell is closed over its opening too)
        edges.sort(key=lambda e: tuple(sorted((tuple(e.verts[0].co), tuple(e.verts[1].co)))))
        if edges:
            filled = bmesh.ops.holes_fill(bm, edges=edges, sides=0)["faces"]
            for f in bmesh.ops.triangulate(bm, faces=filled)["faces"]:
                f.material_index = slot
                f.smooth = False
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
    if not other.data.polygons:
        bpy.data.objects.remove(other)
        return None
    return other


def turn(objects, pivot, axis, degrees):
    """Turns objects (their meshes) about an axis through pivot."""
    m = (Matrix.Translation(Vector(pivot)) @ Matrix.Rotation(math.radians(degrees), 4, Vector(axis).normalized()) @
         Matrix.Translation(-Vector(pivot)))
    for obj in objects:
        obj.data.transform(m)


def shard(name, base, heading, length, width, rise, mat_, thickness=0.12, skew=0.0, sides=3):
    """A broken pane: a thin plate, a triangle (sides 3) or a quadrilateral (4), lying along heading (degrees in
    plan) from base (x, y, z), its far end raised by rise (its tip at z + rise), skew turning its far corner aside."""
    h = math.radians(heading)
    along = Vector((math.cos(h), math.sin(h), 0.0))
    across = Vector((-along.y, along.x, 0.0))
    b = Vector(base)
    if sides == 3:
        outline = [b - across * width * 0.5, b + across * width * 0.5,
                   b + along * length + across * width * skew + Vector((0, 0, rise))]
    else:
        outline = [b - across * width * 0.5, b + across * width * 0.45,
                   b + along * length * 0.8 + across * width * (0.4 + skew) + Vector((0, 0, rise * 0.8)),
                   b + along * length + across * width * (skew - 0.3) + Vector((0, 0, rise))]
    # the plate's normal (up), and its two faces
    n = (outline[1] - outline[0]).cross(outline[-1] - outline[0]).normalized()
    if n.z < 0:
        n = -n
    top = [p + n * thickness * 0.5 for p in outline]
    bottom = [p - n * thickness * 0.5 for p in outline]
    count = len(outline)
    faces = [tuple(range(count)), tuple(range(2 * count - 1, count - 1, -1))]
    faces += [(i, (i + 1) % count, count + (i + 1) % count, count + i) for i in range(count)]
    obj = k.mesh_object(name, [tuple(p) for p in top + bottom], faces, mat_)
    k.recalc_normals(obj)
    return obj


def rock(name, centre, radii, mat_, seed, subdivisions=1, rough=0.25):
    """A lump of rubble: an icosphere scaled to radii, its surface roughened by noise; flat shaded."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        f = 1.0 + rough * perlin(d.x * 1.7 + seed, d.y * 1.7 - seed, d.z * 1.7)
        v.co = Vector((centre[0] + d.x * radii[0] * f, centre[1] + d.y * radii[1] * f, centre[2] + d.z * radii[2] * f))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat_)
    return obj


def clip_below(objects, z=0.0):
    """Cuts away whatever reaches below z (inside the ground anyway), so the bounds start there."""
    for obj in objects:
        mk.apply(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if bm.verts and min(v.co.z for v in bm.verts) < z - 1e-4:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
        bm.free()


def top_z(objects):
    return max((obj.matrix_world @ v.co).z for obj in objects for v in obj.data.vertices)


def raise_to(obj, z_top):
    """Moves obj up or down so its highest point is at z_top."""
    dz = z_top - top_z([obj])
    obj.data.transform(Matrix.Translation((0, 0, dz)))
    return obj


def drop_unused(objects):
    """Drops material slots no face uses (the exporter would export them)."""
    for obj in objects:
        mesh = obj.data
        used = {p.material_index for p in mesh.polygons}
        for i in reversed(range(len(mesh.materials))):
            if i not in used and len(mesh.materials) > 1:
                mesh.materials.pop(index=i)


def finish(name, options, check_top=None):
    """Exports the scene's meshes to <outdir>/<name>.glb, reports them; check_top: the live model's height, which
    the wreck's highest point must equal (so the game, centring both in height, places them alike)."""
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    drop_unused(parts)
    bpy.context.view_layer.update()
    if check_top is not None:
        print("%s: top %.3f (the live model's %.3f)" % (name, top_z(parts), check_top))
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    return parts


# --- The capsules' wreck --------------------------------------------------------------------------------------------

import polish_panel_pills as live  # noqa: E402

LIVE_TOP = live.GLASS_FOOT + live.GLASS_RISE   # 1.8: the live glass's crest
# The fracture: its height over the socket's floor (the glass broken away above it), how much it wanders.
FRACTURE_Z, FRACTURE_JAG = 0.72, 0.2
# The broken panes per capsule: (x from the capsule's middle, y, heading, length, width, rise, shade, glow, sides).
SHARDS = [
    [(-1.3, -7.0, 66, 5.0, 2.2, 0.55, 0x76, 0.0, 4), (1.3, -1.6, 112, 4.2, 2.0, 0.45, 0x76, 0.0, 4),
     (-1.2, 1.6, 74, 4.6, 2.0, 0.5, 0x77, 0.3, 4), (1.1, 5.6, 248, 3.2, 1.6, 0.4, 0x74, 0.0, 3)],
    [(1.2, -7.2, 104, 4.6, 2.0, 0.5, 0x76, 0.0, 4), (-1.3, -2.8, 70, 4.8, 2.1, 0.55, 0x77, 0.0, 4),
     (1.2, 1.0, 118, 3.6, 1.7, 0.45, 0x76, 0.3, 3)],
    [(1.2, -6.4, 108, 4.6, 2.0, 0.5, 0x77, 0.3, 4), (-1.3, -2.0, 76, 4.4, 2.0, 0.5, 0x76, 0.0, 4),
     (1.2, 2.2, 116, 3.8, 1.8, 0.45, 0x76, 0.0, 4), (-1.0, 5.4, 290, 2.8, 1.5, 0.4, 0x74, 0.0, 3)],
]
# The sliver leaning against the middle socket's upper end, its tip at the live glass's height.
SLIVER = (0.5, 4.2, 84, 4.2, 1.3, 1.3, 0x77)


def fracture_z(x, y, i):
    """The fracture's height under (x, y) in capsule i: about FRACTURE_Z, wandering gently, lower where cracks run."""
    n = fbm(x * 0.28 + 11.0 * i, y * 0.2, 0.5 * i, 2)
    crack = abs(perlin(x * 0.5 + 3.0 * i, y * 0.3, 7.0))
    return FRACTURE_Z + FRACTURE_JAG * n - 0.12 * (1.0 - min(1.0, crack * 3.0))


def crazing(c, i):
    """The fracture's darkest hollows (low) and its lighter cracks (high)."""
    return perlin(c.x * 0.4 + 5.0 * i, c.y * 0.25 - 2.0, 3.0)


def build():
    options = k.args()
    k.reset()
    mats = live.materials("glow")
    dark = mats["glass"]["dark"]
    # (at most 15 materials a model: the game colours no more from the palette; the dark glass's own shades serve the
    # fracture, its edge 0x71 and side 0x72)
    inside, crack = dark[0], dark[1]
    hollow = mat("pillswreck_hollow", 0x70, 0.0, 0.18)
    fresh = mat("pillswreck_fracture", 0x70, 0.0, 0.18)  # (the fracture's faces until they are banded)
    panes = {shade: mat(f"pillswreck_shard_{shade:x}", shade, 0.0, 0.15) for shade in (0x74, 0x76, 0x77)}
    ember = mat("pillswreck_ember", 0x77, 0.0, 0.15, 0.3)
    soot = [mat("pillswreck_soot", 0x09, 0.2, 0.45), mat("pillswreck_soot_dark", 0x07, 0.15, 0.55)]
    for i, cx in enumerate(live.CAPSULES):
        # The rim, sooted in patches.
        rim = live.rim(f"rim{i}", cx, (i > 0, i < 2), 1 if i == 0 else -1 if i == 1 else 0, mats)
        mk.apply(rim)
        rim_slot = mk.slot_of(rim, mats["rim"])

        def sooty(c, i=i):
            return fbm(c.x * 0.5 + 20.0, c.y * 0.38 + 4.0 * i, 1.0) + 0.25
        paint_field(rim, sooty, [(-9.0, mats["rim"]), (0.32, soot[0]), (0.62, soot[1])],
                    only=lambda p: p.material_index == rim_slot)
        # The glass, broken away above the fracture.
        glass = live.glass(f"glass{i}", cx, dark)
        cutter = heightfield_cutter(f"cut{i}", cx - live.HALF_WIDTH - 0.3, cx + live.HALF_WIDTH + 0.3,
                                    -live.GLASS_LENGTH - 0.3, live.GLASS_LENGTH + 0.3, 0.62,
                                    lambda x, y, i=i: fracture_z(x, y, i), 4.0, fresh)
        break_away(glass, cutter)
        k.smooth(glass, 35)
        fracture = split_off(glass, fresh, f"fracture{i}")
        bands(fracture, lambda c, i=i: crazing(c, i), [(-9.0, hollow), (-0.3, inside), (0.18, crack)])
        # The broken panes in the hollow.
        for j, (dx, y, heading, length, width, rise, shade, glow, sides) in enumerate(SHARDS[i]):
            z = fracture_z(cx + dx, y, i) - 0.12
            m = ember if glow else panes[shade]
            shard(f"shard{i}_{j}", (cx + dx, y, z), heading, length, width, rise, m, 0.12, 0.2 * ((j % 3) - 1), sides)
    # The sliver up against the middle socket's upper end, its tip at the live glass's height.
    dx, y, heading, length, width, rise, shade = SLIVER
    m = panes[shade]
    sliver = shard("sliver", (live.CAPSULES[1] + dx, y, fracture_z(live.CAPSULES[1] + dx, y, 1) - 0.15), heading,
                   length, width, rise, m, 0.1, -0.1)
    raise_to(sliver, LIVE_TOP)
    clip_below(mk.meshes())
    finish("panel_pills_wreck", options, LIVE_TOP)


if __name__ == "__main__":
    build()
