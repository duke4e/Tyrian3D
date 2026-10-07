/*
 * Tyrian3D: which game objects are shown as 3D models instead of sprites.
 *
 * The mapping lives in assets/models/models.cfg (see the comments there). The game code asks
 * for a model when it is about to draw an enemy or the player; if one is mapped, it records a
 * 3D object in the current frame (layer3d.h) and skips the sprite.
 */
#ifndef MODELS3D_H
#define MODELS3D_H

#include "opentyr.h"

#include "layer3d.h"

#define M3D_MAX_MODELS 64

typedef struct
{
	char name[32];
	char path[512];
	float size;               // footprint in game pixels
	float yaw, pitch, roll;   // degrees, applied to face the model up the screen
} M3DModel;

extern bool m3d_enabled;  // models replace sprites (toggled at runtime)

extern int m3d_model_count;
extern M3DModel m3d_models[M3D_MAX_MODELS];

// Loads the mapping. Missing or broken files leave models disabled.
void m3d_init(void);

// Model for an enemy, or -1. sheet is the enemy shape file letter (0 for other sheets) and
// sprite_index the first sprite of its animation.
int m3d_enemy_model(char sheet, unsigned int sprite_index, bool large, L3DLayerType layer);
// Model for the player's ship, or -1.
int m3d_player_model(void);

#endif /* MODELS3D_H */
