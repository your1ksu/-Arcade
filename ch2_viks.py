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
        import random as _rnd
        self.clear()
        self.background_color = (5, 3, 12)
        lr = int(LIGHT_R_MAX * self.candle / MAX_CANDLE)

        with self.wcam.activate():
            # ── Каменная текстура стен подземелья ───────────────────────────
            cam_x, cam_y = self.wcam.position
            # Горизонтальные трещины в стенах
            _rnd.seed(13)
            for _ in range(40):
                cx2 = _rnd.randint(0, int(self._ww))
                cy2 = _rnd.randint(0, int(self._wh))
                w2  = _rnd.randint(20, 80)
                arcade.draw_line(cx2, cy2, cx2 + w2, cy2 + _rnd.randint(-4, 4),
                                 (30, 24, 45, 70), 1)
            # Факелы на стенах (декоративные)
            for tx, ty in [(160, 200), (640, 350), (320, 520),
                           (800, 180), (480, 700), (160, 860),
                           (720, 960), (400, 1100), (800, 1250)]:
                dist_to_player = 9999.0
                if self.player:
                    dist_to_player = math.sqrt(
                        (tx - self.player.center_x) ** 2
                        + (ty - self.player.center_y) ** 2)
                if dist_to_player < lr + 60:
                    # Настенное крепление
                    arcade.draw_rectangle_filled(tx, ty - 8, 6, 14,
                                                 (70, 55, 35))
                    # Огонь факела
                    import math as _m
                    flicker = 5 + 3 * _m.sin(tx * 0.3 + ty * 0.2)
                    arcade.draw_triangle_filled(
                        tx - int(flicker), ty,
                        tx + int(flicker), ty,
                        tx, ty + int(flicker * 2.5),
                        (220, 120, 30, 180))
                    arcade.draw_triangle_filled(
                        tx - int(flicker * 0.5), ty + 4,
                        tx + int(flicker * 0.5), ty + 4,
                        tx, ty + int(flicker * 2),
                        (255, 200, 60, 200))
                    arcade.draw_circle_filled(tx, ty, int(flicker * 1.4) + 18,
                                             (200, 100, 30, 18))

            # ── Стены с каменной кладкой ─────────────────────────────────────
            self.walls.draw()
            for spr in self.walls:
                # Имитация кирпичей
                sw = int(spr.width)
                sh = int(spr.height)
                for bx in range(-sw // 2 + 10, sw // 2, 20):
                    arcade.draw_line(
                        spr.center_x + bx, spr.center_y - sh // 2,
                        spr.center_x + bx, spr.center_y + sh // 2,
                        (40, 32, 55, 80), 1)

            # ── Масло — светящиеся флаконы ───────────────────────────────────
            for oil in self.oils:
                # Свечение
                arcade.draw_circle_filled(
                    oil.center_x, oil.center_y, 18, (200, 120, 20, 50))
                # Флакон — прямоугольник с горлышком
                arcade.draw_rectangle_filled(
                    oil.center_x, oil.center_y - 2, 14, 18, (180, 100, 20))
                arcade.draw_rectangle_filled(
                    oil.center_x, oil.center_y + 11, 6, 8, (140, 80, 15))
                # Блик
                arcade.draw_rectangle_filled(
                    oil.center_x - 3, oil.center_y + 2, 3, 8,
                    (255, 200, 100, 140))

            self._finish_sl.draw()
            if self.finish:
                arcade.draw_circle_filled(
                    self.finish.center_x, self.finish.center_y,
                    40, (60, 180, 100, 40))

            if self.player:
                # ── Видимые враги ────────────────────────────────────────────
                visible_enemies = arcade.SpriteList()
                for e in self.enemies:
                    d = math.sqrt((e.center_x - self.player.center_x) ** 2
                                   + (e.center_y - self.player.center_y) ** 2)
                    if d < lr + 20:
                        visible_enemies.append(e)
                        # Глаза теней (светятся в темноте)
                        arcade.draw_circle_filled(
                            e.center_x - 6, e.center_y + 12, 3, (160, 60, 200))
                        arcade.draw_circle_filled(
                            e.center_x + 6, e.center_y + 12, 3, (160, 60, 200))
                visible_enemies.draw()

                self._aura.draw()
                self.ps.draw()

                # ── Рыцарь Викс ──────────────────────────────────────────────
                p = self.player
                cx, cy = p.center_x, p.center_y

                # Тень под персонажем
                arcade.draw_ellipse_filled(cx + 2, cy - 22, 24, 8, (0, 0, 0, 70))
                # Плащ (треугольник сзади)
                arcade.draw_triangle_filled(
                    cx - 14, cy - 20, cx + 14, cy - 20, cx, cy + 4,
                    (40, 35, 60))
                # Тело — доспех
                arcade.draw_rectangle_filled(cx, cy, 24, 38, C_VIKS)
                # Нагрудник — стальной блик
                arcade.draw_rectangle_filled(cx, cy + 5, 20, 22, (105, 110, 130))
                arcade.draw_rectangle_filled(cx - 4, cy + 10, 5, 12, (130, 135, 155))
                # Поножи
                arcade.draw_rectangle_filled(cx - 5, cy - 16, 8, 10, (90, 95, 115))
                arcade.draw_rectangle_filled(cx + 5, cy - 16, 8, 10, (90, 95, 115))
                # Шлем с забралом
                arcade.draw_rectangle_filled(cx, cy + 25, 22, 14, (85, 90, 108))
                arcade.draw_rectangle_filled(cx, cy + 29, 14, 6, (65, 70, 88))
                # Прорезь забрала
                arcade.draw_rectangle_filled(cx - 3, cy + 30, 12, 2, (20, 18, 30))

                # ── Красивая свеча ────────────────────────────────────────────
                # Держатель свечи (рука)
                arcade.draw_rectangle_filled(cx + 14, cy + 8, 4, 16, (80, 75, 100))
                # Подсвечник
                arcade.draw_rectangle_filled(cx + 14, cy + 18, 10, 4, (140, 120, 60))
                # Воск — тело свечи
                arcade.draw_rectangle_filled(cx + 14, cy + 26, 6, 16, (245, 238, 210))
                # Воск подтёкший
                arcade.draw_ellipse_filled(cx + 12, cy + 20, 8, 4, (235, 228, 195))
                arcade.draw_ellipse_filled(cx + 16, cy + 21, 6, 3, (235, 228, 195))
                # Фитиль
                arcade.draw_line(cx + 14, cy + 34, cx + 15, cy + 38,
                                 (30, 22, 10), 2)
                # Пламя свечи
                candle_ratio = max(0.0, self.candle / MAX_CANDLE)
                if candle_ratio > 0:
                    fa = min(255, int(230 * candle_ratio))
                    # Внешнее свечение
                    arcade.draw_circle_filled(
                        cx + 14, cy + 44, int(12 * candle_ratio) + 4,
                        (240, 160, 30, int(60 * candle_ratio)))
                    # Основное пламя
                    arcade.draw_triangle_filled(
                        cx + 9,  cy + 38,
                        cx + 19, cy + 38,
                        cx + 14, cy + 52,
                        (245, 140, 30, fa))
                    # Внутреннее белое ядро
                    arcade.draw_triangle_filled(
                        cx + 11, cy + 39,
                        cx + 17, cy + 39,
                        cx + 14, cy + 48,
                        (255, 220, 120, min(255, fa + 30)))
                    # Яркое ядро
                    arcade.draw_circle_filled(
                        cx + 14, cy + 41, int(3 * candle_ratio),
                        (255, 245, 200, fa))

        with self.gcam.activate():
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (8, 5, 18, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (80, 60, 30, 120), 1)
            self._hud()
            draw_bar(130, SCREEN_H - 48, 200, 16,
                     self.candle, MAX_CANDLE,
                     fill=(245, 165, 40), label="Свеча")
            if self.candle < 25:
                self._txt_warn.text = "Свеча гаснет!"
                self._txt_warn.draw()
            arcade.draw_text(
                "WASD — движение  |  O — масло (+30)  "
                "|  Тени и ветер гасят свечу",
                SCREEN_W // 2, 12, (130, 110, 70), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
