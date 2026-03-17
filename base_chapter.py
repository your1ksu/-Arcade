"""
base_chapter.py — Chromatic Heroes
Базовый класс для всех 8 глав. Arcade 3.x.
"""

from __future__ import annotations

from abc import abstractmethod

import arcade
from arcade.camera import Camera2D

import save_data
import utils  # активирует шим draw_rectangle_*
from constants import SCREEN_W, SCREEN_H
from particles import ParticleSystem

# ── Кнопка «В меню» — позиция и размер ───────────────────────────────────────
_BTN_X = SCREEN_W - 70   # правый нижний угол
_BTN_Y = 28
_BTN_W = 120
_BTN_H = 38


class BaseChapter(arcade.View):
    """Общая инфраструктура: камеры, HUD, кнопка «В меню», звуки, переходы."""

    def __init__(self, chapter_num: int) -> None:
        super().__init__()
        self.ch: int = chapter_num
        self.level: int = 1
        self.score: int = 0

        self.wcam: Camera2D = Camera2D()
        self.gcam: Camera2D = Camera2D()

        self.ps: ParticleSystem = ParticleSystem()
        self.keys: set = set()

        # Защита от мгновенного срабатывания финиша при setup()
        self._grace: float = 0.5
        self._grace_t: float = 0.0

        # HUD-тексты
        self._txt_top_left = arcade.Text(
            "", 10, SCREEN_H - 28, (200, 200, 220), 13)
        self._txt_top_right = arcade.Text(
            "", SCREEN_W - 10, SCREEN_H - 28,
            (200, 200, 220), 13, anchor_x="right")
        self._txt_center = arcade.Text(
            "", SCREEN_W // 2, SCREEN_H - 28,
            (230, 210, 180), 13, anchor_x="center")

        # Кнопка «В меню» — один аркадный Text-объект
        self._btn_txt = arcade.Text(
            "⌂  Меню",
            _BTN_X, _BTN_Y,
            (210, 200, 230), 13,
            anchor_x="center", anchor_y="center",
            bold=True,
        )

        self._snd_coin = self._snd(":resources:sounds/coin1.wav")
        self._snd_hurt = self._snd(":resources:sounds/hurt1.wav")
        self._snd_jump = self._snd(":resources:sounds/jump1.wav")
        self._snd_over = self._snd(":resources:sounds/gameover1.wav")

    # ── Звук ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _snd(path: str):
        try:
            return arcade.load_sound(path)
        except Exception:
            return None

    def _play(self, sound) -> None:
        if sound:
            arcade.play_sound(sound, volume=0.35)

    # ── Камера ────────────────────────────────────────────────────────────────
    def _follow(self, tx: float, ty: float,
                ww: float = None, wh: float = None) -> None:
        ww = ww or SCREEN_W
        wh = wh or SCREEN_H
        utils.cam_follow(self.wcam, tx, ty, ww, wh, SCREEN_W, SCREEN_H)

    # ── HUD + кнопка «В меню» ─────────────────────────────────────────────────
    def _hud(self, extra: str = "") -> None:
        """
        Рисует стандартный HUD и кнопку «В меню» в правом нижнем углу.
        Должна вызываться внутри блока  with self.gcam.activate():
        """
        self._txt_top_left.text = f"Гл.{self.ch}  Ур.{self.level}"
        self._txt_top_left.draw()
        self._txt_top_right.text = f"Счёт: {self.score}"
        self._txt_top_right.draw()
        if extra:
            self._txt_center.text = extra
            self._txt_center.draw()

        # ── Кнопка «В меню» ──────────────────────────────────────────────────
        # Фон с закруглёнными ощущениями (два прямоугольника + обводка)
        arcade.draw_rectangle_filled(
            _BTN_X, _BTN_Y, _BTN_W, _BTN_H, (30, 26, 48, 200))
        arcade.draw_rectangle_outline(
            _BTN_X, _BTN_Y, _BTN_W, _BTN_H, (110, 95, 155), 1)
        # Тонкая цветная верхняя линия-акцент
        arcade.draw_rectangle_filled(
            _BTN_X, _BTN_Y + _BTN_H // 2 - 1,
            _BTN_W - 2, 2, (140, 120, 190, 160))
        self._btn_txt.draw()

    def _draw_menu_btn(self) -> None:
        """Можно вызвать отдельно если _hud() не используется."""
        self._hud()

    # ── Hit-test кнопки ───────────────────────────────────────────────────────
    @staticmethod
    def _menu_btn_hit(mx: float, my: float) -> bool:
        return (abs(mx - _BTN_X) <= _BTN_W / 2
                and abs(my - _BTN_Y) <= _BTN_H / 2)

    def _go_menu(self) -> None:
        from view_menu import MenuView
        self.window.show_view(MenuView())

    # ── Переходы ──────────────────────────────────────────────────────────────
    def _level_done(self) -> None:
        self._play(self._snd_coin)
        if self.level < 3:
            self.level += 1
            self.ps.clear()
            self._grace_t = 0.0
            self.setup()
        else:
            save_data.complete_chapter(self.ch, self.score)
            from view_victory import VictoryView
            self.window.show_view(VictoryView(self.ch, self.score))

    def _game_over(self) -> None:
        self._play(self._snd_over)
        from view_game_over import GameOverView
        self.window.show_view(GameOverView(self.ch, self.level, self.score))

    def _can_finish(self) -> bool:
        return self._grace_t >= self._grace

    def _tick_grace(self, dt: float) -> None:
        self._grace_t = min(self._grace + 0.1, self._grace_t + dt)

    # ── Абстрактный интерфейс ─────────────────────────────────────────────────
    @abstractmethod
    def setup(self) -> None:
        """Инициализировать / сбросить текущий уровень."""

    def on_show_view(self) -> None:
        self._grace_t = 0.0
        self.setup()

    def on_key_press(self, key: int, mod: int) -> None:
        self.keys.add(key)
        if key == arcade.key.ESCAPE:
            self._go_menu()

    def on_key_release(self, key: int, mod: int) -> None:
        self.keys.discard(key)

    def on_mouse_press(self, x: float, y: float, button: int, mod: int) -> None:
        """Обрабатываем нажатие кнопки «В меню» для всех глав."""
        if button == arcade.MOUSE_BUTTON_LEFT and self._menu_btn_hit(x, y):
            self._go_menu()
