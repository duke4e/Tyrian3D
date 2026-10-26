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
// The rectangle (window points) a 320x200 screen fills in a window: 8:5, covering the window (or its 16:9 middle
// on ultrawide), centred, so a part of it may lie outside the window.
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
	// Over their own pictures (filling the window's height) too:
	UI_SCREEN_SCORES,      // the high scores: a board (UIScores)
	UI_SCREEN_SCORE_NAME,  // a high score's name being typed (UIDialog, its score in note)
	UI_SCREEN_STORY,       // the story texts between levels, the warnings, an episode's end (UIStory)
	UI_SCREEN_CARD,        // a title card: the next episode, the Super Arcade's ships and codes, the rogue
	                       // run's messages (UICard)
	UI_SCREEN_LOAD,        // load a game (the title's): the slots, the players' pages (UIPaging)
	UI_SCREEN_JUKEBOX,     // the jukebox over its stars (UIJukebox)
	UI_SCREEN_HELP,        // the instructions: a page of help texts (UIHelp, UIPaging)
	UI_SCREEN_CREDITS,     // the credits rolling (UICredits)
	UI_SCREEN_ROGUE,       // the rogue mode's screens (UIRogue)
	UI_SCREEN_DESTRUCT,    // Destruct, the secret artillery duel: its pages and its HUD (UIDestruct)
	UI_SCREEN_SECRETS,     // the secrets found and still locked (UISecrets, secrets.c)
	UI_SCREEN_ENDING,      // the game's ending animation as a 3D scene (jukebox3d.h), nothing over it
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
	int tier;                // how rare (the rogue run's cards: 1 common, 2 rare, 3 epic; 0 none)
	char badge[24];          // a word on it (a card's kind: "Front Gun"), or ""
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
	// Two players: what each has (the ships show side by side), and the Super Arcade's ship info (the
	// original's help boxes: its main and special weapons; super[0] "" none).
	int player_count;
	struct
	{
		char name[24];     // "Player 1"
		char ship[48];
		char score[24];
		char weapon[40];   // its gun and the gun's power
		int power, power_max;
		int lives;         // extra lives (< 0: not shown)
		int bombs;
		char input[24];    // the input device it plays with
	} players[2];
	char super_title[32];  // "Super Arcade Mode"
	char super[2][2][40];  // label and value: "Main Weapon:" "Laser", "Special Weapon:" "..."
	int super_special;     // the special weapon (its icon), or 0
	// The data cubes' player (the store's cubes read aloud: voiceover.h): shown, the cube playing (< 0:
	// none) of how many, paused, how far (0-1), its title.
	bool cube_player;
	int cube_playing, cube_count;
	bool cube_paused;
	float cube_progress;
	char cube_title[48];
	// The next level's map (UI_SHOP_MAP), drawn by the UI itself when map_planet_count > 0, in the original's map
	// window (picture_part, screen pixels): each planet's sprite (PLANET_SHAPES, its frame now), middle and size,
	// whether it is a destination (the selected one) or where the ship is; the routes' dots (lit: the selected
	// route as far as it has come); the grid's scroll (the original's navX and navY halved).
#define UI_MAP_PLANETS 24
#define UI_MAP_DOTS 64
	int map_planet_count;
	struct
	{
		int sprite;
		float x, y, w, h;
		bool destination, selected, origin;
	} map_planet[UI_MAP_PLANETS];
	int map_dot_count;
	struct
	{
		float x, y;
		bool lit, route;
	} map_dot[UI_MAP_DOTS];
	float map_grid_x, map_grid_y;
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
	char note_label[32];   // a value shown large over the field (a high score), or ""
	char note[32];
	bool actions;          // the buttons are the UI's own (ui_take_press: UI_ACTION_YES / _NO), not the original's
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

// The in-game help's parts (what the HUD shows); the instructions' page of help texts.
#define UI_HELP_PARTS 8
typedef struct
{
	int count;
	char title[UI_HELP_PARTS][40];
	char text[UI_HELP_PARTS][240];
} UIHelp;

// Pages of a screen (the high scores' boards, the saved games' players, the instructions' pages): which
// of how many, their names as tabs (or none), the original's paging controls where it takes the mouse.
#define UI_PAGES 8
typedef struct
{
	int index, count;
	char tab[UI_PAGES][24];     // ("" for all: no tabs, a counter)
	bool tabs_click;            // a tab clicked goes to its page (ui_take_press: UI_ACTION_PAGE + n)
	bool prev, next;            // the controls shown
	SDL_Rect hit_prev, hit_next;
	char label[40];             // "Page 3 of 8", or ""
} UIPaging;

// The high scores: a board's tables (one and two players).
#define UI_SCORE_ROWS 3
typedef struct
{
	char heading[24];
	int count;
	char score[UI_SCORE_ROWS][16];
	char name[UI_SCORE_ROWS][32];
	char rank[UI_SCORE_ROWS][24];  // the difficulty it was played at
	int tier[UI_SCORE_ROWS];       // and its number (0-10), for its colour
} UIScoreTable;

typedef struct
{
	int table_count;
	UIScoreTable table[2];
	int new_table, new_row;  // the entry just made (-1: none)
	bool prompt;             // waits for a key
} UIScores;

// A story text between levels (the episode script's ]W and ]Q), shown as the original reveals it.
typedef enum
{
	UI_STORY_TEXT,     // a story text over its picture
	UI_STORY_WARNING,  // a warning (the original flashes bars and sounds an alarm)
	UI_STORY_ENDING,   // an episode's end: the score, then a hint
} UIStoryKind;

#define UI_STORY_LINES 12
typedef struct
{
	UIStoryKind kind;
	int line_count;
	char lines[UI_STORY_LINES][64];
	int shown_line;    // the lines before it shown whole ...
	int shown_chars;   // ... and of it this many characters (shown_line >= line_count: all)
	bool prompt;       // all shown, waits for a key
	bool top;          // the original shows it at the screen's top (its red texts)
	int score_lines;   // UI_STORY_ENDING: the first lines are the score(s), "Your total Score: 123"
} UIStory;

// A title card: lines under the title (the menu's crumb and title), a sprite of the game, a code word.
#define UI_CARD_LINES 6
typedef struct
{
	int line_count;
	char lines[UI_CARD_LINES][80];
	char code[24];           // a word in the lines to type, highlighted (""none)
	const void *icon_sheet;  // a sprite of the game (2x2: a ship), or NULL
	int icon_sprite;
	bool prompt;             // waits for a key
	bool large;              // the title large (an episode's name)
} UICard;

// The jukebox.
typedef struct
{
	int song, song_count;  // the song playing (0-based)
	bool sfx;              // the sound effects' mode: sfx_number (0-based) is the one chosen
	int sfx_number, sfx_count;
	char sfx_title[24];
	bool hidden;           // the texts hidden (Space): only the stars
	bool stopped, fading, fade_looped;
	char look[24];         // the look of its visuals (jukebox3d.h), V changes it
} UIJukebox;

// The credits rolling: the lines on the screen, where (screen pixels, their middle x and their top y).
#define UI_CREDIT_LINES 12
typedef struct
{
	int count;
	char text[UI_CREDIT_LINES][68];
	float x[UI_CREDIT_LINES], y[UI_CREDIT_LINES];
	int colour[UI_CREDIT_LINES];  // the original's colour (its palette's hue)
	char note[48];                // a line at the bottom ("Levels in Episode ..."), or ""
} UICredits;

// The rogue mode's screens.
typedef enum
{
	UI_ROGUE_MENU,     // the rogue run's menu (items), its profile
	UI_ROGUE_UNLOCKS,  // the unlocks (items: their cost or owned)
	UI_ROGUE_MAP,      // the act's map: its nodes, the next to go to
	UI_ROGUE_CARDS,    // a pick of cards (items), or a merchant's
} UIRoguePage;

#define UI_ROGUE_NODES 24
#define UI_ROGUE_STATS 5
typedef struct
{
	UIRoguePage page;
	int stat_count;           // chips at the top: "CORES 12"
	char stat_label[UI_ROGUE_STATS][16], stat_value[UI_ROGUE_STATS][16];
	char text[2][96];         // a description, or ""
	char subheading[64];
	bool merchant;
	char info[96];            // the map: what the selected node is
	int node_count;
	struct
	{
		float x, y;           // its middle (screen pixels)
		float r;              // its planet's radius
		char name[16];
		int kind;             // 0 a level, 1 elite, 2 merchant, 3 boss
		bool can_go, selected, visited;
		int planet;           // its planet's sprite (PLANET_SHAPES), drawn anew over the map's, or -1
		float planet_w, planet_h;  // as the map draws it (screen pixels)
	} nodes[UI_ROGUE_NODES];
	float ship_x, ship_y;     // where the ship is (screen pixels)
} UIRogue;

// Destruct (destruct.c): its pages over its arena, and the HUD while a battle is on.
typedef enum
{
	UI_DESTRUCT_PLAY,   // a battle: the HUD
	UI_DESTRUCT_INTRO,  // its title and how to get help (any key)
	UI_DESTRUCT_MODES,  // the battle to play: the items, each with its hint
	UI_DESTRUCT_HELP,   // both sides' keys (any key)
	UI_DESTRUCT_PAUSE,  // paused (any key)
} UIDestructPage;

#define UI_DESTRUCT_KEYS 5
typedef struct
{
	bool cpu;                 // played by the computer
	int score;
	int units, units_left;    // its units (not the satellites), how many still stand
	char unit[24];            // the unit chosen ("Tank"), or "" when none stands
	int unit_sprite;          // the unit's sprite and its weapon's icon in the game's sheet (UIDestruct.sheet)
	int weapon_sprite;
	char weapon[16];
	bool aims;                // its angle can be changed
	float angle;              // degrees above the horizon, towards the other side
	bool powered;             // its power can be changed
	float power;              // 0-1
	float armor;              // 0-1
	char help_title[24], help_note[48];  // its keys (the help page)
	char help_key[UI_DESTRUCT_KEYS][24], help_action[UI_DESTRUCT_KEYS][40];
} UIDestructSide;

typedef struct
{
	UIDestructPage page;
	const void *sheet;        // the game's sprites for the icons (a Sprite2_array)
	char mode[24];            // the battle being played
	int winner;               // the round is over and this side won it (0 left, 1 right), or -1
	UIDestructSide side[2];
	char lines[2][64];        // the intro's lines
	char help_footer[80];
} UIDestruct;

// The secrets (the title's Secrets: secrets.c): their kinds as tabs, how many of each are found of how many,
// all; the rows are the menu's items (label: its name or "???", value: what or where it is, value2: a share
// found or "", owned: found, hint: how it was found or where to look).
#define UI_SECRET_TABS 4
typedef struct
{
	int tab, tab_count;
	char tab_names[UI_SECRET_TABS][24];
	int found[UI_SECRET_TABS], total[UI_SECRET_TABS];
	int all_found, all_total;
} UISecrets;

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
	// A palette colour the menu's text uses: the menu fades in and out as it does (fade_palette), against
	// the palette it fades to (NULL: colors; the jukebox's own).
	Uint8 text_color;
	const SDL_Color *palette;
	// A point of the screen the original takes for nothing (where the mouse is off the widgets).
	SDL_Point nowhere;
	bool values_turn;  // the values turn with Left / Right (the in-game options), no pickers
	bool enter_turns;  // and with Enter too (their 3D page)
	bool preview;      // the menu at the playfield's side, the 3D view behind it bright (the in-game graphics)
	char hint[112];    // a line at the foot (the store's help line), or ""
	bool hold;         // shown whatever the screen shows until released (ui_menu_release): it animates
	int wheel;         // what the mouse wheel does on it (UI_WHEEL_*)
	UIShop shop;
	UIDialog dialog;
	UIResults results;
	UIHelp help;
	UIPaging paging;
	int rows;  // the setup's pages as tabs: the panel holds this many rows, so it keeps its size from tab to tab
	UIScores scores;
	UIStory story;
	UICard card;
	UIJukebox jukebox;
	UICredits credits;
	UIRogue rogue;
	UIDestruct destruct;
	UISecrets secrets;
} UIMenu;

// What the wheel does over a screen: moves through its items as Up and Down do (the default, with more
// than one item), turns as Left and Right do (pages, the cards in a row), or nothing.
enum { UI_WHEEL_UP_DOWN, UI_WHEEL_LEFT_RIGHT, UI_WHEEL_NONE };

// Widgets of the UI's own on a screen (the original takes no mouse there): the screen's code takes a
// click on one (ui_take_press) as what it is; elsewhere the original takes the mouse as ever.
enum
{
	UI_ACTION_YES = 1, UI_ACTION_NO,  // a question's buttons
	UI_ACTION_BACK,                   // leave the screen
	UI_ACTION_PREV, UI_ACTION_NEXT,   // the previous, the next (song...)
	UI_ACTION_STOP, UI_ACTION_RESTART, UI_ACTION_FADE, UI_ACTION_FADE_LOOPED, UI_ACTION_SFX, UI_ACTION_PLAY_SFX,
	UI_ACTION_HIDE,
	UI_ACTION_LOOK,                   // the jukebox's visuals' next look
	UI_ACTION_PLAY_PAUSE,             // play or pause (the store's data cube player)
	UI_ACTION_PAGE = 32,              // + n: page (tab) n
	UI_ACTION_ITEM = 64,              // + n: item (a song) n
};
// The UI's own widget the left mouse button was pressed on last, once (then 0); 0 when none.
int ui_take_press(void);
// (keyboard.c: a mouse button pressed where the pointer was mapped last.)
void ui_note_press(int button);
// A screen of stage 3 is over: what it published is no longer shown (whatever the screen shows next).
void ui_screen_done(void);
// The screen published last is of that kind.
bool ui_published_is(UIScreenKind kind);
// What it published (NULL: nothing).
const UIMenu *ui_published(void);

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
// caller then treats it as the key *key: Up or Down, or Left or Right: UIMenu.wheel).
bool ui_wheel_moves(float y, SDL_Scancode *key);
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
// The game shows its "insert coin" over a demo (the HUD shows it its own way): its text.
void ui_note_insert_coin(const char *text);
// The pointer drawn into the frame (TYR3D_SOFTWARE_POINTER with the modern UI): at window point x, y.
void ui_build_pointer(const UIView *view, float x, float y, int shape);

/* --- The pointer -------------------------------------------------------------------------- */

// The modern UI's pointer as a picture: size x size pixels, RGBA (straight alpha), its hot spot.
// shape as the game's (MOUSE_POINTER_*). Returns false if the shape isn't known.
bool ui_pointer_image(int shape, int size, Uint32 *rgba, int *hot_x, int *hot_y);
// The pointer's size in window points (24 at the UI scale 100 %).
float ui_pointer_points(void);

#endif /* UI_H */
