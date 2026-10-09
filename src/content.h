/*
 * Tyrian3D: new content (weapons, weapon ports, sidekicks, specials) from assets/content/items.cfg,
 * put into the item data's free slots each time the game loads it (JE_loadItemDat), so the original
 * items stay as they are:
 *
 *   weapons    819-999   (the gap between the data's two banks, 0-818 and 1000-1818)
 *   ports      48-60     (the data's "Test" ports)
 *   sidekicks  33-37
 *   specials   49-54
 *
 * The file's lines (# starts a comment; values are numbers, lists of numbers separated by commas,
 * or "quoted text"):
 *
 *   weapon <id> [copy=<id>] shotrepeat= multi= weapani= max= tx= ty= aim= acceleration=
 *          accelerationx= circlesize= sound= trail= shipblastfilter= attack= del= sx= sy= bx= by= sg=
 *          (the last seven: up to 8 values, one per sub-shot)
 *   port <id> [copy=<id>] name= opnum= op1= op2= cost= graphic= poweruse=
 *          (op1, op2: the weapons of the 11 power levels in mode 1 and 2)
 *   sidekick <id> [copy=<id>] name= pwr= graphic= cost= tr= option= opspd= ani= gr= wport= wpnum=
 *          ammo= stop= icongr=
 *   special <id> [copy=<id>] name= graphic= pwr= stype= wpn=
 *
 * copy= starts from another item (of the data as loaded: episodes 1-3 and 4-5 differ).
 */
#ifndef CONTENT_H
#define CONTENT_H

#include "opentyr.h"

#define CONTENT_WEAPON_FIRST 819
#define CONTENT_WEAPON_LAST 999
#define CONTENT_PORT_FIRST 48
#define CONTENT_SIDEKICK_FIRST 33
#define CONTENT_SPECIAL_FIRST 49

void content_apply(void);

#endif /* CONTENT_H */
