import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import math

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
            arrowstyle='<->', lw=DIM_LW, mutation_scale=10
        ))

        ax.plot([p1[0], x_dim], [y1, y1], lw=EXT_LW, color='black')
        ax.plot([p2[0], x_dim], [y2, y2], lw=EXT_LW, color='black')

        ax.text(x_dim - 0.18, (y1 + y2) / 2, label,
                rotation=90, ha="center", va="center")
    else:
        y_dim = p1[1] + offset
        x1, x2 = p1[0], p2[0]

        ax.add_patch(FancyArrowPatch(
            (x1, y_dim), (x2, y_dim),
            arrowstyle='<->', lw=DIM_LW, mutation_scale=10
        ))

        ax.plot([x1, x1], [p1[1], y_dim], lw=EXT_LW, color='black')
        ax.plot([x2, x2], [p2[1], y_dim], lw=EXT_LW, color='black')

        ax.text((x1 + x2) / 2, y_dim + 0.12, label,
                ha="center", va="bottom")

# =========================
# EARTH PRESSURE FUNCTIONS
# =========================
def rankine_coeff(phi_deg):
    phi = math.radians(phi_deg)
    Ka = math.tan(math.pi / 4 - phi / 2) ** 2
    Kp = math.tan(math.pi / 4 + phi / 2) ** 2
    return Ka, Kp


def earth_pressures(Ha, Hp, gamma_a, gamma_p, phi_a, phi_p, c_a, c_p):
    Ka, _ = rankine_coeff(phi_a)
    _, Kp = rankine_coeff(phi_p)

    Pa = 0.5 * gamma_a * Ka * Ha**2 - 2 * c_a * math.sqrt(Ka) * Ha
    Pp = 0.5 * gamma_p * Kp * Hp**2 + 2 * c_p * math.sqrt(Kp) * Hp

    Pa = max(Pa, 0.0)

    za = Ha / 3
    zp = Hp / 3
    return Pa, Pp, Ka, Kp, za, zp

# =========================
# WALL GEOMETRY
# =========================
def draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb):
    base_h = max(Th, Tt)
    base_L = Lh + Tsb + Lt

    fig, ax = plt.subplots(figsize=(9, 6))

    # Concrete
    ax.add_patch(Rectangle((0, 0), base_L, base_h, fc="0.75", ec="black", lw=2))
    ax.add_patch(Rectangle((Lh, base_h), Tsb, Ha, fc="0.75", ec="black", lw=2))

    # Soils
    ax.add_patch(Rectangle((0, base_h), Lh, Ha, fc="#f4a261", alpha=0.8))
    ax.add_patch(Rectangle((Lh + Tsb, base_h), Lt, Hp, fc="#b7e4c7", alpha=0.8))

    # Water
    if Hw > 0:
        ax.add_patch(Rectangle(
            (0, base_h + Ha - Hw), Lh, Hw,
            fc="#74c0fc", alpha=0.6
        ))

    # Dimensions
    draw_dimension(ax, (0, base_h), (0, base_h + Ha), "Ha", offset=-0.8, vertical=True)
    draw_dimension(ax, (0, base_h + Ha - Hw), (0, base_h + Ha), "Hw", offset=-1.3, vertical=True)
    draw_dimension(ax, (base_L, base_h), (base_L, base_h + Hp), "Hp", offset=0.8, vertical=True)

    draw_dimension(ax, (0, 0), (0, Th), "Th", offset=-0.8, vertical=True)
    draw_dimension(ax, (base_L, 0), (base_L, Tt), "Tt", offset=0.8, vertical=True)

    draw_dimension(ax, (0, 0), (Lh, 0), "Lh", offset=-0.7)
    draw_dimension(ax, (Lh, 0), (Lh + Tsb, 0), "Tsb", offset=-0.7)
    draw_dimension(ax, (Lh + Tsb, 0), (base_L, 0), "Lt", offset=-0.7)

    ax.set_aspect("equal")
    ax.set_xlim(-2, base_L + 2)
    ax.set_ylim(-1.5, base_h + Ha + 1.5)
    ax.axis("off")
    ax.set_title("Retaining Wall Online Calculator")

    return fig

# =========================
# STREAMLIT UI
# =========================
st.title("🧱 Retaining Wall Online Calculator")

st.sidebar.header("Geometry (m)")
Ha = st.sidebar.number_input("Active height Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp", 0.0, 20.0, 3.0)

Th = st.sidebar.number_input("Heel thickness Th", 0.2, 2.0, 0.8)
Tt = st.sidebar.number_input("Toe thickness Tt", 0.2, 2.0, 0.6)
Lh = st.sidebar.number_input("Heel length Lh", 0.5, 10.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt", 0.5, 10.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb", 0.2, 2.0, 0.4)

st.sidebar.header("Active soil")
gamma_a = st.sidebar.number_input("γₐ (kN/m³)", 14.0, 25.0, 18.0)
phi_a = st.sidebar.number_input("φₐ (°)", 0.0, 45.0, 30.0)
c_a = st.sidebar.number_input("cₐ (kPa)", 0.0, 50.0, 0.0)

st.sidebar.header("Passive soil")
gamma_p = st.sidebar.number_input("γₚ (kN/m³)", 14.0, 25.0, 18.0)
phi_p = st.sidebar.number_input("φₚ (°)", 0.0, 45.0, 35.0)
c_p = st.sidebar.number_input("cₚ (kPa)", 0.0, 50.0, 0.0)

st.sidebar.header("Wall / base")
W = st.sidebar.number_input("Wall weight W (kN/m)", 20.0, 500.0, 120.0)
mu = st.sidebar.number_input("Base friction μ", 0.2, 1.0, 0.5)

# =========================
# CALCULATIONS
# =========================
Pa, Pp, Ka, Kp, za, zp = earth_pressures(
    Ha, Hp, gamma_a, gamma_p, phi_a, phi_p, c_a, c_p
)

FS_sliding = (mu * W + Pp) / Pa if Pa > 0 else float("inf")
FS_overturn = (Pp * zp + W * 0.5) / (Pa * za) if Pa > 0 else float("inf")

# =========================
# OUTPUT
# =========================
fig = draw_wall(Ha, Hw, Hp, Th, Tt, Lh, Lt, Tsb)
st.pyplot(fig)

st.subheader("Numerical Results")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Active side")
    st.write(f"Ka = **{Ka:.3f}**")
    st.write(f"Pa = **{Pa:.2f} kN/m**")

with col2:
    st.markdown("### Passive side")
    st.write(f"Kp = **{Kp:.3f}**")
    st.write(f"Pp = **{Pp:.2f} kN/m**")

st.subheader("Stability Checks")

st.write(f"Sliding FS = **{FS_sliding:.2f}**")
st.write(f"Overturning FS = **{FS_overturn:.2f}**")

st.success("Sliding OK") if FS_sliding >= 1.5 else st.error("Sliding NOT OK")
st.success("Overturning OK") if FS_overturn >= 2.0 else st.error("Overturning NOT OK")
