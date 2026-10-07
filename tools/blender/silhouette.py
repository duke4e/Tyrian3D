"""Models from a sprite's silhouette, for enemies whose shape is mostly their outline (jets, plates).

A silhouette is the sprite's rows as strings ('.' transparent, anything else covered), as
tools/blender/sprite_profile.py prints them: row 0 at the top. Positions are in model units (game
pixels) with the origin at the sprite's centre: column c is x = c + 0.5 - width / 2 and row r is
y = height / 2 - (r + 0.5), so the model faces the way the sprite does (build it with yaw=0).
"""
import tyrkit as k


def _span(row):
    covered = [i for i, ch in enumerate(row) if ch != "."]
    return (covered[0], covered[-1]) if covered else None


def outline(rows, width=24, inset=0.15):
    """The silhouette's outline as a counter-clockwise polygon [(x, y), ...] (left edges down,
    right edges up; holes and notches between a row's ends are filled). The edges run through the
    rows' middles, so slanted edges are straight lines rather than steps."""
    height = len(rows)
    spans = [(r, _span(row.ljust(width, "."))) for r, row in enumerate(rows)]
    spans = [(r, span) for r, span in spans if span is not None]
    left, right = [], []
    for i, (r, (a, b)) in enumerate(spans):
        x0, x1 = a - width / 2 + inset, b + 1 - width / 2 - inset
        ys = [height / 2 - r - 0.5]
        if i == 0:
            ys = [height / 2 - r - inset] + ys
        if i == len(spans) - 1:
            ys = ys + [height / 2 - r - 1 + inset]
        left += [(x0, y) for y in ys]
        right += [(x1, y) for y in ys]
    return left + right[::-1]


def centre_run(rows, width=24, centre=None):
    """Per covered row: (y, half width) of the run of covered pixels around the middle column."""
    height = len(rows)
    middle = width // 2 if centre is None else centre
    out = []
    for r, row in enumerate(rows):
        row = row.ljust(width, ".")
        if row[middle] == "." and row[middle - 1] == ".":
            continue
        c = middle if row[middle] != "." else middle - 1
        a = b = c
        while a > 0 and row[a - 1] != ".":
            a -= 1
        while b < width - 1 and row[b + 1] != ".":
            b += 1
        out.append((height / 2 - r - 0.5, (b + 1 - a) / 2, (a + b + 1) / 2 - width / 2))
    return out


def plate(name, rows, z0, z1, mat, width=24, bevel=0.0):
    """The silhouette as a flat part from z0 to z1 (wings, a plate)."""
    return k.slab(name, outline(rows, width), z0, z1, mat, bevel_width=bevel, bevel_segments=2)


def fuselage(name, rows, mat, max_radius=2.6, squash=0.8, width=24, taper_rows=2):
    """A round body along the middle: its radius follows the middle run of the silhouette, at most
    max_radius, closing to points at both ends."""
    run = centre_run(rows, width)
    profile = [(y, min(half, max_radius)) for y, half, _ in reversed(run)]  # increasing y
    # Round off the ends.
    for i in range(min(taper_rows, len(profile) // 2)):
        f = (i + 1) / (taper_rows + 1)
        profile[i] = (profile[i][0], profile[i][1] * f)
        profile[-1 - i] = (profile[-1 - i][0], profile[-1 - i][1] * f)
    body = k.lathe(name, profile, mat, segments=20, squash=squash)
    return k.smooth(body, 60)
