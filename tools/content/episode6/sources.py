"""The original levels' maps (as shape numbers) and headers, for the episode 6 tools."""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import levels  # noqa: E402
import tyrdata  # noqa: E402

MAP_SIZES = [(14, 300), (14, 600), (15, 600)]  # the three layers: columns, rows


EMPTY = 0  # no tile (layers 2 and 3 see through)


def tile(layer, table, index):
    """A map byte as a shape number, as JE_loadMap reads it: layers 2 and 3 have no tile at the
    table's last entries (71; 70 for layer 3). A few maps have a stray byte past the table in
    their top row (never shown): no tile."""
    if index >= 128 or (layer == 1 and index >= 71) or (layer == 2 and index >= 70):
        return EMPTY
    return table[index]


def original_levels():
    """Every level the episode scripts load: episode, name, file number, map and shape file
    letters, the three maps (rows of shape numbers, row 0 the top) and their shape tables."""
    out, seen = [], set()
    for ep in range(1, 6):
        data, n, pos = tyrdata.lvl_positions(os.path.join(tyrdata.DATA, f"tyrian{ep}.lvl"))
        for s in levels.read_strings(os.path.join(tyrdata.DATA, f"levels{ep}.dat")):
            if not s.startswith("]L"):
                continue
            name, number = s[13:22].strip(), int(s[25:27])
            if not 0 < number * 2 <= n or (ep, number) in seen:
                continue
            seen.add((ep, number))
            r = tyrdata.Reader(data, pos[(number - 1) * 2])
            map_file, shape_file = chr(r.u8()), chr(r.u8())
            r.u16(3)
            r.u16(r.u16())
            events = r.u16()  # (not r.o += r.u16() * 11: that adds to the offset before the read)
            r.o += events * 11
            tables = []
            for _ in range(3):
                tables.append(list(struct.unpack_from(">128H", data, r.o)))
                r.o += 256
            maps = []
            for k, ((w, h), table) in enumerate(zip(MAP_SIZES, tables)):
                raw = data[r.o:r.o + w * h]
                r.o += w * h
                maps.append([[tile(k, table, raw[y * w + x]) for x in range(w)] for y in range(h)])
            out.append(dict(episode=ep, name=name, number=number, map_file=map_file, shapes=shape_file.lower(),
                            maps=maps, tables=tables))
    return out


def find(names, shapes=None):
    """The original levels with these names (and that shape file)."""
    return [l for l in original_levels() if l["name"] in names and (shapes is None or l["shapes"] == shapes)]
