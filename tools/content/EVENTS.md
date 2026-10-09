# Tyrian level events: a reference for writing levels

How the game (this fork of OpenTyrian2000) reads a level and runs its events, from the C code.
Line numbers are for the tree at commit 439aa68. `tools/content/tyrevents.py` prints any level's
events decoded this way. "Uncertain" marks what the code does not settle.

Notation: an event is `time type d1 d2 d3 d4 d5 d6` with d1 = `eventdat`, d2 = `eventdat2` (s16),
d3 = `eventdat3`, d5 = `eventdat5`, d6 = `eventdat6` (s8) and d4 = `eventdat4` (u8). "Tick" = one
pass of the level loop, about 28.75 ms at the Normal game speed (frameCountMax 2 times
delayPeriod 0x4300 x 12/14318180 s, `config.c` 584-618, `nortsong.c` 46/354): about 35 ticks/s.

## Sources

| What | Where |
|---|---|
| Script `]L` line, level and map loading | `src/tyrian2.c` 3252-3265, 3670-3820 (`JE_loadMap`) |
| Level start state | `src/tyrian2.c` 1330-1411, 1573-1632 |
| Level loop: events, backgrounds, enemy passes | `src/tyrian2.c` 1634-3020 (`JE_main`) |
| Event switch | `src/tyrian2.c` 4964-5885 (`JE_eventSystem`) |
| Enemy creation | `src/tyrian2.c` 4528-4915 (`JE_newEnemy`, `JE_makeEnemy`, `JE_createNewEventEnemy`) |
| Jumps, link search | `src/tyrian2.c` 4917-4962 (`JE_eventJump`, `JE_searchFor`) |
| Enemy movement, shots, launches | `src/tyrian2.c` 699-1150 (`JE_drawEnemy`) |
| Hits, damage state, link chains, drops | `src/tyrian2.c` ~2085-2300 |
| Background drawing and scrolling | `src/backgrnd.c` 157-268 |
| Horizontal parallax | `src/mainint.c` 4877-4903; ship x clamp 4195-4204 |
| Playfield copy to the screen (x+24, 264x184) | `src/tyrian2.c` 87-160 (`JE_starShowVGA`) |
| Pick-ups (`value`), contact damage | `src/mainint.c` 4916-5232 (`JE_playerCollide`) |
| Level end fly-out | `src/mainint.c` 4032-4047, 4850-4854 |
| Enemy data record | `src/episodes.h` 118-147, loader `src/episodes.c` 191-224 |
| Enemy sprite sheet letters | `src/lvlmast.c` 23-27 (`shapeFile[]`); `EVENT_MAXIMUM` 2500 `src/lvlmast.h` 24 |

## 1. Files

**Script** (`levelsN.dat`, encrypted strings; `tools/levels.py`): a section's `]L[` line loads a
level: `]L[ 9999 004 TYRIAN   18 09` = next section (col 9), name (13-21), song (22), level file
number (25), optional `$` bonus flags (27/28). A section may hold several `]L` lines with `]h[`
(skip the next line on Hard and up) or `]H[` (jump on Easy/Normal) before them: episode 1 TYRIAN
is file 9 on Easy/Normal, file 15 on Hard+.

**Level file** (`tyrianN.lvl`): u16 count, s32 offsets, entries. Level n is entries 2n-2 (header
and events) and 2n-1 (maps); the game seeks entry 2n-2 and reads the maps straight after the
events, so entry 2n-1 must start exactly there (`tyrformat.py` writes it so). Episodes 4+ end with
an item data entry. Entry 2n-2 (all little-endian):

```
char mapFile            unused by the loader
char shapeFile          tile set: shapes<c>.dat (600 tiles of 24x28, each: bool blank, 672 bytes)
u16  mapX, mapX2, mapX3 1, 1, 1 in every original level; mapX and mapX3 shift enemy x (section 4)
u16  levelEnemyMax; u16 levelEnemy[levelEnemyMax]   random sky enemies (max 40)
u16  maxEvent           at most 2499 (eventRec[2500], a sentinel 65500 is written after the last)
maxEvent x 11 bytes: u16 time, u8 type, s16 d1, s16 d2, s8 d3, s8 d5, s8 d6, u8 d4
```

Entry 2n-1: three tables of 128 **big-endian** u16 shape numbers (1-600 in shapes<c>.dat; the
game swaps after a LE read, 3702-3710), then map 1 (14x300 bytes), map 2 (14x600), map 3 (15x600),
row-major from row 0 (the top/end of the level). A map byte is an index into its layer's table:

* layer 1 uses indexes 0-71 (`megaData1.shapes[72]`); a blank shape becomes a black tile.
* layer 2 uses 0-70; index 71 and blank shapes become "no tile" (transparent, NULL).
* layer 3 uses 0-69; indexes 70-71 and blank shapes become "no tile".
* `ref[][]` (3032) is an uninitialised stack array filled only for table entries whose shape
  number matches one of shapes 1-600 (3726-3783). **Every index a map uses, including 71 on
  layer 2 and 70/71 on layer 3, needs a table entry of 1-600**, or the tile pointer is garbage.
  The original tables have 127-128 non-zero entries.

Events must be sorted by time (the dispatcher stops at the first event later than the clock).

## 2. The level clock and event dispatch

* `curLoc` (the clock, u16) starts at 0, `eventLoc` (1-based next event) at 1 (1383-1384).
* Every tick, before anything moves: `while (eventRec[eventLoc-1].eventtime <= curLoc && eventLoc
  <= maxEvent) JE_eventSystem();` (1817-1818). Each call runs one event and does `eventLoc++`
  (5884). Events of the same time run in file order, in the same tick.
* Layer 1 moves in the same statement block that advances the clock (1844-1859):
  `if (--map1YDelay == 0) { map1YDelay = map1YDelayMax; curLoc += backMove; backPos += backMove;
  if (backPos > 27) { backPos -= 28; mapY--; mapYPos -= 14; } }`.
  So **the clock is the number of pixels layer 1 has scrolled**, whatever the speed. Speed only
  changes how many ticks pass between event times, and how far the clock can overshoot an
  event time: an event at T fires at the first tick with curLoc >= T, i.e. at T..T+backMove-1.
  `tyrevents.py` simulates this and prints "fires at curLoc N" when it differs from T.
* Slow mode (event 3: map1YDelayMax 3): `backMove` is forced to 1 on the tick the map moves and 0
  on the others (1834-1835), so the clock still equals the layer 1 scroll (1 px per 3 ticks).
* `backMove == 0` (map stopped): the clock stops, so events stop, unless forced events are on
  (event 53): then `curLoc++` every tick while the map stands still (1831-1832).
* The clock is also set without moving the map by events 38, 54, 70, 71, 75 (skip) and by the level
  timer (67), the return (76) and the link-254 death jump (57); event 77 moves layers 1/2 without
  the clock. After any of these, clock and map no longer agree.

Jumps (`JE_eventJump`, 4917-4936): target 65535 (d1 = -1) means "return": `curLoc = returnLoc`;
otherwise `returnLoc = curLoc + 1; curLoc = target`. Then eventLoc is set so that, after the
`eventLoc++` of the event switch, the first event with time >= curLoc runs next (in the same
tick when its time equals the target). Quirk: the timer (2747-2751), the return (2698-2702) and
the link-254 jump (2211-2212) call `JE_eventJump` outside the switch, without the `++`, so the
event just *before* the target runs again too (and a target at or before the first event reads
`eventRec[-1]`). Event 38 is different again: it resumes at the *last* event with time <= target
(that event runs again). `returnLoc` is a single value: a later 54 overwrites it (no nesting).

Skips (61, 63, 66, 75, 80) add to eventLoc: the next N events in file order are skipped whatever
their times; the skip happens when the skip event runs.

## 3. Maps and scrolling

Three layers, all scrolling down the screen, read from the bottom of the map (high row numbers)
towards row 0. Tiles are 24x28. Initial rows (1330-1335): `mapY = 292` (layer 1), `mapY2 = mapY3 =
592`; the layer pointers are `&mainmap[mapY][0] - 1` (that `-1` matters for events 77/81).

**Vertical.** A layer that has scrolled S pixels draws map row r at screen y = 28(r - start) + S,
with start = 292 (layer 1) or 592 (layers 2, 3) (draw loop `i = -1..6`, `backgrnd.c` 157-268).
The visible playfield is y 0-183, so:

* the row at the top edge is `start - ceil(S/28)`; rows down to `start + floor((183 - S)/28)` show.
* at the start rows 292-298 (layer 1) / 592-598 show; rows 299 / 599 never show.
* layer 1: S = curLoc (section 2). Layer 2: S2 grows by backMove2 every map2YDelayMax ticks
  (moved inside its draw function, `backgrnd.c` 198-211). Layer 3: S3 grows by backMove3 every tick
  (moved before drawing, 246-256). With constant ratios (event 2 with d2 = k*d1) S2 = k*curLoc.
* level start speeds are 1/2/3 (1385-1387); nearly every level sets its own with an event 2 at 0.
* the end of a map: `BKwrapN = BKwrapNto = &mainmap[1][0]` (1630-1632) and every tick
  `if (mapYPos <= BKwrap1) mapYPos = BKwrap1to` (1658-1664): at mapY 1 the pointer stops
  (shifted one tile) and the top row band repeats. Layer 1 therefore lasts 28*291 = 8148 px of
  clock at most; layers 2/3 last 16548 px of their own scroll (at the usual 2x and 3x ratios:
  8274 and 5516 clock pixels). Original levels end around clock 7700-8100 (or stop the map).
* event 81 moves layer 2's wrap: when its pointer reaches `&mainmap2[0][0] + d1/2` it is set to
  `+ d2/2` (positions are 2 x a tile index, the original's 16-bit maps; row-aligned values are
  `28*mapY - 2`). Layers 1 and 3 have no wrap event. Event 77 sets layers 1 and 2 directly.

**Horizontal (parallax).** The ship's x (40-256) picks each layer's offset every tick
(`mainint.c` 4877-4903): `ofs3 = floor((260 - (x - 36)) / 224 * 72 - 1)` (11-81),
`ofs2 = ofs3 * 2 / 3` (7-54), `ofs1 = ofs2 / 2` (3-27). The game draws into a 320-wide surface and
shows x 24-287 (`JE_starShowVGA` copies 264x184 from x 24). In those game coordinates:

* layer 1 column c starts at x = 24c - 48 + ofs1 (columns 3-12 always visible, 12 losing up to
  3 px at the far left; 2 and 13 partly; 1 by at most 3 px; column 0 never).
* layer 2 column c starts at x = 24c - 48 + ofs2 (columns 0-13 all reachable at the edges).
* layer 3 column c starts at x = 24c - 72 + ofs3 (columns 0-14); with event 65 (background3x1)
  layer 3 uses layer 1's offset: x = 24c - 48 + ofs1.
* with the ship centred (x 148): ofs1 15, ofs2 30, ofs3 46.

**Drawing order** (bottom to top, 1837-2605): layer 1; starfield (events 8/9); layer 2 if
`background2over` is 0 or 3; ground enemies (slots 25-49, then 75-99); layer 2 if
`background2over` is 1 (the default); layer 3 if `background3over` is 2; sky enemies (0-24) unless
event 73; layer 3 if `background3over` is 0 (default); top enemies (50-74) unless event 29; shots
and ship; layer 3 if `background3over` is 1 (event 21: over the ship); top enemies if event 29;
sky enemies if event 73; layer 2 if `background2over` is 2. Pixel 0 is transparent everywhere.

## 4. Enemies

### Slots and layers

100 enemy slots, 25 per layer. A layer with 25 live enemies silently drops new ones.

| Slots | Layer | Created by | Drawn with x offset | Moves down each tick by |
|---|---|---|---|---|
| 0-24 | sky | 15, 18, 50, 12 (d6=2), random enemies | ofs2 (layer 2's) | 0 (does not scroll) |
| 25-49 | ground | 6, 17, 49, 12 (d6=0/1) | ofs1 | backMove (layer 1) |
| 50-74 | top | 7, 23, 32, 51, 12 (d6=3) | ofs3, or ofs1 with event 65 | backMove3 (layer 3) |
| 75-99 | ground2 | 10, 56, 52, 12 (d6=4); launches from ground enemies | ofs1 | backMove (layer 1) |

(`JE_drawEnemy(50/100/25/75)` and `tempMapXOfs`/`tempBackMove`, 1909-2014.) **Ground enemies stay
on the ground** because they move down by `backMove` in the same ticks as layer 1 (slow mode
toggles `backMove` 1/0 for both) and are drawn with layer 1's parallax offset. Ground2 is a second
ground list drawn over the first. Top enemies follow layer 3 the same way; sky enemies do not
scroll and use layer 2's parallax.

### Creating an enemy from an event (`JE_createNewEventEnemy`, 4834-4915)

1. First free slot in the layer's 25; none: nothing happens.
2. `JE_makeEnemy(type = d1 (+ part for event 12))` copies enemyDat (below) and sets a start
   position from enemyDat `startx/starty +- startxc/startyc`.
3. Unless d2 is -99 (keep that start position), x and y are set (2nd assignment wins; the
   `ey -= backMoveN` lines are dead code):
   * sky: `ex = d2 - (mapX-1)*24`
   * ground, ground2: `ex = d2 - (mapX-1)*24 - 12`
   * top: `ex = d2 - mapX3*24 - 42`, or `d2 - (mapX-1)*24 - 12` with event 65; event 72 (x1b):
     -6 more, and ey +4
   * `ey = -28`
   * d2 = -200: x random 24-231 (written back into the event, so a re-run reuses it).
4. Event 26 (smallEnemyAdjust) on and a 1x1 enemy: ex -= 10, ey -= 7.
5. `ey += d5; eyc += d3; linknum = d4; fixedmovey = d6`. The "bottom" events then overwrite ey:
   17/18 `190 + d5`, 23 `180 + d5`, 32/56 `190`.

So for spawn events: **d1 enemy type, d2 x, d3 extra y speed, d4 link number, d5 y offset,
d6 constant extra y movement per tick**. Event 12 uses d6 for the layer and zeroes it in the record;
49-52 use d1 as the sprite number, d3 as the sprite sheet and d6 as armor (they patch enemyDat[0]
and make enemy 0).

Sprites: `esize` 0 is one 12x14 sprite drawn at (ex + ofs, ey); `esize` 1 is 2x2 sprites
(24x28) drawn from (ex - 6 + ofs, ey - 7), sprite g at top-left, g+1, g+19, g+20
(`JE_drawEnemy` 756-773). Enemies are drawn first and moved after, so a new enemy shows at its
spawn position for one tick.

### Placing ground enemies on the map

For a ground/ground2 enemy fired when the layer 1 scroll is S (= curLoc, section 2), in layer 1
map pixels (column 0's left edge x = 0, row 0's top y = 0) its reference point is

    X = d2 + 36 - 24*(mapX-1)        Y = 28*291 + d5 - S  (= 8148 + d5 - S)

and it keeps that map position as long as it has no own speed. A 2x2 sprite covers
[X-6, X+18) x [Y-7, Y+21). To put a 2x2 enemy exactly on tile (c, r) of layer 1 (mapX 1):

    d2 = 24c - 30        S = 28*(291 - r) - 7 + d5

The originals' most common choice (about 40% of ground spawns for x, a third for time; many others
are deliberately off the grid) is d2 = 24c - 30 and time - d5 = 28k + 20, i.e. one pixel below the
grid at speed 1 (at odd speeds/phases the overshoot of the clock can make it exact or put it a
few pixels off): for row r, time = 28*(291 - r) - 8 + d5. `tyrevents.py` prints `@L1 col c row r`
for each ground spawn (2x2 top-left corner; integers = on the grid). Event 12's four parts are at
(+24, 0), (0, -28), (+24, -28) from part 0: a 48x56 block whose top-left tile is (c, r-1).
A top enemy is on layer 3 column c when d2 = 24c (mapX3 1); its row depends on layer 3's own
scroll. Sky enemy x at a centred ship: screen x (0-263) = d2 for a 2x2 sprite's left edge.

### enemyDat fields (`episodes.h` 118-147; episodes 1-3 in tyrian.hdt, 4+ in the level file)

Types 0-850 and 1001-1850 (the T2000 bank). `JE_makeEnemy` (4542-4832):

* `armor`: hit points, scaled by difficulty (Wimp x0.5+1, Easy x0.75+1, Normal x1, Hard x1.2,
  Impossible x1.5, Insanity x1.8, Suicide x2, Maniacal x3, Zinglon x4, Nortaneous x8; max 254).
  255: indestructible. 0: not shootable (`enemyAvail` 2): a pick-up if `value` != 0, otherwise
  scenery that scrolls with its layer.
* `value`: cash on death (2-9999, scaled by difficulty x0.75..x8, max 10000); 1 = data cube. For
  armor-0 pick-ups (`mainint.c` 4928-5200): -1/-2 front/rear power-up, -3 orbiting thing, -4
  superbomb, -5 hot dog, 10000+n warp (nextLevel = n), 20000+n armor, 30000+n arcade weapons,
  31000+n rear weapon n, 32000+n sidekick n, 32100+n special n. 30000 = purple ball.
* `esize` (0 1x1, 1 2x2), `egraphic[20]` frames (999 = remove), `ani` frame count, `animate`
  (0 still, 1 always, 2 only when firing), `shapebank` (sprite sheet, below).
* `explosiontype`: bit 0 = 0: contact with the ship damages it (`mainint.c` 5219-5221) and the
  small-explosion set 2-5 is used (code calls this `enemyground`, the comment in mainint calls it
  "not ground"; the naming is contradictory, the behaviour is as stated); bit 0 = 1: no contact
  damage (ground turrets usually). `explosiontype >> 1`: explosion size.
* movement: `xmove/ymove` -> velocity `exc/eyc` (px per tick); `xcaccel/ycaccel` -> `excc/eycc`:
  every |excc| ticks exc changes by 1 towards `exrev`, and on reaching it the direction flips
  (exrev, excc negated): a zig-zag between -exrev and +exrev; `xrev/yrev` 0 = 100 (no flip in
  practice), -99 = 0. `xaccel/yaccel` 0 or 90+n: homing, exc steps 1 towards the ship
  (probability n/11 a tick) up to |exc| < n (`JE_drawEnemy` 709-735).
* `startx/starty/startxc/startyc`: start position (+- random): used by d2 = -99, random level
  enemies (`levelEnemy`, sky slots); launched and dropped enemies take their parent's position.
* `tur[3]`, `freq[3]`: guns (weapon numbers; 251-255 are magnets/repulsor/boss missiles) and fire
  periods in ticks (halved above Normal, again above Maniacal).
* `elaunchfreq`, `elaunchtype`: launch enemy `elaunchtype % 1000` every `elaunchfreq` ticks at the
  enemy's position (`/1000` = 1: only when level with the ship); ground (25-49) launches go to
  ground2 (75-99), others to their own layer (1076-1140).
* `dgr`, `dlevel`, `dani`: damaged look when armor falls to `dlevel` (graphic `dgr` or animation
  `dani`); damaged enemies stop firing and stop counting as "on screen". dlevel -1: leaves a
  wreck. `eenemydie`: enemy created at its position when it dies (same layer; sky if its value >
  30000).

Per tick (`JE_drawEnemy` 826-862): `ey += fixedmovey; ex += exc` (gone if ex < -80 or > 340);
`ey += eyc` (gone if ey < -112 or > 190); bounce box (event 74, default +-10000); pick-ups kept in
x -5..245; `ey += layer scroll`. An enemy counts as **on screen** while its slot is live, ex is in
(-24, 296) and it is not in its damaged state; y is not checked, so enemies above the top edge
count (864-876).

### Sprite sheets (event 5)

Event 5 loads up to four enemy sprite sheets: d1, d2, d3, d4 > 0 are indexes (1-based) into
`shapeFile[] = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%"`, loading `newsh<letter>.shp`; 0 unloads.
An enemy's `shapebank` must be one of the four loaded ids, or 21 (coins and gems) or 26
(two-player items), which are always there (4560-4580); otherwise the slot's previous sprite sheet
is used and a warning printed. Original levels usually load them with one event 5 at time 0
(78 type-5 events in 70 level files).

### Link numbers (d4 -> `linknum`)

* Events 19, 20, 24, 25, 27, 31, 33, 39, 45, 47, 55, 58-60, 74, 85 act on all enemies with a link
  number (0 = all for 20, 25, 27, 47, 55, 59, 74; 99 = all for 31, 58).
* Killing an enemy with link L (0 counts as 255 = alone) also kills (2209-2300): every enemy with
  link L; with link L - 100; with 40 < link <= L in the same block of 20 (link/20 == L/20); and
  all enemies when L is 254 (then event 57's jump). Multi-sprite enemies share a link. The
  damaged-state switch spreads the same way to enemies with `dlevel` > 0 (2139-2195).
* Boss bars (event 79) show the lowest armor among enemies with the given link.
* `JE_searchFor` (events 70, 75) only counts live shootable enemies (`enemyAvail` 0).

### Random enemies

Each tick, with random enemies on (default; events 13/14), `rand % 100 > levelEnemyFrequency`
(default 96, event 37) creates `levelEnemy[rand % levelEnemyMax]` in the sky slots at its
enemyDat start position (1962-1969). With `levelEnemyMax` 0 that is a modulo by zero: a level
without random enemies must turn them off (event 13 at time 0, as all originals do).

## 5. How a level ends

* **Event 11**: d1 = 1 (or all players dead): ends at once. Otherwise `endLevel = true, levelEnd =
  40`: the level-complete song plays, the ship flies up and the level ends when `levelEnd`
  (decremented per tick, `mainint.c` 4850-4853) reaches 0 or the ship is above y -200.
* **Event 36**: from then on, the first tick with no enemy on screen and no explosion running ends
  the level the same way (2988-3003). Bosses: spawn the boss, then 36 (and 79 for the bar).
* Typical originals: 36 after the boss appears, and an event 11 near clock 7700-8100 as the end
  of the map (8148 is the last useful layer 1 clock). Levels that stop the map for a boss turn on
  forced events (53) so later events (and the 11) still come.
* Death of all players: `reallyEndLevel`. The level timer (67) jumps (its target usually holds an
  11). Scenery enemies (armor 0, value 0) count as "on screen" and delay 36 and event 4 restarts.

## 6. Map stops

* Stop: event 2 or 30 with d1 = 0 (usually 0, 0, 0). The clock stops too unless event 53.
* Automatic restart, set up by event 4 (or 83): `stopBackgrounds = true`, `stopBackgroundNum` =
  1 (d1 0/1), 2 (d1 2) or 3 (d1 3). Then:
  * num 1: a tick with no ground/ground2 enemy on screen sets it to 9 (1916-1920); num 2: a tick
    with no sky enemy on screen (1995-1999); num 3: only the rule below.
  * num 9, `backMove == 0` and no explosion running: speeds become 1/2/3 (2969-2985).
  * any tick with no enemy at all on screen (and the level not ending): if `stopBackgrounds`,
    speeds become 1/2/3 (3004-3010), even if the map was not stopped.
  * the restart does not reset the map delays (slow mode stays slow); event 2 with d1 > 0 clears
    `stopBackgroundNum` (not `stopBackgrounds`).

## 7. Event reference

Every type the switch knows (1-85, 99). Others (0, 86-98, 100-255) print a warning and are
skipped; the originals contain a few type 0 (all zero) at time 0 and one 108.

| Type | Name | Fields and effect |
|---|---|---|
| 1 | starfield speed | `starfield_speed = d1` |
| 2 | scroll speed | backMove/2/3 = d1/d2/d3 (px per tick for layers 1/2/3), delays 1; explosions drift with d2 (d1 if d2 is 0); d1 > 0 clears stopBackgroundNum |
| 3 | slow scroll | layer 1: 1 px / 3 ticks, layer 2: 1 px / 2 ticks, layer 3: 1 px / tick |
| 4 | map stop restart | see section 6 (d1: 0/1 ground clear, 2 sky clear, 3 all clear) |
| 5 | enemy sprite sheets | d1-d4: shapeFile indexes for sheet slots 1-4 (0 = unload) |
| 6 | ground enemy | slots 25-49; d1 type, d2 x, d3 +y speed, d4 link, d5 y offset, d6 fixedmovey |
| 7 | top enemy | slots 50-74; as 6 |
| 8 / 9 | stars off / on | `starActive` |
| 10 | ground2 enemy | slots 75-99; as 6 |
| 11 | end level | d1 1: at once; else fly-out (section 5) |
| 12 | 4-part enemy | types d1..d1+3 as a 2x2 block of 2x2 sprites (part 1 x+24, 2 y-28, 3 both); layer by d6: 0/1 ground, 2 sky, 3 top, 4 ground2 (d6 then zeroed); d2-d5 as 6 |
| 13 / 14 | random enemies off / on | `enemiesActive` |
| 15 | sky enemy | slots 0-24; as 6 |
| 16 | text window | message d1 (1-9) and voice: 1 enemy approaching from behind, 2 large mass ahead (boss), 3 intercepting enemy aircraft, 4 cleared enemy platforms, 5 approaching enemy platforms, 6 spikes ahead, 7 afterburners, 8 danger, 9 bonus level |
| 17 | ground enemy at bottom | as 6, then ey = 190 + d5 |
| 18 | sky enemy at bottom | as 15, then ey = 190 + d5 |
| 19 | global move | selection by d3: 0 link d4, 1 all ground (25-49), 2 all sky, 3 all top, 99 all, 80-89 link newPL[d3-80] (event 75), other: none. d1 != -99: exc; d2 != -99: eyc; d6 != 0: fixedmovey (-99: 0); d5 > 0: animation frame |
| 20 | global accel | live enemies with link d4 (0 all; d3 80-89: newPL): d1 != -99: excc; d2 != -99: eycc; d5 > 0: frame; d6 > 0: ani = d6, animin = d5, always animate |
| 21 / 22 / 42 | layer 3 order | `background3over` 1 (over the ship) / 0 (default) / 2 (under sky enemies) |
| 23 | top enemy at bottom | as 7, then ey = 180 + d5 |
| 24 | global animate | link d4: animate always; d1 > 0 frame count; d2 > 0 start frame (else 0); d3 1: once, 2: when firing |
| 25 | global armor | link d4 (0 all): armorleft = d1 (galaga mode scaled) |
| 26 | small enemy adjust | d1: shift 1x1 spawns by (-10, -7) |
| 27 | global reverse | link d4 (0 all; d3 80-89 newPL): d1 != -99 exrev, d2 != -99 eyrev, d3 1-16 colour filter |
| 28 / 29 | top enemies under / over | `topEnemyOver` |
| 30 | scroll speed (keep stop) | as 2, but explosions drift with d2 and stopBackgroundNum is kept |
| 31 | fire override | link d4 (99 all): freq[0..2] = d1, d2, d3, fire next tick; launchers: launchfreq = d5 |
| 32 | top enemy at bottom | as 7, then ey = 190 (d5 ignored) |
| 33 | drops | link d4: `enemydie = d1` (made on death). 512/513 not in 2P/arcade; 533: random special weapon chance by lives; 534 arcade/Super Tyrian substitutions |
| 34 | music fade | |
| 35 | song | play song d1 (1-based) |
| 36 | end when clear | section 5 |
| 37 | random enemy frequency | d1 (spawn when rand%100 > d1) |
| 38 | set clock | curLoc = d1; resume at the last event with time <= d1 (it runs again) |
| 39 | change link | link d1 -> d2 |
| 40 | continual damage | enemies with link L-100 also switch to their damaged look when L does (death chains include them anyway) |
| 41 | clear enemies | d1 0: free all slots; else sky slots only (no explosions) |
| 43 | layer 2 order | `background2over` = d1 (0 under ground enemies, 1 default, 2 over all, 3 like 0 but always opaque) |
| 44 | palette filter | on d1 > 0 (2 fades), filter d2, brightness d3, new filter d4, brightness step d5, fade start d6 == 0 |
| 45 | arcade drops | as 33 but only in 2P/arcade (Tyrian3D rogue runs: purple orbs) |
| 46 | difficulty | difficulty += d1 (clamped Easy..10) if d2 0 or 2P/arcade; d3 != 0: collision damage rate |
| 47 | global armor | as 25 without galaga scaling |
| 48 | layer 2 opaque | no blending of layer 2 |
| 49-52 | custom enemy | ground / sky / top / ground2: enemy 0 with sprite d1 from sheet d3, armor d6; d2, d4, d5 as 6 |
| 53 | forced events | d1 != 99: on (the clock runs while the map is stopped); 99: off |
| 54 | jump | curLoc = d1 (u16; -1 = return to returnLoc); returnLoc = old curLoc + 1 |
| 55 | global homing | link d4 (0 all; d3 80-89 newPL): xaccel = d1, yaccel = d2 (-99 keeps) |
| 56 | ground2 at bottom | as 10, then ey = 190 |
| 57 | link-254 jump | target of the jump when a link-254 enemy dies (0: none) |
| 58 | launch type | link d4 (99 all): launchtype = d1 (from ArcTyr, may differ from T2000) |
| 59 / 68 | replace enemy | link d4 (0: every slot, even free ones): new enemy d1 in the same layer at the old position, old one removed (ArcTyr; 68 replaced "random explosions" in T2000) |
| 60 | special flag | link d4: on death set flag d1 (1-10) to (d2 == 1) |
| 61 | skip if flag | if flag d1 == d2: skip d3 events |
| 62 | sound | sample d1 |
| 63 | skip unless 2P | not 2P/arcade: skip d1 events |
| 64 | effect | effect d1 on/off d2, data d3: 1 lava, 2 water (layer 2 x tied to layer 1), 3/4/5 blurs, 6 spotlight, 9 upside down |
| 65 | layer 3 x | d1 == 0: layer 3 (and top enemies) use layer 1's parallax |
| 66 | difficulty skip | if starting difficulty <= d1: skip d2 events (Easy 1, Normal 2, Hard 3, Impossible 4, ...) |
| 67 | level timer | on d1 == 1; d3 x 100 ticks; then jump d2 |
| 69 | invulnerability | ships invulnerable for d1 ticks |
| 70 | jump if links dead | d2 0: if no live enemy with link 1-19, jump d1; else if none with link d2 (and d3, d4 when non-zero) |
| 71 | jump on map position | if 2 x (layer 1 tile index of its pointer) <= d2, jump d1 (map reached that point) |
| 72 | top enemy shift | d1 == 1: top enemies -6 x, +4 y |
| 73 | sky enemies over all | d1 == 1 |
| 74 | bounce box | link d4 (0 all): xmax d1, ymax d2, xmin d5, ymin d6 (-99 keeps): velocity flips at the box |
| 75 | pick a random link | a random live link in d1..d2 with eyc == 0 -> newPL[d3-80]; none: newPL 255 and skip d4 events (the clock jumps to that event's time - 1) |
| 76 | return when clear | when no enemy is on screen: jump to returnLoc |
| 77 | map position | layer 1 pointer = tile d1/2; layer 2 = tile d2/2 (or d1/2 if d2 <= 0); mapY m is 28m - 2 (8174 = start) |
| 78 | galaga fire rate | +1 (max 10) |
| 79 | boss bars | bars for links d1, d2 (0 = none) |
| 80 | skip if 2P | 2P: skip d1 events |
| 81 | layer 2 wrap | wrap at tile d1/2 to tile d2/2 |
| 82 | special weapon | ship gets special d1 |
| 83 | map stop restart | same as 4 |
| 84 | timed battle timer | as 67, timed battle mode only |
| 85 | timed battle drops | as 33, timed battle mode only |
| 99 | random explosions | d1 == 1 |

## 8. Notes for a level generator

1. Layer 1 is the only map tied to the clock: map row at the top edge = 292 - ceil(curLoc/28).
   Use speed changes (2, 3) freely; they do not shift event times against layer 1.
2. Plan a level as at most ~8100 clock pixels (about 3.9 min at speed 1); end with 36 after the
   boss and an 11 before 8148, or stop the map (2 with 0) plus forced events (53) for a boss.
3. Ground objects: d2 = 24c - 30, time = 28(291 - r) - 7 + d5 (exact at speed 1), or the
   originals' - 8. Keep the layer 1 speed such that the clock hits those times (speed 1, or check
   with `tyrevents.py`'s "fires at").
4. Layers 2 and 3 move at their own speeds; give them ratios to layer 1 that do not run them out
   (layer 3 at 3x lasts 5516 clock px), or keep their upper parts empty.
5. One event 5 at time 0 for the enemy sheets of every type used; event 13 at 0 unless
   random enemies are wanted (an empty random list with them on divides by zero).
6. At most 25 live enemies per layer; multi-part enemies share a link number; drops (33) must
   come after the enemies they apply to (same time, later in the file).
7. Every map table entry used needs a shape number 1-600 (section 1); layer 2 index 71 and layer 3
   70/71 are the transparent tiles.
8. Avoid jump targets reached by the timer, return or link-254 jump right after an event that must
   not run twice (section 2), and prefer 54 to 38.

Testing: `TYR3D_LOG_SPAWNS=1` prints every event spawn (position, speeds, backMove, the 3D view's
prediction), `TYR3D_START=<episode>:<section>` starts at a level (`tools/levels.py`).

## Uncertain

* Whether the one-pixel offset of the originals' ground grid is intended; the arithmetic above is
  from the code (events before drawing, enemies drawn then moved).
* Events 58, 59, 68: from ArcTyr, "may not be 100% accurate to Tyrian 2000" (code comments).
* The meaning of explosiontype bit 0 as "ground" (see enemyDat): behaviour as described, the
  naming in the code contradicts itself.
* `background2over` 3 draws layer 2 opaque under the ground enemies and sets the `background2`
  setting to on (1874-1878); no original level was checked for it.
* Event 75's skip sets `curLoc = time of the event d4 ahead - 1` and moves eventLoc d4-1 ahead;
  combined with the switch's `++` it lands on that event, so it runs the next tick (by reading).
