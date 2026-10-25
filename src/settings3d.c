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

#include <stdio.h>
#include <string.h>

Settings3D settings3d = { .view_3d = true, .models = true, .shadows = true, .effects = true, .camera = 0, .music_midi = true,
                          .mouse_direct = true, .hud_modern = true, .playfield_wide = true, .menus_modern = true,
                          .screens_fill = true, .ui_scale = 100 };

// The settings as the player chose them, which are saved: the environment's overrides only
// apply to settings3d, for the run.
static Settings3D chosen = { .view_3d = true, .models = true, .shadows = true, .effects = true, .camera = 0, .music_midi = true,
                             .mouse_direct = true, .hud_modern = true, .playfield_wide = true, .menus_modern = true,
                             .screens_fill = true, .ui_scale = 100 };
static bool overridden_view_3d, overridden_models, overridden_shadows, overridden_effects, overridden_music, overridden_mouse, overridden_hud,
            overridden_playfield, overridden_menus, overridden_screens, overridden_ui_scale;

static const int ui_scales[] = { 75, 90, 100, 115, 130, 150 };

int settings3d_ui_scale_count(void)
{
	return (int)COUNTOF(ui_scales);
}

int settings3d_ui_scale_value(int i)
{
	return ui_scales[SDL_clamp(i, 0, (int)COUNTOF(ui_scales) - 1)];
}

int settings3d_ui_scale_index(int percent)
{
	int best = 0;
	for (int i = 1; i < (int)COUNTOF(ui_scales); ++i)
		if (SDL_abs(ui_scales[i] - percent) < SDL_abs(ui_scales[best] - percent))
			best = i;
	return best;
}

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
		const char *menus;
		if (config_get_string_option(section, "menus", &menus))
			chosen.menus_modern = SDL_strcasecmp(menus, "classic") != 0;
		const char *screens;
		if (config_get_string_option(section, "screens", &screens))
			chosen.screens_fill = SDL_strcasecmp(screens, "integer") != 0;
		const char *ui_scale;
		if (config_get_string_option(section, "ui_scale", &ui_scale))
			chosen.ui_scale = settings3d_ui_scale_value(settings3d_ui_scale_index(SDL_atoi(ui_scale)));
		const char *soundfont;
		if (config_get_string_option(section, "soundfont", &soundfont))
			SDL_strlcpy(chosen.soundfont, soundfont, sizeof(chosen.soundfont));
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
	const char *menus = SDL_getenv("TYR3D_MENUS");  // modern or classic
	if ((overridden_menus = menus != NULL))
		settings3d.menus_modern = SDL_strcasecmp(menus, "classic") != 0;
	const char *screens = SDL_getenv("TYR3D_SCREENS");  // fill or integer
	if ((overridden_screens = screens != NULL))
		settings3d.screens_fill = SDL_strcasecmp(screens, "integer") != 0;
	const char *ui_scale = SDL_getenv("TYR3D_UI_SCALE");  // per cent
	if ((overridden_ui_scale = ui_scale != NULL))
		settings3d.ui_scale = SDL_clamp(SDL_atoi(ui_scale), 50, 200);
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
	case S3D_MENUS:
		chosen.menus_modern = settings3d.menus_modern;
		overridden_menus = false;
		break;
	case S3D_SCREENS:
		chosen.screens_fill = settings3d.screens_fill;
		overridden_screens = false;
		break;
	case S3D_UI_SCALE:
		chosen.ui_scale = settings3d.ui_scale;
		overridden_ui_scale = false;
		break;
	case S3D_SOUNDFONT:
		SDL_strlcpy(chosen.soundfont, settings3d.soundfont, sizeof(chosen.soundfont));
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
	config_set_string_option(section, "menus", (overridden_menus ? chosen.menus_modern : settings3d.menus_modern) ? "modern" : "classic");
	config_set_string_option(section, "screens", (overridden_screens ? chosen.screens_fill : settings3d.screens_fill) ? "fill" : "integer");
	char percent[16];
	snprintf(percent, sizeof(percent), "%d", overridden_ui_scale ? chosen.ui_scale : settings3d.ui_scale);
	config_set_string_option(section, "ui_scale", percent);
	config_set_string_option(section, "soundfont", settings3d.soundfont);
}

void settings3d_apply(void)
{
	video_set_3d_enabled(settings3d.view_3d);
	m3d_enabled = settings3d.models;
	rgpu_camera.tilt_degrees = cameras[settings3d.camera].tilt;
	rgpu_camera.fov_degrees = cameras[settings3d.camera].fov;
	rgpu_apply_camera_overrides();  // TYR3D_TILT and the like
	music_midi_enable(settings3d.music_midi);
	if (music_midi_available())
		music_midi_use(settings3d.soundfont);
}
