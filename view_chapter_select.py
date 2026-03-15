"""
view_chapter_select.py — Chromatic Heroes
Выбор главы. Arcade 3.x.
"""

from __future__ import annotations

import importlib

import arcade

import save_data
from constants import SCREEN_W, SCREEN_H, CHAPTER_NAMES, HERO_COLORS, FRAGMENTS
from utils import draw_btn, btn_hit

CW, CH_C = 220, 90
COLS = 2
SX = SCREEN_W // 2 - CW // 2 - 120
SY = SCREEN_H - 140
GX, GY = CW + 30, CH_C + 18

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


def _rect(idx: int) -> tuple:
    col = idx % COLS
    row = idx // COLS
    return SX + col * GX, SY - row * GY, CW, CH_C


class ChapterSelectView(arcade.View):

    def on_show_view(self) -> None:
        self.background_color = (12, 8, 25)

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text(
            "Выбор главы",
            SCREEN_W // 2, SCREEN_H - 50,
            (220, 200, 80), 30, anchor_x="center", bold=True,
        )
        unlocked = save_data.get_all_unlocked()
        scores = save_data.get_all_scores()
        for idx in range(8):
            cx, cy, w, h = _rect(idx)
            open_ = unlocked[idx]
            c = HERO_COLORS[idx]
            if open_:
                bg = tuple(v // 4 for v in c)
                border, nc = c, (240, 230, 210)
            else:
                bg, border, nc = (30, 28, 38), (60, 55, 70), (70, 65, 80)
            arcade.draw_rectangle_filled(cx, cy, w, h, bg)
            arcade.draw_rectangle_outline(cx, cy, w, h, border, 2)
            short = CHAPTER_NAMES[idx].split("—")[0].strip()
            arcade.draw_text(short, cx, cy + 22, nc, 11,
                             anchor_x="center", anchor_y="center", bold=True)
            if open_:
                ec = tuple(min(255, v + 40) for v in c)
                arcade.draw_text(FRAGMENTS[idx], cx, cy, ec, 9,
                                 anchor_x="center", anchor_y="center")
                st = f"Лучший: {scores[idx]}" if scores[idx] else "Не пройдена"
                arcade.draw_text(st, cx, cy - 20, (160, 155, 170), 9,
                                 anchor_x="center", anchor_y="center")
            else:
                arcade.draw_text("Заблокировано", cx, cy,
                                 (70, 65, 80), 11,
                                 anchor_x="center", anchor_y="center")
        draw_btn("Меню", 80, 36, 130, 40,
                 bg=(40, 35, 55), border=(120, 110, 150), font_size=14)

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, 80, 36, 130, 40):
            from view_menu import MenuView
            self.window.show_view(MenuView())
            return
        unlocked = save_data.get_all_unlocked()
        for idx in range(8):
            cx, cy, w, h = _rect(idx)
            if unlocked[idx] and btn_hit(x, y, cx, cy, w, h):
                self.launch(idx + 1)
                return

    def launch(self, ch: int) -> None:
        mod, cls = _MODS[ch - 1]
        view = getattr(importlib.import_module(mod), cls)
        self.window.show_view(view(chapter_num=ch))

    def on_key_press(self, key: int, _m: int) -> None:
        if key == arcade.key.ESCAPE:
            from view_menu import MenuView
            self.window.show_view(MenuView())
