"""
ch8_sherry.py — Глава 8: Шерри — Хомячиха-бегунья
Авторан: фон скроллится, препятствия летят навстречу,
скорость нарастает. Arcade 3.x.
"""

from __future__ import annotations

import math
import random

import arcade

from base_chapter import BaseChapter
from constants import (
    SCREEN_W, SCREEN_H,
    RUN_SPD0, RUN_INC, RUN_INC_T,
    C_SHERRY,
)
from sprites import Obstacle

# Фиксированная позиция игрока
PX: int = 160
PY: int = 200
GROUND_Y: int = PY - 20

# Цель — столько пикселей надо пробежать
_GOAL = [3000, 5000, 8000]
_LIVES = 3


class Chapter8View(BaseChapter):

    def __init__(self, chapter_num: int = 8) -> None:
        super().__init__(chapter_num)
        self.player = None
        self.obstacles: arcade.SpriteList = arcade.SpriteList()

        self._spd: float = RUN_SPD0
        self._dist: float = 0.0
        self._inc_t: float = 0.0
        self._spawn_t: float = 0.0
        self._spawn_int: float = 1.8

        self._lives: int = _LIVES
        self._jumping: bool = False
        self._vy: float = 0.0
        self._wheel: float = 0.0
        self._hurt_cd: float = 0.0
        self._dust_t: float = 0.0

    # ── Setup ─────────────────────────────────────────────────────────────────
    def setup(self) -> None:
        self.ps.clear()
        self.obstacles.clear()

        self._spd = RUN_SPD0 + (self.level - 1) * 1.5
        self._dist = 0.0
        self._inc_t = 0.0
        self._spawn_t = 0.0
        self._spawn_int = max(0.8, 1.8 - (self.level - 1) * 0.3)
        self._lives = _LIVES
        self._jumping = False
        self._vy = 0.0
        self._wheel = 0.0
        self._hurt_cd = 0.0
        self._dust_t = 0.0

        self.player = arcade.SpriteSolidColor(32, 32, C_SHERRY)
        self.player.center_x = PX
        self.player.center_y = PY

    # ── Update ────────────────────────────────────────────────────────────────
    def on_update(self, dt: float) -> None:
        if not self.player:
            return

        # Ускорение со временем
        self._inc_t += dt
        if self._inc_t >= RUN_INC_T:
            self._inc_t = 0.0
            self._spd += RUN_INC

        # Расстояние
        self._dist += self._spd * dt
        self._wheel -= self._spd * dt * 0.8

        # Прыжок (ручная физика — в раннере нет платформера)
        if self._jumping:
            self.player.center_y += self._vy * dt
            self._vy -= 600.0 * dt
            if self.player.center_y <= PY:
                self.player.center_y = PY
                self._jumping = False
                self._vy = 0.0

        # Спавн препятствий
        self._spawn_t += dt
        if self._spawn_t >= self._spawn_int:
            self._spawn_t = 0.0
            self._spawn_int = max(
                0.6, random.uniform(0.9, 1.8) - (self.level - 1) * 0.1
            )
            w = random.randint(24, 50)
            h = random.randint(30, 90)
            obs = Obstacle(SCREEN_W + w, GROUND_Y + h // 2, w, h)
            self.obstacles.append(obs)

        # Двигаем препятствия
        for obs in list(self.obstacles):
            obs.center_x -= self._spd * dt
            if obs.center_x < -100:
                obs.remove_from_sprite_lists()
                self.score += 10

        # Опилки за игроком
        self._dust_t += dt
        if self._dust_t >= 0.08:
            self._dust_t = 0.0
            self.ps.emit_dust(
                self.player.center_x - 16,
                self.player.center_y - 10,
            )

        self.ps.update(dt)

        # Столкновения
        self._hurt_cd -= dt
        if self._hurt_cd <= 0:
            hits = arcade.check_for_collision_with_list(
                self.player, self.obstacles
            )
            if hits:
                self._lives -= 1
                self._hurt_cd = 1.5
                for obs in hits:
                    obs.remove_from_sprite_lists()
                self._play(self._snd_hurt)
                if self._lives <= 0:
                    self._game_over()
                    return

        # Победа
        if self._dist >= _GOAL[self.level - 1]:
            self.score += int(self._spd) * 10
            self._level_done()

    # ── Draw ──────────────────────────────────────────────────────────────────
    def on_draw(self) -> None:
        self.clear()
        self.background_color = (60, 45, 30)

        # Скроллящиеся полосы
        sw = 200
        offset = int(self._dist % sw)
        for i in range(-1, SCREEN_W // sw + 2):
            sx = i * sw - offset
            shade = 55 + (i % 2) * 12
            arcade.draw_rectangle_filled(
                sx + sw // 2, SCREEN_H // 2,
                sw, SCREEN_H,
                (shade, shade - 10, shade - 20),
            )

        # Земля
        arcade.draw_rectangle_filled(
            SCREEN_W // 2, GROUND_Y - 15,
            SCREEN_W, 30, (80, 60, 35),
        )

        # Колесо (декоративное)
        wr = 90
        wcx, wcy = SCREEN_W // 2, GROUND_Y + wr
        arcade.draw_circle_outline(wcx, wcy, wr, (100, 80, 55), 6)
        for i in range(8):
            a = math.radians(self._wheel + i * 45)
            arcade.draw_line(
                wcx, wcy,
                wcx + math.cos(a) * wr,
                wcy + math.sin(a) * wr,
                (120, 90, 60), 3,
            )

        self.obstacles.draw()
        self.ps.draw()

        # Игрок
        if self.player:
            p = self.player
            # Мигание при неуязвимости
            flashing = self._hurt_cd > 0 and int(self._hurt_cd * 8) % 2
            bc = (255, 100, 100) if flashing else C_SHERRY

            arcade.draw_ellipse_filled(p.center_x, p.center_y, 32, 28, bc)
            # Щёки
            arcade.draw_circle_filled(
                p.center_x - 12, p.center_y - 2, 9, (220, 160, 100)
            )
            arcade.draw_circle_filled(
                p.center_x + 12, p.center_y - 2, 9, (220, 160, 100)
            )
            # Глаза
            arcade.draw_circle_filled(
                p.center_x - 6, p.center_y + 8, 4, (40, 20, 10)
            )
            arcade.draw_circle_filled(
                p.center_x + 6, p.center_y + 8, 4, (40, 20, 10)
            )
            # Ушки
            arcade.draw_ellipse_filled(
                p.center_x - 8, p.center_y + 20, 8, 14, bc
            )
            arcade.draw_ellipse_filled(
                p.center_x + 8, p.center_y + 20, 8, 14, bc
            )

        # HUD
        with self.gcam.activate():
            self._hud()
            for i in range(_LIVES):
                color = (220, 60, 80) if i < self._lives else (60, 50, 55)
                arcade.draw_text(
                    "♥", 12 + i * 30, SCREEN_H - 52, color, 22,
                )
            arcade.draw_text(
                f"Скорость: {self._spd:.0f} пкс/с",
                SCREEN_W // 2, SCREEN_H - 48,
                (200, 180, 140), 12, anchor_x="center",
            )
            # Полоска прогресса
            goal = _GOAL[self.level - 1]
            pct = min(1.0, self._dist / goal)
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 20, 300, 14, (40, 35, 30)
            )
            if pct > 0:
                arcade.draw_rectangle_filled(
                    SCREEN_W // 2 - 150 + 150 * pct,
                    20, 300 * pct, 14, (180, 120, 50),
                )
            arcade.draw_text(
                f"{int(pct * 100)}%",
                SCREEN_W // 2, 20, (220, 200, 160), 10,
                anchor_x="center", anchor_y="center",
            )
            arcade.draw_text(
                "ПРОБЕЛ / ↑ — прыжок",
                10, 12, (160, 145, 120), 11,
            )

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if (
            key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W)
            and not self._jumping
            and self.player is not None
        ):
            self._jumping = True
            self._vy = 520.0
            self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
