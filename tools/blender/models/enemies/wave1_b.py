"""Enemies of wave 1, batch B, modelled as their sprites look (models.cfg: yaw=0):

(tank_pod_left / tank_pod_right, C 197 / C 199, are built by polish_tank_pod.py; arm_ball_left /
arm_ball_right, V 89 / V 93, by polish_arm_bridge.py; flame_drop, 3 267, by polish_flame_drop.py; comet_tail /
comet_head, 5 203 / 5 241, by polish_comet.py; cell_sphere, 3 229 / 5 89, by polish_cell_sphere.py; rod_top /
rod_tail, 5 55 / 5 93, by polish_tunnel_rod.py.)
- fire_orb (sheet A 277): a glossy glowing orange orb, red round the side; the sprite pulses darker
  (glow option).

usage: Blender -b --factory-startup -P wave1_b.py -- [--only name,name] [--preview <prefix>]
       [--sheets <TYR3D_EXTRACT sheets dir>]   (--sheets: print each model's silhouette overlap)
"""
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

W, H = 24, 28  # a 2x2 sprite


# --- Helpers -------------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.4, glow=None, color=None):
    """A palette material; glow: emission strength, in the palette colour (or color)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=color or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def band_split(obj, values, bands, face_band=None, smooth_angle=60):
    """Colours a mesh in bands of a value per vertex, cutting its faces along the bands' borders so
    the borders are smooth lines rather than the faces' zigzag. bands: [(lowest value, material)],
    ascending (the first takes everything below the second). face_band(polygon) may give a band for
    a whole face (or None); vertices whose value is None go to the first band."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = [bands[0][0] - 1 if v is None else v for v in values]
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina = (vals[a] >= t) == above
            inb = (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, materials = [], []
    for poly in mesh.polygons:
        indices = list(poly.vertices)
        forced = face_band(poly) if face_band else None
        if forced is not None:
            faces.append(indices)
            materials.append(forced)
            continue
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                materials.append(b)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for _, mat in bands:
        new.materials.append(mat)
    for poly, m in zip(new.polygons, materials):
        poly.material_index = m
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


# --- A 277: the glowing orb ----------------------------------------------------------------------

def fire_orb():
    """A glossy orange orb, red round the side; the game's light gives it the sprite's highlight."""
    shades = [(-9.0, 119), (0.22, 120), (0.38, 121), (0.52, 122)]  # by height on the orb
    bands = [(lowest, pal(f"orb_{index}", index, metallic=0.0, roughness=0.12, glow=0.3)) for lowest, index in shades]
    centre, radii = Vector((0.0, 0.5, 8.4)), Vector((8.9, 8.5, 8.2))
    orb = k.smooth(k.ellipsoid("orb", centre, radii, bands[-1][1], 64, 32), 80)
    band_split(orb, [(v.co.z - centre.z) / radii.z for v in orb.data.vertices], bands, smooth_angle=80)


# --- Building ------------------------------------------------------------------------------------

# name: (builder, [(sheet file, sprite)] its top view should match)
MODELS = {
    "fire_orb": (fire_orb, [("enemy_A", 277)]),
}


def main():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    here = os.path.dirname(os.path.abspath(__file__))
    for name, (build, sprites) in MODELS.items():
        if only and name not in only:
            continue
        k.reset()
        build()
        if "sheets" in options:
            for sheet, index in sprites:
                print(f"== {name} vs {sheet} {index}")
                k.check_silhouette(os.path.join(options["sheets"], sheet + ".png"), index)
        bpy.context.view_layer.update()
        corners = [obj.matrix_world @ Vector(c) for obj in bpy.context.scene.objects if obj.type == "MESH"
                   for c in obj.bound_box]
        low = Vector([min(c[i] for c in corners) for i in range(3)])
        high = Vector([max(c[i] for c in corners) for i in range(3)])
        print(f"== {name} bounds {tuple(round(v, 2) for v in low)} .. {tuple(round(v, 2) for v in high)}")
        k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"  # the palette's colours as they are
            k.preview(f"{options['preview']}_{name}", (W, H))


main()
