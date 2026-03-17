"""
view_chapter_select.py — Chromatic Heroes
Экран выбора главы. Минималистичный эстетичный дизайн. Arcade 3.x.
"""
from __future__ import annotations

import importlib
import math

import arcade

import save_data
from constants import (
    SCREEN_W, SCREEN_H,
    CHAPTER_NAMES, HERO_COLORS, FRAGMENTS,
)
from utils import btn_hit

# ── Сетка карточек ────────────────────────────────────────────────────────────
_COLS   = 2
_CW     = 438   # ширина карточки
_CH_C   = 78    # высота карточки
_PAD_X  = 16
_PAD_Y  = 10
# Верхний левый угол первой карточки
_GX0    = SCREEN_W // 2 - _COLS * (_CW + _PAD_X) // 2
_GY0    = SCREEN_H - 108

_MODS = [
    ("ch1_babl",    "Chapter1View"),
    ("ch2_viks",    "Chapter2View"),
    ("ch3_klyaksa", "Chapter3View"),
    ("ch4_melissa", "Chapter4View"),
    ("ch5_kog",     "Chapter5View"),
    ("ch6_pusinka", "Chapter6View"),
    ("ch7_nektaria","Chapter7View"),
    ("ch8_sherry",  "Chapter8View"),
]

_DESC = [
    "Лети через Индустриальный Город",
    "Не дай потухнуть последней свече",
    "Окрась мир — убей всех роботов",
    "Защити улей от механических ос",
    "Расставь шестерни — запусти механизм",
    "Прыгай по облакам к вершине неба",
    "Разведай поля сквозь туман смога",
    "Беги из лаборатории Гируса!",
]


def _card_pos(idx: int):
    col = idx % _COLS
    row = idx // _COLS
    cx = _GX0 + col * (_CW + _PAD_X) + _CW // 2
    cy = _GY0 - row * (_CH_C + _PAD_Y)
    return cx, cy


class ChapterSelectView(arcade.View):

    def __init__(self) -> None:
        super().__init__()
        self._t  = 0.0
        self._mx = self._my = 0.0

    def on_show_view(self) -> None:
        self.background_color = (11, 9, 20)

    def on_update(self, dt: float) -> None:
        self._t += dt

    def on_draw(self) -> None:
        self.clear()

        # ── Фон: тонкая сетка ────────────────────────────────────────────────
        for xi in range(0, SCREEN_W + 60, 60):
            arcade.draw_line(xi, 0, xi, SCREEN_H, (80, 70, 120, 12), 1)
        for yi in range(0, SCREEN_H + 60, 60):
            arcade.draw_line(0, yi, SCREEN_W, yi, (80, 70, 120, 12), 1)

        # ── Мягкое свечение в центре ─────────────────────────────────────────
        pulse = 0.5 + 0.5 * math.sin(self._t * 0.5)
        arcade.draw_circle_filled(SCREEN_W // 2, SCREEN_H // 2,
                                   int(380 * pulse + 40),
                                   (40, 30, 80, 18))

        # ── Заголовок ─────────────────────────────────────────────────────────
        arcade.draw_text(
            "В Ы Б О Р   Г Л А В Ы",
            SCREEN_W // 2, SCREEN_H - 42,
            (190, 175, 240), 22,
            anchor_x="center", anchor_y="center", bold=True,
        )
        # Декоративная линия под заголовком
        lw = int(300 + 20 * math.sin(self._t * 1.1))
        arcade.draw_rectangle_filled(
            SCREEN_W // 2, SCREEN_H - 62, lw, 1, (100, 85, 160, 90))

        # ── Карточки ─────────────────────────────────────────────────────────
        unlocked = save_data.get_all_unlocked()
        scores   = save_data.get_all_scores()

        for idx in range(8):
            cx, cy = _card_pos(idx)
            is_open = unlocked[idx]
            color   = HERO_COLORS[idx]
            hovered = (abs(self._mx - cx) <= _CW / 2
                       and abs(self._my - cy) <= _CH_C / 2
                       and is_open)

            if is_open:
                # Фоновое свечение при hover
                if hovered:
                    glow_a = int(28 + 14 * math.sin(self._t * 3.5))
                    arcade.draw_rectangle_filled(
                        cx, cy, _CW + 12, _CH_C + 10,
                        (*color, glow_a))
                # Основной фон карточки
                bg_alpha = 200
                r = max(0, color[0] // 6)
                g = max(0, color[1] // 6)
                b = max(0, color[2] // 6 + 8)
                arcade.draw_rectangle_filled(cx, cy, _CW, _CH_C, (r, g, b, bg_alpha))
                # Обводка
                brd_alpha = 180 if hovered else 80
                arcade.draw_rectangle_outline(cx, cy, _CW, _CH_C, (*color, brd_alpha), 1)
                # Цветная полоска слева
                arcade.draw_rectangle_filled(
                    cx - _CW // 2 + 3, cy, 4, _CH_C - 4, color)
                # Номер главы
                arcade.draw_text(
                    str(idx + 1),
                    cx - _CW // 2 + 22, cy,
                    (*color, 220), 24,
                    anchor_x="center", anchor_y="center", bold=True,
                )
                # Название героя
                hero = CHAPTER_NAMES[idx].split("—")[1].strip() \
                    if "—" in CHAPTER_NAMES[idx] else ""
                arcade.draw_text(
                    hero,
                    cx - _CW // 2 + 42, cy + 18,
                    (230, 222, 245), 14,
                    anchor_x="left", anchor_y="center", bold=True,
                )
                # Описание
                arcade.draw_text(
                    _DESC[idx],
                    cx - _CW // 2 + 42, cy - 3,
                    (*[min(255, v + 55) for v in color], 180), 11,
                    anchor_x="left", anchor_y="center",
                )
                # Осколок справа
                frag = FRAGMENTS[idx].split("(")[0].strip()
                arcade.draw_text(
                    frag,
                    cx + _CW // 2 - 10, cy + 18,
                    (*color, 160), 10, anchor_x="right", anchor_y="center",
                )
                sc = scores[idx]
                arcade.draw_text(
                    f"★ {sc}" if sc else "не пройдена",
                    cx + _CW // 2 - 10, cy - 3,
                    (140, 130, 165), 10, anchor_x="right", anchor_y="center",
                )
            else:
                # Заблокированная карточка
                arcade.draw_rectangle_filled(cx, cy, _CW, _CH_C, (20, 17, 30, 180))
                arcade.draw_rectangle_outline(cx, cy, _CW, _CH_C, (50, 44, 70, 100), 1)
                # Серый номер
                arcade.draw_text(
                    str(idx + 1),
                    cx - _CW // 2 + 22, cy,
                    (55, 50, 72), 24,
                    anchor_x="center", anchor_y="center",
                )
                # Замок
                arcade.draw_text(
                    "🔒  Заблокировано",
                    cx, cy,
                    (55, 50, 72), 13,
                    anchor_x="center", anchor_y="center",
                )

        # ── Кнопка «Назад» ────────────────────────────────────────────────────
        arcade.draw_rectangle_filled(70, 34, 118, 40, (20, 16, 34, 200))
        arcade.draw_rectangle_outline(70, 34, 118, 40, (80, 68, 120, 140), 1)
        arcade.draw_text(
            "←  М Е Н Ю",
            70, 34, (150, 138, 195), 14,
            anchor_x="center", anchor_y="center",
        )

    def on_mouse_motion(self, x, y, _dx, _dy):
        self._mx, self._my = x, y

    def on_mouse_press(self, x, y, btn, _m):
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, 70, 34, 118, 40):
            from view_menu import MenuView
            self.window.show_view(MenuView())
            return
        unlocked = save_data.get_all_unlocked()
        for idx in range(8):
            cx, cy = _card_pos(idx)
            if (unlocked[idx]
                    and abs(x - cx) <= _CW / 2
                    and abs(y - cy) <= _CH_C / 2):
                self.launch(idx + 1)
                return

    def launch(self, ch: int) -> None:
        mod, cls = _MODS[ch - 1]
        view = getattr(importlib.import_module(mod), cls)
        self.window.show_view(view(chapter_num=ch))

    def on_key_press(self, key, _m):
        if key == arcade.key.ESCAPE:
            from view_menu import MenuView
            self.window.show_view(MenuView())
