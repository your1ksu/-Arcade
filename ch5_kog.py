"""
ch5_kog.py — Глава 5: Мастер Kog — Инженер-предатель
Головоломка с шестерёнками: перетащи мышью, чтобы цепь заработала.
Arcade 3.x.
"""

from __future__ import annotations

import math

import arcade

from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, G_COLS, G_ROWS, G_CELL, C_KOG
from utils import draw_btn

OX = (SCREEN_W - G_COLS * G_CELL) // 2
OY = (SCREEN_H - G_ROWS * G_CELL) // 2

_LEVELS = [
    # Уровень 1: прямая линия через фиксированную (2,2). Нужно 2 шестерёнки: (1,2) и (3,2)
    {"fixed": [(2, 2)],          "src": (0, 2), "tgt": (4, 2), "par": 2},
    # Уровень 2: Г-образный путь. Путь: (0,1)→(1,1)→(2,1)f→(3,1)→(3,2)→(3,3)→(4,3)f→(5,3)→(6,3)
    # Нужно 5 свободных: (1,1),(3,1),(3,2),(3,3),(5,3)
    {"fixed": [(2, 1), (4, 3)],  "src": (0, 1), "tgt": (6, 3), "par": 5},
    # Уровень 3: прямая с отвлекающей шестерёнкой (3,0). Путь по строке 2.
    # Нужно 3 свободных: (2,2),(3,2),(4,2)
    {"fixed": [(1, 2), (3, 0), (5, 2)], "src": (0, 2), "tgt": (6, 2), "par": 5},
]


class _Gear:
    def __init__(self, col: int, row: int,
                 fixed=False, src=False, tgt=False) -> None:
        self.col = col
        self.row = row
        self.fixed = fixed
        self.src = src
        self.tgt = tgt
        self.powered = False
        self.angle = 0.0
        self.placed = fixed  # free gears start unplaced (col=-999)

    @property
    def cx(self) -> float:
        return OX + self.col * G_CELL + G_CELL // 2

    @property
    def cy(self) -> float:
        return OY + self.row * G_CELL + G_CELL // 2

    def adjacent(self, other: "_Gear") -> bool:
        return abs(self.col - other.col) + abs(self.row - other.row) == 1


class Chapter5View(BaseChapter):

    def __init__(self, chapter_num: int = 5) -> None:
        super().__init__(chapter_num)
        self._gears: list = []
        self._drag: _Gear | None = None
        self._dx = 0.0
        self._dy = 0.0
        self._solved = False
        self._solved_t = 0.0
        self._spark_t = 0.0
        self._snd_tick = self._snd(":resources:sounds/rockHit2.ogg")

    def setup(self) -> None:
        self._gears = []
        self._drag = None
        self._solved = False
        self._solved_t = 0.0
        self.ps.clear()

        lv = _LEVELS[self.level - 1]
        sc, sr = lv["src"]
        tc, tr = lv["tgt"]
        self._gears.append(_Gear(sc, sr, fixed=True, src=True))
        self._gears.append(_Gear(tc, tr, fixed=True, tgt=True))
        for fc, fr in lv["fixed"]:
            self._gears.append(_Gear(fc, fr, fixed=True))
        for _ in range(lv["par"]):
            g = _Gear(-999, -999)
            g.placed = False
            self._gears.append(g)

    def _propagate(self) -> None:
        for g in self._gears:
            g.powered = False
        src = next((g for g in self._gears if g.src), None)
        if not src:
            return
        src.powered = True
        q = [src]
        while q:
            cur = q.pop(0)
            for other in self._gears:
                if (not other.powered and other.placed
                        and other.adjacent(cur)):
                    other.powered = True
                    q.append(other)
        self._solved = any(g.tgt and g.powered for g in self._gears)

    def _placed(self) -> list:
        return [g for g in self._gears if g.placed]

    def _inventory(self) -> list:
        return [g for g in self._gears if not g.fixed and not g.placed]

    def on_update(self, dt: float) -> None:
        self._propagate()
        for i, g in enumerate(self._placed()):
            if g.powered:
                g.angle += (1 if i % 2 == 0 else -1) * 90 * dt

        if self._solved:
            self._spark_t += dt
            if self._spark_t >= 0.2:
                self._spark_t = 0.0
                pl = self._placed()
                for i, g1 in enumerate(pl):
                    for g2 in pl[i + 1:]:
                        if g1.adjacent(g2) and g1.powered and g2.powered:
                            self.ps.emit_spark(
                                (g1.cx + g2.cx) / 2,
                                (g1.cy + g2.cy) / 2,
                            )
            self._solved_t += dt
            if self._solved_t >= 2.5:
                self.score += 300
                self._level_done()
                return
        self.ps.update(dt)

    def on_draw(self) -> None:
        import math
        self.clear()
        self.background_color = (16, 14, 22)

        # ── Фоновые декоративные трубы и заклёпки ────────────────────────────
        pipe_cols = [(28, 22, 40), (32, 26, 45)]
        for xi in range(0, SCREEN_W + 60, 60):
            col = pipe_cols[xi // 60 % 2]
            arcade.draw_rectangle_filled(xi, SCREEN_H // 2, 3, SCREEN_H, col)
        for yi in range(0, SCREEN_H + 60, 60):
            col = pipe_cols[yi // 60 % 2]
            arcade.draw_rectangle_filled(SCREEN_W // 2, yi, SCREEN_W, 3, col)
        # Заклёпки на пересечениях
        for xi in range(0, SCREEN_W + 60, 60):
            for yi in range(0, SCREEN_H + 60, 60):
                arcade.draw_circle_filled(xi, yi, 3, (40, 34, 55))

        # ── Чертёжная сетка поля ─────────────────────────────────────────────
        for r in range(G_ROWS):
            for c in range(G_COLS):
                gx = OX + c * G_CELL + G_CELL // 2
                gy = OY + r * G_CELL + G_CELL // 2
                # Ячейка с градиентной рамкой
                arcade.draw_rectangle_filled(
                    gx, gy, G_CELL - 2, G_CELL - 2, (22, 20, 34))
                arcade.draw_rectangle_outline(
                    gx, gy, G_CELL - 2, G_CELL - 2, (55, 48, 72), 1)
                # Уголки ячейки
                for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    corner_x = gx + sx * (G_CELL // 2 - 6)
                    corner_y = gy + sy * (G_CELL // 2 - 6)
                    arcade.draw_point(corner_x, corner_y, (75, 60, 95), 3)

        # ── Линии передачи питания между смежными ─────────────────────────────
        placed = self._placed()
        for i, g1 in enumerate(placed):
            for g2 in placed[i + 1:]:
                if g1.adjacent(g2) and g1.powered and g2.powered:
                    # Яркая линия
                    arcade.draw_line(
                        g1.cx, g1.cy, g2.cx, g2.cy,
                        (180, 140, 50, 160), 3)
                    # Искры
                    mx, my = (g1.cx + g2.cx) / 2, (g1.cy + g2.cy) / 2
                    arcade.draw_circle_filled(mx, my, 5, (240, 200, 80, 200))

        # ── Шестерёнки ───────────────────────────────────────────────────────
        for g in placed:
            self._draw_gear(g.cx, g.cy, 32, self._gear_color(g), g.angle)
            # Подпись источника/цели
            if g.src:
                arcade.draw_text("▶", g.cx, g.cy - 48,
                                  (100, 210, 140), 13,
                                  anchor_x="center", anchor_y="center")
            if g.tgt:
                arcade.draw_text("★", g.cx, g.cy - 48,
                                  (220, 110, 50), 13,
                                  anchor_x="center", anchor_y="center")

        # ── Инвентарь (полочка внизу) ─────────────────────────────────────────
        inv = self._inventory()
        if inv:
            shelf_w = len(inv) * 55 + 20
            shelf_x = SCREEN_W // 2
            arcade.draw_rectangle_filled(
                shelf_x, 55, shelf_w, 66, (24, 20, 36))
            arcade.draw_rectangle_outline(
                shelf_x, 55, shelf_w, 66, (70, 55, 95), 2)
            arcade.draw_text(
                "ЗАПАС", shelf_x, 88,
                (90, 75, 120), 10, anchor_x="center")
        sx_inv = SCREEN_W // 2 - len(inv) * 55 // 2
        for i, g in enumerate(inv):
            if g is not self._drag:
                self._draw_gear(sx_inv + i * 55, 55, 22, (90, 80, 115), g.angle)

        if self._drag and not self._drag.placed:
            self._draw_gear(self._dx, self._dy, 22, (110, 170, 110), 0.0)

        self.ps.draw()

        # ── Сообщение о победе ────────────────────────────────────────────────
        if self._solved:
            # Золотое свечение за текстом
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, SCREEN_H - 52,
                420, 44, (40, 30, 10, 180))
            arcade.draw_rectangle_outline(
                SCREEN_W // 2, SCREEN_H - 52,
                420, 44, (200, 160, 40), 2)
            arcade.draw_text(
                "⚙  МЕХАНИЗМ ЗАПУЩЕН!  ⚙",
                SCREEN_W // 2, SCREEN_H - 52,
                (220, 180, 60), 24,
                anchor_x="center", anchor_y="center", bold=True,
            )

        with self.gcam.activate():
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (12, 10, 20, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (65, 50, 90, 130), 1)
            self._hud()
            hints = [
                "Ур.1: соедини зелёный источник с красной целью по прямой",
                "Ур.2: путь Г-образный — левая фиксированная шестерня вниз",
                "Ур.3: веди цепь по средней строке (верхняя шестерня — ловушка)",
            ]
            arcade.draw_text(
                f"💡 {hints[self.level - 1]}",
                SCREEN_W // 2, 14, (120, 110, 145), 11, anchor_x="center",
            )

    @staticmethod
    def _gear_color(g: _Gear) -> tuple:
        if g.src:
            return (120, 220, 160)
        if g.tgt:
            return (220, 120, 60)
        return (80, 200, 120) if g.powered else (120, 120, 145)

    @staticmethod
    def _draw_gear(cx: float, cy: float, r: int,
                   color: tuple, angle: float) -> None:
        arcade.draw_circle_filled(cx, cy, r, color)
        arcade.draw_circle_outline(cx, cy, r, (20, 20, 30), 2)
        for i in range(8):
            a = math.radians(angle + i * 45)
            tx = cx + math.cos(a) * (r + 8)
            ty = cy + math.sin(a) * (r + 8)
            arcade.draw_rectangle_filled(tx, ty, 8, 5, color)
        arcade.draw_circle_filled(cx, cy, r // 3, (30, 30, 40))

    def on_mouse_press(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn == arcade.MOUSE_BUTTON_LEFT and self._menu_btn_hit(x, y):
            self._go_menu(); return
        if btn != arcade.MOUSE_BUTTON_LEFT:
            return
        inv = self._inventory()
        sx = SCREEN_W // 2 - len(inv) * 55 // 2
        for i, g in enumerate(inv):
            if abs(x - (sx + i * 55)) < 25 and abs(y - 55) < 25:
                self._drag = g
                self._dx, self._dy = x, y
                return
        for g in self._placed():
            if not g.fixed and abs(x - g.cx) < 32 and abs(y - g.cy) < 32:
                g.placed = False
                self._drag = g
                self._dx, self._dy = x, y
                return

    def on_mouse_motion(self, x: float, y: float, _: float, __: float) -> None:
        if self._drag:
            self._dx, self._dy = x, y

    def on_mouse_release(self, x: float, y: float, btn: int, _m: int) -> None:
        if btn != arcade.MOUSE_BUTTON_LEFT or not self._drag:
            return
        col = round((x - OX - G_CELL // 2) / G_CELL)
        row = round((y - OY - G_CELL // 2) / G_CELL)
        occupied = any(
            g is not self._drag and g.placed
            and g.col == col and g.row == row
            for g in self._gears
        )
        if 0 <= col < G_COLS and 0 <= row < G_ROWS and not occupied:
            self._drag.col = col
            self._drag.row = row
            self._drag.placed = True
            self._play(self._snd_tick)
        self._drag = None
