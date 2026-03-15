"""
ch2_viks.py — Глава 2: Сэр Викс — Свечной Рыцарь
PhysicsEnginePlatformer px/кадр. Arcade 3.x.
"""
from __future__ import annotations
import math, random
import arcade
from base_chapter import BaseChapter
from constants import (
    SCREEN_W, SCREEN_H, TS,
    MAX_CANDLE, CANDLE_DRAIN, GUST_DRAIN, OIL_HEAL, LIGHT_R_MAX,
    C_VIKS, C_OIL,
)
from sprites import ShadowEnemy, LightAura
from utils import parse_map, draw_bar

GRAVITY = 0.8
SPEED   = 5
JUMP_V  = 14

# Легенда: W=стена  P=старт  F=финиш  O=масло  E=враг-тень
# Все горизонтальные стены имеют проход (8 пустых тайлов).
# Проходы чередуются справа / слева для зигзага вниз.
_MAPS = [
    # ── Уровень 1 — три этажа, проходы справа → слева ─────────────────────────
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P     O              O               W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",  # проход справа
        "W                                       W",
        "W     O      E       O        E         W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # проход слева
        "W                                       W",
        "W      O      E     O      E    O       W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # ── Уровень 2 — четыре этажа, зигзаг ──────────────────────────────────────
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P   O              O                 W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",  # проход справа
        "W                                       W",
        "W   O     E    E      O        E        W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # проход слева
        "W                                       W",
        "W     O        O     E     O            W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",  # проход справа
        "W                                       W",
        "W      O    E     O      E    O         W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # ── Уровень 3 — пять этажей, гуще тени ────────────────────────────────────
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P  O               O                 W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",  # проход справа
        "W                                       W",
        "W    O   E   E    O   E     O    E      W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # проход слева
        "W                                       W",
        "W   O        O       E    O      E      W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",  # проход справа
        "W                                       W",
        "W      O    E     O         O    E      W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # проход слева
        "W                                       W",
        "W    O   E      O      E     O          W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
]


class Chapter2View(BaseChapter):

    def __init__(self, chapter_num: int = 2) -> None:
        super().__init__(chapter_num)
        self.candle: float = MAX_CANDLE
        self.player   = None
        self.walls    = arcade.SpriteList()
        self.oils     = arcade.SpriteList()
        self.enemies  = arcade.SpriteList()
        self.finish   = None
        self._finish_sl = arcade.SpriteList()
        self.engine   = None
        self._aura    = LightAura(LIGHT_R_MAX)
        self._gust_t  = 0.0
        self._flame_t = 0.0
        self._ww = self._wh = 0.0
        self._txt_warn = arcade.Text("", SCREEN_W // 2, 40,
                                     (255, 120, 30), 18,
                                     anchor_x="center", bold=True)

    def setup(self) -> None:
        self.candle = MAX_CANDLE
        self.ps.clear()
        self.enemies.clear()
        self._gust_t = self._flame_t = 0.0

        md = _MAPS[self.level - 1]
        self._ww = max(len(r) for r in md) * TS
        self._wh = len(md) * TS

        walls, _sp, coll, emark, pp, _fp = parse_map(md)
        self.walls = walls
        self.oils  = arcade.SpriteList()
        self.finish = None
        self._finish_sl = arcade.SpriteList()

        for s in coll:
            if getattr(s, "name", "") == "finish":
                self.finish = s
                self._finish_sl.append(s)
            else:
                s.color = C_OIL
                self.oils.append(s)

        for m in emark:
            self.enemies.append(ShadowEnemy(m.center_x, m.center_y))

        self.player = arcade.SpriteSolidColor(28, 44, C_VIKS)
        self.player.center_x, self.player.center_y = pp[0], pp[1]
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.walls, gravity_constant=GRAVITY,
        )

    def on_update(self, dt: float) -> None:
        if not self.player or not self.engine:
            return
        self._tick_grace(dt)

        if arcade.key.LEFT in self.keys or arcade.key.A in self.keys:
            self.player.change_x = -SPEED
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys:
            self.player.change_x = SPEED
        else:
            self.player.change_x = 0

        self.engine.update()
        self.ps.update(dt)

        self.candle -= CANDLE_DRAIN * dt

        self._gust_t += dt
        if self._gust_t >= max(3.0, 8.0 - self.level * 1.5):
            self._gust_t = 0.0
            self.candle -= GUST_DRAIN
            for _ in range(3):
                self.ps.emit_wind(
                    self.player.center_x + random.uniform(-80, 80),
                    self.player.center_y,
                )

        self._flame_t += dt
        if self._flame_t >= 0.12:
            self._flame_t = 0.0
            self.ps.emit_flame(self.player.center_x, self.player.center_y + 28)

        if self.candle <= 0:
            self._game_over()
            return

        lr = int(LIGHT_R_MAX * self.candle / MAX_CANDLE)
        self._aura.set_radius(max(30, lr))
        self._aura.center_x = self.player.center_x
        self._aura.center_y = self.player.center_y

        for e in self.enemies:
            d = math.sqrt((e.center_x - self.player.center_x) ** 2
                           + (e.center_y - self.player.center_y) ** 2)
            e.frozen = d < lr
            e.on_update(dt)

        for oil in arcade.check_for_collision_with_list(self.player, self.oils):
            self.candle = min(MAX_CANDLE, self.candle + OIL_HEAL)
            self.score += 60
            oil.remove_from_sprite_lists()
            self._play(self._snd_coin)

        if arcade.check_for_collision_with_list(self.player, self.enemies):
            self.candle -= 10.0 * dt

        if (self._can_finish() and self.finish
                and arcade.check_for_collision(self.player, self.finish)):
            self.score += 300 + int(self.candle)
            self._level_done()
            return

        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     self._ww, self._wh)

    def on_draw(self) -> None:
        self.clear()
        self.background_color = (6, 4, 14)
        lr = int(LIGHT_R_MAX * self.candle / MAX_CANDLE)

        with self.wcam.activate():
            self.walls.draw()
            self.oils.draw()
            self._finish_sl.draw()
            if self.player:
                # Рисуем только врагов в зоне света через SpriteList
                visible_enemies = arcade.SpriteList()
                for e in self.enemies:
                    d = math.sqrt((e.center_x - self.player.center_x) ** 2
                                   + (e.center_y - self.player.center_y) ** 2)
                    if d < lr + 20:
                        visible_enemies.append(e)
                visible_enemies.draw()
                self._aura.draw()
                self.ps.draw()
                p = self.player
                arcade.draw_rectangle_filled(
                    p.center_x, p.center_y, 28, 44, C_VIKS)
                arcade.draw_circle_filled(
                    p.center_x, p.center_y + 26, 7, (245, 165, 40))

        with self.gcam.activate():
            self._hud()
            draw_bar(130, SCREEN_H - 48, 200, 16,
                     self.candle, MAX_CANDLE,
                     fill=(245, 165, 40), label="Свеча")
            if self.candle < 25:
                self._txt_warn.text = "Свеча гаснет!"
                self._txt_warn.draw()
            arcade.draw_text(
                "WASD/стрелки — движение  |  O — масло (+30)  "
                "|  Враги и ветер гасят свечу",
                SCREEN_W // 2, 12, (140, 120, 80), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
