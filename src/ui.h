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
	UI_SCREEN_SHOP,        // the store between levels (game_menu.c), its pages (UIShop.page)
	// Over a level's 3D view (rgpu_present_3d_menu), the game halted under them:
	UI_SCREEN_LEVEL_MENU,  // the in-game options and their 3D page: rows as setup's
	UI_SCREEN_LEVEL_HELP,  // the in-game help (F1): what the HUD shows
	UI_SCREEN_LEVEL_PAUSE, // paused
	UI_SCREEN_LEVEL_END,   // the level's end: its results
} UIScreenKind;

typedef enum
{
	UI_ITEM_ACTION,  // chosen with Enter or a click
	UI_ITEM_CHOICE,  // a value, chosen from a picker (or turned with Left / Right: UIMenu.values_turn)
	UI_ITEM_BAR,     // a level (the volumes)
} UIItemKind;

#define UI_MENU_ITEMS 32
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
	// The store's cards and rows:
	const void *icon_sheet;  // a sprite of the game as its icon (a Sprite2_array), or NULL
	int icon_table;          // or of a sprite table (> 0: OPTION_SHAPES...)
	int icon_sprite;
	bool icon_large;         // a 2x2 sprite
	bool owned;              // what the ship has
	bool chosen;             // what the ship has as chosen now (the store shows it on the ship)
	bool unaffordable;       // more than the credits
	int stat_count;          // short stat bars: 0-1, what each is
	float stat[2];
	char stat_label[2][16];
	char value2[24];         // a second value (a saved game's episode)
	int cubes;               // data cube icons after the name (the store's Data)
	bool capturing;          // its value waits for a key or a button
	bool gap_before;         // set apart from the one before it (the store's Quit Game)
} UIItem;

// The store's pages.
typedef enum
{
	UI_SHOP_MENU,      // a menu of actions and settings (the game menu, the arcade's, options, the mouse, keys)
	UI_SHOP_UPGRADE,   // the parts to upgrade: tabs, the selected one's choices beside the ship
	UI_SHOP_ITEMS,     // a part's choices with their costs: cards
	UI_SHOP_SPECS,     // the ship's specifications round the ship
	UI_SHOP_FILES,     // load or save: the slots
	UI_SHOP_MAP,       // the next level: the map and the destinations
	UI_SHOP_CUBES,     // the data cubes: their titles, the selected one's face
	UI_SHOP_CUBE,      // a data cube read
} UIShopPage;

// What 3D scene a screen shows (presented with it: rgpu_present_ui).
typedef enum
{
	UI_SCENE_NONE,
	UI_SCENE_SHIP,  // the store's ship as it is equipped
	UI_SCENE_SIM,   // the store's weapon simulator
} UISceneKind;

#define UI_SHOP_TABS 10
#define UI_CUBE_LINES 96

typedef struct
{
	UIShopPage page;
	UISceneKind scene;
	float scene_w;        // how wide what the scene shows is (screen pixels): the pane shows at least that
	long credits;         // shown at the top right (< 0: not shown)
	long credits_after;   // and what would be left after the change chosen (< 0: none)
	char ship[48];        // the ship's name
	char ship_class[32];  // and its class ("Light Fighter"), or ""
	char specs[2][256];   // ship specs: the ship's two texts
	bool gauges;          // the ship's shield and armor under it
	float shield, armor;  // 0-1
	// The parts to upgrade as tabs: the selected one, where the original takes the mouse on each (in
	// the parts' own list; w 0: not there).
	int tab_count, tab_selected;
	char tab[UI_SHOP_TABS][24];
	SDL_Rect tab_hit[UI_SHOP_TABS];
	// The front or rear weapon chosen: its power (of power_max), whether it goes down or up and for
	// how much, where the original takes the mouse on its arrows.
	bool power_on;
	int power, power_max;
	bool power_down, power_up, power_afford;
	long cost_down, cost_up;
	SDL_Rect hit_down, hit_up;
	char mode[40];        // the rear weapon's firing mode ("": none)
	float generator;      // the simulator's power (0-1; < 0: none)
	// A part of the screen's picture shown at the left (the map, a data cube's face; w 0: none), and a
	// line under it.
	SDL_Rect picture_part;
	char caption[48];
	// A data cube read: its lines, the first shown (fractional), how much of it is read, where its
	// Done is.
	int line_count;
	char lines[UI_CUBE_LINES][40];
	float line_first;
	int percent;
	char done[24];
	SDL_Rect hit_done;
	char note[80];        // a line under the list (the cubes' "no data"), or ""
} UIShop;

// A question over the screen (the store's quit and save): its text, a field being typed, two buttons.
typedef struct
{
	bool on;
	char title[64];
	char text[200];
	char field_label[24];
	char field[32];
	bool field_on, caret;
	char yes[24], no[24];
	int selected;          // 0 yes, 1 no, -1 neither (typing)
	SDL_Rect hit_yes, hit_no;
} UIDialog;

// A level's results.
#define UI_RESULT_ROWS 6
typedef struct
{
	char title[64];
	int row_count;
	char label[UI_RESULT_ROWS][40];
	char value[UI_RESULT_ROWS][40];
	int percent;   // enemies destroyed (< 0: not shown)
	int cubes;     // data cubes found (< 0: not shown)
	bool prompt;   // waits for a key
} UIResults;

// The in-game help's parts (what the HUD shows).
#define UI_HELP_PARTS 8
typedef struct
{
	int count;
	char title[UI_HELP_PARTS][40];
	char text[UI_HELP_PARTS][240];
} UIHelp;

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
	bool values_turn;  // the values turn with Left / Right (the in-game options), no pickers
	bool enter_turns;  // and with Enter too (their 3D page)
	char hint[112];    // a line at the foot (the store's help line), or ""
	bool hold;         // shown whatever the screen shows until released (ui_menu_release): it animates
	UIShop shop;
	UIDialog dialog;
	UIResults results;
	UIHelp help;
} UIMenu;

// A menu cleared for a screen: fill in its items, then publish it.
UIMenu *ui_menu_begin(UIScreenKind kind, const char *title);
UIItem *ui_menu_add(UIMenu *menu, UIItemKind kind, const char *label, int x, int y, int w, int h);
// Publishes the menu as `shown` shows it now (the screen it has just drawn), over `picture` (the
// screen's picture behind the menu: its texts are taken off it).
void ui_menu_publish(UIMenu *menu, const SDL_Surface *shown, const SDL_Surface *picture);
// A screen published with hold is no longer shown as such.
void ui_menu_release(void);
// A question over the screen published last: fill it in, then publish it with the screen as shown now
// (the screen published last stays under it).
UIDialog *ui_dialog_begin(void);
void ui_dialog_publish(const SDL_Surface *shown);

// For presenting (video.c): whether a screen shows the menu last published (then the 3D view
// presents it as such, rgpu_present_ui), and that the frame shown last was it (or not).
bool ui_screen_holds(const SDL_Surface *screen);
void ui_screen_shown(bool shown);
// The published screen is one over a level's 3D view (rgpu_present_3d_menu draws it).
bool ui_screen_over_level(void);
// The 3D scene it shows (the store's ship or weapon simulator).
UISceneKind ui_screen_scene(void);
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
// Or whether it scrolls the published screen's text (a data cube's: the store takes it).
bool ui_wheel_scrolls_text(void);

/* --- Building the overlay (render_gpu.c calls these) --------------------------------------- */

typedef struct
{
	float w, h;           // the window, points
	float pixel;          // a window pixel, points
	float picture[4];     // where the screen's picture shows (x, y, w, h), points
	float playfield[4];   // the 3D view's playfield (x, y, w, h), points (the HUD)
	bool menu_over;       // a menu of the game is over the level (the HUD stays under it)
} UIView;

// Whether the published screen draws the screen's picture filling the window's height (the title,
// setup...), else its own layout over a blurred copy of it (the store).
bool ui_screen_whole_picture(void);
// Where the published screen shows its 3D scene in the window (points: x, y, w, h), and the box of the
// screen it shows in it (screen pixels: the scene is laid out on it as on the screen). False: no scene.
bool ui_scene_pane(const UIView *view, float rect[4], float screen_box[4]);
// The published screen's widgets.
void ui_build_screen(const UIView *view);
// The modern HUD over a level.
void ui_build_hud(const UIView *view);
// The game shows its "game over" (the HUD shows it its own way): its text.
void ui_note_game_over(const char *text);
// The pointer drawn into the frame (TYR3D_SOFTWARE_POINTER with the modern UI): at window point x, y.
void ui_build_pointer(const UIView *view, float x, float y, int shape);

/* --- The pointer -------------------------------------------------------------------------- */

// The modern UI's pointer as a picture: size x size pixels, RGBA (straight alpha), its hot spot.
// shape as the game's (MOUSE_POINTER_*). Returns false if the shape isn't known.
bool ui_pointer_image(int shape, int size, Uint32 *rgba, int *hot_x, int *hot_y);
// The pointer's size in window points (24 at the UI scale 100 %).
float ui_pointer_points(void);

#endif /* UI_H */
