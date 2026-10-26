/*
 * Tyrian3D: the secrets the player has found, and the title menu's Secrets screen that lists them: what is
 * found, and what is still locked (with a hint where to look). Each is kept in the user directory's
 * tyrian3d_secrets.cfg the moment the game reveals it ("found <id>" lines). Nothing is recorded in a demo,
 * a rogue run, a custom episode, or a dev run (TYR3D_START, TYR3D_TEST_KEYS...; TYR3D_SECRETS=1 records
 * anyway, for tests with their own XDG_CONFIG_HOME).
 */
#ifndef SECRETS_H
#define SECRETS_H

#include "opentyr.h"

// A level line of an episode's script read (tyrian2.c ]L): its section (a secret level's, recorded).
void secrets_level(int episode, int section);
// A shop opened (]I) in that section (episode 4's after ?TUNNEL? sells the Stalker 21.126).
void secrets_shop(int episode, int section);
// A code typed at the title accepted: specialName's index (0-8 the Super Arcade ships, SA_DESTRUCT - 1,
// SA_ENGAGE - 1).
void secrets_code(int code);
// The difficulty menu shows that many difficulties (4: Impossible, 5: Suicide, 6: Lord of Game).
void secrets_difficulty(int shown);
// The store's data cubes (cube numbers in the episode's cubetxt file).
void secrets_cubes(int episode, const JE_word *cubes, int count);

// The Secrets screen (the title menu's).
void secrets_screen(void);

#endif // SECRETS_H
