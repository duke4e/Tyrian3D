/*
 * Tyrian3D: the jukebox's visuals. See jukebox3d.h.
 */
#include "jukebox3d.h"

#include "loudness.h"
#include "models3d.h"
#include "musicviz.h"
#include "settings3d.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define PI_F 3.14159265f

/* --- Matrices (column-major) and colours ---------------------------------------------------- */

typedef struct { float m[16]; } M4;

static M4 m4_identity(void)
{
	return (M4){ { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 } };
}

static M4 m4_mul(const M4 *a, const M4 *b)
{
	M4 r;
	for (int c = 0; c < 4; ++c)
		for (int row = 0; row < 4; ++row)
		{
			float s = 0;
			for (int k = 0; k < 4; ++k)
				s += a->m[k * 4 + row] * b->m[c * 4 + k];
			r.m[c * 4 + row] = s;
		}
	return r;
}

// Turned about the axis (0 x, 1 y, 2 z), radians.
static M4 m4_rotation(int axis, float a)
{
	M4 r = m4_identity();
	const float c = cosf(a), s = sinf(a);
	const int i = (axis + 1) % 3, j = (axis + 2) % 3;
	r.m[i * 4 + i] = c;
	r.m[i * 4 + j] = s;
	r.m[j * 4 + i] = -s;
	r.m[j * 4 + j] = c;
	return r;
}

// Scaled by s, turned by `turn` (or not: NULL), at p.
static M4 m4_place(const float p[3], const M4 *turn, float sx, float sy, float sz)
{
	M4 r = turn != NULL ? *turn : m4_identity();
	for (int k = 0; k < 3; ++k)
	{
		r.m[0 + k] *= sx;
		r.m[4 + k] *= sy;
		r.m[8 + k] *= sz;
	}
	r.m[12] = p[0];
	r.m[13] = p[1];
	r.m[14] = p[2];
	return r;
}

// The turn whose axes are x, y and z.
static M4 m4_columns(const float x[3], const float y[3], const float z[3])
{
	M4 r = m4_identity();
	for (int k = 0; k < 3; ++k)
	{
		r.m[0 + k] = x[k];
		r.m[4 + k] = y[k];
		r.m[8 + k] = z[k];
	}
	return r;
}

static float clamp01(float v)
{
	return v < 0 ? 0 : v > 1 ? 1 : v;
}

static float lerpf(float a, float b, float t)
{
	return a + (b - a) * t;
}

static float ease_to(float shown, float target, float dt, float tau)
{
	return shown + (target - shown) * (1 - expf(-dt / tau));
}

static Uint32 hash(Uint32 x)
{
	x ^= x >> 16;
	x *= 0x7feb352dU;
	x ^= x >> 15;
	x *= 0x846ca68bU;
	x ^= x >> 16;
	return x;
}

static float hash01(Uint32 x)
{
	return (hash(x) & 0xffffff) / (float)0x1000000;
}

// A hue (degrees), fully saturated, as linear RGB.
static void hue_rgb(float hue, float out[3])
{
	static const float n[3] = { 5, 3, 1 };
	for (int k = 0; k < 3; ++k)
	{
		const float h = fmodf(n[k] + hue / 60.0f, 6.0f);
		const float v = 1 - clamp01(SDL_min(h, 4 - h));
		out[k] = v * v;  // (roughly linear)
	}
}

// The bars' heat: deep amber, gold, then nearly white, as linear RGB.
static void heat(float v, float out[3])
{
	static const float stops[4][3] = { { 0.30f, 0.07f, 0.01f }, { 0.95f, 0.36f, 0.05f }, { 1.0f, 0.70f, 0.22f }, { 1.0f, 0.93f, 0.75f } };
	const float x = clamp01(v) * 3;
	const int i = SDL_min((int)x, 2);
	for (int k = 0; k < 3; ++k)
		out[k] = lerpf(stops[i][k], stops[i + 1][k], x - i);
}

// The chip's channels' colours (degrees of hue).
static const float channel_hue[MUSICVIZ_CHANNELS] = { 32, 200, 330, 150, 270, 12, 180, 55, 300 };

/* --- The frame's scene ---------------------------------------------------------------------- */

static J3DItem items[J3D_MAX_ITEMS];
static J3DScene scene;
static MusicViz viz;
static float now_t;  // the scene's clock (seconds)

static J3DItem *add(J3DShape shape, J3DLook look, const M4 *m, float r, float g, float b, float a)
{
	if (scene.item_count >= J3D_MAX_ITEMS)
		return NULL;
	J3DItem *it = &items[scene.item_count++];
	it->shape = (Uint8)shape;
	it->look = (Uint8)look;
	it->textured = 0;
	it->model = -1;
	memcpy(it->m, m->m, sizeof(it->m));
	it->color[0] = r;
	it->color[1] = g;
	it->color[2] = b;
	it->color[3] = a;
	return it;
}

static void glow(const float p[3], float size, const float c[3], float k)
{
	const M4 m = m4_place(p, NULL, size, size, size);
	add(J3D_GLOW, J3D_ADDITIVE, &m, c[0] * k, c[1] * k, c[2] * k, 1);
}

static void light(const float p[3], float radius, const float c[3], float energy)
{
	if (scene.light_count >= J3D_MAX_LIGHTS || energy <= 0.01f)
		return;
	float *l = scene.lights[scene.light_count++];
	l[0] = p[0];
	l[1] = p[1];
	l[2] = p[2];
	l[3] = radius;
	l[4] = c[0];
	l[5] = c[1];
	l[6] = c[2];
	l[7] = energy;
}

// The camera at eye looking at target; the scene's middle shifted up the window by shift (NDC).
static void camera(const float eye[3], const float target[3], float fov_degrees, float aspect, float shift)
{
	float f[3] = { target[0] - eye[0], target[1] - eye[1], target[2] - eye[2] };
	float l = sqrtf(f[0] * f[0] + f[1] * f[1] + f[2] * f[2]);
	for (int k = 0; k < 3; ++k)
		f[k] /= l;
	float r[3] = { -f[2], 0, f[0] };  // forward x world up
	l = sqrtf(r[0] * r[0] + r[2] * r[2]);
	r[0] /= l;
	r[2] /= l;
	const float u[3] = { r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0] };
	M4 view = m4_identity();
	for (int k = 0; k < 3; ++k)
	{
		view.m[k * 4 + 0] = r[k];
		view.m[k * 4 + 1] = u[k];
		view.m[k * 4 + 2] = f[k];
	}
	view.m[12] = -(r[0] * eye[0] + r[1] * eye[1] + r[2] * eye[2]);
	view.m[13] = -(u[0] * eye[0] + u[1] * eye[1] + u[2] * eye[2]);
	view.m[14] = -(f[0] * eye[0] + f[1] * eye[1] + f[2] * eye[2]);
	const float t = tanf(fov_degrees * PI_F / 360.0f), near_plane = 0.5f, far_plane = 3000.0f;
	M4 projection = { { 0 } };
	projection.m[0] = 1.0f / (t * aspect);
	projection.m[5] = 1.0f / t;
	projection.m[9] = shift;
	projection.m[10] = far_plane / (far_plane - near_plane);
	projection.m[11] = 1.0f;
	projection.m[14] = -near_plane * far_plane / (far_plane - near_plane);
	const M4 vp = m4_mul(&projection, &view);
	memcpy(scene.view_projection, vp.m, sizeof(vp.m));
	memcpy(scene.position, eye, sizeof(scene.position));
	memcpy(scene.right, r, sizeof(scene.right));
	memcpy(scene.up, u, sizeof(scene.up));
}

// A band's value at a fraction of the spectrum (0 the lows, 1 the highs), between bands.
static float spectrum_at(const float *bands, float x)
{
	const float at = clamp01(x) * (MUSICVIZ_BANDS - 1);
	const int i = SDL_min((int)at, MUSICVIZ_BANDS - 2);
	return lerpf(bands[i], bands[i + 1], at - i);
}

/* --- The stars ------------------------------------------------------------------------------- */

#define STARS 900

static float star_dir[STARS][3], star_bright[STARS], star_rgb[STARS][3];

static void make_stars(void)
{
	for (int i = 0; i < STARS; ++i)
	{
		const float z = hash01(i * 3 + 1) * 2 - 1, a = hash01(i * 3 + 2) * 2 * PI_F, s = sqrtf(1 - z * z);
		star_dir[i][0] = s * cosf(a);
		star_dir[i][1] = z;
		star_dir[i][2] = s * sinf(a);
		const float b = hash01(i * 3 + 3);
		star_bright[i] = 0.25f + 1.6f * b * b * b;
		const float temperature = hash01(i * 7 + 5);
		const float warm[3] = { 1.0f, 0.78f, 0.5f }, cool[3] = { 0.62f, 0.75f, 1.0f };
		for (int k = 0; k < 3; ++k)
			star_rgb[i][k] = lerpf(cool[k], warm[k], temperature);
	}
}

// The stars round the camera, twinkling with the highs and the hi-hats.
static void sky(const float centre[3], float radius, float twinkle)
{
	for (int i = 0; i < STARS; ++i)
	{
		const float p[3] = { centre[0] + star_dir[i][0] * radius, centre[1] + star_dir[i][1] * radius, centre[2] + star_dir[i][2] * radius };
		const float tw = 0.75f + 0.25f * sinf(now_t * (1.5f + 3 * hash01(i + 911)) + i) + twinkle * hash01(i + 77);
		glow(p, radius * 0.0045f * (0.6f + star_bright[i] * 0.5f), star_rgb[i], star_bright[i] * tw * 0.9f);
	}
}

// Faint clouds of colour far behind it all.
static void nebula(const float centre[3], float k)
{
	static const float place[2][3] = { { -0.75f, 0.4f, -0.55f }, { 0.8f, 0.2f, -0.6f } };
	static const float tint[2][3] = { { 0.20f, 0.05f, 0.26f }, { 0.03f, 0.12f, 0.18f } };
	for (int i = 0; i < 2; ++i)
	{
		const float p[3] = { centre[0] + place[i][0] * 800, centre[1] + place[i][1] * 800, centre[2] + place[i][2] * 800 };
		glow(p, 800, tint[i], 0.22f * k);
	}
}

/* --- Look 0: the orrery ---------------------------------------------------------------------- */

#define ORRERY_BARS 72
#define RING_RADIUS 17.0f
#define PLANET_RADIUS 8.5f
#define TRAIL 22
#define SPARKS 160
#define SHOCKS 6
#define BAR_HEIGHT 14.0f

static struct
{
	float trail[MUSICVIZ_CHANNELS][TRAIL][3];
	int trail_at;
	float trail_in;
	float height[MUSICVIZ_CHANNELS];
	float spark[SPARKS][7];  // x, y, z, vx, vy, vz, age (negative: none)
	int spark_next;
	float shock[SHOCKS];     // ages, negative: none
	int shock_next;
	float flare, ripple_angle, ripple, twinkle, punch;
	Uint32 drums_seen[MUSICVIZ_DRUM_KINDS], beats_seen;
	bool started;
} orb;

static void spark_burst(int count, float speed)
{
	for (int n = 0; n < count; ++n)
	{
		float *s = orb.spark[orb.spark_next];
		orb.spark_next = (orb.spark_next + 1) % SPARKS;
		const Uint32 seed = (Uint32)(now_t * 1000) * 31 + n * 7;
		const float a = hash01(seed) * 2 * PI_F;
		const int bar = (int)(hash01(seed + 1) * ORRERY_BARS);
		const float d = SDL_min(bar, ORRERY_BARS - bar) / (ORRERY_BARS / 2.0f);
		const float h = 0.4f + spectrum_at(viz.bands, d) * BAR_HEIGHT;
		s[0] = sinf(a) * RING_RADIUS;
		s[1] = h;
		s[2] = -cosf(a) * RING_RADIUS;
		s[3] = sinf(a) * speed * (0.4f + hash01(seed + 2));
		s[4] = speed * (0.6f + hash01(seed + 3));
		s[5] = -cosf(a) * speed * (0.4f + hash01(seed + 2));
		s[6] = 0;
	}
}

static void orrery_frame(float aspect, float shift, float dt)
{
	if (!orb.started)
	{
		for (int i = 0; i < SPARKS; ++i)
			orb.spark[i][6] = -1;
		for (int i = 0; i < SHOCKS; ++i)
			orb.shock[i] = -1;
		orb.started = true;
	}
	// The drums: the kick (or a beat) a shock wave, the snare sparks, the cymbal a flare, the toms a
	// ripple round the ring, the hi-hats the stars.
	const bool kick = viz.drum_hits[MUSICVIZ_KICK] != orb.drums_seen[MUSICVIZ_KICK] || viz.beats != orb.beats_seen;
	if (kick)
	{
		// (A wave at most every 0.3 s: fast drums don't fill the ring with them.)
		const float *last = &orb.shock[(orb.shock_next + SHOCKS - 1) % SHOCKS];
		if (*last < 0 || *last > 0.3f)
		{
			orb.shock[orb.shock_next] = 0;
			orb.shock_next = (orb.shock_next + 1) % SHOCKS;
		}
		orb.punch = 1;
	}
	if (viz.drum_hits[MUSICVIZ_SNARE] != orb.drums_seen[MUSICVIZ_SNARE])
		spark_burst(26, 9);
	if (viz.drum_hits[MUSICVIZ_CYMBAL] != orb.drums_seen[MUSICVIZ_CYMBAL])
		orb.flare = 1;
	if (viz.drum_hits[MUSICVIZ_TOM] != orb.drums_seen[MUSICVIZ_TOM])
	{
		orb.ripple = 1;
		orb.ripple_angle = hash01((Uint32)(now_t * 997)) * 2 * PI_F;
	}
	if (viz.drum_hits[MUSICVIZ_HAT] != orb.drums_seen[MUSICVIZ_HAT])
		orb.twinkle = 1;
	memcpy(orb.drums_seen, viz.drum_hits, sizeof(orb.drums_seen));
	orb.beats_seen = viz.beats;
	orb.flare = SDL_max(0.0f, orb.flare - dt / 0.7f);
	orb.ripple = SDL_max(0.0f, orb.ripple - dt / 0.9f);
	orb.twinkle = SDL_max(0.0f, orb.twinkle - dt / 0.12f);
	orb.punch = SDL_max(0.0f, orb.punch - dt / 0.35f);

	// The camera: swaying slowly round the planet, a little nearer on a beat.
	const float yaw = 0.22f * sinf(now_t * 0.045f) + 0.06f * sinf(now_t * 0.13f);
	const float pitch = (21.0f + 3.0f * sinf(now_t * 0.07f)) * PI_F / 180;
	const float distance = 66.0f - 2.0f * orb.punch * orb.punch - 3.0f * viz.level;
	const float target[3] = { 0, 3.5f, 0 };
	const float eye[3] = { target[0] + sinf(yaw) * cosf(pitch) * distance, target[1] + sinf(pitch) * distance,
		                   target[2] + cosf(yaw) * cosf(pitch) * distance };
	camera(eye, target, 34.0f, aspect, shift);

	scene.sun[0] = 0.78f;
	scene.sun[1] = -0.32f;
	scene.sun[2] = 0.54f;
	scene.sun_color[0] = 1.0f;
	scene.sun_color[1] = 0.86f;
	scene.sun_color[2] = 0.66f;
	scene.sun_energy = 3.2f;
	scene.ambient[0] = 0.4f;
	scene.ambient[1] = 0.45f;
	scene.ambient[2] = 0.6f;
	scene.ambient_energy = 0.12f;
	scene.metalness = 0.6f;
	scene.roughness = 0.45f;
	scene.bloom = 2.9f;
	scene.bloom_threshold = 1.0f;
	scene.exposure = 1.0f;

	sky(target, 900, orb.twinkle * 1.5f + viz.high * 0.6f);
	nebula(target, 1.0f + viz.bass * 0.4f);

	// The planet, turning, and its halo breathing with the lows.
	{
		const float p[3] = { 0, 0, 0 };
		const M4 tilt = m4_rotation(2, 0.2f), spin = m4_rotation(1, now_t * 0.05f);
		const M4 turn = m4_mul(&tilt, &spin);
		const M4 m = m4_place(p, &turn, PLANET_RADIUS, PLANET_RADIUS, PLANET_RADIUS);
		J3DItem *it = add(J3D_SPHERE, J3D_LIT, &m, 1, 1, 1, 1);
		if (it != NULL)
			it->textured = J3D_TEXTURE_GAS_GIANT;
		const float halo[3] = { 0.16f, 0.42f, 0.75f };
		glow(p, PLANET_RADIUS * 2.6f, halo, 0.1f + viz.bass * 0.2f + orb.punch * 0.12f);
		const float flare[3] = { 0.8f, 0.9f, 1.0f };
		if (orb.flare > 0)
		{
			const float q[3] = { -PLANET_RADIUS * 0.6f, PLANET_RADIUS * 0.75f, -PLANET_RADIUS * 0.6f };
			glow(q, PLANET_RADIUS * 3.5f, flare, orb.flare * orb.flare * 0.5f);
		}
	}

	// The shock waves.
	{
		const float gold[3] = { 1.0f, 0.55f, 0.16f };
		for (int i = 0; i < SHOCKS; ++i)
		{
			if (orb.shock[i] < 0)
				continue;
			orb.shock[i] += dt;
			const float t = orb.shock[i] / 0.9f;
			if (t >= 1)
			{
				orb.shock[i] = -1;
				continue;
			}
			// A thin ring of sparks running out from the bars.
			const float r = RING_RADIUS + 1.5f + t * 24, fade = (1 - t) * (1 - t) * 0.9f;
			for (int d = 0; d < 96; ++d)
			{
				const float a = 2 * PI_F * (d + 0.5f * (i & 1)) / 96;
				const float q[3] = { sinf(a) * r, 0.3f + t * 1.5f, -cosf(a) * r };
				glow(q, 0.9f + t * 0.8f, gold, fade);
			}
		}
	}

	// The spectrum: bars round the ring, the lows at the back (tall, a crown behind the planet), the
	// highs in front, each side the same; their peaks floating above them.
	for (int k = 0; k < ORRERY_BARS; ++k)
	{
		const float a = 2 * PI_F * k / ORRERY_BARS;
		const float d = SDL_min(k, ORRERY_BARS - k) / (ORRERY_BARS / 2.0f);
		const float v = spectrum_at(viz.bands, d), peak = spectrum_at(viz.peaks, d);
		float ripple = 0;
		if (orb.ripple > 0)
		{
			float da = fabsf(fmodf(a - orb.ripple_angle - (1 - orb.ripple) * 2.5f + 7 * PI_F, 2 * PI_F) - PI_F);
			ripple = orb.ripple * expf(-da * da * 8);
		}
		const float h = 0.35f + v * BAR_HEIGHT, w = 2 * PI_F * RING_RADIUS / ORRERY_BARS * 0.55f, depth = 1.2f;
		const M4 turn = m4_rotation(1, PI_F - a);
		const float base[3] = { sinf(a) * RING_RADIUS, 0, -cosf(a) * RING_RADIUS };
		// The pedestal, lit.
		{
			const float p[3] = { base[0], 0.22f, base[2] };
			const M4 m = m4_place(p, &turn, w * 1.25f, 0.44f, depth * 1.25f);
			add(J3D_BOX, J3D_LIT, &m, 0.32f, 0.22f, 0.12f, 1);
		}
		float c[3];
		heat(0.12f + v * 0.82f + ripple * 0.3f, c);
		{
			// (Lit: the sun and the moons' light on its faces.)
			const float p[3] = { base[0], 0.44f + h / 2, base[2] };
			const M4 m = m4_place(p, &turn, w, h, depth);
			const float lit = 0.55f + 0.6f * v + ripple;
			add(J3D_BAR, J3D_LIT, &m, c[0] * lit, c[1] * lit, c[2] * lit, 1);
		}
		// Its top, brighter.
		{
			const float p[3] = { base[0], 0.44f + h + 0.1f, base[2] };
			const M4 m = m4_place(p, &turn, w * 1.06f, 0.2f, depth * 1.06f);
			const float k2 = 0.6f + 2.6f * v * v + ripple;
			add(J3D_BOX, J3D_UNLIT, &m, c[0] * k2, c[1] * k2, c[2] * k2, 1);
			if (v > 0.45f)
				glow(p, 1.2f + 2.5f * v, c, (v - 0.45f) * 0.5f);
		}
		if (peak > 0.04f && peak > v + 0.03f)
		{
			const float p[3] = { base[0], 0.44f + 0.35f + peak * BAR_HEIGHT + 0.4f, base[2] };
			const M4 m = m4_place(p, &turn, w, 0.06f, depth);
			const float pk = (0.35f + peak * 0.9f) * clamp01((peak - v - 0.03f) * 10);
			add(J3D_BOX, J3D_UNLIT, &m, 1.0f * pk, 0.62f * pk, 0.26f * pk, 1);
		}
	}

	// The channels: a moon each, round the planet, its height by its pitch, lit while its notes
	// sound and flashing as each starts, leaving a trail; and lighting what is near.
	orb.trail_in -= dt;
	const bool sample_trail = orb.trail_in <= 0;
	if (sample_trail)
	{
		orb.trail_in = 1.0f / 40;
		orb.trail_at = (orb.trail_at + 1) % TRAIL;
	}
	for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
	{
		const MusicVizChannel *c = &viz.channels[ch];
		const float r = 23.0f + ch * 2.3f, inclination = ((ch * 37) % 17 - 8) * PI_F / 180;
		const float a = ch * 2.39996f + now_t * 2 * PI_F / (38.0f + ch * 6.5f);
		const float target_h = c->drum != 0 ? 1.5f : SDL_clamp((c->note - 60) * 0.22f, -6.0f, 9.0f);
		orb.height[ch] = ease_to(orb.height[ch], target_h, dt, 0.25f);
		const float p[3] = { cosf(a) * r, sinf(a) * r * sinf(inclination) + 2 + orb.height[ch], sinf(a) * r * cosf(inclination) };
		float hue[3];
		hue_rgb(channel_hue[ch], hue);
		const float level = sqrtf(c->level), flash = c->flash * c->flash;
		const float size = 0.45f + 0.55f * level + 0.35f * flash;
		{
			const M4 m = m4_place(p, NULL, size, size, size);
			const float k = 0.2f + 1.2f * level + 1.6f * flash;
			add(J3D_SPHERE, J3D_UNLIT, &m, 0.25f + hue[0] * k, 0.25f + hue[1] * k, 0.25f + hue[2] * k, 1);
		}
		glow(p, 1.2f + 3.0f * level + 4.0f * flash, hue, 0.06f + 0.22f * level + 0.35f * flash);
		light(p, 26, hue, 0.4f + 4 * level * level + 6 * flash);
		if (sample_trail)
			memcpy(orb.trail[ch][orb.trail_at], p, sizeof(p));
		for (int i = 1; i < TRAIL; ++i)
		{
			const float *q = orb.trail[ch][(orb.trail_at - i + TRAIL) % TRAIL];
			if (q[0] == 0 && q[1] == 0 && q[2] == 0)
				continue;
			const float fade = 1 - (float)i / TRAIL;
			glow(q, (0.4f + level * 1.0f) * fade + 0.15f, hue, (0.03f + 0.14f * level) * fade * fade);
		}
	}

	// The sparks.
	const float white[3] = { 1.0f, 0.8f, 0.5f };
	for (int i = 0; i < SPARKS; ++i)
	{
		float *s = orb.spark[i];
		if (s[6] < 0)
			continue;
		s[6] += dt;
		if (s[6] > 1.1f)
		{
			s[6] = -1;
			continue;
		}
		s[4] -= 16 * dt;
		for (int k = 0; k < 3; ++k)
			s[k] += s[k + 3] * dt;
		const float fade = 1 - s[6] / 1.1f;
		glow(s, 0.45f * fade + 0.12f, white, 0.9f * fade);
	}
}

/* --- Look 1: the warp ------------------------------------------------------------------------ */

#define WARP_SEGMENTS 48
#define WARP_RINGS 96
#define WARP_RADIUS 9.0f
#define WARP_NOTES 192
#define WARP_STREAKS 260
#define RINGS_PER_SECOND 20.0f

typedef struct
{
	float z;              // along the flight (0 at the ship, falling behind: negative)
	float bands[WARP_SEGMENTS / 2 + 1];
	float flash;          // a drum's
	float hue;
	bool used;
} WarpRing;

typedef struct
{
	float z0, z1;  // its start's place and its end's (the end at the ship while it sounds)
	float angle, radius;
	int channel;
	bool sounding, used;
	float level;
} WarpNote;

static struct
{
	WarpRing rings[WARP_RINGS];
	int ring_next;
	float ring_in;
	WarpNote notes[WARP_NOTES];
	int note_next;
	int sounding[MUSICVIZ_CHANNELS];  // the note sounding on each channel, or -1
	Uint32 notes_seen[MUSICVIZ_CHANNELS];
	float streak[WARP_STREAKS][3];
	float speed, hue, flash, bank, kick, cymbal;
	Uint32 drums_seen[MUSICVIZ_DRUM_KINDS], beats_seen;
	bool started;
	int ship_model;
} warp;

// The tunnel's colours as the song goes on (r->hue 0-360 round them): teal, blue, violet, magenta,
// amber, back to teal.
static void tunnel_tint(float hue, float out[3])
{
	static const float stops[5][3] = { { 0.05f, 0.55f, 0.6f }, { 0.12f, 0.25f, 0.9f }, { 0.45f, 0.15f, 0.85f }, { 0.8f, 0.12f, 0.45f },
		                               { 0.9f, 0.45f, 0.1f } };
	const float x = fmodf(hue, 360.0f) / 72.0f;
	const int i = (int)x % 5, j = (i + 1) % 5;
	for (int k = 0; k < 3; ++k)
		out[k] = lerpf(stops[i][k], stops[j][k], x - (int)x);
}

// The ships of the game, one for each song.
static const char *const ship_names[] = { "talon", "uship", "gencore2", "stalker", "silver", "storm", "phoenix", "nortship", "dragon",
	                                      "dragonwing" };

static void warp_frame(float aspect, float shift, float dt)
{
	if (!warp.started)
	{
		for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
			warp.sounding[ch] = -1;
		for (int i = 0; i < WARP_STREAKS; ++i)
		{
			const float a = hash01(i * 5 + 1) * 2 * PI_F, r = 14 + hash01(i * 5 + 2) * 60;
			warp.streak[i][0] = cosf(a) * r;
			warp.streak[i][1] = sinf(a) * r;
			warp.streak[i][2] = -hash01(i * 5 + 3) * 400;
		}
		warp.started = true;
	}
	warp.ship_model = m3d_find_model(ship_names[song_playing % SDL_arraysize(ship_names)]);
	if (warp.ship_model < 0)
		warp.ship_model = m3d_find_model("talon");
	warp.speed = ease_to(warp.speed, 34 + 46 * viz.level + 20 * viz.bass, dt, 0.4f);
	warp.hue = fmodf(warp.hue + dt * (9 + 24 * viz.mid), 360.0f);
	const bool kick = viz.drum_hits[MUSICVIZ_KICK] != warp.drums_seen[MUSICVIZ_KICK] || viz.beats != warp.beats_seen;
	const bool snare = viz.drum_hits[MUSICVIZ_SNARE] != warp.drums_seen[MUSICVIZ_SNARE];
	if (viz.drum_hits[MUSICVIZ_CYMBAL] != warp.drums_seen[MUSICVIZ_CYMBAL])
		warp.cymbal = 1;
	memcpy(warp.drums_seen, viz.drum_hits, sizeof(warp.drums_seen));
	warp.beats_seen = viz.beats;
	if (kick)
		warp.kick = 1;
	warp.kick = SDL_max(0.0f, warp.kick - dt / 0.3f);
	warp.cymbal = SDL_max(0.0f, warp.cymbal - dt / 0.8f);

	// Everything falls behind the ship (towards the far end) as it flies on.
	const float dz = warp.speed * dt;
	for (int i = 0; i < WARP_RINGS; ++i)
		if (warp.rings[i].used && (warp.rings[i].z -= dz) < -420)
			warp.rings[i].used = false;
	for (int i = 0; i < WARP_NOTES; ++i)
	{
		WarpNote *n = &warp.notes[i];
		if (!n->used)
			continue;
		n->z0 -= dz;
		if (!n->sounding)
			n->z1 -= dz;
		if (n->z1 < -420)
			n->used = false;
	}
	// A ring of the spectrum now, so many a second (a drum's flashing).
	warp.ring_in -= dt;
	if (warp.ring_in <= 0 || kick || snare)
	{
		warp.ring_in = 1 / RINGS_PER_SECOND;
		WarpRing *r = &warp.rings[warp.ring_next];
		warp.ring_next = (warp.ring_next + 1) % WARP_RINGS;
		r->used = true;
		r->z = 0;
		for (int s = 0; s <= WARP_SEGMENTS / 2; ++s)
			r->bands[s] = spectrum_at(viz.bands, (float)s / (WARP_SEGMENTS / 2));
		r->flash = kick ? 1.0f : snare ? 0.6f : 0;
		r->hue = warp.hue;
	}
	// The channels' notes: a lane of light each, round the tunnel by its pitch, as long as it sounds.
	for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
	{
		const MusicVizChannel *c = &viz.channels[ch];
		WarpNote *was = warp.sounding[ch] >= 0 ? &warp.notes[warp.sounding[ch]] : NULL;
		if (was != NULL)
			was->level = c->level;
		if (was != NULL && (!c->on || c->notes != warp.notes_seen[ch]))
		{
			was->sounding = false;
			warp.sounding[ch] = -1;
		}
		if (c->notes != warp.notes_seen[ch] && c->on && c->drum == 0)
		{
			WarpNote *n = &warp.notes[warp.note_next];
			warp.sounding[ch] = warp.note_next;
			warp.note_next = (warp.note_next + 1) % WARP_NOTES;
			*n = (WarpNote){ .z0 = 0, .z1 = 0, .channel = ch, .sounding = true, .used = true, .level = c->level };
			// Round the tunnel by its pitch (an octave a third of the way), each channel a little apart.
			n->angle = (c->note - 60) / 12.0f * (2 * PI_F / 3) + ch * 0.07f + PI_F / 2;
			n->radius = WARP_RADIUS - 1.6f;
		}
		warp.notes_seen[ch] = c->notes;
	}

	// The camera before the ship, looking back along the tunnel; the ship swaying, rising on the lows.
	warp.bank = ease_to(warp.bank, 0.25f * sinf(now_t * 0.6f) + 0.15f * sinf(now_t * 1.7f) * viz.mid, dt, 0.3f);
	const float shake = warp.kick * warp.kick * 0.25f;
	const float eye[3] = { 3.2f + 1.5f * sinf(now_t * 0.11f) + shake * sinf(now_t * 70), 3.8f + 0.5f * sinf(now_t * 0.17f),
		                   14.0f - warp.kick * 0.6f };
	const float target[3] = { 0, 0.6f, -30 };
	camera(eye, target, 46.0f, aspect, shift);

	scene.sun[0] = 0.35f;
	scene.sun[1] = -0.8f;
	scene.sun[2] = -0.5f;
	scene.sun_color[0] = 1.0f;
	scene.sun_color[1] = 0.9f;
	scene.sun_color[2] = 0.8f;
	scene.sun_energy = 2.6f;
	scene.ambient[0] = 0.5f;
	scene.ambient[1] = 0.5f;
	scene.ambient[2] = 0.7f;
	scene.ambient_energy = 0.45f;
	scene.metalness = 0.3f;
	scene.roughness = 0.5f;
	scene.bloom = 2.9f;
	scene.bloom_threshold = 1.0f;
	scene.exposure = 1.0f;

	// The stars streaming past.
	for (int i = 0; i < WARP_STREAKS; ++i)
	{
		float *s = warp.streak[i];
		s[2] -= dz * 2.5f;
		if (s[2] < -420)
			s[2] += 440;
		const float len = 0.5f + warp.speed * 0.06f;
		const float p[3] = { s[0], s[1], s[2] };
		const M4 m = m4_place(p, NULL, 0.12f, 0.12f, len);
		const float k = (0.6f + viz.high * 0.8f) * clamp01((s[2] + 420) / 120) * (0.4f + hash01(i + 3) * 0.8f);
		add(J3D_BOX, J3D_UNLIT, &m, 0.7f * k, 0.8f * k, 1.0f * k, 1);
	}

	// The rings: the spectrum round the tunnel, the lows at the top, each side the same; their light
	// fading with distance.
	for (int i = 0; i < WARP_RINGS; ++i)
	{
		const WarpRing *r = &warp.rings[i];
		if (!r->used)
			continue;
		const float fade = expf(r->z / 140.0f), flash = r->flash * (0.6f + 0.4f * warp.kick);
		float tint[3];
		tunnel_tint(r->hue, tint);
		for (int s = 0; s < WARP_SEGMENTS; ++s)
		{
			const int b = SDL_min(s, WARP_SEGMENTS - s);
			const float v = r->bands[b];
			const float a = PI_F / 2 + 2 * PI_F * s / WARP_SEGMENTS;  // (s 0 at the top)
			const float len = 0.2f + v * 4.2f;
			const float rr = WARP_RADIUS + len / 2;
			const float p[3] = { cosf(a) * rr, sinf(a) * rr, r->z };
			const float across[3] = { -sinf(a), cosf(a), 0 }, axis[3] = { 0, 0, 1 }, out[3] = { cosf(a), sinf(a), 0 };
			const M4 turn = m4_columns(across, axis, out);
			const M4 m = m4_place(p, &turn, 2 * PI_F * WARP_RADIUS / WARP_SEGMENTS * 0.45f, 0.12f + flash * 0.25f, len);
			// The quiet in the song's colour, the loudest in the bars' heat.
			float c[3];
			heat(0.45f + 0.55f * v, c);
			const float k = (0.18f + 1.5f * v * v + flash * 0.9f + warp.cymbal * 0.3f) * fade;
			const float hot = clamp01((v - 0.5f) * 2);
			for (int q = 0; q < 3; ++q)
				c[q] = lerpf(tint[q] * 0.7f, c[q], hot * hot) * k;
			add(J3D_BAR, J3D_UNLIT, &m, c[0], c[1], c[2], 1);
		}
	}

	// The notes' lanes.
	for (int i = 0; i < WARP_NOTES; ++i)
	{
		const WarpNote *n = &warp.notes[i];
		if (!n->used)
			continue;
		float hue[3];
		hue_rgb(channel_hue[n->channel], hue);
		const float z0 = n->z0, z1 = SDL_max(n->z1, n->z0 + 0.4f);
		const float p[3] = { cosf(n->angle) * n->radius, sinf(n->angle) * n->radius, (z0 + z1) / 2 };
		const M4 m = m4_place(p, NULL, 0.28f, 0.28f, z1 - z0);
		const float k = (0.4f + 1.2f * sqrtf(n->level)) * expf(z0 / 160.0f) * (n->sounding ? 1.4f : 1.0f);
		add(J3D_BOX, J3D_UNLIT, &m, 0.2f + hue[0] * k, 0.2f + hue[1] * k, 0.2f + hue[2] * k, 1);
		if (n->sounding)
		{
			const float q[3] = { p[0], p[1], z1 };
			glow(q, 0.8f + 1.4f * sqrtf(n->level), hue, 0.2f);
			light(q, 16, hue, 1.5f + 4 * n->level);
		}
	}

	// The ship.
	if (warp.ship_model >= 0 && m3d_enabled)
	{
		const float p[3] = { 0, 0.4f + 0.5f * viz.bass + 0.2f * sinf(now_t * 1.3f), 0 };
		const M4 yaw = m4_rotation(1, PI_F + 0.25f), roll = m4_rotation(2, warp.bank), pitch = m4_rotation(0, 0.38f);
		M4 turn = m4_mul(&yaw, &roll);
		turn = m4_mul(&turn, &pitch);
		const M4 m = m4_place(p, &turn, 6.0f, 6.0f, 6.0f);
		J3DItem *it = add(J3D_MODEL, J3D_LIT, &m, 1, 1, 1, 1);
		if (it != NULL)
			it->model = (Sint16)warp.ship_model;
		const float engine[3] = { 1.0f, 0.55f, 0.2f };
		const float q[3] = { 0, p[1], -2.6f };
		glow(q, 2.5f + 3 * viz.level + 3 * warp.kick, engine, 0.2f + 0.35f * viz.level + 0.45f * warp.kick);
		light(q, 10, engine, 2 + 4 * viz.level + 4 * warp.kick);
		const float lamp[3] = { 1.0f, 0.85f, 0.65f };
		const float front[3] = { 0, 4, 8 };
		light(front, 24, lamp, 3);
	}
}

/* --- The game's ending (tyrend.anm) --------------------------------------------------------- */

static struct
{
	int ship_model;
	float t;
	Uint64 last;
} ending;

void jukebox3d_ending_start(int ship_model)
{
	ending.ship_model = ship_model;
	ending.t = 0;
	ending.last = 0;
}

float jukebox3d_ending_time(void)
{
	return ending.t;
}

// 0 before a, 1 after b, smoothly between.
static float smooth(float a, float b, float t)
{
	t = clamp01((t - a) / (b - a));
	return t * t * (3 - 2 * t);
}

static void mix3(const float a[3], const float b[3], float t, float out[3])
{
	for (int k = 0; k < 3; ++k)
		out[k] = lerpf(a[k], b[k], t);
}

static void normalize3(float v[3])
{
	const float l = sqrtf(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
	if (l > 0)
		for (int k = 0; k < 3; ++k)
			v[k] /= l;
}

// The turn of something flying along d (its nose; a model's nose is its -z), its up as near the world's as d
// allows, rolled about d.
static M4 flying_turn(const float d[3], float roll, float x[3], float y[3], float z[3])
{
	z[0] = -d[0], z[1] = -d[1], z[2] = -d[2];
	normalize3(z);
	float rx[3] = { z[2], 0, -z[0] };  // world up x z
	normalize3(rx);
	const float ry[3] = { z[1] * rx[2] - z[2] * rx[1], z[2] * rx[0] - z[0] * rx[2], z[0] * rx[1] - z[1] * rx[0] };
	const float c = cosf(roll), s = sinf(roll);
	for (int k = 0; k < 3; ++k)
	{
		x[k] = rx[k] * c + ry[k] * s;
		y[k] = -rx[k] * s + ry[k] * c;
	}
	return m4_columns(x, y, z);
}

// A point of a flying thing's frame (its axes x, y, z, at p).
static void at_local(const float p[3], const float x[3], const float y[3], const float z[3], float lx, float ly, float lz, float out[3])
{
	for (int k = 0; k < 3; ++k)
		out[k] = p[k] + x[k] * lx + y[k] * ly + z[k] * lz;
}

// The freighter: a long brown hull with a spine, its portholes lit lavender, a dim engine.
static void freighter(const float p[3], const float d[3])
{
	float x[3], y[3], z[3];
	const M4 turn = flying_turn(d, 0.35f, x, y, z);
	const M4 hull = m4_place(p, &turn, 16, 9, 78);
	J3DItem *plating = add(J3D_SPHERE, J3D_LIT, &hull, 0.62f, 0.42f, 0.24f, 1);
	if (plating != NULL)
		plating->textured = J3D_TEXTURE_GAS_GIANT;  // (the planet's bands round it: its plating)
	float q[3];
	at_local(p, x, y, z, 0, 7.6f, 4, q);
	const M4 spine = m4_place(q, &turn, 3.2f, 2.4f, 44);
	add(J3D_BOX, J3D_LIT, &spine, 0.34f, 0.24f, 0.13f, 1);
	for (int side = -1; side <= 1; side += 2)
	{
		at_local(p, x, y, z, side * 12.5f, -1.5f, 10, q);
		const M4 pod = m4_place(q, &turn, 3.0f, 3.0f, 26);
		add(J3D_SPHERE, J3D_LIT, &pod, 0.40f, 0.28f, 0.15f, 1);
	}
	// Ribs round the hull every few metres, a bridge over its front with a lit window.
	for (int i = 0; i < 9; ++i)
	{
		const float lz = -32 + i * 8.0f, along = lz / 39.0f;
		const float r = sqrtf(SDL_max(0.0f, 1 - along * along));
		at_local(p, x, y, z, 0, 0, lz, q);
		const M4 rib = m4_place(q, &turn, 16.5f * r, 9.3f * r, 1.1f);
		add(J3D_SPHERE, J3D_LIT, &rib, 0.30f, 0.21f, 0.12f, 1);
	}
	at_local(p, x, y, z, 0, 7.4f, -22, q);
	const M4 bridge = m4_place(q, &turn, 4.5f, 2.6f, 7);
	add(J3D_SPHERE, J3D_LIT, &bridge, 0.55f, 0.40f, 0.24f, 1);
	at_local(p, x, y, z, 0, 8.2f, -26.5f, q);
	const M4 window = m4_place(q, &turn, 3.2f, 0.45f, 0.6f);
	add(J3D_BOX, J3D_UNLIT, &window, 0.9f, 0.85f, 1.3f, 1);
	// Two rows of portholes along its flank facing the camera (-x, as it passes left of it).
	const float lavender[3] = { 0.75f, 0.70f, 1.0f };
	for (int row = 0; row < 2; ++row)
		for (int i = 0; i < 13; ++i)
		{
			const float lz = -27 + i * 4.5f, along = lz / 39.0f, ly = row == 0 ? 1.8f : -1.6f;
			const float r = sqrtf(SDL_max(0.0f, 1 - along * along - (ly / 9) * (ly / 9)));
			at_local(p, x, y, z, -16.1f * r, ly, lz, q);
			const M4 port = m4_place(q, &turn, 0.75f, 0.75f, 1.1f);
			add(J3D_SPHERE, J3D_UNLIT, &port, 0.85f, 0.8f, 1.2f, 1);
			glow(q, 2.2f, lavender, 0.07f);
		}
	at_local(p, x, y, z, 0, 0, 38, q);
	const float engine[3] = { 1.0f, 0.5f, 0.25f };
	glow(q, 10, engine, 0.25f);
}

const J3DScene *jukebox3d_ending_frame(float w, float h)
{
	static bool stars_made = false;
	if (!stars_made)
	{
		make_stars();
		stars_made = true;
	}
	const Uint64 now = SDL_GetTicksNS();
	const float dt = ending.last != 0 ? SDL_min((now - ending.last) / 1e9f, 0.1f) : 0;
	ending.last = now;
	ending.t += dt;
	now_t += dt;
	const float t = ending.t, aspect = h > 0 ? w / h : 16.0f / 9.0f;
	scene.item_count = 0;
	scene.light_count = 0;
	scene.items = items;

	// The ship: in from the right to beside the camera (3.0-6.2 s), its engines fired (6.4), away into the
	// distance towards a red star that flares (6.6-8.6).
	const float in_from[3] = { 46, -2, -64 }, in_to[3] = { -4, 1.5f, -40 };
	const float away_dir[3] = { 0.22f, 0.04f, -0.97f };  // (away from the planet, up to the left)
	const float s_in = smooth(3.0f, 6.2f, t);
	float ship[3];
	mix3(in_from, in_to, 1 - (1 - s_in) * (1 - s_in), ship);
	const float go = SDL_max(0.0f, t - 6.6f);
	for (int k = 0; k < 3; ++k)
		ship[k] += away_dir[k] * (go * go * 46 + go * 6);
	float heading[3];
	const float in_dir[3] = { -1.0f, 0.06f, -0.42f };
	mix3(in_dir, away_dir, smooth(5.6f, 6.8f, t), heading);
	normalize3(heading);
	const float roll = lerpf(0.7f, 0.12f, smooth(3.0f, 6.0f, t)) - 0.25f * smooth(6.6f, 7.6f, t);

	// The camera: still at first, the planet and the freighter; then after the ship, closing in on its rear.
	float eye[3] = { 0, 0, 0 }, target[3] = { -6, 2, -100 };
	const float follow = smooth(3.2f, 6.0f, t);
	float x[3], y[3], z[3];
	flying_turn(heading, roll, x, y, z);
	float close_eye[3];
	at_local(ship, x, y, z, 7.5f, 3.2f, 14, close_eye);
	if (t > 6.6f)  // (the camera stays where it was as the ship leaves)
	{
		float hold[3], hold_dir[3], hx[3], hy[3], hz[3];
		mix3(in_dir, away_dir, smooth(5.6f, 6.8f, 6.6f), hold_dir);
		normalize3(hold_dir);
		flying_turn(hold_dir, lerpf(0.7f, 0.12f, smooth(3.0f, 6.0f, 6.6f)), hx, hy, hz);
		mix3(in_from, in_to, 1, hold);
		at_local(hold, hx, hy, hz, 7.5f, 3.2f, 14, close_eye);
	}
	mix3(eye, close_eye, follow, eye);
	float look_at[3];
	at_local(ship, x, y, z, 0, 0, -8, look_at);
	mix3(target, look_at, smooth(3.0f, 4.6f, t), target);
	camera(eye, target, 50.0f, aspect, 0);

	scene.sun[0] = -0.5f;  // (the way its light goes: from the front, up to the right)
	scene.sun[1] = -0.4f;
	scene.sun[2] = -0.75f;
	scene.sun_color[0] = 1.0f;
	scene.sun_color[1] = 0.93f;
	scene.sun_color[2] = 0.82f;
	scene.sun_energy = 3.0f;
	scene.ambient[0] = 0.45f;
	scene.ambient[1] = 0.5f;
	scene.ambient[2] = 0.65f;
	scene.ambient_energy = 0.3f;
	scene.metalness = 0.45f;
	scene.roughness = 0.45f;
	scene.bloom = 3.2f;
	scene.bloom_threshold = 1.0f;
	// (In from black and out to it.)
	scene.exposure = smooth(0.0f, 0.6f, t) * (1 - smooth(8.4f, J3D_ENDING_SECONDS, t));

	sky(eye, 900, 0.1f);

	// The green planet up to the left.
	{
		const float p[3] = { -62, 34, -230 };
		// (Turned to show its largest continent, slowly turning on.)
		const M4 tilt = m4_rotation(2, 0.25f), spin = m4_rotation(1, 2.2f + t * 0.03f);
		const M4 turn = m4_mul(&tilt, &spin);
		const M4 m = m4_place(p, &turn, 21, 21, 21);
		J3DItem *it = add(J3D_SPHERE, J3D_LIT, &m, 1, 1, 1, 1);
		if (it != NULL)
			it->textured = J3D_TEXTURE_TERRAN;
		const float halo[3] = { 0.3f, 0.8f, 0.45f };
		glow(p, 54, halo, 0.08f);
	}

	// The freighter sweeping past from the top right to the bottom left (0.9-3.4 s).
	if (t > 0.6f && t < 3.8f)
	{
		const float from[3] = { 120, 44, -96 }, to[3] = { -150, -50, -62 };
		float p[3], d[3] = { to[0] - from[0], to[1] - from[1], to[2] - from[2] };
		mix3(from, to, (t - 0.6f) / 3.2f, p);
		normalize3(d);
		freighter(p, d);
	}

	// The ship, its engines, the red star it leaves for and the flash as it gets there.
	if (t > 2.8f && ending.ship_model >= 0)
	{
		const M4 turn = flying_turn(heading, roll, x, y, z);
		const M4 m = m4_place(ship, &turn, 9, 9, 9);
		J3DItem *it = add(J3D_MODEL, J3D_LIT, &m, 1, 1, 1, 1);
		if (it != NULL)
			it->model = (Sint16)ending.ship_model;
		const float fire = smooth(6.3f, 6.7f, t);
		const float engine[3] = { 1.0f, 0.62f, 0.28f };
		float rear[3];
		at_local(ship, x, y, z, 0, 0.3f, 4.8f, rear);
		glow(rear, 1.2f + 3.0f * fire, engine, 0.06f + 0.28f * fire);
		light(rear, 22, engine, 0.5f + 5 * fire);
		const float lamp[3] = { 1.0f, 0.9f, 0.75f };
		at_local(ship, x, y, z, 3, 8, -6, rear);
		light(rear, 30, lamp, 2.0f);
	}
	{
		float star[3];
		const float base[3] = { in_to[0], in_to[1], in_to[2] };
		for (int k = 0; k < 3; ++k)
			star[k] = base[k] + away_dir[k] * 620;
		const float red[3] = { 1.0f, 0.42f, 0.22f }, white[3] = { 1.0f, 0.9f, 0.75f };
		glow(star, 30 + 50 * smooth(6.8f, 8.2f, t), red, 0.15f + 0.5f * smooth(6.8f, 8.2f, t));
		const float flash = smooth(7.9f, 8.3f, t) * (1 - smooth(8.5f, 9.0f, t));
		if (flash > 0)
			glow(star, 120 + 400 * flash, white, 1.6f * flash);
	}
	return &scene;
}

/* --- The frame ------------------------------------------------------------------------------- */

static const char *const look_names[J3D_LOOKS] = { "Orrery", "Warp" };
static int look = -1;

int jukebox3d_look(void)
{
	if (look < 0)
	{
		// The setting's (by name), or TYR3D_JUKEBOX_LOOK's for the run.
		look = 0;
		for (int i = 0; i < J3D_LOOKS; ++i)
			if (SDL_strcasecmp(settings3d.jukebox_look, look_names[i]) == 0)
				look = i;
		const char *s = SDL_getenv("TYR3D_JUKEBOX_LOOK");
		if (s != NULL)
			look = SDL_clamp(SDL_atoi(s), 0, J3D_LOOKS - 1);
	}
	return look;
}

void jukebox3d_next_look(void)
{
	look = (jukebox3d_look() + 1) % J3D_LOOKS;
	SDL_strlcpy(settings3d.jukebox_look, look_names[look], sizeof(settings3d.jukebox_look));
	settings3d_changed(S3D_JUKEBOX);
}

const char *jukebox3d_look_name(int which)
{
	return look_names[SDL_clamp(which, 0, J3D_LOOKS - 1)];
}

const J3DScene *jukebox3d_frame(float w, float h, bool panel_shown)
{
	static bool stars_made = false;
	if (!stars_made)
	{
		make_stars();
		stars_made = true;
	}
	static Uint64 last = 0;
	const Uint64 now = SDL_GetTicksNS();
	const float dt = last != 0 ? SDL_min((now - last) / 1e9f, 0.1f) : 0;
	last = now;
	now_t += dt;
	musicviz_update(&viz, dt);

	scene.item_count = 0;
	scene.light_count = 0;
	scene.items = items;
	// (While the panel shows, the scene's middle higher: the planet, the ship above the panel.)
	static float shift = 0.3f;
	shift = ease_to(shift, !panel_shown ? 0.0f : jukebox3d_look() == 1 ? 0.62f : 0.36f, dt, 0.25f);
	const float aspect = h > 0 ? w / h : 16.0f / 9.0f;
	if (jukebox3d_look() == 1)
		warp_frame(aspect, shift, dt);
	else
		orrery_frame(aspect, shift, dt);
	return &scene;
}

/* --- The shapes' meshes and the planet ------------------------------------------------------- */

typedef struct
{
	float position[3], normal[3], uv[2], tangent[4], color[4], joints[4], weights[4];
} Vertex;

#define SPHERE_RINGS 32
#define SPHERE_SLICES 64

static Vertex box_vertices[2][24];
static Uint32 box_indices[36];
static Vertex sphere_vertices[(SPHERE_RINGS + 1) * (SPHERE_SLICES + 1)];
static Uint32 sphere_indices[SPHERE_RINGS * SPHERE_SLICES * 6];

static void make_boxes(void)
{
	static const float normals[6][3] = { { 1, 0, 0 }, { -1, 0, 0 }, { 0, 1, 0 }, { 0, -1, 0 }, { 0, 0, 1 }, { 0, 0, -1 } };
	for (int bar = 0; bar < 2; ++bar)
		for (int f = 0; f < 6; ++f)
		{
			const float *n = normals[f];
			// Two axes across the face.
			const int axis = n[0] != 0 ? 0 : n[1] != 0 ? 1 : 2;
			const int u_axis = (axis + 1) % 3, v_axis = (axis + 2) % 3;
			for (int c = 0; c < 4; ++c)
			{
				Vertex *v = &box_vertices[bar][f * 4 + c];
				memset(v, 0, sizeof(*v));
				const float su = (c == 1 || c == 2) ? 0.5f : -0.5f, sv = (c >= 2) ? 0.5f : -0.5f;
				v->position[axis] = n[axis] * 0.5f;
				v->position[u_axis] = su;
				v->position[v_axis] = sv;
				memcpy(v->normal, n, sizeof(v->normal));
				v->uv[0] = su + 0.5f;
				v->uv[1] = sv + 0.5f;
				v->tangent[u_axis] = 1;
				v->tangent[3] = 1;
				// The bar: dark at its foot, full at its top.
				const float k = bar ? 0.12f + 0.88f * powf(v->position[1] + 0.5f, 1.6f) : 1.0f;
				v->color[0] = v->color[1] = v->color[2] = k;
				v->color[3] = 1;
			}
			// (Wound so each face is seen from outside either way: the batches draw both sides.)
			const Uint32 b = (Uint32)f * 4;
			const Uint32 tri[6] = { b, b + 1, b + 2, b, b + 2, b + 3 };
			memcpy(&box_indices[f * 6], tri, sizeof(tri));
		}
}

static void make_sphere(void)
{
	int n = 0;
	for (int r = 0; r <= SPHERE_RINGS; ++r)
	{
		const float theta = PI_F * r / SPHERE_RINGS;
		for (int s = 0; s <= SPHERE_SLICES; ++s)
		{
			const float phi = 2 * PI_F * s / SPHERE_SLICES;
			Vertex *v = &sphere_vertices[n++];
			memset(v, 0, sizeof(*v));
			v->normal[0] = sinf(theta) * cosf(phi);
			v->normal[1] = cosf(theta);
			v->normal[2] = sinf(theta) * sinf(phi);
			memcpy(v->position, v->normal, sizeof(v->position));
			v->uv[0] = (float)s / SPHERE_SLICES;
			v->uv[1] = (float)r / SPHERE_RINGS;
			v->tangent[0] = -sinf(phi);
			v->tangent[2] = cosf(phi);
			v->tangent[3] = 1;
			v->color[0] = v->color[1] = v->color[2] = v->color[3] = 1;
		}
	}
	n = 0;
	for (int r = 0; r < SPHERE_RINGS; ++r)
		for (int s = 0; s < SPHERE_SLICES; ++s)
		{
			const Uint32 a = (Uint32)(r * (SPHERE_SLICES + 1) + s), b = a + SPHERE_SLICES + 1;
			const Uint32 tri[6] = { a, b, a + 1, a + 1, b, b + 1 };
			memcpy(&sphere_indices[n], tri, sizeof(tri));
			n += 6;
		}
}

void jukebox3d_mesh(J3DShape shape, const float **vertices, int *vertex_count, const Uint32 **indices, int *index_count)
{
	static bool made = false;
	if (!made)
	{
		make_boxes();
		make_sphere();
		made = true;
	}
	if (shape == J3D_SPHERE)
	{
		*vertices = (const float *)sphere_vertices;
		*vertex_count = (int)SDL_arraysize(sphere_vertices);
		*indices = sphere_indices;
		*index_count = (int)SDL_arraysize(sphere_indices);
		return;
	}
	*vertices = (const float *)box_vertices[shape == J3D_BAR];
	*vertex_count = 24;
	*indices = box_indices;
	*index_count = 36;
}

// A smooth value noise in [0, 1), wrapping every `period` cells across.
static float noise2(float x, float y, int period, Uint32 seed)
{
	const int xi = (int)floorf(x), yi = (int)floorf(y);
	const float fx = x - xi, fy = y - yi;
	const float ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
	float c[4];
	for (int k = 0; k < 4; ++k)
	{
		const int cx = ((xi + (k & 1)) % period + period) % period, cy = yi + (k >> 1);
		c[k] = hash01((Uint32)(cx * 7919 + cy * 104729) ^ seed);
	}
	return lerpf(lerpf(c[0], c[1], ux), lerpf(c[2], c[3], ux), uy);
}

// Noise of `octaves` octaves, each twice as fine and half as strong, in [0, 1) (wrapping across).
static float fbm2(float x, float y, int period, int octaves, Uint32 seed)
{
	float sum = 0, amp = 1, total = 0;
	for (int o = 0, f = 1; o < octaves; ++o, f *= 2)
	{
		sum += noise2(x * f, y * f, period * f, seed + (Uint32)o) * amp;
		total += amp;
		amp *= 0.5f;
	}
	return sum / total;
}

static void put_rgb(Uint32 *pixel, const float c[3])
{
	const Uint8 rgba[4] = { (Uint8)SDL_clamp(c[0], 0, 255), (Uint8)SDL_clamp(c[1], 0, 255), (Uint8)SDL_clamp(c[2], 0, 255), 255 };
	memcpy(pixel, rgba, 4);
}

static void gas_giant_texture(Uint32 *pixels, int W, int H);
static void terran_texture(Uint32 *pixels, int W, int H);

// The planets' textures (made the first time each is asked for).
const Uint32 *jukebox3d_planet_texture(J3DTexture texture, int *w, int *h)
{
	enum { W = 512, H = 256 };
	static Uint32 pixels[J3D_TEXTURES][W * H];
	static bool made[J3D_TEXTURES];
	if (texture <= J3D_UNTEXTURED || texture >= J3D_TEXTURES)
		texture = J3D_TEXTURE_GAS_GIANT;
	*w = W;
	*h = H;
	if (!made[texture])
	{
		made[texture] = true;
		if (texture == J3D_TEXTURE_TERRAN)
			terran_texture(pixels[texture], W, H);
		else
			gas_giant_texture(pixels[texture], W, H);
	}
	return pixels[texture];
}

// A green world: continents (lowlands, hills, a few mountains) in teal seas, shallower by the coasts, ice at
// the poles, and wisps of cloud over it.
static void terran_texture(Uint32 *pixels, int W, int H)
{
	static const float deep[3] = { 10, 40, 62 }, shallow[3] = { 26, 98, 108 };
	static const float low[3] = { 52, 128, 44 }, hill[3] = { 104, 140, 60 }, peak[3] = { 136, 128, 100 };
	static const float ice[3] = { 222, 234, 236 }, cloud[3] = { 236, 242, 244 };
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			const float u = (float)x / W, v = (float)y / H;
			// (The continents' outline warped a little, so the coasts wander.)
			const float wu = (fbm2(u * 4, v * 2, 4, 3, 91u) - 0.5f) * 0.08f;
			const float height = fbm2((u + wu) * 5, v * 2.5f, 5, 6, 41u);
			const float sea_level = 0.45f;  // (about half land)
			float c[3];
			if (height < sea_level)
			{
				const float d = clamp01((sea_level - height) / 0.12f);
				for (int k = 0; k < 3; ++k)
					c[k] = lerpf(shallow[k], deep[k], sqrtf(d));
			}
			else
			{
				const float e = clamp01((height - sea_level) / 0.16f);
				const float speckle = 0.9f + 0.2f * noise2(u * 160, v * 80, 160, 7u);
				for (int k = 0; k < 3; ++k)
					c[k] = (e < 0.5f ? lerpf(low[k], hill[k], e * 2) : lerpf(hill[k], peak[k], e * 2 - 1)) * speckle;
			}
			// Ice at the poles, its edge ragged.
			const float lat = fabsf(v - 0.5f) * 2;
			const float cap = clamp01((lat - 0.82f + (fbm2(u * 16, v * 8, 16, 4, 13u) - 0.5f) * 0.2f) / 0.04f);
			for (int k = 0; k < 3; ++k)
				c[k] = lerpf(c[k], ice[k], cap);
			// Clouds, in swirls (their noise warped by another).
			const float swirl = (fbm2(u * 4, v * 2, 4, 3, 77u) - 0.5f) * 1.6f;
			const float cl = fbm2(u * 8 + swirl, v * 5 + swirl * 0.5f, 8, 5, 63u);
			const float cover = clamp01((cl - 0.53f) / 0.14f) * 0.8f;
			for (int k = 0; k < 3; ++k)
				c[k] = lerpf(c[k], cloud[k], cover);
			put_rgb(&pixels[y * W + x], c);
		}
}

// A gas giant: bands of teal, slate and amber, turbulent, a storm in the south.
static void gas_giant_texture(Uint32 *pixels, int W, int H)
{
	static const float palette[5][3] = { { 22, 52, 70 }, { 46, 98, 112 }, { 150, 132, 96 }, { 196, 150, 86 }, { 70, 78, 96 } };
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			const float u = (float)x / W, v = (float)y / H;
			float turb = 0, amp = 1, f = 1, total = 0;
			for (int o = 0; o < 5; ++o)
			{
				turb += noise2(u * 8 * f, v * 16 * f, 8 * (int)f, 17u + o) * amp;
				total += amp;
				amp *= 0.5f;
				f *= 2;
			}
			turb /= total;
			const float lat = v + (turb - 0.5f) * 0.06f;
			float band = 0.5f + 0.5f * sinf(lat * 38) * cosf(lat * 11 + 1.3f);
			band = band * 0.75f + turb * 0.25f;
			const float t = clamp01(band) * 4;
			const int i = SDL_min((int)t, 3);
			float c[3];
			for (int k = 0; k < 3; ++k)
				c[k] = lerpf(palette[i][k], palette[i + 1][k], t - i);
			// A storm.
			const float sx = (u - 0.62f) * 2.0f, sy = (v - 0.66f) * 5.0f, sd = sx * sx + sy * sy;
			if (sd < 1)
			{
				const float storm = (1 - sd) * (1 - sd);
				const float sc[3] = { 214, 120, 60 };
				for (int k = 0; k < 3; ++k)
					c[k] = lerpf(c[k], sc[k], storm * 0.8f);
			}
			// Darker at the poles.
			const float pole = 0.55f + 0.45f * sinf(PI_F * v);
			for (int k = 0; k < 3; ++k)
				c[k] *= pole;
			put_rgb(&pixels[y * W + x], c);
		}
}
