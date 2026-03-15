"""
view_game_over.py — Chromatic Heroes
Экран поражения. Arcade 3.x.
"""

from __future__ import annotations

import arcade

from constants import SCREEN_W, SCREEN_H
from utils import draw_btn, btn_hit


class GameOverView(arcade.View):

    def __init__(self, ch: int, lv: int, score: int = 0) -> None:
        super().__init__()
        self._ch, self._lv, self._score = ch, lv, score

    def on_show_view(self) -> None:
        self.background_color = (25, 8, 8)

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text(
            "КОНЕЦ ИГРЫ",
            SCREEN_W // 2, 460, (220, 60, 60), 54,
            anchor_x="center", bold=True,
        )
        arcade.draw_text(
            f"Глава {self._ch}  •  Уровень {self._lv}",
            SCREEN_W // 2, 385, (180, 140, 140), 20, anchor_x="center",
        )
        if self._score:
            arcade.draw_text(
                f"Счёт: {self._score}",
                SCREEN_W // 2, 340, (200, 160, 120), 18, anchor_x="center",
            )
        draw_btn("Попробовать снова", SCREEN_W // 2, 260, 300, 52,
                 bg=(60, 30, 30), border=(200, 80, 80))
        draw_btn("Главное меню", SCREEN_W // 2, 195, 300, 52,
                 bg=(35, 35, 55), border=(130, 120, 170))

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if btn_hit(x, y, SCREEN_W // 2, 260, 300, 52):
            self._retry()
        elif btn_hit(x, y, SCREEN_W // 2, 195, 300, 52):
            from view_menu import MenuView
            self.window.show_view(MenuView())

    def on_key_press(self, key: int, _m: int) -> None:
        if key == arcade.key.R:
            self._retry()
        elif key == arcade.key.ESCAPE:
            from view_menu import MenuView
            self.window.show_view(MenuView())

    def _retry(self) -> None:
        from view_chapter_select import ChapterSelectView
        cs = ChapterSelectView()
        self.window.show_view(cs)
        cs.launch(self._ch)
