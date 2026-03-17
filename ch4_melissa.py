"""
ch4_melissa.py — Глава 4: Мелисса — Королева-пчела
Вид сверху. Собирай нектар с цветов и относи в улей.
Осы летят к улью — отстреливай их жалом (ПРОБЕЛ).
Цель: набери нужное количество мёда. Arcade 3.x.
"""
from __future__ import annotations
import math, random
import arcade
from base_chapter import BaseChapter
from constants import (
    SCREEN_W, SCREEN_H, TS,
    MAX_NECTAR_M, HIVE_HP, WASP_DMG,
    C_MELISSA, C_HIVE,
)
from sprites import Wasp, Stinger, Flower
from utils import draw_bar

WORLD = 1400
SPD   = 240.0

_FIELD_BG   = [(38, 68, 30), (50, 78, 18), (55, 42, 18)]
_FLOWER_CNT = [14, 18, 24]
_WASP_INT   = [3.5, 2.8, 2.0]
_WASP_MAX   = [5, 8, 12]
_HONEY_GOAL = [120, 180, 250]


class Chapter4View(BaseChapter):

    def __init__(self, chapter_num: int = 4) -> None:
        super().__init__(chapter_num)
        self.player   = None
        self.flowers  = arcade.SpriteList()
        self.wasps    = arcade.SpriteList()
        self.stingers = arcade.SpriteList()
        self._nectar  = 0
        self._honey   = 0
        self._hive_hp = HIVE_HP
        self._hive_x  = WORLD / 2
        self._hive_y  = WORLD - 120.0
        self._wt      = 0.0
        self._scd     = 0.0
        self._snd_sting = self._snd(":resources:sounds/hurt2.wav")
        self._txt_goal = arcade.Text("", SCREEN_W // 2, 32,
                                     (220, 200, 60), 13, anchor_x="center")

    def setup(self) -> None:
        self._nectar = 0
        self._honey  = 0
        self._hive_hp = HIVE_HP
        self._wt = self._scd = 0.0
        self.ps.clear()
        self.wasps.clear()
        self.stingers.clear()
        self.flowers.clear()

        random.seed(self.level * 17)
        for _ in range(_FLOWER_CNT[self.level - 1]):
            f = Flower(random.uniform(100, WORLD - 100),
                       random.uniform(80, WORLD - 320))
            self.flowers.append(f)

        self.player = arcade.SpriteSolidColor(34, 34, C_MELISSA)
        self.player.center_x = WORLD / 2
        self.player.center_y = 120.0

    def on_update(self, dt: float) -> None:
        if not self.player:
            return
        self._tick_grace(dt)
        self._scd -= dt

        vx, vy = 0.0, 0.0
        if arcade.key.LEFT  in self.keys or arcade.key.A in self.keys: vx = -SPD
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys: vx = SPD
        if arcade.key.UP   in self.keys or arcade.key.W in self.keys: vy = SPD
        elif arcade.key.DOWN in self.keys or arcade.key.S in self.keys: vy = -SPD

        self.player.center_x = max(20, min(WORLD - 20, self.player.center_x + vx * dt))
        self.player.center_y = max(20, min(WORLD - 20, self.player.center_y + vy * dt))

        self.ps.update(dt)

        # Сбор нектара
        for f in self.flowers:
            if not f.depleted:
                d = math.dist((f.center_x, f.center_y),
                               (self.player.center_x, self.player.center_y))
                if d < 42 and self._nectar < MAX_NECTAR_M:
                    got = f.harvest(10)
                    if got:
                        self._nectar = min(MAX_NECTAR_M, self._nectar + got)
                        self.ps.emit_pollen(f.center_x, f.center_y)
                        self._play(self._snd_coin)

        # Сдача нектара в улей
        hd = math.dist((self.player.center_x, self.player.center_y),
                        (self._hive_x, self._hive_y))
        if hd < 72 and self._nectar > 0:
            self._honey += self._nectar
            self.score += self._nectar * 20
            self._nectar = 0
            self._play(self._snd_coin)

        # Спавн ос
        self._wt += dt
        if (self._wt >= _WASP_INT[self.level - 1]
                and len(self.wasps) < _WASP_MAX[self.level - 1]):
            self._wt = 0.0
            side = random.choice(["t", "b", "l", "r"])
            if   side == "t": wx, wy = random.uniform(50, WORLD - 50), WORLD - 30
            elif side == "b": wx, wy = random.uniform(50, WORLD - 50), 30.0
            elif side == "l": wx, wy = 30.0, random.uniform(100, WORLD - 100)
            else:              wx, wy = WORLD - 30.0, random.uniform(100, WORLD - 100)
            self.wasps.append(Wasp(wx, wy))

        for w in self.wasps:
            w.set_target(self._hive_x, self._hive_y)
            w.on_update(dt)

        # Жала vs осы
        for st in list(self.stingers):
            st.on_update(dt)
            if (st.center_x < 0 or st.center_x > WORLD
                    or st.center_y < 0 or st.center_y > WORLD):
                st.remove_from_sprite_lists();  continue
            for w in arcade.check_for_collision_with_list(st, self.wasps):
                self.ps.emit_pollen(w.center_x, w.center_y)
                w.remove_from_sprite_lists()
                st.remove_from_sprite_lists()
                self.score += 80
                self._play(self._snd_sting)

        # Осы достигают улья
        for w in list(self.wasps):
            wd = math.dist((w.center_x, w.center_y), (self._hive_x, self._hive_y))
            if wd < 48:
                self._hive_hp -= WASP_DMG
                w.remove_from_sprite_lists()
                self._play(self._snd_hurt)
                if self._hive_hp <= 0:
                    self._game_over();  return

        # Победа
        if self._honey >= _HONEY_GOAL[self.level - 1]:
            self.score += self._honey
            self._level_done();  return

        self._follow(self.player.center_x, self.player.center_y, WORLD, WORLD)

    def on_draw(self) -> None:
        import random as _rnd
        self.clear()
        self.background_color = _FIELD_BG[self.level - 1]

        with self.wcam.activate():
            # ── Травяное поле — мягкие пятна и стебли ───────────────────────
            WORLD_L = 1200
            grass_tints = [
                (45, 85, 38, 55), (65, 58, 14, 50), (50, 38, 68, 50),
            ]
            gt = grass_tints[self.level - 1]
            _rnd.seed(self.level * 7)
            for _ in range(80):
                gx = _rnd.randint(0, WORLD_L)
                gy = _rnd.randint(0, WORLD_L)
                gr = _rnd.randint(18, 45)
                arcade.draw_circle_filled(gx, gy, gr, gt)
            # Стебли
            for _ in range(160):
                sx = _rnd.randint(0, WORLD_L)
                sy = _rnd.randint(0, WORLD_L)
                sh = _rnd.randint(12, 30)
                col = _rnd.choice([
                    (55, 110, 42, 80), (70, 130, 50, 70), (45, 90, 35, 90),
                ])
                arcade.draw_line(sx, sy, sx + _rnd.randint(-5, 5), sy + sh,
                                 col, 1)

            # ── Улей — детальный ─────────────────────────────────────────────
            hx, hy = self._hive_x, self._hive_y
            # Тень
            arcade.draw_ellipse_filled(hx + 5, hy - 38, 70, 16, (0, 0, 0, 60))
            # Подставка
            arcade.draw_rectangle_filled(hx, hy - 40, 60, 10, (110, 80, 18))
            # Купол
            arcade.draw_circle_filled(hx, hy, 42, C_HIVE)
            # Сотовые соты
            for i in range(6):
                a = math.radians(60 * i)
                hx2 = hx + math.cos(a) * 18
                hy2 = hy + math.sin(a) * 18
                pts = [(hx2 + 9*math.cos(math.radians(60*i)),
                         hy2 + 9*math.sin(math.radians(60*i))) for i in range(6)]
                arcade.draw_polygon_filled(pts, (195, 148, 18))
            pts = [(hx + 9*math.cos(math.radians(60*i)),
                    hy + 9*math.sin(math.radians(60*i))) for i in range(6)]
            arcade.draw_polygon_filled(pts, (195, 148, 18))
            # Ободок и зона сдачи
            arcade.draw_circle_outline(hx, hy, 42, (240, 200, 50), 2)
            arcade.draw_circle_outline(hx, hy, 72, (220, 200, 55, 90), 2)
            arcade.draw_text("УЛЕЙ", hx, hy, (45, 30, 0), 13,
                             anchor_x="center", anchor_y="center", bold=True)

            # ── Цветки — лепестки ─────────────────────────────────────────────
            field_flower_colors = [
                (200, 140, 220),   # весна — сиреневый
                (240, 195, 35),    # лето — жёлтый
                (220, 120, 70),    # осень — рыжий
            ]
            fc = field_flower_colors[self.level - 1]
            for f in self.flowers:
                if not f.depleted:
                    fx2, fy2 = f.center_x, f.center_y
                    arcade.draw_line(fx2, fy2 - 14, fx2, fy2 - 28,
                                     (55, 120, 40), 2)
                    for i in range(5):
                        a = math.radians(72 * i)
                        arcade.draw_circle_filled(
                            fx2 + math.cos(a) * 9,
                            fy2 + math.sin(a) * 9, 6, fc)
                    arcade.draw_circle_filled(fx2, fy2, 5, (255, 240, 80))
                else:
                    arcade.draw_circle_filled(
                        f.center_x, f.center_y, 5, (80, 70, 55))

            # ── Осы — детальные ──────────────────────────────────────────────
            for w in self.wasps:
                wx, wy = w.center_x, w.center_y
                # Тельце с полосками
                arcade.draw_ellipse_filled(wx, wy, 30, 16, (190, 50, 50))
                for i in range(3):
                    bx2 = wx - 8 + i * 8
                    arcade.draw_line(bx2, wy - 7, bx2, wy + 7,
                                     (20, 14, 0, 160), 3)
                # Крылья
                arcade.draw_ellipse_filled(
                    wx - 10, wy + 10, 16, 7, (200, 225, 255, 150))
                arcade.draw_ellipse_filled(
                    wx + 10, wy + 10, 16, 7, (200, 225, 255, 150))
                # Глаз
                arcade.draw_circle_filled(wx + 10, wy + 3, 3, (255, 60, 60))

            self.stingers.draw()
            self.ps.draw()

            # ── Мелисса — детальная ──────────────────────────────────────────
            if self.player:
                p = self.player
                px2, py2 = p.center_x, p.center_y
                # Тень
                arcade.draw_ellipse_filled(
                    px2 + 3, py2 - 3, 28, 10, (0, 0, 0, 60))
                # Тело
                arcade.draw_ellipse_filled(px2, py2, 28, 22, C_MELISSA)
                # Полоски — чёрные
                for i in range(3):
                    bx2 = px2 - 8 + i * 8
                    arcade.draw_line(bx2, py2 - 10, bx2, py2 + 10,
                                     (30, 20, 0), 3)
                # Крылья
                arcade.draw_ellipse_filled(
                    px2 - 16, py2 + 10, 20, 10, (215, 240, 255, 170))
                arcade.draw_ellipse_filled(
                    px2 + 16, py2 + 10, 20, 10, (215, 240, 255, 170))
                arcade.draw_ellipse_outline(
                    px2 - 16, py2 + 10, 20, 10, (180, 220, 255, 120), 1)
                arcade.draw_ellipse_outline(
                    px2 + 16, py2 + 10, 20, 10, (180, 220, 255, 120), 1)
                # Корона
                for i in range(3):
                    cx3 = px2 - 6 + i * 6
                    arcade.draw_triangle_filled(
                        cx3 - 3, py2 + 14,
                        cx3 + 3, py2 + 14,
                        cx3, py2 + 20,
                        (240, 200, 30))
                # Глаз
                arcade.draw_circle_filled(px2 + 9, py2 + 5, 3, (30, 20, 0))
                arcade.draw_circle_filled(px2 + 10, py2 + 6, 1, (255, 255, 255))

        with self.gcam.activate():
            bg_hud = tuple(max(0, c - 20) for c in _FIELD_BG[self.level - 1])
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (*bg_hud, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (140, 120, 40, 120), 1)
            self._hud(f"Нектар: {self._nectar}/{MAX_NECTAR_M}")
            draw_bar(130, SCREEN_H - 48, 200, 16,
                     self._hive_hp, HIVE_HP, fill=C_HIVE, label="Улей")
            goal = _HONEY_GOAL[self.level - 1]
            self._txt_goal.text = (f"Мёд: {self._honey}/{goal}  "
                                   f"({'✓ Лети в улей!' if self._nectar > 0 else ''})")
            self._txt_goal.draw()
            arcade.draw_text(
                "WASD — полёт  |  ПРОБЕЛ — жало (авто)  "
                "|  подлети к цветку — нектар  |  улей — сдать",
                SCREEN_W // 2, 12, (150, 135, 80), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key == arcade.key.SPACE and self._scd <= 0 and self.player:
            self._scd = 0.30
            # Ищем ближайшую осу
            nearest, md = None, 9999.0
            for w in self.wasps:
                d = math.dist((w.center_x, w.center_y),
                               (self.player.center_x, self.player.center_y))
                if d < md:
                    md, nearest = d, w
            if nearest:
                angle = math.atan2(nearest.center_y - self.player.center_y,
                                   nearest.center_x - self.player.center_x)
            else:
                angle = 0.0
            self.stingers.append(
                Stinger(self.player.center_x, self.player.center_y, angle)
            )

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
