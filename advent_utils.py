from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def read_input(day: int) -> str:
    with open(DATA_DIR / f"day{day:02}.txt", encoding="utf-8") as f:
        return f.read()
