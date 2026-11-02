/*
 * Tyrian3D: GPU presentation through the BTBH renderer (SDL_GPU: Metal / Vulkan).
 *
 * Two ways to present a frame:
 *  - 2D: the 8-bit 320x200 screen, palette-converted and scaled into the window (menus etc.).
 *  - 3D: the captured depth layers of the playfield as planes under a tilted perspective camera,
 *        with the HUD and in-playfield text drawn flat on top.
 */
#ifndef RENDER_GPU_H
#define RENDER_GPU_H

#include "opentyr.h"

#include "layer3d.h"

#include <SDL3/SDL.h>

typedef struct
{
	float tilt_degrees;   // camera tilt away from straight down
	float fov_degrees;    // vertical field of view
	float height_scale;   // multiplier for layer heights
} RGPUCamera;

extern RGPUCamera rgpu_camera;

// Applies the camera settings given in the environment (TYR3D_TILT, TYR3D_FOV,
// TYR3D_HEIGHT_SCALE, TYR3D_SUN) over the current ones.
void rgpu_apply_camera_overrides(void);

// Creates the GPU device and a hidden window. Exits on failure.
SDL_Window *rgpu_init(const char *title, int width, int height);
void rgpu_shutdown(void);

// dst is the 320x200 screen's rectangle in window coordinates. With the modern UI's Screens: Fill
// (ui_fill_screens) it fills the window's height, sharp, over a blurred copy of itself.
void rgpu_present_2d(const SDL_Surface *screen, const SDL_Rect *dst);
// A picture sliding over the screen (the level texts' ]U, ]V and ]R): JE_loadPic's picture with its top left
// corner at x, y on the screen, and the screen's earlier picture moved to old_x, old_y, each drawn anew where
// it is (rgpu_present_2d); picture 0 when the slide is over.
void rgpu_picture_slide(int picture, int x, int y, int old_x, int old_y);
// Whether the 3D view writes picked-up items' values (L3DFrame.values) in Oxanium, so the game leaves out their sprites.
bool rgpu_values_written(void);
// The window black (nothing of the screen).
void rgpu_present_blank(void);
// Whether the 3D view shows the modern HUD (gauges over the scene) rather than the game's panel.
bool rgpu_modern_hud(void);
// hud is the 8-bit screen holding the HUD; its playfield area is replaced by the 3D view.
void rgpu_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);
// The same frame again, `ticks` of the game's ticks later: what moves (the maps, objects with a
// velocity, particles) moved on at its speed. For the frames shown while the game waits for its
// next tick.
void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks);

// Window points per game pixel in the 3D view's playfield (at the player's height).
// A menu or message the game shows over the playfield in a level (pause, the in-game options, the
// level's end), over the 3D view's last frame: what differs from the screen as it was when that
// frame showed (backdrop) is drawn over it, the boxes the menu darkened (x1, y1, x2, y2, as
// JE_barShade takes them) darken it, fade (RGBA 0-1) goes over the whole window. *screen_rect:
// where the screen's pixels show in the window (the playfield's part of them as laid out), for the mouse.
// modern: the screen published over the level is shown in the modern UI's style (ui.h) instead of the
// menu's own drawing, over the scene blurred under its glass.
void rgpu_present_3d_menu(const SDL_Surface *screen, const Uint8 *backdrop, const int (*shades)[4], int shade_count,
                          const float fade[4], const L3DFrame *frame, const SDL_Rect *dst, SDL_Rect *screen_rect, bool modern);

// A box of the store's screen as a scene (the illustration of the ship, the weapon simulator): its
// picture without the ship (and shots) on the ground seen from straight above, models over it, the
// screen over everything but where it still shows the picture.
typedef struct
{
	int model;
	float x, y;    // screen pixels (on a parent: from its centre, as it is drawn unturned)
	float height;  // above the picture (on a parent: above its origin), screen pixels
	float size;    // footprint, screen pixels, centred on its bounds (0: its own size in screen pixels, at its origin)
	float yaw, pitch, roll;  // degrees
	int parent;    // an earlier object it rides on (turns with it), or -1
	// model M3D_VOLUME (models3d.h): a sprite with volume, as the 3D view draws what has no model (an HD volume from
	// the 4x sheets where there is one): sheet a Sprite2_array, style a V3DStyle (flat: shots), large a 2x2 sprite; at
	// the sprite's own size, centred on x, y (size and parent unused).
	const void *sheet;
	Uint16 sprite;
	bool large;
	Uint8 style;
	float scale;   // a model this many times its size (0: as built)
} RGPUShowcaseObject;

// Light round a point of a showcase's scene, as the levels' shots, items and engines glow (L3DGlow): drawn
// additively, and the strongest light what is near them.
typedef struct
{
	float x, y;            // screen pixels, as the objects
	float height;          // above the picture, screen pixels
	float size, strength;  // diameter in screen pixels; how much of its colour is added at its middle
	Uint8 color;           // a palette index, or 0: rgb
	Uint8 rgb[3];          // sRGB
} RGPUShowcaseGlow;

typedef struct
{
	SDL_Rect pane;             // the box (screen pixels)
	const Uint8 *backdrop;     // the screen with the box's picture under the models (SCREEN_W x SCREEN_H)
	const Uint8 *transparent;  // where the screen is as this, the scene shows
	const RGPUShowcaseObject *objects;
	int object_count;
	float fade[4];             // a colour over everything (RGBA 0-1)
	const RGPUShowcaseGlow *glows;  // with the Effects setting
	int glow_count;
	bool particles;            // the particles (particles3d.h) are the scene's, in screen pixels (the weapon simulator's
	                           // missiles' smoke), drawn as the levels draw theirs (with the Effects setting)
} RGPUShowcase;

void rgpu_present_showcase(const SDL_Surface *screen, const RGPUShowcase *show, const SDL_Rect *dst);

// A screen of the modern UI (ui.h): the published menu's picture filling the window's height over its
// blurred copy (or, for the store, its layout over the blurred picture), and the menu's panels over
// it (ui_build_screen); with a scene (the store's ship, its weapon simulator: scene->objects, and
// for the simulator scene->backdrop its picture under them), that drawn where the layout puts it.
void rgpu_present_ui(const RGPUShowcase *scene);
// The same screen again between the game's ticks, without a scene of the store (the jukebox's visuals
// move on); not counted as one of the game's frames (dumps, TYR3D_EXIT_AFTER).
void rgpu_present_ui_again(void);

float rgpu_playfield_scale(void);
// A window point (points) as a position on the player's plane in the view shown last, in game
// screen coordinates, and back. False before a 3D frame was shown (or above the horizon).
bool rgpu_window_to_playfield(float wx, float wy, float *x, float *y);
bool rgpu_playfield_to_window(float x, float y, float *wx, float *wy);

/*
 * The UI's drawing (ui.c): shapes, text and icons over the frame being made, in window points, in the
 * order drawn (later over earlier). Colours are RGBA 0-1, straight alpha.
 */
enum { RGPU_FONT_BOLD, RGPU_FONT_SEMIBOLD, RGPU_FONT_MEDIUM };
// A convex quad: its corners in order round it, a colour each.
void rgpu_ui_quad(const float x[4], const float y[4], const float rgba[4][4]);
// The screen's picture blurred where it lies under a convex quad (frosted glass), times tint; only on
// the modern UI's screens (rgpu_ui_frost_ready).
void rgpu_ui_frost(const float x[4], const float y[4], const float tint[4]);
bool rgpu_ui_frost_ready(void);
// A picture of the UI's own (RGBA, straight alpha, at most 128 square) in a rectangle; key: which picture
// it is (it is uploaded again when that changes).
void rgpu_ui_image(Uint32 key, const Uint32 *rgba, int w, int h, float x, float y, float dw, float dh);
// A sprite of the game (sheet: a Sprite2_array; large: a 2x2 sprite) in a rectangle, in the palette.
void rgpu_ui_sprite(const void *sheet, unsigned int sprite, bool large, float x, float y, float w, float h, float alpha);
// A sprite of one of the game's sprite tables (OPTION_SHAPES...), fitted in a rectangle at its aspect.
void rgpu_ui_table_sprite(unsigned int table, unsigned int sprite, float x, float y, float w, float h, float alpha);
// An item's icon rendered from its 3D model (a models.cfg model index; assets/models/icons/<model>.png, see
// rgpu_render_icons), square in the middle of a rectangle at the window's own pixels: false if the model has no such
// render (the item's sprite stands in); true while it is being read too, before it fades in.
bool rgpu_ui_model_icon(int model, float x, float y, float w, float h, float alpha);
// TYR3D_RENDER_ICONS: renders those models' icons into <dir>/<model>.png, each a model (models.cfg index) and the
// palette ramp its palette materials take (as models.cfg's color=sprite), or -1; true if all were written.
typedef struct
{
	int model;
	int ramp;
} RGPUIcon;
bool rgpu_render_icons(const char *dir, const RGPUIcon *icons, int count);
// A part of the screen's picture (screen pixels) in a rectangle, sharp (whole steps, then smoothly).
void rgpu_ui_picture(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha);
// Text in Oxanium (RGPU_FONT_*): the top of its capitals at y, cap height in points, shaded from top to
// bottom, with a shadow that far below and right (0: none); and how wide it is.
bool rgpu_ui_text_ready(void);
float rgpu_ui_text_width(int font, const char *s, float cap);
void rgpu_ui_text(int font, const char *s, float x, float y, float cap, const float top[4], const float bottom[4], float shadow);
// The quads made so far; those made since a mark that much more transparent.
int rgpu_ui_mark(void);
void rgpu_ui_fade_since(int mark, float alpha);

#endif /* RENDER_GPU_H */
