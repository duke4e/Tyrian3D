"""A layout of our own for a map laid by a remake from GBC blocks (spec `layout`): DELICORE's layer 1, under its BRAINIAC
platforms (layer 2, the GBC map's), was the GBC map again, the same design twice (the user: "novi layer 1, autonomno
smislimo layout, jer sad ovako s 2 layera kopiramo isti dizajn").

deli(st, h, w): an h x w map of DeliCore's GBC blocks for remake.exact: 0 the pads (UNDERDELI's framed blue mesh), 10 the
brick floor between them, 15 a dome, 16-19 the 2 x 2 machine, 20-23 the crab machine's run of four. From the start (the
bottom) up, stretches of 24-44 rows each one motif, never the same twice in a row:
  spine  a brick corridor two wide winding up the map, rooms off its sides through doors two wide;
  hall   a wide brick hall, pad pillars in rows, machines between them;
  cells  rooms apart in two or three columns, a dome or a machine in each;
  cross  corridors across the map joined by short ones up it, rooms at some joins;
with a row or two of bare pad between stretches. Brick is never one cell thin (the pads' frames close round two)."""
import random

PAD, BRICK, DOME = 0, 10, 15
MACHINE = ((16, 17), (18, 19))
CRAB = (20, 21, 22, 23)


def deli(st, h, w):
    rnd = random.Random(st.get('seed', 1))
    g = [[PAD] * w for _ in range(h)]

    margin = st.get('margin', 1)

    def rect(y0, x0, rows, cols, b=BRICK):
        # (on a grid of 2 x 2 cells from the first column inside the margin: every side and step at least two cells,
        # the user's fifth review: steps of one cell drew the pads' chain as curls, "čudne spojeve")
        y1, x1 = y0 + rows, x0 + cols
        y0, x0 = y0 - y0 % 2, x0 - (x0 - margin) % 2
        y1, x1 = y1 + y1 % 2, x1 + (x1 - margin) % 2
        for y in range(max(0, y0), min(h, y1)):
            for x in range(max(margin, x0), min(w - margin - (w - 2 * margin) % 2, x1)):
                g[y][x] = b

    def brick(y, x):
        return 0 <= y < h and 0 <= x < w and g[y][x] == BRICK

    def inside(y, x, rows, cols):
        """Every cell of the block and the ring round it brick."""
        return all(brick(yy, xx) for yy in range(y - 1, y + rows + 1) for xx in range(x - 1, x + cols + 1))

    wanted = []

    def furnish(y0, x0, rows, cols, n=1):
        wanted.append((y0, x0, rows, cols, n))  # (once the map is laid: a later room or pillar can't cut into them)

    def place(y0, x0, rows, cols, n=1):
        """Machines inside a brick area: the crab's run where four and a ring fit, else the 2 x 2 one, else a dome."""
        spots = [(y, x) for y in range(y0, y0 + rows) for x in range(x0, x0 + cols)]
        rnd.shuffle(spots)
        for _ in range(n):
            kind = rnd.choice(('crab', 'machine', 'dome', 'dome'))
            for y, x in spots:
                if kind == 'crab' and inside(y, x, 1, 4):
                    g[y][x:x + 4] = list(CRAB)
                    break
                if kind == 'machine' and inside(y, x, 2, 2):
                    g[y][x:x + 2] = list(MACHINE[0])
                    g[y + 1][x:x + 2] = list(MACHINE[1])
                    break
                if kind == 'dome' and inside(y, x, 1, 1):
                    g[y][x] = DOME
                    break

    def spine(top, bottom):
        x = rnd.randint(1, w - 3)
        y = bottom
        while y - 4 > top:
            run = min(rnd.randint(5, 9), y - top - 2)
            rect(y - run, x, run, 2)
            # a room off one side, its door two wide
            if rnd.random() < 0.8 and run >= 4:
                rows, cols = rnd.randint(3, min(5, run)), rnd.randint(3, 4)
                ry = y - run + rnd.randint(0, run - rows)
                left = x - cols - 1 >= 0 and (x + 3 + cols > w or rnd.random() < 0.5)
                rx = x - cols - 1 if left else x + 3
                if 0 <= rx and rx + cols <= w:
                    rect(ry, rx, rows, cols)
                    rect(ry + max(0, rows // 2 - 1), x - 1 if left else x + 2, 2, 1)
                    furnish(ry, rx, rows, cols)
            y -= run
            nx = min(max(0, x + rnd.choice((-4, -3, -2, 2, 3, 4))), w - 2)
            rect(y - 2, min(x, nx), 2, abs(nx - x) + 2)  # the turn, two rows across
            x, y = nx, y - 2

    def hall(top, bottom):
        y = bottom
        while y - 8 > top:
            rows = min(y - top - 1, rnd.randint(9, 14))
            cols = rnd.randint(6, w)
            x0 = rnd.randint(0, w - cols)
            rect(y - rows, x0, rows, cols)
            # pad pillars two by two, brick two wide between them
            step = rnd.choice((4, 5))
            for py in range(y - rows + 2, y - 3, step):
                for px in range(x0 + 2, x0 + cols - 3, 4):
                    if rnd.random() < 0.7:
                        rect(py, px, 2, 2, PAD)
            furnish(y - rows + 1, x0 + 1, rows - 2, cols - 2, n=3)
            y -= rows
            if y - 8 > top:  # (to the next one by a corridor of three rows)
                cx = rnd.randint(x0, x0 + cols - 2)
                rect(y - 3, cx, 3, 2)
                y -= 3

    def cells(top, bottom):
        n = rnd.choice((2, 3))
        width = (w - (n - 1)) // n
        y = bottom
        while y - 4 > top:
            rows = min(rnd.randint(3, 6), y - top - 1)
            for k in range(n):
                if rnd.random() < 0.8:
                    cols = rnd.randint(min(3, width), width)
                    x = k * (width + 1) + rnd.randint(0, width - cols)
                    rect(y - rows, x, rows, cols)
                    furnish(y - rows, x, rows, cols)
            y -= rows + rnd.randint(1, 2)

    def cross(top, bottom):
        y, below = bottom, None
        while y - 3 > top:
            x0 = rnd.randint(0, w - 6)
            x1 = rnd.randint(x0 + 5, w - 1)
            rect(y - 2, x0, 2, x1 - x0 + 1)
            if below:  # (joined to the corridor below where both reach)
                lo, hi = max(x0, below[0]), min(x1, below[1]) - 1
                a = rnd.randint(lo, hi) if hi >= lo else below[0]
                rect(y, a, below[2] - y, 2)
            if rnd.random() < 0.5 and y - 6 > top:
                cols = rnd.randint(3, 4)
                rx = min(max(0, rnd.randint(x0, x1) - 1), w - cols)
                rect(y - 5, rx, 3, cols)
                furnish(y - 5, rx, 3, cols)
            below = (x0, x1, y - 2)
            y -= rnd.randint(6, 9)

    motifs = dict(spine=spine, hall=hall, cells=cells, cross=cross)
    y, last = h - st.get('open_start', 10), None
    while y > 16:
        kind = rnd.choice([k for k in motifs if k != last])
        top = max(4, y - rnd.randint(24, 40))
        motifs[kind](top, y)
        last = kind
        y = top - rnd.randint(1, 2)
    # brick never one cell thin (a lone column or row of it between pads): made pad
    for _ in range(3):
        for yy in range(h):
            for xx in range(w):
                if g[yy][xx] != BRICK:
                    continue
                across = brick(yy, xx - 1) or brick(yy, xx + 1) or not (0 < xx < w - 1)
                along = brick(yy - 1, xx) or brick(yy + 1, xx)
                if not across or not along:
                    g[yy][xx] = PAD
    for args in wanted:
        place(*args)
    return g


def repair(g, known, blocks, around, st, left=2, columns=14):
    """The layout made so that every pad cell's neighbourhood (around, on the PC columns the remake lays: the GBC's first
    and last columns go on to the sides) is one the original has at least `least` times (known(neighbourhood): how
    often): a bad cell's GBC cell or one next to it turned pad or brick, the turn that leaves the fewest bad cells round
    it, until none is left or no turn helps. Brick keeps `margin` GBC columns off the map's sides (a room cut by the
    side has no edge there)."""
    least, margin, reach = st.get('least', 2), st.get('margin', 1), st.get('reach', 2)
    h, w = len(g), len(g[0])
    g = [row[:] for row in g]
    col = [min(max(c - left, 0), w - 1) for c in range(columns)]
    for row in g:
        for x in list(range(margin)) + list(range(w - margin, w)):
            row[x] = PAD

    g = smooth(g, margin)
    mask = [[g[i][col[c]] in blocks for c in range(columns)] for i in range(h)]

    def remask(i):
        mask[i] = [g[i][col[c]] in blocks for c in range(columns)]

    def bad(i, c):
        return mask[i][c] and known(around(mask, i, c)) < least

    def score(r0, r1):
        return sum(bad(i, c) for i in range(max(0, r0), min(h, r1 + 1)) for c in range(columns))

    for _ in range(400):
        bads = [(i, c) for i in range(h) for c in range(columns) if bad(i, c)]
        if not bads:
            break
        moved = False
        for i, c in bads:
            if not bad(i, c):
                continue
            base = score(i - 2 - reach, i + 2 + reach)
            best = None
            for y in range(max(0, i - reach), min(h, i + reach + 1)):
                for x in range(max(margin, col[c] - reach), min(w - margin, col[c] + reach + 1)):
                    if g[y][x] not in (PAD, BRICK):
                        continue
                    old = g[y][x]
                    g[y][x] = BRICK if old == PAD else PAD
                    remask(y)
                    now = score(i - 2 - reach, i + 2 + reach)
                    g[y][x] = old
                    remask(y)
                    if now < base and (best is None or now < best[0]):
                        best = (now, y, x)
            if best:
                _, y, x = best
                g[y][x] = BRICK if g[y][x] == PAD else PAD
                remask(y)
                moved = True
        if not moved:
            break
    # (a machine with pad beside it, the repair's or the smoothing's, the room's floor instead: its tiles stood in the
    # pads' frame, broken bits of chain round it; the mask the same)
    seen = set()
    for y in range(h):
        for x in range(w):
            if g[y][x] in (PAD, BRICK) or (y, x) in seen:
                continue
            group, stack = [], [(y, x)]
            seen.add((y, x))
            while stack:
                a, b = stack.pop()
                group.append((a, b))
                for c_, d_ in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= c_ < h and 0 <= d_ < w and (c_, d_) not in seen and g[c_][d_] not in (PAD, BRICK):
                        seen.add((c_, d_))
                        stack.append((c_, d_))
            if any(not (0 <= a + da < h and 0 <= b + db < w) or g[a + da][b + db] == PAD
                   for a, b in group for da in (-1, 0, 1) for db in (-1, 0, 1)):
                for a, b in group:
                    g[a][b] = BRICK
    left_bad = sum(bad(i, c) for i in range(h) for c in range(columns))
    print(f"  layout: {left_bad} pad cells left in a neighbourhood the original has under {least} times")
    return g


def smooth(g, margin=1):
    """Brick and pad both at least two cells thick everywhere (each cell in a 2 x 2 square of its own kind; the machines
    count as brick and stay): a pad notch of one cell in a room's side filled, a brick spur of one cell taken off, until
    nothing changes; the side margins pad."""
    h, w = len(g), len(g[0])

    def covered(y, x, kind):
        return any(all(0 <= y + a < h and 0 <= x + b < w and (g[y + a][x + b] != PAD) == kind
                       for a in (dy, dy + 1) for b in (dx, dx + 1)) for dy in (-1, 0) for dx in (-1, 0))
    for _ in range(10):
        changed = 0
        for y in range(h):  # (brick no thinner than two: a spur pad)
            for x in range(w):
                if g[y][x] == BRICK and not covered(y, x, True):
                    g[y][x] = PAD
                    changed += 1
        for y in range(h):  # (pad no thinner than two: a notch brick)
            for x in range(margin, w - margin):
                if g[y][x] == PAD and not covered(y, x, False):
                    g[y][x] = BRICK
                    changed += 1
        if not changed:
            break
    return g
