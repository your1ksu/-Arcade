"""
main.py — Chromatic Heroes: The Canvas Awakening
Точка входа. Запуск: python main.py
Arcade 3.x.

Этапы проекта:
┌────────────────────────────────────────────────────┬────────────┐
│ Этап                                               │ Дата       │
├────────────────────────────────────────────────────┼────────────┤
│ Описание проекта                                   │ 10.01.2026 │
│ Задание (ТЗ)                                       │ 14.01.2026 │
│ ТЗ + Часть задания выполнена                       │ 20.01.2026 │
│ Код + Работающая часть проекта                     │ 26.01.2026 │
│ Код + Черновик пояснительной записки и презентации │ 01.02.2026 │
│ Код + ПЗ + Презентация + Почти всё работает        │ 07.02.2026 │
│ Всё готово                                         │ 14.02.2026 │
└────────────────────────────────────────────────────┴────────────┘
"""

import sys
import os

# Гарантируем правильный sys.path при запуске из любой папки
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
os.chdir(_HERE)

# ВАЖНО: utils должен быть импортирован ДО arcade.run(),
# чтобы шим совместимости draw_rectangle_* был применён заранее.
import utils  # noqa: F401, E402  (шим arcade 2→3)

import arcade  # noqa: E402

from constants import SCREEN_W, SCREEN_H, TITLE  # noqa: E402
import save_data  # noqa: E402


def main() -> None:
    """Создать окно arcade и запустить главное меню."""
    window = arcade.Window(SCREEN_W, SCREEN_H, TITLE, resizable=False)
    save_data.load()
    from view_menu import MenuView
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
