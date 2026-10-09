"""Episode 6's mini-game: INVADERS, a Space Invaders round after round, as the galaga game ALE is
at the end of episode 1 (docs/plans/2026-10-09-epizoda-6.md, 7).

The map stands still (event 2 with 0, the clock running on: 53). Each round puts a formation of
enemies on the screen, each on its own link (an enemy's link dies with it, so a row on one link
would go at the first hit), moves it as the invaders move (across, a step down, back, a step down:
event 19 for each link, round after round by a jump back, 54), lets them fire now and then (31)
and leave coins (33), and sends a saucer across the top (a top layer enemy, its own link, a gem).
When no enemy of links 1-19 is left (event 70), the next round; after the last, the level ends.
"""
import random

from compose import event

ROUNDS = [
    # (rows of enemies, top row first (episode 5's item data), speed in px per tick, fire periods)
    ([163, 164, 167], 1, (260, 420)),
    ([133, 129, 164], 1, (220, 380)),
    ([743, 296, 340], 1, (200, 340)),
    ([202, 293, 296], 2, (180, 300)),
    ([169, 133, 743], 2, (150, 260)),
]
SAUCER = 339         # EYESPY's eye: worth a big gem
COLUMNS = 6
SPACING = 34
ROW_Y = (30, 58, 86)
SWING = 30           # px either way of the middle
STEP = 8             # ticks of a step down (1 px a tick)
ROUND_LENGTH = 1500  # clock between rounds' starts (a round's loop stays inside it)
SAUCER_LINK = 30
COINS = (392, 393, 394, 395)  # 50-250 credits an invader
GEM = 398                     # 2500 credits, the saucer's


def invaders(seed=1):
    """The level's events (enemies of episode 5)."""
    rnd = random.Random(seed)
    x0 = (264 - (COLUMNS - 1) * SPACING - 24) // 2
    events = [event(0, 2), event(0, 53), event(60, 16, d1=9, d2=30)]  # "bonus level"
    t = 200
    for k, (rows, speed, fire) in enumerate(ROUNDS):
        links = []
        for r, enemy in enumerate(rows):
            for c in range(COLUMNS):
                link = len(links) + 1
                links.append(link)
                # Sky enemies: x is d2, y is -28 + d5.
                events += [event(t, 15, d1=enemy, d2=x0 + c * SPACING, d4=link, d5=ROW_Y[r] + 28, ep=5),
                           event(t, 20, d1=0, d2=0, d4=link), event(t, 19, d1=0, d2=0, d4=link),
                           event(t, 31, d1=0, d2=0, d3=0, d4=link),  # quiet until its turn
                           event(t, 33, d1=rnd.choice(COINS[:2 + k // 2]), d4=link, ep=5),
                           event(t + rnd.randint(40, 200), 31, d1=rnd.randint(*fire), d2=0, d3=0, d4=link)]
        # The saucer: a top layer enemy (its x is d2 - 66), right to left or left to right.
        left = k % 2 == 0
        saucer_t = t + 300
        events += [event(saucer_t, 7, d1=SAUCER, d2=66 - 30 if left else 66 + 270, d4=SAUCER_LINK, d5=34, ep=5),
                   event(saucer_t, 20, d1=0, d2=0, d4=SAUCER_LINK),
                   event(saucer_t, 19, d1=2 if left else -2, d2=0, d4=SAUCER_LINK),
                   event(saucer_t, 33, d1=GEM, d4=SAUCER_LINK, ep=5)]
        # The march: from the middle to the right, then (the loop) down, left across, down, right
        # across; the round is checked at every turn.
        go = SWING // speed
        start = saucer_t + 10
        loop = start + go
        moves = [(start, speed, 0), (loop, 0, 1), (loop + STEP, -speed, 0), (loop + STEP + 2 * go, 0, 1),
                 (loop + 2 * STEP + 2 * go, speed, 0)]
        end = loop + 2 * STEP + 4 * go
        next_round = t + ROUND_LENGTH
        assert end < next_round - 20
        for when, dx, dy in moves:
            events += [event(when, 19, d1=dx, d2=dy, d4=link) for link in links]
            events.append(event(when, 70, d1=next_round - 10))
        events += [event(end, 70, d1=next_round - 10), event(end, 54, d1=loop)]
        # Between rounds: what is left of the last one (coins) falls away.
        t = next_round
    events += [event(t - 10, 16, d1=4, d2=30), event(t + 100, 11)]
    return sorted(events, key=lambda e: e["t"])
