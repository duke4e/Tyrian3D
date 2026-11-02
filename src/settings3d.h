/*
 * Tyrian3D: the player's 3D settings (plan M4.3), set in the setup menu ("3D...") and kept in
 * the [tyrian3d] section of opentyrian.cfg. Environment variables (TYR3D_2D, TYR3D_NO_MODELS,
 * TYR3D_SHADOWS, TYR3D_SSAO, TYR3D_SHAKE, TYR3D_TILT, TYR3D_VOICES, ...) override them for a run.
 */
#ifndef SETTINGS3D_H
#define SETTINGS3D_H

#include "opentyr.h"

#include "config_file.h"

typedef struct
{
	bool view_3d;   // the 3D view (else the original 2D screen); F3 toggles it
	bool models;    // models and generated volume (else flat sprites); F4 toggles it
	bool shadows;
	bool ssao;      // screen-space ambient occlusion: contact darkening under what stands, in hollows (render_gpu.c)
	bool effects;   // particles and the glow of shots
	bool shake;     // the view shakes at big blasts near the ship and at hits (p3d_shake; Destruct's too)
	int camera;     // a camera preset (settings3d_camera_name)
	bool music_midi;  // the music through a SoundFont as MIDI (else the emulated OPL chip)
	bool mouse_direct;  // the mouse moves the ship as far as it moves (else as in the original)
	int sidekick_fire;  // sidekicks with charge stages and endless ammo, with the main fire (settings3d_sidekick_fire_name)
	bool special_auto;  // the special weapon (the Flare's kind) fires again whenever it's ready while fire is held (else a
	                    // press each, as the original); not in network games and demos
	bool hud_modern;    // a few gauges over the scene (else the original panel beside it)
	bool playfield_wide;  // the 3D view's wide playfield (l3d_field_wide), from the next level on
	bool menus_modern;    // the menus in the new style over the 3D view (ui.h), else the original screens
	bool screens_fill;    // with them, the old 320x200 screens fill the window's height (else as Scaling Mode says)
	int ui_scale;         // the size of the menus and the HUD, per cent (settings3d_ui_scale_*)
	char soundfont[64];   // the SoundFont the music plays through, by name (music_midi_use; "" the default)
	bool voices;          // the data cubes and story texts read aloud (voiceover.h)
	int voice_volume;     // their volume, 0-255 (as the music's and the samples')
	bool cube_autoplay;   // the store reads its data cubes aloud one after another as it opens (voiceover.h)
	int pointer_size;     // the modern pointer's size, window points (settings3d_pointer_*)
	char jukebox_look[16];  // the jukebox's visuals' look, by name (jukebox3d.h; "" the first)
} Settings3D;

extern Settings3D settings3d;

int settings3d_camera_count(void);
const char *settings3d_camera_name(int preset);

// How the sidekicks that charge up (Tyrian 2000's charge stages: the Zica Supercharger's) and have endless ammo fire:
// only on their own key, as the original has it (S3D_SIDEKICK_HOLD), or by themselves while the main fire is held, at
// full charge (S3D_SIDEKICK_CHARGED) or as fast as they can, uncharged (S3D_SIDEKICK_RAPID). (The others fire with the
// main fire anyway, and those with ammo only on their key.)
enum { S3D_SIDEKICK_HOLD, S3D_SIDEKICK_CHARGED, S3D_SIDEKICK_RAPID, S3D_SIDEKICK_FIRE_COUNT };
const char *settings3d_sidekick_fire_name(int mode);

// The UI scale's choices (per cent): count, the i-th, and which one a value is (nearest).
int settings3d_ui_scale_count(void);
int settings3d_ui_scale_value(int i);
int settings3d_ui_scale_index(int percent);

// The pointer size's choices (window points): count, the i-th, its name, and which one a value is (nearest).
int settings3d_pointer_count(void);
int settings3d_pointer_value(int i);
const char *settings3d_pointer_name(int i);
int settings3d_pointer_index(int points);

// Reads the settings from their section (NULL: defaults), then the environment's overrides.
void settings3d_load(const ConfigSection *section);
void settings3d_save(ConfigSection *section);

// Makes the settings take effect (view, models, camera, music).
void settings3d_apply(void);

typedef enum { S3D_VIEW, S3D_MODELS, S3D_SHADOWS, S3D_EFFECTS, S3D_CAMERA, S3D_MUSIC, S3D_MOUSE, S3D_HUD, S3D_PLAYFIELD, S3D_MENUS,
               S3D_SCREENS, S3D_UI_SCALE, S3D_SOUNDFONT, S3D_VOICES, S3D_JUKEBOX, S3D_POINTER, S3D_SSAO, S3D_SHAKE,
               S3D_SIDEKICK_FIRE, S3D_SPECIAL_AUTO } Settings3DField;

// To be called when the player changed a setting (menu, F3, F4): it is saved as it is, whatever
// the environment overrode.
void settings3d_changed(Settings3DField field);

#endif /* SETTINGS3D_H */
