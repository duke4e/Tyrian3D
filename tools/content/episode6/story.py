"""Episode 6's story and shops: the stages (a shop, then a level), the data cubes, the ending
(docs/plans/2026-10-09-epizoda-6.md). build.py writes them into the episode's script and cube
files; a stage whose level isn't generated yet is left out.

Shop lines are the script's ]I lists: ships, front guns, rear guns, generators ("Power"),
engines and armor (not used by the game), left and right sidekicks, shields; numbers as the item
data has them (episode 5's, plus the new items of assets/content/items.cfg: ports 48-53,
sidekicks 33-37).
"""

# Each stage: its level (levels/<slug>.json), the planet the map flies to, the cubes the shop
# shows (indices in CUBES, from 1), a message before the level (or None), and the shop; secret:
# the data cube a courier of its level leaves (shown in the next shop when it was picked up).
# kind "secret": a level only a warp orb leads to (its parent's), back to the stage after its
# parent; kind "bonus": a level after the one before it, without a shop. Their cubes (secret ones,
# picked up in them) show in the next shop. Few have a message (the user, 2026-11-03, of one before
# nearly every level: "sad već zbilja imamo previše tih warninga u ovoj epizodi"): VAULT's, where the
# orb took you; MIGRATION's, the dragons and the first flight seen from the side; THE CORE's, the end.
WARNING_PICTURE = 5  # what the messages show over (]P): the planet in space, as nearly all the originals' do
STAGES = [
    dict(level="dig_site", planet=8, cubes=[1], secret=[13], warning=None, shop=[
        " Ship   3 14 16", " WeapF  1 3 13 48 49", " WeapR  0 9 10 52 53", " Power  3 4", " Engine 1",
        " Opt1   0 6 29 33", " Opt2   0 6 29 34", " Armor  1 2 3", " Shield 3 5 8"]),
    dict(level="reef", planet=8, cubes=[2, 9], secret=[14], warning=None, shop=[
        " Ship   4 5 16", " WeapF  8 13 17 50", " WeapR  0 9 18 28 52", " Power  4 5", " Engine 1",
        " Opt1   0 16 13 14 35", " Opt2   0 20 13 14 36", " Armor  1 2 3", " Shield 5 6 8"]),
    dict(level="grey_moon", planet=12, cubes=[3], warning=None, shop=[
        " Ship   5 6 2", " WeapF  3 27 42 51", " WeapR  0 21 22 30 53", " Power  5", " Engine 1",
        " Opt1   0 7 8 9 37", " Opt2   0 7 8 9 37", " Armor  1 2 3", " Shield 6 7 9"]),
    dict(level="vault", kind="secret", parent="grey_moon", cubes=[], secret=[21, 22],
         warning=["The orb pulls you off course, down a shaft", "in the grey moon, into a sealed vault."]),
    dict(level="deli_ruin", planet=3, cubes=[10], secret=[15], warning=None, shop=[
        " Ship   5 6 16", " WeapF  3 8 27 42 51", " WeapR  0 21 22 30 53", " Power  5", " Engine 1",
        " Opt1   0 7 8 12 37", " Opt2   0 7 8 12 37", " Armor  1 2 3", " Shield 6 7 9"]),
    dict(level="roost", planet=2, cubes=[4], secret=[16], warning=None, shop=[
        " Ship   6 7 2", " WeapF  5 18 19 48 49", " WeapR  0 28 29 21", " Power  5 6", " Engine 1",
        " Opt1   0 12 17 21 33 35", " Opt2   0 12 22 23 34 36", " Armor  1 2 3", " Shield 9 10"]),
    dict(level="migration", planet=2, cubes=[23], secret=[25], warning=[
        "Warning:", "The dragons' flight is crossing the system.", "Fly with it, side by side."], shop=[
        " Ship   6 7 2", " WeapF  5 18 19 48 49 50", " WeapR  0 28 29 21 52", " Power  5 6", " Engine 1",
        " Opt1   0 12 17 21 33 35", " Opt2   0 12 22 23 34 36", " Armor  1 2 3", " Shield 9 10"]),
    dict(level="deep_ice", planet=14, cubes=[5], secret=[17], warning=None, shop=[
        " Ship   7 6 2", " WeapF  5 20 27 50 51", " WeapR  0 29 21 22 52", " Power  6", " Engine 1",
        " Opt1   0 12 17 25 37", " Opt2   0 12 26 27 37", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="glacier", planet=14, cubes=[6], secret=[18], warning=None, shop=[
        " Ship   7 12 2", " WeapF  5 18 19 20 27", " WeapR  0 21 28 29 53", " Power  6", " Engine 1",
        " Opt1   0 12 25 28 33 35", " Opt2   0 12 26 28 34 36", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="collector", planet=16, cubes=[11], secret=[19], warning=None, shop=[
        " Ship   7 12 13", " WeapF  5 18 19 20 27 50", " WeapR  0 21 28 29 52", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 35", " Opt2   0 12 22 26 28 36", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="crustgate", planet=6, cubes=[7, 8], secret=[20], warning=None, shop=[
        " Ship   7 12 13", " WeapF  5 18 20 27 42 48", " WeapR  0 21 28 29 52", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 37", " Opt2   0 12 22 26 28 37", " Armor  1 2 3", " Shield 11"]),
    dict(level="gravitron", planet=6, cubes=[24], secret=[26], warning=None, shop=[
        " Ship   7 12 13", " WeapF  5 18 20 27 42 48", " WeapR  0 21 28 29 52 53", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 37", " Opt2   0 12 22 26 28 37", " Armor  1 2 3", " Shield 11"]),
    dict(level="the_core", planet=6, cubes=[12], warning=["Warning:", "Gravitron core ahead.",
                                                          "The Collector is already there."], shop=[
        " Ship   7 12 13", " WeapF  5 18 20 27 42 48 51", " WeapR  0 21 28 29 52 53", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 33 37", " Opt2   0 12 22 26 28 34 37", " Armor  1 2 3", " Shield 11"]),
]

# (kit: flown with the mini-game's weapons, as the originals' mini-games are, the ship's own back after it: ]k[,
# tyrian2.c kit_restore)
STAGES.append(dict(level="invaders", kind="bonus", cubes=[], warning=None, kit=True))  # (">>> Bonus Level <<<" in it)
# The last two (generate.py): STARFALL, the Collector's fleet chased low over the farmland, seen from behind the
# ship; THE HOARD, its bosses one after another. Their shops sell the best the episode has.
LAST_SHOP = [" Ship   7 12 13", " WeapF  5 18 20 27 42 48 50 51", " WeapR  0 21 28 29 52 53", " Power  6", " Engine 1",
             " Opt1   0 12 22 25 28 33 35 37", " Opt2   0 12 22 26 28 34 36 37", " Armor  1 2 3", " Shield 11"]
STAGES.append(dict(level="starfall", planet=6, cubes=[], warning=None, shop=LAST_SHOP))
STAGES.append(dict(level="the_hoard", planet=6, cubes=[], warning=None, shop=LAST_SHOP))
STAGES.append(dict(level="hoard_ii", planet=6, cubes=[], warning=None, shop=LAST_SHOP))  # (THE HOARD's second half)

# The specials each shop sells (the shop's 10th list, " Spec": game_menu.c shop_has_specials, mainint.c
# special_shop_cost; the user, 2026-11-04: "u 6. epizodi bi zapravo u shop i mogli dodati speciale tipa flare"), 0 for
# none, the weaker first: the Repulsor and the Attractor, then the beams and the Flare, the fields, the zones, the
# Lightning Zone and at the end the Nova (ROOST's courier gives one early) and the Dragon Lightning.
SPECIALS = {
    "dig_site": [0, 1, 4], "reef": [0, 1, 4, 5], "grey_moon": [0, 5, 6], "deli_ruin": [0, 6, 2],
    "roost": [0, 6, 2, 7], "migration": [0, 2, 7, 8], "deep_ice": [0, 7, 8, 45], "glacier": [0, 8, 45, 13],
    "collector": [0, 13, 14, 47], "crustgate": [0, 14, 47, 40], "gravitron": [0, 40, 41, 49], "the_core": [0, 40, 49, 48],
    "starfall": [0, 49, 48], "the_hoard": [0, 49, 48], "hoard_ii": [0, 49, 48],
}

# The data cubes: (face sprite, title, header, lines). ~word~ highlights a word, as in the game.
CUBES = [
    (17, "INCOMING MESSAGE FROM HAZUDRA : 93102 mark", "Collector", [
        "Greetings again, ~Trent~. We trust the quiet has been restful.",
        "",
        "You will have noticed that the device on your ship is awake once more. Do not",
        "be alarmed. We ask only one last service, and then it sleeps for good.",
        "",
        "On ~Savara~, the scientist ~Graphim~ ~Arugo~ has dug up books of a grey material,",
        "from a world called ~Earth~. Unmarked ships are on their way to take them.",
        "Keep the books safe. Keep him alive. We will be watching."]),
    (1, "DATACUBE: ARUGO FIELD LOG 1", "Data", [
        "The first pages are not stories. They are maintenance tables.",
        "",
        "Schedules, load figures, a diagram that matches ~Tyrian's~ ~gravitron~ ~crust~",
        "layer for layer. Whoever wrote these did not study the crust. They built it.",
        "",
        "And a word I cannot place, on every page: ~keepers~."]),
    (2, "DATACUBE DISPATCH 0517:SV-818", "News", [
        "Report, L-line Agents, stream 77",
        "",
        "The ships that struck the ~Savara~ dig were traced to an old mining moon in the",
        "~Grey~ ~Belt~. The station there was sealed decades ago. Its lights came back on",
        "three weeks before the attack."]),
    (2, "ARCHIVE DATA", "Data", [
        "Reference: Torm Biology - Dragon (update)",
        "",
        "The dragons of ~Torm~ have left their nests, all of them, on the same day.",
        "Their flight path runs straight out of the system, toward coordinates that",
        "match a line in the grey books: ~the~ ~keepers'~ ~gate~."]),
    (1, "DATACUBE: ARUGO FIELD LOG 2", "Data", [
        "I have it now. ~Tyrian~ is not a planet that grew a strange crust. The crust",
        "came first, a shell built around something, and a world grew on top of it.",
        "",
        "The books call the builders ~keepers~. The machine that holds the shell",
        "together sits under the ice of ~Ixmucane~ and the lava of the deep crust.",
        "Someone is taking it apart, piece by piece."]),
    (18, "INTERCEPTED: HAZUDRA BAND", "Collector", [
        "...seventh shard secured. The ~Collector~ moves to the glacier field.",
        "The human continues to be useful. He clears our way without knowing it.",
        "",
        "When the last shard is taken, the shell will fail. The device on his ship",
        "will no longer matter. Nothing on ~Tyrian~ will."]),
    (15, "RECORDING, 4 YEARS OLD", "Message", [
        "~Trent~, if this reaches you, I did not make it.",
        "",
        "My people are not collectors of art. They collect worlds. Not to keep: to",
        "open. I tried to stop them at the ~gate~. Do not trust their thanks.",
        "",
        "Your friend, ~Buce~."]),
    (1, "DATACUBE: ARUGO FIELD LOG 3", "Data", [
        "The last diagram shows the heart of the machine: the ~gravitron~ ~core~, where",
        "the shell is anchored. If the ~Collector~ reaches it first, the crust falls in.",
        "",
        "Go down through the ~gate~. I will keep reading."]),
    (13, "HAVE YOU SEEN MY OVENS?", "Alert", [
        "This is ~Baker~ ~Bob~ again. After the pretzel incident, the ~Twister~ ~Bakers~",
        "were rebuilt, repainted and stolen AGAIN. If you see three flying ovens",
        "heading for ~Savara~, please do not shoot them. Unless they shoot first.",
        "They will shoot first."]),
]

CUBES += [
    (14, "HOLO NEWS - GD3 v123-07-30", "News", [
        "~Deliani~ ~Ruins~ ~Reopened~",
        "",
        "The old quarter of ~Deliani~, empty since the war with the ~Vykromod~, has been",
        "reoccupied by unknown forces. Residents report grey ships landing at night and",
        "crates of strange equipment carried below the city."]),
    (18, "INCOMING MESSAGE FROM HAZUDRA : 99999 mark", "Collector", [
        "You have done well, ~Trent~. Too well. We had hoped you would understand.",
        "",
        "Every world is a shell around a seed. We open them. It is what we are for.",
        "Come to our ship if you wish. You will not leave it."]),
    (1, "DATACUBE: ARUGO FIELD LOG 4", "Data", [
        "The ~Collector~ has reached the core. The shell is already shaking; the",
        "readings jump every hour.",
        "",
        "Destroy it there, ~Trent~, before it opens the seed. Whatever is inside",
        "the keepers wanted to stay inside."]),
]

# Secret cubes: one a courier carries in most levels, two in the vault (STAGES' "secret").
CUBES += [
    (1, "DATACUBE: SAVARA DIG CREW NOTES", "Data", [
        "Day 12. The books will not burn, tear or get wet. Mill tried all three.",
        "",
        "Day 13. ~Arugo~ says that is the point: they were made to outlast whoever",
        "reads them. Mill says he was only checking. Nobody believes Mill.",
        "",
        "Day 14. Unmarked ships on the scanner. Packing the books first, Mill second."]),
    (2, "SAVARA COAST WATCH, NIGHT LOG", "News", [
        "Fishing boats off the ~Savara~ reef report grey hulls under the water, moving",
        "in lines, with no lights. The reef fish have gone deep and will not come up.",
        "",
        "The coast watch reminds all crews: do not follow anything grey."]),
    (14, "DELIANI PROPERTY EXCHANGE", "News", [
        "~For~ ~lease~: the old quarter, ruins included. Quiet neighbours, mostly grey.",
        "Basement levels already occupied; the occupants did not sign anything and",
        "have stopped answering the door.",
        "",
        "Rent payable in advance. Bring your own lights."]),
    (2, "ARCHIVE DATA", "Data", [
        "Reference: Torm Biology - Dragon Eggs",
        "",
        "The dragons left their eggs behind. The eggs are warm, though nothing sits",
        "on them, and every one of them turns slowly to face the same point in the",
        "sky: the ~keepers'~ ~gate~."]),
    (1, "ICE CORE SAMPLE 4412", "Data", [
        "Depth 900 m: a layer of grey dust, the same material as the books.",
        "Depth 1400 m: the dust is laid in lines, like writing.",
        "Depth 2100 m: the drill head comes back warm. The ice down there hums.",
        "",
        "Drilling suspended. The hum has not."]),
    (18, "HAZUDRA DUTY ROSTER", "Collector", [
        "Shard team: three. Shell team: seven. Watching the human: one.",
        "",
        "Note to the one watching the human: you are not to admire his flying.",
        "Report the facts. The facts are bad enough."]),
    (17, "THE COLLECTOR'S CATALOGUE (EXCERPT)", "Collector", [
        "World 31: opened. World 32: opened. World 33: opened, found empty.",
        "World 34: opened, did not stay opened. World 35: ~Tyrian~, in progress.",
        "",
        "Remark on world 34: we will not speak of world 34."]),
    (1, "FROM THE GREY BOOKS, TRANSLATED", "Data", [
        "~To~ ~whoever~ ~comes~ ~after~:",
        "",
        "We did not build the shell to keep you out. We built it to keep it in.",
        "Mend the shell. Do not open the seed. It is not empty, and it is not asleep.",
        "",
        "~The~ ~keepers~"]),
    (14, "VAULT LEDGER, GREY BELT STATION", "Data", [
        "Credits taken from the ~Savara~ dig: all. From the ~Deliani~ banks: most.",
        "Purpose of the money: hiring pilots who ask no questions.",
        "",
        "Note: the pilots asked questions. The money stays here for now."]),
    (1, "DATACUBE: ARUGO, A PAGE NOBODY SAW", "Data", [
        "One page of the books was cut out before they reached me. Its shape is in the",
        "binding: a circle around a circle. The ~keepers'~ mark for the seed.",
        "",
        "Whoever cut it out knew what it said. I think they were afraid of it.",
        "I think I would be too."]),
]

# Cubes of the levels seen from the side: their own (23, 24) and their couriers' (25, 26).
CUBES += [
    (2, "ARCHIVE DATA", "Data", [
        "Reference: Torm Biology - Dragon Flight",
        "",
        "A dragon flight in open space is not supposed to be possible. They hold their",
        "breath, close their scales and glide on the solar wind for weeks.",
        "",
        "Pilots are advised to fly alongside, not through. They do not turn for ships."]),
    (1, "DATACUBE: ARUGO FIELD LOG 5", "Data", [
        "Below the crust the books' diagrams turn on their side: the keepers built",
        "their shafts across, not down, so the shell would not fall in if one broke.",
        "",
        "You will be flying sideways through a world, ~Trent~. Mind the walls."]),
    (13, "BAKER BOB'S FLIGHT NOTES", "Alert", [
        "Followed the dragons for a day to see where they go. They go fast.",
        "Lost two ovens and my hat. The dragons ate the hat.",
        "",
        "Recipe for dragon-safe pretzels to follow, once I find a dragon that is safe."]),
    (18, "INTERCEPTED: HAZUDRA BAND", "Collector", [
        "The keepers' shafts are open. The human flies them faster than our drills.",
        "",
        "Let him. Every wall he passes is one we will not have to break."]),
]

ENDING = [
    "The Collector falls into the crust it came to break.",
    "",
    "Graphim Arugo seals the gate behind you. The grey books stay",
    "with him; the keepers' machine holds, for now.",
    "",
    "The device on your ship falls silent. This time, you take",
    "it out yourself.",
]

HINTS = [
    ["Did you know?", "Tyrian purple, the dye, took thousands of sea snails", "for a single gram."],
    ["Did you know?", "Purple orbs are experience in a rogue run."],
    ["Did you know?", "Repulsors push you away; magnets pull you in."],
]
