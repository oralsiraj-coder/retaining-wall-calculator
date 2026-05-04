import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# ==================================================
# VIEWPORT SETTINGS (FIXED)
# ==================================================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

DIM_LW = 0.8
EXT_LW = 0.6

# ==================================================
# DIMENSION DRAWING
# ==================================================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        y1, y2 = p1[1], p2[1]

        ax.add_patch(FancyArrowPatch(
            (x, y1), (x, y2),
            arrowstyle="<->", lw=DIM_LW, mutation_scale=10
        ))
        ax.plot([p1[0], x], [y1, y1], lw=EXT_LW, color="black")
        ax.plot([p2[0], x], [y2, y2], lw=EXT_LW, color="black")

        ax.text(x - 0.18, (y1 + y2) / 2,
                label, rotation=90, ha="center", va="center")
    else:
        y = p1[1] + offset
        x1, x2 = p1[0], p2[0]

        ax.add_patch(FancyArrowPatch(
            (x1, y), (x2, y),
            arrowstyle="<->", lw=DIM_LW, mutation_scale=10
        ))
        ax.plot([x1, x1], [p1[1], y], lw=EXT_LW, color="black")
        ax.plot([x2, x2], [p2[1], y], lw=EXT_LW, color="black")

        ax.text((x1 + x2) / 2, y + 0.12,
                label, ha="center", va="bottom")

# ==================================================
# SCALE COMPUTATION (GEOMETRY ONLY)
# ==================================================
def compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb):
    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt
    total_H = base_h + max(Ha, Hp)
    sx = (VIEW_W * MARGIN) / base_L
    sy = (VIEW_H * MARGIN) / total_H
    return min(sx, sy)

# ==================================================
# WALL DRAWING (NO CALCULATIONS)
# ==================================================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    scale = compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb)

    # Scale geometry
    Ha *= scale
    Hw *= scale
    Hp *= scale
    Th *= scale
    Tt *= scale
    Lh *= scale
    Lt *= scale
    Tsb *= scale

    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt

    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8

    fig, ax = plt.subplots(figsize=(7, 7))

    # Concrete
    ax.add_patch(Rectangle((x0, y0), base_L, base_h,
                           fc="0.75", ec="black", lw=2))
    ax.add_patch(Rectangle((x0 + Lh, y0 + base_h), Tsb, Ha,
                           fc="0.75", ec="black", lw=2))

    # Active soil
    ax.add_patch(Rectangle((x0, y0 + base_h), Lh, Ha,
                           fc="#f4a261", alpha=0.85))

    # Passive soil
    ax.add_patch(Rectangle((x0 + Lh + Tsb, y0 + base_h), Lt, Hp,
                           fc="#b7e4c7", alpha=0.85))

    # Water
    if Hw > 0:
        ax.add_patch(Rectangle(
            (x0, y0 + base_h + Ha - Hw),
            Lh, Hw, fc="#74c0fc", alpha=0.6))

    # Soil labels
    ax.text(x0 + Lh * 0.5, y0 + base_h + Ha * 0.5,
        f"Active soil\n"
        f"γ = {gamma_a:.1f} kN/m³\n"
        f"φ = {phi_a:.1f}°\n"
        f"c = {c_a:.1f} kPa",
        ha="center", va="center", fontsize=9)

    ax.text(x0 + Lh + Tsb + Lt * 0.5, y0 + base_h + Hp * 0.5,
        f"Passive soil\n"
        f"γ = {gamma_p:.1f} kN/m³\n"
        f"φ = {phi_p:.1f}°\n"
        f"c = {c_p:.1f} kPa",
        ha="center", va="center", fontsize=9)

    # Dimensions
    draw_dimension(ax, (x0, y0 + base_h),
                   (x0, y0 + base_h + Ha),
                   "Ha", offset=-0.6, vertical=True)
    draw_dimension(ax, (x0, y0 + base_h + Ha - Hw),
                   (x0, y0 + base_h + Ha),
                   "Hw", offset=-1.0, vertical=True)
    draw_dimension(ax, (x0 + base_L, y0 + base_h),
                   (x0 + base_L, y0 + base_h + Hp),
                   "Hp", offset=0.6, vertical=True)

    draw_dimension(ax, (x0, y0),
                   (x0, y0 + Th),
                   "Th", offset=-0.6, vertical=True)
    draw_dimension(ax, (x0 + base_L, y0),
                   (x0 + base_L, y0 + Tt),
                   "Tt", offset=0.6, vertical=True)

    draw_dimension(ax, (x0, y0),
                   (x0 + Lh, y0),
                   "Lh", offset=-0.6)
    draw_dimension(ax, (x0 + Lh, y0),
                   (x0 + Lh + Tsb, y0),
                   "Tsb", offset=-0.6)
    draw_dimension(ax, (x0 + Lh + Tsb, y0),
                   (x0 + base_L, y0),
                   "Lt", offset=-0.6)

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retaining Wall Geometry with Soil Parameters")

    return fig

# ==================================================
# STREAMLIT UI
# ==================================================
st.title("🧱 Retaining Wall Geometry Tool")

st.sidebar.header("Geometry inputs (m)")
Ha = st.sidebar.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.sidebar.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)
Lh = st.sidebar.number_input("Heel length Lh", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)

st.sidebar.header("Active soil (input only)")
gamma_a = st.sidebar.number_input("γₐ (kN/m³)", 14.0, 25.0, 18.0)
phi_a   = st.sidebar.number_input("φₐ (°)", 0.0, 45.0, 30.0)
c_a     = st.sidebar.number_input("cₐ (kPa)", 0.0, 50.0, 0.0)

st.sidebar.header("Passive soil (input only)")
gamma_p = st.sidebar.number_input("γₚ (kN/m³)", 14.0, 25.0, 18.0)
phi_p   = st.sidebar.number_input("φₚ (°)", 0.0, 45.0, 35.0)
c_p     = st.sidebar.number_input("cₚ (kPa)", 0.0, 50.0, 0.0)

fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
                gamma_a, phi_a, c_a,
                gamma_p, phi_p, c_p)

st.pyplot(fig)
