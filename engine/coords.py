"""Convert provider pitch coordinates into the engine's 0-100 system."""

SB_LENGTH, SB_WIDTH = 120, 80


def from_statsbomb(x: float, y: float) -> tuple[float, float]:
    """StatsBomb (0,0) top-left, 120x80 -> engine (0,0) bottom-left, 0-100."""
    return round(x / SB_LENGTH * 100, 2), round(100 - y / SB_WIDTH * 100, 2)