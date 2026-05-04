import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# =======================
# FIXED VIEWPORT SETTINGS
# =======================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

# Line weights (CAD-like)
LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4

# Drafting gap (1 mm in model space)
DRAFT_GAP = 0.1

# =======================
# DIMENSION DRAWING
# =======================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        y1, y2 = p1[1], p2[1]

        ax.add_patch(FancyArrowPatch(
            (x, y1), (x, y2),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
        ))
        ax.plot([p1[0], x], [y1, y1], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [y2, y2], lw=LW_EXT, color="black")

        ax.text(x - 0.15, (y1 + y2) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)

    else:
        y = p1[1] + offset
        x1, x2 = p1[0], p2[0]

        ax.add_patch(FancyArrowPatch(
            (x1, y), (x2, y),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
        ))
        ax.plot([x1, x1], [p1[1], y], lw=LW_EXT, color="black")
        ax.plot([x2, x2], [p2[1], y], lw=LW_EXT, color="black")

        ax.text((x1 + x2) / 2, y + 0.1,
                label, ha="center", va="bottom", fontsize=8)

# =======================
# SCALE COMPUTATION
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
# WALL DRAWING
# =======================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    scale = compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb)

    # Scale geometry
    Ha *= scale; Hw *= scale; Hp *= scale
    Th *= scale; Tt *= scale
    Lh *= scale; Lt *= scale; Tsb *= scale

    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt

    gap = DRAFT_GAP
    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8

    fig, ax = plt.subplots(figsize=(7, 7))

    # =======================
    # ACTIVE SOIL
    ax.add_patch(Rectangle(
        (x0 + gap, y0 + base_h + gap),
        Lh - gap,
        Ha - gap,
        fc="#f4a261", ec="none", alpha=0.85
    ))

    # WATER
    if Hw > 0:
        water_bottom = y0 + base_h + Ha - Hw
        water_top = y0 + base_h + Ha

        ax.add_patch(Rectangle(
            (x0 + gap, water_bottom + gap),
            Lh - gap,
            Hw - gap,
            fc="#74c0fc", ec="none", alpha=0.6
        ))

    # PASSIVE SOIL
    ax.add_patch(Rectangle(
        (x0 + Lh + Tsb + gap, y0 + base_h + gap),
        Lt - gap,
        Hp - gap,
        fc="#b7e4c7", ec="none", alpha=0.85
    ))

    # =======================
    # CONCRETE
    ax.add_patch(Rectangle(
        (x0, y0), base_L, base_h,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh, y0 + base_h),
        Tsb, Ha,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))

    # =======================
    # DIMENSIONS
    draw_dimension(ax,
        (x0, y0 + base_h),
        (x0, y0 + base_h + Ha),
        "Ha", offset=-0.6, vertical=True)

    draw_dimension(ax,
        (x0 + base_L, y0 + base_h),
        (x0 + base_L, y0 + base_h + Hp),
        "Hp", offset=0.6, vertical=True)

    # ✅ WATER HEIGHT DIMENSION
    if Hw > 0:
        draw_dimension(ax,
            (x0 + Lh * 0.8, water_bottom),
            (x0 + Lh * 0.8, water_top),
            "Hw", offset=0.25, vertical=True)

    draw_dimension(ax,
        (x0, y0),
        (x0 + base_L, y0),
        "L", offset=-0.6)

    # =======================
    # VIEWPORT
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retaining Wall Geometry")

    return fig

# =======================
# STREAMLIT UI
# =======================
st.title("🧱 Retaining Wall Geometry Tool")

st.sidebar.header("Geometry (m)")
Ha = st.sidebar.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.sidebar.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)
Lh = st.sidebar.number_input("Heel length Lh", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)

st.sidebar.header("Active soil (display only)")
gamma_a = st.sidebar.number_input("γₐ", 14.0, 25.0, 18.0)
phi_a = st.sidebar.number_input("φₐ", 0.0, 45.0, 30.0)
c_a = st.sidebar.number_input("cₐ", 0.0, 50.0, 0.0)
beta = st.sidebar.number_input(
    "Backfill inclination β (deg)",
    min_value=0.0,
    max_value=45.0,
    value=0.0,
    step=1.0
)

st.sidebar.header("Passive soil (display only)")
gamma_p = st.sidebar.number_input("γₚ", 14.0, 25.0, 18.0)
phi_p = st.sidebar.number_input("φₚ", 0.0, 45.0, 35.0)
c_p = st.sidebar.number_input("cₚ", 0.0, 50.0, 0.0)

fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
                gamma_a, phi_a, c_a,
                gamma_p, phi_p, c_p)

st.pyplot(fig)
