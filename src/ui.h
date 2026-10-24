/*
 * Tyrian3D: the modern UI (settings3d.menus_modern), drawn over the 3D view's frames and the game's
 * screens at any window size, sharp, in the original's brass and warm browns.
 *
 * Layout: virtual units, 1080 to the window's height (times the UI scale setting), in a 16:9 safe
 * area (the window, but at most 16:9 wide, centred: on ultrawide the menus and the HUD stay round the
 * playfield), placed by its nine anchors. Text has a smallest size in the window's pixels so it stays
 * legible in small windows.
 *
 * Screens: a menu of the game (the title, setup, the new game's choices) keeps drawing itself into the
 * 320x200 screen as ever (the classic UI and the 2D view show that) and also publishes what it shows
 * (ui_menu_publish): its items, which is selected, an open picker, where the original takes the mouse.
 * While the screen shows what was published, the 3D view presents it in the new style instead: the
 * screen's picture without its texts, filling the window's height over a blurred copy of itself, and
 * the menu as panels over it. The mouse is taken in window points on the new widgets and handed to the
 * menu as the point of the original's item it is on, so the menu's own code (keys, mouse, flow) runs
 * as it always has.
 *
 * The HUD: the modern HUD's gauges and the game's own displays (score, lives, bombs, the special
 * weapon, the boss bar, the level timer) from the game's state, round the playfield (ui_build_hud).
 */
#ifndef UI_H
#define UI_H

#include "opentyr.h"

#include <SDL3/SDL.h>

// The modern UI is on: the setting, the 3D view, and its font.
bool ui_modern(void);
// The game's old 320x200 screens fill the window's height over a blurred copy of themselves (the
// modern UI with Screens: Fill), in whole steps and then smoothly.
bool ui_fill_screens(void);
// The rectangle (window points) a 320x200 screen fills in a window: 8:5, as large as fits, centred.
void ui_fill_rect(int window_w, int window_h, SDL_Rect *out);

/* --- Menus' screens -------------------------------------------------------------------------- */

typedef enum
{
	UI_SCREEN_NONE,
	UI_SCREEN_TITLE,       // the title screen's menu
	UI_SCREEN_SETUP,       // setup and its pages
	UI_SCREEN_PLAYERS,     // the new game: players (gameplaySelect)
	UI_SCREEN_EPISODES,    // the episode (episodeSelect)
	UI_SCREEN_DIFFICULTY,  // the difficulty (difficultySelect)
	UI_SCREEN_TIMED,       // the timed battle (timedBattleSelect)
} UIScreenKind;

typedef enum
{
	UI_ITEM_ACTION,  // chosen with Enter or a click
	UI_ITEM_CHOICE,  // a value, chosen from a picker
	UI_ITEM_BAR,     // a level (the volumes)
} UIItemKind;

#define UI_MENU_ITEMS 16
#define UI_PICKER_ITEMS 16

typedef struct
{
	UIItemKind kind;
	char label[48];
	char value[48];   // UI_ITEM_CHOICE: the value shown
	char hint[112];   // what it does, shown while it is selected
	float bar;        // UI_ITEM_BAR: 0-1
	bool muted;       // UI_ITEM_BAR: off (the sound muted)
	bool disabled;    // can't be chosen
	int pips;         // a row of pips (the difficulty), of which pips_on lit (0: none)
	int pips_on;
	SDL_Rect hit;        // where the original takes the mouse on the item (screen pixels): its name
	SDL_Rect hit_value;  // and on its value (w 0: none)
} UIItem;

typedef struct
{
	UIScreenKind kind;
	char title[48];
	char crumb[48];    // the page it is in (setup's), or ""
	char footer[48];   // a line in the corner (the title screen's version), or ""
	int item_count;
	UIItem items[UI_MENU_ITEMS];
	int selected;
	// A picker open over the selected item's value: its choices, which is selected, where the original
	// takes the mouse on each.
	int picker_count;
	int picker_selected;
	char picker[UI_PICKER_ITEMS][48];
	SDL_Rect picker_hit[UI_PICKER_ITEMS];
	// A palette colour the menu's text uses: the menu fades in and out as it does (fade_palette).
	Uint8 text_color;
	// A point of the screen the original takes for nothing (where the mouse is off the widgets).
	SDL_Point nowhere;
} UIMenu;

// A menu cleared for a screen: fill in its items, then publish it.
UIMenu *ui_menu_begin(UIScreenKind kind, const char *title);
UIItem *ui_menu_add(UIMenu *menu, UIItemKind kind, const char *label, int x, int y, int w, int h);
// Publishes the menu as `shown` shows it now (the screen it has just drawn), over `picture` (the
// screen's picture behind the menu: its texts are taken off it).
void ui_menu_publish(UIMenu *menu, const SDL_Surface *shown, const SDL_Surface *picture);

// For presenting (video.c): whether a screen shows the menu last published (then the 3D view
// presents it as such, rgpu_present_ui), and that the frame shown last was it (or not).
bool ui_screen_holds(const SDL_Surface *screen);
void ui_screen_shown(bool shown);
// The published screen's picture (320 x 200 palette indices) and how far it is faded in (0-1).
const Uint8 *ui_screen_picture(void);
float ui_screen_fade(void);
// A window point (points) as the screen point the original menu takes it at: on a widget, a point of
// the original's item; elsewhere the menu's point of nothing. False when the frame shown last wasn't
// a published screen.
bool ui_map_pointer(float wx, float wy, Sint32 *x, Sint32 *y);
// The mouse wheel turned (y > 0 up) over a published screen: true if it moves through the menu (the
// caller then treats it as Up or Down).
bool ui_wheel_moves(float y);

/* --- Building the overlay (render_gpu.c calls these) --------------------------------------- */

typedef struct
{
	float w, h;           // the window, points
	float pixel;          // a window pixel, points
	float picture[4];     // where the screen's picture shows (x, y, w, h), points
	float playfield[4];   // the 3D view's playfield (x, y, w, h), points (the HUD)
	bool menu_over;       // a menu of the game is over the level (the HUD stays under it)
} UIView;

// The published screen's widgets.
void ui_build_screen(const UIView *view);
// The modern HUD over a level.
void ui_build_hud(const UIView *view);
// The pointer drawn into the frame (TYR3D_SOFTWARE_POINTER with the modern UI): at window point x, y.
void ui_build_pointer(const UIView *view, float x, float y, int shape);

/* --- The pointer -------------------------------------------------------------------------- */

// The modern UI's pointer as a picture: size x size pixels, RGBA (straight alpha), its hot spot.
// shape as the game's (MOUSE_POINTER_*). Returns false if the shape isn't known.
bool ui_pointer_image(int shape, int size, Uint32 *rgba, int *hot_x, int *hot_y);
// The pointer's size in window points (24 at the UI scale 100 %).
float ui_pointer_points(void);

#endif /* UI_H */
