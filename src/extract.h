/*
 * Tyrian3D dev tool: exports sprite sheets and a catalogue of enemies and ships (see extract.c).
 */
#ifndef EXTRACT_H
#define EXTRACT_H

void dev_extract(const char *dir);
// TYR3D_EXPORT_PICTURES=<dir>: the game's pictures as PNGs, to be drawn anew (README.txt in it says where
// each one shows).
void dev_export_pictures(const char *dir);

#endif /* EXTRACT_H */
