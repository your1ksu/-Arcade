"""
particles.py — Chromatic Heroes
Система частиц. Arcade 3.x: on_update вместо update.
"""

from __future__ import annotations

import math
import random

import arcade

from constants import (
    CP_SOAP, CP_FLAME, CP_INK, CP_POLLEN,
    CP_SPARK, CP_DUST, CP_RAINBOW,
)


class Particle(arcade.SpriteSolidColor):
    """Частица, которая движется и угасает."""

    def __init__(
        self, x: float, y: float, color: tuple,
        vx: float, vy: float, lifetime: float,
        size: int = 5, grav: float = 0.0,
    ) -> None:
        super().__init__(size, size, color)
        self.center_x, self.center_y = x, y
        self._vx, self._vy = vx, vy
        self._lt = lifetime
        self._age = 0.0
        self._grav = grav

    def on_update(self, dt: float = 1 / 60) -> None:
        self._age += dt
        self._vy -= self._grav * dt
        self.center_x += self._vx * dt
        self.center_y += self._vy * dt
        self.alpha = max(0, int(255 * (1.0 - self._age / self._lt)))
        if self._age >= self._lt:
            self.remove_from_sprite_lists()


class ParticleSystem:
    """Менеджер частиц. update() → on_update(), draw() → draw()."""

    def __init__(self) -> None:
        self._p: arcade.SpriteList = arcade.SpriteList()

    def update(self, dt: float) -> None:
        self._p.update(dt)

    def draw(self) -> None:
        self._p.draw()

    def clear(self) -> None:
        self._p.clear()

    def _burst(
        self, x: float, y: float, color: tuple,
        n: int = 8, spd0: float = 40, spd1: float = 120,
        lt0: float = 0.4, lt1: float = 0.9,
        sz: int = 5, grav: float = 80.0,
    ) -> None:
        for _ in range(n):
            a = random.uniform(0, 2 * math.pi)
            spd = random.uniform(spd0, spd1)
            lt = random.uniform(lt0, lt1)
            s = random.randint(max(2, sz - 2), sz + 2)
            self._p.append(
                Particle(x, y, color,
                         math.cos(a) * spd, math.sin(a) * spd,
                         lt, s, grav)
            )

    def emit_soap(self, x: float, y: float) -> None:
        self._burst(x, y, CP_SOAP, n=12, spd0=60, spd1=150,
                    lt0=0.3, lt1=0.7, sz=6, grav=20.0)

    def emit_flame(self, x: float, y: float) -> None:
        for _ in range(6):
            self._p.append(Particle(
                x, y, CP_FLAME,
                random.uniform(-25, 25), random.uniform(60, 140),
                random.uniform(0.3, 0.6), random.randint(3, 7), grav=-30.0,
            ))

    def emit_ink(self, x: float, y: float) -> None:
        self._burst(x, y, CP_INK, n=10, spd0=50, spd1=130,
                    lt0=0.4, lt1=0.8, sz=7, grav=60.0)

    def emit_pollen(self, x: float, y: float) -> None:
        for _ in range(8):
            self._p.append(Particle(
                x, y, CP_POLLEN,
                random.uniform(-40, 40), random.uniform(20, 80),
                random.uniform(0.5, 1.0), random.randint(3, 5), grav=10.0,
            ))

    def emit_spark(self, x: float, y: float) -> None:
        self._burst(x, y, CP_SPARK, n=14, spd0=80, spd1=200,
                    lt0=0.2, lt1=0.5, sz=4, grav=100.0)

    def emit_dust(self, x: float, y: float) -> None:
        for _ in range(10):
            self._p.append(Particle(
                x, y, CP_DUST,
                random.uniform(-150, -30), random.uniform(-60, 60),
                random.uniform(0.3, 0.7), random.randint(3, 6), grav=50.0,
            ))

    def emit_rainbow(self, x: float, y: float) -> None:
        for i, color in enumerate(CP_RAINBOW):
            a = math.pi * (0.3 + 0.08 * i)
            spd = random.uniform(60, 130)
            self._p.append(Particle(
                x, y, color,
                math.cos(a) * spd, math.sin(a) * spd,
                random.uniform(0.5, 1.0), 6, grav=30.0,
            ))

    def emit_wind(self, x: float, y: float) -> None:
        for _ in range(6):
            self._p.append(Particle(
                x, y, (180, 180, 200),
                random.uniform(-200, -80), random.uniform(-20, 20),
                random.uniform(0.3, 0.6), 4, grav=0.0,
            ))
