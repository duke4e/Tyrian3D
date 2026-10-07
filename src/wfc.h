/*
 * Tyrian3D: a wave function collapse solver for tile grids (the simple tiled model).
 *
 * Rules say which tile kinds may stand to the right of and below each kind, and how often each
 * kind should appear; they are usually learned from an example grid (wfc_learn). The solver fills
 * a grid so that every pair of neighbours follows the rules, starting with the most constrained
 * cells. The grid can be bound to fixed kinds just outside it: a column to its left or right and
 * a row above it.
 */
#ifndef WFC_H
#define WFC_H

#include <stdbool.h>
#include <stdint.h>

#define WFC_MAX_KINDS 128
#define WFC_WORDS (WFC_MAX_KINDS / 64)

typedef struct
{
	uint64_t bits[WFC_WORDS];
} WFCSet;

typedef struct
{
	int kinds;
	WFCSet right[WFC_MAX_KINDS];  // kinds that may stand right of each kind
	WFCSet left[WFC_MAX_KINDS];   // the same rule seen from the other side
	WFCSet down[WFC_MAX_KINDS];   // kinds that may stand below each kind
	WFCSet up[WFC_MAX_KINDS];
	float weight[WFC_MAX_KINDS];  // how often each kind appears (0: never used)
} WFCRules;

static inline bool wfc_has_any(const WFCSet *s)
{
	for (int w = 0; w < WFC_WORDS; ++w)
		if (s->bits[w] != 0)
			return true;
	return false;
}

// Learns the rules from an example grid of kinds (row by row; negative entries are skipped).
void wfc_learn(WFCRules *rules, int kinds, const int *grid, int rows, int columns);

// Fills out (rows x columns kinds, row by row). left/right: per row, the kind just outside the
// grid on that side, or -1 for none (either may be NULL). above: the row just above the grid, or
// NULL. Returns false if it ran into a contradiction (out is then undefined); another seed may
// succeed.
bool wfc_solve(const WFCRules *rules, int rows, int columns, const int *left, const int *right, const int *above,
               uint32_t seed, int *out);

#endif /* WFC_H */
