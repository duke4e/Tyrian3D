/* 
 * OpenTyrian: A modern cross-platform port of Tyrian
 * Copyright (C) 2007-2009  The OpenTyrian Development Team
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
#ifndef NORTSONG_H
#define NORTSONG_H

#include "opentyr.h"

#include "musmast.h"
#include "sndmast.h"

#include <SDL3/SDL.h>

extern JE_word frameCountMax;

extern float nortsong_time_scale;  // Tyrian3D: delays this many times as long (the debug flight's speed)
extern bool nortsong_skip_waits;   // Tyrian3D: no waiting (the debug flight's replay)
extern float nortsong_tick_pace;   // Tyrian3D: a level's ticks this many times as long (setTickDelay*)

extern Sint16 *soundSamples[SOUND_COUNT];
extern size_t soundSampleCount[SOUND_COUNT];

extern JE_word tyrMusicVolume, fxVolume;
extern const JE_word fxPlayVol;
extern JE_word tempVolume;

void setDelay(int delay);
// Tyrian3D: a delay that starts where the last one ended, so the game keeps its pace while the
// 3D view waits for ticks; and how much of the current delay is left or gone.
void setDelayContinued(int delay);
// Tyrian3D: a level's tick (nortsong_tick_pace times as long).
void setTickDelay(int delay);
void setTickDelayContinued(int delay);
Sint64 getDelayLeftNS(void);
float getDelayProgress(void);
void wait_delay_precise(void);
void setDelay2(int delay);
Uint32 getDelayTicks(void);
Uint32 getDelayTicks2(void);

void wait_delay(void);
void service_wait_delay(void);
void wait_delayorinput(void);

void setDelaySpeed(Uint16 speed);

void JE_changeVolume(JE_word *music, int music_delta, JE_word *sample, int sample_delta);

void loadSndFile(bool xmas);
void JE_playSampleNum(JE_byte samplenum);

#endif /* NORTSONG_H */
