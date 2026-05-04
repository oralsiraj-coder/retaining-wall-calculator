import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np

# =======================
# VIEWPORT & STYLE
# =======================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4
DRAFT_GAP = 0.1

# =======================
# DIMENSION FUNCTION
# =======================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch(
            (x, p1[1]), (x, p2[1]),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
        ))
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [p2[1], p2[1]], lw=LW_EXT, color="black")
        ax.text(x - 0.15, (p1[1] + p2[1]) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb):
    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt
    total_H = base_h + max(Ha, Hp)
    return min((VIEW_W * MARGIN) / base_L,
               (VIEW_H * MARGIN) / total_H)

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb, beta):

    scale = compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb)

    # Scale all geometry
    Ha_s = Ha * scale
    Hw_s = Hw * scale
    Hp_s = Hp * scale
    Th_s = Th * scale
    Tt_s = Tt * scale
    Lh_s = Lh * scale
    Lt_s = Lt * scale
    Tsb_s = Tsb * scale

    base_h = max(Th_s, Tt_s)
    base_L = Lh_s + Tsb_s + Lt_s

    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8
    gap = DRAFT_GAP

    beta_rad = np.deg2rad(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    # ======================================================
    # ACTIVE SOIL – CORRECT TRAPEZOID (β FROM HORIZONTAL)
    # ======================================================
    x_left = x0 + gap                      # wall face
    x_bottom_right = x0 + Lh_s - gap       # heel end at base

    y_bottom = y0 + base_h + gap
    y_top = y_bottom + Ha_s

    # Horizontal retreat of ground surface
    dx = Ha_s / np.tan(beta_rad) if beta > 0 else 0.0
    x_top_right = x_bottom_right - dx

    active_soil = [
        (x_left, y_bottom),           # bottom-left (wall)
        (x_bottom_right, y_bottom),   # bottom-right (heel)
        (x_top_right, y_top),         # top-right (retreated)
        (x_left, y_top)               # top-left (wall)
    ]

    ax.add_patch(Polygon(
        active_soil,
        closed=True,
        facecolor="#f4a261",
        edgecolor="none",
        alpha=0.85
    ))

    # =======================
    # WATER (PARALLEL TO GROUND)
    # =======================
    if Hw > 0:
        y_wb = y_top - Hw_s
        dx_w = Hw_s / np.tan(beta_rad) if beta > 0 else 0.0
        x_wtr = x_bottom_right - dx_w

        water_poly = [
            (x_left, y_wb),
            (x_bottom_right, y_wb),
            (x_wtr, y_top),
            (x_left, y_top)
        ]

        ax.add_patch(Polygon(
            water_poly,
            closed=True,
            facecolor="#74c0fc",
            edgecolor="none",
            alpha=0.6
        ))

        # Water level dashed
        ax.plot(
            [x_left, x_wtr],
            [y_top, y_top],
            linestyle="--",
            color="#1c7ed6"
        )

        draw_dimension(
            ax,
            (x_left - 0.4, y_wb),
            (x_left - 0.4, y_top),
            f"Hw = {Hw:.2f} m",
            vertical=True
        )

    # =======================
    # PASSIVE SOIL
    # =======================
    ax.add_patch(Rectangle(
        (x0 + Lh_s + Tsb_s + gap, y0 + base_h + gap),
        Lt_s - gap,
        Hp_s - gap,
        fc="#b7e4c7",
        ec="none",
        alpha=0.85
    ))

    # =======================
    # CONCRETE WALL
    # =======================
    ax.add_patch(Rectangle(
        (x0, y0),
        base_L, base_h,
        fc="0.85",
        ec="black",
        lw=LW_CONCRETE
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh_s, y0 + base_h),
        Tsb_s,
        Ha_s,
        fc="0.85",
        ec="black",
        lw=LW_CONCRETE
    ))

    # =======================
    # GROUND SURFACE (INCLINED)
    # =======================
    ax.plot(
        [x_left, x_top_right],
        [y_top, y_top],
        linestyle="--",
        color="black"
    )

    ax.text(
        (x_left + x_top_right) / 2,
        y_top + 0.12,
        f"β = {beta:.0f}°",
        ha="center",
        fontsize=8
    )

    # =======================
    # DIMENSIONS
    # =======================
    draw_dimension(
        ax,
        (x0, y0 + base_h),
        (x0, y0 + base_h + Ha_s),
        f"Ha = {Ha:.2f} m",
        offset=-0.6,
        vertical=True
    )

    # =======================
    # VIEW
    # =======================
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retaining Wall – Backfill Inclined from Horizontal")

    return fig

# =======================
# STREAMLIT UI
# =======================
st.title("🧱 Retaining Wall Geometry")

st.sidebar.header("Geometry (m)")
Ha = st.sidebar.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.sidebar.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)
Lh = st.sidebar.number_input("Heel length Lh", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)
beta = st.sidebar.number_input("Backfill inclination β (deg from horizontal)", 0.0, 45.0, 10.0)

fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb, beta)
st.pyplot(fig)
