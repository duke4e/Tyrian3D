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

// Dark chunks thrown up from the ground that tumble and fall back, and lie there a moment.
static void debris(float x, float y, float height, int count)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_DEBRIS, x, y, height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.3f, 1.3f);
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(1.5f, 3.5f);
		p->gravity = 0.22f;
		p->drag = 0.97f;
		p->size = random_range(2.0f, 3.6f);
		p->life = random_range(40, 60);
		p->turn = random_range(0, 2 * (float)M_PI);
		p->spin = random_range(-0.35f, 0.35f);
		const Uint8 shade = (Uint8)random_range(46, 78);
		set_colors(p, shade, (Uint8)(shade * 0.82f), (Uint8)(shade * 0.66f), 255, shade, (Uint8)(shade * 0.82f), (Uint8)(shade * 0.66f), 255);
	}
}

// The burnt mark a ground explosion leaves, which stays a few seconds and fades.
static void scorch(float x, float y, float size)
{
	P3DParticle *p = spawn(P3D_SCORCH, x + random_range(-2, 2), y + random_range(-2, 2), 0);
	if (p == NULL)
		return;
	p->size = size * random_range(0.85f, 1.15f);
	p->age = -4;  // (under the fireball, once it has burst)
	p->life = random_range(220, 280);
	set_colors(p, 14, 10, 7, 255, 14, 10, 7, 0);
}

// Shards of a craft blown apart in the air: bits of grey plating that tumble down to the ground.
static void shards(float x, float y, float height, int count)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_DEBRIS, x, y, height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.4f, 1.6f);
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(-0.5f, 1.5f);
		p->gravity = 0.1f;
		p->drag = 0.96f;
		p->size = random_range(2.2f, 3.8f);
		p->life = random_range(50, 75);
		p->turn = random_range(0, 2 * (float)M_PI);
		p->spin = random_range(-0.45f, 0.45f);
		const Uint8 shade = (Uint8)random_range(90, 140);
		set_colors(p, shade, shade, (Uint8)(shade * 1.05f), 255, shade, shade, (Uint8)(shade * 1.05f), 255);
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

// Billowing fire: noisy puffs that swell, rise a little and cool from white-hot to dark red.
static void fireball(float x, float y, float height, int count, float size, float life, float spread)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_FIRE, x + random_range(-spread, spread), y + random_range(-spread, spread), height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.1f, 0.5f) * size / 10;
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(0.15f, 0.5f);
		p->drag = 0.92f;
		p->size = size * random_range(0.55f, 0.9f);
		p->grow = size * random_range(0.03f, 0.06f);
		p->age = -random_range(0, 3);
		p->life = life * random_range(0.75f, 1.2f);
		p->height = SDL_max(p->height, p->size * 0.5f);  // a puff facing the camera, not cut by the ground
		// The first puffs hottest; additive, so they stay orange where they overlap.
		const float heat = i == 0 ? 1.0f : random_range(0.55f, 0.85f);
		set_colors(p, 255, (Uint8)(190 * heat), (Uint8)(90 * heat), 170, 140, 30, 6, 0);
	}
}

// Embers: small glowing bits thrown up that fall back, cooling.
static void embers(float x, float y, float height, int count, float speed)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_GLOW, x, y, height);
		if (p == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(0.3f, 1.0f) * speed;
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(0.8f, 2.2f);
		p->gravity = 0.12f;
		p->drag = 0.96f;
		p->size = random_range(1.0f, 1.8f);
		p->life = random_range(20, 36);
		set_colors(p, 255, 200, 90, 255, 200, 40, 0, 0);
	}
}

// A shock wave: a ring racing out and fading.
static void shock_ring(float x, float y, float height, float size, float life)
{
	P3DParticle *p = spawn(P3D_RING, x, y, height);
	if (p == NULL)
		return;
	p->size = size * 0.3f;
	p->grow = size / life;
	p->life = life;
	set_colors(p, 255, 200, 140, 150, 255, 110, 40, 0);
}

void p3d_field(float x, float y, float height, P3DField field, float reach, bool pulse)
{
	// Cold blue-white light, unlike the explosions' fire.
	if (pulse && (field == P3D_FIELD_REPULSE || field == P3D_FIELD_ATTRACT))
	{
		for (int k = 0; k < 2; ++k)
		{
			P3DParticle *p = spawn(P3D_RING, x, y, height);
			if (p == NULL)
				return;
			const float life = 20;
			if (field == P3D_FIELD_REPULSE)
			{
				p->size = 8;
				p->grow = (2 * reach - 8) / life;
			}
			else
			{
				p->size = 2 * reach;
				p->grow = -(2 * reach - 8) / life;
			}
			p->age = -6.0f * k;
			p->life = life;
			set_colors(p, 150, 220, 255, 150, 40, 90, 255, 0);
		}
	}
	const int count = pulse ? 10 : 2;
	for (int i = 0; i < count; ++i)
	{
		const float angle = random_range(0, 2 * (float)M_PI);
		float px = x, py = y, vx, vy;
		switch (field)
		{
		case P3D_FIELD_REPULSE:
			vx = cosf(angle) * random_range(2.5f, 4.0f);
			vy = sinf(angle) * random_range(2.5f, 4.0f);
			break;
		case P3D_FIELD_ATTRACT:
		{
			// From the edge of its reach, inwards.
			const float r = reach * random_range(0.6f, 1.0f), s = random_range(2.5f, 4.0f);
			px += cosf(angle) * r;
			py += sinf(angle) * r;
			vx = -cosf(angle) * s;
			vy = -sinf(angle) * s;
			break;
		}
		default:
		{
			const float side = field == P3D_FIELD_RIGHT ? 1.0f : -1.0f;
			px += random_range(-6, 6);
			py += random_range(-reach, reach);
			vx = side * random_range(3.0f, 5.0f);
			vy = random_range(-0.2f, 0.2f);
			break;
		}
		}
		P3DParticle *p = spawn(P3D_GLOW, px, py, height);
		if (p == NULL)
			return;
		p->vx = vx;
		p->vy = vy;
		p->drag = 0.97f;
		p->size = random_range(1.4f, 2.4f);
		p->life = field == P3D_FIELD_ATTRACT ? reach * 0.8f / 3.2f : random_range(12, 18);
		set_colors(p, 180, 230, 255, 230, 60, 120, 255, 0);
	}
}

// A plume of dark smoke rising after the fire.
static void plume(float x, float y, float height, int count, float size, Uint8 grey)
{
	for (int i = 0; i < count; ++i)
	{
		P3DParticle *p = spawn(P3D_SMOKE, x + random_range(-4, 4), y + random_range(-4, 4), height);
		if (p == NULL)
			return;
		p->vx = random_range(-0.1f, 0.1f);
		p->vy = random_range(-0.15f, 0.05f);
		p->vheight = random_range(0.35f, 0.7f);
		p->drag = 0.985f;
		p->size = size * random_range(0.5f, 0.8f);
		p->grow = size * 0.035f;
		p->age = -random_range(4, 12);  // after the fire
		p->life = random_range(40, 60);
		p->height = SDL_max(p->height, p->size * 0.5f);
		set_colors(p, grey, grey, grey, 110, grey / 2, grey / 2, grey / 2, 0);
	}
}

void p3d_trail(float x, float y, float dx, float dy, float height)
{
	const float speed = sqrtf(dx * dx + dy * dy);
	if (speed < 0.5f)
		return;
	// Behind its motor, a little off its line, drifting slowly as it thins out.
	const float bx = x - dx / speed * 5.0f, by = y - dy / speed * 5.0f;
	P3DParticle *p = spawn(P3D_SMOKE, bx + random_range(-0.6f, 0.6f), by + random_range(-0.6f, 0.6f), height);
	if (p != NULL)
	{
		p->vx = -dx * 0.04f + random_range(-0.08f, 0.08f);
		p->vy = -dy * 0.04f + random_range(-0.08f, 0.08f);
		p->vheight = random_range(0.0f, 0.06f);
		p->drag = 0.94f;
		p->size = random_range(2.2f, 3.0f);
		p->grow = 0.22f;
		p->life = random_range(16, 24);
		const Uint8 grey = (Uint8)random_range(150, 190);
		set_colors(p, grey, grey, grey, 95, grey, grey, grey, 0);
	}
	P3DParticle *spark = spawn(P3D_GLOW, bx + dx / speed * 1.5f, by + dy / speed * 1.5f, height);
	if (spark != NULL)
	{
		spark->size = random_range(3.5f, 5.0f);
		spark->life = 2;
		set_colors(spark, 255, 190, 90, 255, 255, 110, 30, 0);
	}
}

bool p3d_explosion(int x, int y, int type)
{
	// The explosion sprite's centre (they are 12x14).
	const float cx = x + 6.0f, cy = y + 7.0f;
	switch (type)
	{
	case 0: case 1: case 11: case 12: case 13:  // hits
		flash(cx, cy, 30, 10, 5);
		fireball(cx, cy, 30, 3, 8, 14, 2);
		sparks(cx, cy, 30, 6, 2.4f);
		light(cx, cy, 24, 30, 2.5f, 6);
		return true;
	case 2: case 3: case 4: case 5:  // a quarter of a large explosion on the ground
		flash(cx, cy, 10, 22, 7);
		fireball(cx, cy, 8, 6, 18, 28, 5);
		sparks(cx, cy, 8, 6, 2.8f);
		embers(cx, cy, 6, 5, 1.5f);
		debris(cx, cy, 6, 5);
		scorch(cx, cy, 28);
		plume(cx, cy, 8, 3, 18, 40);
		if (type == 5)  // once, at the middle of the four
			shock_ring(cx - 6, cy - 7, 2, 90, 16);
		light(cx, cy, 12, 56, 5.5f, 12);
		return true;
	case 6:  // white smoke
		smoke(cx, cy, 30, 3, 10, 200);
		return true;
	case 7: case 8: case 9: case 10:  // a quarter of a large explosion in the air
		flash(cx, cy, 30, 22, 7);
		fireball(cx, cy, 30, 6, 17, 24, 5);
		sparks(cx, cy, 30, 9, 3.2f);
		embers(cx, cy, 30, 4, 1.7f);
		plume(cx, cy, 30, 2, 15, 60);
		shards(cx, cy, 30, 2);
		if (type == 10)
			shock_ring(cx - 6, cy - 7, 30, 80, 14);
		light(cx, cy, 24, 60, 5.5f, 12);
		return true;
	default:  // the player's shield, coin values, weapons' own hits: their sprites
		return false;
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
			if (p->height > 0)
				p->turn += p->spin;  // (debris tumbles while it flies)
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
