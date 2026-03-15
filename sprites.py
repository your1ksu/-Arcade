"""
sprites.py — Chromatic Heroes
Игровые классы спрайтов. Arcade 3.x.
"""

from __future__ import annotations

import math
import random

import arcade

from constants import (
    C_ENEMY, C_BULLET, C_STING, C_WASP,
    ENEMY_SPD, WASP_SPD, BULLET_SPD, STING_SPD, TS,
)


class WalkingEnemy(arcade.SpriteSolidColor):
    """Паtrulирует горизонталь, разворачивается на краях."""

    def __init__(
        self, x: float, y: float,
        patrol: float = TS * 3,
        speed: float = ENEMY_SPD,
        color: tuple = C_ENEMY,
        w: int = 40, h: int = 50,
    ) -> None:
        super().__init__(w, h, color)
        self.center_x, self.center_y = x, y
        self._ox = x
        self._patrol = patrol
        self._spd = speed
        self._dir = 1.0

    def on_update(self, dt: float = 1 / 60) -> None:
        self.center_x += self._spd * self._dir * dt
        if abs(self.center_x - self._ox) >= self._patrol:
            self._dir *= -1


class ShadowEnemy(WalkingEnemy):
    """Глава 2: замирает в свете."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x, y, patrol=TS * 2, speed=60.0,
            color=(30, 30, 50), w=36, h=48,
        )
        self.frozen = False

    def on_update(self, dt: float = 1 / 60) -> None:
        if not self.frozen:
            super().on_update(dt)


class Wasp(arcade.SpriteSolidColor):
    """Летит к улью."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(34, 22, C_WASP)
        self.center_x, self.center_y = x, y
        self._tx = 0.0
        self._ty = 0.0

    def set_target(self, tx: float, ty: float) -> None:
        self._tx, self._ty = tx, ty

    def on_update(self, dt: float = 1 / 60) -> None:
        dx = self._tx - self.center_x
        dy = self._ty - self.center_y
        d = math.sqrt(dx * dx + dy * dy)
        if d > 1:
            self.center_x += dx / d * WASP_SPD * dt
            self.center_y += dy / d * WASP_SPD * dt
        self.center_y += math.sin(self.center_x * 0.05) * 0.3


class InkBullet(arcade.SpriteSolidColor):
    """Чернильный снаряд."""

    def __init__(self, x: float, y: float, angle: float) -> None:
        super().__init__(12, 12, C_BULLET)
        self.center_x, self.center_y = x, y
        self._vx = math.cos(angle) * BULLET_SPD
        self._vy = math.sin(angle) * BULLET_SPD

    def on_update(self, dt: float = 1 / 60) -> None:
        self.center_x += self._vx * dt
        self.center_y += self._vy * dt


class Stinger(arcade.SpriteSolidColor):
    """Жало пчелы."""

    def __init__(self, x: float, y: float, angle: float) -> None:
        super().__init__(14, 6, C_STING)
        self.center_x, self.center_y = x, y
        self._vx = math.cos(angle) * STING_SPD
        self._vy = math.sin(angle) * STING_SPD
        self.angle = math.degrees(angle)

    def on_update(self, dt: float = 1 / 60) -> None:
        self.center_x += self._vx * dt
        self.center_y += self._vy * dt


class LightAura:
    """
    Мягкий световой круг (Глава 2).
    Рисуется вручную концентрическими кругами (arcade 3 убрал make_soft_circle_texture).
    """

    def __init__(self, radius: int = 200) -> None:
        self._r = radius
        self.center_x: float = 0.0
        self.center_y: float = 0.0

    def set_radius(self, r: int) -> None:
        self._r = r

    def draw(self) -> None:
        """Рисует мягкое световое пятно градиентными кольцами."""
        steps = 10
        for i in range(steps, 0, -1):
            ratio = i / steps
            r = int(self._r * ratio)
            alpha = int(130 * (1.0 - ratio))
            arcade.draw_circle_filled(
                self.center_x, self.center_y, r,
                (255, 200, 100, alpha),
            )


class Flower(arcade.SpriteSolidColor):
    """Цветок с нектаром."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(28, 28, (220, 100, 160))
        self.center_x, self.center_y = x, y
        self.nectar = 10
        self.depleted = False

    def harvest(self, amount: int = 10) -> int:
        if self.depleted:
            return 0
        got = min(amount, self.nectar)
        self.nectar -= got
        if self.nectar <= 0:
            self.depleted = True
            self.color = arcade.color.GRAY
        return got


class CloudPlatform(arcade.SpriteSolidColor):
    """Движущаяся облачная платформа. _spd в px/кадр."""

    def __init__(
        self, x: float, y: float, w: int,
        left: float, right: float, speed: float,
    ) -> None:
        super().__init__(w, 18, (230, 240, 255))
        self.center_x, self.center_y = x, y
        self._left, self._right = left, right
        self._spd = speed

    def update(self) -> None:
        """Движение в px/кадр (без dt)."""
        self.center_x += self._spd
        if self.center_x < self._left or self.center_x > self._right:
            self._spd *= -1

    def on_update(self, dt: float = 1 / 60) -> None:
        self.update()


class Obstacle(arcade.SpriteSolidColor):
    """Препятствие в раннере."""

    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        color = random.choice([
            (180, 60, 60), (60, 120, 180), (60, 180, 80), (180, 150, 40),
        ])
        super().__init__(w, h, color)
        self.center_x, self.center_y = x, y
