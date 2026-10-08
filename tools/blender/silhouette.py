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


def _simplify(points, epsilon):
    """Douglas-Peucker on an open polyline."""
    if len(points) < 3:
        return points
    (ax, ay), (bx, by) = points[0], points[-1]
    dx, dy = bx - ax, by - ay
    length = (dx * dx + dy * dy) ** 0.5
    worst, at = -1.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        d = abs(dy * (px - ax) - dx * (py - ay)) / length if length > 0 else ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        if d > worst:
            worst, at = d, i
    if worst <= epsilon:
        return [points[0], points[-1]]
    return _simplify(points[:at + 1], epsilon)[:-1] + _simplify(points[at:], epsilon)


def outline(rows, width=24, epsilon=0.75):
    """The silhouette's outline as a counter-clockwise polygon [(x, y), ...]: the boundary of the
    covered pixels (notches and gaps between parts stay; holes inside are filled), simplified so
    that slanted edges are straight lines rather than steps."""
    height = len(rows)
    grid = [row.ljust(width, ".") for row in rows]
    covered = lambda x, r: 0 <= x < width and 0 <= r < height and grid[r][x] != "."
    # Pixel edges between covered and empty pixels, clockwise round the covered ones (rows down).
    edges = {}
    for r in range(height):
        for x in range(width):
            if not covered(x, r):
                continue
            if not covered(x, r - 1):
                edges.setdefault((x, r), []).append((x + 1, r))
            if not covered(x + 1, r):
                edges.setdefault((x + 1, r), []).append((x + 1, r + 1))
            if not covered(x, r + 1):
                edges.setdefault((x + 1, r + 1), []).append((x, r + 1))
            if not covered(x - 1, r):
                edges.setdefault((x, r + 1), []).append((x, r))
    loops = []
    while edges:
        start = next(iter(edges))
        loop, point = [start], start
        while True:
            nexts = edges.get(point)
            if not nexts:
                break
            nxt = nexts.pop()
            if not nexts:
                del edges[point]
            if nxt == start:
                break
            loop.append(nxt)
            point = nxt
        loops.append(loop)
    loop = max(loops, key=len)  # the outer boundary
    # Drop points in the middle of straight runs, then simplify from the two farthest points.
    far = max(range(len(loop)), key=lambda i: (loop[i][0] - loop[0][0]) ** 2 + (loop[i][1] - loop[0][1]) ** 2)
    first, second = loop[:far + 1], loop[far:] + [loop[0]]
    points = _simplify(first, epsilon)[:-1] + _simplify(second, epsilon)[:-1]
    polygon = [(px - width / 2, height / 2 - py) for px, py in points]
    area = sum(polygon[i][0] * polygon[(i + 1) % len(polygon)][1] - polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
               for i in range(len(polygon)))
    return polygon if area > 0 else polygon[::-1]


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
