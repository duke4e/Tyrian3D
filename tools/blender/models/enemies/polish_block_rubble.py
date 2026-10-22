"""The broken red block (sheet M sprite 3, 2x2: 24 x 28 pixels) and the half-broken one (M 2), polished (2026-10-22,
round 35; it replaces wave3_ah.py's rubble(), block_rubble() and block_half_rubble(): convex hulls of jittered boxes on
a bed of crumbs, the half model the old wave3_ah block's half beside them). models.cfg: model block_rubble /
block_half_rubble enemies/*.glb (unchanged, drawn centred in height: the game rests them on the ground); sprite m 3
block_rubble yaw=0 and sprite m 2 block_half_rubble yaw=0 (unchanged).

Where the levels show them (the enemy data, tools/content/tyrdata.py): SOH JIN's red block (enemy 837) turns to M 3 when
its armour falls under 20 (its damaged look, dgr 3); the indestructible red blocks of ASTEROID1 and WINDY (542, 849)
name M 2 as their wreck (dgr 2), which the sheet draws as the red block's right half (M 1's columns 12-23) beside the
broken block's left half (M 3's columns 0-11): M 2 is exactly those pixels. Not animated; no other enemy shows them.

As the sprite and its 4x upscale draw M 3 (ramp 4's reds 0x40-0x4f, its outline 0x01): the red block's outline, its
glossy candy broken into angular lumps parted by dark cracks: a high lump at the top left (lit 0x4c-0x4f), a broad
flat one at the top right, smaller ones down the left and in the middle, two at the bottom, dark hollows (0x40-0x42)
between them.

Built from polish_blocks.py's block (its body(): the same footprint, walls, roll and dome, the glossy red 0x47 and the
dark foot 0x01) broken along the sprite's cracks: the footprint cut into lumps round SEEDS (the cells of the seeds,
within the block's plan), each lump the block's shape over its cell lowered to SINK of its height, tilted a little
(TILT) and drawn in a little from its neighbours (GAP), its edges bevelled, painted by how its faces meet the light
(0x47, lit 0x4a, its broken faces 0x44, undersides 0x41); under them a dark bed of crumbs (0x41). M 2 is the intact
block's right half (cut at x = 0, moved 12 left) beside the rubble's left half (moved 12 right), the cuts closed in the
block's inside colour (0x44).

Coordinates as in tyrkit: 1 unit = 1 game pixel; +X right, +Y up the sprite, +Z up from the ground; the origin is the
sprite's centre (pixel corner 12, 14).

Replaces wave3_ah.py's section "M 3: the broken red block" (CHUNKS, rubble(), block_rubble(), block_half_rubble());
with the roller and the tank (polish_miners_machines.py) they were all wave3_ah.py still built: it goes, and so do its
kit wave3_ah_kit.py and its pixels wave3_ah_art.py (BLOCK_RED, RUBBLE, HALF among them; nothing else imports them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each one's silhouette from
above against its sprite), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_blocks as pb  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

# The lumps' seeds (the sprite's columns and rows) and how high each stays (a share of the block's height), how it is
# tilted (degrees about x, about y).
SEEDS = [((5.0, 5.0), 0.9, (9.0, -8.0)), ((15.5, 5.5), 0.72, (-5.0, 6.0)), ((21.0, 9.5), 0.55, (3.0, 12.0)),
         ((3.0, 15.5), 0.62, (-7.0, -10.0)), ((9.5, 12.0), 0.5, (8.0, 5.0)), ((16.5, 15.5), 0.75, (-9.0, -4.0)),
         ((5.5, 22.0), 0.58, (-8.0, 6.0)), ((16.0, 22.5), 0.66, (7.0, -8.0)), ((11.0, 18.5), 0.42, (4.0, 9.0))]
GAP = 0.6
CRUMBS = [(9.5, 3.0, 0.9), (12.0, 10.0, 1.0), (6.0, 11.0, 0.8), (13.5, 20.5, 0.9), (20.5, 13.5, 0.8), (8.5, 18.0, 0.7),
          (14.0, 9.0, 0.7)]
BED = 1.1


def seed_xy(c, r):
    return Vector((c + 0.5 - 12.0, 13.5 - r))


def materials():
    return {"red": k.material("rubble_red", palette=0x47, metallic=0.05, roughness=0.3),
            "red_lit": k.material("rubble_red_lit", palette=0x4a, metallic=0.05, roughness=0.28),
            "broken": k.material("rubble_broken", palette=0x44, metallic=0.05, roughness=0.6),
            "dark": k.material("rubble_dark", palette=0x41, metallic=0.0, roughness=0.8),
            "outline": k.material("rubble_outline", palette=0x01, metallic=0.0, roughness=0.85)}


def lumps(m):
    """The block cut into the seeds' cells, each lump lowered, tilted and drawn in a little."""
    seeds = [seed_xy(*s) for s, _, _ in SEEDS]
    out = []
    for i, ((c, r), keep, (tx, ty)) in enumerate(SEEDS):
        block = pb.body(f"lump{i}", m["red"], m["outline"])
        bm = bmesh.new()
        bm.from_mesh(block.data)
        p = seeds[i]
        for j, q in enumerate(seeds):
            if j == i:
                continue
            mid = (p + q) / 2
            n = (q - p).normalized()
            co = Vector((mid.x - n.x * GAP / 2, mid.y - n.y * GAP / 2, 0.0))
            res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                         plane_no=(n.x, n.y, 0.0), clear_outer=True)
            edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
            open_edges = [e for e in edges if len(e.link_faces) == 1]
            if open_edges:
                filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector((n.x, n.y, 0.0))) < 0:
                        f.normal_flip()
                    f.material_index = 1
                    f.smooth = False
        bm.to_mesh(block.data)
        bm.free()
        # lowered (scaled in height about the ground), tilted about its middle, its broken faces dark red
        centre = Vector((p.x, p.y, 0.0))
        tilt = (Matrix.Translation(centre) @ Matrix.Rotation(math.radians(tx), 4, "X") @
                Matrix.Rotation(math.radians(ty), 4, "Y") @ Matrix.Diagonal((1.0, 1.0, keep, 1.0)) @
                Matrix.Translation(-centre))
        block.data.transform(tilt)
        mk.bevel(block, 0.35, 2, 30)
        mk.shade(block, 35)

        def pick(cc, n, block=block):
            if n.z < -0.5:
                return m["dark"]
            if abs(n.z) < 0.35 and cc.z > 1.4:
                return m["broken"] if n.dot(LIGHT) < 0.45 else m["red"]
            if n.z > 0.5:
                return m["red_lit"] if n.dot(LIGHT) > 0.78 else m["red"]
            return None
        mk.paint(block, pick)
        out.append(block)
    # crumbs in the cracks: small dark lumps
    for i, (c, r, s) in enumerate(CRUMBS):
        p = seed_xy(c, r)
        crumb = mk.ball(f"crumb{i}", (p.x, p.y, BED + 0.2), (s, s * 0.8, s * 0.6), m["broken"], 8, 4, angle=20)
        out.append(crumb)
    bed = mk.prism("bed", [(x, y) for x, y in
                           [(math.cos(2 * math.pi * i / 40) * (pb.HALF_W - 0.6) * 1.0,
                             math.sin(2 * math.pi * i / 40) * (pb.HALF_D - 0.6)) for i in range(40)]],
                   -0.4, BED, m["dark"])
    mk.bevel(bed, 0.4, 2, 35)
    out.append(bed)
    return out


def intact(m):
    return [pb.body("block", k.material("rubble_block", palette=0x47, metallic=0.05, roughness=0.3), m["outline"])]


def half(objs, keep_x0, keep_x1, shift, cap):
    """The part of the objects between x0 and x1, the cut closed, moved by shift."""
    out = []
    for o in objs:
        mk.apply(o)
        p = mk.cut(o, (keep_x0, keep_x1, -40.0, 40.0), cap)
        bpy.data.objects.remove(o)
        if p is not None:
            p.data.transform(Matrix.Translation((shift, 0.0, 0.0)))
            out.append(p)
    return out


def export(parts, name, options, sheets, sprite):
    out = mk.outdir(options)
    for o in parts:
        mk.apply(o)
    bpy.context.view_layer.update()
    if sheets:
        mk.compare("%s (M %d) from above" % (name, sprite), mk.coverage(parts, 24, 28),
                   k.sprite_mask(os.path.join(sheets, "enemy_M.png"), sprite))
    drop_unused(parts)
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    bpy.context.view_layer.update()
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj])


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    if not only or "block_rubble" in only:
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        export(lumps(m), "block_rubble", options, sheets, 3)
    if not only or "block_half_rubble" in only:
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        right = half(intact(m), 0.0, 40.0, -12.0, m["broken"])
        left = half(lumps(m), -40.0, 0.0, 12.0, m["broken"])
        export(right + left, "block_half_rubble", options, sheets, 2)


if __name__ == "__main__":
    build()
