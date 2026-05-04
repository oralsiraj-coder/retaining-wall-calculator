import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# -------------------------
# Styling parameters
# -------------------------
DIM_LW = 0.8
EXT_LW = 0.6

# -------------------------
# Dimension drawing
# -------------------------
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):

    if vertical:
        y1, y2 = p1[1], p2[1]
        x_dim = p1[0] + offset

        arrow = FancyArrowPatch(
            (x_dim, y1),
            (x_dim, y2),
            arrowstyle='<->',
            mutation_scale=10,
            lw=DIM_LW,
            color='black'
        )
        ax.add_patch(arrow)

        ax.plot([p1[0], x_dim], [y1, y1], lw=EXT_LW, color='black')
        ax.plot([p2[0], x_dim], [y2, y2], lw=EXT_LW, color='black')

        ax.text(x_dim - 0.18, (y1 + y2) / 2,
                label, rotation=90, ha='center', va='center')

    else:
        x1, x2 = p1[0], p2[0]
        y_dim = p1[1] + offset

        arrow = FancyArrowPatch(
            (x1, y_dim),
            (x2, y_dim),
            arrowstyle='<->',
            mutation_scale=10,
            lw=DIM_LW,
            color='black'
        )
        ax.add_patch(arrow)

        ax.plot([x1, x1], [p1[1], y_dim], lw=EXT_LW, color='black')
        ax.plot([x2, x2], [p2[1], y_dim], lw=EXT_LW, color='black')

        ax.text((x1 + x2) / 2, y_dim + 0.12,
                label, ha='center', va='bottom')


# -------------------------
# Geometry drawing
# -------------------------
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb):

    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt

    fig, ax = plt.subplots(figsize=(9, 6))

    # Concrete
    ax.add_patch(Rectangle((0, 0), base_L, base_h,
                           fc='0.75', ec='black', lw=2))
    ax.add_patch(Rectangle((Lh, base_h), Tsb, Ha,
                           fc='0.75', ec='black', lw=2))

    # Soils
    ax.add_patch(Rectangle((0, base_h), Lh, Ha,
                           fc='#f4a261', alpha=0.8))
    ax.add_patch(Rectangle((Lh + Tsb, base_h), Lt, Hp,
                           fc='#b7e4c7', alpha=0.8))

    # Water
    if Hw > 0:
        ax.add_patch(Rectangle((0, base_h + Ha - Hw), Lh, Hw,
                               fc='#74c0fc', alpha=0.6))

    # Dimensions
    draw_dimension(ax, (0, base_h), (0, base_h + Ha), "Ha", offset=-0.8, vertical=True)
    draw_dimension(ax, (0, base_h + Ha - Hw), (0, base_h + Ha), "Hw", offset=-1.3, vertical=True)
    draw_dimension(ax, (base_L, base_h), (base_L, base_h + Hp), "Hp", offset=0.8, vertical=True)

    draw_dimension(ax, (0, 0), (0, Th), "Th", offset=-0.8, vertical=True)
    draw_dimension(ax, (base_L, 0), (base_L, Tt), "Tt", offset=0.8, vertical=True)

    draw_dimension(ax, (0, 0), (Lh, 0), "Lh", offset=-0.7)
    draw_dimension(ax, (Lh, 0), (Lh + Tsb, 0), "Tsb", offset=-0.7)
    draw_dimension(ax, (Lh + Tsb, 0), (base_L, 0), "Lt", offset=-0.7)

    ax.set_aspect('equal')
    ax.set_xlim(-2.0, base_L + 2.0)
    ax.set_ylim(-1.3, base_h + Ha + 1.3)
    ax.axis('off')
    ax.set_title("Retaining Wall – Online Calculator")

    return fig


# =========================
# STREAMLIT UI
# =========================
st.title("🧱 Retaining Wall Online Geometry Calculator")

st.sidebar.header("Input Parameters (m)")

Ha = st.sidebar.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp", 0.0, 20.0, 3.5)

Th = st.sidebar.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.sidebar.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)

Lh = st.sidebar.number_input("Heel length Lh", 0.5, 10.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt", 0.5, 10.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)

# Validation
if Hp > Ha:
    st.warning("⚠ Passive height Hp should normally not exceed Ha")

fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb)
st.pyplot(fig)
