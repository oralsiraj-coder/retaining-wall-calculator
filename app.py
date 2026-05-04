import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np

# =======================
# VIEWPORT
# =======================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4
DRAFT_GAP = 0.1

# =======================
# DIMENSIONS
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
        ax.text(
            x - 0.15, (p1[1] + p2[1]) / 2,
            label, rotation=90,
            ha="center", va="center", fontsize=8
        )

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb):
    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt
    total_H = base_h + max(Ha, Hp)
    return min(
        (VIEW_W * MARGIN) / base_L,
        (VIEW_H * MARGIN) / total_H
    )

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb, beta):

    scale = compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb)

    # Scale geometry
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

    # =======================
    # ACTIVE SOIL (CORRECT – SLOPES DOWNWARD)
    x_left = x0 + gap
    x_right = x0 + Lh_s - gap

    y_bottom = y0 + base_h + gap
    y_top_left = y_bottom + Ha_s

    # Vertical drop over heel
    dy = Lh_s * np.tan(beta_rad)
    y_top_right = y_top_left - dy

    active_poly = [
        (x_left, y_bottom),
        (x_right, y_bottom),
        (x_right, y_top_right),
        (x_left, y_top_left)
    ]

    ax.add_patch(Polygon(
        active_poly,
        closed=True,
        facecolor="#f4a261",
        edgecolor="none",
        alpha=0.85
    ))

    # =======================
    # WATER (PARALLEL TO GROUND)
    if Hw > 0:
        y_wl_left = y_top_left
        y_wl_right = y_top_right
        y_wb_left = y_wl_left - Hw_s
        y_wb_right = y_wl_right - Hw_s

        water_poly = [
            (x_left, y_wb_left),
            (x_right, y_wb_right),
            (x_right, y_wl_right),
            (x_left, y_wl_left)
        ]

        ax.add_patch(Polygon(
            water_poly,
            closed=True,
            facecolor="#74c0fc",
            edgecolor="none",
            alpha=0.6
        ))

        ax.plot(
            [x_left, x_right],
            [y_wl_left, y_wl_right],
            linestyle="--",
            color="#1c7ed6"
        )

        draw_dimension(
            ax,
            (x_left - 0.4, y_wb_left),
            (x_left - 0.4, y_wl_left),
            f"Hw = {Hw:.2f} m",
            vertical=True
        )

    # =======================
    # PASSIVE SOIL
    ax.add_patch(Rectangle(
        (x0 + Lh_s + Tsb_s + gap, y0 + base_h + gap),
        Lt_s - gap,
        Hp_s - gap,
        fc="#b7e4c7",
        ec="none",
        alpha=0.85
    ))

    # =======================
    # CONCRETE
    ax.add_patch(Rectangle(
        (x0, y0),
        base_L, base_h,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh_s, y0 + base_h),
        Tsb_s, Ha_s,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))

    # =======================
    # GROUND SURFACE
    ax.plot(
        [x_left, x_right],
        [y_top_left, y_top_right],
        linestyle="--",
        color="black"
    )

    ax.text(
        (x_left + x_right) / 2,
        (y_top_left + y_top_right) / 2 + 0.1,
        f"β = {beta:.0f}°",
        ha="center",
        fontsize=8
    )

    # =======================
    # DIMENSIONS
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
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retaining Wall – Backfill Sloping Downward")

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
beta = st.sidebar.number_input(
    "Backfill slope β (deg from horizontal, downward)",
    0.0, 45.0, 10.0
)

fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb, beta)
st.pyplot(fig)
