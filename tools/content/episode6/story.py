"""Episode 6's story and shops: the stages (a shop, then a level), the data cubes, the ending
(docs/plans/2026-10-09-epizoda-6.md). build.py writes them into the episode's script and cube
files; a stage whose level isn't generated yet is left out.

Shop lines are the script's ]I lists: ships, front guns, rear guns, generators ("Power"),
engines and armor (not used by the game), left and right sidekicks, shields; numbers as the item
data has them (episode 5's, plus the new items of assets/content/items.cfg: ports 48-53,
sidekicks 33-37).
"""

# Each stage: its level (levels/<slug>.json), the planet the map flies to, the cubes the shop
# shows (indices in CUBES, from 1), a message before the level (or None), and the shop.
STAGES = [
    dict(level="dig_site", planet=8, cubes=[1], warning=None, shop=[
        " Ship   3 14 16", " WeapF  1 3 13 48 49", " WeapR  0 9 10 52 53", " Power  3 4", " Engine 1",
        " Opt1   0 6 29 33", " Opt2   0 6 29 34", " Armor  1 2 3", " Shield 3 5 8"]),
    dict(level="reef", planet=8, cubes=[2, 9], warning=None, shop=[
        " Ship   4 5 16", " WeapF  8 13 17 50", " WeapR  0 9 18 28 52", " Power  4 5", " Engine 1",
        " Opt1   0 16 13 14 35", " Opt2   0 20 13 14 36", " Armor  1 2 3", " Shield 5 6 8"]),
    dict(level="grey_moon", planet=12, cubes=[3], warning=["Warning:", "The grey moon's base answers no hails.",
                                                           "Its guns are already turning."], shop=[
        " Ship   5 6 2", " WeapF  3 27 42 51", " WeapR  0 21 22 30 53", " Power  5", " Engine 1",
        " Opt1   0 7 8 9 37", " Opt2   0 7 8 9 37", " Armor  1 2 3", " Shield 6 7 9"]),
    dict(level="deli_ruin", planet=3, cubes=[10], warning=None, shop=[
        " Ship   5 6 16", " WeapF  3 8 27 42 51", " WeapR  0 21 22 30 53", " Power  5", " Engine 1",
        " Opt1   0 7 8 12 37", " Opt2   0 7 8 12 37", " Armor  1 2 3", " Shield 6 7 9"]),
    dict(level="roost", planet=2, cubes=[4], warning=None, shop=[
        " Ship   6 7 2", " WeapF  5 18 19 48 49", " WeapR  0 28 29 21", " Power  5 6", " Engine 1",
        " Opt1   0 12 17 21 33 35", " Opt2   0 12 22 23 34 36", " Armor  1 2 3", " Shield 9 10"]),
    dict(level="deep_ice", planet=14, cubes=[5], warning=None, shop=[
        " Ship   7 6 2", " WeapF  5 20 27 50 51", " WeapR  0 29 21 22 52", " Power  6", " Engine 1",
        " Opt1   0 12 17 25 37", " Opt2   0 12 26 27 37", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="glacier", planet=14, cubes=[6], warning=["Warning:", "Hazudra Collector signal ahead.",
                                                         "It has noticed you."], shop=[
        " Ship   7 12 2", " WeapF  5 18 19 20 27", " WeapR  0 21 28 29 53", " Power  6", " Engine 1",
        " Opt1   0 12 25 28 33 35", " Opt2   0 12 26 28 34 36", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="collector", planet=16, cubes=[11], warning=["Warning:", "The Collector's ship. It is larger",
                                                            "than any fleet you have seen."], shop=[
        " Ship   7 12 13", " WeapF  5 18 19 20 27 50", " WeapR  0 21 28 29 52", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 35", " Opt2   0 12 22 26 28 36", " Armor  1 2 3", " Shield 10 11"]),
    dict(level="crustgate", planet=6, cubes=[7, 8], warning=["Warning:", "Gravitron readings off every scale.",
                                                             "The crust is opening."], shop=[
        " Ship   7 12 13", " WeapF  5 18 20 27 42 48", " WeapR  0 21 28 29 52", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 37", " Opt2   0 12 22 26 28 37", " Armor  1 2 3", " Shield 11"]),
    dict(level="the_core", planet=6, cubes=[12], warning=["Warning:", "Gravitron core ahead.",
                                                          "The Collector is already there."], shop=[
        " Ship   7 12 13", " WeapF  5 18 20 27 42 48 51", " WeapR  0 21 28 29 52 53", " Power  6", " Engine 1",
        " Opt1   0 12 22 25 28 33 37", " Opt2   0 12 22 26 28 34 37", " Armor  1 2 3", " Shield 11"]),
]

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
