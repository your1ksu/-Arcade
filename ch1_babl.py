"""
ch1_babl.py — Глава 1: Бабл — Мальчик в пузыре
PhysicsEnginePlatformer использует px/кадр (НЕ px/s).
GRAVITY, JUMP_V, SPEED — всё в единицах per-frame. Arcade 3.x.
"""
from __future__ import annotations
import arcade
from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, MAX_BUBBLE, SOAP_HEAL, SPIKE_DMG, C_BABL
from utils import parse_map, draw_bar

# ── Физика (px/кадр, НЕ px/s) ────────────────────────────────────────────────
GRAVITY      = 0.7    # добавляется к change_y каждый кадр
SPEED        = 8      # change_x в px/кадр
JUMP_V       = 14     # начальный change_y при прыжке
BUBBLE_DRAIN = 0.25   # ед/с пассивная утечка пузыря

_MAPS = [
    # ── Уровень 1 ── три этажа, два прохода вниз ──────────────────────────────
    # Проходы: стена A→B — справа (8 пустых тайлов), стена B→C — слева (9 тайлов)
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P    S          S         S          W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W       WWWWWWWW    S    WWWWWWWW       W",
        "W    S                         S        W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    S      X       S     X    S        W",
        "W                                       W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # ── Уровень 2 ── ветер, зигзаг вниз ───────────────────────────────────────
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P    S          S                    W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W    S    X    X    S         S    X    W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    S              S         S         W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W      X    S    X    X    S    X       W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
    # ── Уровень 3 ── четыре этажа, чередующиеся проходы ───────────────────────
    [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W  P   S          S          S          W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W    S    X    X    S    X    X    S    W",
        "W                                       W",
        "W        WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W                                       W",
        "W    S         S         S              W",
        "W                                       W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW        W",
        "W                                       W",
        "W    S    X    S    X    S    X    S    W",
        "W  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  W",
        "W                                   F  W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ],
]

# Ветровые зоны по уровням: (col_start, col_end)
_WIND = [[], [(15, 24)], [(8, 16), (24, 32)]]

class Chapter1View(BaseChapter):

    def __init__(self, chapter_num: int = 1) -> None:
        super().__init__(chapter_num)
        self.bubble: float = MAX_BUBBLE
        self.player    = None
        self.walls     = arcade.SpriteList()
        self.spikes    = arcade.SpriteList()
        self.soaps     = arcade.SpriteList()
        self.finish    = None
        self._finish_sl = arcade.SpriteList()
        self.engine    = None
        self._wind_ranges: list = []
        self._ww = self._wh = 0.0
        self._wind_t = 0.0
        self._txt_warn = arcade.Text("", SCREEN_W // 2, 40,
                                     (255, 80, 40), 18,
                                     anchor_x="center", bold=True)

    def setup(self) -> None:
        self.bubble = MAX_BUBBLE
        self.ps.clear()
        self._wind_t = 0.0

        md = _MAPS[self.level - 1]
        self._ww = max(len(r) for r in md) * TS
        self._wh = len(md) * TS

        walls, spikes, coll, _e, pp, _fp = parse_map(md)
        self.walls  = walls
        self.spikes = spikes
        self.soaps  = arcade.SpriteList()
        self.finish = None
        self._finish_sl = arcade.SpriteList()

        for s in coll:
            if getattr(s, "name", "") == "finish":
                self.finish = s
                self._finish_sl.append(s)
            else:
                self.soaps.append(s)

        self._wind_ranges = [
            (c0 * TS, c1 * TS) for c0, c1 in _WIND[self.level - 1]
        ]

        self.player = arcade.SpriteSolidColor(30, 30, C_BABL)
        self.player.center_x = pp[0]
        self.player.center_y = pp[1]

        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.walls,
            gravity_constant=GRAVITY,
        )

    def on_update(self, dt: float) -> None:
        if not self.player or not self.engine:
            return
        self._tick_grace(dt)

        # Горизонталь: px/кадр (change_x, не умножать на dt)
        if arcade.key.LEFT in self.keys or arcade.key.A in self.keys:
            self.player.change_x = -SPEED
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys:
            self.player.change_x = SPEED
        else:
            self.player.change_x = 0

        # Ветер: небольшое постоянное добавление к change_x
        px = self.player.center_x
        in_wind = any(x0 <= px <= x1 for x0, x1 in self._wind_ranges)
        if in_wind:
            self.player.change_x += 2   # px/кадр
            self._wind_t += dt
            if self._wind_t >= 0.1:
                self._wind_t = 0.0
                self.ps.emit_wind(px, self.player.center_y)

        # Физический движок обрабатывает гравитацию и коллизии со стенами
        self.engine.update()
        self.ps.update(dt)

        # Шипы — урон в секунду
        if arcade.check_for_collision_with_list(self.player, self.spikes):
            self.bubble -= SPIKE_DMG * dt
            self.ps.emit_soap(self.player.center_x, self.player.center_y)

        # Мыло — подбор
        for s in arcade.check_for_collision_with_list(self.player, self.soaps):
            self.bubble = min(MAX_BUBBLE, self.bubble + SOAP_HEAL)
            self.score += 50
            self.ps.emit_soap(s.center_x, s.center_y)
            s.remove_from_sprite_lists()
            self._play(self._snd_coin)

        # Пассивная утечка
        self.bubble -= BUBBLE_DRAIN * dt
        if self.bubble <= 0:
            self._game_over()
            return

        # Финиш (только после grace-периода)
        if (self._can_finish() and self.finish
                and arcade.check_for_collision(self.player, self.finish)):
            self.score += 300 + int(self.bubble)
            self._level_done()
            return

        # Провал за нижний край
        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     self._ww, self._wh)

    def on_draw(self) -> None:
        import math
        self.clear()
        # Ночной индустриальный город — глубокий сине-лиловый
        self.background_color = (10, 12, 32)

        with self.wcam.activate():
            cam_x, cam_y = self.wcam.position

            # ── СЛОЙ 1: звёздное небо ────────────────────────────────────────
            import random as _r; _r.seed(7)
            for _ in range(60):
                sx = _r.randint(0, int(self._ww))
                sy = _r.randint(int(self._wh * 0.3), int(self._wh))
                a  = _r.randint(60, 140)
                arcade.draw_circle_filled(
                    sx - cam_x * 0.05, sy, _r.randint(1, 2), (200, 210, 255, a))

            # ── СЛОЙ 2: далёкие здания — сиреневый горизонт ──────────────────
            far_bld = [(80,220),(190,310),(340,190),(470,270),
                       (600,210),(760,330),(880,170),(1020,240),
                       (1180,290),(1340,200),(1500,250)]
            for bx, bh in far_bld:
                px = bx - cam_x * 0.12
                # Корпус здания с градиентом (верх светлее)
                arcade.draw_rectangle_filled(px, bh//2, 72, bh, (22, 20, 52))
                arcade.draw_rectangle_filled(px, bh - 12, 72, 20, (32, 28, 68))
                # Окна — тёплые, каждое отдельно
                for row in range(18, bh - 18, 32):
                    for col in (-20, 0, 20):
                        lit = (int(px)+col + row) % 5 != 0
                        c = (190, 165, 70, 150) if lit else (35, 33, 58)
                        arcade.draw_rectangle_filled(px + col, row, 9, 12, c)
                # Антенна на крыше
                arcade.draw_line(px, bh, px, bh+18, (40, 36, 72), 2)
                arcade.draw_circle_filled(px, bh+18, 3, (210, 80, 80, 160))

            # ── СЛОЙ 3: ближние тёмные здания без окон ───────────────────────
            near_bld = [(50,140),(260,105),(440,150),(650,115),
                        (850,160),(1060,130),(1290,145),(1480,120)]
            for bx, bh in near_bld:
                px = bx - cam_x * 0.28
                arcade.draw_rectangle_filled(px, bh//2, 95, bh, (16, 14, 38))
                # Верхний контур
                arcade.draw_line(px-47, bh, px+47, bh, (30, 26, 60), 1)

            # ── Туман у пола — атмосфера ─────────────────────────────────────
            for i in range(5):
                arcade.draw_rectangle_filled(
                    self._ww/2, i*18+9, self._ww, 18, (40, 60, 110, 22-i*4))

            # ── Ветровые зоны — холодное синее свечение ──────────────────────
            for x0, x1 in self._wind_ranges:
                mid = (x0 + x1) / 2
                for layer, (alpha, extra) in enumerate([(22,30),(14,12),(7,0)]):
                    arcade.draw_rectangle_filled(
                        mid, self._wh/2, (x1-x0)+extra, self._wh,
                        (60, 120, 240, alpha))
                arcade.draw_line(x0, 0, x0, self._wh, (80, 150, 255, 60), 1)
                arcade.draw_line(x1, 0, x1, self._wh, (80, 150, 255, 60), 1)
                # Иконка ветра
                arcade.draw_text("≋", mid, 20, (80, 160, 255, 120), 14,
                                  anchor_x="center")

            # ── Стены: тёмно-синий металл с рёбрами ──────────────────────────
            for spr in self.walls:
                wx, wy = spr.center_x, spr.center_y
                ww, wh = spr.width, spr.height
                arcade.draw_rectangle_filled(wx, wy, ww, wh, (28, 32, 70))
                # Светлая верхняя грань
                arcade.draw_line(wx-ww//2, wy+wh//2,
                                  wx+ww//2, wy+wh//2, (55, 70, 130), 1)
                # Тёмная нижняя грань
                arcade.draw_line(wx-ww//2, wy-wh//2,
                                  wx+ww//2, wy-wh//2, (14, 16, 40), 1)

            # ── Шипы — красно-оранжевые треугольники ─────────────────────────
            for spr in self.spikes:
                sx, sy = spr.center_x, spr.center_y
                hw = spr.width // 2
                arcade.draw_triangle_filled(
                    sx - hw, sy - 4, sx + hw, sy - 4, sx, sy + 16,
                    (190, 45, 60))
                arcade.draw_triangle_outline(
                    sx - hw, sy - 4, sx + hw, sy - 4, sx, sy + 16,
                    (230, 80, 90), 1)
                # Блик на острие
                arcade.draw_circle_filled(sx, sy+14, 2, (255, 160, 160, 180))

            # ── Мыло — переливчатые пузырьки ─────────────────────────────────
            for s in self.soaps:
                cx2, cy2 = s.center_x, s.center_y
                # Внешнее мягкое свечение
                arcade.draw_circle_filled(cx2, cy2, 18, (100, 180, 255, 28))
                # Основной пузырь
                arcade.draw_circle_filled(cx2, cy2, 12, (160, 210, 255, 90))
                arcade.draw_circle_outline(cx2, cy2, 12, (210, 235, 255), 2)
                # Радужный отлив
                arcade.draw_arc_outline(cx2-2, cy2+2, 14, 14,
                                         (190, 230, 255, 110), 35, 145, 2)
                # Два блика
                arcade.draw_circle_filled(cx2-4, cy2+5, 3, (255,255,255,160))
                arcade.draw_circle_filled(cx2+5, cy2-3, 2, (255,255,255,100))

            # ── Финиш — портал с пульсацией ──────────────────────────────────
            self._finish_sl.draw()
            if self.finish:
                fx2, fy2 = self.finish.center_x, self.finish.center_y
                for ring, (r2, a2) in enumerate([(45,35),(35,55),(26,70)]):
                    arcade.draw_circle_filled(fx2, fy2, r2, (50, 210, 110, a2))
                arcade.draw_circle_outline(fx2, fy2, 26, (120, 255, 160), 2)
                arcade.draw_text("▶", fx2, fy2, (180, 255, 200), 14,
                                   anchor_x="center", anchor_y="center",
                                   bold=True)

            self.ps.draw()

            # ── Бабл — стеклянный пузырь ─────────────────────────────────────
            if self.player:
                p = self.player
                cx3, cy3 = p.center_x, p.center_y
                # Мягкий ореол
                arcade.draw_circle_filled(cx3, cy3, 30, (70, 140, 255, 18))
                # Полупрозрачный шар
                arcade.draw_circle_filled(cx3, cy3, 21, (80, 155, 245, 70))
                # Контур — чуть переливчатый
                arcade.draw_circle_outline(cx3, cy3, 21, (170, 215, 255), 2)
                # Внутренний блик-дуга
                arcade.draw_arc_outline(cx3-3, cy3+3, 26, 26,
                                         (210, 240, 255, 90), 25, 155, 3)
                # Лицо мальчика
                arcade.draw_circle_filled(cx3, cy3-1, 9, (255, 215, 175))
                arcade.draw_circle_filled(cx3-3, cy3, 2, (55, 38, 18))
                arcade.draw_circle_filled(cx3+3, cy3, 2, (55, 38, 18))
                # Улыбка
                arcade.draw_arc_outline(cx3, cy3-3, 8, 5,
                                         (160, 100, 60), 200, 340, 1)
                # Блик стекла
                arcade.draw_circle_filled(cx3-7, cy3+9, 4, (255,255,255,100))

        with self.gcam.activate():
            # HUD-полоса снизу
            arcade.draw_rectangle_filled(
                SCREEN_W//2, 24, SCREEN_W, 48, (8, 10, 28, 215))
            arcade.draw_line(0, 48, SCREEN_W, 48, (45, 75, 150, 100), 1)
            self._hud()
            draw_bar(130, SCREEN_H-48, 200, 16,
                     self.bubble, MAX_BUBBLE,
                     fill=(90, 185, 255), label="Пузырь")
            if self.bubble < 30:
                self._txt_warn.text = "⚠ Пузырь лопается!"
                self._txt_warn.draw()
            arcade.draw_text(
                "WASD/← → — движение  |  ↑/W/ПРОБЕЛ — прыжок  "
                "|  S — мыло (+25)  |  X — шипы",
                SCREEN_W//2, 12, (90, 130, 200), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
