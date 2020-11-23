import random
import math

from scipy.interpolate import CubicSpline


def get_noised_line(x0, y0, x1, y1, noise_strength=10, point_count=5) -> list:
    if x0 == x1 and y0 == y1:
        return [(x0, y0)]
    axis_changed = False
    if abs(x1 - x0) < abs(y1 - y0):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        axis_changed = True
    dx = abs(x1 - x0)
    points = [0] + [(2.0 * random.random() - 1) * noise_strength for _ in range(0, point_count)] + [0]
    cs = CubicSpline([0] + [(t + 1) / (point_count + 1) * dx for t in range(0, point_count)] + [dx], points)

    k = (y1 - y0) / (x1 - x0)

    return [(x, y0 + k * (x - x0) + cs(abs(x - x0))) for x in range(x0, x1, 1 if x1 >= x0 else -1)] if not axis_changed else \
        [(y0 + k * (x - x0) + cs(abs(x - x0)), x) for x in range(x0, x1, 1 if x1 >= x0 else -1)]


def get_length(x0, y0, x1, y1) -> float:
    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)