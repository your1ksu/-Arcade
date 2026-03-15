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
    {"fixed": [(2, 2)],          "src": (0, 2), "tgt": (4, 2), "par": 3},
    {"fixed": [(1, 1), (3, 3)],  "src": (0, 0), "tgt": (4, 4), "par": 4},
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
        self.clear()
        self.background_color = (20, 20, 30)
        for r in range(G_ROWS):
            for c in range(G_COLS):
                gx = OX + c * G_CELL + G_CELL // 2
                gy = OY + r * G_CELL + G_CELL // 2
                arcade.draw_rectangle_outline(
                    gx, gy, G_CELL - 4, G_CELL - 4, (50, 55, 65), 1
                )
        for g in self._placed():
            self._draw_gear(g.cx, g.cy, 32,
                            self._gear_color(g), g.angle)
        inv = self._inventory()
        sx = SCREEN_W // 2 - len(inv) * 55 // 2
        for i, g in enumerate(inv):
            if g is not self._drag:
                self._draw_gear(sx + i * 55, 55, 22, (80, 80, 100), g.angle)
        if self._drag and not self._drag.placed:
            self._draw_gear(self._dx, self._dy, 22, (100, 160, 100), 0.0)
        self.ps.draw()
        if self._solved:
            arcade.draw_text(
                "МЕХАНИЗМ ЗАПУЩЕН!",
                SCREEN_W // 2, SCREEN_H - 50,
                (80, 230, 120), 28, anchor_x="center", bold=True,
            )
        with self.gcam.activate():
            self._hud()
            arcade.draw_text(
                "Перетащи шестерёнки мышью (ЛКМ)",
                SCREEN_W // 2, 14, (140, 135, 160), 12, anchor_x="center",
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
