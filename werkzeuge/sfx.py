"""Retro-UI-Soundeffekte per Synthese (44,1 kHz, 16 Bit, mono).

Aufruf: python sfx.py <zielordner>
"""
from __future__ import annotations

import os
import sys
import wave

import numpy as np

SR = 44100


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, total=None):
    total = total or n / SR
    t = np.arange(n) / SR
    e = np.zeros(n)
    a_n = max(1, int(a * SR))
    e[:a_n] = np.linspace(0, 1, a_n)
    rest = t[a_n:] - a
    e[a_n:] = np.exp(-rest / max(d, 1e-4)) * (1 - s) + s
    r_n = min(n, int(r * SR))
    if r_n > 0:
        e[-r_n:] *= np.linspace(1, 0, r_n)
    return e


def tone(freq, dur, wave_='square', duty=0.5, vib=0.0, slide=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + slide * t / dur) * (1 + vib * np.sin(2 * np.pi * 6 * t))
    ph = np.cumsum(f) / SR
    if wave_ == 'square':
        return np.where((ph % 1) < duty, 1.0, -1.0)
    if wave_ == 'tri':
        return 2 * np.abs(2 * (ph % 1) - 1) - 1
    if wave_ == 'saw':
        return 2 * (ph % 1) - 1
    return np.sin(2 * np.pi * ph)


def noise(dur, seed=0):
    r = np.random.default_rng(seed)
    return r.uniform(-1, 1, int(dur * SR))


def lowpass(x, k=0.2):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


def mixdown(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def delay(x, ms=90, fb=0.3, taps=3):
    d = int(ms / 1000 * SR)
    out = np.concatenate([x, np.zeros(d * taps)])
    for k in range(1, taps + 1):
        out[d * k:d * k + len(x)] += x * (fb ** k)
    return out


def save(path, x, vol=0.5):
    x = x / (np.max(np.abs(x)) + 1e-9) * vol
    data = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def build(out):
    os.makedirs(out, exist_ok=True)
    # Hover: ganz leises, kurzes Ticken
    x = tone(1800, 0.03, 'square', 0.25) * env(int(0.03 * SR), 0.001, 0.012)
    save(f'{out}/ui_hover.wav', lowpass(x, 0.35), 0.18)
    # Klick: zwei schnelle Toene
    x = mixdown(tone(880, 0.05, 'square', 0.5) * env(int(0.05 * SR), 0.001, 0.02),
                np.concatenate([np.zeros(int(0.025 * SR)), tone(1320, 0.05, 'square', 0.5) * env(int(0.05 * SR), 0.001, 0.02)]))
    save(f'{out}/ui_click.wav', lowpass(x, 0.3), 0.32)
    # Zurueck / Abbrechen: absteigend
    x = mixdown(tone(990, 0.06, 'square', 0.5) * env(int(0.06 * SR), 0.001, 0.025),
                np.concatenate([np.zeros(int(0.035 * SR)), tone(660, 0.07, 'square', 0.5) * env(int(0.07 * SR), 0.001, 0.03)]))
    save(f'{out}/ui_back.wav', lowpass(x, 0.3), 0.3)
    # Auswahl in Liste: weicher Glockenton
    x = tone(1046, 0.18, 'sine') * env(int(0.18 * SR), 0.002, 0.07) + 0.4 * tone(2093, 0.18, 'sine') * env(int(0.18 * SR), 0.002, 0.04)
    save(f'{out}/ui_select.wav', x, 0.35)
    # Umschalten (Toggle / Pfeile)
    x = tone(660, 0.04, 'tri') * env(int(0.04 * SR), 0.001, 0.018)
    save(f'{out}/ui_toggle.wav', x, 0.3)
    # Fehler: tiefes Brummen
    x = mixdown(tone(140, 0.22, 'square', 0.4, slide=-0.2) * env(int(0.22 * SR), 0.002, 0.12),
                tone(147, 0.22, 'square', 0.4, slide=-0.2) * env(int(0.22 * SR), 0.002, 0.12))
    save(f'{out}/ui_error.wav', lowpass(x, 0.2), 0.3)
    # Fenster oeffnen / schliessen: Wusch
    x = noise(0.18, 1) * env(int(0.18 * SR), 0.03, 0.07)
    save(f'{out}/ui_open.wav', lowpass(x, 0.08), 0.22)
    x = noise(0.14, 2) * env(int(0.14 * SR), 0.01, 0.05)
    save(f'{out}/ui_close.wav', lowpass(x, 0.05), 0.2)
    # Tippen im Namensfeld
    x = noise(0.02, 3) * env(int(0.02 * SR), 0.0005, 0.006)
    save(f'{out}/ui_type.wav', lowpass(x, 0.5), 0.15)
    # Wuerfel: mehrere Klacker
    parts = []
    for i, off in enumerate([0, 0.05, 0.11, 0.16, 0.24]):
        k = noise(0.03, 10 + i) * env(int(0.03 * SR), 0.0005, 0.01)
        parts.append(np.concatenate([np.zeros(int(off * SR)), lowpass(k, 0.4 - i * 0.05)]))
    save(f'{out}/ui_dice.wav', mixdown(*parts), 0.35)
    # Charakter erstellt: heller magischer Akkord (Arpeggio + Schimmer)
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5]
    parts = []
    for i, f in enumerate(notes):
        seg = (tone(f, 0.9, 'sine') + 0.3 * tone(f * 2, 0.9, 'tri')) * env(int(0.9 * SR), 0.004, 0.35)
        parts.append(np.concatenate([np.zeros(int(i * 0.07 * SR)), seg]))
    shimmer = noise(1.0, 5) * env(int(1.0 * SR), 0.2, 0.4) * 0.15
    save(f'{out}/char_created.wav', delay(mixdown(*parts, lowpass(shimmer, 0.6)), 110, 0.3), 0.45)
    # Charakter geloescht: dunkler Abstieg
    x = mixdown(tone(220, 0.6, 'saw', slide=-0.5) * env(int(0.6 * SR), 0.005, 0.3),
                tone(110, 0.6, 'square', 0.3, slide=-0.4) * env(int(0.6 * SR), 0.005, 0.3) * 0.6)
    save(f'{out}/char_deleted.wav', lowpass(x, 0.12), 0.4)
    # Welt betreten: aufsteigender heiliger Klang
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    swell = np.minimum(1, t / 0.8) * np.exp(-np.maximum(0, t - 0.9) / 0.35)
    chord = sum(tone(f, 1.6, 'sine', vib=0.004) for f in (392.0, 493.88, 587.33, 783.99)) * swell
    rise = lowpass(noise(1.6, 7), 0.05) * swell * 0.8
    save(f'{out}/enter_world.wav', delay(chord + rise, 140, 0.25), 0.5)
    # Titel: beliebige Taste - Glockenschlag
    x = sum(tone(f, 1.2, 'sine') * env(int(1.2 * SR), 0.002, d) for f, d in ((523.25, 0.5), (1046.5, 0.3), (1567.98, 0.2)))
    save(f'{out}/title_start.wav', delay(x, 160, 0.3), 0.45)
    # Hardcore-Warnung: tiefer Schlag + Glocke
    x = mixdown(lowpass(noise(0.5, 9), 0.05) * env(int(0.5 * SR), 0.002, 0.15) * 2,
                tone(98, 0.8, 'sine') * env(int(0.8 * SR), 0.002, 0.4),
                tone(466.16, 0.8, 'sine') * env(int(0.8 * SR), 0.002, 0.3) * 0.4)
    save(f'{out}/hardcore.wav', x, 0.45)


if __name__ == '__main__':
    build(sys.argv[1])
