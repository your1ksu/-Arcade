"""
ch7_nektaria.py — Глава 7: Нектария — Пчела-разведчица
Уникальная механика: туман войны + опасные зоны + бонусные цветы.
- Поле покрыто «туманом»: видно только круг вокруг игрока
- Красные зоны (ядовитый смог Гируса) сжигают нектар при входе
- Золотые цветы дают x3 нектара
- Цель: собрать все цветы и вернуть нектар в улей
Arcade 3.x.
"""
from __future__ import annotations

import math
import random

import arcade

from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, C_NEKTAR, C_HIVE
from sprites import Flower
from utils import draw_bar

WORLD = 1800          # размер поля
SPD   = 220.0         # px/s

# Радиус видимости вокруг игрока (туман войны)
_FOG_R = [220, 180, 140]

_FBG    = [(25, 45, 20), (50, 42, 10), (30, 18, 40)]
_FCOL   = [(200, 160, 240), (240, 200, 40), (160, 100, 240)]
_GOLD   = (255, 210, 30)       # цвет золотого цветка (x3)
_FCOUNT = [16, 22, 30]         # обычных цветов
_GCOUNT = [3,  4,   5]         # золотых цветов
_SMOG   = [3,  4,   5]         # зон смога
_SMOG_R = 90                   # радиус зоны смога
_TIME   = [120.0, 100.0, 85.0]
MAX_NECTAR = 50


class SmogZone:
    """Красная ядовитая зона: сжигает нектар при нахождении внутри."""
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y
        self.pulse = random.uniform(0, math.pi * 2)  # фаза пульсации

    def draw(self) -> None:
        r = _SMOG_R + 6 * math.sin(self.pulse)
        arcade.draw_circle_filled(self.x, self.y, r, (200, 40, 40, 60))
        arcade.draw_circle_outline(self.x, self.y, r, (220, 60, 60), 2)

    def contains(self, px: float, py: float) -> bool:
        return math.dist((self.x, self.y), (px, py)) < _SMOG_R


class Chapter7View(BaseChapter):

    def __init__(self, chapter_num: int = 7) -> None:
        super().__init__(chapter_num)
        self.player   = None
        self.flowers  = arcade.SpriteList()   # обычные цветы
        self.gold_flowers: list[Flower] = []  # золотые цветы
        self._gold_sl = arcade.SpriteList()
        self._smog_zones: list[SmogZone] = []

        self._nectar  = 0
        self._honey   = 0
        self._hx      = WORLD / 2
        self._hy      = WORLD - 150.0
        self._time    = 0.0
        self._fog_r   = 220
        self._smog_drain_t = 0.0  # таймер урона от смога

        self._txt_smog = arcade.Text(
            "", SCREEN_W // 2, SCREEN_H // 2 - 40,
            (255, 80, 80), 20, anchor_x="center", bold=True,
        )
        self._smog_flash = 0.0

    def setup(self) -> None:
        self._nectar  = 0
        self._honey   = 0
        self._smog_drain_t = 0.0
        self._smog_flash   = 0.0
        self.ps.clear()
        self.flowers.clear()
        self.gold_flowers.clear()
        self._gold_sl.clear()
        self._smog_zones.clear()

        lv = self.level - 1
        self._time  = _TIME[lv]
        self._fog_r = _FOG_R[lv]

        random.seed(lv * 53 + 11)

        # Обычные цветы
        for _ in range(_FCOUNT[lv]):
            f = Flower(random.uniform(100, WORLD - 100),
                       random.uniform(100, WORLD - 350))
            f.color = _FCOL[lv]
            self.flowers.append(f)

        # Золотые цветы (x3 нектара)
        for _ in range(_GCOUNT[lv]):
            f = Flower(random.uniform(120, WORLD - 120),
                       random.uniform(120, WORLD - 300))
            f.color = _GOLD
            f.nectar = 30       # x3
            self.gold_flowers.append(f)
            self._gold_sl.append(f)

        # Зоны смога
        for _ in range(_SMOG[lv]):
            sx = random.uniform(150, WORLD - 150)
            sy = random.uniform(150, WORLD - 350)
            # Не ставить смог на улей
            if math.dist((sx, sy), (self._hx, self._hy)) > 180:
                self._smog_zones.append(SmogZone(sx, sy))

        self.player = arcade.SpriteSolidColor(30, 30, C_NEKTAR)
        self.player.center_x = self._hx
        self.player.center_y = self._hy - 80

    def on_update(self, dt: float) -> None:
        if not self.player:
            return
        self._time -= dt
        if self._time <= 0:
            self._game_over()
            return

        # Пульсация смога
        for sz in self._smog_zones:
            sz.pulse += dt * 2.0

        spd = SPD + (self.level - 1) * 30
        vx, vy = 0.0, 0.0
        if arcade.key.LEFT  in self.keys or arcade.key.A in self.keys: vx = -spd
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys: vx =  spd
        if arcade.key.UP    in self.keys or arcade.key.W in self.keys: vy =  spd
        elif arcade.key.DOWN in self.keys or arcade.key.S in self.keys: vy = -spd

        self.player.center_x = max(20, min(WORLD - 20,
                                            self.player.center_x + vx * dt))
        self.player.center_y = max(20, min(WORLD - 20,
                                            self.player.center_y + vy * dt))
        self.ps.update(dt)

        px, py = self.player.center_x, self.player.center_y

        # Смог — сжигает нектар
        in_smog = any(sz.contains(px, py) for sz in self._smog_zones)
        if in_smog:
            self._smog_drain_t += dt
            self._smog_flash    = 0.4
            if self._smog_drain_t >= 0.5:
                self._smog_drain_t = 0.0
                if self._nectar > 0:
                    self._nectar = max(0, self._nectar - 5)
                    self.ps.emit_pollen(px, py)
        else:
            self._smog_drain_t = 0.0
        self._smog_flash = max(0.0, self._smog_flash - dt)

        # Сбор обычных цветов
        for f in self.flowers:
            if not f.depleted and self._nectar < MAX_NECTAR:
                if math.dist((f.center_x, f.center_y), (px, py)) < 42:
                    got = f.harvest(10)
                    if got:
                        self._nectar = min(MAX_NECTAR, self._nectar + got)
                        self.ps.emit_pollen(f.center_x, f.center_y)
                        self._play(self._snd_coin)

        # Сбор золотых цветов
        for f in list(self.gold_flowers):
            if not f.depleted and self._nectar < MAX_NECTAR:
                if math.dist((f.center_x, f.center_y), (px, py)) < 42:
                    got = f.harvest(30)
                    if got:
                        self._nectar = min(MAX_NECTAR, self._nectar + got)
                        self.ps.emit_spark(f.center_x, f.center_y)
                        self.ps.emit_pollen(f.center_x, f.center_y)
                        self.score += 50
                        self._play(self._snd_coin)

        # Сдача в улей
        hd = math.dist((px, py), (self._hx, self._hy))
        if hd < 72 and self._nectar > 0:
            self._honey  += self._nectar
            self.score   += self._nectar * 15
            self._nectar  = 0
            self._play(self._snd_coin)

        # Победа: все цветы собраны
        all_done = (all(f.depleted for f in self.flowers)
                    and all(f.depleted for f in self.gold_flowers))
        if all_done:
            self.score += int(self._time) * 10
            self._level_done()
            return

        self._follow(px, py, WORLD, WORLD)

    def on_draw(self) -> None:
        import math
        import random as _r
        self.clear()
        self.background_color = _FBG[self.level - 1]

        with self.wcam.activate():
            # ── Фон: текстура поля — мягкая клетка тёмного тона ─────────────
            bg = _FBG[self.level - 1]
            tile = 120
            for xi in range(0, WORLD + tile, tile):
                for yi in range(0, WORLD + tile, tile):
                    shade = ((xi // tile + yi // tile) % 2) * 6
                    c = (bg[0]+shade, bg[1]+shade, bg[2]+shade)
                    arcade.draw_rectangle_filled(xi+tile//2, yi+tile//2,
                                                  tile, tile, c)

            # ── Трава — тонкие стебли с лёгкими изгибами ─────────────────────
            _r.seed(42 + self.level * 3)
            grass_palettes = [
                [(48, 110, 40, 90),(35, 90, 28, 75),(60, 130, 50, 80)],
                [(90, 82, 22, 80),(70, 65, 18, 70),(110, 95, 30, 85)],
                [(70, 45, 95, 80),(55, 35, 80, 70),(85, 55, 110, 85)],
            ]
            for _ in range(200):
                gx = _r.randint(0, WORLD)
                gy = _r.randint(0, WORLD)
                gh = _r.randint(10, 22)
                lean = _r.randint(-5, 5)
                col = _r.choice(grass_palettes[self.level-1])
                arcade.draw_line(gx, gy, gx+lean, gy+gh, col, 1)

            # ── Улей — детальный ──────────────────────────────────────────────
            hx, hy = self._hx, self._hy
            # Тень
            arcade.draw_ellipse_filled(hx+5, hy-8, 95, 30, (0, 0, 0, 50))
            # Основа
            arcade.draw_circle_filled(hx, hy, 46, (185, 140, 28))
            # Соты-узор
            for ring in range(4):
                r_ring = 12 + ring * 10
                n_cells = max(6, ring * 6)
                for ci in range(n_cells):
                    angle = 2 * math.pi * ci / n_cells
                    cx2 = hx + math.cos(angle) * r_ring
                    cy2 = hy + math.sin(angle) * r_ring
                    arcade.draw_circle_filled(cx2, cy2, 5,
                        (160, 115, 20, 90))
            # Контур и блик
            arcade.draw_circle_outline(hx, hy, 46, (220, 175, 50), 2)
            arcade.draw_circle_filled(hx-14, hy+14, 9, (235, 195, 80, 130))
            # Зона сдачи
            arcade.draw_circle_outline(hx, hy, 72, (200, 180, 50, 60), 2)
            arcade.draw_text("УЛЕЙ", hx, hy, (50, 30, 0), 13,
                             anchor_x="center", anchor_y="center", bold=True)

            # ── Зоны смога — объёмные, тревожные ─────────────────────────────
            for sz in self._smog_zones:
                r_sz = 90 + 8 * math.sin(sz.pulse)
                # Три слоя разной прозрачности
                arcade.draw_circle_filled(sz.x, sz.y, r_sz+22, (160,28,28,18))
                arcade.draw_circle_filled(sz.x, sz.y, r_sz+8,  (185,38,38,30))
                arcade.draw_circle_filled(sz.x, sz.y, r_sz,    (205,48,48,48))
                # Контур с пульсацией
                arcade.draw_circle_outline(sz.x, sz.y, r_sz, (220, 60, 60), 2)
                # Иконка опасности
                arcade.draw_text("☠", sz.x, sz.y, (220, 80, 80, 140), 18,
                                  anchor_x="center", anchor_y="center")

            # ── Цветы — красивые, не квадратики ──────────────────────────────
            petal_colors = [
                (200, 150, 230),  # лиловые (уровень 1)
                (230, 195, 40),   # жёлтые  (уровень 2)
                (165, 105, 235),  # фиолетовые (уровень 3)
            ]
            pc = petal_colors[self.level - 1]
            for f in self.flowers:
                if not f.depleted:
                    fx, fy = f.center_x, f.center_y
                    # 5 лепестков
                    for pi in range(5):
                        pa = 2 * math.pi * pi / 5
                        px2 = fx + math.cos(pa) * 10
                        py2 = fy + math.sin(pa) * 10
                        arcade.draw_ellipse_filled(px2, py2, 9, 12,
                                                    (*pc, 210))
                    # Серединка
                    arcade.draw_circle_filled(fx, fy, 6, (240, 220, 60))
                    arcade.draw_circle_outline(fx, fy, 6, (200, 180, 30), 1)
                    # Стебель
                    arcade.draw_line(fx, fy-6, fx, fy-20,
                                      (60, 140, 45), 2)
                else:
                    # Завявший цветок
                    arcade.draw_circle_filled(f.center_x, f.center_y, 5,
                                               (70, 65, 60, 130))

            # ── Золотые цветы — крупнее и ярче ───────────────────────────────
            for f in self.gold_flowers:
                if not f.depleted:
                    fx, fy = f.center_x, f.center_y
                    # Свечение
                    arcade.draw_circle_filled(fx, fy, 22, (255, 210, 40, 35))
                    for pi in range(6):
                        pa = 2 * math.pi * pi / 6
                        px2 = fx + math.cos(pa) * 13
                        py2 = fy + math.sin(pa) * 13
                        arcade.draw_ellipse_filled(px2, py2, 10, 14,
                                                    (250, 200, 30, 220))
                    arcade.draw_circle_filled(fx, fy, 7, (255, 240, 100))
                    arcade.draw_circle_outline(fx, fy, 7, (220, 180, 20), 1)
                    arcade.draw_line(fx, fy-7, fx+3, fy-22, (70, 155, 50), 2)
                    arcade.draw_text("★", fx, fy+22, (255, 220, 50), 11,
                                      anchor_x="center")

            self.ps.draw()

            # ── Игрок — Нектария, пчела-разведчица ───────────────────────────
            if self.player:
                p = self.player
                px3, py3 = p.center_x, p.center_y
                # Тень
                arcade.draw_ellipse_filled(px3+3, py3-10, 28, 8, (0,0,0,50))
                # Брюшко — полосатое
                arcade.draw_ellipse_filled(px3, py3, 26, 18,
                                            (220, 195, 30))
                for stripe in range(-8, 10, 8):
                    arcade.draw_line(px3+stripe, py3-8, px3+stripe, py3+8,
                                      (30, 22, 5), 3)
                # Голова
                arcade.draw_circle_filled(px3+13, py3+4, 9, (220, 195, 30))
                arcade.draw_circle_filled(px3+17, py3+6, 3, (20, 15, 5))
                # Крылья — нежно-голубые
                arcade.draw_ellipse_filled(
                    px3-6, py3+16, 24, 11, (190, 235, 255, 170))
                arcade.draw_ellipse_filled(
                    px3-4, py3+4,  20, 9,  (190, 235, 255, 140))
                # Жало
                arcade.draw_line(px3-13, py3, px3-20, py3-3,
                                  (180, 160, 30), 2)

                # ── ТУМАН ВОЙНЫ ──────────────────────────────────────
                r   = self._fog_r
                fbg = _FBG[self.level - 1]
                fog = (*fbg, 205)
                arcade.draw_rectangle_filled(
                    px3, py3 + r + 700, WORLD * 4, 1400, fog)
                arcade.draw_rectangle_filled(
                    px3, py3 - r - 700, WORLD * 4, 1400, fog)
                arcade.draw_rectangle_filled(
                    px3 - r - 1400, py3, 2800, r * 6, fog)
                arcade.draw_rectangle_filled(
                    px3 + r + 1400, py3, 2800, r * 6, fog)
                # Мягкое кольцо — несколько слоёв
                for ring in range(5):
                    arcade.draw_circle_outline(
                        px3, py3, r + ring * 16,
                        (*fbg, 90 - ring * 16), 22)

        with self.gcam.activate():
            arcade.draw_rectangle_filled(
                SCREEN_W//2, 24, SCREEN_W, 48, (12, 18, 10, 215))
            arcade.draw_line(0, 48, SCREEN_W, 48, (55, 100, 40, 100), 1)
            self._hud(f"Нектар: {self._nectar}/{MAX_NECTAR}")
            draw_bar(130, SCREEN_H-48, 200, 16,
                     self._time, _TIME[self.level-1],
                     fill=(70, 190, 90), label="Время")
            total = len(self.flowers) + len(self.gold_flowers)
            done  = (sum(1 for f in self.flowers if f.depleted)
                     + sum(1 for f in self.gold_flowers if f.depleted))
            arcade.draw_text(
                f"Цветов: {done}/{total}   Мёд: {self._honey}",
                SCREEN_W//2, 32, (200, 185, 55), 13, anchor_x="center",
            )
            if self._smog_flash > 0:
                self._txt_smog.text = "⚠ СМОГ! Нектар испаряется!"
                self._txt_smog.draw()
            arcade.draw_text(
                "WASD — полёт  |  подлети к цветку — нектар  "
                "|  ★ золотые = ×3  |  красные зоны — смог",
                SCREEN_W//2, 12, (140, 130, 70), 10, anchor_x="center",
            )
    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
