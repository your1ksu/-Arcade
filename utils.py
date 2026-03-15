"""
utils.py — Chromatic Heroes
Вспомогательные функции для arcade 3.x.
Содержит шим совместимости: патчит arcade.draw_rectangle_filled /
arcade.draw_rectangle_outline, которые были переименованы в arcade 3.
"""

from __future__ import annotations

import math
import random

import arcade
from arcade.camera import Camera2D

from constants import TS, C_WALL, C_SPIKE, C_SOAP, C_OIL, C_CARROT, C_FINISH


# ── Шим совместимости arcade 2 → arcade 3 ────────────────────────────────────
# arcade 3 переименовал draw_rectangle_* в draw_rect_*.
# Патчим один раз при импорте utils — это покрывает все файлы проекта.

def _compat_rect_filled(cx: float, cy: float, w: float, h: float,
                        color, angle: float = 0) -> None:
    arcade.draw_rect_filled(arcade.XYWH(cx, cy, w, h), color)


def _compat_rect_outline(cx: float, cy: float, w: float, h: float,
                         color, border: float = 1, angle: float = 0) -> None:
    arcade.draw_rect_outline(arcade.XYWH(cx, cy, w, h), color, border)


if not hasattr(arcade, "draw_rectangle_filled"):
    arcade.draw_rectangle_filled = _compat_rect_filled   # type: ignore

if not hasattr(arcade, "draw_rectangle_outline"):
    arcade.draw_rectangle_outline = _compat_rect_outline  # type: ignore


# ── Парсер карт ───────────────────────────────────────────────────────────────
def parse_map(map_data: list, tile_size: int = TS) -> tuple:
    """
    Строковая сетка → SpriteLists.
    Возвращает: walls, spikes, collectibles, enemy_markers,
                player_pos, finish_pos
    Символы: W=стена  X=шип  P=игрок  F=финиш
             S=мыло   O=масло  C=морковь  E=враг
    """
    walls = arcade.SpriteList(use_spatial_hash=True)
    spikes = arcade.SpriteList(use_spatial_hash=True)
    collectibles = arcade.SpriteList()
    enemies = arcade.SpriteList()
    player_pos = [tile_size, tile_size * 2]
    finish_pos = [tile_size * 3, tile_size * 2]
    rows = len(map_data)

    for r, row in enumerate(map_data):
        for c, ch in enumerate(row):
            cx = c * tile_size + tile_size // 2
            cy = (rows - 1 - r) * tile_size + tile_size // 2

            if ch == "W":
                s = arcade.SpriteSolidColor(tile_size, tile_size, C_WALL)
                s.center_x, s.center_y = cx, cy
                walls.append(s)
            elif ch == "X":
                s = arcade.SpriteSolidColor(tile_size - 4, tile_size // 2, C_SPIKE)
                s.center_x, s.center_y = cx, cy
                spikes.append(s)
            elif ch in ("S", "O", "C"):
                color = C_SOAP if ch == "S" else C_OIL if ch == "O" else C_CARROT
                s = arcade.SpriteSolidColor(22, 22, color)
                s.center_x, s.center_y = cx, cy
                collectibles.append(s)
            elif ch == "F":
                s = arcade.SpriteSolidColor(40, tile_size, C_FINISH)
                s.center_x, s.center_y = cx, cy
                s.name = "finish"
                finish_pos[:] = [cx, cy]
                collectibles.append(s)
            elif ch == "E":
                s = arcade.SpriteSolidColor(32, 32, (200, 0, 0))
                s.center_x, s.center_y = cx, cy
                enemies.append(s)
            elif ch == "P":
                player_pos[:] = [cx, cy]

    return walls, spikes, collectibles, enemies, player_pos, finish_pos


# ── Камера arcade 3 ───────────────────────────────────────────────────────────
def make_cameras() -> tuple:
    """Возвращает (world_cam, gui_cam) — Camera2D для arcade 3."""
    return Camera2D(), Camera2D()


def cam_follow(
    cam: Camera2D,
    tx: float, ty: float,
    world_w: float, world_h: float,
    view_w: float = 1024, view_h: float = 768,
) -> None:
    """Плавное следование камеры за объектом с ограничением по границам мира."""
    hw, hh = view_w / 2, view_h / 2
    x = max(hw, min(tx, world_w - hw))
    y = max(hh, min(ty, world_h - hh))
    cx, cy = cam.position
    cam.position = (cx + (x - cx) * 0.12, cy + (y - cy) * 0.12)


# ── Кнопки ────────────────────────────────────────────────────────────────────
def draw_btn(
    text: str, x: float, y: float,
    w: float = 260, h: float = 48,
    bg=(60, 60, 90), fg=(255, 255, 255),
    border=(140, 140, 200), font_size: int = 18,
) -> None:
    arcade.draw_rectangle_filled(x, y, w, h, bg)
    arcade.draw_rectangle_outline(x, y, w, h, border, 2)
    arcade.draw_text(
        text, x, y, fg, font_size,
        anchor_x="center", anchor_y="center", bold=True,
    )


def btn_hit(
    mx: float, my: float,
    bx: float, by: float,
    w: float = 260, h: float = 48,
) -> bool:
    return abs(mx - bx) <= w / 2 and abs(my - by) <= h / 2


# ── HUD-бар ───────────────────────────────────────────────────────────────────
def draw_bar(
    x: float, y: float, w: float, h: float,
    value: float, max_val: float,
    fill, bg=(40, 40, 50), label: str = "",
) -> None:
    ratio = max(0.0, min(1.0, value / max_val))
    arcade.draw_rectangle_filled(x, y, w, h, bg)
    fw = w * ratio
    if fw > 0:
        arcade.draw_rectangle_filled(x - w / 2 + fw / 2, y, fw, h, fill)
    arcade.draw_rectangle_outline(x, y, w, h, (200, 200, 200), 1)
    if label:
        arcade.draw_text(
            label, x - w / 2 + 4, y - 6, (220, 220, 220), 11, bold=True,
        )


# ── Математика ────────────────────────────────────────────────────────────────
def atan2(y: float, x: float) -> float:
    return math.atan2(y, x)


def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
