"""
view_menu.py — Chromatic Heroes
Главное меню. Минималистичный эстетичный дизайн. Arcade 3.x.
"""
from __future__ import annotations

import math
import random

import arcade

import save_data
from constants import SCREEN_W, SCREEN_H, HERO_COLORS
from utils import btn_hit

_CX = SCREEN_W // 2

# Кнопки
_B_PLAY  = (_CX,       318)
_B_QUIT  = (_CX - 155, 248)
_B_RESET = (_CX + 155, 248)
_BW, _BH         = 290, 54
_BW_SM, _BH_SM   = 240, 44


def _draw_pill(x, y, w, h, fill, border, border_w=1):
    """Рисует прямоугольник — «таблетка»."""
    arcade.draw_rectangle_filled(x, y, w, h, fill)
    arcade.draw_rectangle_outline(x, y, w, h, border, border_w)


class MenuView(arcade.View):

    def __init__(self) -> None:
        super().__init__()
        self._t = 0.0
        # Фоновые точки-«пыль»
        random.seed(7)
        self._dust = [
            (random.uniform(0, SCREEN_W),
             random.uniform(0, SCREEN_H),
             random.uniform(0.15, 0.55),   # скорость Y
             random.uniform(1, 2.5),        # размер
             random.choice(HERO_COLORS),
             random.uniform(0, math.pi * 2))
            for _ in range(55)
        ]
        save_data.load()

    def on_show_view(self) -> None:
        self.background_color = (11, 9, 20)

    def on_update(self, dt: float) -> None:
        self._t += dt
        self._dust = [
            (x, (y + spd) % (SCREEN_H + 10),
             spd, r, col, phase)
            for x, y, spd, r, col, phase in self._dust
        ]

    def on_draw(self) -> None:
        self.clear()

        # ── Фон: тонкая сетка ────────────────────────────────────────────────
        grid_alpha = 14
        for xi in range(0, SCREEN_W + 60, 60):
            arcade.draw_line(xi, 0, xi, SCREEN_H,
                             (80, 70, 120, grid_alpha), 1)
        for yi in range(0, SCREEN_H + 60, 60):
            arcade.draw_line(0, yi, SCREEN_W, yi,
                             (80, 70, 120, grid_alpha), 1)

        # ── Мягкое радиальное свечение по центру ─────────────────────────────
        pulse = 0.5 + 0.5 * math.sin(self._t * 0.6)
        for radius, alpha in [(320, 22), (200, 35), (110, 28)]:
            arcade.draw_circle_filled(
                _CX, 380, int(radius * (0.92 + 0.08 * pulse)),
                (60, 45, 110, int(alpha * (0.8 + 0.2 * pulse))))

        # ── Плавающая пыль (цветные частицы) ─────────────────────────────────
        for x, y, spd, r, col, phase in self._dust:
            brightness = 0.5 + 0.5 * math.sin(self._t * 1.2 + phase)
            alpha = int(40 + 60 * brightness)
            arcade.draw_circle_filled(x, y, r, (*col, alpha))

        # ── Орнамент: горизонтальные акцентные линии ─────────────────────────
        for y_line, alpha_line in [(540, 60), (200, 45)]:
            for xi in range(0, SCREEN_W, 4):
                phase_shift = xi * 0.04 + self._t * 0.8
                dot_y = y_line + int(5 * math.sin(phase_shift))
                col_idx = int(xi / SCREEN_W * len(HERO_COLORS))
                c = HERO_COLORS[min(col_idx, len(HERO_COLORS) - 1)]
                arcade.draw_circle_filled(xi, dot_y, 1, (*c, alpha_line))

        # ── Заголовок ─────────────────────────────────────────────────────────
        wave = 4 * math.sin(self._t * 1.8)
        # Тень
        arcade.draw_text(
            "CHROMATIC HEROES",
            _CX + 2, 498 + wave,
            (30, 20, 60, 160), 46,
            anchor_x="center", anchor_y="center", bold=True,
        )
        # Основной текст
        arcade.draw_text(
            "CHROMATIC HEROES",
            _CX, 500 + wave,
            (235, 215, 80), 46,
            anchor_x="center", anchor_y="center", bold=True,
        )
        # Подзаголовок
        arcade.draw_text(
            "T H E   C A N V A S   A W A K E N I N G",
            _CX, 454,
            (160, 145, 210), 13,
            anchor_x="center", anchor_y="center",
        )
        # Тонкая декоративная линия
        line_w = int(340 + 20 * math.sin(self._t * 0.9))
        arcade.draw_rectangle_filled(_CX, 434, line_w, 1, (120, 100, 180, 100))

        # ── Кнопка ИГРАТЬ ─────────────────────────────────────────────────────
        glow = int(30 + 20 * math.sin(self._t * 2.2))
        arcade.draw_rectangle_filled(
            _CX, _B_PLAY[1], _BW + 24, _BH + 14,
            (40, glow + 55, 50, 35))
        _draw_pill(*_B_PLAY, _BW, _BH,
                   fill=(28, 60, 38),
                   border=(70, 195, 95), border_w=2)
        arcade.draw_text(
            "▶   П Л А Й",
            _CX, _B_PLAY[1],
            (180, 240, 190), 20,
            anchor_x="center", anchor_y="center", bold=True,
        )

        # ── Кнопки ВЫХОД и СБРОС ─────────────────────────────────────────────
        _draw_pill(*_B_QUIT, _BW_SM, _BH_SM,
                   fill=(40, 22, 22),
                   border=(170, 60, 60), border_w=1)
        arcade.draw_text(
            "✕  В Ы Х О Д",
            _B_QUIT[0], _B_QUIT[1],
            (200, 120, 120), 14,
            anchor_x="center", anchor_y="center",
        )
        _draw_pill(*_B_RESET, _BW_SM, _BH_SM,
                   fill=(30, 24, 14),
                   border=(130, 100, 35), border_w=1)
        arcade.draw_text(
            "↺  С Б Р О С",
            _B_RESET[0], _B_RESET[1],
            (175, 150, 80), 14,
            anchor_x="center", anchor_y="center",
        )

        # ── Прогресс и слоган ─────────────────────────────────────────────────
        n = sum(save_data.get_all_unlocked())
        bar_w = 260
        arcade.draw_rectangle_filled(_CX, 178, bar_w, 5, (35, 30, 55))
        if n > 0:
            arcade.draw_rectangle_filled(
                _CX - bar_w / 2 + bar_w * n / 16,
                178, bar_w * n / 8, 5, (110, 80, 200))
        arcade.draw_text(
            f"Открыто  {n} / 8  глав",
            _CX, 162, (100, 90, 140), 12, anchor_x="center",
        )
        arcade.draw_text(
            "Eight souls.  One rainbow.  A world reborn.",
            _CX, 138, (70, 62, 100), 11, anchor_x="center",
        )

    def on_mouse_press(self, x, y, btn, _m):
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, *_B_PLAY, _BW, _BH):
            from view_chapter_select import ChapterSelectView
            self.window.show_view(ChapterSelectView())
        elif btn_hit(x, y, *_B_QUIT, _BW_SM, _BH_SM):
            arcade.exit()
        elif btn_hit(x, y, *_B_RESET, _BW_SM, _BH_SM):
            save_data.reset_all()
            save_data.load()

    def on_key_press(self, key, _m):
        if key == arcade.key.ESCAPE:
            arcade.exit()
        elif key == arcade.key.RETURN:
            from view_chapter_select import ChapterSelectView
            self.window.show_view(ChapterSelectView())
