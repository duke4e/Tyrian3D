/*
 * Tyrian3D: the data cubes and the story texts read aloud (tools/voices renders them with
 * ElevenLabs). The voices directory (data/voices; TYR3D_VOICES_DIR) holds e<episode>/<cube>.wav and
 * story/e<episode>_<n>.wav, listed in manifest.txt with a hash of the text each one reads, so a voice plays
 * only over the text it was made from (an edited cube, a custom episode's own cubes: silence).
 *
 * A voice plays over the music, which is ducked meanwhile (loudness.c), while its text shows: the
 * store's data cube reader, a story text between levels. It stops when the text closes. Settings:
 * settings3d.voices and voice_volume (Setup, Sound, Voices); TYR3D_DEBUG_VOICES=1 prints each event.
 */
#ifndef VOICEOVER_H
#define VOICEOVER_H

#include "opentyr.h"

#include <SDL3/SDL.h>

// The text hash (32-bit FNV-1a over each line's bytes and a '\n'), as tools/voices computes it.
#define VOICEOVER_HASH_START 2166136261u
Uint32 voiceover_hash(Uint32 hash, const char *line);

// Whether there are voices (a manifest in the voices directory).
bool voiceover_installed(void);

// The data cube shown, each frame the store shows its menus: episode, the cube's number in its
// episode's cubetxt file and its text's hash; cube 0 when no cube is shown. A new cube's voice
// starts, the old one stops.
void voiceover_cube(int episode, int cube, Uint32 text_hash);

// A story text shown (levelWarningText): lines first..count-1 are what is read. Plays until
// voiceover_stop.
void voiceover_story(char (*lines)[61], int first, int count);

// Stops the voice (its text closed); voiceover_update frees what has finished.
void voiceover_stop(void);
void voiceover_update(void);

// The voice volume or the on/off setting changed (settings3d): applied at once.
void voiceover_settings_changed(void);

#endif /* VOICEOVER_H */
