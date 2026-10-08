/*
 * Tyrian3D: particle effects for the 3D view. See particles3d.h.
 */
#include "particles3d.h"

#include <math.h>
#include <string.h>

P3DParticle p3d_particles[P3D_MAX_PARTICLES];
int p3d_particle_count = 0;

// The particles' own random numbers (xorshift32), apart from the game's.
static Uint32 random_state = 0x9e3779b9u;

static float random_unit(void)
{
	random_state ^= random_state << 13;
	random_state ^= random_state >> 17;
	random_state ^= random_state << 5;
	return (random_state >> 8) / 16777216.0f;
}

static float random_range(float low, float high)
{
	return low + (high - low) * random_unit();
}

static P3DParticle *spawn(P3DKind kind, float x, float y, float height)
{
	if (p3d_particle_count == P3D_MAX_PARTICLES)
		return NULL;
	P3DParticle *p = &p3d_particles[p3d_particle_count++];
	memset(p, 0, sizeof(*p));
	p->kind = (Uint8)kind;
	p->x = x;
	p->y = y;
	p->height = height;
	p->air = height >= 20;
	p->drag = 1.0f;
	return p;
}

static void set_colors(P3DParticle *p, Uint8 r, Uint8 g, Uint8 b, Uint8 a, Uint8 r2, Uint8 g2, Uint8 b2, Uint8 a2)
{
	const Uint8 start[4] = { r, g, b, a }, end[4] = { r2, g2, b2, a2 };
	memcpy(p->color, start, 4);
	memcpy(p->end_color, end, 4);
}

// A bright flash that swells and fades.
static void flash(float x, float y, float height, float size, float life)
{
	P3DParticle *p = spawn(P3D_GLOW, x, y, height);
	if (p == NULL)
		return;
	p->size = size;
	p->grow = size * 0.05f;
	p->life = life;
	set_colors(p, 255, 210, 120, 220, 255, 90, 10, 0);
}

// Sparks thrown out in every direction, slowing down, cooling from yellow to red.
static void sparks(float x, float y, float height, int count, float speed)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_GLOW, x, y, height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.4f, 1.0f) * speed;
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(-0.3f, 1.0f) * s;
		p->gravity = 0.06f;
		p->drag = 0.9f;
		p->size = random_range(1.6f, 3.0f);
		p->life = random_range(8, 16);
		set_colors(p, 255, 240, 150, 255, 230, 60, 0, 0);
	}
}

// Smoke that rises, spreads and thins out.
static void smoke(float x, float y, float height, int count, float size, Uint8 grey)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_SMOKE, x + random_range(-3, 3), y + random_range(-3, 3), height);
		if (p == NULL)
			return;
		p->vx = random_range(-0.15f, 0.15f);
		p->vy = random_range(-0.25f, 0.05f);
		p->vheight = random_range(0.2f, 0.45f);
		p->drag = 0.98f;
		p->size = size * random_range(0.6f, 1.0f);
		p->grow = size * 0.04f;
		p->age = -random_range(0, 4);  // puffs appear one after another
		p->life = random_range(28, 44);
		set_colors(p, grey, grey, grey, 120, grey / 2, grey / 2, grey / 2, 0);
	}
}

// Dark chunks thrown up from the ground that fall back.
static void debris(float x, float y, float height, int count)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_SMOKE, x, y, height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.3f, 1.3f);
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(1.5f, 3.5f);
		p->gravity = 0.22f;
		p->drag = 0.97f;
		p->size = random_range(1.0f, 2.2f);
		p->life = random_range(22, 34);
		set_colors(p, 60, 48, 36, 255, 40, 32, 24, 255);
	}
}

P3DLight p3d_lights[P3D_MAX_LIGHTS];
int p3d_light_count = 0;

// A flash's light; flashes close together in the same frame (the quarters of a large explosion)
// make one brighter, larger light.
static void light(float x, float y, float height, float radius, float energy, float life)
{
	for (int i = 0; i < p3d_light_count; ++i)
	{
		P3DLight *l = &p3d_lights[i];
		if (l->age == 0 && fabsf(l->x - x) < 16 && fabsf(l->y - y) < 16)
		{
			l->x = (l->x + x) / 2;
			l->y = (l->y + y) / 2;
			l->radius = SDL_min(l->radius * 1.15f, 64.0f);
			l->energy = SDL_min(l->energy + energy * 0.35f, 9.0f);
			l->life = SDL_max(l->life, life);
			return;
		}
	}
	if (p3d_light_count == P3D_MAX_LIGHTS)
		return;
	P3DLight *l = &p3d_lights[p3d_light_count++];
	*l = (P3DLight){ x, y, height, radius, energy, 0, life, { 255, 150, 60 }, height >= 20 };
}

float p3d_light_energy(const P3DLight *l, float ahead)
{
	const float t = (l->age + ahead) / l->life;
	return t >= 1 ? 0 : l->energy * (1 - t) * (1 - 0.5f * t);
}

void p3d_explosion(int x, int y, int type)
{
	// The explosion sprite's centre (they are 12x14).
	const float cx = x + 6.0f, cy = y + 7.0f;
	switch (type)
	{
	case 0: case 1: case 11: case 12: case 13:  // hits
		flash(cx, cy, 30, 8, 4);
		sparks(cx, cy, 30, 4, 2.0f);
		light(cx, cy, 24, 30, 2.5f, 6);
		break;
	case 2: case 3: case 4: case 5:  // a quarter of a large explosion on the ground
		flash(cx, cy, 8, 14, 6);
		sparks(cx, cy, 8, 4, 2.2f);
		debris(cx, cy, 6, 4);
		smoke(cx, cy, 8, 2, 14, 45);
		light(cx, cy, 12, 56, 5.5f, 12);
		break;
	case 6:  // white smoke
		smoke(cx, cy, 30, 3, 10, 200);
		break;
	case 7: case 8: case 9: case 10:  // a quarter of a large explosion in the air
		flash(cx, cy, 30, 14, 6);
		sparks(cx, cy, 30, 6, 2.6f);
		smoke(cx, cy, 30, 1, 14, 55);
		light(cx, cy, 24, 60, 5.5f, 12);
		break;
	default:  // the player's shield, coin values
		break;
	}
}

void p3d_update(int drift)
{
	for (int i = 0; i < p3d_light_count; )
	{
		P3DLight *l = &p3d_lights[i];
		if (++l->age >= l->life)
		{
			*l = p3d_lights[--p3d_light_count];
			continue;
		}
		l->y += drift;
		++i;
	}

	for (int i = 0; i < p3d_particle_count; )
	{
		P3DParticle *p = &p3d_particles[i];
		if (++p->age >= p->life)
		{
			*p = p3d_particles[--p3d_particle_count];
			continue;
		}
		if (p->age > 0)
		{
			p->x += p->vx;
			p->y += p->vy + drift;
			p->height += p->vheight;
			p->vx *= p->drag;
			p->vy *= p->drag;
			p->vheight = p->vheight * p->drag - p->gravity;
			if (p->height < 0)  // on the ground
			{
				p->height = 0;
				p->vx = p->vy = p->vheight = 0;
			}
			p->size += p->grow;
		}
		++i;
	}
}

void p3d_clear(void)
{
	p3d_particle_count = 0;
	p3d_light_count = 0;
}
