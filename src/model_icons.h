/*
 * Tyrian3D: the modern UI's item icons rendered from the items' own 3D models (assets/models/icons/<model>.png, made by
 * TYR3D_RENDER_ICONS: render_gpu.c rgpu_render_icons; drawn by rgpu_ui_model_icon). The pictures are read and resized to
 * the size they are drawn at on a thread of their own, so a page showing new icons never waits for them.
 */
#ifndef MODEL_ICONS_H
#define MODEL_ICONS_H

#include <SDL3/SDL.h>

#include <stdbool.h>

// The icon picture at `path` (straight alpha) as `size` x `size` pixels with its colours multiplied by its alpha (RGBA8,
// as the UI's canvas blends them): true once it is made, with the pixels (the caller's, SDL_free), or with *pixels NULL if
// the picture can't be read; false while it is being made (it is asked for on the first call).
bool model_icon_take(const char *path, int size, Uint8 **pixels);

// The rectangle x0, y0 - x1, y1 (pixels, fractional) of a w x h picture (premultiplied RGBA, floats) resized into
// size x size pixels (Mitchell-Netravali): for TYR3D_RENDER_ICONS.
bool model_icon_resample(const float *rgba, int w, int h, double x0, double y0, double x1, double y1, float *out, int size);

#endif /* MODEL_ICONS_H */
