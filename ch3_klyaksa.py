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

# Клавиши стрельбы — одинаковые физические клавиши на RU и EN раскладке:
#   F  = стрелять по ближайшему врагу (автонаводка)
#   J  = стрелять вправо
#   G / Э = стрелять влево  (arcade.key.G == arcade.key.Э физически)
SHOOT_KEYS_AUTO  = (arcade.key.F,)            # автонаводка — ближайший враг
SHOOT_KEYS_RIGHT = (arcade.key.J,)            # вправо
SHOOT_KEYS_LEFT  = (arcade.key.G,)            # влево

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
        import math, random as _rnd
        self.clear()
        self.background_color = (18, 10, 30)

        with self.wcam.activate():
            cam_x, cam_y = self.wcam.position

            # ── Фон: стены галереи с рамками-картинами ───────────────────────
            # Тёмные полосы — имитация панелей стен
            for xi in range(0, int(self._ww) + 200, 200):
                arcade.draw_line(xi, 0, xi, self._wh, (32, 20, 50, 80), 1)
            for yi in range(0, int(self._wh) + 150, 150):
                arcade.draw_line(0, yi, self._ww, yi, (32, 20, 50, 60), 1)

            # Декоративные пустые рамки на стенах
            _rnd.seed(42)
            for _ in range(22):
                fx = _rnd.randint(60, int(self._ww) - 60)
                fy = _rnd.randint(80, int(self._wh) - 80)
                fw = _rnd.randint(50, 90)
                fh = _rnd.randint(40, 70)
                # Рамка — серая
                arcade.draw_rectangle_outline(fx, fy, fw, fh, (55, 40, 75), 2)
                # Внутри — цветное пятно (залитое чернилами)
                ink_c = _rnd.choice([
                    (120, 40, 180, 60), (180, 40, 100, 60),
                    (40, 100, 180, 60), (160, 160, 40, 50),
                ])
                arcade.draw_rectangle_filled(fx, fy, fw - 6, fh - 6, ink_c)

            # ── Стены с имитацией покраски ───────────────────────────────────
            self.walls.draw()
            for spr in self.walls:
                arcade.draw_rectangle_outline(
                    spr.center_x, spr.center_y,
                    spr.width, spr.height,
                    (60, 35, 85, 140), 1)

            # ── Враги — серые роботы ─────────────────────────────────────────
            for robot in self.enemies:
                robot.color = (175, 55, 55) if robot.aggroed else (68, 68, 80)
                # Свечение вокруг агрессивных
                if robot.aggroed:
                    arcade.draw_circle_filled(
                        robot.center_x, robot.center_y,
                        28, (200, 50, 50, 35))
            self._enemy_sl.draw()
            # Глаза-диоды на роботах
            for robot in self.enemies:
                eye_col = (255, 80, 80) if robot.aggroed else (80, 80, 120)
                arcade.draw_circle_filled(
                    robot.center_x - 6, robot.center_y + 10, 4, eye_col)
                arcade.draw_circle_filled(
                    robot.center_x + 6, robot.center_y + 10, 4, eye_col)

            # ── Снаряды ──────────────────────────────────────────────────────
            # Фиолетовые чернила — всегда рисуем вручную (игнорируем цвет спрайта)
            for b in self.p_bullets:
                arcade.draw_circle_filled(
                    b.center_x, b.center_y, 11, (100, 20, 160, 60))
                arcade.draw_circle_filled(
                    b.center_x, b.center_y, 7, (160, 40, 220))
                arcade.draw_circle_filled(
                    b.center_x, b.center_y, 4, (210, 120, 255))
            # Снаряды врагов — тускло-серые
            for b in self.e_bullets:
                arcade.draw_circle_filled(
                    b.center_x, b.center_y, 8, (80, 75, 100, 70))
                arcade.draw_circle_filled(
                    b.center_x, b.center_y, 5, (155, 150, 175))

            # ── Финиш — светящийся портал ────────────────────────────────────
            if self._finish_open:
                self._finish_sl.draw()
                if self.finish:
                    for ring in range(3):
                        arcade.draw_circle_outline(
                            self.finish.center_x, self.finish.center_y,
                            30 + ring * 10,
                            (80 + ring * 40, 220, 120, 80 - ring * 20), 2)

            self.ps.draw()

            # ── Игрок — Клякса ───────────────────────────────────────────────
            if self.player:
                p = self.player
                # Мигание
                if self._hurt_cd > 0 and int(self._hurt_cd * 8) % 2:
                    body_c = (255, 100, 100)
                else:
                    body_c = C_KLYAKSA
                # Берет
                arcade.draw_ellipse_filled(
                    p.center_x, p.center_y + 24, 26, 10, (100, 30, 160))
                arcade.draw_rectangle_filled(
                    p.center_x - 1, p.center_y + 28, 8, 6, (80, 20, 130))
                # Тело
                arcade.draw_rectangle_filled(
                    p.center_x, p.center_y, 26, 40, body_c)
                # Шарф
                arcade.draw_rectangle_filled(
                    p.center_x, p.center_y + 12, 28, 8, (200, 50, 80))
                # Пушка
                arcade.draw_rectangle_filled(
                    p.center_x + 18, p.center_y + 4, 24, 8, (60, 15, 110))
                arcade.draw_circle_filled(
                    p.center_x + 30, p.center_y + 4, 5, (150, 40, 220))

        with self.gcam.activate():
            # Нижняя панель HUD
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (12, 6, 22, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (80, 40, 120, 140), 1)
            self._hud(f"Враги: {self._killed}/{self._total}")
            # Жизни
            for i in range(MAX_LIVES):
                col = (210, 70, 70) if i < self._lives else (50, 40, 55)
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
                "↑/W/ПРОБЕЛ — прыжок  |  F — авто-выстрел  "
                "|  J — вправо  G — влево  |  ЛКМ — мышь",
                SCREEN_W // 2, 12, (140, 110, 180), 11, anchor_x="center",
            )

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)
        # Стрельба клавиатурой
        elif key in SHOOT_KEYS_AUTO:
            self._shoot_keyboard(auto=True)
        elif key in SHOOT_KEYS_RIGHT:
            self._shoot_keyboard(angle=0.0)
        elif key in SHOOT_KEYS_LEFT:
            self._shoot_keyboard(angle=math.pi)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)

    def _shoot_keyboard(self, auto: bool = False,
                        angle: float = 0.0) -> None:
        """Выстрел с клавиатуры. auto=True → автонаводка на ближайшего врага."""
        if not self.player or self._shoot_cd > 0:
            return
        self._shoot_cd = 0.22

        if auto and self.enemies:
            # Ищем ближайшего живого врага
            px, py = self.player.center_x, self.player.center_y
            nearest = min(
                self.enemies,
                key=lambda e: math.dist((e.center_x, e.center_y), (px, py)),
            )
            angle = math.atan2(
                nearest.center_y - py,
                nearest.center_x - px,
            )
        elif auto:
            # Нет врагов — стреляем вправо
            angle = 0.0

        b = InkBullet(
            self.player.center_x + math.cos(angle) * 22,
            self.player.center_y + math.sin(angle) * 22,
            angle,
        )
        self.p_bullets.append(b)
        self.ps.emit_ink(self.player.center_x, self.player.center_y)
        self._play(self._snd_shoot)

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn == arcade.MOUSE_BUTTON_LEFT and self._menu_btn_hit(x, y):
            self._go_menu(); return
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
