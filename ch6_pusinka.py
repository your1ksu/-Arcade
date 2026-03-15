"""
ch6_pusinka.py — Глава 6: Пушинка — Облачный зайчик
Вертикальный платформер. px/кадр физика. Arcade 3.x.
"""
from __future__ import annotations
import random
import arcade
from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, C_PUSINKA, C_CARROT
from sprites import CloudPlatform

GRAVITY = 0.7
SPEED   = 5
JUMP_V  = 14
DJUMP_V = 13

_WH = [2400, 3200, 4000]
_CARROTS_TARGET = [10, 14, 18]


def _build(lv: int) -> tuple:
    random.seed(lv * 7 + 42)
    wh = _WH[lv]
    walls = arcade.SpriteList(use_spatial_hash=True)
    clouds: list = []
    cloud_sl = arcade.SpriteList()
    carrots = arcade.SpriteList()

    # Пол
    for cx in range(0, SCREEN_W + TS, TS):
        g = arcade.SpriteSolidColor(TS, TS, (60, 80, 100))
        g.center_x, g.center_y = cx, TS // 2
        walls.append(g)

    fx = random.randint(200, SCREEN_W - 200)
    fy = wh - 80

    y = 220
    sect = 0
    while y < wh - 200:
        x = random.randint(80, SCREEN_W - 80)
        w = random.randint(90, 210)
        if sect % 3 == 0:
            p = arcade.SpriteSolidColor(w, 18, (180, 200, 220))
            p.center_x, p.center_y = x, y
            walls.append(p)
        else:
            bl = max(40, x - 150)
            br = min(SCREEN_W - 40, x + 150)
            # Скорость облака в px/кадр
            spd = random.uniform(0.5, 1.5)
            if random.random() < 0.5:
                spd = -spd
            cp = CloudPlatform(x, y, w, bl, br, spd)
            clouds.append(cp)
            cloud_sl.append(cp)
        if random.random() < 0.55 and len(carrots) < _CARROTS_TARGET[lv]:
            c = arcade.SpriteSolidColor(18, 28, C_CARROT)
            c.center_x = x + random.randint(-30, 30)
            c.center_y = y + 30
            carrots.append(c)
        y += random.randint(90, 160)
        sect += 1

    return walls, clouds, cloud_sl, carrots, (SCREEN_W // 2, TS * 2), (fx, fy)


class Chapter6View(BaseChapter):

    def __init__(self, chapter_num: int = 6) -> None:
        super().__init__(chapter_num)
        self.player  = None
        self.walls   = arcade.SpriteList()
        self._clouds: list = []
        self._csl    = arcade.SpriteList()
        self.carrots = arcade.SpriteList()
        self.engine  = None
        self._dj     = True
        self._jonce  = False
        self._wh     = 0.0
        self._fx = self._fy = 0.0
        self._got = 0

    def setup(self) -> None:
        self.ps.clear()
        self._got = 0
        self._dj  = True
        self._jonce = False
        lv = self.level - 1
        self._wh = _WH[lv]
        (self.walls, self._clouds, self._csl,
         self.carrots, pp, fp) = _build(lv)
        self._fx, self._fy = fp

        self.player = arcade.SpriteSolidColor(28, 34, C_PUSINKA)
        self.player.center_x, self.player.center_y = pp[0], pp[1]
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.walls,
            gravity_constant=GRAVITY,
            platforms=self._csl,
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

        if self.engine.can_jump():
            self._dj    = True
            self._jonce = False

        # Облака двигаются в px/кадр (update без dt)
        for cp in self._clouds:
            cp.update()

        self.engine.update()
        self.ps.update(dt)

        for c in arcade.check_for_collision_with_list(self.player, self.carrots):
            c.remove_from_sprite_lists()
            self._got += 1
            self.score += 40
            self._play(self._snd_coin)

        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        import math
        d = math.sqrt((self.player.center_x - self._fx) ** 2
                       + (self.player.center_y - self._fy) ** 2)
        if self._can_finish() and d < 80:
            self.score += 400 + self._got * 10
            self._level_done()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     SCREEN_W, self._wh)

    def on_draw(self) -> None:
        self.clear()
        self.background_color = (100, 140, 200)
        with self.wcam.activate():
            arcade.draw_circle_filled(self._fx, self._fy, 30, (80, 220, 120))
            arcade.draw_text("★", self._fx, self._fy, (255, 255, 255), 24,
                             anchor_x="center", anchor_y="center")
            self.walls.draw()
            self._csl.draw()
            self.carrots.draw()
            self.ps.draw()
            if self.player:
                p = self.player
                arcade.draw_ellipse_filled(
                    p.center_x, p.center_y, 28, 32, C_PUSINKA)
                arcade.draw_ellipse_filled(
                    p.center_x - 7, p.center_y + 20, 8, 14, C_PUSINKA)
                arcade.draw_ellipse_filled(
                    p.center_x + 7, p.center_y + 20, 8, 14, C_PUSINKA)
                arcade.draw_circle_filled(
                    p.center_x - 5, p.center_y + 5, 3, (60, 40, 80))
                arcade.draw_circle_filled(
                    p.center_x + 5, p.center_y + 5, 3, (60, 40, 80))
        with self.gcam.activate():
            self._hud(f"Морковок: {self._got}")
            arcade.draw_text(
                "WASD/стрелки — движение  |  ПРОБЕЛ/W/↑ — прыжок (двойной!)",
                SCREEN_W // 2, 12, (200, 190, 220), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.player:
                if self.engine.can_jump():
                    self.player.change_y = JUMP_V
                    self._jonce = True
                    self._play(self._snd_jump)
                elif self._dj and self._jonce:
                    self.player.change_y = DJUMP_V
                    self._dj = False
                    self.ps.emit_rainbow(
                        self.player.center_x, self.player.center_y)
                    self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
        if (key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE)
                and self.player and self.player.change_y > 0):
            self.player.change_y *= 0.45
