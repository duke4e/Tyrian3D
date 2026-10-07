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
	Uint8 filter;         // enemy hit-flash filter (palette hue << 4), 0 for none
} L3DObject;

#define L3D_MAX_OBJECTS 256

typedef struct
{
	int layer_count;
	L3DLayer layers[L3D_MAX_LAYERS];

	int object_count;
	L3DObject objects[L3D_MAX_OBJECTS];

	// JE_filterScreen parameters, applied when layers are converted to colour.
	int filter_hue;         // -99 for none
	int filter_brightness;  // -99 for none
} L3DFrame;

extern bool l3d_enabled;  // the 3D view is active (set by the renderer)
extern bool l3d_capturing; // inside an in-game frame between begin and end

extern L3DFrame l3d_frame;

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
// Records a volumetric sprite (sheet is a Sprite2_array *). Same contract as l3d_add_object.
bool l3d_add_volume(const void *sheet, unsigned int sprite, bool large, int style, float x, float y, float height,
                    float yaw, float roll, Uint8 filter);

// Records full-screen filter parameters instead of applying them to the composite.
void l3d_set_filter(int hue, int brightness);

// Height of a layer type above the ground plane, in game pixels.
float l3d_layer_height(L3DLayerType type);
const char *l3d_layer_name(L3DLayerType type);

#endif /* LAYER3D_H */
