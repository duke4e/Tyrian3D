# Tyrian3D

A 2.5D/3D port of [OpenTyrian2000](https://github.com/KScl/opentyrian2000). The original game
logic runs unchanged. Only the presentation changes: the playfield is drawn under a tilted
perspective camera, and selected sprites are replaced by 3D models.

Rendering uses the BTBH renderer (`external/btbh-renderer`, branch `tyrian3d`), which runs on
SDL3's SDL_GPU: Metal on macOS, Vulkan on Windows and Linux.

## Build (macOS)

```bash
brew install sdl3 assimp cmake
git submodule update --init external/btbh-renderer
```

Shaders are compiled with SDL_shadercross, which is built once from the renderer's submodule:

```bash
cmake -S external/btbh-renderer/external/SDL_shadercross -B build/shadercross -DCMAKE_BUILD_TYPE=Release -DSDLSHADERCROSS_DXC=ON -DSDLSHADERCROSS_VENDORED=ON -DSDLSHADERCROSS_SHARED=OFF -DSDLSHADERCROSS_STATIC=ON -DSDLSHADERCROSS_SPIRVCROSS_SHARED=OFF -DSDLSHADERCROSS_CLI=ON -DSDLSHADERCROSS_CLI_STATIC=OFF -DSDLSHADERCROSS_INSTALL=OFF -DSDLSHADERCROSS_TESTS=OFF -DSPIRV_SKIP_TESTS=ON
```

```bash
cmake --build build/shadercross --target shadercross -j 6
```

Then build the game:

```bash
cmake -S . -B build/game && cmake --build build/game -j 10
```

The game needs the freeware Tyrian 2000 data in `data/tyrian2000`: `tools/fetch_data.sh` downloads it
(and Camanis 2, and with `gbc` the GBC ROM) from the archive of the old Tyrian fan site's downloads page,
https://jkdf2.net/JKBot/JKArchive/JKDF2/JKDF2/Websites/Tyrian/downloads.html, and checks each file.
Everything else the game shows (the HD art, the voices, the remastered sound effects, the default
SoundFont, episode 7's levels) is in the repository.

On a fresh clone `tools/bootstrap.sh` does all of the above: the submodule, shadercross, the data and
the game. `tools/bootstrap.sh --devtools` also brings what the offline tools start from (the ESRGAN
models, the ground logs, the HD tiles' saved upscales, the voices' render cache: `tools/fetch_devtools.sh`,
from the repository's `devtools` release) and sets up their Python (`tools/setup_tools_venv.sh`).

```bash
build/game/tyrian3d
```

To make an app bundle (`build/package/Tyrian3D.app`, with its shaders, models, map sides and
libraries inside):

```bash
tools/package_macos.sh
```

The app looks for the game data in `~/Library/Application Support/Tyrian3D/data` or in a folder
named `data` beside the app (or `open Tyrian3D.app --args -t <folder>`). If it finds none, it asks
for the folder and remembers it (`~/Library/Application Support/Tyrian3D/data_dir.txt`).

## Controls

The original controls are unchanged. These are added:

| Key | Action |
| --- | --- |
| F3 | Switch between the 3D view and the original 2D view |
| F4 | Switch 3D appearances (models, volumetric sprites) on or off; off shows the flat sprites |
| F5 | Reload `assets/models/models.cfg` |
| Page Up / Page Down | Camera tilt |
| Home / End | Field of view |
| Insert / Delete | Height spread between layers |

The camera keys work only while the 3D view is on screen.

The setup menu has a **3D** page: the view (3D or the original 2D screen), objects (3D or flat
sprites), shadows, ambient occlusion (soft shading where things meet and in the hollows), effects (explosion particles, glowing shots, the ship's engine flame, deep space, weather), screen shake (the view shaking at big blasts near the ship and at hits, also in Destruct), a camera preset (Standard,
Steep, Overhead), the mouse, Sidekicks (how the sidekicks that charge up and never run out, the Zica
SuperCharger's kind, fire: Charged, the default, by themselves while the main fire is held, each time
they are fully charged; Rapid, as fast as they can, uncharged; Hold, only on their own key, as in the
original; `sidekick_fire` in `[tyrian3d]`; network games and demos play as the original; the trailing ones, the
companion ships, the Mint-O-Ship and the Tropical Cherry Companion, fly after the ship to their places behind it either
side rather than along its last positions, which zigzagged after the mouse: `mainint.c` `companion_chase`), Specials (Auto, the default: while
fire is held the special weapon, the Flare's kind, fires again whenever it is ready; Click: a press each, as the original;
`special_auto`), and the HUD: Modern (the playfield fills the window; in a 16:9 area
round it, so on ultrawide it stays near the action: shield, armor and power at the bottom right, the
guns' power and the sidekicks' ammunition at the top right, the score with the lives, super bombs
and special weapon (lit while it is ready) at the bottom left, the boss bar and the level timer at the top, all from the
game's state (the game's own drawing of them is left out), each fading to a third while the ship or
dense enemy fire is under it; the level's name as it starts, the game's messages in a pill at the
bottom, "game over" on a plate; under a menu the game shows over the level; two players have a
panel each at the bottom corners: the score, shield and armor, the gun each fires and its power,
player 2's sidekick level and charge (its pips over the ship too), lives and super bombs) or Classic
(the original panel beside the playfield). The **Graphics** page adds the menus:
Modern (the new UI over the 3D view, below) or Classic (the original screens), Screens: Fill (the
game's other 320x200 screens fill the window, cut at its top and bottom in a window wider than 8:5 or at its
sides in a narrower one; on ultrawide its 16:9 middle, a blurred, dimmed copy beyond) or Integer (as Scaling
Mode says, black bars), and the UI Scale (75-150 %). With the modern menus the settings' pages are tabs
across the top of one panel (Graphics, 3D, Sound, Extras: the jukebox and the debug flight; Tab, Shift+Tab,
Page Up/Down or a click switch them, Esc and Done leave the settings). They are kept in the `[tyrian3d]` section of `opentyrian.cfg`; F3 and F4
change the first two as well. In a level, Escape's options are Return to Game, **Graphics**, the two
volumes, the music (SoundFont or AdLib) and its SoundFont, the game speed, the mouse and Quit Level; Graphics is a page
of the 3D page's settings with the menus, screens, UI scale and the original's detail level, each
changed with Left/Right, Enter or a click and taking effect at once, with the modern menus at the
playfield's left and the 3D view bright beside them, so what each change does shows behind it
(`ingame_options_3d` in `mainint.c`; turning the view to 2D and back there shows the 3D view again).

**The modern UI** (Menus: Modern, the 3D view): the title screen, setup and its pages and pickers,
the new game's choices (players, episode, difficulty, timed battle), the store between levels and the
screens over a level, in dark glass panels with brass rims, in Oxanium, at any window size, in a 16:9
area (`src/ui.c`). The store: the ship as a large 3D model on a lit pad at the left (the weapon
simulator in its place for the weapons, the generator and the sidekicks, with the weapon's power,
its costs and the generator's output under it), the page at the right: the parts to upgrade as tabs,
their choices as cards with an icon (the item's own 3D model where it has one, rendered in a three-quarter view
and lit as the pad's ship: the ships, the guns and generators as the pad's mounts, the sidekicks, the specials' power-ups, the
data cube; the shields keep their pictures), short stats against the best on offer (a long list keeps them: its cards
scroll rather than shrink past them, `ui.c` `shop_cards`), the cost or that the
ship has it, the credits and what is left after the change chosen, a note when a purchase is made;
ship specs round the ship; options, load and save, the keyboard, joystick and mouse, the next
level's map, the data cubes and their texts, and the store's questions (quit, save) as dialogs.
Lists scroll. Two players: both ships side by side, what each has under them (the ship, the score,
the gun and its power, lives, the input device). The Super Arcade and Super Tyrian: the mode, the
ship's name, its main and special weapons (the original's help boxes there). Over a level (the scene
blurred under the glass): the in-game options and their graphics
page, the help (F1), pause, the level's results, game over. And the other screens: the high scores
(the boards as tabs, medals, the difficulty played; the name of a new high score typed in a
question with its score), the story texts between levels (reflowed in Oxanium in a glass panel over
their picture, revealed as the original writes them; a warning's panel and the window's edges pulse
red; an episode's end shows its score and the hint), title cards (the next episode, the Super
Arcade's ship and the code to type), load game (the players' pages as tabs), the instructions (the
topics, the pages of help with their titles), the jukebox (the songs as a list, the one playing
large with its controls, the sound effects, over visuals that play with the music: V or the Look
button switches between the Orrery and the Warp, Space hides the panel), the credits rolling in a column, and the rogue run's
screens (its menu with the profile, the unlocks, the act's map with its nodes named and the next
ringed, the cards and the merchants as large cards with their tiers, the messages as cards). The
mouse works on the panels (hover, click, the wheel moves through the items, the pages and the cards
and scrolls a data cube's text), the keys and the joystick as ever; when the joystick was used
last, the key hints show its pad and buttons. The store's next-level map is the UI's own (`ui.c` `shop_map`, from what `game_menu.c` publishes of
`JE_updateNavScreen`'s planets, routes and grid): deep space, a faint brass grid scrolling at half the planets' pace,
the routes' dots (the selected route lit as far as it has come), the planets as 3D spheres turning (below), a pulsing brass ring round the
selected destination and a faint one where the ship is. In the store one click chooses (the original's first
click only selects; `shop_one_click`), but a part's choices, where the first click tries one on the
ship ("BUY" over its cost) and the next buys it, the volumes, the map's planets and the saved games.
Upgrade Ship lists the ship's parts as rows, as the original does (Up and Down go through them; each shows
what the ship has there and its icon, the part's name above it); a part's page is its choices alone, its
name the title. The pointer is a smooth one sized in window points, as Graphics → **Pointer Size** says
(Small 24, Medium 30, Large 36, the default, Huge 44, times the UI Scale; `pointer_size` in `[tyrian3d]`); a level's
crosshair keeps the small size.
The original screens stay for Menus: Classic and the 2D view.

**Playfield** (3D page and the in-game 3D options, from the next level): **Wide** (the default in
3D) plays in all the 3D view shows: the whole width the game draws (game x 0-319 instead of
24-287, the maps held still instead of the horizontal parallax, so the maps' edge columns and
what stands on them can be played) and 64 pixels above the screen, where enemies are made ahead of
their time (as far up as they fly down meanwhile, so from where the original makes them on they
fly as there; those that don't come down start at the playfield's top). The 2D view then shows
the 264 pixels round the ship. **Original** is the game 1:1 (`l3d_field_wide`, `TYR3D_PLAYFIELD`).
Items drift in to where the ship picks them up (within 8 pixels of where it goes, rather than the edges of what
shows, x 1-307, out of its reach), and down into reach from above it; and once a level only waits for the screen to
clear (event 36), an item standing still drifts down past the ship and away (REEF's cube from a courier held its end
for 40 seconds), whatever the playfield (not in network games or demos). A boss gone to wrecks takes its bar down
(they kept it up at their last hit's armour), and a mouse or pad button already held as a story text comes counts
only once let go (firing as the warp orb was picked up skipped VAULT's text at once).
On upside-down levels (LAVA RUN, EYESPY, episode 6's flips) the 3D view turns the playfield half round, seen from
beyond its top looking down it the other way, and turns the controls' left and right with it (`render_gpu.c`
`fit_camera`, `mainint.c` `view_turned`); mirrored top for bottom as the game draws it, the view looked up through
the ground and everything but the models was lit from behind.
What lies outside the playfield shows darkened, dimmed enemies coming or leaving included. The enemies still to come
are shown coming before the game makes them (`tyrian2.c` `draw_coming_enemies`), not those an event 66 skips on the
difficulty played (2026-10-29: shown, episode 7's Normal and Hard enemies came down on Easy and vanished where they'd
have been made, ASTEROID's asteroids and SAVARA's planes; `TYR3D_LOG_SPAWNS` prints where each is first shown).

## Debug flight

Setup → **Debug Flight...** lists every level of the episodes; Enter flies it from its start (the
following levels follow, shops skipped) without losing lives. A line at the top shows the level,
its time and tick, and the speed. While flying:

| Key | Action |
|---|---|
| `-` / `=` | Slower / faster (1/4×, 1/2×, 1×, 2×, 4×, 8×) |
| Backspace | Back 5 seconds (the level restarts and the input so far is played back, quickly and unseen) |
| `` ` `` | Pause / resume (the camera keys work while paused) |
| `.` | One tick on, while paused |
| F12 | Snapshot to `export/feedback/<LEVEL>_e<episode>s<section>_t<tick>_<time>.png` |
| `[` / `]` | Front weapon: the previous / next weapon port (the new ones too) |
| `9` / `0` | Rear weapon: the previous / next weapon port |
| `;` / `'` | Both weapons' power down / up (1-11) |
| `7` / `8` | The next left / right sidekick |

A loadout change also changes the level's start, so a rewind keeps it.

The tick in a snapshot's name finds the moment again: `TYR3D_START=<episode>:<section> TYR3D_DEBUG=1
TYR3D_DEBUG_SEEK=<tick>` starts a debug flight there.

## New content

**Checkpoints.** In a one-player full game the long levels (their events going on past clock 4500: the middle; past
9000: the thirds) have checkpoints: "Checkpoint" shows as one is passed, and the ship lost after it plays the level
again from its start unseen and unwaited, its recorded input played back (the debug flight's recording: the level
launched as its script launched it, without the shop and texts, `tyrian2.c` `launch_again`), to there, so the ship
is where it was with what it had, a moment unhurt, and plays on (`debugmode.c` `checkpoint_restart`). Not in network
games, demos, timed battles, rogue runs, arcade or two-player play.

New items live in the item data's free slots, so the original ones stay as they are: weapons
819-999, weapon ports 48-60, sidekicks 33-37, specials 49-54. `assets/content/items.cfg` lists them
(the format is in `src/content.h`); the game reads it each time it loads the item data
(`content_apply` at the end of `JE_loadItemDat`). `tools/content/make_items.py` writes the file by
rules from the original data (`tools/content/tyrdata.py` reads it), so the rules change, not the file.

| Port / sidekick | Made from | Its 11 levels |
|---|---|---|
| 48 Phoenix Cannon | the Phoenix Device's fireballs | 1-3 fireballs in a fan; a hit bursts into a small blast, then an eight-way burst, at 10-11 the Phoenix's own fireworks |
| 49 Wobble Cannon | the Wobbley's blobs | pairs weaving side to side, 1-3 pairs, damage 1-4 |
| 50 Micro-Missile Swarm | the Mini-Missile | 1-5 tubes, 1-3 missiles a trigger, faster |
| 51 Zica Flamer | the Zica Flamethrower | flames passing through enemies, reaching further, burning harder |
| 52 8-Way Burst (rear) | the 8-Way MicroBomb | bombs in 2-8 directions |
| 53 Mine Layer (rear) | the Post-It Mine | sticky mines drifting slowly ahead, more often, in pairs from 7 |
| 33 Laser Option | Laser power 6 | gun pod |
| 34 Sonic Option | Sonic Wave power 5 | twin pods |
| 35 Lightning Option | Lightning Cannon power 5 | rotary pod |
| 36 Banana Option | Banana Blast power 5 | gun pod |
| 37 Guided Option | Guided Bombs power 4 | orbiting satellite |
| special 49 Nova | (new: stype 19, `varz.c` `nova`) | a shock racing out from the ship (8 pixels a frame for 22 frames) that wipes out the enemy shots it reaches and hits every enemy it reaches once with weapon 885 (a still blast of 40) made on it; ready again 140 frames on; the 3D view draws it as white-violet rings, a flash and sparks (`particles3d.c` `p3d_nova`) |

**Overclock** (`player.h` `weapon_power_max`): in episode 6 and the rogue run, for one player, the guns' power goes on
past 11 to 15 (the store's upgrade arrows, power-ups, the rogue run's upgrades; the costs go on as before: to 12-15, 78, 91, 105 and 120
times the gun's price). Powers 12-15 shoot as 11 does, each step 25 % harder (so through more: a
shot goes on with what an enemy's armour leaves of it) and 10 % quicker to fire again (`shots.c`
`player_shot_overclock`); the HUD and the store show 15 pips there. The original game stays at 11.

No shop sells them yet (that comes with the new episode and the rogue mode); the debug flight's
loadout keys and `TYR3D_WEAPONS` / `TYR3D_SIDEKICKS` fly them. The new sidekicks look as the ones they copy, in 3D too
(`models.cfg` `sidekick 33`-`37`: the Single Shot's, Dual Shot's, Vulcan Shot's, Single Shot's and Satellite Marlo's
models; until 2026-10-29 the Beno's disc of the original's empty slots).

## Rogue mode

Start New Game → **Rogue Run**. A run is three acts of the episodes' own levels (episodes 1, 2-3
and 4-5), each a map with branches: two or three nodes a row, three rows, then a boss. After every
level you take one of three cards: a weapon (front or rear, its power kept), a power level, a
sidekick, a shield or generator (better ones only), a ship, a special weapon, an extra life or
credits; cards are common, rare or epic, rarer later in the run and after harder levels. Elite
nodes fly a level one difficulty higher for a bounty and better cards; merchants sell cards for
credits; the acts are Normal, Hard and Impossible. Dying without an extra life ends the run (an
extra life flies the level again, as it began). Purple orbs are experience in a run (in the full game they slowly power the front gun up). They drop
as in arcade mode: the arcade's drops (event 45 marks enemy groups to leave one when they die) all
leave an orb in a run, its weapons and items being the cards. Every experience level (10, 15,
20... orbs) is an extra card after the level; the HUD shows it as XP. Orbs, the XP bar and the
sidekicks' ammunition are Tyrian purple (#66023c). Runs
earn cores (one a level, two more a boss,
three for winning), which buy unlocks between runs: the new weapons and sidekicks, special weapons,
ships no shop sells, more credits, an extra life or a warmer gun at the start, a fourth card.

The acts, their levels, the items and the unlocks are `assets/content/rogue.cfg` (written by
`tools/content/make_rogue.py` from the game's data; format in `src/rogue.h`). The profile (cores,
unlocks, runs) is `tyrian3d_rogue.cfg` beside `opentyrian.cfg`. A run skips the episode scripts'
shops, story texts and pictures, and never writes the player's save slots.

## Twin-stick

Start New Game → **1 Player Twin-Stick**: one player alone with the two players' linked ship (in a
two-player game the ships join into one when they meet: player 1 flies it, player 2 turns and fires
the Dragonwing's gun). It is a two-player arcade game (the Silver Ship with the Dragonwing behind it,
power-ups instead of the shop, the two-player Game Menu between levels) whose two players are one:

* **Keyboard and mouse**: the arrows (or WASD, unless the keys are bound to something else) fly the
  ship; the mouse aims the turret, which turns to the pointer (a brass crosshair, with a line across
  and one down the playfield through it, fading to its edges, to find it in a busy screen: drawn by
  the 3D view, `aim_line_quads` in `render_gpu.c`; the ship doesn't follow the mouse, whatever the
  mouse setting); the left button, or the fire key, fires the front
  gun and the turret together; the other buttons and keys do what the settings say (the sidekicks,
  super bombs, the rear gun's mode).
* **Controller**: the left stick (or the pad) flies, the right stick aims (let go, the turret keeps
  its way), the right trigger or the fire button fires both guns, the left trigger fires the
  sidekicks. The sticks are read through SDL's gamepad API, so any controller SDL knows as a gamepad
  has them; the buttons are the joystick settings' as ever.
* Whichever was moved last aims: the mouse or the right stick.
* The ship and the turret are always linked (the sidekick buttons don't part them); the turret is
  never hit on its own (only the ship's hits count), armor pick-ups go whole to the ship, and the
  turret goes and comes back with the ship: its lives are the ship's (the front gun's
  power, as in arcade play); the rear power-ups power the turret, the sidekicks are the turret's, as
  player 2's are. The difficulty is as chosen (two players' is a step harder).
* The modern HUD is one player's: the score (both guns' together), lives, super bombs and special
  weapon at the bottom left, shield and armor at the bottom right, the front gun, the turret, its
  charge (the two players' charge gun, which the turret fires) and the sidekicks' ammunition at the
  top right. The store's Game Menu shows the ship and the turret side by side with the score and
  each one's gun, and Fly and Aim in place of the two players' input devices. Pick-up messages are
  one player's. The classic HUD keeps the original's two-player panel.
* A twin-stick game is saved as a two-player game whose input devices are both "any" (0), which is
  how a save, and the arcade's continue after game over, know it again (`twinStickMode`,
  `twin_stick()` in `player.h`; `JE_playerMovement` in `mainint.c`).

## Episode 6

Episode 6, "The Grey Books" (plan: `docs/plans/2026-10-09-epizoda-6.md`), is written in the game's
own formats by `tools/content/episode6/build.py` into `assets/content/episode6` (`tyrian6.lvl`,
`levels6.dat`, `cubetxt6.dat`), at build time when the game's data is there: it is made from that
data, so it isn't in the repository. The game finds those files in the content directory
(`dir_fopen`), lists the episode in the episode menu and plays it like the others; a full game goes on to it after episode 5
(`last_episode()`). At its end the game asks where next (`menus.c` `episode6EndSelect`, one player, with the GBC levels
and Camanis 2 there): the bonus level Camanis 2 and then episode 7 (`custom_then_gbc`), or episode 1 again.

Its levels are generated anew, the original levels only their inspiration
(`tools/content/episode6/generate.py`, run with a Python that has numpy and PIL): the maps from
the tiles of originals of the same look, by a plan of the level's design (`mapsynth.py`: each
tile follows its neighbours as the originals have them, row by row, nothing copied). The looks are the originals'
least used ones (of their maps grouped by the tiles they show, SAVARA's sea has five levels, the asteroids' nine,
DELIANI's three): DIG SITE has SURFACE's desert, REEF CORAL's reef, GREY MOON ASSASSIN's grey rock and ice (without
the brown ground its level starts on, `map_rows`), VAULT BRAINIAC's halls, ROOST GYGES' hive (its walls on layer 3
along a winding channel, `channel`) and CRUSTGATE SIDE EXIT's glowing crust and crags; their ground enemies are those
of the same originals, and their weather, water and gulls go with the look (`assets/models/terrain.cfg`). The events
from the originals' waves placed anew along a difficulty curve, stationary ground enemies on tiles
that suit them, a boss at the end (bosses fought in stages taken whole, their stages' links and jumps with them:
GRAVITRON's DREAD-NOT, DEEP ICE's ASSASSIN; once it is dead, its wrecks are sent down off the screen and its bar
taken down, so the level ends as the screen clears; `compose.py`, `waves.py`; the event rules in
`tools/content/EVENTS.md`, `tools/content/tyrevents.py` prints any level's events). As many enemies as the
episodes before have by then (the originals' median, whole levels, is 28, 38, 41, 34 and 44 enemies per 1000 clock
for episodes 1-5; episode 6's waves are paced for 38 at its first level up to 52 at its last, by their enemies that
can be shot, generate.py `ORDER`, `waves_target`; 37-55 up to the boss after it, from 12-27), at most 9 kinds of
waves a level (they come round again: other episodes' enemies bring their weapons into the item data, whose slots
for them are few, `enemydata.py`) and 3 waves of scenery (SURFACE's rock arches, completed by `waves.arch_parts`).
A boss gets escorts (`compose.escorts`): waves of its own level from round its fight (else the level's own small
ones) every 420 clock while it is fought, six at most, each skipped once it is gone (its last links set flag 10 as
they die, 60; a 61 before each wave's spawns); and none of its parts stands unshootable longer than 350 clock unless
a stage of its pattern comes first (`shorter_invulnerable`: BRAINIAC's brain waited 1000). The originals' cubes made
as enemies (TYRIAN X's boss's) are coins: the episode's cubes are its own. The originals' gimmicks are mixed in per
level (`gimmicks` in the designs, `compose.py`): a boss of another level in the middle (the map
stops, its pattern loops until it is gone: events 2, 53, 54, 70; then its wrecks go down off the screen and its bar
goes), rushes (all layers faster) along the map's most open stretches (`map_gimmicks`: even rows, the fewest
ground enemies; the event clock follows layer 1, so the map's rows give their times),
ambushes from behind with their warning, dark stretches with the ship's spotlight (over the map's darkest stretch:
DEEP ICE's crevasse; or while something is fought: THE CORE's mid-level boss, DELI RUIN's siege, the power cut) and
the screen upside down (effects 6 and 9; turned by a boss, as EYESPY's, after a "Danger" message, and back when it
dies: ROOST's final boss, CRUSTGATE's MINERS), a siege (the map stops, waves come round until the level timer,
67, runs out). `generate.py --events <level>` makes a level's events again on its map, its ground enemies kept
(its terrain is levelled under them). Only three levels have a message before them (VAULT's arrival, MIGRATION, THE CORE), each over the
planet picture (`]P 005[`, as the originals' are). Secrets: in most levels a courier crosses the top of the screen
fast; shot down, it leaves a data cube (shown in the next shop after the stage's own, `]+` and
`]?`), and in GREY MOON a warp orb to the secret bonus level VAULT (`$$`: dying costs nothing).
After THE CORE comes INVADERS, a Space Invaders mini-game in rounds (`minigames.py`) as ALE is
at the end of episode 1, flown as the originals' mini-games are with the Atomic RailGun alone (script `]k[`: the
ship's own weapons, sidekicks and special back before the next shop or level, `tyrian2.c` `kit_restore`); then the last two: STARFALL, the Collector's fleet chased low over Tyrian's farmland
(HARVEST's own maps, so its terrain and plants; `original_maps`), flown on the rail as Star Fox 64 flies (below; script
`]r[`, its 2D level's events unused); and THE HOARD and HOARD II (`make_hoard`), over open space, the Collector's hoard: every boss of the game one after
another as mid-level bosses (`HOARD_BOSSES`: the originals' levels with one, the same boss once, 29 and BRAINIAC),
each with the last of its approach and its own defences and pattern (`compose.midboss_template`'s `trim`: some bring
their level's whole boss stretch), a mechanic with every other one (lights out, upside down, from behind the ship,
from the side, a rush before it), episodes 1-3's bosses in THE HOARD (New Deli's its last), episodes 4-5's in HOARD
II, a siege, then BRAINIAC (two levels: an event's clock it jumps to is a signed 16-bit number, so a level's events
end by 32767; the game's table holds 5000 events, `EVENT_MAXIMUM`, the original's 2500); the sheets change for each
fight (event 5: `build.py` checks each enemy against the sheets loaded where it is made), and the weapons of the
bosses' enemies that find no slot in the item data are episode 5's most like them (`enemydata.nearest_weapon`). ROOST's first courier carries the Nova (special 49: the pickup
of episode 5's 1296 worth 32149, `courier_events` "special:49", slower than the cube couriers). Its shops sell specials too: a shop's 10th list (` Spec` in its `]I` block,
`story.SPECIALS`: the Repulsor and the Attractor first, the Flare, the fields and zones, the Nova and the Dragon
Lightning last) makes the special an 8th part of the ship in the store, "Done" after it (`game_menu.c`
`shop_has_specials`; the specials have no cost of their own: `mainint.c` `special_shop_cost`). MIGRATION and GRAVITRON are seen from the side (Tyrian3D event 200): the
game runs as ever, the 3D view is turned a quarter so the level scrolls from left to right (the
controls turned with it), seen from straight above so the level crosses the window evenly and its
craft show from above as in the other levels (the menus over the level keep it turned), over open
space with the stars in depth and rocks along the window's top and bottom edges
(`layer3d.c` `add_side_decor`); their playfield reaches 250 pixels further ahead (event 200's d3:
enemies are made there, shots and the ship go there), at least 340 (`tyrian2.c` `SIDE_AHEAD`) so
enemies are made past the window's right edge, not in the middle of it; the sidekicks mounted in front follow the
ship there too (they stopped at the screen's top, a third of the way across), and the planet in the deep turns with
the view, its poles up the window as in the other levels. While a boss's bar shows, the view eases back as far as
puts the boss in the window's middle (at most 140 pixels; the game stops one near the screen's top, a quarter of
the way across), the ship kept in view (`l3d_side_shift`, `l3d_ship_top`). The
generated
levels (`levels/*.json`: our maps and events, and references to the original waves and bosses)
are in the repository; `build.py` expands them with the game's data at build time and brings the
enemies of episodes 1-3 they use into episode 6's item data (`enemydata.py`). Map pictures go to
`export/episode6`.

## Episode 7: Tyrian GBC

The levels of Tyrian 2000 for the Game Boy Color (World Tree Games, 2000; never sold, freeware since
2007) as an episode of the PC game, flown with its ships, weapons and enemies (plan:
`docs/plans/2026-10-25-gbc-epizoda.md`). It is made from the GBC ROM, which is not in the repository
(`tools/fetch_data.sh gbc` puts it in `data/gbc/Tyrian.gb`); the levels rebuilt from it are
(`data/gbc/episode7`, `data/gbc/shop.json`), the rest the tools take from it stays out. The tools in
`tools/gbc` (run with the tools' Python, which has numpy, scipy and PIL) read it:

* `extract.py` runs the ROM in the tools' own GBC emulator (`gbemu.c`, a shared library driven from
  Python by `gb.py`: CPU, MBC1, PPU, CGB banks and palettes, HDMA, logs of ROM reads, VRAM and sound
  register writes) through the menus into each of its 24 levels (the level dispatcher, bank 7
  `$4fea`, reads the level from `$d92f`), and writes each level's map (11 blocks of 16x16 a row,
  read upwards from the pointer the level's init routine sets at `$c449`), tiles, palettes, sprites
  and a gallery of what it shows to `data/gbc/levels`; `songs.py` and `apu.py` render its 25 songs
  (played by the ROM's own driver, ticked alone, `$1a5f`) to `data/gbc/music`; `music.py` finds each
  one's loop in its register writes (the shortest period after which every frame's writes repeat to the end
  of the log) and cuts it there, mono, its last 10 ms blended into the 10 ms before the loop's start, into
  `data/gbc/music/loops` with which songs each level plays (its own; its boss song, the one its init starts
  after it); `build.py` copies them beside the episode's files with `music.txt`, and episode 7's levels play
  them in place of the PC songs (`tyrian2.c` `gbc_music`: its own from the start, its boss's from event
  204 at the boss's arrival; `loudness.c` `play_recorded_song`: the WAV converted to the output's rate,
  from the loop's start again at its end, faded out by `fade_song`, ended by `play_song` and `stop_song`;
  the shops and menus keep the PC's songs). Where the music plays through the SoundFont (Sound → Music: MIDI), each
  plays as MIDI instead: `midi.py` reads the notes from the same register writes (the driver writes a note's frequency
  only as it starts it: a trigger is a note on, its frequency the pitch; it ends at the channel's next trigger, its
  length or its envelope running out or its DAC off; the envelope's volume is the velocity, a swell or a slow fade the
  expression), each of a channel's instruments a part of its own with a General MIDI program by its role, from the
  ones the PC songs use most (the wave channel low: synth bass 38; a pulse low: synth bass 39; held or slow: saw lead
  81, square 80 at 50 % duty; short: synth brass 62; swelling: synth strings 50; quiet: polysynth 90; `SONG_PROGRAMS`
  for a song's own), the noise channel's hits drums by their pitch and length (hats, snares, kick); CC 111 marks the
  loop's start; `music_midi.c` `music_midi_song_*` plays the file on the synth the PC's translation uses (a SoundFont
  chosen in the options starts it again on the new one; Music switched between MIDI and AdLib, the other form from its
  start: `loudness.c` `follow_recorded_song`). The level's song no longer comes back over the boss's (`tyrian2.c`
  restarted the PC song whenever the Loudness player stood still, as it always does under a recorded song, so the
  boss songs were never heard, 2026-10-30); `report.py` writes
  the overview the user chose this episode from (`data/gbc/report/index.html`).
* `episode.py` makes each GBC level a PC level of the original level it is a version of (TYRIAN,
  ASTEROID1, SAVARA IV, TORM, STARGATE, CAMANIS, FLEET, BRAINIAC, LAVA EXIT...: the GBC artists drew
  their own, smaller tiles of the same looks, so the tiles are matched by material, not by pixels;
  its enemies are the PC sprites made small). The GBC map is scaled 1.5x (its 176 pixels are the 264
  the PC playfield shows) and cut into the PC tiles' quarters; each quarter's material (the tile
  set's main colours, k-means of the used tiles weighted by how much of the originals they cover, so a
  rare tile can't make a material of its own: CAMANIS's dashed plate took its cobbled plateaus; the GBC
  lightness range moved to the tile set's, the GBC grain blurred) picks a
  tile with those quarters among the originals' ground tiles and their shores' corners and edges (used
  twice or more: they never stand beside themselves, and without them every island was cut off square;
  not the objects standing on the ground, nor
  the tiles `make_cleanground.py` learns as objects' tiles, `learn_object_tiles`: it erases every copy
  of those with a stand-in on it, and GBC DELIANI's pod tile as fill gave 2364; cached in
  `data/gbc/cache/object_tiles.json` while the ground log and `cleanground.json` stay as they were): the
  map is the choice that misses the plan least (a quarter off costs 1, the rarer tiles a little) and
  pairs its tiles as the originals pair them or as their edges join (a pair beside or above each other
  that no original has costs up to 4 by its edge's mismatch: the step in colour across it beyond the
  steps just inside the tiles, 20 Lab costing the most; two grasses join, grass beside the sea doesn't),
  found over the whole map (min-sum belief propagation, 60 rounds) and bettered row by row (Viterbi along
  a row, given the rows below and above it) over a few passes (row by row alone can't change two rows
  together, which a shore needs, and gave the plan up for strips); the log counts the pairs left that no
  original has and those of them badly joined (over 12; 2026-10-29: 175 in the GBC maps' rows, from 3078).
  Space levels are the original's
  blank tile with the stars. Backgrounds 2 and 3 (the GBC has one map) are made anew from the original's
  where it has more on them than one tile's filler or a sign at the start (`upper_layers`; SAVARA takes
  SAVARA V's clouds): TYRIAN's clouds and rock outcrops, SAVARA V's clouds, CAMANIS's and ICE EXIT's ice,
  FLEET's passing ships, BRAINIAC's, NOSE DRIP's and DELIANI's decks, LAVA's rock islands; episode 6's
  synthesiser learns the stretch each fills, as full as the original's (the empty tile weighed until it is
  within a sixth; one that runs into a dead end is made again from another seed, and what it can't continue,
  BRAINIAC's background 3, is the original's as it is, as are FLEET's ships of many tiles: `as_they_are`), its top 12 rows left
  empty (one that runs out repeats its top rows). They scroll at the pace each keeps longest against layer 1
  in its original (TYRIAN 2x and 3x, ICE EXIT 1x, FLEET's ships 5x),
  at most as fast as their 592 rows last until the boss (event 2's d2 and d3 from the GBC script's speed);
  episode 7's explosions drift with layer 1 as they did, not with background 2 as the PC's (`tyrian2.c`
  events 2 and 30). The levels, in the GBC game's Full Game order (found by flying it
  through in the emulator) with its five Arcade-only levels after one of their look, go to
  `data/gbc/episode7` as episode 6's level JSON, with `preview/` pictures (the GBC map beside the
  PC one).
* `enemies.py` flies each GBC level in the emulator on Hard (so every enemy type shows; the ship kept
  alive and never firing, so every enemy lives out its path) and logs its script as it runs; for every spawn it draws the new enemy's
  sprites and gives each GBC enemy type the PC enemy whose sprite looks most like it (silhouette and
  shading against the PC atlases in `upscale/in`, 4-part enemies as 48x56 blocks, at the 1.5x scale;
  the enemies of the original level first; of a type's frames only those of about its main one's
  size and shape, as the frames can catch a neighbour), into `data/gbc/enemies` (`Lnn.json`, and
  `Lnn_matches.png`: each type beside its candidates). The PC enemies made of several are candidates
  too (`composites()`): the original levels spawn their parts together, each at its offset (the long
  rockets, the face with arms, the robots of four, the green bombers, the desert bunkers); a group of
  one enemy (a row of fighters) is not one, and a chain with a run of the same part (a rocket's
  body) also comes with that run of one and of two, as the GBC versions are shorter.
  `enemy_overrides.json` holds the corrections by eye (`"L23:29": [episode, enemy]`,
  `[episode, enemy, 4]` for an event 12 block, `[episode, [[enemy, dx, dy], ...]]` for a composite,
  or `null` to leave the type out; checked over all 24 levels on 2026-10-25); their sprite sheets are
  loaded before the other types' (after the boss's). `review.py` draws the sheets for that check:
  `Lnn_review.png` (one row per look of the level's types, most spawned first: the GBC sprite, the
  PC enemy the level uses, the six best candidates with the sheets each needs, green if loaded;
  composites' parts in `Lnn_review.txt`) and `Lnn_pool.png` (every enemy of the originals the level
  condenses).
* `script.py` turns a GBC script into PC events: the GBC game's script is a port of the PC event
  system with its own numbers (trigger positions in scrolled pixels; records of command, a, b, c,
  group): enemies (03/04, on Hard or Normal only 21-24, blocks 28+) become sky or ground spawns of
  their PC enemies (ground when the originals make that enemy on the ground) with a link per GBC
  group, the group speed (13) event 19, its zig-zag (14: every |c| frames the speed steps by 1,
  turning at the third byte, as the PC's) events 20 and 27, its acceleration (16) event 20, turn
  speeds (15) event 27, a group's new group (0b) event 39, the scroll (02) event 2, the difficulty
  skip (00) event 66. A GBC frame is 0.375 PC ticks and a speed unit 2 PC px a tick (a GBC pixel is
  1.5 PC pixels, its scroll of a pixel every 4 frames the PC's 1 px a tick). A GBC enemy moves as the
  ROM moves it (the spawn `$2ca8`, the mover `$20b8`, command 13 at `$289c`): from its type's start speed
  (the type table's bytes 3 and 4, half pixels a frame; 99 steers it towards the ship), and with the map
  (a pixel each time it scrolls) only when command 03 or an even block command made it (04, odd blocks and
  the Hard and Normal ones, 21-24, whose flag `$26f3` works out as 4 minus the command,
  stay where they are on the screen but for their own speed: about a third of the scripts' spawns); 13 with 99 steers
  that way towards the ship, without it steering stops. So each spawn gets its start speed's y as its own
  (the spawn event's speed, which makes up for the PC enemy's: per enemy, which the 3D view's look ahead
  and forecasts take), its x, the PC enemy's steps and steering undone and the steering towards the ship
  by its link as it is made (a group's older enemies that a 13 sent elsewhere change with it: 64 of the
  4,660 spawns); sky ones the map carries the scroll as fixedmovey (again at each new scroll speed, for links
  made in the last 900 ticks), the others none; ground ones (the ground scrolls them) the GBC doesn't carry
  get the scroll taken off their speeds (the spawn's and their 13s'). The level's type table's place
  comes from its init (`enemies.py --tables`, into `Lnn.json`). `moves.py` checks it: it flies the GBC
  level (the ship parked as `boss_rom.py` parks it) following each enemy from its spawn, reads the PC
  level's from `TYR3D_LOG_MOVES`, and sets each spawn's speeds over its first 15 ticks side by side
  (2026-10-27, TYRIAN, ASTEROID, OASIS, SPACE ATK, DELICORE: 284 of the 293 spawns it could pair move
  within a pixel a tick of the GBC's; the rest the steering towards the ship, whose GBC step, a speed
  unit every 10 frames with no top speed, the PC's 55 only comes near, and a zig-zag's first steps).
  Where the GBC scrolls a pixel every 3 frames the PC map's whole pixel a tick is a quarter slower,
  so carried enemies drift that much slower too. Backgrounds 2 and 3 (empty) scroll with
  layer 1 (at the usual 2x and 3x they run out of map at clock 8274 and 5516, which these levels
  pass). The GBC boss is the script's last stretch (`boss.py`, below); the five levels with none in the GBC
  game (DELICORE, AST.BONUS, LAVA I, BUBBLES, FINALE) get the original level's boss (or a related level's),
  placed as episode 6 places them, with all its sprite sheets, and an event 11 ends the level if it is never
  destroyed (as the originals have one near 8100; after the boss block's last event where that runs longer).
  What the GBC script does past its map's top is pressed into the time before the boss (at most clock 7000).
  Every GBC type is a PC enemy: the best candidate on the level's
  sheets (4-part ones as event 12 blocks, a composite's parts each spawned at its offset, centred on
  the GBC enemy, in its link). A GBC block record is the pieces of one big enemy (seen in the GBC
  game: two columns one robot, a bunker, SAVARA's airship of eight, a stalactite of three; never a
  formation): one PC enemy, centred on its pieces. The GBC game also builds a big ship of several
  types side by side in one group, and each type's look was found for the whole of it: a spawn whose
  place lies inside the sprite of another of the same moment and group is left out (`pieces`, its
  type PIECE), so the ship isn't made two or three times on top of itself (LAVA II's rocks, DELI's
  ships, OASIS's bunkers). `episode.py` names the spawns it leaves out (types never seen
  in the flight, or with no candidate on the level's sheets) and the pieces merged.
* The boss fight of the levels without a GBC boss (`build.py` `boss_fight`, which places the boss itself): the boss is the original
  level's (or a related one's), its block taken from the spawns of its last boss bar's links (from 400
  before the bar: those links make ordinary enemies all through some levels, DELIANI's, LAVA EXIT's,
  and the block ran on for thousands of ticks), with the moves of a layer's or all enemies over it
  (BRAINIAC's hold its brain against the scroll), links of its own (31-40 for the originals' low
  ones: the GBC script's are 1-30) and the original's scroll over it (the blocks leave scroll events
  out; in a GBC level the map still ran there, so bosses flew through the screen and their "end when
  clear", 36, ended the level). Where the original stops its map over the boss, so does the level
  (TORM's boss holds its place against the scroll till then); a boss that holds its place itself (its
  own speed up the screen while the map runs: IXMUCANE's, SAVARA IV's) keeps the original's scroll;
  any other stops the map once its body is on screen (its highest piece's top at y 24, from its
  pieces' spawns and speeds) and its drifting pieces stop (19 by link). Forced events (53) keep the
  clock running for its script; the level ends when it is gone (36, added where its block has none;
  and once its bars' links are empty, checked every 12 ticks with event 70, every enemy taken off, as the
  GBC's levels end once their boss is gone: an end when clear waited for the rest too, and BUBBLES's bubble
  machines on the stopped map never stopped blowing, so a boss killed at once left the level running for
  ever, 2026-10-29), or at its event 11, 2400 to 6000 ticks of fight later (an unkillable boss: as long as its block, the
  final one's phases); the block's map restarts (4, 83) are left out. All 24 bosses checked by eye.
* WARP (STARGATE's look, black, its stars off) is open space with the stars on, as the GBC level is.
* The other game modes (Arcade, two players, timed battle, Super Arcade) find their pickups as the PC
  levels give them, through drop events (33, and 45 for the arcade modes only: what the enemies of a
  link leave when shot down: purple balls, value 30000, power up the guns in Arcade and are cash in the
  full game; 30000 + N and 31000 + N the front and rear guns; 533/534 the front and rear guns' power-ups,
  in Arcade at times a random special): the GBC game has none of its own (its script has no such
  command), so `episode.py` (`with_drops`) gives each level its original's drops in their order and at
  their pace, and as many: a drop reaches every enemy of its link that came in the 120 ticks before it
  (SAVARA V's waves of 17 planes leave 17 purple balls each), so it goes to as many GBC groups as that
  takes, those that come nearest the same share of the way to the boss, after the enemy of the group that
  makes up the number (2026-10-29, the user: the GBC levels' pickups are poor, Arcade above all: given to
  one GBC enemy each, the levels had 419 purple balls where their originals have 1100; now 972, the guns,
  power-ups and specials as the originals'; the rest where a level has too few enemies, WARP's 131). Not
  to the pieces of a GBC boss (links 101 and up) nor to enemies that can't be shot down; JUNGLE II, whose
  boss loop is the whole level, over its groups in the loop. A boss block found at its original's start
  (CAMANIS, LAVA EXIT) doesn't count as where it ends (every drop after it went to the last groups). The
  first level of its pool with drops where the original has none (DESERTRUN); not the originals' data
  cubes (the GBC story's are the episode's) nor their warp orbs (value 10000 + a section: the originals'
  secret levels). Episode 7 is in those modes' episode menus as in the full game's. Checked with
  `TYR3D_MODE=arcade`, `two`, `timed:1` and `super:1` on TYRIAN, JUNGLE and DELI CORE. In episode 7 a gun's
  power-up that finds nothing to power up in its port (no gun there, or one at full power) powers up the
  other port's (`mainint.c` `power_up_port`; the user lost them to the cash prize: the GBC's one list of
  guns often leaves the rear port empty, and the two pills look alike).
* A boss that passes by in its original (its map going on once it is gone: ASTEROID2's tank) stops once
  it is in and fights; one whose pieces are drawn damaged from the start (dani < 0) doesn't count as on
  screen, so it gets no end when clear (its level ends at its 11).
* In the 3D view (`tyrian2.c` `gbc_faces_its_way`) episode 7's sky enemies keep their models' heading
  (down the screen, as the GBC's sprites always face, whichever way they fly) and lean towards where
  they go sideways, at most 40 degrees, easing into it (`gbc_lean_now`; until 2026-10-28 they turned
  round to their way at once, and on the ROM's paths, which go sideways and back up the screen, many
  faced the wrong way); not the pieces of an object of several sprites (models drawn at their origin,
  or other sprites made with it at its side; a boss's pieces even apart), turning items, nor what stands
  on the ground.
* Episode 7 at the GBC's pace (`tyrian2.c` `GBC_PACE`, `nortsong.c` `setTickDelay`): its translation
  makes a GBC frame 0.375 ticks (the GBC map's pixel every 4 frames the PC's pixel a tick), and the GBC
  shows 59.73 frames a second, so its levels' ticks last 8/3 of a GBC frame, 44.6 ms, where the PC's
  Normal is 28.75 (its Slower 43): map, enemies, shots and script as fast as on the GBC; at the PC's
  pace they all went 1.55 times as fast (the user: some enemies too fast and abrupt, the bosses too).
  That played too slow beside the PC episodes (the user, 2026-10-29), so the ticks last 1.25 times the
  PC's (35.9 ms), about halfway. The player's ship and shots go by the same ticks. Menus and the shop keep the PC's pace.
* Episode 7's enemies die alone, as the GBC's do (`gbc_takes_along`): a GBC group is one link, and the
  PC kills a link's enemies together, so shooting one took its group's others with it (they seemed to
  vanish by themselves). Only the pieces of one GBC enemy go together: a composite's parts (the events
  after an event 201, Tyrian3D's, which names how many: `script.py` `OBJECT`) and an event 12's four
  (`gbc_object`, tagged as an event makes them), and whole: when one of them is shot down or turns to its wreck, so do
  all of its picture, their link and damage level or not, with the pieces made with it that stand next to it and show
  another sprite (JUNGLE's walls of three, DELICORE's machines, made by events of their own), and theirs in turn
  (`gbc_mark_picture`; the 3D models lost a piece at a time, as tiles).
* Episode 7's enemies are as tough as the GBC's and fire as often (`tyrian2.c` `gbc_fight`, event 203,
  Tyrian3D's, before the event that makes one: `script.py` `FIGHT`, `boss.py` for a boss's pieces): the PC
  enemy drawn for a GBC one is often far tougher (a big ship for a small GBC enemy, a wall that can't be shot
  for one that can: DELICORE's) and fires far more (BUBBLES' bubbles a stream a tick, where the GBC's never
  fire). Its hit points are the GBC type's (Normal: the type table's byte 1), on the GBC's difficulty scale
  (Easy half, Hard 1.5x), shared among an object's PC parts by their armour; it fires one gun, as a GBC
  enemy has (`gbc_fire`: the first of its PC guns that fires by itself, or its first), at the type's pace
  (bytes 5 and 6), none where it has none, and a group given a gun (command 0e) gets an event 31 (d6 1: the
  same, its launches as they are). Its enemies' shots hurt as the GBC's do on its difficulty, a point less on
  Easy and one more on Hard (a gun's damage + the difficulty - 1, `$054d`), at least one. Where a level still
  costs the ship well over its PC original, its enemies fire less often (`episode.py` `FIRE_PACE`: SAVARA's
  boss aims 6-point shots every 2 ticks from two pieces, 4 times slower; JUNGLE, DESERT, AST.BONUS, SPACE
  ATK). Measured with `TYR3D_LOG_BALANCE` (each level and its original on Easy in Arcade, the autopilot
  firing in god mode: damage at the ship a 1000 ticks, which enemy dealt it, by shot or collision). (2026-10-29,
  the user: Easy is quite hard; take the ratios of the PC originals the GBC levels were made from.)
* `story.py` flies the GBC Full Game through (each level ended at once) and logs the story texts
  (plain ASCII in the ROM: `/` a new line, `|` a new page) and the speaker names it reads, in order,
  into `data/gbc/story.json`: Transon's greeting and Trent's escape before the first shop, one text
  after each level (News, Javi, Reid, Vykromod, the captain...), the ending.
* `tools/content/gbc/build.py` (standard library; run by the build when `data/gbc/episode7` is
  there; when the item data has no free gun slot left for a brought-in enemy, its gun is episode
  5's of that number) makes the story the episode's data cubes (each shop holds what the GBC game tells after the
  level before it; the GBC capitals in sentence case, the names marked; the speaker's PC portrait:
  Transon, Reid, Vykromod, the captain, the news...) and the GBC ending its ending, expands the bosses (episode 6's `compose.expand`) and brings the enemies into the episode's
  item data (`enemydata.py`) and writes `assets/content/episode7`: `tyrian7.lvl`, `levels7.dat` (a shop before every level:
  the GBC shop's offer before that level, the planet map pointing at the original level's planet; the
  original level's song) and `cubetxt7.dat`.
* `shop.py` reads what the GBC shop offers before each level of the Full Game into `data/gbc/shop.json`:
  its Items menu has six lists (Ship, Weapon, Engine, Shield, SideA, SideB), each showing the items
  unlocked by name from the ROM's tables of 8-character names; the game is flown through as `story.py`
  flies it and at every shop each list is opened (and scrolled) and the names it reads (the ROM's read
  flags) are its offer. The offers change from shop to shop (before SAVARA: Talon and Storm; Pulse,
  Multi and Scatter; the Std and Micro engines; the Low and Hard shields...). `build.py` (`gbc_shop`)
  puts them in an original's shop block as the PC's items: ships by name (Micros the Stalker, Phoenx the
  Phoenix), the one GBC weapon slot as the front gun (the nearest front gun by name and look: Scatter the
  Mega Pulse, Sonic the Sonic Impulse, Rail the Widget Beam, L.Ball the RetroBall, Arrow the Missile
  Launcher...), the engines as generators, the shields by strength, the sidekicks on both sides (the PC
  has no shield, repair, magnet or cold sidekick: the nearest in use), and after them that original
  block's own of each kind, at most 6 a list (`SHOP_MAX`; the GBC's lists are as short as the PC's, 3 to 5,
  but draw from the same few each time, and the user found the offer thin and much the same: the original's
  at that point of the episode brings the PC's progression); the rear guns and armour stay the
  originals' shops' (from episode 1's first to episode 4's, spread over the episode). The Arcade-only
  levels and FINALE take the offer before them.
* `bosses.py`: each level is flown from its script's end and the boss's look taken (the largest cluster of
  sprites on screen, `data/gbc/bosses/Lnn_boss.png`, with the screens) beside the PC bosses' bodies (every
  original level's). They are mostly the PC's made small, often another level's: TYRIAN's is ASSASSIN's,
  ASTEROID's and OASIS's ASTEROID2's tank, SPACE's ICE EXIT's claws, SAVARA's SAVARA V's airship, SAVARA
  II's SAVARA's red fortress, ASTEROID2's ASTEROID1's dome, ICE EXIT's and DELI CORE's DREAD-NOT's skull,
  DELIANI's DELIANI's claw ship (`episode.py` LEVELS boss=, picked by eye; JUNGLE's and JUNGLE II's TORM,
  CAMANIS's, FLEET's, TUNNEL's IXMUCANE, LAVA II's CORE and DESERT's SURFACE are their originals').
* The GBC bosses' behaviour (`boss_rom.py`, `boss.py`; the user: translate their movement and attacks from
  the ROM as faithfully as possible). A GBC boss is no code of its own: it is enemies of the level's type
  table spawned by the script and steered by it as the other enemies are, the script's last stretch run as a
  loop. Its interpreter (bank 0 `$2741`-`$2828`, the per-enemy update `$1160`-`$12e3`, the fire routine `$054d`,
  the spawn `$2ca8`) gives the commands: 02's third byte stops the map while the clock runs on (from the boss
  on); 06 sets the clock back (the loop: the records from its position run again); 05 (end, ., ., group) ends
  the level once no enemy of the group is left (255: none at all), every enemy taken off first (`$2b79`,
  `$0a9d`); 0e (gun, frames, filter, group) sets a group's gun and how often it fires (ff: those whose gun is
  the filter); 0a a group's hit points; 1d its speed and fire interval; 13 with 99 steers towards the ship (a
  step every 10 frames). The level's tables (pointers set by its init): types at `$c453`, 10 bytes (hit points
  for Normal, Easy half, Hard 1.5x, 255 can't be hurt, 0 dies at the first hit; start speed, 99 towards the
  ship; gun; interval; sprite tile), guns at `$c451`, 7 bytes from gun 1 (sprite, damage plus the difficulty
  minus 1, 99 when the next gun fires with it, speed in pixels a frame or 99 aimed at 3 pixels a frame along x
  and y together, where from); guns 20 and up launch an enemy of type gun - 20. At most 10 enemy shots fly
  at once and 17 enemies live (its tables at `$c37f`, `$c192`; WARP's and ASTEROID2's bosses launch at the
  17, OASIS's tank fires a shot a frame into the 10): in episode 7 a GBC boss's piece fires only while fewer
  than 10 enemy shots fly, and a launch waits for fewer than 17 enemies (`tyrian2.c` `gbc_shots_full`,
  `gbc_enemies_full`; WARP's orbs filled the screen). GBC enemies move on the screen by their own speeds (half pixels a frame), and with the map only those
  command 03 or an even block command makes (`$2ca8`'s flag, `$20b8`); they leave when off it (x from -36 to
  190, y from -36 to 160). `boss_rom.py` reads all that for each level whose
  script ends in a loop (19 of them) into `data/gbc/bosses/rom.json`: the stretch, the loop, the end, the
  boss's groups (the one its end waits for and those spawned with it, or right after it: TYRIAN's claws,
  DESERT's turrets, JUNGLE II's body after its head), their types and guns, and a flight from the boss on
  (Normal, the ship kept in a corner, never firing: each group's place every 4 frames, the shots fired, the
  loops; the enemies the pieces launch, matched to PC enemies by look as `enemies.py` does).
  `boss.py` makes the stretch PC events (`script.Translator`, the main script's) and what only the boss does:
  each piece one PC enemy of its own (a block's 16-px pieces each; episode 7's record, `build.py`
  `boss_enemy`) at the GBC piece's place, drawn as the PC boss's part nearest that place in its body (both
  boxes 0-1; `boss_overrides.json` by eye, `boss_review.py` draws `Lnn_pieces.png` to check); in the 3D view
  (since 2026-10-28) a group of 4 pieces or more draws the PC boss's whole body instead, centred on the group,
  each part drawn by the piece nearest it (`boss.py` `wholes`, events 202 right before the piece's spawn,
  `tyrian2.c` `gbc_look`: a piece a part left gaps, TYRIAN showed 9 of ASSASSIN's 12, and a piece of a cut
  body flying apart looked like a broken one), a piece with none drawing nothing while its group's others
  draw theirs; smaller groups (TYRIAN's claws, SAVARA II's side pods, FLEET's hanging plates) as
  `boss_looks.json` has them, by eye (parts of the PC boss that look whole on their own; WARP's bubbles, for
  which ASSASSIN is too big, STARGATE's big orb); in the sky
  (the PC parts that stand on the ground in their originals too; one drawn damaged from the start, dani < 0,
  loses that flag, which in the PC keeps it from firing: ASTEROID2's tank, ASTEROID's and OASIS's boss, was
  silent), drifting with the map as the GBC's does,
  with the GBC piece's hit
  points as its armour (1:1: the PC's and the GBC's first guns do 2 a shot), its start speed, its guns
  (each GBC gun with the ones chained to it one PC weapon, `build.py` `gbc_weapon`: the shots' speeds 4x, at
  most 18 px a tick, faster ones would pass by the ship between ticks; aimed ones at the PC's aim 9; the
  same damage; from where the GBC's come), what it launches, the PC part's worth; 0e and 1d's interval event
  31 (a link's three guns' frequencies: a group's three most used guns), 0a event 25, homing event 55, 02's
  stop the map stopped (2), forced events (53) and every enemy's drift stopped (19), the loop event 54 back
  to its first event (when it starts before the map stops, a copy of it after the first time, timed as the
  stopped map's; its clock from the last record before it at the rate then, as the stopped map's rate can
  change after the stop: DELIANI's loop ran its speed record again each time round and drifted off the
  screen; the jump after whatever else falls on its tick: a speed rounded onto it was lost, ICE EXIT's boss
  went 104 px a loop), the end event 70 every 6 ticks (a jump to the end once the group's link is empty; 255: the
  boss's links) where every enemy is taken off (41) and the level ends (11). The clock: a position 1.5 ticks
  while the map moves, (b + 1) x 0.375 after a 02 that stops it (a step every b + 1 frames). A group's
  pieces share a link of 101-120: in the PC an enemy shot down or rammed takes every enemy of its link with
  it, the GBC's pieces go one by one, each with its own hit points, so in episode 7 a piece on those links
  goes alone (`tyrian2.c` `gbc_piece_link`, also in `mainint.c`'s ramming; nor does it turn the others
  damaged); the link still moves them all and the end waits for it. They are one body, though, as a PC boss is
  (the user, 2026-10-29: each piece had a whole PC boss's hit points, and every one had to go): the GBC hit
  points of those that can be shot go into one pool as they are made, the pool their sum over the root of
  their number (TYRIAN's nine of 50-100, 780: 260), every hit on a piece, shot or rammed, comes off it, and
  when it is gone all the pieces die together, the unshootable ones too; the boss bar shows it
  (`tyrian2.c` `gbc_pool_join`, `gbc_pool_hit`, `gbc_pool_takes`, `draw_boss_bar`). Pieces that can't be hurt in the group
  the end waits for (CAMANIS's middle one: the GBC level can never end) get a link of their own that does
  what the group does, the end not waiting for them. A group's speeds are the GBC's own (`gbc_speeds`, as its
  mover changes them, `$2109`: every |c| frames a step of a unit, the counter starting at |c|, a negative c's
  at |c| - 1, the turn at a bound that isn't 0, speeds bytes that wrap; checked frame by frame against the
  emulator), each change an event 19 at its time: the PC's own steps (20) are half a unit at whole ticks, and
  the zig-zags came out off (SAVARA's boss went 104 px a loop). The PC's whole ticks and the GBC's half pixels
  (odd speeds move a pixel on alternate frames) still part the ways a little, and a loop repeats that
  (TYRIAN's boss rose 18 px a loop, out of the screen): each group's way over its first pass and over a loop
  is simulated as the engine moves enemies (its clock at the map's speed, a tick a tick when forced) and
  made the GBC's (the flight's, frame by frame: each loop's way) by a nudge while its speed is steady
  (`corrections`). So each boss goes as the GBC's does, the GBC's own slow drifts too (DESERT's right turret
  rises 16 GBC px a loop, TUNNEL's boss sinks 6-7). Groups steered towards the ship, or whose steps go on
  through the loops (ASTEROID's, OASIS's, WARP's, DELIANI's zig-zags between bounds), keep the PC's own steps
  (20, 27); but where the loop runs again from before their spawn (JUNGLE II's: the whole level) they keep the
  GBC's, carried on through the replay, its records steering them as the GBC's do (the PC's steps, without
  the GBC's bounds, took the boss off the screen in seconds): after about 560 ticks its boss flies off and
  the GBC's level ends (the flight: 71 frames into the replay), so the replay is cut 100 ticks after that,
  where the level ends. The other enemies of the boss's stretch (its waves) are made as the main script makes
  them (at their types' start speeds, with the map only those 03 or an even block command makes). The levels
  with no GBC boss keep
  the original's (`boss_fight`, above). The free weapon numbers are few (enemies name their guns by a byte),
  so the GBC guns are made first and the same gun of two levels is one weapon, and a brought-in enemy's gun
  it never fires (frequency 0) stays episode 5's of its number unless an event 31 of its level may turn it
  on.

Its 3D view's assets are made as episode 6's (`tools/content/gbc/terrain.py`, with the game built):
each level's maps are exported and their side columns written, the export marked episode 7 (several
GBC levels have an original's name, and `make_cleanground.py` takes their maps, like episode 6's, as
not teaching the tilesets), each ground map gets its original's terrain settings in
`tools/terrain/levels.json` (marked `"episode": 7`) with its surfaces' heights carried over by colour
(the original map's classes, each one's mean colour with its height, as make_terrain.py's
`"materials"`), then the ground enemies are logged and the clean ground, terrain and vegetation are
built into `assets/terrain`; backgrounds 2 and 3 get their original's settings (solids where its are:
TYRIAN's rocks, BRAINIAC's decks, NOSE DRIP's rock, LAVA's islands). Maps an original has too (open space
of one tile) stay the original's.
`tools/levels.py` lists episode 7's sections.

The game finds those files in the content directory as it finds episode 6's (`src/file.c`) and lists
"Episode 7: Tyrian GBC" in the episode menu when they are there. It is played on its own: a full
game doesn't go on to it after episode 6 (`last_episode`), and its end goes back to the title screen
without a high score (the save file's tables are episodes 1-6's). Its level file has 49 entries (24
levels and the item data): the table of a level file's entries holds 100 now (`lvllib.h`; it held
42, and a longer file overran it). A background whose pointer runs past its map's top (a long level
at the layer's speed) draws nothing there (`backgrnd.c`) rather than reading outside the map. `TYR3D_START=7:<section>` starts
one of its levels (the levels are the even sections, 2-48). Stages 1-5 of the plan: the maps, shops,
songs, enemies, bosses, story and the 3D terrain, and the enemies checked by eye; the GBC's own bosses'
behaviour translated from the ROM (2026-10-27).

The GBC's big ships are mostly the PC's made smaller: SAVARA II's red bomber is SAVARA's of seven parts
(1:302-308), the DELI levels' red claws DELIANI's claw ship of twelve (1:400-411; the GBC makes it of two
types side by side, the second left out), both given by the overrides as composites; a composite is
centred on the GBC enemy (its sprite, or a block's pieces: script.py `sizes`). What no PC level has is
episode 7's own (`tools/content/gbc/new_enemies.json`): so far ASTEROID2's derrick, a mining rig on four
legs with a wrecking ball hanging from its beam (`["gbc", "derrick"]` in the overrides). Its model is
built like the PC enemies' (`tools/blender/models/enemies/gbc_derrick.py`: whole, leaned back as the
levels' tall ground objects, cut into the four pieces of a 4-part ground enemy) and its sprites are
drawn from it: the model's top view (`--sprite`) in the levels' palette, cut into the 2x2 sprites
(`tools/content/gbc/sheet.py`, PIL) of a sheet of its own, W (`newshw.shp`, with `sheet_w.png` to look
at; the game's compressed sprite format, checked against the game's sheets both ways), which the
build copies into `assets/content/episode7`. The game takes it as the 37th sheet (`shapeFile`,
`lvlmast.c`; `src/file.c` finds it in episode 7's content); the enemy's records are its base's (its
guns, its explosion) with those sprites, its armour and value (`build.py` `new_enemy`).

## Custom episodes

Episodes the community made in the game's own formats play beside the game's, without replacing
any of its files (`src/episodes.h`). Each is a folder of `data/custom` (`TYR3D_CUSTOM_DIR`; for the
app, `custom` in the game data's folder) holding the episode's files under the names they have for
the episode N they were made as: `levels<N>.dat` (the script: shops, levels, texts) and
`tyrian<N>.lvl` (the maps, their events and, for episodes 4 and up, the item data with the enemies),
optionally `cubetxt<N>.dat`, in small letters or capitals; `name.txt` (one line) is the name the
menus show, else the folder's. Start New Game's episode menu lists them after the game's episodes
("Custom: <name>"; not in a network game), and so does the debug flight. One is played as episode N
with every file of its folder standing in for the data's of that name (`dir_fopen`; the shapes,
music and pictures it doesn't have are the game's). It isn't saved (Save Game in its shop does
nothing: a save would load as the original episode N), has no high score (the board would be
episode N's) and its end (`]Q`) goes back to the title screen. `TYR3D_START=<folder>:<section>`
starts one in a test run, and `tools/levels.py` lists their sections that way, so the tools that go
through every level (`each_level.sh`, `ground_log.sh`, `review.sh`) take them too.

**Camanis 2** (`data/custom/camanis2`, from `LEVELS4.DAT` and `TYRIAN4.LVL` made for episode 4 by
Kenneth Frank Henderson Jr., 2005; `tools/fetch_data.sh camanis2`): a shop (`Camanis 2 Buy/Sell`), one level, the end. The level is on CAMANIS's ice tileset
(`shapesw.dat`, a third of its ground rows are CAMANIS's) with backgrounds 2 and 3 empty; its item
data is episode 4's with 190 enemies changed, most of them episode 1-3 enemies (CAMANIS's and
IXMUCANE's) copied into episode 4's slots, and a boss of four `b` sheet pieces (link 254) that is
hit only from clock 8300 (armour 254) and whose death (event 57) ends the level. Its 3D view: the
missing HD tiles of tileset W (`tools/tiles_hd.py --add`: shapes 248-250, 259, 260, 270), terrain
`3bf11c7517b5e2ad` (the rocky snow plateaus +18 as CAMANIS's, the rest `~` over the ice at 0),
clean ground and stand-ins (all 11 looks have CAMANIS's wreck models), its side columns. Of the 63
enemy looks it shows, one has no model and shows with volume: the ground gun turret that opens the
level (enemy 267, sheet `2` sprites 41, 131, 43, 93 turning; no original level has it).

## Destruct

Tyrian's secret minigame (`src/destruct.c`): an artillery duel of two armies (tanks, nuke and dirt
launchers, magnets, lasers, jumpers, helicopters, satellites) on a field of dirt that every shot digs
into, in five battles (5-Card War, Traditional, Heli Assault, Heli Defense, Outgunned; Custom from
`[destruct custom]` in `opentyrian.cfg`). Its logic is the original's (there is no wind).

It is reached as in the original: **DESTRUCT** typed at the title screen. Once it has been played
(`discovered` in `opentyrian.cfg`'s `[destruct]`), the title's menu offers it too, between Setup and
Demo (`destruct_discovered`, `titleScreen`).

With the modern UI its screens are panels over its field (`UI_SCREEN_DESTRUCT`, `UIDestruct` in
`ui.h`, published by `destruct.c` as it draws them): the intro as a card, the battles as a list with
what each side has (the mouse picks one), the help (F1) as both sides' keys as configured, the pause.
The keys: the left side X/Shift fire, C/V angle, A/Z power, Space/Ctrl weapon, Alt next unit; the
right side Enter/Insert, Left/Right, Up/Down, PgUp/PgDn, \ or Num 5; F10 and F11 hand the left and
the right side to the computer or back, Backspace makes a new field, P pauses, Esc goes back to the
battles. Test runs reach it with `TYR3D_TEST_KEYS=60:Space,4000:TypeDESTRUCT,3000:Space,2500:Return`
(the intro's logos skipped, the code typed, the intro passed, the first battle); F11 then hands the
right side to the computer, so the battle plays itself.

In the 3D view (with the modern UI) the battle is a diorama (`src/destruct3d.c`, drawn by
`present_destruct` in `render_gpu.c` while Destruct's screen is published): the field is the cut face
of a ridge seen a little from above, the game's plane (where the units stand and the shots fly) 4
pixels behind the face. The game's 320x200 picture of dirt stays the truth: the ridge is a density
field over its columns, rows and 14 slices 2 pixels apart, made into meshes by surface nets in chunks
of 16 columns, each made again when the dirt under it changes. Where the game digs dirt away the face
is dug back into the ridge in a bowl as deep as the hole is wide (each dug pixel's distance to the
dirt left, smoothed), so the explosions' holes are craters; the field's pixels on fire (the
explosions' 241-255) glow in the game's plane, and each explosion lights what is round it. The faces
show the earth in layers, darker down and back in the bowls, what faces up dry topsoil. Behind the
ridge the land falls away (the faster, the higher the ridge stands there) to rolling hills fading into
the dark; beside the field it goes on from its edges; a starry sky with faint nebulae and a red planet
lit by the sun. The units and the walls are models (`tools/blender/models/destruct/destruct.py`,
`assets/models/destruct`, models.cfg's `destruct_*` lines): for each side in its colours (the left
brass, the right green) a tank, a nuke launcher, a dirt launcher, a magnet, a laser, a jumper, a
helicopter and a satellite, a quarter larger than the game's sprites about their feet, the right side's
mirrored to face the left; their barrel, rail, tube or emitter (a model of its own) turned by the
unit's angle, a helicopter's rotor turning and the helicopter facing the way it flies, its nose dipping
as it speeds up; the walls blocks of blue stone. (A unit without a model shows as the game's sprite
with volume.) The crosshairs are gold rings. The effects (`destruct3d.c`, its own random numbers, never
the game's): an explosion flashes, burns in billowing fire, throws sparks, smoke that rises and, in the
dirt, clods that fall and stay where they land; a large one sends a shock wave and shakes the camera; a
dirt shot's burst throws clods and dust; each shot leaves a trail (sparks, a lasers' blue streak, the
big shells' smoke, dust) and a flash and a puff at the muzzle as it leaves; a magnet pushing sends
blue rings from its poles; a unit badly damaged smokes, one destroyed smokes where it stood for five
seconds; the field's pixels on fire spread a little over their neighbours, embers rather than squares. The modern HUD: each side's panel at the top (who plays it, its points, the unit chosen and how
many stand, the weapon with its icon, the barrel's angle on a dial, the power and the armor), the
battle and the score between them, the round's winner, the keys at the bottom. The camera fits the
field to the window's width and height (on wide windows the land beside it shows). `TYR3D_PROFILE=1`
prints the frames a second and what a frame and the ridge's meshes take.

A wall placed at the field's right edge (x 309 or more) made the original read and write past its
320 columns of heights, into the screen pointer after them, and the next field's terrain was drawn
from there: a crash. Placement now stops at the field's last column (`JE_placementPosition`).

## Environment variables

| Variable | Meaning |
| --- | --- |
| `TYR3D_2D=1` | Start in the original 2D view |
| `TYR3D_NO_MODELS=1` | Start with flat sprites (as after F4) |
| `TYR3D_MODEL_CONFIG` | Appearance file in `assets/models` (default `models.cfg`; `models_kenney.cfg` has the PoC 2 models) |
| `TYR3D_TILT`, `TYR3D_FOV`, `TYR3D_HEIGHT_SCALE` | Initial camera (defaults 20, 30, 1) |
| `TYR3D_GPU_BACKEND=vulkan` | Use Vulkan instead of Metal (macOS needs MoltenVK) |
| `TYR3D_DEMO_IDLE_MS` | Title-screen idle time before the demo starts (default 30000) |
| `TYR3D_DUMP_DIR`, `TYR3D_DUMP_EVERY`, `TYR3D_EXIT_AFTER`, `TYR3D_DUMP_LAYERS` | Frame dumps for automated checks (see `tools/capture_run.sh`) |
| `TYR3D_LOG_ENEMIES=1` | Print each enemy type on screen with its sprite sheet and index, for `models.cfg` (and, with frame dumps, which dump is which 3D frame) |
| `TYR3D_PROFILE=1` | Print the cost of 3D presentation, and of presenting the game's other screens (menus, the store, the screens over a level); `TYR3D_PROFILE=gpu` also the GPU's time for each 3D frame (`3d gpu:` median, mean and most of the last 300, from its submission to its completion, each frame waited for first, which slows the game a little) and for each frame the modern UI draws (`ui gpu:`: the store with its pad's or simulator's scene, Destruct, the jukebox, the menus). For A/B costs: a debug flight paused on one frame (`TYR3D_DEBUG=1 TYR3D_DEBUG_SEEK=<tick>`, `` TYR3D_TEST_KEYS=90:` ``) presents the same scene again and again |
| `TYR3D_START=<episode>:<section>` | Start a game at a level section, skipping the menus (see `tools/levels.py`); `<custom episode folder>:<section>` starts a custom episode's |
| `TYR3D_AUTOPILOT=1`, `TYR3D_GODMODE=1` | The ship weaves and fires by itself; the player takes no damage (`TYR3D_GODMODE_UNTIL=<clock>`: until the level's clock is there, to test a checkpoint) (`TYR3D_AUTOPILOT=nofire`: it never fires, so enemies live to be looked at; `park`: held in the bottom left corner, never firing, as `tools/gbc/boss_rom.py` flies the GBC's bosses, out of the way of what sweeps the screen). With `TYR3D_START` the autopilot steers in place of constant play's drift and held buttons (until 2026-10-25 the drift cancelled its steering and held the ship at the left edge, x 23, and fired with `nofire` too: ground logs, reviews and sweeps made with the autopilot before then flew there, so `tools/terrain/ground_log.sh` may log more after) |
| `TYR3D_SEED=<n>` | With `TYR3D_START`: the game's random seed (default 1; runs with the autopilot repeat frame for frame) |
| `TYR3D_MUSIC=midi\|opl` | The music through the SoundFont as MIDI, or on the emulated AdLib chip (default: the setting, Sound → Music). The player's chip writes become MIDI as they come (`music_midi.c`): a note while its channel's key is on, its loudness from the chip's total level, key scale level and envelope (the decay to the sustain level and, with a decaying envelope, on to silence while the key is held: a note that fades out on the chip ends there); instruments whose MIDI program is 128 and up are drums, the General MIDI drum note (program - 128) on the drum channel (Loudness's MIDI drums: hi-hats, snares, bass drums, cymbals) |
| `TYR3D_DEBUG_MIDI=1` | Print each MIDI note as it starts with the chip's registers for it (level, envelope) |
| `TYR3D_JUKEBOX=<song>` | Open the jukebox at once (no intro, no title screen), playing that song (1-41) first; for its visuals' test runs |
| `TYR3D_CREDITS=1` | Roll the credits at once (no intro), then the title screen; for their test runs |
| `TYR3D_JUKEBOX_LOOK=<n>` | The jukebox's visuals' look for the run: 0 Orrery, 1 Warp (default: the setting, V in the jukebox) |
| `TYR3D_LOG_MUSICVIZ=1` | Print what the jukebox's visuals measure of the music every half second: loudness, lows, mids, highs, onsets, beats, each chip channel's note (+ sounding, level, pitch, notes started, d a drum), the drums' hits, the spectrum |
| `TYR3D_VOICES=0\|1` | The data cubes and story texts read aloud, off or on, for the run (default: the setting, Sound → Voices) |
| `TYR3D_VOICES_DIR=<dir>` | Where the voices are: `manifest.txt`, `e<episode>/<cube>.wav`, `story/e<episode>_<n>.wav` (default `data/voices`; see Voices) |
| `TYR3D_DEBUG_VOICES=1` | Print each voice event: the manifest read, a voice played (its file, length and load time), stopped or ended, a text without a voice or whose text differs from its voice's |
| `TYR3D_SOUNDFONT=<file>` | Another SoundFont for the music (for the run; the menus' SoundFont choice, Sound → SoundFont or the in-game options, picks among the `.sf2` files in `data/soundfonts`, kept as `soundfont` in `[tyrian3d]`) |
| `TYR3D_RECORD_AUDIO=<file>` | Write the game's sound output as raw 16-bit mono samples at 44.1 kHz |
| `TYR3D_EXPORT_SFX=<dir>` | Write the sound effects and voices as WAV files (`<number>_<title>.wav`, 11025 Hz) |
| `TYR3D_ORIGINAL_SFX=1` | Ignore replacement sounds in the data's `sfx` directory |
| `TYR3D_CONTENT_DIR=<dir>` | Where `items.cfg` and `rogue.cfg` are (default `assets/content`) |
| `TYR3D_CUSTOM_DIR=<dir>` | Where the custom episodes' folders are (default `data/custom`; see Custom episodes) |
| `TYR3D_ROGUE=<seed>`, `TYR3D_ROGUE=menu` | A rogue run at once with that seed, or the rogue screen; the profile isn't saved |
| `TYR3D_ROGUE_AUTO=1` | In a rogue run the screens choose by themselves (whole runs with the autopilot) |
| `TYR3D_ROGUE_UNLOCKS=all` | Every unlock for that run |
| `TYR3D_LEVEL_TICKS=<n>`, `TYR3D_LEVEL_DIE=<n>` | End every level as cleared after n ticks, or destroy the ship after n ticks (for testing what follows) |
| `TYR3D_DUMP_KEYS=1` | With `TYR3D_DUMP_DIR`: dump the first frame shown after the game has taken each test key (its key, button, wheel or pointer event) instead of every n-th (menus) |
| `TYR3D_UPSCALE_DIR=<dir>` | Where the HD resources are: `tiles/*.hdt`, `sheets/*.hd`, `hud_1p.png`, `hud_2p.png`, `pictures/pic_NN.png` (default `data/hd`) |
| `TYR3D_MODE=<mode>` | With `TYR3D_START`: `arcade`, `two` (two players), `twin` (twin-stick), `galaga` (the secret level's mode), `timed:<1-2>` (timed battle; start at section 1) or `super:<1-9>` (Super Arcade) instead of a full game |
| `TYR3D_TEST_PAD=1` | A virtual gamepad ("Tyrian3D test pad", which SDL takes in background windows too) that `TYR3D_TEST_KEYS`' Pad keys drive: `PadLX<v>`, `PadLY<v>`, `PadRX<v>`, `PadRY<v>` put a stick's axis at v (-1..1, right and down positive) and leave it there, `PadLT<v>`, `PadRT<v>` a trigger (0..1), `PadA`, `PadB`, `PadX`, `PadY`, `PadBack`, `PadStart`, `PadLB`, `PadRB` press a button (`*<ms>` holds it) |
| `TYR3D_SHIP=<1-18>` | With `TYR3D_START`: the player's ship, numbered as in the shop |
| `TYR3D_PLAYFIELD=wide` or `original` | The playfield for the run (as the setting) |
| `TYR3D_SIDEWAYS=<1-3>` | Every level seen from the side (as episode 6's side-scrolling levels; 2 and 3 add asteroids or crags along the edges) |
| `TYR3D_EP6_END=camanis` | With `TYR3D_START`: at episode 6's end, on to Camanis 2 and episode 7 (a test run asks nothing; without it, episode 1) |
| `TYR3D_CHASE=1` | Every level seen from behind the ship (as Tyrian3D event 205 shows a level: the camera low behind the playfield's bottom edge, `CHASE_TILT` degrees from straight down, looking up it) |
| `TYR3D_DIFFICULTY=<n>` | With `TYR3D_START`: the difficulty (1 easy, 2 normal, the default, 3 hard, 4 impossible ...; `config.h`); episode 1's TYRIAN and SAVARA have maps of their own from Hard on |
| `TYR3D_SHOP=1` | With `TYR3D_START`: the store between levels isn't skipped (start at the section before a level to see it) |
| `TYR3D_CUBES=1` | Every store holds all the data cubes its script lists, as if they were picked up (to test the reader and its voices) |
| `TYR3D_SECRETS=0\|1` | Record the secrets found, or not, whatever the run (by default a dev run, a demo, a rogue run or a custom episode records none; see Secrets). Use with its own `XDG_CONFIG_HOME` |
| `TYR3D_TEST_KEYS=<frame>:<key>[,<ms>:<key>...]` | Press a key (an SDL scancode name: `P`, `Escape`, `Return`, `Down`...; `MouseLeft`, `MouseRight`, `MouseMiddle`; `<key>*<ms>` holds it (a modifier, `Left Shift`, `Left Ctrl`..., in SDL's modifier state too, so `Left Shift*3000,400:G` is Shift+G); `MouseTo<x>x<y>` moves the game's pointer to that window point, where the mouse buttons then click, without moving the system's; `WheelUp`, `WheelDown` turn the mouse wheel a notch; `Joy<key>` presses the key as the joystick's, as its menu input does, so the key hints show the joystick's; `Type<text>` types the text, as a name or a code at the title) when that frame shows, then each next one so many milliseconds after the one before; any length |
| `TYR3D_DUMP_FROM=<frame>` | With `TYR3D_DUMP_DIR`: dump from that frame on |
| `TYR3D_DEBUG=pick` | The debug flight's level list first, instead of the intro and title screen |
| `TYR3D_DEBUG=1`, `TYR3D_DEBUG_SEEK=<tick>` | With `TYR3D_START`: a debug flight (see above), starting that many ticks in |
| `TYR3D_FONTS=0` | The game's texts in its pixel fonts, not in Oxanium, over the 3D view |
| `TYR3D_ERASE=0` | The maps' clean ground is left out: the objects, wrecks and palms painted into the map stay in the ground under their models, and no stand-ins are drawn |
| `TYR3D_RAIL_FROM=<tick>` | A level flown on the rail starts at that tick of its flight (70 a second), the waves before it skipped (the boss at 7980, the checkpoint at 3920) |
| `TYR3D_RAIL_DUMP=<dir>` | A level flown on the rail (`rail.c`): each chunk of its ground's texture as it is made, `chunk_<k>.bmp` |
| `TYR3D_LOG_OBJECTS=1` | With frame dumps, print every 3D object of each dumped frame: its model, its look (sheet and sprite), where on the screen, its layer, the events that made it (time and link) and whether it is a stand-in |
| `TYR3D_LOG_STANDINS=1` | Every 30th frame, print the stand-ins shown on the screen (their look, placeholder or own model, where on the screen and on the map, as the `.std` has it, and the nearest enemy) and how many are covered by their enemies (with frame dumps, `dump:` lines say which 3D frame a dump is) |
| `TYR3D_DARK_LIGHTING=0` | Spotlight levels show the game's lit cone as an overlay, instead of being dark and lit by the ship's lamp |
| `TYR3D_RC=off\|low\|high` | The radiance cascades: light of what glows spreads over the playfield (default low, with Effects) |
| `TYR3D_RC_INTENSITY=<0-2>` | How much light they add (default 1) |
| `TYR3D_LOG_RC=1` | Print the radiance cascades' state now and then |
| `TYR3D_GLOW_LIGHTS=0` | Shots and other glows don't light their surroundings |
| `TYR3D_LIGHT_CEILING=<luminance>` | The point lights' ceiling (default 1.0, 0 none): the light the explosions and glows add to a surface eases out towards the room it has left under this luminance (at least a fifth of it), so dark ground still flashes bright while pale ice or snow under a stream of shots doesn't burn white (`BTBHGPUSceneLighting.point_light_ceiling`) |
| `TYR3D_FLAME=<share>` | How much of a flame model's glowing materials is added to what is behind it (`models.cfg` `model ... flame`; default 0.25, 0 draws them opaque as other models) |
| `TYR3D_POINT_LIGHTS=<n>` | At most n point lights in a frame (default 12, 0-32): the explosions' and the glows' lights, the most important first, lights close together merged into one (`render_gpu.c` `add_explosion_lights`); every lit pixel adds up every light, so their number is the cost |
| `TYR3D_LOG_LIGHTS=1` | Print the point lights of each frame |
| `TYR3D_LOG_BOSS=1` | Print the boss bar's armor each time it changes |
| `TYR3D_LOG_EVENTS=1` | Print each of the level's events as the clock reaches it (its number, time, type and data) |
| `TYR3D_LOG_JUMPS=1` | Print the level clock's jumps (loops, timers, mid-level bosses), scroll speed changes, warp orbs and data cubes picked up |
| `TYR3D_TEST_EXPLOSION=<x>,<y>,<every>` | A large explosion at this screen point every so many frames, to look at the particles |
| `TYR3D_TEST_PICKUP=<every>` | An item's pickup flash at the ship every so many frames, and a coin's value over it (250 and 1k in turn), to look at them |
| `TYR3D_TEST_WARP=<frame>` | The level ends at that frame as its last event ends it (the ship warping away) |
| `TYR3D_TEST_WRECK=<every>` | The player's ship's wreck flung apart (with a large explosion) mid-screen every so many frames |
| `TYR3D_WEAPONS=<front>,<rear>[,<power>]` | With `TYR3D_START`: the weapons, ids as in the shop's weapon ports, and their power (1-11) |
| `TYR3D_SIDEKICKS=<left>,<right>` | With `TYR3D_START`: the sidekicks, numbered as in the shop (the catalogue lists them) |
| `TYR3D_SPECIAL=<n>`, `TYR3D_BOMBS=<n>`, `TYR3D_ARMOR=<n>` | With `TYR3D_START`: a special weapon (its id in the item data), super bombs at each level's start (0-10), the ship's armor at each level's start (1-28; under 6 the low-armor warning) |
| `TYR3D_WINDOWED=1` | Run in a window in the corner of the screen without taking the focus, and keep playing without it (`tools/capture_run.sh` sets it) |
| `TYR3D_EXPORT_MUSIC=<dir>` | Export every song as a MIDI file (with the General MIDI instruments the composer set for MIDI devices, the drums on the drum channel), and the instruments they use (`instruments.json`, with each one's raw MIDI bytes: program, dum1, dum2) |
| `TYR3D_EXTRACT=<dir>` | Export the sprite sheets and the enemy catalogue (see `tools/catalog_html.py`) |
| `TYR3D_EXPORT_PICTURES=<dir>` | Export the game's pictures as PNGs, each in its palette, to be drawn anew: the 14 full-screen pictures of `tyrian.pic` (menus, title, HUD panels, logos, story pictures), `tshp2.pcx`, the data cubes' faces and the ending's animation frame by frame; `README.txt` in it says where each shows (e.g. `export/legacy`) |
| `TYR3D_BACKGROUNDS=<digits>` | Draw tiles only for these background maps, e.g. `13` (for checking; default all) |
| `TYR3D_HD_TILES=0` | Leave out the HD tiles (`data/hd/tiles`, `tools/tiles_hd.py`): the maps' tiles at their size |
| `TYR3D_DEBUG_TILES=1` | Tint the map tiles by background: background 2 magenta, background 3 cyan (for checking which map a tile belongs to) |
| `TYR3D_LIGHTING=<sun>,<sky>` | Override the models' light: the sun's energy and the share of the sky's light (for tuning; defaults 4, 0.3) |
| `TYR3D_SHADOWS=0`, `TYR3D_EFFECTS=0` | No shadows, no particles and glows (override the 3D settings) |
| `TYR3D_SHADOW_SOFTNESS=<n>` | The sun's apparent size for the shadows' penumbrae (default 1; 0 sharp, only the hardware's 2x2 filtering; for tuning) |
| `TYR3D_SSAO=0\|1` | The ambient occlusion off or on for the run (default: the setting, 3D → Ambient Occlusion, `ssao` in `[tyrian3d]`) |
| `TYR3D_SHAKE=0\|1` | The view's shaking off or on for the run (default: the setting, 3D → Screen Shake, `shake` in `[tyrian3d]`) |
| `TYR3D_SSAO_TUNE=<radius>,<intensity>,<power>,<bias>` | Tune the ambient occlusion (defaults 14, 3.5, 1, 0.05; the radius and the bias in game pixels: how far round a point it looks for what hides it, how far over a surface a point must stand to count) |
| `TYR3D_SSAO_DEBUG=1\|2` | 1: the scene shows the ambient occlusion alone, in grey (the see-through surfaces still drawn over it); 2: every other scene is drawn without it, to see before and after in one run (Destruct and the jukebox don't repeat frame for frame) |
| `TYR3D_SIDES=mirror` | Continue the background maps beyond their sides mirrored, as before the generated columns |
| `TYR3D_WINDOW_SIZE=<w>x<h>` | With `TYR3D_WINDOWED`: the window's size, for checking other aspect ratios |
| `TYR3D_GLINTS=<scale>,<strength>,<sharpness>,<tilt>` | Tune the sun's glints on water (defaults 1, 0.5, 140, 3) |
| `TYR3D_SMOOTH=0` | Show each of the game's frames once, as it renders them (no frames between ticks) |
| `TYR3D_DUMP_AHEAD=1` | Frame dumps include the frames shown between ticks |
| `TYR3D_SOFTWARE_POINTER=1` | Draw the mouse pointer into the screen as the original does, instead of the system pointer |
| `TYR3D_HUD=modern\|classic` | The HUD over the playfield, or the original panel beside it |
| `TYR3D_MENUS=modern\|classic` | The menus in the modern UI's style, or the original screens (as Graphics > Menus) |
| `TYR3D_SCREENS=fill\|integer` | With the modern UI: the old 320x200 screens fill the window (cut to its shape; on ultrawide its 16:9 middle over a blurred copy), or as Scaling Mode says |
| `TYR3D_UI_SCALE=<percent>` | The modern UI's and the HUD's size (50-200; the setting has 75-150) |
| `TYR3D_UI_GALLERY=1` | The title screen shows the modern UI's widgets (tabs, item cards, pickers, bars, keys) instead of its menu, to judge the style by |
| `TYR3D_MODEL_ICONS=0` | The modern UI's item icons as the sprites' pictures (the HD upscales), as before 2026-10-29, instead of the renders of the items' models (`assets/models/icons`), to compare (with `TYR3D_PROFILE` each render's texture prints as it is made: `model icon: <model> at <n> pixels, its texture made in <ms> ms`, what it took the main thread) |
| `TYR3D_RENDER_ICONS=<dir>` | Once the modern store shows the ship, render the icon of every model an item's icon shows into `<dir>/<model>.png` (`render_gpu.c` `rgpu_render_icons`; `assets/models/icons` is what the UI reads; see Models), printing every item and what its icon shows (`icons: <ship\|gun\|shield\|generator\|sidekick\|special\|data cube> <id> <name>: <model or "its sprite">`), then `icons: <model>: <w>x<h> of a <n> square, written` for each render and how many |
| `TYR3D_SPECIAL_AUTO=0\|1` | The special weapon a press each, or again whenever it is ready while fire is held, for the run (default: the setting, 3D → Specials) |
| `TYR3D_SIDEKICK_FIRE=hold\|charged\|rapid` | How the charging sidekicks with endless ammo fire for the run (default: the setting, 3D → Sidekicks) |
| `TYR3D_MOUSE=direct\|original` | The ship goes where the (hidden) pointer is, which moves as on the desktop (default), or the original's mouse control (a speed, with momentum) |
| `TYR3D_RENDER_SCALE=<0.25..1>` | Render the 3D scene at this scale of the window's pixels (default: the window's size in points, half on high-density displays) |
| `TYR3D_TILES_ONLY=1` | Leave out the background layers the game drew, so only the map's tiles show the backgrounds (to compare them) |
| `TYR3D_LAYER_PARALLAX=1` | Show the layers' planes unscaled (positions on different layers no longer line up as in the game) |
| `TYR3D_LOG_SPAWNS=1` | Print each enemy an event makes, and whether the 3D view showed it coming; and where the 3D view first shows an event's enemy coming (`coming:` lines: one shown and never made vanishes where it would have been) |
| `TYR3D_LOG_SPRITES=1` | Print what the 3D view draws from sprites (an HD volume from the 4x sheets, the sprite's own volume, a flat shot, or the flat sprite) rather than as a model, to find what still lacks a model (`devtools.c` `dev_log_sprites_frame`, every captured frame; the store's weapon simulator too): each look once, as it is first drawn so, `sprites: look <kind> sheet <sheet> sprite <frame> first <first sprite> <1x1\|2x2> <volume\|flat\|sprite> layer <layer> at <x>,<y> episode <n> level <name> clock <tick> -> <a model of the same thing, or "no model">` (kinds by the objects' keys: enemy, item (coins and power-ups sheets), coming (shown before it is made), shot, enemyshot, departed (flown off the screen's top), player, sidekick, store; sheets as `models.cfg` names them; `sprite`: an enemy in sight that left no 3D object three frames running; blank sprites left out; the model near: its own sprite or shot line, which the path that drew it went without, or a sprite or frame line of another frame of its animation), and for each level as it ends and for the run, how many objects were drawn either way (`sprites: level <episode>:<name>: ...`, `sprites: run total: ...`). Shots without a model are flat volumes, as the levels draw them; since 2026-10-30 every shot sprite the game draws has a model (`models.cfg`'s shot lines), so a shot in this log is a new or a missed one. It also reports the game's own drawing over the playfield, the overlay layer the 3D view shows flat at the screen's size (texts, bars, brightened bands): `sprites: overlay <pixels> px at <x0>,<y0>-<x1>,<y1> episode <n> level <name> clock <tick> frame <presented frame>` at most once a second while it shows, and `overlay in <n> frames` in the level's and the run's totals (a sweep of the 83 levels of episodes 1-6 on 2026-10-30: none) |
| `TYR3D_LOG_MOVES=1` | Print every enemy each tick (clock, slot, enemy, place, speed and what carries it, steering, link): `tools/gbc/moves.py` sets episode 7's paths against the GBC's |
| `TYR3D_LOG_BALANCE=1` | Print what a level costs and gives the player, a `balance: <what> <value> clock <tick>` line each (`devtools.c` `dev_balance`): an enemy that comes (`spawn`, its type), one killed or rammed (`kill`, `rammed`: its slot), an enemy shot fired (`shot`), the damage that hits the ship (`damage`, in god mode too; right after what dealt it: `hit`, an enemy shot, or `bump`, a collision, the enemy's type), an item an enemy leaves (`drop`, or `droplost` with no free slot for it: its value) and one picked up (`pickup`), to set a level against another (episode 7's against their originals) |
| `TYR3D_AA=<0..3>` | Anti-aliasing: 0 off, 1 SMAA low, 2 SMAA high (default), 3 FXAA |
| `TYR3D_LOG_CLOUDS=1` | Print which tiles of backgrounds 2 and 3 are shown as cloud puffs, and each cloud canvas's height and the ground under it |
| `TYR3D_TERRAIN=0` | Leave out the terrain from assets (the ground flat or with per-tile relief, backgrounds 2 and 3 flat) |
| `TYR3D_VEGETATION=0` | Leave out the vegetation (palms, trees and grass from `assets/terrain/<map>.veg`) |
| `TYR3D_VIEWER_FIRST=<n>` | Model viewer (`TYR3D_VIEWER=enemies`): start at the n-th sprite rule of `models.cfg` |
| `TYR3D_HD=0` | Leave out the HD volumes (the generated models from the 4x upscaled sheets) |
| `TYR3D_FILTER=0` | Show the maps' tiles and the layers as sharp pixels instead of smoothly filtered |
| `TYR3D_DEBUG_TERRAIN=1` | Print each frame which backgrounds can be terrain and why not (blended, filtered, composed) |
| `TYR3D_LOG_GROUND_MODE=1` | Print how the ground is drawn whenever that changes: as terrain (its map, heights and holes), in relief by tiles, or flat and why (stars, a filter) |
| `TYR3D_TURBO=<factor>` | Run the game that many times faster, showing only every so many ticks (for collecting data over whole levels) |
| `TYR3D_LOG_GROUND=1` | Print where ground enemies stand or move on the background maps (`ground:` lines: also their sheet and first sprite, where on the screen, the 3D frame, and the object each is a piece of) and what their models cover round them (`groundmodel:`), for `tools/terrain/make_terrain.py` (`tools/terrain/ground_log.sh`); the top enemies riding background 3 as `riding:` lines on its map (for `make_cleanground.py`'s upper maps: `cleanground.json` `upper_maps`, whose `.std` stand-ins the game draws among the top enemies) |
| `TYR3D_LOG_CLIP=1` | Every 10th frame, print each enemy model that raised ground or a background hides in part, or that shows where the game hides it, by more than 2 pixels: its model's triangles as drawn, rasterized as the camera sees them, each point that shows checked on its way to the camera (`render_gpu.c` `log_clipping`): `clip: <kind> frame <3D frame> layer <layer> sheet <sheet> sprite <first sprite> model <name> at <x>,<y> depth <pixels> of <its height> area <percent> inside <percent> screen <x>,<y>` (depth in the model's game pixels; area: the share of what shows of the model affected that deep; inside: of that, where the model is in the terrain or solid rather than behind raised ground in front of it; screen: its middle in the window, 0-1, and with frame dumps `dump:` lines say which 3D frame a dump is). Kinds: `terrain` (the ground's terrain), `bg2-solid`, `bg3-solid` (backgrounds 2 and 3 as solids), `ground` (background 1 drawn flat), `bg2-plane`, `bg3-plane` (backgrounds 2 and 3 drawn flat hiding a model the game draws over them), `bg2-over`, `bg3-over` (a model showing above one of them where the game draws it over the enemy), `float` (a ground enemy on raised or covered ground: its lowest points seen stand higher above the ground drawn under them than they would above a flat ground; leaning, its lowest points above its leaning base, the lean counted in its lift; depth is how much higher, area the share of those points, and a `gap <pixels>` at the end how far above the ground the worst one is). With frame dumps every dumped frame is checked too. Sheet and sprite as in `models.cfg`'s `sprite` lines; `TYR3D_LOG_CLIP=2` adds where the deepest point is, the lift the model got, the ground drawn under its middle, the terrain stored at its position and its lean (degrees across x and z) |
| `TYR3D_RELIEF=<height>` | Per-tile relief of the ground where a map has no terrain asset (default 8, 0 off) |
| `TYR3D_DEBUG_WATER=1` | Tint the procedural water red (to see where it is) |
| `TYR3D_EXPLOSION_LIGHTS=0` | Leave out the explosions' lights |
| `TYR3D_TEST_LIGHT=<x>,<y>,<height>,<radius>,<energy>` | Add a point light at a game position (to check the lighting) |
| `TYR3D_BLOOM=<intensity>,<threshold>,<knee>,<radius>` | Tune the bloom (defaults 0.35, 1.25, 0.2, 1.2; intensity 0 turns it off) |
| `TYR3D_SUN=<x>,<y>,<z>` | Override the direction the sun's light travels (for tuning; default 0.6,-1,0.6: from the top left of the screen) |
| `TYR3D_VIEWER=ships` | Model viewer: each ship's 3D look beside its sprite (see `src/viewer.h`), with `TYR3D_VIEWER_YAW`, `_ROLL`, `_SPIN`; `sidekicks` shows the sidekicks |

## How it works

- **SDL3 port.** OpenTyrian2000 was moved from SDL2 to SDL3, which SDL_GPU requires.
- **Layer capture** (`src/layer3d.c`). The main loop marks where each draw phase starts:
  background 1, ground enemies, background 2, sky enemies, background 3, player and shots,
  explosions, and so on. At the end of each phase the screen is diffed against a snapshot, and
  the pixels that changed become that phase's layer. Each layer is captured before later phases
  cover it, so it is complete. Filter effects (water, blur, darkening) write their changes back
  into the layer that owns each pixel. The level's colour filter is applied per layer, as a
  palette remap.
- **Levels flown on the rail** (`src/rail.c`, `rail.h`; the script's `]r[` before a level's `]L` line; episode 6's
  STARFALL: `story.py` `rail`, `build.py`). A game of its own in 3D, as Star Fox 64 flies, with no 2D view: the level
  is loaded as ever (its maps, their HD tiles, terrain and plants), then flown instead of played. The ship goes on a
  rail into the window, low over the ground seen from behind it, the camera following it softly and leaning into the
  rail's turns; it moves across the window and up and down (the keys, a joystick, the mouse), fires twin lasers along
  its nose (their power the front gun's, 1-11, raised by blue capsules; one laser below 3, blue from 6), and with a
  rear gun homing missiles as well; the sidekick keys brake and boost (the boost gauge), the mode key drops a bomb (two,
  three with a special: everything near ahead goes), a double tap left or right rolls it (shots glance off). Fire held
  past `CHARGE_TICKS` (the lasers going on) glows at the nose and the reticle locks on the enemy (or the boss) it passes
  over, ringed red; let go, the charge goes as a ball of green light homing at it and bursting on the first thing it
  meets, hurting all within `BLAST` (several down at once: a hit more for each past the first). The
  ground: background 1's map with its generated columns and, PLATEAU higher where it has tiles, background 3's (HARVEST's
  meadows over its machinery, mirrored from its own columns), each with its terrain's relief, built in chunks along the
  flight (40 rows, its HD tiles at two texels a pixel, mipmapped) a few rows a tick; the maps go on mirrored end to
  end as long as the flight goes, and beside it. Its plants are the 3D view's (nearest first, grass only near), shaded
  as the 3D view's terrain is (unlit, the sun baked into its vertices), soft shadows under what flies; haze walls across
  the flight veil the far ground into a sky wall's gradient. The level is a list of waves by the flight's tick (70 a
  second, whatever the display's pace; `WAVES`): fighters in Vs at the ship, across ahead of it, up from behind it and
  round, standing ahead strafing, diving from high; turrets and domes in the meadows; mines; rings that restore the
  shield and the armor, capsules, bombs, cash, some left by a formation's last fighter (a whole formation down: +500).
  Two sets of stone arches stand across the rail (`ARCH_SETS`; the model `rail_arch`, `tools/modelkit/make_rail_arch.py`),
  one after another and each a little to one side: through one, +100; through every one of a set, +1000 and a bomb;
  into one's stone, hurt and thrown off. Then the boss, SAVARA's big red jet built from its seven pieces as SAVARA's events place them: up from behind over the
  ship, round at it, firing fans, launching fighters, and at half its armor charging. The HUD (`ui.c`
  `build_rail_hud`): score and hits, shield, armor, boost, the lasers' power, bombs, the boss's armor, a line in the
  middle; P pauses, Esc pauses and asks, Esc again leaves the level. Halfway (`CHECKPOINT_TICK`) a checkpoint: a ship
  lost after it flies on from there, whole, the enemies gone, the cash and the rest as they were there; low on armor,
  a warning and smoke from the ship. It ends as the level would: through, the cash it earned the player's with 25 a hit,
  its enemies' share the results'; lost before the checkpoint, as a ship lost in a level. Plan and what is left
  (radio voices, other stretches): `docs/plans/2026-11-04-starfox.md`.
- **Background maps** (`src/background3d.c`). The game draws only the background tiles that fit
  on its screen; the tilted camera sees much more. So the 3D view draws the three background maps
  itself, as tiles on each background's plane, for the whole area the camera sees (up to 640
  pixels ahead, then fading out). Each time the game draws a background its scroll state is
  recorded, so the tiles line up with the game's own drawing, and scrolling further up follows
  the map's wrap points. Beside the map, 16 columns on each side are generated from the map's
  own tiles by wave function collapse (`src/wfc.c`): which tile may stand next to which is
  learned from the map, and the columns next to it must fit its edge. Which of the fitting tiles
  each cell gets follows a guide, so that the map's large features go on beyond its edge rather
  than stop there: the map mirrored at the edge, sheared along the slant of what meets the edge
  (a river or a cliff that leaves the map at a slant goes on straight instead of turning back),
  warped by smooth noise the more the further out (no mirror image), each tile weighed by how
  often the map uses it and how much it looks like the guide's tile there (colours averaged over
  4 x 4 pixel blocks, mirrored where the guide is). So water stays water and land land, shores
  and plateaus close beyond the edge, and the map's rare pieces (pipes, buildings) turn up only
  where the edge leaves no other choice. The columns are solved in bands of 24 rows, each a few
  rows further than it keeps so that the next goes on from it, and the solver undoes choices that
  lead to a contradiction, so no band breaks off from the one above or from the map (until
  2026-11-04, `SIDE_CACHE_VERSION` 5, the tiles were weighed by their use alone: grid-like crests,
  water and islands stopping short at the edge, bands cut off straight). They are made ahead of
  time for every level (`tools/precompute_sides.sh`, into `assets/sides`); a map without them
  gets them when it loads, kept in `tyrian3d-sides` in the user's directory. Further out the
  map continues mirrored; everything beyond the map slowly darkens. `TYR3D_SIDES=mirror`
  mirrors only, for comparison. The terrain covers the generated columns too, so new sides want
  the terrain, clean ground and vegetation made again (`make_terrain.py`'s classes are frozen
  in `tools/terrain/centroids.json`, so the heights stay with their surfaces).
  Inside the playfield the captured layer is drawn over the tiles. Backgrounds that the game
  filters (lava, water, ice) cannot be tiles, since the filters blur and waver across tile edges:
  they are composed on the CPU for the area the camera sees and run through the game's own
  filter code, with the waver aligned to the game's screen.
- **Deep space** (`render_gpu.c` `add_deep_star_batch`, `add_nebula_batch`). While the game's starfield
  is on, more stars lie in layers far below the ground and scroll with the game's stars, the deeper
  ones slower; deeper still, a few patches of faint glowing gas (a nebula in two hues of the level's
  own, by its background 1 map) drift by, and deepest a planet (`add_planet_batch`: one of the jukebox's
  surfaces, gas giant or green world, tinted by the level's map, its axis along the screen, turning slowly,
  sunlit with its shading baked into its mesh, a halo of atmosphere round it) drifts by at a tenth of the
  stars' pace, coming round again after a long while; now and then a shooting star streaks across deep space
  (`add_meteor_batch`: a bright head and a fading tail, under a second, at uneven times). No shadow falls so deep, and smoke there thins out pale
  (dark, it showed as soot over the nebula and the planet). Both show through what background 1 leaves empty, and only
  with the Effects setting. A map that shows nothing (no tile, or only tiles of colour 0) is neither
  drawn as tiles nor makes the backgrounds under it composed, even if the game blends it (episode 6's
  GRAVITRON: its empty, blended background 2 had background 1 composed, opaque, hiding the deep space).
- **Weather** (`render_gpu.c` `add_weather_batch`; `assets/models/terrain.cfg` "weather <snow|embers|pollen|sand|leaves|bubbles> <level>").
  Over the ice planets (CAMANIS, ICE EXIT, ICESECRET, DEEP ICE, GLACIER, Camanis 2) snow falls and drifts
  down the screen at every depth between the ground and the camera, so the air itself shows depth; over the
  lava (LAVA RUN, LAVA EXIT, CORE, THE CORE, CRUSTGATE, MINERS, the GBC's LAVA I and II) embers rise from
  the ground, flickering and fading as they climb; over the meadows and jungles (TORM, BOTANY A and B,
  the GBC's JUNGLE and JUNGLE II) pollen floats low and glints; over the deserts (DESERTRUN, SURFACE, DIG SITE, the GBC's
  DESERT and OASIS) sand blows in pale streaks low over the ground; over WINDY autumn leaves are blown along,
  fluttering; in CORAL and REEF (under the sea: CORAL's eels and submarines) bubbles rise from the floor, wobbling; in open space (the starfield on) faint dust streams by
  at every depth as the ship flies on. Five bands of heights, each spread over what the camera sees there;
  Effects only.
- **Gulls** (`render_gpu.c` `add_bird_batch`; `assets/models/terrain.cfg` "birds <level>"): over the sea levels
  (SAVARA) a few flocks of gulls fly in a loose V each, their own heading and height,
  beating their wings and gliding by turns, their shadows on the water; Effects only.
- **Overscan.** Sprites can be seen above the original top edge, so in 3D mode the game also draws
  enemies into 64 extra rows above the screen. A shot the game drops as it leaves the screen's top flies on in the 3D
  view (`layer3d.c` `l3d_shot_departed`) as it was drawn: its model, a missile with its smoke, or its sprite's volume
  (2026-10-29; until then always the sprite's volume, so a missile turned flat at the screen's top edge).
- **Rendering** (`src/render_gpu.c`). Layers become textured planes at increasing heights, each
  scaled about the point below the camera so that a position on any layer is seen where the game
  draws it (a turret's shots and explosion stay on the turret); objects scale with their plane. What
  stands on the ground stands on it as drawn (`render_gpu.c` `stand_lift`: the terrain's relief under it in
  the world, on the edge of its footprint the camera sees), and on terrain leans with it, by pitch and roll
  of at most 12 degrees, following it smoothly as the map scrolls (`compute_object_lifts`, `lean_matrix`;
  what leans is moved along the camera's rays so it is still seen where the game draws it): a thing alone
  by the plane of the ground under its footprint, where that ground is one; the pieces of one enemy, made
  together by the level's events, on one plane, leaning as best fits the ground under them, at their lifts'
  mean but none deeper in the ground than half its height. What the game draws under a solid background 2
  or 3 and lies mostly inside it fades out (`hide_in_solids`). Solids scroll at their own speed over the ground's
  terrain (TYRIAN's stone platforms three times as fast), so its raised ground and plants would stand up through
  their tops: the tops alone are drawn first and mark their pixels in the stencil, the ground and its plants aren't
  drawn there (as the game draws the solids over the ground), then the solids whole, their walls going down into the
  ground as drawn (a wall, of a solid or a hole, is textured with its surface's pattern from a little way in, as deep as half
  its height, not its edge stretched down: `TERRAIN_WALL_INSET`); plants under a solid's top aren't drawn at all (`not_on_solids`, `under_solid`). The enemies of a layer the game draws after
  a background stand above that background's plane (`layer_base`; background 3 drawn under the sky enemies
  is the layer `bg3-low`, below them). The camera is fitted so the playfield's bottom edge, at the player's height, fills the original
  playfield width; the projection is shifted onto the playfield's rectangle in the window, and
  the scene continues into the rest of the window. The HUD panel stands at the window's right
  edge, as tall as the window, and the playfield is as large as fits beside it (on 16:9 it fills
  the window's height); messages from the bar below the playfield are shown as text in the
  playfield. Two-player games have the same layout. The HUD and in-playfield text are drawn flat
  on top; the HUD panel at four times its resolution (Scale2x twice). If the panel's picture
  has been upscaled (`data/hd/hud_1p.png`, `hud_2p.png`, see HD resources below), that
  picture is drawn, and only the pixels the game changed on it (gauges, text) come from the game.
- **The modern UI** (`src/ui.c`). Sizes are virtual units, 1080 to the window's height times the
  UI scale, with a smallest size for text in the window's pixels; everything is placed in a 16:9
  safe area (the window, at most 16:9 wide, centred). Panels are octagons (cut corners) drawn as quads
  with a pixel-wide soft edge, the blurred picture under them as frosted glass; text from Oxanium's
  rasters; all of it through the overlay's quads (`rgpu_ui_*`), as the HUD. A menu keeps drawing the
  original screen and publishes what it shows (`ui_menu_publish`: items, selection, an open picker,
  where the original takes the mouse on each); while the screen still shows that (98 % of its pixels),
  `rgpu_present_ui` draws the screen's picture (its texts taken off) and the menu in the new style.
  The pointer's window position on a widget is handed to the menu as a point of the original's item
  (`mapWindowPointToScreen`), so the menu's own code takes the mouse as ever; the wheel is Up and
  Down. The old screens' fill: the screen magnified in whole steps into a target, then drawn smoothly
  (`sharp_steps`), the window round it a blurred copy (80x50, made again only when the picture
  changes). The game's displays on the playfield (score, lives, bombs, special, boss bar, timer) are
  a layer of their own (`L3D_HUD`), left out under the modern HUD.
  The store publishes what it shows each time it shows (`shop_publish` in `game_menu.c`: its menu, the
  parts' choices with costs, icons and stats, the weapon's power, the credits, where the original takes
  the mouse on each) and the 3D view draws its own layout over the picture blurred, with the ship's
  models or the weapon simulator's (its ship and shots over deep space of its own: stars drifting by in three
  layers and a faint nebula, `make_sim_space`, the pane a little larger than the original's box so the ship's
  model shows whole) drawn by the
  scene into the layout's pane (`rgpu_present_ui`). The items' icons are renders of each item's own 3D model where it has
  one (2026-10-29, the user: items were drawn from upscaled sprites while a model of them exists; `ui.h`
  `UIItem.icon_model`, from `game_menu.c` `shop_item_model`: the ship's model, a gun's or the generator's mount as the pad
  shows it (the new content's guns, ports 48-53, the sidekick whose picture they show: the Phoenix Cannon the Phoenix
  Device, ...), a sidekick's; `special_item_model`: a special's power-up; the data cube's pick-up; `ui.c` `build_card`: a
  title card's ship by its sprite): `assets/models/icons/<model>.png`, rendered by the game from the models
  (`TYR3D_RENDER_ICONS`, see Models), drawn by `render_gpu.c` `rgpu_ui_model_icon` at the size its well has in the window's
  pixels (resized from the 512-pixel render on a thread of their own, `model_icons.c`, Mitchell-Netravali; the texture made
  as it is ready, in a frame or two, and faded in), so they are sharp at every UI scale; colours multiplied by the alpha,
  so glass and glows lie over the well. The shields, the MegaMissile sidekick (blank sprites), the specials without a
  power-up model (all but Repulsor, Pearl Wind, Soul of Zinglon, Attractor, Ice Beam and Flare) and items without a
  render keep their pictures (`hd_icon`; `TYR3D_RENDER_ICONS` lists every item and what it shows). The
  scene draws one pass a frame (the pad's), so the icons are pictures, not live models; the item chosen turns on the pad.
  The simulator looks as a level does (2026-10-29, the user: the
  store's preview still used many old visuals; `video.c` `video_sim_*`, `render_gpu.c` `add_showcase_volumes`,
  `add_showcase_glows`, `add_showcase_particles`, `add_showcase_lights`): the shots without a model are their
  sprites with volume, flat, from the 4x sheets (they were the screen's pixels laid over the pane, cut at the
  original's box), every shot glows in its sprite's brightest colour and the strongest light the ship (point
  lights), the missiles leave their smoke (the particles are the simulator's while it shows), the ship's engines
  glow and flame, and its sidekicks show where the simulator fires their shots from (the original draws none),
  with their glows; its logic and what it fires are the original's (no targets: it has none). The ship's scene
  shows the sidekicks' glows and its own model's engines (not the illustration's big ship), and in the modern store,
  on the shields' page, the shield round the ship as a level shows it, as strong as the shield (`video.c`
  `showcase_glows`: the original's arc over its illustration, which the modern store's pad hasn't; the classic store
  keeps the arc). The classic store in the 3D view draws the same simulator over its box's picture. Screens that
  animate on their own while shown (ship
  specs, a level's end) are published with `hold` and shown so until released. The screens over a level
  are drawn over the 3D scene (`rgpu_present_3d_menu` with `modern`); their glass shows the scene copied
  once it is drawn and made smaller in halves by the canvas (`scene_blur`), again only when the scene
  changes. The HUD's panels fade by what is under them: the ship's box and the enemies' shots in the
  window (`hud_fade`); two players: both ships.
  The other screens publish the same way, each with its own data in `UIMenu`: the high scores
  (`UIScores`, `JE_highScoreScreen`, `JE_highScoreCheck`), story texts (`UIStory`: `JE_displayText`
  publishes before each frame `JE_outCharGlow` shows, with how far the original has revealed the text,
  over the picture as it was before the text, `story_begin`; the text is laid out again in paragraphs,
  each character keeping its place in the original's lines, so it shows as far as the original's),
  title cards (`UICard`, `card_publish`), load (`UIPaging` for the players' pages), the jukebox
  (`UIJukebox`, published every frame over its visuals: below), the instructions, the credits (`UICredits`:
  the lines where the original draws them) and the rogue run (`UIRogue`). Where the original takes no
  mouse (the high scores' and load's tabs, the jukebox's buttons and songs, the name question's
  buttons), the widgets are the UI's own: the pointer on one maps to the screen's point of nothing,
  and the screen's code takes a click on it with `ui_take_press` (modern only). The wheel moves
  Up/Down or Left/Right as the screen says (`UIMenu.wheel`). A screen that is over calls
  `ui_screen_done`, so the next screen can't match its picture. The key hints show the joystick's pad
  and buttons when the last key came from the joystick (`push_key` counts its keys:
  `joystick_last_input`).
- **The jukebox's visuals** (`src/musicviz.c`, `src/jukebox3d.c`). With the modern menus the jukebox shows a
  3D scene that plays with the music under its panel, instead of the original's starfield (Classic menus
  keep the original). The music is measured where it is made (`musicviz.h`): the audio callback hands over
  the mixed output (as heard: the music and the sound effects) into a ring, and after each of the player's
  updates the chip's state (`adlib_registers`): each channel's key, pitch, instrument (its General MIDI
  program, 128 and up a drum), the notes it has started (`lds_channel_notes`) and how loud it sounds (its
  operators' levels, key scaling and envelope, `midi_chip_channel_db`, then its release) — both kinds of
  music, the chip and MIDI through the SoundFont, play from the same chip writes. Nothing waits for a lock
  in the audio thread (a ring with an atomic count, a spinlock for two numbers). Each frame the main thread
  reads them where the output is heard now (about 2048 samples behind the newest, on by the clock since the
  last buffer): 2048-sample Hann windows every 512 samples, FFT, 48 bands from 30 Hz to 16 kHz (+4.5 dB an
  octave above 1 kHz), against a reference that follows the music's loudest of late (up in 0.35 s, down in
  14 s; the bands 46 dB below it to it, to the power 1.45), quick to rise and slower to fall, with falling peaks; onsets as the spectrum's rise (the lows
  twice); beats from the song's own kick and snare notes, else from the onsets. Silent test runs
  (SDL's dummy audio driver) measure the same.
  The scene (`jukebox3d_frame`) is boxes, bars, spheres, glows, rings and models that `render_gpu.c`
  draws over the whole window (`present_jukebox_scene`), bloom and all, the panel's glass showing it
  blurred (made again each frame); its middle higher while the panel shows (Space hides it). Between the
  jukebox's ticks it is shown again at the display's rate (`video_wait_tick_ui`). Two looks, V or the
  panel's Look button (kept as `jukebox_look` in `[tyrian3d]`):
  - **Orrery**: a planet (a gas giant made at start) with a crown of 72 bars of lit metal on a ring round
    it, the lows tall at the back, the highs in front, both sides the same, their tops glowing with the
    bars' heat and their peaks floating above them; the chip's nine channels as moons orbiting it in their
    colours, higher with higher notes, lit while their notes sound and flashing as each starts, leaving
    trails and lighting the planet and the bars (point lights); the kick (or a beat) a ring of sparks
    running out from the bars (at most every 0.3 s), the snare sparks from the bars' tops, the toms a ripple
    round the ring, the cymbals a flare behind the planet, the hi-hats the stars; faint nebulae behind; the
    camera sways slowly and comes nearer on the beats.
  - **Warp**: one of the game's ships (a fighter for each song, the USP Talon first) flies towards
    the camera, seen from above at a slant, drawing the spectrum behind it as rings of a tunnel (20 a
    second and on every drum, the lows at the top; the quiet in the tunnel's colour, which goes round teal,
    blue, violet, magenta and amber with the mids, the loud in the bars' heat) and the channels' notes as
    lanes of light along it, round the tunnel by their pitch (an octave a third of the way round), as long
    as each sounds (a piano roll); the drums flash and thicken the rings and shake the camera, the cymbals
    light them all, the stars streak past faster with the music's loudness and its lows.
- **Clean ground and stand-ins** (`tools/terrain/make_cleanground.py`, `src/tyrian2.c` `draw_standins`).
  The maps paint under many ground enemies what is left of them once destroyed (a crater, a burnt housing,
  a broken pyramid), or the object itself, or its base; in 2D the sprite covers it while the enemy lives, in
  3D it showed under and round the model. Offline, each ground map's painted art at the places where ground
  enemies stand (and its copies where none stands), and the desert maps' painted palms, are erased and
  filled with the map's own ground round them (`assets/terrain/<map>.era`: pixels taken from the map at an
  offset, so the palette effects and the HD tiles fill them too; `erase_painted_enemies` applies them as
  the terrain's rows are made). Only where something 3D takes the place: landscape the game animates
  (waterfalls), the rock arches and paintings without a model stay. Where the original shows the painting
  (before the enemy comes, once it is destroyed, where none ever stands), the 3D view shows its model, a
  stand-in (`assets/terrain/<map>.std`): the look the game leaves when the enemy is destroyed, the object's
  own model where the map paints the object as it is (or, where the map paints it in other colours, models.cfg's
  `standin <sheet> <sprite> <model>`: TYRIAN's and SOH JIN's rubble in rock browns, `tools/glb_palette_remap.py`
  makes such colour variants), its wreck model (models.cfg `wreck <sheet> <sprite>
  <model>`: the painting as a model, drawn with the enemy type's options; `none`: nothing), or until it has one the enemy's
  model slumped and darkened (`render_gpu.c` `STANDIN_SLUMP`, `STANDIN_SHADE`). A stand-in is drawn while no ground
  enemy of its looks (the enemy itself, its damaged and dead looks, what it turns into) stands on its place;
  it is only drawn, the game knows nothing of it. A wreck's pieces stand together on the terrain as an object's
  pieces do (at their lifts' mean), unless the ground under them steps by more than 6 pixels (a slot on the edge
  of SAVARA V's sea rocks): then each stands on its own (`render_gpu.c` `STANDIN_STEP`). The terrain and the vegetation are made on the clean
  ground, so grass grows round the turrets and the palms stand on bare sand; the plants are kept off the
  models' footprints, and in the game cleared only under the enemies that move.
- **Appearances** (`src/models3d.c`, `assets/models/models.cfg`). Each enemy type and player
  ship is shown as a model, as its sprite with generated volume, or as the flat sprite. For the
  first two the game records a 3D object instead of drawing the sprite; objects are depth-tested
  against the layers and lit by a sun and ambient light.
- **Shadows** (`render_gpu.c` `shadow_view_projection`; the renderer's `production_model.frag.hlsl`
  `primary_directional_visibility`). The sun's shadow map is an orthographic view along its light over what the
  window shows of the ground and of what stands over it (12 below the ground to 110 game pixels above it, no
  further than 160 game pixels above the playfield and 120 beside and below it; beyond that nothing is shadowed),
  fitted in the light's own plane with the world's x across it: about 4.7 million square texels in the region's
  shape (2560x1792 with the Standard and Steep cameras, 2816x1792 overhead; Destruct keeps 2048x2048), up to 1.5
  times as fine as the square map round the view's bounding circle before. Its texel's size is quantized and its
  corner lies on whole texels, from the steady view (not the shaking one), so the shadows' edges keep their place.
  Soft shadows (percentage-closer soft shadows): five gathered depths round each point find how far above it its
  blockers stand (only those whose penumbra can reach it count, so terrain bumps and grass don't make it pay for
  a filter), the penumbra widens by 0.035 world units for each unit of that (`TYR3D_SHADOW_SOFTNESS` scales it):
  a turret's shadow is sharp at its foot, a ship's on the ground about 3 units soft; it is filtered by 4 to 32
  comparison taps (each a hardware 2x2 filter) against the receiver's own plane (from its face, so slopes take no
  acne and the old blocky self-shadowing of the terrain's relief is gone). See-through layers (clouds, weather:
  `unlit_enabled` 3) take four plain taps, lit models look the shadow up only where the sun reaches them. On a
  busy level the GPU spends about 0.1-0.4 ms a frame more than with the old 3x3 filter (TORM's grass the most).
- **Ambient occlusion** (`render_gpu.c` `scene_ssao`; the renderer's `production_ssao.frag.hlsl`,
  `production_ssao_denoise.frag.hlsl`, `production_ssao_resolve.frag.hlsl`; 2026-10-29, the user: SSAO could make the
  game prettier still, depth above all). The 3D setting Ambient Occlusion (on by default): where things meet and in the
  hollows the light is shaded softly (under what stands on the ground, at the foot of walls and cliffs, in the
  canyons and the terrain's dips, in the models' own creases), worked out from the opaque surfaces' depth and normals
  once they are drawn (and the radiance cascades composed) and laid over them before the see-through ones, so clouds,
  weather, smoke, glows and particles keep their light. At half the render resolution: four directions round each
  point, turned by a 4x4 pattern, four steps along each out to 14 game pixels; each step that stands higher over the
  surface's plane than those before raises the horizon (HBAO), counting less with its distance, and only what stands
  within the radius counts, so the ship and the flying enemies leave no halo on the ground far below them. A
  depth-aware 5x5 pass evens the pattern out (each pixel takes all 16 of its turns once, so the shading keeps still as
  the map scrolls and the view shakes), and a depth-aware upsample from the four texels round each pixel lays it over
  the scene where it darkens (most of the screen is left alone). It darkens all of a surface's light but its glow, the
  pixel art's too (the renderer's contact mode; exp(-3.5 times the occlusion), so deep corners don't go black). How
  each surface takes part is its batch's `ssao_mode`, which the model shader writes as the length of its normal: the
  terrain, the solids, tiles in relief, palms and trees, models, volumetric sprites and debris take it and cast it;
  the backgrounds' flat planes and flat tiles take it but cast none (planes 2 to 12 pixels apart, they would darken
  what lies round each other's edges: background 2's flat pieces over the ground); the grass takes it only (its blades
  darkened all of it in a grain); the sprites' layers, the stars, deep space, clouds, weather, gulls, particles and glows
  neither, and procedural water never takes it. The store's box and pane have it too (their floor takes it, the
  simulator's deep space not; the radius in the box's pixels), as do the jukebox and Destruct; the icons' renders
  (`TYR3D_RENDER_ICONS`) don't. On a busy level the GPU spends about
  0.1-0.35 ms a frame more (paused scenes at 1920x1080: TORM's grass +0.34, TYRIAN's canyons +0.29, ASSASSIN +0.29,
  SAVARA's boss +0.15, DELIANI +0.09, deep space +0.03); the store's pad +0.27, the jukebox +0.29, Destruct +0.15.
  Without the radiance cascades (Effects off, the store, the jukebox, Destruct) the scene then also writes its normals
  and emission for it (the ambient targets, which only the cascades read, stay in tile memory).
- **Volumetric sprites** (`src/volume3d.c`). The default appearance: a sprite's silhouette is
  inflated into a rounded relief and textured with the sprite's own pixels. The sun's shading is
  baked into the mesh, scaled so that faces pointing up keep exactly the sprite's colours: every
  object has volume while it keeps its original look. Ground objects, whose sprites include the
  ground around them, stay nearly flat.

## Models

Models are built in Blender by Python scripts in `tools/blender/models`, using the kit in
`tools/blender/tyrkit.py`, and exported to `assets/models` as glTF binaries:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/blender/models/ships/talon.py -- --preview /tmp/talon
```

`--preview` also renders a top view framed like the sprite and a three-quarter view. Conventions:
1 unit = 1 game pixel, the nose up the screen (+Y in Blender), the origin at the sprite's centre.
Materials take the colour an up-facing surface should show in the game, so sprite colours can be
used directly. Better, `tyrkit.material(palette=<index>)` takes a palette index: the game then
colours the material from the current palette, as it does the sprites, so models follow the
level's palette, fades and filters (such materials are named `<name>@<index>`). Those named
`<name>water@<index>` are water: with Effects their darker shades are the procedural water the ground's rivers and
seas are (its colour, waves and glints, a little of their own shading through: `render_gpu.c` `water_shade`), their
light ones keep their colours over it (the waterfall's curtain of TORM and BONUS: its light strands and foam over the
rivers' own water, where it was a glassy grey-blue between them).
`tools/blender/sprite_profile.py` lists a sprite's silhouette and palette indices, from sheets
exported by `TYR3D_EXTRACT` (in the levels' palette, `tools/blender/palette_levels.txt`). The
export reverses the triangles' winding (`tools/blender/glb_winding.py`):
BTBH takes clockwise triangles as the front of static models, glTF counter-clockwise; models
from elsewhere need the same treatment once.

Items (coins, gems, crystals, data cubes, armour, power-ups) are grey models that take the colour
of the sprite's current frame (`color=sprite` in `models.cfg`), so one model serves every colour
and follows animations that cycle colours; see the options at the top of `models.cfg`.

The model viewer shows the models in the game's view and light beside their sprites:

```bash
tools/capture_run.sh /tmp/viewer 30 30 TYR3D_VIEWER=ships
```

(or run the game with `TYR3D_VIEWER=ships` and look; `TYR3D_VIEWER_ROLL=90` shows the side.)

The modern UI's item icons are renders of the models (`assets/models/icons/<model>.png`, 512 pixels, straight alpha;
see the store in How it works): every model an item's icon shows (the ships, the guns' and generators' mounts, the
sidekicks, the specials' power-ups, the data cube in its first frame's ramp; `game_menu.c` `shop_icon_models`), in one
three-quarter view (turned 30 degrees clockwise, its front tilted 35 degrees up towards a camera looking straight down at
it, as the pad's), lit as the store's pad (the sun from the upper left, the sky, its own shadows, the bloom), rendered by
the game twice into the window, over black and over grey (the difference is the alpha, glass and all), framed by what
shows of it with the same margin round its longer side, and resized from three to four times its size (`render_gpu.c`
`rgpu_render_icons`). Made again when a model changes (the store in the store's palette; a window of 1600x900 points at
2x gives a 1800-pixel square, about 15 s for all):

```bash
TYR3D_START=1:4 TYR3D_SHOP=1 TYR3D_WINDOWED=1 TYR3D_WINDOW_SIZE=1600x900 TYR3D_RENDER_ICONS=assets/models/icons TYR3D_EXIT_AFTER=300 build/game/tyrian3d
```

## HD resources

The 3D view's HD pictures are made from the game's data and are in the repository; the
game loads them from `data/hd` (beside `data/tyrian2000`; `TYR3D_UPSCALE_DIR` overrides it): `tiles/<tileset>.hdt`
(the background tiles at 4x), `sheets/<sheet>.hd` (the sprite sheets at 4x, for the HD volumes) and `hud_1p.png`,
`hud_2p.png` (the HUD panel). Without them the game draws the original pixels. The HD tiles and terrain rows are
coloured with the frame's colours a few a frame once those have held for two frames, the rows at the tiles' size
meanwhile; under the game's brightness filter (the Flare special's flicker, stepping every tick; a level coming up
from dark) they keep the colours without it and are dimmed instead (`render_gpu.c` `tile_filter_dim`, not brightened),
and when the colours change a row keeps its HD colouring till it is coloured anew (2026-10-29, the user: the Flare
showed the old textures, the tiles at their own size all through it). `pictures/pic_NN.png` and
`pictures/tshp2.png` are the game's full-screen pictures drawn anew (by hand or an image generator, from
`TYR3D_EXPORT_PICTURES`' pictures, in the same frame at any size; `tools/hd_pictures.py <dir>` puts them there, a
picture with alpha laid on black): where the screen shows one of them much as the game loaded it (45 % of its own,
not black, pixels or more: the logos as the game starts, the title, the menus' backgrounds, a story's picture), in
the modern UI or the old screens, the new picture shows under the screen, which keeps only what the game drew over
its picture (the title's logo, texts), and fades with the palette, to black or white (the median over the picture's
colours, so that colours the screen animates don't count) (`render_gpu.c` `match_hd_picture`;
`TYR3D_DEBUG_PICTURES=1` prints the matches and fades). The user's reconstructions are in `data/hd/pictures`
(not the HUD panels and the old screens' pictures, which the modern UI draws itself, nor the ending's animation).
`pictures/logo_tyrian.png` and `pictures/logo_2000.png` are the title's logo and its 2000(tm) drawn anew (from the
export's `logo_tyrian.png` and `logo_2000.png`, in the same frame at any size, with alpha): over the title's picture,
where the screen shows the logo's sprite (also while it flies in), the new logo shows in its box and the sprite's
pixels are taken off (`render_gpu.c` `find_hd_logos`); a fully clear `logo_2000.png` takes the 2000(tm) away.
`pictures/face_NN.png` are the data cubes' faces drawn anew (the user's, from the export's `face_NN.png`, any size,
clear round the figure): `tools/hd_pictures.py` fits each into the store's portrait window (the export's
`face_frame.png`: the frame, its window clear), as large as it takes to cover it, cut to its shape with a soft edge,
over the whole portrait at 6x; where the store's screen shows a face as it draws it, its pixels give way to the
window's colour and the new face shows over the portrait, fading with its palette (`render_gpu.c` `find_hd_face`; in
the modern UI and the old store with the 3D view; only the face shown is loaded). `pictures/portrait_frame.png` is the
portrait's frame round them drawn anew (the export's `face_frame.png` through `tools/upscale_sprites.py` with
4x-BigFArt-Detail, cut to the portrait by `tools/hd_pictures.py --frame-hd <the upscale>`): drawn over the frame, under
the face, where the store's screen shows it (`find_hd_frame`). `planets/planet3d_<first sprite>.png` are the map's turning planets as 3D spheres (`tools/planets3d.py`: each
planet's surface put together from its 15 frames of a turn, the meridian each frame faces a slice of it, its painted
light evened out and its poles faded into the colour round them, rendered anew lit from the upper left with its
night side, a rim and halo of air, in 48 frames); wherever the UI shows a turning planet's frame (the store's map,
the rogue run's map) its sphere turns instead, one turn in 40 seconds, crossfaded frame to frame (`render_gpu.c`
`planet3d_quad`; the asteroid fields and the unknown "?" stay sprites). `pictures/face_none.png` is what the window shows for a
cube without a face (a message, a guide): a hologram of a data cube in amber (`tools/make_empty_face.py` writes it into
`export/legacy`, `tools/hd_pictures.py` fits it as the faces), shown where the frame shows round an empty window. `icons/` holds the modern UI's icons drawn anew (`shop_`, `ship_`,
`shipt_`, `ship_s_`, `special_`, `option_`, `planet_<sprite>.png`): the export's `icons/` (the store's items as its cards
show them, the ships, the HUD's small ship and bomb, the specials, the data cube icons, the planets of its map, each in
its screen's palette) through `tools/upscale_sprites.py` with 4x-BigFArt-Detail; where one is there
the UI draws it instead of the sprite's pixels (`render_gpu.c` `hd_icon`: the store's cards and its map's planets, and
the rogue run's map, its planets drawn anew over the map's in their own palette's colours; an item with a 3D model of its own
shows a render of the model instead, `assets/models/icons`, see Models). `upscale/` is only the work folder
(atlases to upscale, the upscaled atlases, pictures to look at) and can be deleted; `export/maps` (`tools/export_maps.sh`)
is the HD tiles' input. To make everything again (the upscales take 3-4 hours on the GPU):

```bash
tools/setup_tools_venv.sh
PY=~/Library/Caches/Tyrian3D/tools-venv/bin/python
MODEL=~/Library/Caches/Tyrian3D/esrgan/4x-Fatality.pth
DETAIL=~/Library/Caches/Tyrian3D/esrgan/4x-BigFArt-Detail.pth
$PY tools/tiles_hd.py $DETAIL --tilesets z,y,x,w --work upscale/out/tiles_bigfart
$PY tools/tiles_hd.py $MODEL --tilesets ')'
TYR3D_EXTRACT=export/extract build/game/tyrian3d
$PY tools/make_atlases.py export/extract upscale/in
$PY tools/upscale_sprites.py $MODEL upscale/in upscale/out
$PY tools/hd_sheets.py
```

The sprites, the HUD panels and the lava's tiles (x29) are upscaled with 4x-Fatality by twittman (OpenModelDB, CC BY-NC-SA
4.0); the other tilesets' tiles (z: asteroids, TYRIAN, DELI; y: SAVARA; x: TORM and the jungles; w: the ice) since
2026-10-26 with 4x-BigFArt-Detail by DinJerr (OpenModelDB, CC BY-NC 4.0): sharper stones, grids and ice (the user
chose Fatality for the lava after a comparison in the game on 2026-10-18; the comparison of the others is in item 58 of
`TYRIAN3D_HANDOFF.md`). The Fatality tiles of z, y, x and w are kept in `data/hd/tiles_fatality` (`cp
data/hd/tiles_fatality/*.hdt data/hd/tiles/` goes back). BigFArt-Detail is not in OpenModelDB's own storage: its
author's public OneDrive folder holds it as `4x_BigFArt_Detail_300000_G.pth` (SHA-256
0f8007e6a5ee9b08567c1219def8c13fc2b902f1cfc5f4d6fa17103b69c06002, 66 958 607 bytes; OneDrive's anonymous API: a
token from `https://api-badgerp.svc.ms/v1.0/token` with app id 5cbed6ac-a083-4e14-b191-b4ba07653de2, then the share
`https://1drv.ms/u/s!Aip-EMByJHY23if0ac150Sj2qnbp?e=qLp7SP` encoded as `u!<base64url>` under
`https://api.onedrive.com/v1.0/shares/.../driveitem/children` with `Authorization: Badger <token>`; ask the user
before downloading).

## Tools

| Tool | What it does |
| --- | --- |
| `tools/capture_run.sh` | Runs the game in a background window, silent (`TYR3D_AUDIO=1` keeps the sound), and dumps frames (see the environment variables) |
| `tools/sweep.sh`, `tools/levels.py` | Plays every level for a while and makes a contact sheet per level; `levels.py` lists the level sections (`TYR3D_START`'s), the custom episodes' too |
| `tools/review.sh` | Visual review: plays each level briefly (or the given episodes or `episode:section`s) in a background window and keeps a few frames per level as PNGs; the big BMP dumps are deleted right away |
| `tools/blender/render_models.py`, `tools/model_sheet.py` | Renders `.glb` models in one Blender run (`--list` of files), then contact sheets of the enemy models beside their 4x sprites (with a `TYR3D_EXTRACT` catalogue: ordered by how often they appear, by episode; needs PIL) |
| `tools/catalog_html.py` | Browsable page of the `TYR3D_EXTRACT` catalogue |
| `tools/make_atlases.py` | PNG atlases of the sprites by group (ships, sidekicks, enemies by episode, items), for upscaling and as references |
| `tools/anim_semantics.py` | Sorts the enemies' animations into rotations, rolls, cycles and changes of shape, for models that move as the sprites do (needs numpy, e.g. Blender's Python) |
| `tools/package_macos.sh` | Builds the macOS app bundle |
| `tools/voices/export_cubes.py`, `tools/voices/generate.py`, `tools/voices/say_placeholders.py` | The data cubes and story texts read aloud (see Voices): the script from the game's data, the ElevenLabs render, placeholder voices from macOS `say` |
| `tools/upscale_sfx.py` | Upscales the sound effects and voices with AudioSR into the data's `sfx` directory (run with AudioSR's Python) |
| `tools/hd_sheets.py` | Puts the upscaled atlases back together as 4x sprite sheets (`data/hd/sheets/<sheet>.hd`) for the HD volumes, and copies the upscaled HUD panels to `data/hd` |
| `tools/sprite_reference.py` | An enemy type's reference picture for modelling: every animation frame from the 4x upscales, beside the original |
| `tools/terrain/make_terrain.py` | Terrain for the background maps: `classify` sorts an exported ground map's pixels into surfaces (a review image in `export/terrain`), `build` writes `assets/terrain/<map>.ter` from the settings in `tools/terrain/levels.json` (class heights, chasms where space is black, backgrounds 2 and 3 as solids, or with `"ground": true` a background 2 that covers the whole ground under its enemies as the ground itself; level pads under what stands and gentle roads along what moves, as far as the terrain drawn under them reaches, so their models stand flat; solids clear round what the models cover) and a relief image to review (with the enemies' tracks), `sheets` puts the reliefs on contact sheets, `freeze` keeps the maps' classes as they are found now in `tools/terrain/centroids.json` (k-means on the map with its generated columns: new columns would number them otherwise), which `classify` and `build` then use (needs numpy, scipy, PIL) |
| `tools/fix_macho_tls.py` | Makes pip's scipy load on macOS 27 (its modules' zero-fill thread-local sections carry a file offset the new dyld refuses): clears the offsets and signs the modules again. The terrain tools' Python is a venv in `~/Library/Caches/Tyrian3D/tools-venv` (numpy, scipy, Pillow from pip, then this over its `site-packages`) |
| `tools/terrain/make_cleanground.py` | Clean ground (replaces `make_erasures.py`): for the ground maps, the art painted under and round the ground enemies (wrecks, housings, stumps, the objects themselves, their copies where none stands) and the painted palms, erased and filled with the map's own ground round them, where a model takes its place, into `assets/terrain/<map>.era`; the stand-ins shown there while no enemy covers the place into `assets/terrain/<map>.std`; review pictures `export/terrain/<map>_clean.png` and `export/terrain/standins.txt` (what stands in for each look). Overrides (paintings that stay, stand-in looks, maps left alone) in `tools/terrain/cleanground.json`. Run it before `make_terrain.py build` and `make_vegetation.py`, which take the clean ground. Episode 6's and the custom episodes' maps are cleaned with what the game's own maps teach about their tilesets, not teaching them |
| `tools/terrain/footprints.py` | What the ground enemies' models cover of the ground seen from above (their triangles as the renderer turns and scales them), for the clean ground and the vegetation's keep-out; `check` compares them with the renderer's `groundmodel:` boxes |
| `tools/terrain/make_vegetation.py` | Vegetation for the ground maps, on the clean ground: palms (where the maps paint them on desert maps, `"palms": true`), trees (textured green areas) and grass (smooth green areas), off the footprints of the models that stand on the map (ground enemies and stand-ins), into `assets/terrain/<map>.veg`; also for a background 2 or 3 map whose entry has `"vegetation": true`, where that is the level's grass (HARVEST's background 3: its meadows and woods over the machinery), only where it has something, drawn on its plane and cleared round the enemies riding it |
| `tools/terrain/ground_log.sh` | Plays every level fast with the autopilot and collects where the ground enemies stand and move, and what their models cover, into `export/terrain/ground.txt` (the terrain keeps them on the ground) | (episode 1's SAVARA has a map of its own from Hard on: log, export and build it with `TYR3D_START=1:10 TYR3D_DIFFICULTY=3`)
| `tools/polish_progress.py` | How far the models' polish is: the share of the catalogue's enemy appearances (`TYR3D_EXTRACT`'s `catalog.json`, weighted by count) whose model was last written with a `polish_*.py` script, for the enemies, launched enemies and drops, blank looks (invisible markers) left out; and the most seen looks still missing (run with the tools' Python) |
| `tools/sweep.sh` | Plays every section of the episodes with the autopilot, one run after another, and reports each run's level, whether it ran to the end and its warnings |
| `tools/tiles_hd.py` | HD background tiles that still tile: whole exported maps (`tools/export_maps.sh`) through an ESRGAN model, every tile the per-pixel median of its upscales among its real neighbours, quantized to the palette ramps it uses (palette effects keep working); writes `data/hd/tiles/<tileset>.hdt`, which the game loads with the maps (atlas and terrain at 4x), and its pictures to look at and kept medians to `upscale/out/tiles`. `--requantize` writes them again from the kept medians; `--add` makes only the shapes the kept medians lack (maps exported since, a custom episode's) and keeps the rest. Tiles are per tileset and shape, so generated maps get them too |
| `tools/upscale_sprites.py` | Upscales the sprite atlases 4x with an ESRGAN model (`.pth`, e.g. from OpenModelDB), with alpha (run with a Python that has torch) |
| `tools/setup_tools_venv.sh` | Makes the tools' Python (numpy, scipy, Pillow, torch: `~/Library/Caches/Tyrian3D/tools-venv`) and fetches the ESRGAN model 4x-Fatality (`~/Library/Caches/Tyrian3D/esrgan`); downloads ~180 MB |
| `tools/precompute_sides.sh` | Generates the columns beside every level's background maps into `assets/sides`, all of them anew in place of what is there (`TYR3D_GAME_DIR`: the game's folder to run, as for `each_level.sh`; default `build/game`) |
| `tools/content/make_items.py` | Writes `assets/content/items.cfg`, the new weapons and sidekicks, by rules from the original data (see New content) |
| `tools/content/make_rogue.py` | Writes `assets/content/rogue.cfg`: the rogue mode's acts (levels, bosses found by their boss bars), the items its cards offer (the shops' lists, tiered by price) and its unlocks |
| `tools/content/episode6/build.py`, `tools/content/tyrformat.py` | Episode 6 in the game's formats (the encrypted script and data cubes, the level file with the episode's item data); run at build time |
| `tools/gbc/extract.py`, `songs.py`, `report.py`, `episode.py` | The GBC Tyrian ROM (`data/gbc/Tyrian.gb`, the user's) read in the tools' GBC emulator (`gbemu.c`, `gb.py`; `disasm.py` disassembles): its levels, music and an overview to `data/gbc`, and its levels as PC levels for episode 7 (see Episode 7) |
| `tools/content/gbc/build.py` | Episode 7 in the game's formats from `data/gbc/episode7`; run at build time when those are there |
| `tools/content/gbc/sheet.py` | Episode 7's own enemies' sprites (sheet W, `newshw.shp`) from their models' top views (needs PIL) |
| `tools/content/tyrdata.py` | Reads the game's item data (weapons, ports, sidekicks, ships, enemies...) for the content tools |
| `tools/blender/` | The model pipeline (see Models) |

## The ending in 3D

With the modern UI and the 3D view the game's ending animation (`tyrend.anm`, played by the episode script's `]A`
at the end of episode 3's last level) is a 3D scene of its own instead (`animlib.c` `play_ending_3d`,
`jukebox3d.c` `jukebox3d_ending_frame`, drawn as the jukebox's scenes are: `UI_SCREEN_ENDING`): nine seconds, as the
original: out of black, a green planet up to the left (its own texture: green continents in teal seas, ice caps, swirls of
cloud; jukebox3d.c terran_texture, the jukebox's gas giant the other J3DTexture), turning slowly, a freighter (a long plated hull with ribs, a bridge and two
rows of lit portholes) sweeping past close by from the top right, then the player's own ship (its model) flying in
from the right, the camera closing in behind it, its engines flaring as it leaves into the distance for a red star
that flashes white, and back to black. A key or a click skips it. Classic menus and the 2D view play the original
animation.

## Secrets

The title menu's **Secrets** (where the instructions were; `src/secrets.c`) lists the game's secrets in four kinds,
as tabs with how many of each are found: the levels only a warp orb or a hidden condition leads to (episodes 1-4
and 6: BUBBLES, HOLES, SOH JIN, ASTEROID?, MINEMAZE, WINDY and ALE; GEM WAR, MARKERS, MISTAKES; AST. CITY,
SAWBLADES and the hard-only TYRIAN X, SAVARA Y, New Deli; episode 4's WINDY, DESERTRUN, ICESECRET, SIDE EXIT,
?TUNNEL?, TIME WAR, SQUADRON; episode 6's VAULT), the codes typed at the title (the nine Super Arcade ships,
DESTRUCT, ENGAGE: locked ones as a question mark per letter), the data cubes read in each episode (of how many its
`cubetxt` file holds), and the others (the hidden difficulties Impossible, Suicide and Lord of Game, episode 4's
shop that sells the Stalker 21.126). A found one shows its name, a locked one "???"; the selected one's line says
where to look. Modern UI: a panel over the menus' picture (tabs, rows with FOUND or LOCKED, a click on a tab or a
row); classic: the original screen's fonts. Left/Right change the kind, Up/Down the row, Esc goes back.

The game reveals them as it plays (`tyrian2.c`: a secret level's `]L` line read, the shop's `]I` in its section,
a code accepted at the title; `menus.c`: a difficulty shown; `game_menu.c` `load_cubes`: the store's cubes), and
each is kept at once in the user directory's `tyrian3d_secrets.cfg` (`found <id>` lines: `level <episode>
<section>`, `code <n>`, `cube <episode> <n>`, `difficulty <n>`, `shop <episode> <section>`). Nothing is recorded
in a demo, a rogue run, a custom episode or a dev run (`TYR3D_START`, `TYR3D_TEST_KEYS`, `TYR3D_AUTOPILOT`,
`TYR3D_ROGUE`, `TYR3D_MODE`, `TYR3D_DUMP_DIR`, `TYR3D_EXIT_AFTER`), unless `TYR3D_SECRETS=1`. Destruct counts as
found once it has been discovered (`[destruct] discovered`).

## Voices

The data cubes and the story texts between levels are read aloud (`src/voiceover.c`): when the store's
data cube reader opens a cube, or a story text, a warning or an episode's end with its secret hint shows
(classic or modern menus), its voice plays over the music and the sounds, which are ducked by about 6 dB (200 ms
ramps, `loudness.c`), and a story's stops when the text closes (a 30 ms fade); the text stays as the subtitles.
A cube's voice plays on when its reader closes, until the store closes: the store's data cube player (the
modern UI's bar under the ship: previous, play or pause, next, the cube playing and how far; P plays or
pauses, `[` and `]` go to the previous or next cube, wrapping round) plays the store's cubes while you
shop, and a cube opened in the reader plays from its start; the Data list marks the cube playing ("PLAYING",
"PAUSED"). Sound →
**Voices** in Setup is its volume (Left/Right) and on/off (Enter), kept as `voices` and `voice_volume` in
`[tyrian3d]`; "No voices installed" when there are none. With Sound → **Cube Autoplay** (on by default,
`cube_autoplay`) a data cube picked up in a level is read aloud there and then, once the game's "Data acquired" has
been said: the cube the store after the level shows in its place, found by the store's list (`]?`) in the episode's
sections ahead (`upcoming_cube`; not in network games or demos); and the store reads its cubes aloud one after
another as it opens, each once a visit, passing over those already read in the level; a cube opened in the reader
plays at once, and when a voice ends while a reader is open the autoplay stops there.

The voices go in `data/voices` (in the repository, without the render cache and the previews; `TYR3D_VOICES_DIR`): `e<episode>/<cube>.wav` (the cube's
number in its episode's `cubetxt` file), `story/e<episode>_<n>.wav` and `manifest.txt`, which lists each
with the hash of the text it reads (32-bit FNV-1a over the cube's text lines or the story's
`levelWarningText` lines); the game plays a voice only over its own text, so an edited cube (episode 6's
are generated) or a custom episode's cubes stay silent. Any WAV SDL reads works; the render writes IMA
ADPCM, 24 kHz mono, -18 LUFS (`tools/package_macos.sh` copies them into the app when they are there).

Rendering them (ElevenLabs, the user's own subscription, a paid plan for voice design; the key is
read only from `ELEVENLABS_API_KEY`, the gitignored `.env.local` that `npx @elevenlabs/cli@latest
onboard connect --env-path .env.local` writes, or `~/.config/tyrian3d/elevenlabs_key`, and goes only
into the request header):

1. `python3 tools/voices/export_cubes.py` writes the script `data/voices/script.json` and the
   proofreading copy `script.html` from the game's data: 170 cubes (`E:N`; 190 with the Game Boy
   Color episode 7, `--episode7`), the 96 story texts and
   hints (`E:101`... in the order of the episode's script, the end's secret hints `E:201`...), split
   by speaker. `tools/voices/cast.json` has the speakers (28 designed voices; minor parts borrow one,
   `voice_of`), which cubes and stories each reads (`cube_rules`, by the same ids) and the voice
   prompts; `pronunciation.json` the names' readings.
2. `python3 tools/voices/generate.py estimate` (no network): characters, minutes, credits and the plan
   (about 134,000 characters, 140-163 minutes). `status` shows the account's credits.
3. `generate.py design [--speaker K]` makes three previews per voice in `data/voices/previews/`;
   `adopt K N` makes the one chosen the speaker's voice (its `voice_id` in `cast.json`).
4. `generate.py generate [--only E:N,...] [--jobs 4]` renders what is not in the render cache
   (`data/voices/cache`, keyed by text, voice and settings: a changed line renders again alone) and
   builds the WAVs and the manifest; `--retake E:N[:S]` renders a cube or segment again;
   `generate.py build` rebuilds from the cache without the network.

Rendered 2026-10-25 with `eleven_v4` (about 0.44 credits a character; about 69,000 credits with the voice
design): all 170 cubes and the 96 story texts and hints, about 140 minutes, 100 MB of WAVs, with the
render cache (about 400 MB) beside them in `data/voices`. The voices chosen are in `cast.json` (`voice_id`,
`adopted_preview`); the account's 30 custom voices hold the 28 and the user's own. The Game Boy Color
episode's 20 cubes (episode 7, from `assets/content/episode7`;
local corrections such as 7:11's "your're" in `data/voices/overrides.json`) were rendered 2026-10-26 with the
same voices (3,180 credits), its story text and end hints on the same day (207 credits; the 8 hints are 3 texts
repeated, and a voice is found by its text, so 3 were rendered).
another take of a cube is `generate.py generate --retake E:N`, a speaker's tempo its `settings.speed`
and `generate.py build --only ...` (from the cache, free).

`tools/voices/say_placeholders.py --out DIR --only 1:1,1:101 --stories` makes placeholder voices with
macOS's `say` (no account), to try the playback with `TYR3D_VOICES_DIR=DIR`.

## Roadmap

1. ~~PoC 1: the original sprites in 3D.~~
2. ~~PoC 2: placeholder CC0 models (Kenney Space Kit) for enemies and the player.~~
3. ~~Volumetric sprites for every enemy and player ship; per-enemy appearance rules with yaw modes.~~
4. ~~Background maps drawn for everything the 3D camera sees.~~
5. Next steps (see `docs/plans/2026-10-07-tyrian3d-plan.md`):
   - ~~Shadows from models onto the ground layer.~~
   - Models for shots and power-ups; explosions as particles (started: `src/particles3d.c` adds a
     flash, sparks, smoke and debris to every explosion).
   - ~~Upside-down levels (`starShowVGASpecialCode` 1) and spotlight levels (2) in 3D.~~
   - Custom models matching the original sprites, and higher-resolution background tiles.

## Credits

See `LICENSES.md` for the licenses (the macOS app has them in `Contents/Resources/licenses`).

- Tyrian: Eclipse Software / Jason Emery (freeware data).
- OpenTyrian / OpenTyrian2000: the OpenTyrian team and Kaito Sinclaire (GPL-2.0).
- Placeholder models: Kenney Space Kit, CC0 (`assets/models/kenney-space-kit/License.txt`).
- Music synth: TinySoundFont by Bernhard Schelling, MIT (`external/tinysoundfont/LICENSE`).
- SoundFont: GeneralUser GS by S. Christian Collins, free to use (in the repository with its license,
  `data/soundfonts`; the game also plays through any other `.sf2` put there).
- Sound effect upscaling: AudioSR by Haohe Liu et al. (run locally; the results are in `data/tyrian2000/sfx`).
- Voices of the data cubes and story texts: ElevenLabs text to speech (rendered with the user's own
  subscription by `tools/voices/generate.py`; in `data/voices`).
