/*
 * Tyrian3D: how game objects appear in 3D (model, volumetric sprite or flat sprite).
 *
 * The mapping lives in assets/models/models.cfg (see the comments there). The game code asks
 * for an appearance when it is about to draw an enemy or the player; if it is a model, it records
 * a 3D object in the current frame (layer3d.h) and skips the sprite.
 */
#ifndef MODELS3D_H
#define MODELS3D_H

#include "opentyr.h"

#include "layer3d.h"

#define M3D_MAX_MODELS 64

// Appearance kinds besides a model index (>= 0).
#define M3D_SPRITE (-1)  // the original sprite in its layer
#define M3D_VOLUME (-2)  // the original sprite with volume (generated mesh)

typedef struct
{
	char name[32];
	char path[512];
	float size;               // footprint in game pixels; 0 = model units are game pixels
	float yaw, pitch, roll;   // degrees, applied to face the model up the screen
} M3DModel;

typedef enum
{
	M3D_YAW_FIXED,     // yaw degrees (enemies default to 180: nose down the screen)
	M3D_YAW_VELOCITY,  // face the direction of movement
	M3D_YAW_AIM,       // face the player
	M3D_YAW_FRAMES,    // animation frame k faces yaw + k * yaw_step
} M3DYawMode;

typedef struct
{
	int model;          // model index, M3D_SPRITE or M3D_VOLUME
	M3DYawMode yaw_mode;
	float yaw;          // degrees; 0 = nose up the screen
	float yaw_step;     // degrees per animation frame, for M3D_YAW_FRAMES
	float height;       // added to the layer's height, game pixels
	bool banking;       // player ships: roll with the banking sprite
	float roll_step;    // degrees of roll per animation frame (the animation is a roll), or 0
} M3DAppearance;

extern bool m3d_enabled;  // appearances other than M3D_SPRITE are used (toggled at runtime)

extern int m3d_model_count;
extern M3DModel m3d_models[M3D_MAX_MODELS];
extern unsigned int m3d_generation;  // increases on every (re)load, so renderers can drop caches

// Loads the mapping; missing or broken files leave everything as sprites.
void m3d_init(void);
// Reloads models.cfg (F5).
void m3d_reload(void);

// Appearance of an enemy. sheet is the enemy shape file letter (0 for other sheets) and
// first_sprite the first sprite of its animation.
M3DAppearance m3d_enemy_appearance(char sheet, unsigned int first_sprite, bool large, L3DLayerType layer);
// Appearance of a player ship (ship id as in the shop, 1-based).
M3DAppearance m3d_ship_appearance(unsigned int ship_id);
// Appearance of a sidekick (option id as in the shop, 1-based).
M3DAppearance m3d_sidekick_appearance(unsigned int sidekick_id);

// The "sprite" lines of models.cfg (one enemy type each), for the model viewer.
int m3d_sprite_rule_count(void);
void m3d_sprite_rule(int i, char *sheet, unsigned int *first_sprite, M3DAppearance *appearance);

#endif /* MODELS3D_H */
