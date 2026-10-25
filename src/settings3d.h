/*
 * Tyrian3D: the player's 3D settings (plan M4.3), set in the setup menu ("3D...") and kept in
 * the [tyrian3d] section of opentyrian.cfg. Environment variables (TYR3D_2D, TYR3D_NO_MODELS,
 * TYR3D_SHADOWS, TYR3D_TILT, TYR3D_VOICES, ...) override them for a run.
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
	bool effects;   // particles and the glow of shots
	int camera;     // a camera preset (settings3d_camera_name)
	bool music_midi;  // the music through a SoundFont as MIDI (else the emulated OPL chip)
	bool mouse_direct;  // the mouse moves the ship as far as it moves (else as in the original)
	bool hud_modern;    // a few gauges over the scene (else the original panel beside it)
	bool playfield_wide;  // the 3D view's wide playfield (l3d_field_wide), from the next level on
	bool menus_modern;    // the menus in the new style over the 3D view (ui.h), else the original screens
	bool screens_fill;    // with them, the old 320x200 screens fill the window's height (else as Scaling Mode says)
	int ui_scale;         // the size of the menus and the HUD, per cent (settings3d_ui_scale_*)
	char soundfont[64];   // the SoundFont the music plays through, by name (music_midi_use; "" the default)
	bool voices;          // the data cubes and story texts read aloud (voiceover.h)
	int voice_volume;     // their volume, 0-255 (as the music's and the samples')
} Settings3D;

extern Settings3D settings3d;

int settings3d_camera_count(void);
const char *settings3d_camera_name(int preset);

// The UI scale's choices (per cent): count, the i-th, and which one a value is (nearest).
int settings3d_ui_scale_count(void);
int settings3d_ui_scale_value(int i);
int settings3d_ui_scale_index(int percent);

// Reads the settings from their section (NULL: defaults), then the environment's overrides.
void settings3d_load(const ConfigSection *section);
void settings3d_save(ConfigSection *section);

// Makes the settings take effect (view, models, camera, music).
void settings3d_apply(void);

typedef enum { S3D_VIEW, S3D_MODELS, S3D_SHADOWS, S3D_EFFECTS, S3D_CAMERA, S3D_MUSIC, S3D_MOUSE, S3D_HUD, S3D_PLAYFIELD, S3D_MENUS,
               S3D_SCREENS, S3D_UI_SCALE, S3D_SOUNDFONT, S3D_VOICES } Settings3DField;

// To be called when the player changed a setting (menu, F3, F4): it is saved as it is, whatever
// the environment overrode.
void settings3d_changed(Settings3DField field);

#endif /* SETTINGS3D_H */
