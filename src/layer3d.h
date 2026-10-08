/*
 * Tyrian3D: depth-layer capture of the 2D game screen.
 *
 * The original game composites everything into a single 8-bit 320x200 surface. To show it
 * in 3D we split each frame into layers by draw phase: the main loop marks where each phase
 * (background 1, ground enemies, background 2, ...) begins, and we diff the composite against
 * a snapshot taken at the start of the phase. Pixels that changed belong to that phase's layer.
 * Every layer is captured before later phases cover it, so each one is complete and can be
 * placed at its own height in the 3D scene.
 *
 * Filter phases (water, blur, darkening) modify pixels in place: their changes are written
 * back into whichever layer currently owns each pixel.
 */
#ifndef LAYER3D_H
#define LAYER3D_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define L3D_WIDTH  320
#define L3D_HEIGHT 200
// Layers also hold the rows above the screen's top edge (see SCREEN_OVERSCAN_MAX in video.h).
// Layer row r is game screen row r - L3D_OVERSCAN.
#define L3D_OVERSCAN 64
#define L3D_ROWS (L3D_HEIGHT + L3D_OVERSCAN)

// Visible playfield inside the game screen.
#define L3D_PLAYFIELD_X 24
#define L3D_PLAYFIELD_W 264
#define L3D_PLAYFIELD_H 184

typedef enum
{
	L3D_GROUND,        // background 1 / starfield
	L3D_BG2_LOW,       // background 2 drawn under ground enemies
	L3D_GROUND_ENEMY,
	L3D_BG2,
	L3D_SKY_ENEMY,
	L3D_BG3,
	L3D_TOP_ENEMY,
	L3D_PLAYER,        // player ships, player shots, enemy shots, particles
	L3D_EXPLOSION,
	L3D_BG2_OVER,      // background 2 drawn over explosions
	L3D_BG3_OVER,      // background 3 drawn over the player
	L3D_OVERLAY,       // in-playfield text and gauges, shown flat in screen space
	L3D_LAYER_TYPE_COUNT
} L3DLayerType;

#define L3D_MAX_LAYERS 24

typedef struct
{
	L3DLayerType type;
	Uint8 index[L3D_WIDTH * L3D_ROWS];  // palette indices
	Uint8 cover[L3D_WIDTH * L3D_ROWS];  // non-zero where the layer has a pixel
	int min_y, max_y;                   // layer rows that contain pixels (max_y exclusive)
} L3DLayer;

// Object kinds besides a model index (>= 0); matches M3D_VOLUME in models3d.h.
#define L3D_VOLUME (-2)   // a volumetric sprite

// A game object shown in 3D instead of as a flat sprite.
typedef struct
{
	int model;            // index into m3d_models, or L3D_VOLUME
	const void *sheet;    // L3D_VOLUME: the Sprite2_array the sprite comes from
	Uint16 sprite;        // L3D_VOLUME: sprite index (1-based)
	bool large;           // L3D_VOLUME: 2x2 sprite
	Uint8 style;          // L3D_VOLUME: V3DStyle
	float x, y;           // centre, in game screen coordinates
	L3DLayerType layer;   // draw phase the object was drawn in
	float height;         // added to the layer's height, game pixels
	float yaw;            // degrees; 0 = nose up the screen
	float roll;           // degrees, positive banks right
	Uint8 filter;         // the sprite filter (blit_sprite2_filter: index = filter | shade), 0 for none
	bool ghost;           // half transparent (the player's ship while invulnerable)
	float vx, vy;         // how far it moved since the last frame (game pixels), see l3d_key_last_object
	bool pointer;         // moves with the mouse between ticks (l3d_pointer_lead), not by vx, vy
	Uint8 open_sides;     // L3D_VOLUME: sides another part of the same enemy continues (V3D_OPEN_*)
} L3DObject;

#define L3D_MAX_OBJECTS 1024

// Recolouring filters the game applies to what is already on screen. The 3D view repeats their
// colours on the background tiles outside the playfield (background3d.h).
typedef enum
{
	L3D_EFFECT_LAVA,   // lava_filter
	L3D_EFFECT_WATER,  // water_filter; parameter: the water's hue
	L3D_EFFECT_ICE,    // iced_blur_filter
} L3DEffect;

#define L3D_MAX_EFFECTS 4

// A background map drawn in a phase, with the scroll state it was drawn with. The 3D view uses it
// to draw all of the map the camera sees (background3d.h).
typedef struct
{
	int layer;                // index of the layer it was drawn into
	Uint8 set;                // which background map: 1, 2 or 3 (megaData1/2/3)
	bool blend;               // averaged with what is below (draw_background_2_blend)
	Uint8 **top_row;          // map entry drawn as the first tile of the topmost row
	Uint8 **position;         // the map's scroll position (mapYPos & co.)
	Uint8 **wrap, **wrap_to;  // scrolling up to wrap continues at wrap_to (BKwrap*)
	int x, top_y;             // screen position of the topmost row's first tile
	int effect_count;         // filters applied after it was drawn, in order
	Uint8 effects[L3D_MAX_EFFECTS], effect_params[L3D_MAX_EFFECTS];
} L3DBackground;

#define L3D_MAX_BACKGROUNDS 4

// A star of the background starfield (update_and_draw_starfield), as the game positions it:
// row * 320 + column in a ring of 65536 pixels.
typedef struct
{
	Uint16 position;
	Uint8 color;  // palette index
	bool bright;  // drawn with four dimmer neighbours
} L3DStar;

#define L3D_MAX_STARS 128

// A glow around a shot or an item (the 3D view draws it as additive light): its centre, size and
// strength, the layer it was drawn in, and the palette index of its colour.
typedef struct
{
	float x, y;
	float size, strength;  // diameter in game pixels; fraction of the colour added at the centre
	float vx, vy;          // how far it moved since the last frame (game pixels)
	Uint8 layer;
	Uint8 color;
} L3DGlow;

#define L3D_MAX_GLOWS 256

typedef struct
{
	int layer_count;
	L3DLayer layers[L3D_MAX_LAYERS];

	int object_count;
	L3DObject objects[L3D_MAX_OBJECTS];

	int background_count;
	L3DBackground backgrounds[L3D_MAX_BACKGROUNDS];

	int star_count;
	int star_layer;  // layer the starfield was drawn into
	L3DStar stars[L3D_MAX_STARS];

	int glow_count;
	L3DGlow glows[L3D_MAX_GLOWS];

	// JE_filterScreen parameters, applied when layers are converted to colour.
	int filter_hue;         // -99 for none
	int filter_brightness;  // -99 for none
} L3DFrame;

extern bool l3d_enabled;  // the 3D view is active (set by the renderer)
extern bool l3d_capturing; // inside an in-game frame between begin and end

extern L3DFrame l3d_frame;

// Frames captured so far: a clock for things that only show (models spinning), apart from the game's.
extern Uint32 l3d_frame_number;

// Starts capturing a frame if the 3D view is enabled. The first phase is always a fully opaque layer.
void l3d_frame_begin(L3DLayerType first_type);
// Ends the current phase; drawing that follows belongs to a layer of the given type.
void l3d_phase(L3DLayerType type);
// Ends the current phase; drawing that follows modifies existing layers in place.
void l3d_modify(void);
// Ends the last phase. The frame stays readable until the next l3d_frame_begin.
void l3d_frame_end(void);
// True once per completed frame; clears the flag.
bool l3d_take_frame(void);

// Layer type of the current draw phase.
L3DLayerType l3d_current_layer(void);
// Records a model object in the current phase. Returns false if the frame isn't being captured
// (the caller should draw the sprite instead).
bool l3d_add_object(int model, float x, float y, float height, float yaw, float roll, Uint8 filter);
// Makes the object recorded last half transparent, as the game draws the invulnerable player's
// ship (blit_sprite2x2_blend).
void l3d_ghost_last_object(void);

// Gives the object recorded last a key that stays the same from frame to frame (an enemy's slot):
// it then gets the velocity it moved with since the last frame, so the 3D view can move it on in
// the frames it shows between the game's ticks. Jumps (a slot taken by a new enemy) count as no
// motion. Returns the velocity, which a glow belonging to the object can take too.
void l3d_key_last_object(Uint32 key, float *vx, float *vy);
// Whether an object had the key in the last frame (or has it in this one).
bool l3d_key_seen(Uint32 key);
// Where the object with the key was last recorded (centre, game pixels); false if never.
bool l3d_key_position(Uint32 key, float *x, float *y);
// For the object keyed last when its key is new (an enemy that has just appeared, which has no
// motion yet to go by): the velocity it will move with (game pixels a tick). Returns it, or the
// measured one.
void l3d_new_object_velocity(float vx, float vy, float *out_vx, float *out_vy);

// The ship the mouse moves directly: in the frames shown between ticks it is drawn where the mouse
// has moved it so far (l3d_pointer_lead, game pixels), rather than moved on by its velocity.
void l3d_pointer_last_object(void);
// The volumetric sprite recorded last continues on these sides (V3D_OPEN_*) in another part of
// the same enemy (the parts of large enemies and bosses join without a seam).
void l3d_open_last_object(Uint8 sides);
extern float l3d_pointer_lead[2];

// Key ranges (an enemy slot, shot index and the like is added).
#define L3D_KEY_ENEMY      0x10000u
#define L3D_KEY_PLAYER     0x20000u
#define L3D_KEY_SIDEKICK   0x21000u
#define L3D_KEY_SHOT       0x30000u
#define L3D_KEY_ENEMY_SHOT 0x40000u

// A shot's sprite (1x1, drawn at x, y as blit_sprite2 draws it) as a flat volumetric sprite with
// its glow, which moves on between ticks (key: the shot's L3D_KEY_* + index). False when the 3D
// view isn't capturing or shows flat sprites: then draw the sprite as usual.
bool l3d_add_shot(const void *sheet, unsigned int sprite, int x, int y, Uint32 key);

// A shot the game dropped because it left the screen at the top: the 3D view, which sees further,
// lets it fly on (vx, vy: game pixels a tick) until it is far away. l3d_draw_departed_shots adds
// them to the frame (in the player's phase, once a frame).
void l3d_shot_departed(const void *sheet, unsigned int sprite, int x, int y, int vx, int vy);
void l3d_draw_departed_shots(void);
void l3d_clear_departed_shots(void);
// Sets the velocity of the glow recorded last.
void l3d_last_glow_velocity(float vx, float vy);
// Records a glow of a palette colour centred on x, y moving vx, vy a frame (a spark). False when
// the 3D view isn't capturing (or has no room), so the caller draws it as usual.
bool l3d_add_color_glow(float x, float y, float size, float strength, Uint8 color, float vx, float vy);
// Records a volumetric sprite (sheet is a Sprite2_array *). Same contract as l3d_add_object.
bool l3d_add_volume(const void *sheet, unsigned int sprite, bool large, int style, float x, float y, float height,
                    float yaw, float roll, Uint8 filter);

// Records a background map drawn in the current phase (see L3DBackground).
void l3d_add_background(int set, Uint8 **top_row, Uint8 **position, Uint8 **wrap, Uint8 **wrap_to,
                        int x, int top_y, bool blend);

// Records a star of the background starfield drawn in the current phase.
void l3d_add_star(Uint16 position, Uint8 color, bool bright);

// Records a glow around a 1x1 sprite (a shot; sheet is a Sprite2_array *) drawn at x, y in the
// current phase. Its colour is the sprite's brightest.
void l3d_add_glow(const void *sheet, unsigned int sprite, int x, int y);
// Records a glow of the given size and strength centred on x, y, in a light shade of a sprite's
// main colour (large: a 2x2 sprite).
void l3d_add_sprite_glow(const void *sheet, unsigned int sprite, bool large, float x, float y, float size,
                         float strength);

// The palette ramp (index >> 4) of a sprite's main colour: the most used, not counting dark
// outlines (large: a 2x2 sprite).
Uint8 l3d_sprite_ramp(const void *sheet, unsigned int sprite, bool large);

// Records a recolouring filter applied to everything drawn so far in the frame.
void l3d_add_effect(L3DEffect effect, int param);

// Records full-screen filter parameters instead of applying them to the composite.
void l3d_set_filter(int hue, int brightness);

// Height of a layer type above the ground plane, in game pixels.
// Added to the heights of the layers above the ground's enemies, to make room for raised terrain.
extern float l3d_terrain_headroom;
float l3d_layer_height(L3DLayerType type);
const char *l3d_layer_name(L3DLayerType type);

#endif /* LAYER3D_H */
