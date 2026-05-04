import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# =========================
# STYLE PARAMETERS
# =========================
DIM_LW = 0.8
EXT_LW = 0.6

# =========================
# DIMENSION DRAWING
# =========================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x_dim = p1[0] + offset
        y1, y2 = p1[1], p2[1]

        ax.add_patch(FancyArrowPatch(
            (x_dim, y1), (x_dim, y2),
            arrowstyle="<->", lw=DIM_LW, mutation_scale=10
        ))

        ax.plot([p1[0], x_dim], [y1, y1], lw=EXT_LW, color="black")
        ax.plot([p2[0], x_dim], [y2, y2], lw=EXT_LW, color="black")

        ax.text(x_dim - 0.18, (y1 + y2) / 2,
                label, rotation=90, ha="center", va="center")

    else:
        y_dim = p1[1] + offset
        x1, x2 = p1[0], p2[0]

        ax.add_patch(FancyArrowPatch(
            (x1, y_dim), (x2, y_dim),
            arrowstyle="<->", lw=DIM_LW, mutation_scale=10
        ))

        ax.plot([x1, x1], [p1[1], y_dim], lw=EXT_LW, color="black")
        ax.plot([x2, x2], [p2[1], y_dim], lw=EXT_LW, color="black")

