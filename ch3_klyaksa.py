"""
ch3_klyaksa.py — Глава 3: Клякса — Художник-бунтарь
Шутер с видом сбоку.
Враги (серые роботы):
  - патрулируют горизонталь
  - при виде игрока (дистанция < AGGRO_RANGE) — преследуют
  - периодически стреляют серыми снарядами в сторону игрока
  - касание с игроком → -1 жизнь
Игрок стреляет чернилами мышью (ЛКМ).
Убей всех врагов → откроется финиш (зелёный портал).
Arcade 3.x, физика px/кадр.
"""
from __future__ import annotations

import math
import random

import arcade

from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, C_KLYAKSA
from sprites import InkBullet
from utils import parse_map, draw_bar

# ── Физика (px/кадр) ──────────────────────────────────────────────────────────
GRAVITY = 0.8
SPEED   = 5
JUMP_V  = 14

# ── Параметры врагов ──────────────────────────────────────────────────────────
PATROL_SPD   = 1.5    # px/кадр, патруль
CHASE_SPD    = 3.0    # px/кадр, преследование
AGGRO_RANGE  = 260    # px — дальность обнаружения игрока
SHOOT_RANGE  = 320    # px — дальность стрельбы
SHOOT_CD     = 2.2    # секунд между выстрелами
ENEMY_BULLET_SPD = 6  # px/кадр скорость серого снаряда

# ── Жизни игрока ──────────────────────────────────────────────────────────────
MAX_LIVES   = 3
HURT_CD     = 1.2     # секунд неуязвимости после получения урона

# ── Карты ─────────────────────────────────────────────────────────────────────
_MAPS = [
    # Уровень 1 — три этажа
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
    # Уровень 3 — пять этажей
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


# ── Класс врага ───────────────────────────────────────────────────────────────
class GreyRobot(arcade.SpriteSolidColor):
    """
    Серый робот: патрулирует горизонталь, при виде игрока
    преследует и периодически стреляет.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(36, 46, (75, 75, 85))
        self.center_x, self.center_y = x, y
        self._ox = x
        self._dir = 1.0
        self._patrol = TS * 3
        self._shoot_t: float = random.uniform(0.5, SHOOT_CD)
        self.aggroed: bool = False

    def move_toward_player(self, px: float, py: float, dt: float) -> None:
        """Преследует игрока по X."""
        dx = px - self.center_x
        spd = CHASE_SPD if self.aggroed else PATROL_SPD
        if abs(dx) > 4:
            self._dir = 1.0 if dx > 0 else -1.0
        self.center_x += self._dir * spd

    def patrol(self) -> None:
        """Стандартный патруль."""
        self.center_x += self._dir * PATROL_SPD
        if abs(self.center_x - self._ox) >= self._patrol:
            self._dir *= -1


class EnemyBullet(arcade.SpriteSolidColor):
    """Серый снаряд врага."""

    def __init__(self, x: float, y: float, angle: float) -> None:
        super().__init__(14, 8, (160, 160, 170))
        self.center_x, self.center_y = x, y
        self._vx = math.cos(angle) * ENEMY_BULLET_SPD
        self._vy = math.sin(angle) * ENEMY_BULLET_SPD
        self.angle_deg = math.degrees(angle)

    def on_update(self, dt: float = 1 / 60) -> None:
        self.center_x += self._vx
        self.center_y += self._vy


# ── Основной вид ──────────────────────────────────────────────────────────────
class Chapter3View(BaseChapter):

    def __init__(self, chapter_num: int = 3) -> None:
        super().__init__(chapter_num)
        self.player        = None
        self.walls         = arcade.SpriteList()
        self.enemies: list[GreyRobot] = []
        self._enemy_sl     = arcade.SpriteList()
        self.p_bullets     = arcade.SpriteList()   # чернила игрока
        self.e_bullets     = arcade.SpriteList()   # снаряды врагов
        self.finish        = None
        self._finish_sl    = arcade.SpriteList()
        self.engine        = None

        self._ww = self._wh = 0.0
        self._shoot_cd  = 0.0    # кулдаун выстрела игрока
        self._total     = 0
        self._killed    = 0
        self._finish_open = False

        self._lives     = MAX_LIVES
        self._hurt_cd   = 0.0

        self._snd_shoot = self._snd(":resources:sounds/hurt2.wav")
        self._snd_hit   = self._snd(":resources:sounds/hit3.wav")

        self._txt_hint = arcade.Text(
            "", SCREEN_W // 2, SCREEN_H - 55,
            (220, 180, 255), 14, anchor_x="center",
        )

    # ── Setup ─────────────────────────────────────────────────────────────────
    def setup(self) -> None:
        self.ps.clear()
        self.p_bullets.clear()
        self.e_bullets.clear()
        self.enemies.clear()
        self._enemy_sl.clear()
        self._shoot_cd = 0.0
        self._killed   = 0
        self._finish_open = False
        self._lives    = MAX_LIVES
        self._hurt_cd  = 0.0

        md = _MAPS[self.level - 1]
        self._ww = max(len(r) for r in md) * TS
        self._wh = len(md) * TS

        walls, _sp, coll, emark, pp, _fp = parse_map(md)
        self.walls = walls
        self.finish    = None
        self._finish_sl = arcade.SpriteList()
        for s in coll:
            if getattr(s, "name", "") == "finish":
                self.finish = s
                self._finish_sl.append(s)

        for m in emark:
            robot = GreyRobot(m.center_x, m.center_y)
            self.enemies.append(robot)
            self._enemy_sl.append(robot)
        self._total = len(self.enemies)

        self.player = arcade.SpriteSolidColor(28, 44, C_KLYAKSA)
        self.player.center_x, self.player.center_y = pp[0], pp[1]
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.walls, gravity_constant=GRAVITY,
        )

    # ── Update ────────────────────────────────────────────────────────────────
    def on_update(self, dt: float) -> None:
        if not self.player or not self.engine:
            return
        self._tick_grace(dt)

        # Движение игрока
        if arcade.key.LEFT in self.keys or arcade.key.A in self.keys:
            self.player.change_x = -SPEED
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys:
            self.player.change_x = SPEED
        else:
            self.player.change_x = 0

        self._shoot_cd -= dt
        self._hurt_cd  -= dt
        self.engine.update()
        self.ps.update(dt)

        px, py = self.player.center_x, self.player.center_y

        # ── AI врагов ─────────────────────────────────────────────────────────
        for robot in list(self.enemies):
            d = math.dist((robot.center_x, robot.center_y), (px, py))
            same_y = abs(robot.center_y - py) < TS * 1.5

            if d < AGGRO_RANGE and same_y:
                robot.aggroed = True
                robot.move_toward_player(px, py, dt)
            else:
                robot.aggroed = False
                robot.patrol()

            # Выстрел врага
            robot._shoot_t -= dt
            if robot._shoot_t <= 0 and d < SHOOT_RANGE:
                robot._shoot_t = SHOOT_CD + random.uniform(-0.3, 0.3)
                angle = math.atan2(py - robot.center_y,
                                   px - robot.center_x)
                eb = EnemyBullet(
                    robot.center_x + math.cos(angle) * 22,
                    robot.center_y + math.sin(angle) * 22,
                    angle,
                )
                self.e_bullets.append(eb)

        # ── Снаряды игрока ────────────────────────────────────────────────────
        for b in list(self.p_bullets):
            b.on_update(dt)
            if (b.center_x < -50 or b.center_x > self._ww + 50
                    or b.center_y < -50 or b.center_y > self._wh + 50):
                b.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(b, self.walls):
                self.ps.emit_ink(b.center_x, b.center_y)
                b.remove_from_sprite_lists()
                continue
            for robot in arcade.check_for_collision_with_list(
                    b, self._enemy_sl):
                self.ps.emit_ink(robot.center_x, robot.center_y)
                robot.remove_from_sprite_lists()
                self.enemies.remove(robot)
                b.remove_from_sprite_lists()
                self._killed += 1
                self.score  += 100
                self._play(self._snd_shoot)

        # ── Снаряды врагов ────────────────────────────────────────────────────
        for eb in list(self.e_bullets):
            eb.on_update(dt)
            if (eb.center_x < -50 or eb.center_x > self._ww + 50
                    or eb.center_y < -50 or eb.center_y > self._wh + 50):
                eb.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(eb, self.walls):
                eb.remove_from_sprite_lists()
                continue
            if self._hurt_cd <= 0 and arcade.check_for_collision(
                    eb, self.player):
                eb.remove_from_sprite_lists()
                self._lives -= 1
                self._hurt_cd = HURT_CD
                self.ps.emit_ink(self.player.center_x, self.player.center_y)
                self._play(self._snd_hurt)
                if self._lives <= 0:
                    self._game_over()
                    return

        # ── Контактный урон от врага ──────────────────────────────────────────
        if self._hurt_cd <= 0:
            contact = arcade.check_for_collision_with_list(
                self.player, self._enemy_sl
            )
            if contact:
                self._lives -= 1
                self._hurt_cd = HURT_CD
                self._play(self._snd_hurt)
                if self._lives <= 0:
                    self._game_over()
                    return

        # ── Финиш ─────────────────────────────────────────────────────────────
        self._finish_open = (self._killed >= self._total)
        if (self._can_finish() and self._finish_open and self.finish
                and arcade.check_for_collision(self.player, self.finish)):
            self.score += 300 + self._lives * 100
            self._level_done()
            return

        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     self._ww, self._wh)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def on_draw(self) -> None:
        self.clear()
        self.background_color = (28, 16, 42)

        with self.wcam.activate():
            self.walls.draw()

            # Враги: агрессивные подсвечиваются красным контуром
            for robot in self.enemies:
                color = (75, 75, 85)
                robot.color = (180, 60, 60) if robot.aggroed else color
            self._enemy_sl.draw()

            self.p_bullets.draw()
            self.e_bullets.draw()

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
                # Мигание при неуязвимости
                if self._hurt_cd > 0 and int(self._hurt_cd * 8) % 2:
                    color_p = (255, 120, 120)
                else:
                    color_p = C_KLYAKSA
                arcade.draw_rectangle_filled(
                    p.center_x, p.center_y, 28, 44, color_p)
                # Пушка
                arcade.draw_rectangle_filled(
                    p.center_x + 20, p.center_y + 6, 22, 8, (80, 20, 130))

        with self.gcam.activate():
            self._hud(f"Враги: {self._killed}/{self._total}")

            # Жизни
            for i in range(MAX_LIVES):
                col = (220, 80, 80) if i < self._lives else (60, 50, 60)
                arcade.draw_text("♥", 12 + i * 28, SCREEN_H - 52, col, 20)

            if not self._finish_open:
                self._txt_hint.text = (
                    f"Убей всех врагов! Осталось: {self._total - self._killed}"
                )
                self._txt_hint.draw()
            else:
                self._txt_hint.text = "Все враги повержены! Иди к финишу!"
                self._txt_hint.draw()

            arcade.draw_text(
                "WASD — движение  |  ЛКМ — стрелять чернилами  "
                "|  Красные роботы — агрессивны",
                SCREEN_W // 2, 12, (160, 130, 200), 11, anchor_x="center",
            )

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        if not self.player or self._shoot_cd > 0:
            return
        self._shoot_cd = 0.22
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
        self.p_bullets.append(b)
        self.ps.emit_ink(self.player.center_x, self.player.center_y)
        self._play(self._snd_shoot)
