import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# =======================
# FIXED VIEWPORT
# =======================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

# Lineweights
LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4

# ✅ VISIBLE drafting gap (viewport-based)
DRAFT_GAP = 0.02 * min(VIEW_W, VIEW_H)

# =======================
# DIMENSIONS
# =======================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch(
            (x, p1[1]), (x, p2[1]),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8
        ))
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [p2[1], p2[1]], lw=LW_EXT, color="black")
        ax.text(x - 0.15, (p1[1] + p2[1]) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch(
            (p1[0], y), (p2[0], y),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8
        ))
        ax.plot([p1[0], p1[0]], [p1[1], y], lw=LW_EXT, color="black")
        ax.plot([p2[0], p2[0]], [p2[1], y], lw=LW_EXT, color="black")
        ax.text((p1[0] + p2[0]) / 2, y + 0.10,
                label, ha="center", va="bottom", fontsize=8)

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb):
    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt
    return min(
        (VIEW_W * MARGIN) / base_L,
        (VIEW_H * MARGIN) / (base_h + max(Ha, Hp))
    )

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    s = compute_scale(Ha, Hp, Th, Tt, Lh, Lt, Tsb)

    Ha, Hw, Hp = Ha*s, Hw*s, Hp*s
    Th, Tt = Th*s, Tt*s
    Lh, Lt, Tsb = Lh*s, Lt*s, Tsb*s

    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt

    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8
    g = DRAFT_GAP

    fig, ax = plt.subplots(figsize=(7, 7))

    # Active soil (✅ visible gap from stem)
    ax.add_patch(Rectangle(
        (x0 + g, y0 + base_h + g),
        Lh - g, Ha - g,
        fc="#f4a261", ec="none", alpha=0.85
    ))

    # Water (inherits same gap)
    if Hw > 0:
        ax.add_patch(Rectangle(
            (x0 + g, y0 + base_h + Ha - Hw + g),
            Lh - g, Hw - g,
            fc="#74c0fc", ec="none", alpha=0.6
        ))

    # Passive soil (✅ gap from stem)
    ax.add_patch(Rectangle(
        (x0 + Lh + Tsb + g, y0 + base_h + g),
        Lt - g, Hp - g,
        fc="#b7e4c7", ec="none", alpha=0.85
    ))

    # Concrete
    ax.add_patch(Rectangle(
        (x0, y0), base_L, base_h,
        fc="0.9", ec="black", lw=LW_CONCRETE
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh, y0 + base_h),
        Tsb, Ha,
        fc="0.9", ec="black", lw=LW_CONCRETE
    ))

    # Labels
    ax.text(x0 + Lh/2, y0 + base_h + Ha/2,
            f"Active soil\nγ={gamma_a}\nφ={phi_a}°\nc={c_a}",
            ha="center", va="center", fontsize=8)

    ax.text(x0 + Lh + Tsb + Lt/2, y0 + base_h + Hp/2,
            f"Passive soil\nγ={gamma_p}\nφ={phi_p}°\nc={c_p}",
            ha="center", va="center", fontsize=8)

    # Viewport lock
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

# =======================
# UI
# =======================
st.title("🧱 Retaining Wall Geometry Tool (Correct Visible Gaps)")

Ha = st.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.number_input("Passive height Hp", 0.0, 20.0, 3.0)
Th = st.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)
Lh = st.number_input("Heel length Lh", 0.5, 15.0, 3.0)
Lt = st.number_input("Toe length Lt", 0.5, 15.0, 2.0)
Tsb = st.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)

gamma_a = st.number_input("γₐ", 14.0, 25.0, 18.0)
phi_a = st.number_input("φₐ", 0.0, 45.0, 30.0)
c_a = st.number_input("cₐ", 0.0, 50.0, 0.0)

gamma_p = st.number_input("γₚ", 14.0, 25.0, 18.0)
phi_p = st.number_input("φₚ", 0.0, 45.0, 35.0)
c_p = st.number_input("cₚ", 0.0, 50.0, 0.0)

st.pyplot(draw_wall(
    Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb,
    gamma_a, phi_a, c_a,
    gamma_p, phi_p, c_p
))
