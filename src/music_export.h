/*
 * Tyrian3D dev tool: TYR3D_EXPORT_MUSIC=<dir> writes every song as a MIDI file to <dir> (and the
 * instruments they use to <dir>/instruments.json), then exits. See music_export.c.
 */
#ifndef MUSIC_EXPORT_H
#define MUSIC_EXPORT_H

void dev_export_music(const char *dir);

#endif /* MUSIC_EXPORT_H */
