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
        self.background_color = (52, 36, 22)

        goal = _GOAL[self.level - 1]
        pct  = min(1.0, self._dist / goal)

        # ── Фон лаборатории — технические плиты ──────────────────────────────
        tile_w = 120
        offset = int(self._dist * 0.6) % tile_w
        for i in range(-1, SCREEN_W // tile_w + 2):
            tx = i * tile_w - offset
            shade_a = 18 if i % 2 == 0 else 12
            arcade.draw_rectangle_filled(
                tx + tile_w // 2, SCREEN_H // 2,
                tile_w - 1, SCREEN_H, (60 + shade_a, 44 + shade_a // 2, 25, 220))
        # Горизонтальные трубы/кабели
        for y_pipe, col_pipe in [(GROUND_Y + 110, (110, 70, 35, 130)),
                                  (GROUND_Y + 160, (140, 90, 45, 100)),
                                  (SCREEN_H - 60,  (90,  55, 28, 80))]:
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, y_pipe, SCREEN_W, 6, col_pipe)
        # Вертикальные стойки каркаса
        frame_offset = int(self._dist * 0.9) % 200
        for i in range(-1, SCREEN_W // 200 + 2):
            fx2 = i * 200 - frame_offset
            arcade.draw_rectangle_filled(
                fx2, SCREEN_H // 2, 4, SCREEN_H, (70, 50, 28, 180))
            arcade.draw_circle_filled(fx2, GROUND_Y + 35, 5, (100, 72, 40))

        # ── Пол — технический настил ─────────────────────────────────────────
        arcade.draw_rectangle_filled(
            SCREEN_W // 2, GROUND_Y - 18, SCREEN_W, 36, (65, 45, 24))
        # Разметка пола
        for xi in range(0, SCREEN_W + 60, 60):
            fx3 = xi - int(self._dist * 0.4) % 60
            arcade.draw_line(fx3, GROUND_Y - 18, fx3, GROUND_Y + 18,
                             (90, 65, 38, 110), 1)
        # Неоновая полоска вдоль пола
        neon_pulse = int(40 + 20 * math.sin(self._dist * 0.05))
        arcade.draw_rectangle_filled(
            SCREEN_W // 2, GROUND_Y + 17, SCREEN_W, 3,
            (180, neon_pulse + 60, 30, 160))

        # ── Большое колесо — хромированное ───────────────────────────────────
        wr  = 95
        wcx = SCREEN_W // 2
        wcy = GROUND_Y + wr + 8
        # Внешнее свечение
        arcade.draw_circle_filled(wcx, wcy, wr + 14, (140, 90, 30, 30))
        # Обод
        arcade.draw_circle_outline(wcx, wcy, wr, (170, 120, 55), 5)
        arcade.draw_circle_outline(wcx, wcy, wr - 8, (130, 95, 40, 130), 2)
        # Спицы
        for i in range(8):
            a = math.radians(self._wheel + i * 45)
            arcade.draw_line(
                wcx, wcy,
                wcx + math.cos(a) * wr,
                wcy + math.sin(a) * wr,
                (155, 110, 55), 3)
        # Ступицa
        arcade.draw_circle_filled(wcx, wcy, 12, (130, 90, 40))
        arcade.draw_circle_outline(wcx, wcy, 12, (190, 150, 80), 2)

        # ── Препятствия — лабораторные контейнеры ───────────────────────────
        for obs in self.obstacles:
            ox, oy = obs.center_x, obs.center_y
            ow, oh = obs.width, obs.height
            # Основной блок
            arcade.draw_rectangle_filled(ox, oy, ow, oh, obs.color)
            # Неоновая обводка
            r_col, g_col, b_col = obs.color[:3]  # arcade 3 даёт RGBA
            border_c = (min(255, r_col + 60), min(255, g_col + 60),
                        min(255, b_col + 60))
            arcade.draw_rectangle_outline(ox, oy, ow, oh, border_c, 2)
            # Предупреждающая диагональная полоска
            arcade.draw_line(ox - ow // 2, oy - oh // 2,
                             ox + ow // 2, oy + oh // 2,
                             (255, 220, 0, 80), 2)
            # Блик
            arcade.draw_rectangle_filled(
                ox - ow // 4, oy + oh // 4, ow // 4, oh // 6,
                (255, 255, 255, 40))

        self.ps.draw()

        # ── Шерри — хомячка-раннер ───────────────────────────────────────────
        if self.player:
            p = self.player
            flashing = self._hurt_cd > 0 and int(self._hurt_cd * 8) % 2
            bc = (255, 100, 100) if flashing else C_SHERRY
            # Тень
            arcade.draw_ellipse_filled(
                p.center_x + 3, p.center_y - 12, 30, 8, (0, 0, 0, 80))
            # Тело
            arcade.draw_ellipse_filled(p.center_x, p.center_y, 32, 28, bc)
            # Щёки
            arcade.draw_circle_filled(
                p.center_x - 13, p.center_y - 2, 9, (210, 150, 90))
            arcade.draw_circle_filled(
                p.center_x + 13, p.center_y - 2, 9, (210, 150, 90))
            # Глаза — блестящие
            arcade.draw_circle_filled(
                p.center_x - 6, p.center_y + 8, 5, (30, 18, 8))
            arcade.draw_circle_filled(
                p.center_x + 6, p.center_y + 8, 5, (30, 18, 8))
            arcade.draw_circle_filled(
                p.center_x - 5, p.center_y + 9, 2, (255, 255, 255))
            arcade.draw_circle_filled(
                p.center_x + 7, p.center_y + 9, 2, (255, 255, 255))
            # Ушки с розовым внутри
            arcade.draw_ellipse_filled(
                p.center_x - 9, p.center_y + 20, 9, 15, bc)
            arcade.draw_ellipse_filled(
                p.center_x + 9, p.center_y + 20, 9, 15, bc)
            arcade.draw_ellipse_filled(
                p.center_x - 9, p.center_y + 21, 5, 9, (220, 140, 140))
            arcade.draw_ellipse_filled(
                p.center_x + 9, p.center_y + 21, 5, 9, (220, 140, 140))
            # Нос
            arcade.draw_circle_filled(
                p.center_x, p.center_y + 2, 3, (200, 100, 100))

        # ── HUD ──────────────────────────────────────────────────────────────
        with self.gcam.activate():
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (35, 22, 10, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (110, 75, 35, 130), 1)
            self._hud()
            # Жизни
            for i in range(_LIVES):
                color = (200, 55, 75) if i < self._lives else (45, 42, 50)
                arcade.draw_text("♥", 12 + i * 30, SCREEN_H - 52, color, 22)
            # Скорость с неоновым цветом
            speed_col = (min(255, int(180 + pct * 60)),
                         min(255, int(130 + pct * 60)), 60)
            arcade.draw_text(
                f"Скорость: {self._spd:.0f}",
                SCREEN_W // 2, SCREEN_H - 48,
                speed_col, 12, anchor_x="center",
            )
            # Прогресс-бар — неоновый
            bar_x, bar_y, bar_w = SCREEN_W // 2, 22, 320
            arcade.draw_rectangle_filled(bar_x, bar_y, bar_w, 14, (38, 26, 12))
            if pct > 0:
                arcade.draw_rectangle_filled(
                    bar_x - bar_w / 2 + bar_w * pct / 2,
                    bar_y, bar_w * pct, 14,
                    (min(255, int(160 + pct * 80)),
                     min(255, int(100 + pct * 60)), 40))
            arcade.draw_rectangle_outline(bar_x, bar_y, bar_w, 14,
                                          (120, 82, 38, 160), 1)
            arcade.draw_text(
                f"{int(pct * 100)}%",
                bar_x, bar_y, (220, 185, 130), 10,
                anchor_x="center", anchor_y="center",
            )
            arcade.draw_text(
                "ПРОБЕЛ / ↑ — прыжок",
                10, 12, (175, 140, 90), 11,
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
