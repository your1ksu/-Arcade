"""
view_victory.py — Chromatic Heroes
Экран победы. Arcade 3.x.
"""

from __future__ import annotations

import math
import random

import arcade

from constants import (
    SCREEN_W, SCREEN_H, FRAGMENTS, HERO_COLORS, CP_RAINBOW,
)
from utils import draw_btn, btn_hit


class VictoryView(arcade.View):

    def __init__(self, chapter: int = 0, score: int = 0, final: bool = False):
        super().__init__()
        self._ch = chapter
        self._score = score
        self._final = final
        self._t = 0.0
        self._conf = [
            (random.uniform(0, SCREEN_W),
             random.uniform(0, SCREEN_H),
             random.uniform(0.5, 3.0),
             random.choice(CP_RAINBOW))
            for _ in range(60)
        ]

    def on_show_view(self) -> None:
        self.background_color = (10, 18, 10)

    def on_update(self, dt: float) -> None:
        self._t += dt
        self._conf = [
            (x, (y - spd * 60 * dt) % SCREEN_H, spd, col)
            for x, y, spd, col in self._conf
        ]

    def on_draw(self) -> None:
        self.clear()
        for x, y, _, col in self._conf:
            arcade.draw_rectangle_filled(x, y, 8, 14, col)
        if self._final:
            self._draw_final()
        else:
            self._draw_ch()
        draw_btn("Главное меню", SCREEN_W // 2, 130, 300, 52,
                 bg=(35, 55, 35), border=(80, 200, 100))
        if not self._final and self._ch < 8:
            draw_btn("Продолжить >>>", SCREEN_W // 2, 195, 300, 52,
                     bg=(30, 50, 80), border=(80, 160, 240))

    def _draw_ch(self) -> None:
        w = int(4 * math.sin(self._t * 2.5))
        arcade.draw_text(
            "ГЛАВА ПРОЙДЕНА!",
            SCREEN_W // 2, 530 + w,
            (100, 230, 120), 44, anchor_x="center", bold=True,
        )
        arcade.draw_circle_filled(
            SCREEN_W // 2, 435, 32, HERO_COLORS[self._ch - 1]
        )
        arcade.draw_text(
            FRAGMENTS[self._ch - 1], SCREEN_W // 2, 385,
            (220, 215, 180), 18, anchor_x="center",
        )
        arcade.draw_text(
            f"Счёт: {self._score}", SCREEN_W // 2, 340,
            (180, 220, 180), 16, anchor_x="center",
        )

    def _draw_final(self) -> None:
        p = int(6 * math.sin(self._t * 3))
        arcade.draw_text(
            "ВСЕ ОСКОЛКИ СОБРАНЫ!",
            SCREEN_W // 2, 540 + p,
            (240, 215, 60), 40, anchor_x="center", bold=True,
        )
        arcade.draw_text(
            "Принцесса Аква освобождена.\nГирус стал садовником.",
            SCREEN_W // 2, 455,
            (200, 240, 200), 18,
            anchor_x="center", anchor_y="center",
            multiline=True, width=600,
        )
        arcade.draw_text(
            '"Мир не должен быть серым или слишком ярким.\n'
            'Он прекрасен в балансе."',
            SCREEN_W // 2, 320,
            (160, 190, 160), 14,
            anchor_x="center", anchor_y="center",
            multiline=True, width=600,
        )
        for i, col in enumerate(HERO_COLORS):
            a = (2 * math.pi / 8) * i + self._t * 0.5
            arcade.draw_circle_filled(
                SCREEN_W // 2 + math.cos(a) * 80,
                555 + math.sin(a) * 30, 12, col,
            )

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, SCREEN_W // 2, 130, 300, 52):
            from view_menu import MenuView
            self.window.show_view(MenuView())
        elif (
            not self._final and self._ch < 8
            and btn_hit(x, y, SCREEN_W // 2, 195, 300, 52)
        ):
            from view_cutscene import CutsceneView
            self.window.show_view(CutsceneView(self._ch, self._ch + 1))

    def on_key_press(self, key: int, _m: int) -> None:
        if key == arcade.key.ESCAPE:
            from view_menu import MenuView
            self.window.show_view(MenuView())
