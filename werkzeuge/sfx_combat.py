"""Kampf-Soundeffekte per Synthese (gleicher Stil wie sfx.py: 44,1 kHz, 16 Bit, mono).

Aufruf: python sfx_combat.py <zielordner>
"""
from __future__ import annotations

import os
import sys

import numpy as np

from sfx import SR, delay, env, lowpass, mixdown, noise, save, tone


def _at(x, sec):
    return np.concatenate([np.zeros(int(sec * SR)), x])


def _chime(freqs, dur, spacing, decay, wave_='sine', vib=0.0):
    parts = []
    for i, f in enumerate(freqs):
        seg = tone(f, dur, wave_, vib=vib) * env(int(dur * SR), 0.003, decay)
        parts.append(_at(seg, i * spacing))
    return mixdown(*parts)


def build(out):
    os.makedirs(out, exist_ok=True)
    # Zauber beginnt: leises, aufsteigendes Lichtsummen
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    swell = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.25) / 0.12)
    x = (tone(660, 0.45, 'sine', slide=0.35, vib=0.01) + 0.5 * tone(990, 0.45, 'sine', slide=0.35)) * swell
    save(f'{out}/cast_holy.wav', x + lowpass(noise(0.45, 21), 0.08) * swell * 0.4, 0.28)
    # Heilung trifft: warmer Glockenakkord mit Schimmer
    x = _chime([783.99, 987.77, 1174.66, 1567.98], 0.7, 0.035, 0.22)
    shimmer = lowpass(noise(0.6, 22), 0.5) * env(int(0.6 * SR), 0.05, 0.18) * 0.12
    save(f'{out}/heal_land.wav', delay(mixdown(x, shimmer), 90, 0.25, 2), 0.36)
    # Erneuerung (HoT): sanftes Perlen
    x = _chime([1046.5, 1318.5, 1568.0, 2093.0], 0.35, 0.05, 0.1, 'tri')
    save(f'{out}/hot_apply.wav', delay(x, 70, 0.3, 2), 0.25)
    # Heilige Pein: heller Lichtschlag
    crack = lowpass(noise(0.25, 23), 0.35) * env(int(0.25 * SR), 0.001, 0.05)
    bell = _chime([523.25, 1046.5, 1568.0], 0.5, 0.0, 0.15, 'tri')
    save(f'{out}/smite_hit.wav', delay(mixdown(crack * 1.2, bell * 0.8), 60, 0.25, 2), 0.42)
    # Schatten: dunkles Wabern
    x = mixdown(tone(110, 0.5, 'saw', slide=-0.3, vib=0.04) * env(int(0.5 * SR), 0.01, 0.2),
                lowpass(noise(0.5, 24), 0.06) * env(int(0.5 * SR), 0.02, 0.2) * 1.5,
                tone(220, 0.5, 'sine', slide=-0.4) * env(int(0.5 * SR), 0.01, 0.15) * 0.5)
    save(f'{out}/shadow_hit.wav', lowpass(x, 0.15), 0.36)
    # Physischer Treffer: dumpfer Schlag
    x = mixdown(lowpass(noise(0.12, 25), 0.18) * env(int(0.12 * SR), 0.0005, 0.03) * 1.6,
                tone(95, 0.12, 'sine', slide=-0.5) * env(int(0.12 * SR), 0.0005, 0.05))
    save(f'{out}/hit_physical.wav', x, 0.34)
    # Schwerer Treffer (Krit / Tank-Buster)
    x = mixdown(lowpass(noise(0.3, 26), 0.22) * env(int(0.3 * SR), 0.0005, 0.07) * 1.8,
                tone(70, 0.3, 'sine', slide=-0.5) * env(int(0.3 * SR), 0.0005, 0.12) * 1.3,
                tone(140, 0.2, 'square', 0.3, slide=-0.6) * env(int(0.2 * SR), 0.0005, 0.05) * 0.4)
    save(f'{out}/hit_heavy.wav', x, 0.46)
    # Magischer Treffer (Funken, Wachs): Zischen
    x = mixdown(lowpass(noise(0.28, 27), 0.55) * env(int(0.28 * SR), 0.002, 0.08),
                tone(880, 0.2, 'square', 0.3, slide=-0.6) * env(int(0.2 * SR), 0.001, 0.05) * 0.3)
    save(f'{out}/hit_magic.wav', x, 0.3)
    # Schwung (Nahkampf-Ausholen)
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    w = noise(0.16, 28) * np.sin(np.pi * t / 0.16) ** 2
    save(f'{out}/swing.wav', lowpass(w, 0.12), 0.2)
    # Gegner stirbt: abfallender Ton
    x = mixdown(tone(330, 0.45, 'square', 0.4, slide=-0.6) * env(int(0.45 * SR), 0.002, 0.2),
                lowpass(noise(0.3, 29), 0.1) * env(int(0.3 * SR), 0.001, 0.08))
    save(f'{out}/death_enemy.wav', lowpass(x, 0.25), 0.3)
    # Gruppenmitglied stirbt: dunkler Moll-Abstieg
    x = _chime([392.0, 311.13, 261.63, 196.0], 0.9, 0.14, 0.35, 'tri')
    save(f'{out}/death_party.wav', delay(lowpass(x, 0.3), 150, 0.3, 2), 0.42)
    # Level-Up: Fanfare nach oben
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5, 1567.98]
    parts = [_at((tone(f, 0.9, 'square', 0.35) * 0.35 + tone(f, 0.9, 'sine')) * env(int(0.9 * SR), 0.004, 0.3), i * 0.075)
             for i, f in enumerate(notes)]
    shimmer = lowpass(noise(1.3, 30), 0.6) * env(int(1.3 * SR), 0.3, 0.45) * 0.15
    save(f'{out}/level_up.wav', delay(mixdown(*parts, shimmer), 120, 0.3), 0.46)
    # Quest abgeschlossen: kurzer Jubelakkord
    x = mixdown(_chime([523.25, 659.25, 783.99], 0.3, 0.09, 0.1, 'square'),
                _at(_chime([1046.5, 1318.5, 1567.98], 0.9, 0.0, 0.35, 'sine'), 0.3))
    save(f'{out}/quest_done.wav', delay(lowpass(x, 0.4), 110, 0.25), 0.42)
    # Welle beginnt: Horn
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    sw = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.5) / 0.15)
    x = (tone(196, 0.9, 'saw', vib=0.006) + tone(293.66, 0.9, 'saw', vib=0.006) * 0.7) * sw
    save(f'{out}/wave_start.wav', delay(lowpass(x, 0.08), 160, 0.25, 2), 0.4)
    # Sieg: froher Dreiklang
    x = mixdown(_chime([392.0, 493.88, 587.33], 0.25, 0.1, 0.08, 'square'),
                _at(_chime([783.99, 987.77, 1174.66], 1.0, 0.0, 0.4, 'tri'), 0.32))
    save(f'{out}/victory.wav', delay(lowpass(x, 0.35), 120, 0.3), 0.42)
    # Niederlage: langsamer Abstieg
    x = _chime([293.66, 261.63, 233.08, 196.0], 1.0, 0.28, 0.45, 'saw')
    save(f'{out}/defeat.wav', delay(lowpass(x, 0.1), 180, 0.3), 0.42)
    # Warnung Tank-Buster: tiefer Doppelschlag
    x = mixdown(tone(110, 0.25, 'square', 0.5) * env(int(0.25 * SR), 0.002, 0.1),
                _at(tone(110, 0.3, 'square', 0.5) * env(int(0.3 * SR), 0.002, 0.14), 0.2),
                _at(tone(220, 0.3, 'saw') * env(int(0.3 * SR), 0.002, 0.12) * 0.4, 0.2))
    save(f'{out}/warn_buster.wav', lowpass(x, 0.18), 0.42)
    # Warnung Flaechenschaden: aufsteigendes Brodeln
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    sw = np.minimum(1, t / 0.5) * np.exp(-np.maximum(0, t - 0.55) / 0.08)
    x = (tone(180, 0.7, 'saw', slide=0.8, vib=0.05) + lowpass(noise(0.7, 31), 0.12) * 1.2) * sw
    save(f'{out}/warn_aoe.wav', lowpass(x, 0.2), 0.36)
    # Gegner beginnt zu zaubern
    x = tone(440, 0.3, 'tri', slide=0.5, vib=0.03) * env(int(0.3 * SR), 0.02, 0.1)
    save(f'{out}/cast_enemy.wav', x, 0.22)
    # Spott: kurzer Ruf
    x = mixdown(tone(160, 0.3, 'saw', slide=0.3, vib=0.08) * env(int(0.3 * SR), 0.01, 0.12),
                tone(240, 0.3, 'square', 0.3, slide=0.3) * env(int(0.3 * SR), 0.01, 0.1) * 0.4)
    save(f'{out}/taunt.wav', lowpass(x, 0.15), 0.34)
    # Donnerknall: Grollen
    x = mixdown(lowpass(noise(0.7, 32), 0.05) * env(int(0.7 * SR), 0.002, 0.25) * 2.2,
                tone(55, 0.7, 'sine', slide=-0.3) * env(int(0.7 * SR), 0.002, 0.3) * 1.5)
    save(f'{out}/thunder_clap.wav', x, 0.5)
    # Schildwall: metallisches Klingen
    x = mixdown(_chime([1244.5, 1661.2, 2217.5], 0.6, 0.0, 0.2, 'tri'), lowpass(noise(0.1, 33), 0.4) * env(int(0.1 * SR), 0.0005, 0.02))
    save(f'{out}/shield_wall.wav', delay(x, 80, 0.3, 2), 0.34)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'healer-simulator', 'assets', 'sfx'))
