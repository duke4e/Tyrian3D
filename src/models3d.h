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

#define M3D_MAX_MODELS 4096

// Appearance kinds besides a model index (>= 0).
#define M3D_SPRITE (-1)  // the original sprite in its layer
#define M3D_VOLUME (-2)  // the original sprite with volume (generated mesh)

typedef struct
{
	char name[32];
	char path[512];
	float size;               // footprint in game pixels; 0 = model units are game pixels
	float yaw, pitch, roll;   // degrees, applied to face the model up the screen
	bool keep_origin;         // drawn at its own origin (pieces of one object), not centred in height
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
	float spin;         // degrees turned every frame, on top of the yaw (items turning)
	bool recolor;       // palette materials take the colour ramp of the sprite's current frame
	float glow_size;    // a glow in the sprite's colour this wide (game pixels); 0 none
	float glow_strength;
	Uint8 glow_color;   // the glow in this palette colour; 0 the sprite's main colour
	bool glow_has_rgb;  // the glow in this colour (#rrggbb in models.cfg) instead
	Uint8 glow_rgb[3];
	float glow_dx, glow_dy;  // the glow this far from the sprite's centre (game pixels, y down the screen)
	int layer;          // drawn at this layer's height (L3DLayerType + 1) whatever layer the game uses; 0 its own
	bool trail;         // shots: a smoke trail behind it (missiles)
	bool beam;          // shots: a beam's segment, fired one a tick (models.cfg "beam")
	float at_dx, at_dy;  // shots: the model this far from the sprite's centre (game pixels, y down the screen)
	float scale;        // shots: the model this many times its size (0: as built)
} M3DAppearance;

// Sheet letters for the enemies drawn from the coins and gems sheet and from the power-ups sheet
// (the shape files' letters are digits, letters and a few signs).
#define M3D_SHEET_COINS    '$'
#define M3D_SHEET_POWERUPS '+'

extern bool m3d_enabled;  // appearances other than M3D_SPRITE are used (toggled at runtime)

extern int m3d_model_count;
extern M3DModel m3d_models[M3D_MAX_MODELS];
extern unsigned int m3d_generation;  // increases on every (re)load, so renderers can drop caches

// Loads the mapping; missing or broken files leave everything as sprites.
void m3d_init(void);
// Reloads models.cfg (F5).
void m3d_reload(void);

// Appearance of an enemy. sheet is the enemy shape file letter (M3D_SHEET_COINS and
// M3D_SHEET_POWERUPS for those sheets, 0 for others) and first_sprite the first sprite of its
// animation.
M3DAppearance m3d_enemy_appearance(char sheet, unsigned int first_sprite, bool large, L3DLayerType layer);
// The Dragonwing, the second player's ship in two-player arcade games, which isn't in the shop
// ("ship dragonwing" in models.cfg).
#define M3D_SHIP_DRAGONWING 255

// Appearance of a player ship (ship id as in the shop, 1-based, or M3D_SHIP_DRAGONWING).
M3DAppearance m3d_ship_appearance(unsigned int ship_id);
// Appearance of a sidekick (option id as in the shop, 1-based).
M3DAppearance m3d_sidekick_appearance(unsigned int sidekick_id);

// The store's illustration of the ship: the model of a big ship's picture (option shapes sprite) and
// of a gun's or generator's picture (weapon shapes sprite), or -1.
int m3d_illustration_model(int option_sprite);
int m3d_mount_model(int weapon_sprite);

// The "sprite" lines of models.cfg (one enemy type each), for the model viewer.
// The model to show while an enemy whose appearance is `model` shows animation frame `sprite`
// (models.cfg "frame" lines: a model for a frame that changes shape); `model` if there is none.
int m3d_frame_model(char sheet, unsigned int sprite, int model);
// What is left of an enemy type where the ground map paints it once destroyed (models.cfg "wreck"
// lines: the clean ground's stand-ins), or -1; M3D_WRECK_NONE: nothing stands in for it ("wreck ... none":
// a launched enemy's look, the map painting what launched it there).
#define M3D_WRECK_NONE (-2)
int m3d_wreck_model(char sheet, unsigned int sprite);
// The model that stands in for a look where the map paints it as it is (models.cfg "standin" lines: the
// painting's colours where they are not the sprite's), or -1 (its own model).
int m3d_standin_model(char sheet, unsigned int sprite);
// A shot's model (models.cfg "shot" lines), for sprite `sprite` of the shots sheet (shots2: the
// second one); false if it has none (it shows as a volume).
bool m3d_shot_appearance(bool shots2, unsigned int sprite, M3DAppearance *appearance);
// The model of a big shot drawn from the option shapes ("shot options <shape>" lines: the Xega Ball, the Plasma
// Storm), or false.
bool m3d_option_shot_appearance(unsigned int shape, M3DAppearance *appearance);
int m3d_sprite_rule_count(void);
// The model of that name in models.cfg, or -1.
int m3d_find_model(const char *name);
void m3d_sprite_rule(int i, char *sheet, unsigned int *first_sprite, M3DAppearance *appearance);

#endif /* MODELS3D_H */
