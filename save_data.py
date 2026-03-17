"""
save_data.py — Chromatic Heroes
Сохранение прогресса: CSV + TXT.
"""

import csv
import os

from constants import SAVE_FILE, PROGRESS_FILE

_unlocked: list = [True] + [False] * 7
_scores: list = [0] * 8


def _write() -> None:
    with open(SAVE_FILE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["chapter", "unlocked", "score"])
        for i in range(8):
            w.writerow([i + 1, int(_unlocked[i]), _scores[i]])
    with open(PROGRESS_FILE, "w", encoding="utf-8") as fh:
        fh.write("Chromatic Heroes — Progress\n")
        for i, ok in enumerate(_unlocked):
            fh.write(
                f"Chapter {i + 1}: "
                f"{'unlocked' if ok else 'locked'}, "
                f"score={_scores[i]}\n"
            )


def load() -> None:
    global _unlocked, _scores
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                idx = int(row["chapter"]) - 1
                if 0 <= idx < 8:
                    _unlocked[idx] = bool(int(row["unlocked"]))
                    _scores[idx] = int(row["score"])
    except (KeyError, ValueError, csv.Error):
        pass


def is_unlocked(ch: int) -> bool:
    return _unlocked[ch - 1] if 1 <= ch <= 8 else False


def get_score(ch: int) -> int:
    return _scores[ch - 1] if 1 <= ch <= 8 else 0


def complete_chapter(ch: int, score: int) -> None:
    if not 1 <= ch <= 8:
        return
    _unlocked[ch - 1] = True
    if score > _scores[ch - 1]:
        _scores[ch - 1] = score
    if ch < 8:
        _unlocked[ch] = True
    _write()


def get_all_unlocked() -> list:
    return list(_unlocked)


def get_all_scores() -> list:
    return list(_scores)


def all_complete() -> bool:
    return all(_unlocked)


def reset_all() -> None:
    """Полностью обнуляет прогресс — только 1-я глава остаётся открытой."""
    global _unlocked, _scores
    _unlocked = [True] + [False] * 7
    _scores   = [0] * 8
    _write()
