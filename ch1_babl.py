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
SPEED        = 5      # change_x в px/кадр
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
        self.clear()
        self.background_color = (22, 32, 75)

        with self.wcam.activate():
            for x0, x1 in self._wind_ranges:
                arcade.draw_rectangle_filled(
                    (x0 + x1) / 2, self._wh / 2,
                    x1 - x0, self._wh, (80, 140, 255, 30),
                )
            self.walls.draw()
            self.spikes.draw()
            self.soaps.draw()
            self._finish_sl.draw()
            self.ps.draw()
            if self.player:
                p = self.player
                # Пузырь
                arcade.draw_circle_filled(p.center_x, p.center_y, 18,
                                          (*C_BABL, 90))
                arcade.draw_circle_outline(p.center_x, p.center_y, 18,
                                           (200, 235, 255), 2)
                # Мальчик
                arcade.draw_circle_filled(p.center_x, p.center_y - 1, 8,
                                          (255, 210, 170))
                # Блик
                arcade.draw_circle_filled(p.center_x - 5, p.center_y + 7,
                                          3, (255, 255, 255, 130))

        with self.gcam.activate():
            self._hud()
            draw_bar(130, SCREEN_H - 48, 200, 16,
                     self.bubble, MAX_BUBBLE,
                     fill=(80, 190, 255), label="Пузырь")
            if self.bubble < 30:
                self._txt_warn.text = "Пузырь лопается!"
                self._txt_warn.draw()
            arcade.draw_text(
                "WASD/стрелки — движение  |  ↑/W/ПРОБЕЛ — прыжок  "
                "|  S — мыло (+25)  |  X — шипы",
                SCREEN_W // 2, 12, (120, 150, 200), 11, anchor_x="center",
            )

    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.engine.can_jump() and self.player:
                self.player.change_y = JUMP_V
                self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
