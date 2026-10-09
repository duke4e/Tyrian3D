/*
 * Tyrian3D: the player's 3D settings. See settings3d.h.
 */
#include "settings3d.h"

#include "layer3d.h"
#include "models3d.h"
#include "music_midi.h"
#include "render_gpu.h"
#include "video.h"

#include <SDL3/SDL.h>

#include <string.h>

Settings3D settings3d = { .view_3d = true, .models = true, .shadows = true, .effects = true, .camera = 0, .music_midi = true,
                          .mouse_direct = true, .hud_modern = true, .playfield_wide = true };

// The settings as the player chose them, which are saved: the environment's overrides only
// apply to settings3d, for the run.
static Settings3D chosen = { .view_3d = true, .models = true, .shadows = true, .effects = true, .camera = 0, .music_midi = true,
                             .mouse_direct = true, .hud_modern = true, .playfield_wide = true };
static bool overridden_view_3d, overridden_models, overridden_shadows, overridden_effects, overridden_music, overridden_mouse, overridden_hud,
            overridden_playfield;

static const struct
{
	const char *name;
	float tilt, fov;
} cameras[] = {
	{ "Standard", 20.0f, 30.0f },
	{ "Steep",    35.0f, 30.0f },
	{ "Overhead",  0.0f, 30.0f },
};

int settings3d_camera_count(void)
{
	return (int)COUNTOF(cameras);
}

const char *settings3d_camera_name(int preset)
{
	return cameras[SDL_clamp(preset, 0, (int)COUNTOF(cameras) - 1)].name;
}

void settings3d_load(const ConfigSection *section)
{
	if (section != NULL)
	{
		config_get_bool_option(section, "view_3d", &chosen.view_3d);
		config_get_bool_option(section, "models", &chosen.models);
		config_get_bool_option(section, "shadows", &chosen.shadows);
		config_get_bool_option(section, "effects", &chosen.effects);
		const char *music;
		if (config_get_string_option(section, "music", &music))
			chosen.music_midi = SDL_strcasecmp(music, "opl") != 0;
		const char *mouse;
		if (config_get_string_option(section, "mouse", &mouse))
			chosen.mouse_direct = SDL_strcasecmp(mouse, "original") != 0;
		const char *hud;
		if (config_get_string_option(section, "hud", &hud))
			chosen.hud_modern = SDL_strcasecmp(hud, "classic") != 0;
		const char *playfield;
		if (config_get_string_option(section, "playfield", &playfield))
			chosen.playfield_wide = SDL_strcasecmp(playfield, "original") != 0;
		const char *camera;
		if (config_get_string_option(section, "camera", &camera))
			for (int i = 0; i < (int)COUNTOF(cameras); ++i)
				if (SDL_strcasecmp(camera, cameras[i].name) == 0)
					chosen.camera = i;
	}
	settings3d = chosen;

	if ((overridden_view_3d = SDL_getenv("TYR3D_2D") != NULL))
		settings3d.view_3d = false;
	if ((overridden_models = SDL_getenv("TYR3D_NO_MODELS") != NULL))
		settings3d.models = false;
	const char *shadows = SDL_getenv("TYR3D_SHADOWS");
	if ((overridden_shadows = shadows != NULL))
		settings3d.shadows = SDL_atoi(shadows) != 0;
	const char *effects = SDL_getenv("TYR3D_EFFECTS");
	if ((overridden_effects = effects != NULL))
		settings3d.effects = SDL_atoi(effects) != 0;
	const char *music = SDL_getenv("TYR3D_MUSIC");  // midi or opl
	if ((overridden_music = music != NULL))
		settings3d.music_midi = SDL_strcasecmp(music, "opl") != 0;
	const char *mouse = SDL_getenv("TYR3D_MOUSE");  // direct or original
	if ((overridden_mouse = mouse != NULL))
		settings3d.mouse_direct = SDL_strcasecmp(mouse, "original") != 0;
	const char *hud = SDL_getenv("TYR3D_HUD");  // modern or classic
	if ((overridden_hud = hud != NULL))
		settings3d.hud_modern = SDL_strcasecmp(hud, "classic") != 0;
	const char *playfield = SDL_getenv("TYR3D_PLAYFIELD");  // wide or original
	if ((overridden_playfield = playfield != NULL))
		settings3d.playfield_wide = SDL_strcasecmp(playfield, "original") != 0;
}

void settings3d_changed(Settings3DField field)
{
	// What the player changed (in the menu, with F3 or F4) is theirs, overridden or not.
	switch (field)
	{
	case S3D_VIEW:
		chosen.view_3d = settings3d.view_3d;
		overridden_view_3d = false;
		break;
	case S3D_MODELS:
		chosen.models = settings3d.models;
		overridden_models = false;
		break;
	case S3D_SHADOWS:
		chosen.shadows = settings3d.shadows;
		overridden_shadows = false;
		break;
	case S3D_EFFECTS:
		chosen.effects = settings3d.effects;
		overridden_effects = false;
		break;
	case S3D_CAMERA:
		chosen.camera = settings3d.camera;
		break;
	case S3D_MUSIC:
		chosen.music_midi = settings3d.music_midi;
		overridden_music = false;
		break;
	case S3D_MOUSE:
		chosen.mouse_direct = settings3d.mouse_direct;
		overridden_mouse = false;
		break;
	case S3D_HUD:
		chosen.hud_modern = settings3d.hud_modern;
		overridden_hud = false;
		break;
	case S3D_PLAYFIELD:
		chosen.playfield_wide = settings3d.playfield_wide;
		overridden_playfield = false;
		break;
	}
}

void settings3d_save(ConfigSection *section)
{
	config_set_bool_option(section, "view_3d", overridden_view_3d ? chosen.view_3d : settings3d.view_3d, NO_YES);
	config_set_bool_option(section, "models", overridden_models ? chosen.models : settings3d.models, NO_YES);
	config_set_bool_option(section, "shadows", overridden_shadows ? chosen.shadows : settings3d.shadows, NO_YES);
	config_set_bool_option(section, "effects", overridden_effects ? chosen.effects : settings3d.effects, NO_YES);
	config_set_string_option(section, "camera", settings3d_camera_name(settings3d.camera));
	config_set_string_option(section, "music", (overridden_music ? chosen.music_midi : settings3d.music_midi) ? "midi" : "opl");
	config_set_string_option(section, "mouse", (overridden_mouse ? chosen.mouse_direct : settings3d.mouse_direct) ? "direct" : "original");
	config_set_string_option(section, "hud", (overridden_hud ? chosen.hud_modern : settings3d.hud_modern) ? "modern" : "classic");
	config_set_string_option(section, "playfield",
	                         (overridden_playfield ? chosen.playfield_wide : settings3d.playfield_wide) ? "wide" : "original");
}

void settings3d_apply(void)
{
	video_set_3d_enabled(settings3d.view_3d);
	m3d_enabled = settings3d.models;
	rgpu_camera.tilt_degrees = cameras[settings3d.camera].tilt;
	rgpu_camera.fov_degrees = cameras[settings3d.camera].fov;
	rgpu_apply_camera_overrides();  // TYR3D_TILT and the like
	music_midi_enable(settings3d.music_midi);
}
