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

    def rect(y0, x0, rows, cols, b=BRICK):
        for y in range(max(0, y0), min(h, y0 + rows)):
            for x in range(max(0, x0), min(w, x0 + cols)):
                g[y][x] = b

    def brick(y, x):
        return 0 <= y < h and 0 <= x < w and g[y][x] == BRICK

    def inside(y, x, rows, cols):
        """Every cell of the block and the ring round it brick."""
        return all(brick(yy, xx) for yy in range(y - 1, y + rows + 1) for xx in range(x - 1, x + cols + 1))

    def furnish(y0, x0, rows, cols, n=1):
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
    return g
