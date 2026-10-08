/*
 * Tyrian3D: a wave function collapse solver for tile grids. See wfc.h.
 */
#include "wfc.h"

#include <stdlib.h>
#include <string.h>

static void set_add(WFCSet *s, int kind)
{
	s->bits[kind / 64] |= (uint64_t)1 << (kind % 64);
}

static bool set_has(const WFCSet *s, int kind)
{
	return (s->bits[kind / 64] >> (kind % 64)) & 1;
}

static int set_count(const WFCSet *s)
{
	int n = 0;
	for (int w = 0; w < WFC_WORDS; ++w)
		for (uint64_t bits = s->bits[w]; bits != 0; bits &= bits - 1)  // (portable: no compiler built-ins)
			++n;
	return n;
}

static void set_and(WFCSet *s, const WFCSet *t)
{
	for (int w = 0; w < WFC_WORDS; ++w)
		s->bits[w] &= t->bits[w];
}

static void set_or(WFCSet *s, const WFCSet *t)
{
	for (int w = 0; w < WFC_WORDS; ++w)
		s->bits[w] |= t->bits[w];
}

static bool set_equal(const WFCSet *s, const WFCSet *t)
{
	return memcmp(s->bits, t->bits, sizeof(s->bits)) == 0;
}

void wfc_learn(WFCRules *rules, int kinds, const int *grid, int rows, int columns)
{
	memset(rules, 0, sizeof(*rules));
	rules->kinds = kinds < WFC_MAX_KINDS ? kinds : WFC_MAX_KINDS;
	for (int r = 0; r < rows; ++r)
		for (int c = 0; c < columns; ++c)
		{
			const int k = grid[r * columns + c];
			if (k < 0 || k >= rules->kinds)
				continue;
			rules->weight[k] += 1;
			if (c + 1 < columns)
			{
				const int right = grid[r * columns + c + 1];
				if (right >= 0 && right < rules->kinds)
				{
					set_add(&rules->right[k], right);
					set_add(&rules->left[right], k);
				}
			}
			if (r + 1 < rows)
			{
				const int below = grid[(r + 1) * columns + c];
				if (below >= 0 && below < rules->kinds)
				{
					set_add(&rules->down[k], below);
					set_add(&rules->up[below], k);
				}
			}
		}
}

// A small, fast generator (xorshift32).
static uint32_t next_random(uint32_t *state)
{
	uint32_t x = *state;
	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	return *state = x;
}

// What a neighbour may be, given the kinds a cell may be: the union of the rule sets.
static WFCSet supported(const WFCSet *rule_sets, const WFCSet *cell, int kinds)
{
	WFCSet out = { { 0 } };
	for (int k = 0; k < kinds; ++k)
		if (set_has(cell, k))
			set_or(&out, &rule_sets[k]);
	return out;
}

typedef struct
{
	const WFCRules *rules;
	int rows, columns;
	WFCSet *cells;
	int *stack;
	bool *queued;
	int stack_size;
} Solver;

static void push(Solver *s, int i)
{
	if (!s->queued[i])
	{
		s->queued[i] = true;
		s->stack[s->stack_size++] = i;
	}
}

// Narrows a cell to the kinds in `allowed`; queues it if it changed. False on a contradiction.
static bool narrow(Solver *s, int i, const WFCSet *allowed)
{
	WFCSet narrowed = s->cells[i];
	set_and(&narrowed, allowed);
	if (set_equal(&narrowed, &s->cells[i]))
		return true;
	s->cells[i] = narrowed;
	if (set_count(&narrowed) == 0)
		return false;
	push(s, i);
	return true;
}

static bool propagate(Solver *s)
{
	const WFCRules *rules = s->rules;
	while (s->stack_size > 0)
	{
		const int i = s->stack[--s->stack_size];
		s->queued[i] = false;
		const int r = i / s->columns, c = i % s->columns;
		if (c + 1 < s->columns)
		{
			const WFCSet allowed = supported(rules->right, &s->cells[i], rules->kinds);
			if (!narrow(s, i + 1, &allowed))
				return false;
		}
		if (c > 0)
		{
			const WFCSet allowed = supported(rules->left, &s->cells[i], rules->kinds);
			if (!narrow(s, i - 1, &allowed))
				return false;
		}
		if (r + 1 < s->rows)
		{
			const WFCSet allowed = supported(rules->down, &s->cells[i], rules->kinds);
			if (!narrow(s, i + s->columns, &allowed))
				return false;
		}
		if (r > 0)
		{
			const WFCSet allowed = supported(rules->up, &s->cells[i], rules->kinds);
			if (!narrow(s, i - s->columns, &allowed))
				return false;
		}
	}
	return true;
}

bool wfc_solve(const WFCRules *rules, int rows, int columns, const int *left, const int *right, const int *above,
               uint32_t seed, int *out)
{
	const int n = rows * columns;
	Solver s = { rules, rows, columns, malloc(sizeof(WFCSet) * n), malloc(sizeof(int) * n), calloc(n, sizeof(bool)), 0 };
	bool ok = s.cells != NULL && s.stack != NULL && s.queued != NULL;
	uint32_t random = seed != 0 ? seed : 1;

	// Every kind that is used at all, then the bindings outside the grid.
	WFCSet used = { { 0 } };
	for (int k = 0; k < rules->kinds; ++k)
		if (rules->weight[k] > 0)
			set_add(&used, k);
	for (int i = 0; ok && i < n; ++i)
		s.cells[i] = used;
	for (int r = 0; ok && r < rows; ++r)
	{
		if (left != NULL && left[r] >= 0)
			ok = narrow(&s, r * columns, &rules->right[left[r]]);
		if (ok && right != NULL && right[r] >= 0)
			ok = narrow(&s, r * columns + columns - 1, &rules->left[right[r]]);
	}
	for (int c = 0; ok && above != NULL && c < columns; ++c)
		if (above[c] >= 0)
			ok = narrow(&s, c, &rules->down[above[c]]);
	ok = ok && propagate(&s);

	// Collapse the cell with the fewest kinds left (ties at random) to one of them, chosen by
	// weight, until all are decided.
	while (ok)
	{
		int best = -1, best_count = 0;
		uint32_t best_tie = 0;
		for (int i = 0; i < n; ++i)
		{
			const int count = set_count(&s.cells[i]);
			if (count <= 1)
				continue;
			const uint32_t tie = next_random(&random);
			if (best < 0 || count < best_count || (count == best_count && tie < best_tie))
			{
				best = i;
				best_count = count;
				best_tie = tie;
			}
		}
		if (best < 0)
			break;

		float total = 0;
		for (int k = 0; k < rules->kinds; ++k)
			if (set_has(&s.cells[best], k))
				total += rules->weight[k];
		float pick = (next_random(&random) / 4294967296.0f) * total;
		int chosen = -1;
		for (int k = 0; k < rules->kinds; ++k)
			if (set_has(&s.cells[best], k))
			{
				chosen = k;
				if ((pick -= rules->weight[k]) < 0)
					break;
			}
		WFCSet one = { { 0 } };
		set_add(&one, chosen);
		ok = narrow(&s, best, &one) && propagate(&s);
	}

	for (int i = 0; ok && i < n; ++i)
		for (int k = 0; k < rules->kinds; ++k)
			if (set_has(&s.cells[i], k))
			{
				out[i] = k;
				break;
			}

	free(s.cells);
	free(s.stack);
	free(s.queued);
	return ok;
}
