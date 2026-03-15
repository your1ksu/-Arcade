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
        self.clear()
        self.background_color = _FIELD_BG[self.level - 1]

        with self.wcam.activate():
            # Улей
            arcade.draw_circle_filled(self._hive_x, self._hive_y, 42, C_HIVE)
            arcade.draw_text("УЛЕЙ", self._hive_x, self._hive_y,
                             (60, 40, 0), 12,
                             anchor_x="center", anchor_y="center", bold=True)
            # Зона сдачи
            arcade.draw_circle_outline(self._hive_x, self._hive_y, 72,
                                       (220, 200, 60, 80), 2)

            self.flowers.draw()
            self.wasps.draw()
            self.stingers.draw()
            self.ps.draw()

            if self.player:
                p = self.player
                arcade.draw_circle_filled(p.center_x, p.center_y, 17, C_MELISSA)
                arcade.draw_ellipse_filled(
                    p.center_x - 14, p.center_y + 6, 14, 8, (200, 230, 255, 160))
                arcade.draw_ellipse_filled(
                    p.center_x + 14, p.center_y + 6, 14, 8, (200, 230, 255, 160))

        with self.gcam.activate():
            self._hud(f"Нектар: {self._nectar}/{MAX_NECTAR_M}")
            draw_bar(130, SCREEN_H - 48, 200, 16,
                     self._hive_hp, HIVE_HP, fill=C_HIVE, label="Улей")
            goal = _HONEY_GOAL[self.level - 1]
            self._txt_goal.text = (f"Мёд: {self._honey}/{goal}  "
                                   f"({'✓ Лети в улей!' if self._nectar > 0 else ''})")
            self._txt_goal.draw()
            arcade.draw_text(
                "WASD — полёт  |  ПРОБЕЛ — жало  |  подлети к цветку — нектар  "
                "|  улей — сдать",
                SCREEN_W // 2, 12, (160, 150, 100), 11, anchor_x="center",
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
