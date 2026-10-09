#!/usr/bin/env python3
"""Reads Tyrian 2000's item data (weapons, ports, specials, generators, ships, sidekicks, shields,
enemies) as JE_loadItemDat does (src/episodes.c), for the content tools.

usage: tools/content/tyrdata.py   (prints each episode's data size and the weapon ports)
"""
import os
import struct

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "tyrian2000"))

WEAP_END1, WEAP_START2, WEAP_NUM = 818, 1000, 1818
PORT_NUM, POWER_NUM, OPTION_NUM, SHIP_NUM, SHIELD_NUM, SPECIAL_NUM = 60, 6, 37, 18, 11, 54
ENEMY_END1, ENEMY_START2, ENEMY_NUM = 850, 1001, 1850


class Reader:
    def __init__(self, data, offset):
        self.b = data
        self.o = offset

    def _read(self, fmt, size, n):
        if n is None:
            v = struct.unpack_from("<" + fmt, self.b, self.o)[0]
            self.o += size
            return v
        v = list(struct.unpack_from(f"<{n}{fmt}", self.b, self.o))
        self.o += size * n
        return v

    def u8(self, n=None):
        return self._read("B", 1, n)

    def s8(self, n=None):
        return self._read("b", 1, n)

    def u16(self, n=None):
        return self._read("H", 2, n)

    def s16(self, n=None):
        return self._read("h", 2, n)

    def s32(self):
        return self._read("i", 4, None)

    def name(self):
        length = self.u8()
        raw = self.b[self.o:self.o + 30]
        self.o += 30
        return raw[:min(length, 30)].decode("latin1")


def lvl_positions(path):
    """A level file's bytes, its entry count and the entries' offsets (plus the end)."""
    data = open(path, "rb").read()
    r = Reader(data, 0)
    n = r.u16()
    pos = [r.s32() for _ in range(n)]
    pos.append(len(data))
    return data, n, pos


def load_items(ep, data_dir=DATA):
    """The item data the game uses in episode ep (1-3: tyrian.hdt; 4-5: the episode's level file)."""
    if ep <= 3:
        data = open(os.path.join(data_dir, "tyrian.hdt"), "rb").read()
        r = Reader(data, 0)
        r.o = r.s32()
    else:
        data, n, pos = lvl_positions(os.path.join(data_dir, f"tyrian{ep}.lvl"))
        r = Reader(data, pos[n - 1])
    item_num = r.u16(7)
    weapons = {}
    for lo, hi in ((0, WEAP_END1), (WEAP_START2, WEAP_NUM)):
        for i in range(lo, hi + 1):
            weapons[i] = dict(drain=r.u16(), shotrepeat=r.u8(), multi=r.u8(), weapani=r.u16(), max=r.u8(), tx=r.u8(),
                              ty=r.u8(), aim=r.u8(), attack=r.u8(8), del_=r.u8(8), sx=r.s8(8), sy=r.s8(8), bx=r.s8(8),
                              by=r.s8(8), sg=r.u16(8), acceleration=r.s8(), accelerationx=r.s8(), circlesize=r.u8(),
                              sound=r.u8(), trail=r.u8(), shipblastfilter=r.u8())
    ports = [dict(name=r.name(), opnum=r.u8(), op=[r.u16(11), r.u16(11)], cost=r.u16(), itemgraphic=r.u16(),
                  poweruse=r.u16()) for _ in range(PORT_NUM + 1)]
    specials = [dict(name=r.name(), itemgraphic=r.u16(), pwr=r.u8(), stype=r.u8(), wpn=r.u16())
                for _ in range(SPECIAL_NUM + 1)]
    gens = [dict(name=r.name(), itemgraphic=r.u16(), power=r.u8(), speed=r.s8(), cost=r.u16())
            for _ in range(POWER_NUM + 1)]
    ships = [dict(name=r.name(), shipgraphic=r.u16(), itemgraphic=r.u16(), ani=r.u8(), spd=r.s8(), dmg=r.u8(),
                  cost=r.u16(), bigshipgraphic=r.u8()) for _ in range(SHIP_NUM + 1)]
    options = [dict(name=r.name(), pwr=r.u8(), itemgraphic=r.u16(), cost=r.u16(), tr=r.u8(), option=r.u8(),
                    opspd=r.s8(), ani=r.u8(), gr=r.u16(20), wport=r.u8(), wpnum=r.u16(), ammo=r.u8(), stop=r.u8(),
                    icongr=r.u8()) for _ in range(OPTION_NUM + 1)]
    shields = [dict(name=r.name(), tpwr=r.u8(), mpwr=r.u8(), itemgraphic=r.u16(), cost=r.u16())
               for _ in range(SHIELD_NUM + 1)]
    enemies = {}
    for lo, hi in ((0, ENEMY_END1), (ENEMY_START2, ENEMY_NUM)):
        for i in range(lo, hi + 1):
            enemies[i] = dict(ani=r.u8(), tur=r.u8(3), freq=r.u8(3), xmove=r.s8(), ymove=r.s8(), xaccel=r.s8(),
                              yaccel=r.s8(), xcaccel=r.s8(), ycaccel=r.s8(), startx=r.s16(), starty=r.s16(),
                              startxc=r.s8(), startyc=r.s8(), armor=r.u8(), esize=r.u8(), egraphic=r.u16(20),
                              explosiontype=r.u8(), animate=r.u8(), shapebank=r.u8(), xrev=r.s8(), yrev=r.s8(),
                              dgr=r.u16(), dlevel=r.s8(), dani=r.s8(), elaunchfreq=r.u8(), elaunchtype=r.u16(),
                              value=r.s16(), eenemydie=r.u16())
    return dict(itemNum=item_num, weapons=weapons, ports=ports, specials=specials, gens=gens, ships=ships,
                options=options, shields=shields, enemies=enemies, end=r.o, size=len(data))


if __name__ == "__main__":
    for ep in range(1, 6):
        items = load_items(ep)
        print(ep, "itemNum", items["itemNum"], "end", items["end"], "size", items["size"])
    for i, p in enumerate(load_items(1)["ports"]):
        print("port", i, repr(p["name"].strip()), p["opnum"], p["op"], p["cost"], p["poweruse"])
