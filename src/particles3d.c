/*
 * Tyrian3D: particle effects for the 3D view. See particles3d.h.
 */
#include "particles3d.h"
#include "settings3d.h"
#include "player.h"

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

// A wisp of white smoke that drifts up and thins out soon: the game's smoke behind missiles, many in a row.
static void wisp(float x, float y, float height)
{
	for (int i = 0; i < 2; ++i)
	{
		P3DParticle *p = spawn(P3D_SMOKE, x + random_range(-1.5f, 1.5f), y + random_range(-1.5f, 1.5f), height);
		if (p == NULL)
			return;
		p->vx = random_range(-0.1f, 0.1f);
		p->vy = random_range(-0.15f, 0.05f);
		p->vheight = random_range(0.15f, 0.3f);
		p->drag = 0.97f;
		p->size = random_range(4.5f, 6.0f);
		p->grow = 0.22f;
		p->age = -random_range(0, 2);
		p->life = random_range(18, 28);
		set_colors(p, 200, 200, 200, 52, 100, 100, 100, 0);
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
		p->size = random_range(1.4f, 2.8f);  // (2-3.6: brown cubes all round a large explosion)
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
		p->size = random_range(1.5f, 2.9f);
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

void p3d_smoulder(float x, float y, float height, float scale, float strength)
{
	if (strength <= 0 || random_range(0, 1) > 0.2f + 0.45f * strength)
		return;
	const float spread = 3.0f * scale;
	P3DParticle *p = spawn(P3D_SMOKE, x + random_range(-spread, spread), y + random_range(-spread, spread), height);
	if (p != NULL)
	{
		p->vx = random_range(-0.06f, 0.06f);
		p->vy = random_range(-0.1f, 0.02f);
		p->vheight = random_range(0.25f, 0.45f);
		p->drag = 0.985f;
		p->size = random_range(3.5f, 5.0f) * scale;
		p->grow = 0.14f * scale;
		p->life = random_range(36, 54);
		const Uint8 grey = (Uint8)random_range(70, 100);
		set_colors(p, grey, grey, grey, (Uint8)(130 + 90 * strength), (Uint8)(grey + 30), (Uint8)(grey + 30),
		           (Uint8)(grey + 30), 0);
	}
	if (random_range(0, 1) < 0.25f * strength)
	{
		P3DParticle *e = spawn(P3D_GLOW, x + random_range(-spread, spread), y + random_range(-spread, spread), height);
		if (e == NULL)
			return;
		e->vx = random_range(-0.15f, 0.15f);
		e->vy = random_range(-0.15f, 0.15f);
		e->vheight = random_range(0.4f, 0.8f);
		e->drag = 0.96f;
		e->size = random_range(1.4f, 2.2f);
		e->life = random_range(14, 24);
		set_colors(e, 255, 170, 60, 255, 200, 50, 10, 0);
	}
}

void p3d_pickup(float x, float y, float height)
{
	// Pale gold, unlike the explosions' fire.
	P3DParticle *ring = spawn(P3D_RING, x, y, height);
	if (ring != NULL)
	{
		ring->screen = true;
		ring->size = 6;
		ring->grow = 1.6f;
		ring->life = 12;
		set_colors(ring, 255, 240, 190, 200, 255, 200, 110, 0);
	}
	P3DParticle *glow = spawn(P3D_GLOW, x, y, height);
	if (glow != NULL)
	{
		glow->screen = true;
		glow->size = 14;
		glow->grow = -0.9f;
		glow->life = 8;
		set_colors(glow, 255, 245, 210, 170, 255, 210, 120, 0);
	}
	for (int i = 0; i < 10; ++i)
	{
		P3DParticle *p = spawn(P3D_GLOW, x, y, height);
		if (p == NULL)
			return;
		p->screen = true;
		const float angle = (i + random_range(0, 0.6f)) * 2 * (float)M_PI / 10, s = random_range(1.4f, 2.2f);
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(0.0f, 0.8f);
		p->drag = 0.86f;
		p->size = random_range(1.6f, 2.4f);
		p->life = random_range(12, 18);
		set_colors(p, 255, 250, 220, 255, 255, 200, 90, 0);
	}
}

void p3d_nova(float x, float y, float height, float reach, int life)
{
	// White-violet, a shock rather than fire.
	for (int k = 0; k < 2; ++k)
	{
		P3DParticle *ring = spawn(P3D_RING, x, y, height);
		if (ring == NULL)
			return;
		ring->screen = true;
		ring->size = 8;
		ring->grow = (2 * reach - 8) / life;
		ring->age = -3.0f * k;  // (a second ring close behind)
		ring->life = (float)life;
		set_colors(ring, 255, 245, 255, 255, 170, 110, 255, 0);
	}
	P3DParticle *flash = spawn(P3D_GLOW, x, y, height);
	if (flash != NULL)
	{
		flash->screen = true;
		flash->size = 40;
		flash->grow = -2.5f;
		flash->life = 14;
		set_colors(flash, 255, 250, 255, 255, 190, 140, 255, 0);
	}
	for (int i = 0; i < 28; ++i)
	{
		P3DParticle *p = spawn(P3D_GLOW, x, y, height);
		if (p == NULL)
			return;
		p->screen = true;
		const float angle = (i + random_range(0, 0.8f)) * 2 * (float)M_PI / 28, s = reach / life * random_range(0.8f, 1.1f);
		p->vx = cosf(angle) * s;
		p->vy = sinf(angle) * s;
		p->vheight = random_range(0.0f, 1.0f);
		p->size = random_range(2.0f, 3.2f);
		p->life = (float)life * random_range(0.8f, 1.0f);
		set_colors(p, 255, 240, 255, 255, 160, 120, 255, 0);
	}
	p3d_add_shake(0.35f);
}

void p3d_field(float x, float y, float height, P3DField field, float reach, bool pulse)
{
	// Cold blue-white light, unlike the explosions' fire.
	if (pulse && (field == P3D_FIELD_REPULSE || field == P3D_FIELD_ATTRACT))
	{
		// (One faint ring a pulse: two bright ones every 14 frames, from several fields, covered the screen in
		// overlapping blue rings, 1:19, 3:6.)
		for (int k = 0; k < 1; ++k)
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
			set_colors(p, 150, 220, 255, 80, 40, 90, 255, 0);
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

void p3d_trail(float x, float y, float dx, float dy, float height, P3DTrail kind, float span)
{
	const float speed = sqrtf(dx * dx + dy * dy);
	if (speed < 0.5f)
		return;
	if (kind == P3D_TRAIL_VAPOUR)
	{
		// From the wingtips, a little behind them, lingering and spreading; the engine glowing between. Puffs
		// every pixel and a half along the way it came this frame, so the trails are lines, not beads.
		const float ux = dx / speed, uy = dy / speed;
		const int steps = SDL_min(8, (int)ceilf(speed / 1.5f));
		for (int k = 0; k < steps; ++k)
		{
			const float back = 3.0f + speed * k / steps;
			for (int side = -1; side <= 1; side += 2)
			{
				P3DParticle *p = spawn(P3D_SMOKE, x - ux * back - uy * span / 2 * side, y - uy * back + ux * span / 2 * side, height);
				if (p == NULL)
					return;
				p->vx = random_range(-0.03f, 0.03f);
				p->vy = random_range(-0.03f, 0.03f);
				p->drag = 0.9f;
				// (Thin and short: 2.6-3.2 growing 0.1 for 18-24 frames made two thick white worms behind every jet.)
				p->size = random_range(1.7f, 2.2f);
				p->grow = 0.06f;
				p->life = random_range(12, 16) - k * 0.4f;
				set_colors(p, 235, 240, 245, 36, 235, 240, 245, 0);
			}
		}
		P3DParticle *glow = spawn(P3D_GLOW, x - ux * 6.0f, y - uy * 6.0f, height);
		if (glow != NULL)
		{
			glow->size = random_range(4.0f, 5.5f);
			glow->life = 2;
			set_colors(glow, 255, 170, 80, 200, 255, 110, 40, 0);
		}
		return;
	}
	// Behind its motor, a little off its line, drifting slowly as it thins out: puffs every two pixels along the way
	// it came this frame, thin and soon gone, so the trail is a wisp, not a row of thick beads that crosses the
	// screen (one puff a frame of 2.2-3 growing 0.22 for 16-24 frames: grey worms over every space level's shots).
	const float bx = x - dx / speed * 5.0f, by = y - dy / speed * 5.0f;
	const int steps = SDL_clamp((int)ceilf(speed / 2.0f), 1, 4);
	for (int k = 0; k < steps; ++k)
	{
		const float back = speed * k / steps;
		P3DParticle *p = spawn(P3D_SMOKE, bx - dx / speed * back + random_range(-0.4f, 0.4f),
		                       by - dy / speed * back + random_range(-0.4f, 0.4f), height);
		if (p == NULL)
			break;
		p->vx = -dx * 0.03f + random_range(-0.06f, 0.06f);
		p->vy = -dy * 0.03f + random_range(-0.06f, 0.06f);
		p->vheight = random_range(0.0f, 0.05f);
		p->drag = 0.94f;
		p->size = random_range(1.6f, 2.2f);
		p->grow = 0.14f;
		p->life = random_range(11, 16) - k * 0.4f;
		const Uint8 grey = (Uint8)random_range(150, 190);
		set_colors(p, grey, grey, grey, 60, grey, grey, grey, 0);
	}
	P3DParticle *spark = spawn(P3D_GLOW, bx + dx / speed * 1.5f, by + dy / speed * 1.5f, height);
	if (spark != NULL)
	{
		spark->size = random_range(3.5f, 5.0f);
		spark->life = 2;
		set_colors(spark, 255, 190, 90, 255, 255, 110, 30, 0);
	}
}

void p3d_ship_destroyed(float x, float y, float height)
{
	// (The game's own explosions burst round it for a second: its fire and light.)
	p3d_add_shake(1.0f);
	shock_ring(x, y, height, 130, 22);
	sparks(x, y, height, 20, 4.0f);
	// Pieces of the hull: bronze plates and dark machinery, flung out, tumbling down to the ground.
	for (int i = 0; i < 16; ++i)
	{
		P3DParticle *d = spawn(P3D_DEBRIS, x, y, height);
		if (d == NULL)
			return;
		const float angle = random_range(0, 2 * (float)M_PI), s = random_range(2.0f, 4.0f);
		d->vx = cosf(angle) * s;
		d->vy = sinf(angle) * s;
		d->vheight = random_range(-0.2f, 1.6f);
		d->gravity = 0.1f;
		d->drag = 0.975f;
		d->size = random_range(3.0f, 5.5f);
		d->life = random_range(70, 100);
		d->turn = random_range(0, 2 * (float)M_PI);
		d->spin = random_range(-0.5f, 0.5f);
		if (i % 3 == 0)
		{
			const Uint8 shade = (Uint8)random_range(40, 60);
			set_colors(d, shade, shade, (Uint8)(shade + 4), 255, shade, shade, (Uint8)(shade + 4), 255);
		}
		else
		{
			const Uint8 shade = (Uint8)random_range(150, 200);
			set_colors(d, shade, (Uint8)(shade * 0.78f), (Uint8)(shade * 0.5f), 255, shade, (Uint8)(shade * 0.78f),
			           (Uint8)(shade * 0.5f), 255);
		}
	}
}

// A big explosion shakes the view the more the nearer it is to the ship (none beyond 110 pixels).
static void shake_near(float x, float y)
{
	const float dx = x - (player[0].x + 7), dy = y - (player[0].y + 7);
	const float d = sqrtf(dx * dx + dy * dy);
	if (d < 110)
		p3d_add_shake(0.45f * (1 - d / 110));
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
		// (One flash at the middle of the four: a flash each burned into a white rounded square.)
		if (type == 5)
			flash(cx - 6, cy - 7, 10, 34, 8);
		fireball(cx, cy, 8, 6, 18, 28, 5);
		sparks(cx, cy, 8, 6, 2.8f);
		embers(cx, cy, 6, 5, 1.5f);
		debris(cx, cy, 6, 5);
		plume(cx, cy, 8, 3, 18, 40);
		if (type == 5)  // once, at the middle of the four
		{
			shake_near(cx - 6, cy - 7);
			shock_ring(cx - 6, cy - 7, 2, 90, 16);
			scorch(cx - 6, cy - 7, 36);
		}
		light(cx, cy, 12, 56, 5.5f, 12);
		return true;
	case 6:  // white smoke (the game's missiles leave it every few frames: a wisp each, or they drew thick grey worms)
		wisp(cx, cy, 30);
		return true;
	case 7: case 8: case 9: case 10:  // a quarter of a large explosion in the air
		if (type == 10)
			flash(cx - 6, cy - 7, 30, 34, 8);
		fireball(cx, cy, 30, 6, 17, 24, 5);
		sparks(cx, cy, 30, 9, 3.2f);
		embers(cx, cy, 30, 4, 1.7f);
		plume(cx, cy, 30, 2, 15, 60);
		shards(cx, cy, 30, 2);
		if (type == 10)
		{
			shake_near(cx - 6, cy - 7);
			shock_ring(cx - 6, cy - 7, 30, 80, 14);
		}
		light(cx, cy, 24, 60, 5.5f, 12);
		return true;
	case 14: case 15: case 16: case 17: case 18: case 19: case 20: case 21: case 22:
		// The player's shield: the 3D view shows its own round the ship (l3d_shield_glow), with Effects.
		return settings3d.effects;
	default:  // coin values, weapons' own hits: their sprites
		return false;
	}
}

float p3d_shake = 0;

void p3d_add_shake(float amount)
{
	if (settings3d.shake)
		p3d_shake = SDL_min(1.0f, p3d_shake + amount);
}

void p3d_update(int drift)
{
	p3d_shake *= 0.84f;
	if (p3d_shake < 0.01f)
		p3d_shake = 0;

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
			p->y += p->vy + (p->screen ? 0 : drift);
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
