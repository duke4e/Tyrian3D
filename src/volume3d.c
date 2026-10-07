/*
 * Tyrian3D: volumetric sprites. See volume3d.h.
 */
#include "volume3d.h"

#include "palette.h"

#include <math.h>
#include <string.h>

// Same decoding as blit_sprite2_clip: each byte holds an opaque pixel count (high nibble) and a
// transparent skip (low nibble); a zero count ends the row; 0x0f ends the sprite.
static void decode_cell(const Sprite2_array *sheet, unsigned int index, int ox, int oy, Uint8 *indices, Uint8 *cover)
{
	if (sheet->data == NULL || index == 0 || 2 * index > sheet->size)
		return;
	const Uint16 offset = SDL_Swap16LE(((const Uint16 *)sheet->data)[index - 1]);
	if (offset >= sheet->size)
		return;

	const Uint8 *data = sheet->data + offset;
	const Uint8 *end = sheet->data + sheet->size;
	int x = 0, y = 0;
	for (; data < end && *data != 0x0f; ++data)
	{
		x += *data & 0x0f;
		int count = (*data >> 4) & 0x0f;
		if (count == 0)
		{
			y += 1;
			x -= V3D_CELL_W;
			continue;
		}
		while (count-- && data + 1 < end)
		{
			++data;
			if (x >= 0 && x < V3D_CELL_W && y >= 0 && y < V3D_CELL_H)
			{
				const int i = (oy + y) * V3D_ATLAS_W + ox + x;
				indices[i] = *data;
				cover[i] = 1;
			}
			++x;
		}
	}
}

void v3d_decode_sheet(const Sprite2_array *sheet, Uint8 *indices, Uint8 *cover)
{
	memset(indices, 0, V3D_ATLAS_W * V3D_ATLAS_H);
	memset(cover, 0, V3D_ATLAS_W * V3D_ATLAS_H);
	if (sheet->data == NULL || sheet->size < 2)
		return;

	const unsigned int count = SDL_min((unsigned int)SDL_Swap16LE(((const Uint16 *)sheet->data)[0]) / 2,
	                                   (unsigned int)(V3D_COLUMNS * V3D_ROWS));
	for (unsigned int i = 1; i <= count; ++i)
		decode_cell(sheet, i, (int)((i - 1) % V3D_COLUMNS) * V3D_CELL_W, (int)((i - 1) / V3D_COLUMNS) * V3D_CELL_H, indices, cover);
}

static float luminance(Uint8 palette_index)
{
	const Uint8 *c = (const Uint8 *)&rgb_palette[palette_index];
	return (0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2]) / 255.0f;
}

int v3d_build_mesh(const Uint8 *sheet_indices, const Uint8 *sheet_cover, unsigned int index, bool large,
                   V3DStyle style, V3DVertex *vertices, int *vertex_count, Uint32 *indices)
{
	*vertex_count = 0;
	if (index == 0 || index > V3D_COLUMNS * V3D_ROWS)
		return 0;

	const int w = large ? 2 * V3D_CELL_W : V3D_CELL_W;
	const int h = large ? 2 * V3D_CELL_H : V3D_CELL_H;
	const int ox = (int)((index - 1) % V3D_COLUMNS) * V3D_CELL_W;
	const int oy = (int)((index - 1) / V3D_COLUMNS) * V3D_CELL_H;
	if (ox + w > V3D_ATLAS_W || oy + h > V3D_ATLAS_H)
		return 0;

	#define COVERED(x, y) ((x) >= 0 && (x) < w && (y) >= 0 && (y) < h && sheet_cover[(oy + (y)) * V3D_ATLAS_W + ox + (x)])
	#define CORNER(cx, cy) ((cy) * (w + 1) + (cx))

	// Distance of each pixel corner from the silhouette's edge (two-pass chamfer).
	float distance[V3D_MAX_VERTICES];
	for (int cy = 0; cy <= h; ++cy)
		for (int cx = 0; cx <= w; ++cx)
		{
			const bool inside = COVERED(cx - 1, cy - 1) && COVERED(cx, cy - 1) && COVERED(cx - 1, cy) && COVERED(cx, cy);
			distance[CORNER(cx, cy)] = inside ? 1e9f : 0.0f;
		}
	const float diagonal = 1.41421356f;
	for (int cy = 0; cy <= h; ++cy)
		for (int cx = 0; cx <= w; ++cx)
		{
			float *d = &distance[CORNER(cx, cy)];
			if (cx > 0)                      *d = SDL_min(*d, distance[CORNER(cx - 1, cy)] + 1);
			if (cy > 0)                      *d = SDL_min(*d, distance[CORNER(cx, cy - 1)] + 1);
			if (cx > 0 && cy > 0)            *d = SDL_min(*d, distance[CORNER(cx - 1, cy - 1)] + diagonal);
			if (cx < w && cy > 0)            *d = SDL_min(*d, distance[CORNER(cx + 1, cy - 1)] + diagonal);
		}
	for (int cy = h; cy >= 0; --cy)
		for (int cx = w; cx >= 0; --cx)
		{
			float *d = &distance[CORNER(cx, cy)];
			if (cx < w)                      *d = SDL_min(*d, distance[CORNER(cx + 1, cy)] + 1);
			if (cy < h)                      *d = SDL_min(*d, distance[CORNER(cx, cy + 1)] + 1);
			if (cx < w && cy < h)            *d = SDL_min(*d, distance[CORNER(cx + 1, cy + 1)] + diagonal);
			if (cx > 0 && cy < h)            *d = SDL_min(*d, distance[CORNER(cx - 1, cy + 1)] + diagonal);
		}

	// The silhouette is a short wall (rim) so edge pixels stay flat and crisp; inside it the top
	// rises in a rounded profile to full height a few pixels in, plus a little relief from the
	// brightness of the surrounding pixels (dark detail sits lower).
	const bool flat = style == V3D_STYLE_FLAT;
	const float rim = flat ? 0.25f : (large ? 1.5f : 1.0f);
	const float max_height = flat ? (large ? 1.5f : 1.0f) : (large ? 5.0f : 3.0f);
	const float round_distance = large ? 4.0f : 2.5f;
	const float relief = flat ? 0.8f : (large ? 1.0f : 0.6f);
	float height[V3D_MAX_VERTICES];
	for (int cy = 0; cy <= h; ++cy)
		for (int cx = 0; cx <= w; ++cx)
		{
			const float t = SDL_min(distance[CORNER(cx, cy)] / round_distance, 1.0f);
			float value = rim + (max_height - rim) * sqrtf(1.0f - (1.0f - t) * (1.0f - t));
			if (t > 0)
			{
				float lum = 0;
				int n = 0;
				for (int py = cy - 1; py <= cy; ++py)
					for (int px = cx - 1; px <= cx; ++px)
						if (COVERED(px, py))
						{
							lum += luminance(sheet_indices[(oy + py) * V3D_ATLAS_W + ox + px]);
							++n;
						}
				if (n > 0)
					value += relief * t * (lum / n - 0.5f);
			}
			height[CORNER(cx, cy)] = SDL_max(value, rim * 0.5f);
		}

	// Vertices at every corner (unused ones are harmless), centred on the sprite.
	int vc = 0;
	for (int cy = 0; cy <= h; ++cy)
		for (int cx = 0; cx <= w; ++cx)
		{
			const float hl = height[CORNER(SDL_max(cx - 1, 0), cy)], hr = height[CORNER(SDL_min(cx + 1, w), cy)];
			const float hu = height[CORNER(cx, SDL_max(cy - 1, 0))], hd = height[CORNER(cx, SDL_min(cy + 1, h))];
			const float span_x = (float)(SDL_min(cx + 1, w) - SDL_max(cx - 1, 0));
			const float span_z = (float)(SDL_min(cy + 1, h) - SDL_max(cy - 1, 0));
			float n[3] = { -(hr - hl) / span_x, 1.0f, -(hd - hu) / span_z };
			const float length = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);

			V3DVertex *v = &vertices[vc++];
			memset(v, 0, sizeof(*v));
			v->position[0] = cx - w / 2.0f;
			v->position[1] = height[CORNER(cx, cy)];
			v->position[2] = cy - h / 2.0f;
			v->normal[0] = n[0] / length;
			v->normal[1] = n[1] / length;
			v->normal[2] = n[2] / length;
			v->uv[0] = (float)(ox + cx) / V3D_ATLAS_W;
			v->uv[1] = (float)(oy + cy) / V3D_ATLAS_H;
			v->tangent[0] = 1;
			v->tangent[3] = 1;
			v->color[0] = v->color[1] = v->color[2] = v->color[3] = 1;
		}

	// Two triangles per covered pixel.
	int ic = 0;
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			if (!COVERED(x, y))
				continue;
			const Uint32 a = CORNER(x, y), b = CORNER(x + 1, y), c = CORNER(x + 1, y + 1), d = CORNER(x, y + 1);
			indices[ic++] = a;
			indices[ic++] = b;
			indices[ic++] = c;
			indices[ic++] = a;
			indices[ic++] = c;
			indices[ic++] = d;
		}

	// Walls down to the base on every edge facing an empty pixel, in that pixel's colour.
	static const int edges[4][2] = { { 0, -1 }, { 1, 0 }, { 0, 1 }, { -1, 0 } };  // top, right, bottom, left
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			if (!COVERED(x, y))
				continue;
			const float u = (ox + x + 0.5f) / V3D_ATLAS_W, v = (oy + y + 0.5f) / V3D_ATLAS_H;
			for (int e = 0; e < 4; ++e)
			{
				if (COVERED(x + edges[e][0], y + edges[e][1]))
					continue;
				int x0, y0, x1, y1;
				switch (e)  // edge corners, clockwise seen from above
				{
				case 0:  x0 = x;     y0 = y;     x1 = x + 1; y1 = y;     break;
				case 1:  x0 = x + 1; y0 = y;     x1 = x + 1; y1 = y + 1; break;
				case 2:  x0 = x + 1; y0 = y + 1; x1 = x;     y1 = y + 1; break;
				default: x0 = x;     y0 = y + 1; x1 = x;     y1 = y;     break;
				}
				const float corner_x[2] = { x0 - w / 2.0f, x1 - w / 2.0f };
				const float corner_z[2] = { y0 - h / 2.0f, y1 - h / 2.0f };
				const float top[2] = { height[CORNER(x0, y0)], height[CORNER(x1, y1)] };
				const Uint32 base = (Uint32)vc;
				for (int k = 0; k < 4; ++k)
				{
					const int side = (k == 1 || k == 2) ? 1 : 0;
					V3DVertex *wv = &vertices[vc++];
					memset(wv, 0, sizeof(*wv));
					wv->position[0] = corner_x[side];
					wv->position[1] = k < 2 ? top[side] : 0.0f;
					wv->position[2] = corner_z[side];
					wv->normal[0] = (float)edges[e][0];
					wv->normal[2] = (float)edges[e][1];
					wv->uv[0] = u;
					wv->uv[1] = v;
					wv->tangent[0] = 1;
					wv->tangent[3] = 1;
					wv->color[0] = wv->color[1] = wv->color[2] = wv->color[3] = 1;
				}
				// k: 0 top-start, 1 top-end, 2 base-end, 3 base-start
				indices[ic++] = base;
				indices[ic++] = base + 1;
				indices[ic++] = base + 2;
				indices[ic++] = base;
				indices[ic++] = base + 2;
				indices[ic++] = base + 3;
			}
		}
	*vertex_count = vc;
	#undef COVERED
	#undef CORNER
	return ic;
}
