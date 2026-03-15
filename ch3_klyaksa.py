"""
ch3_klyaksa.py — Глава 3: Клякса — Художник-бунтарь
Шутер. Убей всех врагов — откроется финиш. Arcade 3.x px/кадр.
"""
from __future__ import annotations
import math
import arcade
from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, C_KLYAKSA
from sprites import InkBullet, WalkingEnemy
from utils import parse_map

GRAVITY = 0.8
SPEED   = 5
JUMP_V  = 14

_MAPS = [
    # Уровень 1 — три этажа, проходы справа→слева
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P            E              E        W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W     E       E           E             W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    E           E         E            W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # Уровень 2 — четыре этажа
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P         E              E           W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W    E    E       E        E            W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    E       E       E       E          W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W    E    E       E     E    E          W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # Уровень 3 — пять этажей, тесно
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P      E    E      E     E           W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W   E   E    E      E     E    E        W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    E      E    E     E     E          W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W     E   E     E     E    E   E        W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W   E    E      E   E     E    E        W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
]


class Chapter3View(BaseChapter):

    def __init__(self, chapter_num: int = 3) -> None:
        super().__init__(chapter_num)
        self.player   = None
        self.walls    = arcade.SpriteList()
        self.enemies  = arcade.SpriteList()
        self.bullets  = arcade.SpriteList()
        self.finish   = None
        self._finish_sl = arcade.SpriteList()
        self.engine   = None
        self._ww = self._wh = 0.0
        self._cd = 0.0
        self._total = self._killed = 0
        self._finish_open = False
        self._snd_shoot = self._snd(":resources:sounds/hurt2.wav")
        self._txt_hint = arcade.Text("", SCREEN_W // 2, SCREEN_H - 55,
                                     (200, 180, 255), 14, anchor_x="center")

    def setup(self) -> None:
        self.ps.clear()
        self.bullets.clear()
        self.enemies.clear()
        self._cd = 0.0
        self._killed = 0
        self._finish_open = False

        md = _MAPS[self.level - 1]
        self._ww = max(len(r) for r in md) * TS
        self._wh = len(md) * TS

        walls, _sp, coll, emark, pp, _fp = parse_map(md)
        self.walls = walls
        self.finish = None
        self._finish_sl = arcade.SpriteList()
        for s in coll:
            if getattr(s, "name", "") == "finish":
                self.finish = s
                self._finish_sl.append(s)

        for m in emark:
            self.enemies.append(WalkingEnemy(m.center_x, m.center_y))
        self._total = len(self.enemies)

        self.player = arcade.SpriteSolidColor(28, 44, C_KLYAKSA)
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

        self._cd -= dt
        self.engine.update()
        self.ps.update(dt)

        for e in self.enemies:
            e.on_update(dt)

        for b in list(self.bullets):
            b.on_update(dt)
            if (b.center_x < -50 or b.center_x > self._ww + 50
                    or b.center_y < -50 or b.center_y > self._wh + 50):
                b.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(b, self.walls):
                self.ps.emit_ink(b.center_x, b.center_y)
                b.remove_from_sprite_lists()
                continue
            for e in arcade.check_for_collision_with_list(b, self.enemies):
                self.ps.emit_ink(e.center_x, e.center_y)
                e.remove_from_sprite_lists()
                b.remove_from_sprite_lists()
                self._killed += 1
                self.score += 100
                self._play(self._snd_shoot)

        self._finish_open = (self._killed >= self._total)

        if (self._can_finish() and self._finish_open and self.finish
                and arcade.check_for_collision(self.player, self.finish)):
            self.score += 300
            self._level_done()
            return

        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     self._ww, self._wh)

    def on_draw(self) -> None:
        self.clear()
        self.background_color = (30, 18, 45)

        with self.wcam.activate():
            self.walls.draw()
            self.enemies.draw()
            self.bullets.draw()
            if self._finish_open:
                self._finish_sl.draw()
                if self.finish:
                    arcade.draw_circle_outline(
                        self.finish.center_x, self.finish.center_y,
                        35, (100, 255, 140), 3,
                    )
            self.ps.draw()
            if self.player:
                p = self.player
                arcade.draw_rectangle_filled(
                    p.center_x, p.center_y, 28, 44, C_KLYAKSA)
                arcade.draw_rectangle_filled(
                    p.center_x + 20, p.center_y + 6, 22, 8, (80, 20, 130))

        with self.gcam.activate():
            self._hud(f"Враги: {self._killed}/{self._total}")
            if not self._finish_open:
                self._txt_hint.text = (
                    f"Убей всех врагов! Осталось: {self._total - self._killed}"
                )
                self._txt_hint.draw()
            arcade.draw_text(
                "WASD — движение  |  ЛКМ — стрелять чернилами",
                SCREEN_W // 2, 12, (160, 130, 200), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT or not self.player or self._cd > 0:
            return
        self._cd = 0.22
        cam_x, cam_y = self.wcam.position
        wx = x + cam_x - SCREEN_W / 2
        wy = y + cam_y - SCREEN_H / 2
        angle = math.atan2(wy - self.player.center_y,
                           wx - self.player.center_x)
        b = InkBullet(
            self.player.center_x + math.cos(angle) * 22,
            self.player.center_y + math.sin(angle) * 22,
            angle,
        )
        self.bullets.append(b)
        self.ps.emit_ink(self.player.center_x, self.player.center_y)
        self._play(self._snd_shoot)
