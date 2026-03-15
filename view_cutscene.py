"""
view_cutscene.py — Chromatic Heroes
Кат-сцена между главами. Arcade 3.x.
"""

from __future__ import annotations

import math

import arcade

from constants import SCREEN_W, SCREEN_H, CUTSCENES, HERO_COLORS
from utils import draw_btn, btn_hit


class CutsceneView(arcade.View):

    def __init__(self, done: int, next_ch: int) -> None:
        super().__init__()
        self._done = done
        self._next = next_ch
        self._t = 0.0
        data = CUTSCENES.get(done, ("", ""))
        self._head = data[0]
        self._body = data[1]
        self._col = HERO_COLORS[done - 1]

    def on_show_view(self) -> None:
        self.background_color = (8, 6, 20)

    def on_update(self, dt: float) -> None:
        self._t += dt

    def on_draw(self) -> None:
        self.clear()
        c = self._col
        for i in range(6):
            a = (2 * math.pi / 6) * i + self._t * 0.4
            arcade.draw_circle_filled(
                SCREEN_W // 2 + math.cos(a) * 320,
                610 + math.sin(a) * 100,
                4, tuple(v // 3 for v in c),
            )
        arcade.draw_circle_filled(SCREEN_W // 2, 610, 28, c)
        arcade.draw_circle_outline(SCREEN_W // 2, 610, 28, (255, 255, 255), 2)
        arcade.draw_text(
            f"Глава {self._done} завершена!",
            SCREEN_W // 2, 560, (220, 200, 80), 22,
            anchor_x="center", bold=True,
        )
        arcade.draw_text(
            self._head, SCREEN_W // 2, 490,
            (210, 205, 230), 16,
            anchor_x="center", anchor_y="center",
            multiline=True, width=700,
        )
        arcade.draw_text(
            self._body, SCREEN_W // 2, 370,
            (180, 175, 200), 13,
            anchor_x="center", anchor_y="center",
            multiline=True, width=700,
        )
        label = "Финал!" if self._next > 8 else f"Глава {self._next} >>>"
        draw_btn(label, SCREEN_W // 2, 180, 340, 52,
                 bg=(50, 60, 80), border=(140, 180, 220))
        draw_btn("Меню", 80, 36, 130, 40,
                 bg=(40, 35, 55), border=(120, 110, 150), font_size=14)

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, SCREEN_W // 2, 180, 340, 52):
            self._go()
        elif btn_hit(x, y, 80, 36, 130, 40):
            from view_menu import MenuView
            self.window.show_view(MenuView())

    def on_key_press(self, key: int, _m: int) -> None:
        if key in (arcade.key.ENTER, arcade.key.SPACE):
            self._go()
        elif key == arcade.key.ESCAPE:
            from view_menu import MenuView
            self.window.show_view(MenuView())

    def _go(self) -> None:
        if self._next > 8:
            from view_victory import VictoryView
            self.window.show_view(VictoryView(final=True))
        else:
            from view_chapter_select import ChapterSelectView
            cs = ChapterSelectView()
            self.window.show_view(cs)
            cs.launch(self._next)
