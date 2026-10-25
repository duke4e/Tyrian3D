#!/usr/bin/env python3
"""Voice the data cubes with ElevenLabs: estimate, design the voices, render, assemble.

Reads data/voices/script.json (made by tools/voices/export_cubes.py), tools/voices/cast.json and
tools/voices/pronunciation.json. The API key is read only from the ELEVENLABS_API_KEY environment
variable, the project's .env.local (gitignored; `npx @elevenlabs/cli@latest onboard connect
--env-path .env.local` writes it there) or the file ~/.config/tyrian3d/elevenlabs_key, and only ever
goes into the request's xi-api-key header: it is never printed, logged or written anywhere.
Voice design and adopting voices need a paid plan (the API refuses them on the free one).

  estimate                    characters per speaker and in total, minutes of speech, disk sizes
                              and the plan that covers it (no network)
  design [--speaker K ...]    voice previews from the voice_prompt of every speaker that has no
                              voice yet (ElevenLabs Voice Design, 3 per call), saved to
                              data/voices/previews/<speaker>/; listen, then
  adopt K N                   makes preview N (or R-N: round R) speaker K's voice and writes its
                              voice_id into cast.json (adopt K --voice-id ID: any voice, e.g. one
                              from the Voice Library, which needs no voice slot)
  generate [--only E|E:N|E:N:S] [--speaker K] [--jobs N] [--max-chars N] [--retake E:N[:S]]
                              renders every segment not in the cache (data/voices/cache: keyed by
                              a hash of the text, voice, model and settings, so a rerun or a
                              corrected line renders only what changed), then assembles
                              data/voices/e<E>/<N>.wav and data/voices/manifest.json/.txt
  build                       assembles the cubes again from the cache (no network): after
                              changing pauses, speed, loudness or the file format
  try --speaker K "text"      renders one line to data/voices/try/ (a voice, a name's reading)
  dictionary                  uploads pronunciation.json as an ElevenLabs pronunciation
                              dictionary (used when cast.json defaults.pronunciation is
                              "dictionary"; the default "alias" substitutes the respellings here)
  status                      the account's credits and voice slots (one request)

ElevenLabs documentation used (2026-10-24): see DOCS below.
"""
import argparse
import array
import base64
import concurrent.futures
import datetime
import hashlib
import io
import json
import math
import os
import random
import re
import shutil
import ssl
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CAST_PATH = os.path.join(HERE, "cast.json")
PRON_PATH = os.path.join(HERE, "pronunciation.json")
VOICES = os.path.join(ROOT, "data", "voices")
KEY_FILE = os.path.expanduser("~/.config/tyrian3d/elevenlabs_key")
ENV_FILE = os.path.join(ROOT, ".env.local")  # npx @elevenlabs/cli onboard connect writes ELEVENLABS_API_KEY there (gitignored)
# ELEVENLABS_API_BASE: one of the regional servers the API reference lists (api.us.elevenlabs.io,
# api.eu.residency.elevenlabs.io, ...), for accounts with data residency.
API = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io").rstrip("/")

DOCS = {
    "text to speech (with timestamps)": "https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps",
    "text to speech": "https://elevenlabs.io/docs/api-reference/text-to-speech/convert",
    "models": "https://elevenlabs.io/docs/models",
    "voice design": "https://elevenlabs.io/docs/api-reference/text-to-voice/design",
    "create voice from preview": "https://elevenlabs.io/docs/api-reference/text-to-voice/create",
    "pronunciation dictionary from rules": "https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/create-from-rules",
    "subscription": "https://elevenlabs.io/docs/api-reference/user/subscription/get",
    "errors": "https://elevenlabs.io/docs/eleven-api/resources/errors",
    "pricing": "https://elevenlabs.io/pricing",
}

# https://elevenlabs.io/pricing, 2026-10-24: (plan, $/month, credits/month, custom voice slots, concurrency, note).
# Unused credits of a paid plan roll over for two months (at most 2x the monthly amount).
PLANS = [
    ("Free", 0, 10_000, 3, 2, "no commercial licence"),
    ("Starter", 6, 30_000, 10, 3, "$1 the first month"),
    ("Creator", 22, 121_000, 30, 5, "$11 the first month; extra usage about $0.18 per 1000 credits"),
    ("Pro", 99, 600_000, 160, 10, "44.1 kHz PCM through the API"),
    ("Scale", 299, 1_800_000, 660, 15, ""),
]
FIRST_MONTH = {"Starter": 1, "Creator": 11}
# Text to speech costs 1 credit a character; the Flash models 0.5 through the API (pricing page).
CREDITS_PER_CHAR = {"eleven_flash_v2": 0.5, "eleven_flash_v2_5": 0.5}
CHARS_PER_MINUTE = (850, 1000)   # speech pace: ElevenLabs counts 1000 characters a minute; acted v3 reads slower
IMA_BYTES_PER_SAMPLE = 0.502     # IMA ADPCM, mono, ffmpeg's blocks (measured)
DIALOGUE_LIMIT = 1900            # text to dialogue: at most 2,000 characters a request, all inputs together


class Fatal(Exception):
    """Stops the whole run (no key, no credits, a refused key)."""


class Failed(Exception):
    """One request failed for good (a bad request); the run goes on."""


# --- files -------------------------------------------------------------------------------------

def load_json(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        raise Fatal(f"{os.path.relpath(path, ROOT)} is missing" +
                    (" (run tools/voices/export_cubes.py first)" if path.endswith("script.json") else ""))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data, compact=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=None if compact else 2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


# --- the key and the API -----------------------------------------------------------------------

_key = None


_ssl = None


def ssl_context():
    """Certificates checked as always; a python.org Python on macOS ships without its own CA
    bundle (until "Install Certificates.command" runs), so the system's is used then."""
    global _ssl
    if _ssl is None:
        _ssl = ssl.create_default_context()
        if not _ssl.get_ca_certs():
            for bundle in (os.environ.get("SSL_CERT_FILE"), "/etc/ssl/cert.pem", "/opt/homebrew/etc/ca-certificates/cert.pem"):
                if bundle and os.path.exists(bundle):
                    _ssl.load_verify_locations(cafile=bundle)
                    break
    return _ssl


def api_key():
    global _key
    if _key is None:
        k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not k and os.path.exists(ENV_FILE):
            with open(ENV_FILE, encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"\s*(?:export\s+)?ELEVENLABS_API_KEY\s*=\s*(.*?)\s*$", line)
                    if m:
                        k = m.group(1).strip().strip("'\"")
        if not k and os.path.exists(KEY_FILE):
            mode = os.stat(KEY_FILE).st_mode
            if mode & (stat.S_IRGRP | stat.S_IROTH):
                print(f"note: {KEY_FILE} is readable by others; chmod 600 it", file=sys.stderr)
            with open(KEY_FILE, encoding="utf-8") as f:
                k = f.read().strip()
        if not k:
            raise Fatal("no API key: set ELEVENLABS_API_KEY, or run npx @elevenlabs/cli@latest onboard connect --env-path .env.local, "
                        "or put the key in ~/.config/tyrian3d/elevenlabs_key")
        _key = k
    return _key


def error_of(e):
    """(status, code, message) of an HTTPError, without anything from the request."""
    try:
        body = json.loads(e.read().decode("utf-8", "replace"))
        d = body.get("detail", body)
        if isinstance(d, dict):
            return e.code, str(d.get("code") or d.get("status") or ""), str(d.get("message") or "")
        return e.code, "", json.dumps(d)[:300]
    except Exception:
        return e.code, "", ""


def call(method, path, body=None, query=None, accept="application/json", timeout=300, attempts=7):
    """One API request with retries for rate limits and the server's troubles. Returns
    (headers, body bytes)."""
    url = API + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(attempts):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("xi-api-key", api_key())
        req.add_header("Accept", accept)
        req.add_header("User-Agent", "tyrian3d-voices/1")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        wait = None
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as r:
                return {k.lower(): v for k, v in r.headers.items()}, r.read()
        except urllib.error.HTTPError as e:
            status, code, message = error_of(e)
            what = f"HTTP {status}" + (f" {code}" if code else "") + (f": {message}" if message else "")
            if status in (401, 402, 403):
                raise Fatal(what)
            if status == 429 or status == 409 or status >= 500:
                retry_after = e.headers.get("Retry-After") if e.headers else None
                if retry_after and retry_after.isdigit():
                    wait = int(retry_after)
                elif code in ("concurrent_limit_exceeded", "too_many_concurrent_requests"):
                    wait = 2 + attempt * 2
                else:
                    wait = min(60, 2 ** (attempt + 1))
                last = what
            else:
                raise Failed(what)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            wait = min(60, 2 ** (attempt + 1))
            last = f"network: {getattr(e, 'reason', e)}"
        time.sleep(wait + random.uniform(0, 1))
    raise Failed(f"gave up after {attempts} attempts ({last})")


# --- cast, models, text -----------------------------------------------------------------------

def is_tag_model(model):
    return model.startswith("eleven_v3") or model.startswith("eleven_v4")


def chain(cast, key):
    """The speaker and the speakers whose voice it borrows, root first."""
    out, seen = [], set()
    while key and key not in seen:
        seen.add(key)
        spk = cast["speakers"].get(key)
        if spk is None:
            raise Fatal(f"speaker {key!r} is not in cast.json (run export_cubes.py again?)")
        out.append((key, spk))
        key = spk.get("voice_of")
    return list(reversed(out))


def speaker_conf(cast, key, model_override=None):
    """Everything a speaker's segments are rendered with."""
    d = cast["defaults"]
    links = chain(cast, key)
    settings = dict(d.get("settings", {}))
    voice_id, model, prefix = "", None, ""
    for _, spk in links:
        settings.update(spk.get("settings") or {})
        voice_id = spk.get("voice_id") or voice_id
        model = spk.get("model_id") or model
    prefix = cast["speakers"][key].get("v3_prefix", "")
    model = model_override or model or d["model_id"]
    return {"key": key, "root": links[0][0], "voice_id": voice_id, "model": model, "settings": settings,
            "prefix": prefix, "tags": is_tag_model(model)}


def api_settings(conf):
    """voice_settings as the model takes them; speed the model does not take is applied later."""
    s, model = conf["settings"], conf["model"]
    out = {"stability": float(s.get("stability", 0.5)), "similarity_boost": float(s.get("similarity_boost", 0.75)),
           "use_speaker_boost": bool(s.get("use_speaker_boost", True))}
    post_speed = 1.0
    if model.startswith("eleven_v3"):
        out["stability"] = min((0.0, 0.5, 1.0), key=lambda v: abs(v - out["stability"]))  # Creative/Natural/Robust
        post_speed = float(s.get("speed", 1.0))
    elif model.startswith("eleven_v4"):
        post_speed = float(s.get("speed", 1.0))  # v4: no style or speed (eleven-v4 capability page)
    else:
        out["style"] = float(s.get("style", 0.0))
        out["speed"] = max(0.7, min(1.2, float(s.get("speed", 1.0))))
    return out, max(0.8, min(1.25, post_speed))


def alias_rules(pron):
    rules = []
    for t in sorted(pron["terms"], key=lambda t: -len(t["term"])):
        say, term = t.get("say"), t["term"]
        if not say:
            continue
        if t.get("kind") in ("acronym", "code") or not term[0].isalpha():
            rx = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)")
            rules.append((rx, lambda m, s=say: s))
        else:  # a name: also when the text has it in lower case ("gencore")
            rx = re.compile(r"(?<!\w)([" + term[0].upper() + term[0].lower() + "])" + re.escape(term[1:]) + r"(?!\w)")
            rules.append((rx, lambda m, s=say: (s[0].lower() + s[1:]) if m.group(1).islower() else s))
    return rules


def apply_aliases(text, rules):
    for rx, repl in rules:
        text = rx.sub(repl, text)
    return text


def strip_tags(text):
    return re.sub(r"[ \t]{2,}", " ", re.sub(r"\[[^\[\]]*\]\s*", "", text)).strip()


def request_text(seg, conf, rules):
    """The text sent for a segment and where each of its pieces lies in it."""
    text, spans = "", []
    if conf["tags"] and conf["prefix"]:
        text = conf["prefix"]
    for piece in seg["pieces"]:
        t = apply_aliases(piece["tts"], rules) if rules is not None else piece["tts"]
        if not conf["tags"]:
            t = strip_tags(t)
        if not t:
            spans.append((len(text), len(text)))
            continue
        if spans and any(b > a for a, b in spans):
            text += piece["sep"] or " "
        spans.append((len(text), len(text) + len(t)))
        text += t
    if not conf["tags"] and not re.search(r"[A-Za-z0-9]", text):
        return "", spans
    return text, spans


class Context:
    def __init__(self, args, need_script=True):
        self.args = args
        self.out = os.path.abspath(getattr(args, "out_dir", None) or VOICES)
        self.cast = load_json(CAST_PATH)
        self.pron = load_json(PRON_PATH)
        self.script = load_json(os.path.join(VOICES, "script.json")) if need_script else None
        self.state_path = os.path.join(VOICES, "state.json")
        self.state = load_json(self.state_path, {})
        self.takes = load_json(os.path.join(VOICES, "takes.json"), {})
        self.mode = self.cast["defaults"].get("pronunciation", "alias")
        self.rules = alias_rules(self.pron) if self.mode != "dictionary" else None
        self.cache = os.path.join(VOICES, "cache")
        self.model_override = getattr(args, "model", None)
        self.lock = threading.Lock()

    def conf(self, key):
        return speaker_conf(self.cast, key, self.model_override)

    def dictionary(self, strict=True):
        if self.mode != "dictionary":
            return None
        d = self.state.get("dictionary")
        if not d and not strict:
            return [{"pronunciation_dictionary_id": "(not created yet)"}]
        if not d:
            raise Fatal("cast.json asks for the pronunciation dictionary: run generate.py dictionary first")
        return [{"pronunciation_dictionary_id": d["id"], "version_id": d["version_id"]}]

    def cubes(self):
        """The cubes to voice, then the story texts between levels (numbered from 101 in each
        episode, the end's hints from 201: export_cubes.py), which are voiced as cubes are."""
        for ep in self.script["episodes"]:
            for c in ep["cubes"] + ep.get("stories", []):
                if not c["skip"]:
                    yield c

    def job(self, cube, seg, strict=True):
        """What a segment is rendered with, and its cache key."""
        conf = self.conf(seg["speaker"])
        text, spans = request_text(seg, conf, self.rules)
        settings, post_speed = api_settings(conf)
        take = int(self.takes.get(f"{cube['id']}:{seg['index']}", 0))
        seed = int(hashlib.sha256(f"{cube['id']}:{seg['index']}:{take}".encode()).hexdigest()[:8], 16)
        d = self.cast["defaults"]
        body = {"text": text, "model_id": conf["model"], "voice_settings": settings, "seed": seed}
        if not conf["model"].startswith("eleven_multilingual_v2") and d.get("language_code"):
            body["language_code"] = d["language_code"]
        if d.get("apply_text_normalization", "auto") != "auto":
            body["apply_text_normalization"] = d["apply_text_normalization"]
        locators = self.dictionary(strict)
        if locators:
            body["pronunciation_dictionary_locators"] = locators
        fmt = d.get("output_format", "pcm_24000")
        ident = json.dumps({"v": 1, "voice": conf["voice_id"], "format": fmt, "body": body}, sort_keys=True)
        key = hashlib.sha256(ident.encode("utf-8")).hexdigest()
        return {"cube": cube, "seg": seg, "conf": conf, "text": text, "spans": spans, "body": body,
                "format": fmt, "key": key, "post_speed": post_speed, "take": take}

    def units(self, cube, strict=True):
        """The cube's requests in order: a segment each, or, where cast.json cube_rules gives the
        cube "dialogue", runs of its segments sent together to text to dialogue (eleven_v3 acts
        short alternating lines better in context)."""
        jobs = [self.job(cube, s, strict) for s in cube["segments"]]
        jobs = [j for j in jobs if j["text"]]
        rule = self.cast.get("cube_rules", {}).get(cube["id"], {}).get("dialogue")
        if not rule:
            return [dict(j, kind="tts", jobs=[j]) for j in jobs]
        rule = rule if isinstance(rule, dict) else {}
        lo, hi = rule.get("from", 0), rule.get("to", 10 ** 6)
        out, run = [], []

        def flush():
            if len(run) >= 2:
                out.append(self.dialogue_job(cube, list(run), rule, strict))
            else:
                out.extend(dict(j, kind="tts", jobs=[j]) for j in run)
            run.clear()
        for j in jobs:
            # a dialogue takes one model with audio tags; a segment on another model goes alone
            if not lo <= j["seg"]["index"] <= hi or not j["conf"]["tags"]:
                flush()
                out.append(dict(j, kind="tts", jobs=[j]))
                continue
            if run and (j["conf"]["model"] != run[0]["conf"]["model"]
                        or sum(len(x["text"]) for x in run) + len(j["text"]) > DIALOGUE_LIMIT):
                flush()
            run.append(j)
        flush()
        return out

    def dialogue_job(self, cube, jobs, rule, strict=True):
        d = self.cast["defaults"]
        take = sum(int(self.takes.get(f"{cube['id']}:{j['seg']['index']}", 0)) for j in jobs)
        first = jobs[0]["seg"]["index"]
        seed = int(hashlib.sha256(f"{cube['id']}:d{first}:{take}".encode()).hexdigest()[:8], 16)
        stability = float(rule.get("stability", d.get("settings", {}).get("stability", 0.5)))
        if jobs[0]["conf"]["model"].startswith("eleven_v3"):
            stability = min((0.0, 0.5, 1.0), key=lambda v: abs(v - stability))
        body = {"inputs": [{"text": j["text"], "voice_id": j["conf"]["voice_id"]} for j in jobs],
                "model_id": jobs[0]["conf"]["model"], "settings": {"stability": stability}, "seed": seed}
        for k in ("language_code", "apply_text_normalization", "pronunciation_dictionary_locators"):
            if k in jobs[0]["body"]:
                body[k] = jobs[0]["body"][k]
        fmt = d.get("output_format", "pcm_24000")
        ident = json.dumps({"v": 1, "kind": "dialogue", "format": fmt, "body": body}, sort_keys=True)
        return {"kind": "dialogue", "cube": cube, "jobs": jobs, "seg": jobs[0]["seg"], "conf": jobs[0]["conf"],
                "text": "\n".join(j["text"] for j in jobs), "chars": sum(len(j["text"]) for j in jobs),
                "body": body, "format": fmt, "key": hashlib.sha256(ident.encode("utf-8")).hexdigest(),
                "take": take, "post_speed": 1.0}

    def cache_paths(self, key):
        d = os.path.join(self.cache, key[:2])
        return os.path.join(d, key + ".audio"), os.path.join(d, key + ".json")

    def cached(self, job):
        audio, meta = self.cache_paths(job["key"])
        return os.path.exists(audio) and os.path.exists(meta)


# --- selection --------------------------------------------------------------------------------

def parse_only(values):
    out = []
    for v in values or []:
        for part in v.split(","):
            part = part.strip()
            if part:
                bits = part.split(":")
                if not all(b.isdigit() for b in bits) or len(bits) > 3:
                    raise Fatal(f"--only {part!r}: give an episode (4), a cube (4:17) or a segment (4:17:2)")
                out.append(tuple(int(b) for b in bits))
    return out


def selected(ctx, only, speakers, referenced_only=False):
    """(cube, segment) pairs the options pick."""
    for c in ctx.cubes():
        if referenced_only and not c["referenced"]:
            continue
        if only and not any(o[0] == c["episode"] and (len(o) < 2 or o[1] == c["cube"]) for o in only):
            continue
        for s in c["segments"]:
            if only and not any(o[0] == c["episode"] and (len(o) < 2 or o[1] == c["cube"]) and (len(o) < 3 or o[2] == s["index"])
                                for o in only):
                continue
            if speakers:
                conf = ctx.conf(s["speaker"])
                if s["speaker"] not in speakers and conf["root"] not in speakers:
                    continue
            yield c, s


# --- estimate ---------------------------------------------------------------------------------

def cmd_estimate(ctx):
    per_speaker, per_voice, per_episode = {}, {}, {}
    total = cached = segments = 0
    credits = 0.0
    models = set()
    dialogues = 0
    for c in ctx.cubes():
        for u in ctx.units(c, strict=False):
            if u["kind"] == "dialogue":
                dialogues += 1
                if all(j["conf"]["voice_id"] for j in u["jobs"]) and ctx.cached(u):
                    cached += u["chars"]
            elif u["conf"]["voice_id"] and ctx.cached(u):
                cached += len(u["text"])
            for j in u["jobs"]:
                s = j["seg"]
                n = len(j["text"])
                segments += 1
                total += n
                credits += n * CREDITS_PER_CHAR.get(j["conf"]["model"], 1.0)
                models.add(j["conf"]["model"])
                k, root = s["speaker"], j["conf"]["root"]
                e = per_speaker.setdefault(k, {"chars": 0, "cubes": set(), "segments": 0, "root": root})
                e["chars"] += n
                e["cubes"].add(c["id"])
                e["segments"] += 1
                per_voice[root] = per_voice.get(root, 0) + n
                per_episode[c["episode"]] = per_episode.get(c["episode"], 0) + n
    roots = sorted(per_voice, key=lambda r: -per_voice[r])
    need_design = [r for r in roots if not ctx.cast["speakers"][r].get("voice_id")]
    print(f"Script: {sum(1 for _ in ctx.cubes())} cubes, {segments} segments, {total:,} characters to send "
          f"(after the pronunciation respellings and tags), model {', '.join(sorted(models))}")
    print("By episode: " + ", ".join(f"{e}: {n:,}" for e, n in sorted(per_episode.items()))
          + f"; {dialogues} runs of short lines go to text to dialogue (cast.json cube_rules)")
    print()
    print(f"{'speaker':14s} {'voice':14s} {'cubes':>5s} {'segs':>5s} {'chars':>8s} {'share':>6s}")
    for k in sorted(per_speaker, key=lambda k: (-per_voice[per_speaker[k]['root']], per_speaker[k]['root'] != k, -per_speaker[k]['chars'])):
        e = per_speaker[k]
        print(f"{k:14s} {(e['root'] if e['root'] != k else '(own)'):14s} {len(e['cubes']):5d} {e['segments']:5d} "
              f"{e['chars']:8,d} {100.0 * e['chars'] / total:5.1f}%")
    print()
    print(f"Voices: {len(roots)} (designed voices take a custom voice slot each; Voice Library voices take none); "
          f"{len(need_design)} have no voice_id yet")
    print("Characters per voice: " + ", ".join(f"{r} {per_voice[r]:,}" for r in roots))
    print()
    pauses_s = segments * 0.5 + sum(1 for _ in ctx.cubes()) * 0.47
    lo = total / CHARS_PER_MINUTE[1] + pauses_s / 60
    hi = total / CHARS_PER_MINUTE[0] + pauses_s / 60
    mid = (lo + hi) / 2
    rate = int(re.sub(r"\D", "", ctx.cast["defaults"].get("output_format", "pcm_24000").split("_")[1]) or 24000)
    print(f"Speech: about {lo:.0f}-{hi:.0f} minutes ({total / CHARS_PER_MINUTE[1]:.0f}-{total / CHARS_PER_MINUTE[0]:.0f} "
          f"spoken at {CHARS_PER_MINUTE[0]}-{CHARS_PER_MINUTE[1]} characters a minute, plus pauses)")
    print(f"Disk for the cubes' WAV files ({mid:.0f} minutes, mono):")
    for name, r, bps in [("IMA ADPCM", rate, IMA_BYTES_PER_SAMPLE), ("16-bit PCM", rate, 2.0),
                         ("IMA ADPCM", 44100, IMA_BYTES_PER_SAMPLE), ("16-bit PCM", 44100, 2.0), ("16-bit PCM", 22050, 2.0)]:
        mb = mid * 60 * r * bps / 1e6
        chosen = "  <- chosen" if name.startswith("IMA") and r == rate and ctx.cast["defaults"]["audio"]["format"] == "ima_adpcm" else ""
        chosen = chosen or ("  <- chosen" if name.startswith("16") and r == rate and ctx.cast["defaults"]["audio"]["format"] == "pcm16" else "")
        print(f"  {name:10s} {r:5d} Hz: {mb:6.0f} MB{chosen}")
    print(f"  the render cache (the lossless source, kept for retakes and rebuilds): about {mid * 60 * rate * 2 / 1e6:.0f} MB")
    print()
    design_chars = len(need_design) * 2 * 300  # two design calls of ~300 characters a voice
    need = credits * 1.15 + design_chars
    print(f"Credits: {credits:,.0f} to render once (1 a character), {cached:,} characters already in the cache; "
          f"with 15% for retakes and {design_chars:,} for voice design (2 rounds a voice): about {need:,.0f}")
    print("Plans (elevenlabs.io/pricing, 2026-10-24): credits a month, custom voices, parallel requests")
    best = None
    for name, price, monthly, slots, conc, note in PLANS:
        months = max(1, math.ceil(need / monthly))
        fits = slots >= len(roots)
        cost = (FIRST_MONTH.get(name, price) + price * (months - 1)) if price else 0
        verdict = ("enough in one month" if months == 1 else f"{months} months") + ("" if fits else f", only {slots} voice slots")
        print(f"  {name:8s} ${price:>3}/month  {monthly:>9,d}  {slots:>4d} voices  {conc:>2d} parallel: {verdict}"
              + (f" (${cost})" if price and months <= 6 else "") + (f"; {note}" if note else ""))
        if price and fits and months <= 2 and (best is None or cost < best[1]):
            best = (name, cost, months)
    if best:
        print(f"Recommended: {best[0]} ({best[2]} month{'s' if best[2] > 1 else ''}, about ${best[1]}); "
              f"or one month with usage-based billing on for the rest")
    return 0


# --- rendering --------------------------------------------------------------------------------

_timestamps_ok = {"tts": True, "dialogue": True}


def post(ctx, kind, path_plain, path_ts, body, query):
    """POST to the with-timestamps endpoint (alignment for the subtitles' timing), or to the plain
    one if that is refused for this model."""
    if _timestamps_ok[kind]:
        try:
            headers, raw = call("POST", path_ts, body, query)
            return headers, json.loads(raw)
        except Failed as e:
            if "timestamp" not in str(e).lower() and "alignment" not in str(e).lower():
                raise
            _timestamps_ok[kind] = False
    headers, raw = call("POST", path_plain, body, query, accept="*/*")
    return headers, {"audio": raw}


def render(ctx, job):
    """Renders one request (a segment, or a dialogue of several) into the cache; returns the
    characters it cost."""
    audio_path, meta_path = ctx.cache_paths(job["key"])
    query = {"output_format": job["format"]}
    meta = {"cube": job["cube"]["id"], "format": job["format"], "model": job["body"]["model_id"],
            "seed": job["body"]["seed"], "take": job["take"], "created": datetime.datetime.now().isoformat(timespec="seconds")}
    if job["kind"] == "dialogue":
        headers, data = post(ctx, "dialogue", "/v1/text-to-dialogue", "/v1/text-to-dialogue/with-timestamps", job["body"], query)
        spans = {}
        for vs in data.get("voice_segments") or []:
            i = vs.get("dialogue_input_index")
            if i is None:
                continue
            t0, t1 = vs["start_time_seconds"] * 1000, vs["end_time_seconds"] * 1000
            old = spans.get(i)
            spans[i] = (min(old[0], t0), max(old[1], t1)) if old else (t0, t1)
        meta.update({"kind": "dialogue", "segments": [j["seg"]["index"] for j in job["jobs"]],
                     "speakers": [j["seg"]["speaker"] for j in job["jobs"]], "chars": job["chars"],
                     "inputs_ms": [list(map(round, spans[i])) if i in spans else None for i in range(len(job["jobs"]))],
                     "texts": [j["text"] for j in job["jobs"]]})
    else:
        voice = job["conf"]["voice_id"]
        headers, data = post(ctx, "tts", f"/v1/text-to-speech/{voice}", f"/v1/text-to-speech/{voice}/with-timestamps",
                             job["body"], query)
        al, alignment = data.get("alignment") or {}, None
        if al.get("characters"):
            alignment = {"chars": len(al["characters"]),
                         "start_ms": [round(x * 1000) for x in al["character_start_times_seconds"]],
                         "end_ms": [round(x * 1000) for x in al["character_end_times_seconds"]],
                         "text_matches": "".join(al["characters"]) == job["text"]}
        meta.update({"kind": "tts", "segment": job["seg"]["index"], "speaker": job["seg"]["speaker"], "voice_id": voice,
                     "chars": len(job["text"]), "text": job["text"], "alignment": alignment})
    audio = data["audio"] if "audio" in data else base64.b64decode(data["audio_base64"])
    cost = headers.get("character-cost")
    meta["character_cost"] = int(cost) if cost and cost.isdigit() else None
    meta["request_id"] = headers.get("request-id")
    write_bytes(audio_path, audio)
    save_json(meta_path, meta, compact=True)
    return meta["character_cost"] or meta["chars"]


def check_credits(ctx, need, force):
    try:
        _, raw = call("GET", "/v1/user/subscription", attempts=3)
    except Failed as e:
        print(f"note: could not read the subscription ({e}); going on")
        return
    sub = json.loads(raw)
    left = sub.get("character_limit", 0) - sub.get("character_count", 0)
    print(f"Account: {sub.get('tier')} plan, {left:,} credits left this period; this run needs about {need:,}")
    if need > left and not force:
        extra = " (usage-based billing is on, so it would bill the rest)" if sub.get("can_extend_character_limit") else ""
        raise Fatal(f"not enough credits for this run{extra}; render less (--only, --max-chars) or pass --force")


def unit_chars(u):
    return u["chars"] if u["kind"] == "dialogue" else len(u["text"])


def unit_name(u):
    segs = [j["seg"]["index"] for j in u["jobs"]]
    who = sorted({j["seg"]["speaker"] for j in u["jobs"]})
    idx = f"{segs[0]}" if len(segs) == 1 else f"{segs[0]}-{segs[-1]} (dialogue)"
    return f"{u['cube']['id']}:{idx} {'+'.join(who)}"


def selected_units(ctx, only, speakers, referenced_only, strict=True):
    """The requests that hold a segment the options pick."""
    picked = {(c["id"], s["index"]) for c, s in selected(ctx, only, speakers, referenced_only)}
    cubes = sorted({cid for cid, _ in picked}, key=lambda cid: tuple(int(x) for x in cid.split(":")))
    by_id = {c["id"]: c for c in ctx.cubes()}
    for cid in cubes:
        for u in ctx.units(by_id[cid], strict):
            if any((cid, j["seg"]["index"]) in picked for j in u["jobs"]):
                yield u


def cmd_generate(ctx):
    args = ctx.args
    for r in args.retake or []:
        bits = r.split(":")
        if len(bits) not in (2, 3) or not all(b.isdigit() for b in bits):
            raise Fatal(f"--retake {r!r}: give a cube (4:17) or a segment (4:17:2)")
        cube = next((c for c in ctx.cubes() if c["id"] == f"{bits[0]}:{bits[1]}"), None)
        if cube is None:
            raise Fatal(f"--retake {r}: no such cube")
        for s in cube["segments"]:
            if len(bits) == 2 or int(bits[2]) == s["index"]:
                k = f"{cube['id']}:{s['index']}"
                ctx.takes[k] = int(ctx.takes.get(k, 0)) + 1
        save_json(os.path.join(VOICES, "takes.json"), ctx.takes)
    if args.retake and not args.only:
        args.only = list(args.retake)
    only = parse_only(args.only)
    speakers = set(args.speaker or [])
    todo, missing_voice, skipped = [], {}, 0
    for u in selected_units(ctx, only, speakers, args.referenced_only):
        lacking = [j["conf"]["root"] for j in u["jobs"] if not j["conf"]["voice_id"]]
        if lacking:
            for root in lacking:
                missing_voice[root] = missing_voice.get(root, 0) + 1
            continue
        if ctx.cached(u):
            skipped += 1
            continue
        todo.append(u)
    need = sum(unit_chars(u) for u in todo)
    for root, n in sorted(missing_voice.items()):
        print(f"no voice yet for {root} ({n} segments): generate.py design --speaker {root}, then adopt")
    if args.max_chars:
        kept, total = [], 0
        for u in todo:
            if total + unit_chars(u) > args.max_chars:
                break
            kept.append(u)
            total += unit_chars(u)
        if len(kept) < len(todo):
            print(f"--max-chars {args.max_chars:,}: rendering {len(kept)} of {len(todo)} requests")
        todo, need = kept, total
    print(f"{len(todo)} requests to render ({need:,} characters), {skipped} already in the cache")
    if args.dry_run:
        for u in todo:
            print(f"  {unit_name(u)} {unit_chars(u)} ch")
        return 0
    failures = []
    if todo:
        check_credits(ctx, need, args.force)
        done = [0, 0]
        stop = threading.Event()

        def work(u):
            if stop.is_set():
                return
            try:
                cost = render(ctx, u)
            except Fatal:
                stop.set()
                raise
            except Failed as e:
                with ctx.lock:
                    failures.append((u, str(e)))
                    print(f"  FAILED {unit_name(u)}: {e}")
                return
            with ctx.lock:
                done[0] += 1
                done[1] += cost
                print(f"  [{done[0]}/{len(todo)}] {unit_name(u):40s} {unit_chars(u):5d} ch   total {done[1]:,} / {need:,}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futures = [pool.submit(work, u) for u in todo]
            fatal = None
            for f in concurrent.futures.as_completed(futures):
                try:
                    f.result()
                except Fatal as e:
                    fatal = fatal or e
            if fatal:
                raise fatal
        print(f"rendered {done[0]} requests, {done[1]:,} characters charged")
    if not args.no_build:
        build(ctx, only, speakers if speakers else None, args.referenced_only)
    if failures:
        print(f"{len(failures)} requests failed; run the same command again to retry them")
        return 1
    return 0


# --- assembling the cubes ---------------------------------------------------------------------

def ffmpeg_path(args):
    p = getattr(args, "ffmpeg", None) or os.environ.get("FFMPEG") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(p):
        p = shutil.which("ffmpeg") or p
    if not os.path.exists(p):
        raise Fatal("ffmpeg not found (give --ffmpeg PATH)")
    return p


def ff(ffmpeg, args, data=None):
    p = subprocess.run([ffmpeg, "-hide_banner", "-nostdin" if data is None else "-nostats"] + args,
                       input=data, capture_output=True)
    err = p.stderr.decode("utf-8", "replace")
    if p.returncode != 0:
        last = err.strip().splitlines()[-1] if err.strip() else f"exit status {p.returncode}"
        raise Failed("ffmpeg: " + last)
    return p.stdout, err


def decode_segment(ffmpeg, audio_path, fmt, rate):
    """The cached audio as 16-bit mono samples at rate."""
    with open(audio_path, "rb") as f:
        raw = f.read()
    src_rate, pcm = None, None
    if fmt.startswith("pcm_"):
        src_rate, pcm = int(fmt.split("_")[1]), raw
    elif fmt.startswith("wav_"):
        with wave.open(io.BytesIO(raw)) as w:
            src_rate, pcm = w.getframerate(), w.readframes(w.getnframes())
    if src_rate != rate or pcm is None:
        if src_rate:
            pcm, _ = ff(ffmpeg, ["-f", "s16le", "-ar", str(src_rate), "-ac", "1", "-i", "-", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-"], pcm)
        else:
            pcm, _ = ff(ffmpeg, ["-i", audio_path, "-f", "s16le", "-ar", str(rate), "-ac", "1", "-"])
    a = array.array("h")
    a.frombytes(pcm[:len(pcm) // 2 * 2])
    if sys.byteorder != "little":
        a.byteswap()
    return a


def trim_silence(a, rate, db, margin_ms=40):
    thr = int(32768 * 10 ** (db / 20))
    win = max(1, rate // 100)
    n, start, end = len(a), 0, len(a)
    while start < n:
        c = a[start:start + win]
        if max(c) > thr or -min(c) > thr:
            break
        start += win
    while end > start:
        c = a[max(start, end - win):end]
        if max(c) > thr or -min(c) > thr:
            break
        end -= win
    m = rate * margin_ms // 1000
    return max(0, start - m), min(n, end + m)


def loudness(ffmpeg, pcm, rate, target):
    """loudnorm's first pass: the measured values (input_i ...), or None if too short or silent."""
    if len(pcm) < rate * 2:  # under a second
        return None
    _, err = ff(ffmpeg, ["-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "-", "-af",
                         f"loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}:print_format=json", "-f", "null", "-"], pcm)
    m = re.findall(r"\{[^{}]*\}", err)
    if not m:
        return None
    d = json.loads(m[-1])
    try:
        if not math.isfinite(float(d["input_i"])) or float(d["input_i"]) < -70:
            return None
    except ValueError:
        return None
    return d


def build(ctx, only=None, speakers=None, referenced_only=False):
    """Joins every complete cube of the selection into its WAV file and writes the manifest."""
    ffmpeg = ffmpeg_path(ctx.args)
    d = ctx.cast["defaults"]
    au = d["audio"]
    fmt_name = getattr(ctx.args, "format", None) or au.get("format", "ima_adpcm")
    rate = int(au.get("sample_rate") or (d.get("output_format", "pcm_24000").split("_")[1] if d.get("output_format", "").startswith(("pcm_", "wav_")) else 24000))
    target = {"I": au.get("loudness_lufs", -18.0), "TP": au.get("true_peak_db", -1.5), "LRA": au.get("lra", 11.0)}
    pause = au.get("pause_ms", {})
    manifest_path = os.path.join(ctx.out, "manifest.json")
    manifest = load_json(manifest_path, {"cubes": {}})
    built, incomplete = 0, []
    cubes = [c for c in ctx.cubes() if (not referenced_only or c["referenced"])
             and (not only or any(o[0] == c["episode"] and (len(o) < 2 or o[1] == c["cube"]) for o in only))]

    def silence(ms):
        return array.array("h", bytes(2 * (rate * ms // 1000)))

    for c in cubes:
        units = ctx.units(c)
        if speakers and not any(j["seg"]["speaker"] in speakers or j["conf"]["root"] in speakers for u in units for j in u["jobs"]):
            continue
        if not units or not all(all(j["conf"]["voice_id"] for j in u["jobs"]) and ctx.cached(u) for u in units):
            incomplete.append(c["id"])
            continue
        pcm = silence(au.get("lead_in_ms", 120))
        windows, prev = [], None  # (job, start_ms, end_ms, alignment or None, trim_ms, speed)
        for u in units:
            audio_path, meta_path = ctx.cache_paths(u["key"])
            meta = load_json(meta_path)
            a = decode_segment(ffmpeg, audio_path, meta["format"], rate)
            s0, s1 = trim_silence(a, rate, au.get("trim_db", -50.0))
            a = a[s0:s1]
            filters = []
            speed = u["post_speed"] if abs(u["post_speed"] - 1.0) > 0.005 else 1.0
            if speed != 1.0:
                filters.append(f"atempo={speed:.3f}")
            if au.get("match_segments", True):
                m = loudness(ffmpeg, a.tobytes(), rate, target)
                if m:
                    gain = max(-12.0, min(12.0, target["I"] - float(m["input_i"])))
                    if abs(gain) > 0.3:
                        filters.append(f"volume={gain:.2f}dB")
            if filters:
                out, _ = ff(ffmpeg, ["-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "-", "-af", ",".join(filters),
                                     "-f", "s16le", "-ar", str(rate), "-ac", "1", "-"], a.tobytes())
                a = array.array("h")
                a.frombytes(out[:len(out) // 2 * 2])
            if prev is not None:
                ms = pause.get(u["seg"]["break"], pause.get("paragraph", 550))
                if u["seg"]["speaker"] != prev:
                    ms = max(ms, pause.get("speaker_change", 450))
                pcm.extend(silence(ms))
            base = len(pcm) * 1000 / rate
            dur = len(a) * 1000 / rate
            trim_ms = s0 * 1000 / rate
            pcm.extend(a)
            if u["kind"] == "dialogue":
                inputs = meta.get("inputs_ms") or [None] * len(u["jobs"])
                total_chars = max(1, sum(len(j["text"]) for j in u["jobs"]))
                pos = 0
                for j, w in zip(u["jobs"], inputs):
                    if w:
                        t0, t1 = (w[0] - trim_ms) / speed, (w[1] - trim_ms) / speed
                    else:  # no timing came back: by characters
                        t0, t1 = dur * pos / total_chars, dur * (pos + len(j["text"])) / total_chars
                    pos += len(j["text"])
                    t0 = min(max(0.0, t0), dur)
                    windows.append((j, base + t0, base + min(max(t0, t1), dur), None, 0.0, 1.0))
                prev = u["jobs"][-1]["seg"]["speaker"]
            else:
                al = meta.get("alignment")
                windows.append((u, base, base + dur, al if al and al.get("chars") == len(u["text"]) else None, trim_ms, speed))
                prev = u["seg"]["speaker"]
        pcm.extend(silence(au.get("tail_ms", 350)))
        out_rel = c["audio"]
        out_path = os.path.join(ctx.out, out_rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = os.path.join(tmp, "cube.raw")
            with open(raw_path, "wb") as f:
                f.write(pcm.tobytes())
            m = loudness(ffmpeg, pcm.tobytes(), rate, target)
            af = (f"loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}:measured_I={m['input_i']}:"
                  f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                  f"offset={m['target_offset']}:linear=true") if m else "anull"
            codec = "adpcm_ima_wav" if fmt_name == "ima_adpcm" else "pcm_s16le"
            tmp_out = os.path.join(tmp, "cube.wav")
            ff(ffmpeg, ["-y", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", raw_path, "-af", af,
                        "-ar", str(rate), "-ac", "1", "-c:a", codec, tmp_out])
            shutil.move(tmp_out, out_path)
        duration_ms = round(len(pcm) * 1000 / rate)
        segs = [{"segment": j["seg"]["index"], "speaker": j["seg"]["speaker"], "voice": j["conf"]["root"],
                 "start_ms": round(w0), "end_ms": round(w1), "chars": len(j["text"])} for j, w0, w1, _, _, _ in windows]
        manifest["cubes"][c["id"]] = {"kind": c.get("kind", "cube"), "file": out_rel, "title": c["title"],
                                     "text_hash": c["text_hash"], "duration_ms": duration_ms,
                                     "bytes": os.path.getsize(out_path), "segments": segs,
                                     "lines_ms": line_times(c, piece_times(windows), duration_ms)}
        built += 1
        print(f"  {out_rel}: {duration_ms / 1000:.1f} s, {os.path.getsize(out_path) / 1e6:.2f} MB")
    if built:
        write_manifest(ctx, manifest, fmt_name, rate, target)
    print(f"assembled {built} cubes" + (f"; {len(incomplete)} not complete yet (segments missing): "
                                        + " ".join(incomplete[:30]) + (" ..." if len(incomplete) > 30 else "") if incomplete else ""))
    return built


def piece_times(windows):
    """{(paragraph, start, end): (t0_ms, t1_ms)} of every piece in the cube file: from the
    character timing ElevenLabs returns where it matches the text sent, otherwise spread over the
    segment's time by characters."""
    out = {}
    for j, w0, w1, al, trim_ms, speed in windows:
        n = max(1, len(j["text"]))
        for piece, (a, b) in zip(j["seg"]["pieces"], j["spans"]):
            if b <= a:
                continue
            if al:
                t0 = w0 + max(0.0, (al["start_ms"][a] - trim_ms) / speed)
                t1 = w0 + max(0.0, (al["end_ms"][b - 1] - trim_ms) / speed)
            else:
                t0, t1 = w0 + (w1 - w0) * a / n, w0 + (w1 - w0) * b / n
            t0 = min(max(w0, t0), w1)
            out[(piece["p"], piece["a"], piece["b"])] = (t0, min(max(t0, t1), w1))
    return out


def line_times(cube, times, duration_ms):
    """When each of the reader's lines (src/game_menu.c cube text) starts being spoken."""
    by_para = {}
    for (p, a, b), t in times.items():
        by_para.setdefault(p, []).append((a, b, t))
    for v in by_para.values():
        v.sort()
    raw = []
    for line in cube["lines"]:
        p, o = line["p"], line["o"]
        t = None
        if p is not None and p in by_para:
            for a, b, (t0, t1) in by_para[p]:
                if o < b:
                    t = t0 + (t1 - t0) * max(0, o - a) / max(1, b - a) if o >= a else t0
                    break
            if t is None:
                t = by_para[p][-1][2][1]
        raw.append(t)
    out, nxt = [None] * len(raw), duration_ms
    for i in range(len(raw) - 1, -1, -1):  # a blank line: the next line's time
        if raw[i] is not None:
            nxt = raw[i]
        out[i] = nxt
    last = 0
    for i, t in enumerate(out):  # never going back
        last = max(last, t)
        out[i] = round(last)
    return out


def write_manifest(ctx, manifest, fmt_name, rate, target):
    manifest.update({"version": 1, "generated": datetime.datetime.now().isoformat(timespec="seconds"),
                     "format": fmt_name, "sample_rate": rate, "loudness_lufs": target["I"],
                     "note": "Made by tools/voices/generate.py. lines_ms: when each line of the reader's text starts."})
    for cid in list(manifest["cubes"]):
        if not os.path.exists(os.path.join(ctx.out, manifest["cubes"][cid]["file"])):
            del manifest["cubes"][cid]
    manifest["cubes"] = dict(sorted(manifest["cubes"].items(), key=lambda kv: tuple(int(x) for x in kv[0].split(":"))))
    save_json(os.path.join(ctx.out, "manifest.json"), manifest)
    # The game's list (src/voiceover.c): a voice plays only over the text whose hash it carries.
    lines = ["# Tyrian3D voices (tools/voices/generate.py), read by src/voiceover.c. One voice a line:",
             "# cube <episode> <cube> <text hash> <duration_ms> <file> <line_count> <start_ms of each reader line...>",
             "# story <text hash> <duration_ms> <file>   (a story text between levels, found by its text)",
             f"# format {fmt_name}, {rate} Hz mono, {target['I']} LUFS"]
    for cid, e in manifest["cubes"].items():
        ep, n = cid.split(":")
        if e.get("kind") == "story":
            lines.append(f"story {e['text_hash']} {e['duration_ms']} {e['file']}")
        else:
            lines.append(f"cube {ep} {n} {e['text_hash']} {e['duration_ms']} {e['file']} {len(e['lines_ms'])} "
                         + " ".join(str(t) for t in e["lines_ms"]))
    with open(os.path.join(ctx.out, "manifest.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def cmd_build(ctx):
    only = parse_only(ctx.args.only)
    built = build(ctx, only, set(ctx.args.speaker) if ctx.args.speaker else None, ctx.args.referenced_only)
    return 0 if built or not only else 1


# --- voice design -----------------------------------------------------------------------------

def sample_text(ctx, key):
    """Preview text for a speaker's voice: its own lines, 100-1000 characters (the API's limits)."""
    segs = []
    for c in ctx.cubes():
        for s in c["segments"]:
            if s["speaker"] == key:
                segs.append(s)
    segs.sort(key=lambda s: -len(s["tts"]))
    text = ""
    for s in segs:
        for sentence in re.split(r"(?<=[.!?])\s+", strip_tags(apply_aliases(s["tts"], ctx.rules or []))):
            if len(text) >= 260:
                break
            text = (text + " " + sentence).strip()
        if len(text) >= 260:
            break
    text = re.sub(r"\s+", " ", text)[:950]
    return text if len(text) >= 100 else None


def cmd_design(ctx):
    args = ctx.args
    keys = args.speaker or [k for k, s in ctx.cast["speakers"].items()
                            if not s.get("voice_of") and not s.get("voice_id") and s.get("usage", {}).get("characters")]
    if not keys:
        print("every voice has a voice_id; give --speaker K to design one again")
        return 0
    total = 0
    for key in keys:
        spk = ctx.cast["speakers"].get(key)
        if spk is None:
            raise Fatal(f"no speaker {key!r}")
        if spk.get("voice_of"):
            print(f"{key} uses {spk['voice_of']}'s voice (voice_of); design that one, or remove voice_of first")
            continue
        prompt = spk.get("voice_prompt")
        if not prompt:
            print(f"{key}: no voice_prompt in cast.json")
            continue
        text = args.text or sample_text(ctx, key)
        body = {"voice_description": prompt, "model_id": ctx.cast["defaults"].get("design_model_id", "eleven_ttv_v3")}
        if text:
            body["text"] = text
        else:
            body["auto_generate_text"] = True
        for opt, name in (("guidance", "guidance_scale"), ("loudness", "loudness"), ("seed", "seed")):
            if getattr(args, opt) is not None:
                body[name] = getattr(args, opt)
        if args.enhance:
            body["should_enhance"] = True
        folder = os.path.join(VOICES, "previews", key)
        log_path = os.path.join(folder, "previews.json")
        log = load_json(log_path, {"speaker": key, "rounds": []})
        rnd = len(log["rounds"]) + 1
        print(f"{key}: designing (round {rnd}, {len(text or '')} characters of preview text)...")
        _, raw = call("POST", "/v1/text-to-voice/design", body, {"output_format": "mp3_44100_128"})
        data = json.loads(raw)
        entry = {"round": rnd, "created": datetime.datetime.now().isoformat(timespec="seconds"),
                 "prompt": prompt, "text": data.get("text", text), "previews": []}
        for n, p in enumerate(data.get("previews", []), 1):
            ext = ".mp3" if "mpeg" in p.get("media_type", "audio/mpeg") else ".audio"
            name = f"{rnd}-{n}{ext}"
            write_bytes(os.path.join(folder, name), base64.b64decode(p["audio_base_64"]))
            entry["previews"].append({"n": n, "file": name, "generated_voice_id": p["generated_voice_id"],
                                      "duration_secs": p.get("duration_secs")})
        log["rounds"].append(entry)
        save_json(log_path, log)
        total += len(text or "")
        print(f"  {len(entry['previews'])} previews in {os.path.relpath(folder, ROOT)}/{rnd}-*.mp3; "
              f"keep one with: tools/voices/generate.py adopt {key} {rnd}-<n>")
    print(f"voice design: {total:,} characters of preview text charged")
    page = write_previews_page()
    if page:
        print(f"listen: open {os.path.relpath(page, ROOT)}")
    return 0


def write_previews_page():
    """data/voices/previews/index.html: every speaker's previews to listen to side by side, the
    prompt and text they read, which one is adopted, and the command that adopts each."""
    import html
    root = os.path.join(VOICES, "previews")
    if not os.path.isdir(root):
        return None
    cast = load_json(CAST_PATH)
    parts = ["<!doctype html><meta charset=utf-8><title>Tyrian3D voice previews</title><style>"
             "body{font:15px system-ui;background:#1b1712;color:#e8dcc6;max-width:980px;margin:24px auto;padding:0 16px}"
             "h2{color:#e2b866;margin:28px 0 4px}.role,.prompt,.text{color:#b5a68c;font-size:13px;margin:4px 0}"
             ".text{font-style:italic}.row{display:flex;gap:12px;align-items:center;margin:6px 0}"
             "code{background:#2c251c;padding:2px 6px;border-radius:4px;user-select:all}.on{color:#9fdc8f}"
             "audio{height:32px}</style><h1>Tyrian3D voice previews</h1>"
             "<p>Listen, then keep one per voice: <code>python3 tools/voices/generate.py adopt &lt;speaker&gt; &lt;round&gt;-&lt;n&gt;</code></p>"]
    for key in sorted(os.listdir(root)):
        log_path = os.path.join(root, key, "previews.json")
        if not os.path.exists(log_path):
            continue
        log = load_json(log_path)
        spk = cast["speakers"].get(key, {})
        adopted = spk.get("adopted_preview")
        parts.append(f"<h2>{html.escape(spk.get('name', key))} <small>({html.escape(key)})</small></h2>"
                     f"<div class=role>{html.escape(spk.get('description', ''))}</div>")
        for r in log["rounds"]:
            parts.append(f"<div class=prompt>Round {r['round']}: {html.escape(r['prompt'])}</div>"
                         f"<div class=text>“{html.escape(r.get('text') or '')}”</div>")
            for pv in r["previews"]:
                tag = f"{r['round']}-{pv['n']}"
                mark = " <b class=on>adopted</b>" if adopted == tag else ""
                parts.append(f"<div class=row><b>{tag}</b><audio controls preload=none src='{key}/{pv['file']}'></audio>"
                             f"<code>python3 tools/voices/generate.py adopt {key} {tag}</code>{mark}</div>")
    path = os.path.join(root, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    return path


def cmd_adopt(ctx):
    args = ctx.args
    key = args.key
    spk = ctx.cast["speakers"].get(key)
    if spk is None:
        raise Fatal(f"no speaker {key!r} in cast.json")
    if args.voice_id:
        voice_id = args.voice_id.strip()
    else:
        if not args.preview:
            raise Fatal("give the preview (adopt K 2-1) or --voice-id ID")
        log = load_json(os.path.join(VOICES, "previews", key, "previews.json"))
        rnd, n = (args.preview.split("-") + [None])[:2] if "-" in args.preview else (len(log["rounds"]), args.preview)
        entry = next((r for r in log["rounds"] if r["round"] == int(rnd)), None)
        p = entry and next((p for p in entry["previews"] if p["n"] == int(n)), None)
        if not p:
            raise Fatal(f"no preview {args.preview} for {key}")
        body = {"voice_name": f"Tyrian3D - {spk.get('name', key)}"[:100],
                "voice_description": (spk.get("voice_prompt") or spk.get("description") or key)[:1000],
                "generated_voice_id": p["generated_voice_id"],
                "labels": {"project": "tyrian3d", "speaker": key}}
        _, raw = call("POST", "/v1/text-to-voice", body)
        voice_id = json.loads(raw)["voice_id"]
    cast = load_json(CAST_PATH)
    cast["speakers"][key]["voice_id"] = voice_id
    if not args.voice_id:
        cast["speakers"][key]["adopted_preview"] = f"{int(rnd)}-{int(n)}"
    save_json(CAST_PATH, cast)
    write_previews_page()
    print(f"{key}: voice_id {voice_id} written into tools/voices/cast.json")
    return 0


def cmd_try(ctx):
    args = ctx.args
    key = args.speaker[0] if args.speaker else None
    if not key:
        raise Fatal("give --speaker K")
    seg = {"index": 0, "speaker": key, "break": "paragraph",
           "pieces": [{"p": 0, "a": 0, "b": len(args.text), "text": args.text, "tts": args.text, "sep": ""}]}
    cube = {"id": "try:" + hashlib.sha256(args.text.encode()).hexdigest()[:8]}
    j = ctx.job(cube, seg)
    j = dict(j, kind="tts", jobs=[j])
    if not j["conf"]["voice_id"]:
        raise Fatal(f"{key} has no voice yet")
    print(f"sending {len(j['text'])} characters: {j['text']}")
    if not ctx.cached(j):
        render(ctx, j)
    audio_path, meta_path = ctx.cache_paths(j["key"])
    rate = int(j["format"].split("_")[1]) if j["format"].startswith(("pcm_", "wav_")) else 24000
    a = decode_segment(ffmpeg_path(args), audio_path, j["format"], rate)
    out = os.path.join(VOICES, "try", f"{key}-{j['key'][:8]}.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(a.tobytes())
    print(f"wrote {os.path.relpath(out, ROOT)}")
    return 0


def cmd_dictionary(ctx):
    rules = []
    for t in ctx.pron["terms"]:
        if t.get("ipa") and " " not in t["term"]:
            rules.append({"type": "phoneme", "string_to_replace": t["term"], "phoneme": t["ipa"], "alphabet": "ipa"})
        elif t.get("say"):
            rules.append({"type": "alias", "string_to_replace": t["term"], "alias": t["say"]})
    body = {"name": "Tyrian3D data cubes", "rules": rules,
            "description": "Proper nouns of Tyrian (tools/voices/pronunciation.json)"}
    _, raw = call("POST", "/v1/pronunciation-dictionaries/add-from-rules", body)
    d = json.loads(raw)
    ctx.state["dictionary"] = {"id": d["id"], "version_id": d["version_id"], "rules": len(rules),
                               "created": datetime.datetime.now().isoformat(timespec="seconds")}
    save_json(ctx.state_path, ctx.state)
    print(f"pronunciation dictionary {d['id']} (version {d['version_id']}, {len(rules)} rules) saved in "
          f"data/voices/state.json; set cast.json defaults.pronunciation to \"dictionary\" to use it "
          f"(phoneme rules: eleven_v3, eleven_v4 and eleven_flash_v2 only)")
    return 0


def cmd_status(ctx):
    _, raw = call("GET", "/v1/user/subscription", attempts=3)
    sub = json.loads(raw)
    reset = sub.get("next_character_count_reset_unix")
    reset = datetime.datetime.fromtimestamp(reset).strftime("%Y-%m-%d") if reset else "?"
    print(f"plan {sub.get('tier')} ({sub.get('status')}): {sub.get('character_count', 0):,} of "
          f"{sub.get('character_limit', 0):,} credits used, resets {reset}; voice slots "
          f"{sub.get('voice_slots_used', '?')} of {sub.get('voice_limit', '?')}; usage-based billing "
          f"{'on' if sub.get('can_extend_character_limit') else 'off'}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__[__doc__.index("  estimate"):__doc__.index("ElevenLabs documentation")])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("estimate", help="characters, minutes, sizes and the plan (no network)")
    p = sub.add_parser("design", help="voice previews for the speakers without a voice")
    p.add_argument("--speaker", action="append")
    p.add_argument("--text", help="preview text instead of the speaker's own lines (100-1000 characters)")
    p.add_argument("--guidance", type=float, help="guidance_scale: higher follows the prompt more closely")
    p.add_argument("--loudness", type=float, help="-1 (quiet) to 1 (loud); 0 is about -24 LUFS")
    p.add_argument("--seed", type=int)
    p.add_argument("--enhance", action="store_true", help="let ElevenLabs expand the prompt")
    p = sub.add_parser("adopt", help="make a preview (or any voice) a speaker's voice")
    p.add_argument("key")
    p.add_argument("preview", nargs="?", help="N or ROUND-N, as in previews/<speaker>/ROUND-N.mp3")
    p.add_argument("--voice-id", help="use this voice instead (a Voice Library or own voice)")
    for name in ("generate", "build"):
        p = sub.add_parser(name, help="render and assemble" if name == "generate" else "assemble from the cache only")
        p.add_argument("--only", action="append", help="E, E:N or E:N:S (several: comma or repeat)")
        p.add_argument("--speaker", action="append", help="only this speaker's segments (or a voice's)")
        p.add_argument("--referenced-only", action="store_true", help="skip the cubes no episode script lists")
        p.add_argument("--format", choices=("ima_adpcm", "pcm16"), help="the cube files' encoding (default: cast.json)")
        p.add_argument("--out-dir", help="where e<E>/<N>.wav and the manifest go (default data/voices)")
        p.add_argument("--ffmpeg")
        p.add_argument("--model", help="render with another model this time (e.g. eleven_v4 for a comparison)")
        if name == "generate":
            p.add_argument("--jobs", type=int, default=2, help="parallel requests (plans allow 2-15)")
            p.add_argument("--max-chars", type=int, help="stop after about this many characters")
            p.add_argument("--retake", action="append", help="E:N or E:N:S: render again with a new seed")
            p.add_argument("--dry-run", action="store_true", help="list what would be rendered (no network)")
            p.add_argument("--no-build", action="store_true", help="render only")
            p.add_argument("--force", action="store_true", help="go on even if the credits look short")
    p = sub.add_parser("try", help="render one line with a speaker's voice")
    p.add_argument("--speaker", action="append", required=True)
    p.add_argument("text")
    p.add_argument("--ffmpeg")
    p.add_argument("--model")
    sub.add_parser("dictionary", help="upload pronunciation.json as a pronunciation dictionary")
    sub.add_parser("status", help="credits and voice slots of the account")
    args = ap.parse_args()
    try:
        ctx = Context(args, need_script=args.cmd not in ("status", "dictionary", "adopt"))
        return {"estimate": cmd_estimate, "design": cmd_design, "adopt": cmd_adopt, "generate": cmd_generate,
                "build": cmd_build, "try": cmd_try, "dictionary": cmd_dictionary, "status": cmd_status}[args.cmd](ctx)
    except Fatal as e:
        print(f"stopped: {e}", file=sys.stderr)
        return 2
    except Failed as e:
        print(f"failed: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted; what was rendered is in the cache", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
