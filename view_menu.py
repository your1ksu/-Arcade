"""
view_menu.py — Chromatic Heroes
Главное меню. Arcade 3.x.
"""

from __future__ import annotations

import math

import arcade

import save_data
from constants import SCREEN_W, SCREEN_H, HERO_COLORS
from utils import draw_btn, btn_hit

BX = SCREEN_W // 2
B_PLAY = (BX, 300)
B_QUIT = (BX, 235)
BW, BH = 280, 52


class MenuView(arcade.View):

    def __init__(self) -> None:
        super().__init__()
        self._t = 0.0
        save_data.load()

    def on_show_view(self) -> None:
        self.background_color = arcade.color.BLACK

    def on_update(self, dt: float) -> None:
        self._t += dt

    def on_draw(self) -> None:
        self.clear()
        self._stars()
        self._orbs()
        self._title()
        self._buttons()
        n = sum(save_data.get_all_unlocked())
        arcade.draw_text(
            f"Открыто глав: {n} / 8",
            SCREEN_W // 2, 180,
            (130, 120, 160), 13, anchor_x="center",
        )

    def _stars(self) -> None:
        import random
        random.seed(99)
        for _ in range(90):
            sx = random.randint(0, SCREEN_W)
            sy = random.randint(0, SCREEN_H)
            b = int(100 + 80 * math.sin(self._t * 1.4 + sx * 0.1))
            arcade.draw_point(sx, sy, (b, b, b), 2)

    def _orbs(self) -> None:
        cx, cy = SCREEN_W // 2, 160
        for i, color in enumerate(HERO_COLORS):
            a = (2 * math.pi / 8) * i + self._t * 0.3
            rx = cx + math.cos(a) * 110
            ry = cy + math.sin(a) * 35
            dim = tuple(v // 3 for v in color)
            arcade.draw_circle_filled(rx, ry, 18, dim)
            arcade.draw_circle_outline(rx, ry, 18, color, 1)

    def _title(self) -> None:
        w = int(5 * math.sin(self._t * 2))
        arcade.draw_text(
            "CHROMATIC HEROES",
            SCREEN_W // 2, 500 + w,
            (240, 220, 80), 44,
            anchor_x="center", anchor_y="center", bold=True,
        )
        arcade.draw_text(
            "The Canvas Awakening",
            SCREEN_W // 2, 450,
            (200, 180, 240), 22,
            anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            "Eight souls.  One rainbow.  A world reborn.",
            SCREEN_W // 2, 415,
            (160, 150, 200), 14,
            anchor_x="center", anchor_y="center",
        )

    def _buttons(self) -> None:
        draw_btn(
            "ИГРАТЬ", *B_PLAY, BW, BH,
            bg=(50, 100, 60), border=(100, 220, 120),
        )
        draw_btn(
            "ВЫХОД", *B_QUIT, BW, BH,
            bg=(80, 40, 40), border=(200, 80, 80),
        )

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, *B_PLAY, BW, BH):
            from view_chapter_select import ChapterSelectView
            self.window.show_view(ChapterSelectView())
        elif btn_hit(x, y, *B_QUIT, BW, BH):
            arcade.exit()

    def on_key_press(self, key: int, _m: int) -> None:
        if key == arcade.key.ESCAPE:
            arcade.exit()
