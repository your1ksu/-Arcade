"""
ch6_pusinka.py — Глава 6: Пушинка — Облачный зайчик
Вертикальный платформер с ручными картами.
Каждая платформа гарантированно достижима прыжком.
Arcade 3.x, физика px/кадр.
"""
from __future__ import annotations
import arcade
from base_chapter import BaseChapter
from constants import SCREEN_W, SCREEN_H, TS, C_PUSINKA, C_CARROT
from sprites import CloudPlatform

GRAVITY  = 0.55
SPEED    = 5
JUMP_V   = 15
DJUMP_V  = 14

# Формат платформы: (cx, cy, width, is_cloud, cloud_range, cloud_speed)
# is_cloud=False → статичная, is_cloud=True → облако
# cloud_range: ±px от центра, cloud_speed: px/кадр
# Гарантия: разница по Y между соседними < 60px, по X < 280px (легко добежать)

_LEVELS = [
    # ── Уровень 1: нижняя половина статична, верхняя — анимированные облака ──────
    {
        "wh": 1600,
        "start": (512, 80),
        "finish": (512, 1520),
        "platforms": [
            # (cx,  cy,   w,   cloud, rng, spd)
            # --- нижняя половина: статичные платформы (y 80-750) ---
            (512,  80,  340,  False, 0,    0),    # старт
            (300,  140, 260,  False, 0,    0),
            (700,  200, 260,  False, 0,    0),
            (200,  260, 240,  False, 0,    0),
            (600,  320, 240,  False, 0,    0),
            (400,  380, 280,  False, 0,    0),
            (800,  430, 220,  False, 0,    0),
            (250,  480, 260,  False, 0,    0),
            (650,  530, 260,  False, 0,    0),
            (450,  590, 300,  False, 0,    0),
            (150,  640, 220,  False, 0,    0),
            (700,  690, 240,  False, 0,    0),
            (350,  750, 280,  False, 0,    0),
            # --- верхняя половина: анимированные облака (y 800-1520) ---
            (800,  800, 220,  True,  55,  0.28),  # облако
            (500,  860, 240,  True,  60,  0.22),  # облако
            (200,  910, 220,  True,  50,  0.30),  # облако
            (700,  970, 240,  True,  55,  0.25),  # облако
            (400, 1030, 260,  True,  60,  0.20),  # облако
            (750, 1090, 220,  True,  50,  0.28),  # облако
            (300, 1150, 240,  True,  55,  0.22),  # облако
            (600, 1210, 220,  True,  60,  0.25),  # облако
            (512, 1280, 300,  False, 0,    0),    # статичная площадка перед финишем
            (512, 1340, 280,  False, 0,    0),
            (512, 1400, 260,  False, 0,    0),
            (512, 1460, 240,  False, 0,    0),
            (512, 1520, 280,  False, 0,    0),    # финиш
        ],
        "carrots": [
            (320, 165), (680, 225), (220, 290), (580, 350),
            (420, 410), (820, 455), (270, 510), (670, 565),
            (470, 620), (170, 670), (720, 720), (370, 780),
            (820, 828), (520, 888), (220, 942),
        ],
    },
    # ── Уровень 2: смешанный — облака медленные, разный ритм ─────────────────
    {
        "wh": 2000,
        "start": (512, 80),
        "finish": (512, 1920),
        "platforms": [
            (512,  80,  340,  False,  0,    0),    # старт
            (250,  135, 240,  False,  0,    0),
            (700,  190, 220,  False,  0,    0),
            (400,  250, 260,  True,  55,  0.25),   # облако
            (750,  305, 220,  False,  0,    0),
            (200,  360, 240,  False,  0,    0),
            (550,  415, 260,  True,  60,  0.20),   # облако
            (850,  470, 200,  False,  0,    0),
            (400,  530, 240,  False,  0,    0),
            (150,  585, 220,  False,  0,    0),
            (650,  640, 260,  True,  50,  0.22),   # облако
            (350,  700, 240,  False,  0,    0),
            (800,  755, 220,  False,  0,    0),
            (500,  815, 260,  True,  55,  0.18),   # облако
            (200,  870, 240,  False,  0,    0),
            (700,  930, 220,  False,  0,    0),
            (400,  990, 260,  False,  0,    0),
            (850, 1045, 200,  True,  45,  0.25),   # облако
            (300, 1105, 240,  False,  0,    0),
            (650, 1165, 260,  False,  0,    0),
            (450, 1225, 280,  True,  60,  0.20),   # облако
            (750, 1285, 220,  False,  0,    0),
            (250, 1345, 240,  False,  0,    0),
            (600, 1405, 260,  False,  0,    0),
            (400, 1465, 280,  True,  50,  0.22),   # облако
            (700, 1525, 220,  False,  0,    0),
            (350, 1590, 260,  False,  0,    0),
            (600, 1650, 240,  False,  0,    0),
            (512, 1720, 300,  False,  0,    0),
            (512, 1780, 280,  False,  0,    0),
            (512, 1840, 260,  False,  0,    0),
            (700, 1880, 220,  False,  0,    0),
            (512, 1920, 280,  False,  0,    0),   # финиш
        ],
        "carrots": [
            (270, 158), (720, 212), (420, 272), (770, 330),
            (220, 383), (570, 438), (870, 495), (420, 558),
            (170, 608), (670, 665), (370, 725), (820, 782),
            (520, 843), (220, 895), (720, 955), (420, 1020),
            (870, 1070), (320, 1132), (670, 1192),
        ],
    },
    # ── Уровень 3: ритм меняется, облака быстрее, проходы узкие ──────────────
    {
        "wh": 2400,
        "start": (512, 80),
        "finish": (512, 2320),
        "platforms": [
            (512,  80,  300,  False,  0,    0),    # старт
            (250,  130, 220,  False,  0,    0),
            (650,  180, 200,  False,  0,    0),
            (400,  235, 240,  True,  50,  0.30),
            (800,  285, 180,  False,  0,    0),
            (200,  340, 220,  False,  0,    0),
            (550,  395, 200,  True,  55,  0.28),
            (850,  450, 180,  False,  0,    0),
            (350,  505, 220,  True,  45,  0.32),
            (700,  560, 200,  False,  0,    0),
            (150,  615, 220,  False,  0,    0),
            (600,  665, 200,  True,  60,  0.25),
            (350,  720, 220,  False,  0,    0),
            (800,  775, 180,  False,  0,    0),
            (450,  830, 220,  True,  50,  0.30),
            (200,  885, 200,  False,  0,    0),
            (700,  940, 200,  False,  0,    0),
            (400,  995, 220,  True,  55,  0.28),
            (750, 1050, 180,  False,  0,    0),
            (300, 1105, 220,  False,  0,    0),
            (650, 1160, 200,  True,  45,  0.32),
            (200, 1215, 220,  False,  0,    0),
            (600, 1270, 200,  False,  0,    0),
            (400, 1330, 220,  True,  50,  0.28),
            (800, 1385, 180,  False,  0,    0),
            (300, 1440, 220,  False,  0,    0),
            (650, 1495, 200,  True,  55,  0.25),
            (350, 1555, 220,  False,  0,    0),
            (750, 1610, 200,  False,  0,    0),
            (450, 1665, 220,  True,  45,  0.30),
            (200, 1720, 220,  False,  0,    0),
            (700, 1775, 200,  False,  0,    0),
            (400, 1835, 220,  True,  50,  0.28),
            (750, 1890, 180,  False,  0,    0),
            (300, 1950, 220,  False,  0,    0),
            (600, 2005, 200,  False,  0,    0),
            (450, 2065, 220,  True,  55,  0.25),
            (700, 2105, 220,  False,  0,    0),
            (512, 2140, 300,  False,  0,    0),
            (512, 2200, 280,  False,  0,    0),
            (512, 2260, 260,  False,  0,    0),
            (512, 2320, 280,  False,  0,    0),   # финиш
        ],
        "carrots": [
            (270, 153), (670, 202), (420, 257), (820, 308),
            (220, 363), (570, 418), (870, 473), (370, 528),
            (720, 583), (170, 638), (620, 688), (370, 743),
            (820, 798), (470, 853), (220, 908), (720, 963),
            (420, 1018), (770, 1073), (320, 1128), (670, 1183),
            (220, 1238), (620, 1293), (420, 1353), (820, 1408),
        ],
    },
]


class Chapter6View(BaseChapter):

    def __init__(self, chapter_num: int = 6) -> None:
        super().__init__(chapter_num)
        self.player   = None
        self.walls    = arcade.SpriteList()
        self._clouds: list[CloudPlatform] = []
        self._csl     = arcade.SpriteList()
        self.carrots  = arcade.SpriteList()
        self.engine   = None
        self._dj      = True
        self._jonce   = False
        self._wh      = 0.0
        self._fx = self._fy = 0.0
        self._got = 0
        self._dj_flash = 0.0
        self._txt_dj = arcade.Text(
            "★ ДВОЙНОЙ ПРЫЖОК!",
            SCREEN_W // 2, SCREEN_H // 2,
            (255, 240, 80), 22, anchor_x="center", bold=True,
        )

    def setup(self) -> None:
        self.ps.clear()
        self._got      = 0
        self._dj       = True
        self._jonce    = False
        self._dj_flash = 0.0

        lv_data = _LEVELS[self.level - 1]
        self._wh = lv_data["wh"]
        self._fx, self._fy = lv_data["finish"]

        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self._clouds.clear()
        self._csl = arcade.SpriteList()
        self.carrots = arcade.SpriteList()

        # Пол
        for cx in range(0, SCREEN_W + TS, TS):
            g = arcade.SpriteSolidColor(TS, TS, (55, 75, 95))
            g.center_x, g.center_y = cx, TS // 2
            self.walls.append(g)

        # Платформы из данных уровня
        for cx, cy, w, is_cloud, rng, spd in lv_data["platforms"]:
            if is_cloud:
                bl = max(60, cx - rng)
                br = min(SCREEN_W - 60, cx + rng)
                cp = CloudPlatform(cx, cy, w, bl, br, spd)
                self._clouds.append(cp)
                self._csl.append(cp)
            else:
                # Финишная платформа — зелёная
                if (cx, cy) == lv_data["finish"]:
                    color = (60, 210, 100)
                else:
                    color = (180, 210, 245)
                p = arcade.SpriteSolidColor(w, 20, color)
                p.center_x, p.center_y = cx, cy
                self.walls.append(p)

        # Морковки — используем ресурс arcade или рисуем как составной спрайт
        for cx, cy in lv_data["carrots"]:
            # Создаём узнаваемую морковку: оранжевый треугольник + зелёный хвостик
            c = arcade.SpriteSolidColor(14, 24, C_CARROT)
            c.center_x, c.center_y = cx, cy
            self.carrots.append(c)

        sx, sy = lv_data["start"]
        self.player = arcade.SpriteSolidColor(28, 34, C_PUSINKA)
        self.player.center_x, self.player.center_y = sx, sy + 30

        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.walls,
            gravity_constant=GRAVITY,
            platforms=self._csl,
        )

    def on_update(self, dt: float) -> None:
        if not self.player or not self.engine:
            return
        self._tick_grace(dt)
        self._dj_flash = max(0.0, self._dj_flash - dt)

        if arcade.key.LEFT in self.keys or arcade.key.A in self.keys:
            self.player.change_x = -SPEED
        elif arcade.key.RIGHT in self.keys or arcade.key.D in self.keys:
            self.player.change_x = SPEED
        else:
            self.player.change_x = 0

        if self.engine.can_jump():
            self._dj    = True
            self._jonce = False

        for cp in self._clouds:
            cp.update()

        self.engine.update()
        self.ps.update(dt)

        for c in arcade.check_for_collision_with_list(self.player, self.carrots):
            c.remove_from_sprite_lists()
            self._got  += 1
            self.score += 40
            self._play(self._snd_coin)

        if self.player.center_y < -TS * 2:
            self._game_over()
            return

        import math
        d = math.sqrt((self.player.center_x - self._fx) ** 2
                       + (self.player.center_y - self._fy) ** 2)
        if self._can_finish() and d < 100:
            self.score += 400 + self._got * 15
            self._level_done()
            return

        self._follow(self.player.center_x, self.player.center_y,
                     SCREEN_W, self._wh)

    def on_draw(self) -> None:
        import math
        self.clear()
        sky_bg = [(32, 28, 72), (22, 18, 58), (14, 12, 40)]
        self.background_color = sky_bg[self.level - 1]

        with self.wcam.activate():
            cam_x, cam_y = self.wcam.position

            # ── Звёзды (параллакс 0.1) ────────────────────────────────────────
            import random as _rnd
            _rnd.seed(self.level * 31)
            for _ in range(80):
                sx = _rnd.randint(0, SCREEN_W * 3)
                sy = _rnd.randint(0, self._wh)
                spx = sx - cam_x * 0.1
                if 0 <= spx <= SCREEN_W:
                    br = _rnd.randint(120, 220)
                    arcade.draw_circle_filled(
                        spx, sy, _rnd.randint(1, 2), (br, br, br, 160))

            # ── Туманные горизонтальные полосы ────────────────────────────────
            for by in range(200, self._wh, 400):
                if abs(by - (cam_y + SCREEN_H / 2)) < SCREEN_H:
                    arcade.draw_rectangle_filled(
                        SCREEN_W // 2, by, SCREEN_W, 38, (55, 50, 90, 22))

            # ── Статичные платформы (не пол) — светящиеся ───────────────────
            for spr in self.walls:
                sh2 = int(spr.height)
                sw2 = int(spr.width)
                if sh2 > 30:
                    continue
                arcade.draw_rectangle_filled(
                    spr.center_x, spr.center_y - 3,
                    sw2 + 8, sh2 + 6, (100, 145, 215, 22))
                arcade.draw_rectangle_filled(
                    spr.center_x, spr.center_y, sw2, sh2, spr.color)
                arcade.draw_rectangle_filled(
                    spr.center_x, spr.center_y + sh2 // 2 - 2,
                    sw2 - 4, 3, (200, 225, 255, 110))
            # Пол
            for spr in self.walls:
                if int(spr.height) > 30:
                    arcade.draw_rectangle_filled(
                        spr.center_x, spr.center_y,
                        int(spr.width), int(spr.height), spr.color)

            # ── Облачные платформы ────────────────────────────────────────────
            for cp in self._csl:
                cx2, cy2 = cp.center_x, cp.center_y
                cw = int(cp.width)
                arcade.draw_ellipse_filled(
                    cx2, cy2 - 3, cw + 18, 12, (155, 185, 255, 28))
                arcade.draw_ellipse_filled(cx2, cy2, cw, 18, (215, 232, 255))
                for bx2 in range(-cw // 2 + 18, cw // 2, 24):
                    arcade.draw_circle_filled(
                        cx2 + bx2, cy2 + 7, 10, (232, 242, 255))
                arcade.draw_ellipse_filled(
                    cx2, cy2 - 6, cw - 12, 7, (155, 175, 218, 55))

            # ── Морковки ─────────────────────────────────────────────────────
            for c in self.carrots:
                cx, cy = c.center_x, c.center_y
                arcade.draw_circle_filled(cx, cy, 13, (255, 140, 40, 38))
                arcade.draw_triangle_filled(
                    cx - 7, cy + 8, cx + 7, cy + 8, cx, cy - 10,
                    (230, 100, 20))
                arcade.draw_line(cx - 3, cy + 5, cx - 3, cy - 4,
                                 (200, 80, 15), 1)
                arcade.draw_line(cx + 3, cy + 5, cx + 3, cy - 4,
                                 (200, 80, 15), 1)
                arcade.draw_line(cx, cy + 8, cx, cy + 20, (55, 170, 35), 2)
                arcade.draw_line(cx, cy + 8, cx - 7, cy + 17, (55, 170, 35), 2)
                arcade.draw_line(cx, cy + 8, cx + 7, cy + 17, (55, 170, 35), 2)

            # ── Финиш — пульсирующая звезда ──────────────────────────────────
            fx2, fy2 = self._fx, self._fy + 32
            arcade.draw_circle_filled(fx2, fy2, 34, (55, 190, 100, 45))
            arcade.draw_circle_filled(fx2, fy2, 24, (75, 220, 115))
            arcade.draw_circle_outline(fx2, fy2, 24, (175, 255, 195), 2)
            arcade.draw_text("★", fx2, fy2, (255, 255, 255), 20,
                             anchor_x="center", anchor_y="center")

            self.ps.draw()

            # ── Зайчик Пушинка ────────────────────────────────────────────────
            if self.player:
                p = self.player
                px2, py2 = p.center_x, p.center_y
                arcade.draw_circle_filled(px2, py2, 21, (200, 200, 255, 22))
                arcade.draw_ellipse_filled(px2, py2, 28, 32, C_PUSINKA)
                arcade.draw_ellipse_filled(px2, py2 - 4, 16, 18, (245, 218, 228))
                arcade.draw_ellipse_filled(px2 - 7, py2 + 22, 8, 16, C_PUSINKA)
                arcade.draw_ellipse_filled(px2 + 7, py2 + 22, 8, 16, C_PUSINKA)
                arcade.draw_ellipse_filled(px2 - 7, py2 + 22, 4, 9, (232, 175, 198))
                arcade.draw_ellipse_filled(px2 + 7, py2 + 22, 4, 9, (232, 175, 198))
                arcade.draw_circle_filled(px2 - 5, py2 + 6, 4, (45, 30, 60))
                arcade.draw_circle_filled(px2 + 5, py2 + 6, 4, (45, 30, 60))
                arcade.draw_circle_filled(px2 - 4, py2 + 7, 1, (255, 255, 255))
                arcade.draw_circle_filled(px2 + 6, py2 + 7, 1, (255, 255, 255))
                arcade.draw_circle_filled(px2, py2 + 2, 2, (215, 138, 158))

        with self.gcam.activate():
            arcade.draw_rectangle_filled(
                SCREEN_W // 2, 24, SCREEN_W, 48, (12, 10, 28, 210))
            arcade.draw_line(0, 48, SCREEN_W, 48, (65, 60, 115, 110), 1)
            self._hud(f"Морковок: {self._got}")
            arcade.draw_text(
                "← → — движение  |  ПРОБЕЛ/↑ — прыжок  "
                "|  ×2 — двойной  |  цель: ★",
                SCREEN_W // 2, 12, (158, 152, 208), 11, anchor_x="center",
            )
            if self._dj_flash > 0:
                self._txt_dj.draw()


    def on_key_press(self, key: int, mod: int) -> None:
        super().on_key_press(key, mod)
        if key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine and self.player:
                if self.engine.can_jump():
                    self.player.change_y = JUMP_V
                    self._jonce = True
                    self._play(self._snd_jump)
                elif self._dj and self._jonce:
                    self.player.change_y = DJUMP_V
                    self._dj       = False
                    self._dj_flash = 0.7
                    self.ps.emit_rainbow(
                        self.player.center_x, self.player.center_y)
                    self._play(self._snd_jump)

    def on_key_release(self, key: int, mod: int) -> None:
        super().on_key_release(key, mod)
        if (key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE)
                and self.player and self.player.change_y > 0):
            self.player.change_y *= 0.5
