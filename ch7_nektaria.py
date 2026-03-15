"""
ch7_nektaria.py — Глава 7: Нектария — Пчела-разведчица
Вид сверху, сбор нектара на время. Arcade 3.x.
"""

from __future__ import annotations

import math
import random

import arcade

from base_chapter import BaseChapter
from constants import (
    SCREEN_W, SCREEN_H, TS,
    SPEED_TD, MAX_NECTAR_N, WORLD,
    C_NEKTAR, C_HIVE,
)
from sprites import Flower
from utils import draw_bar

_FBG = [(35, 65, 30), (70, 60, 15), (40, 30, 55)]
_FCOL = [(220, 180, 240), (240, 200, 40), (180, 120, 240)]
_FCOUNT = [20, 28, 36]
_TIME = [90.0, 80.0, 70.0]


class Chapter7View(BaseChapter):

    def __init__(self, chapter_num: int = 7) -> None:
        super().__init__(chapter_num)
        self.player = None
        self.walls = arcade.SpriteList()
        self.flowers = arcade.SpriteList()
        self._nectar = 0
        self._honey = 0
        self._hx = WORLD / 2
        self._hy = WORLD - 120.0
        self._time = 0.0

    def setup(self) -> None:
        self._nectar = 0
        self._honey = 0
        self.ps.clear()
        self.flowers.clear()
        self.walls.clear()
        lv = self.level - 1
        self._time = _TIME[lv]

        random.seed(lv * 31 + 7)
        for i in range(0, WORLD + TS, TS):
            for cx, cy in [(i, 0), (i, WORLD), (0, i), (WORLD, i)]:
                if cx > WORLD or cy > WORLD:
                    continue
                w = arcade.SpriteSolidColor(TS, TS, (30, 30, 30))
                w.center_x, w.center_y = cx, cy
                self.walls.append(w)

        for _ in range(_FCOUNT[lv]):
            f = Flower(random.uniform(120, WORLD - 120),
                       random.uniform(120, WORLD - 300))
            f.color = _FCOL[lv]
            self.flowers.append(f)

        self.player = arcade.SpriteSolidColor(30, 30, C_NEKTAR)
        self.player.center_x = self._hx
        self.player.center_y = self._hy - 80

    def on_update(self, dt: float) -> None:
        if not self.player:
            return
        self._time -= dt
        if self._time <= 0:
            self._game_over()
            return
        spd = SPEED_TD + (self.level - 1) * 20
        vx, vy = 0.0, 0.0
        if arcade.key.LEFT in self.keys or arcade.key.A in self.keys:
            vx = -spd
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys:
            vx = spd
        if arcade.key.UP in self.keys or arcade.key.W in self.keys:
            vy = spd
        elif arcade.key.DOWN in self.keys or arcade.key.S in self.keys:
            vy = -spd
        self.player.center_x = max(20, min(WORLD - 20, self.player.center_x + vx * dt))
        self.player.center_y = max(20, min(WORLD - 20, self.player.center_y + vy * dt))
        self.ps.update(dt)

        for f in self.flowers:
            if not f.depleted:
                d = math.sqrt((f.center_x - self.player.center_x) ** 2
                               + (f.center_y - self.player.center_y) ** 2)
                if d < 40 and self._nectar < MAX_NECTAR_N:
                    got = f.harvest(10)
                    if got > 0:
                        self._nectar = min(MAX_NECTAR_N, self._nectar + got)
                        self.ps.emit_pollen(f.center_x, f.center_y)
                        self._play(self._snd_coin)

        hd = math.sqrt((self.player.center_x - self._hx) ** 2
                        + (self.player.center_y - self._hy) ** 2)
        if hd < 70 and self._nectar > 0:
            self._honey += self._nectar
            self.score += self._nectar * 15
            self._nectar = 0
            self._play(self._snd_coin)

        if all(f.depleted for f in self.flowers):
            self.score += int(self._time) * 10
            self._level_done()
            return

        self._follow(self.player.center_x, self.player.center_y, WORLD, WORLD)

    def on_draw(self) -> None:
        self.clear()
        self.background_color = _FBG[self.level - 1]
        with self.wcam.activate():
            arcade.draw_circle_filled(self._hx, self._hy, 45, C_HIVE)
            arcade.draw_text("УЛЕЙ", self._hx, self._hy, (40, 30, 0), 13,
                             anchor_x="center", anchor_y="center", bold=True)
            self.flowers.draw()
            self.ps.draw()
            if self.player:
                p = self.player
                arcade.draw_ellipse_filled(p.center_x, p.center_y, 28, 20, C_NEKTAR)
                for i in range(3):
                    sx = p.center_x - 10 + i * 10
                    arcade.draw_line(sx, p.center_y - 9, sx, p.center_y + 9,
                                     (40, 30, 0), 3)
                arcade.draw_ellipse_filled(p.center_x, p.center_y + 16,
                                           22, 10, (210, 240, 255, 160))
        with self.gcam.activate():
            self._hud(f"Нектар: {self._nectar}/{MAX_NECTAR_N}")
            draw_bar(120, SCREEN_H - 48, 200, 16,
                     self._time, _TIME[self.level - 1],
                     fill=(80, 200, 100), label="Время")
            arcade.draw_text(
                f"Мёд: {self._honey}",
                SCREEN_W // 2, 14, (220, 200, 60), 13, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
