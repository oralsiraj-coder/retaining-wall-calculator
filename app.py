import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np
import math

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
            arrowstyle="<->",
            lw=LW_DIM,
            mutation_scale=8,
            color="black"
        ))
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [p2[1], p2[1]], lw=LW_EXT, color="black")
        ax.text(
            x - 0.15,
            (p1[1] + p2[1]) / 2,
            label,
            rotation=90,
            ha="center",
            va="center",
            fontsize=8
        )
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch(
            (p1[0], y), (p2[0], y),
            arrowstyle="<->",
            lw=LW_DIM,
            mutation_scale=8,
            color="black"
        ))
        ax.plot([p1[0], p1[0]], [p1[1], y], lw=LW_EXT, color="black")
        ax.plot([p2[0], p2[0]], [p2[1], y], lw=LW_EXT, color="black")
        ax.text(
            (p1[0] + p2[0]) / 2,
            y + 0.1,
            label,
            ha="center",
            va="bottom",
            fontsize=8
        )

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base_L = Lh + Tsb + Lt
    total_H = Th + max(Ha, Hp)
    return min(
        (VIEW_W * MARGIN) / base_L,
        (VIEW_H * MARGIN) / total_H
    )

# =======================
# RANKINE COEFFICIENTS
# (DEFINED BEFORE USE)
# =======================
def rankine_active_coefficient(phi_deg, beta_deg):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)

    if beta > phi:
        raise ValueError("Rankine theory invalid: β must be ≤ φ")

    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)

    Ka = (
        math.cos(beta)
        * (math.cos(beta) - term)
        / (math.cos(beta) + term)
    )
    return Ka


def rankine_passive_coefficient(phi_deg, beta_deg=0.0):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)

    if beta > phi:
        raise ValueError("Rankine theory invalid: β must be ≤ φ")

    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)

    Kp = (
        math.cos(beta)
        * (math.cos(beta) + term)
        / (math.cos(beta) - term)
    )
    return Kp

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s = Ha * scale
    Hw_s = Hw * scale
    Hp_s = Hp * scale
    Th_s = Th * scale
    Lh_s = Lh * scale
    Lt_s = Lt * scale
    Tsb_s = Tsb * scale

    base_L = Lh_s + Tsb_s + Lt_s

    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8
    gap = DRAFT_GAP
    beta_rad = np.deg2rad(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    # Active soil
    xL = x0 + gap
    xR = x0 + Lh_s - gap
    yB = y0 + Th_s + gap
    yTL = yB + Ha_s
    yTR = yTL - Lh_s * np.tan(beta_rad)

    ax.add_patch(Polygon(
        [(xL, yB), (xR, yB), (xR, yTR), (xL, yTL)],
        fc="#f4a261", ec="none", alpha=0.85
    ))

    # Water
    if Hw > 0:
        ax.add_patch(Polygon(
            [(xL, yTL - Hw_s), (xR, yTR - Hw_s),
             (xR, yTR), (xL, yTL)],
            fc="#74c0fc", ec="none", alpha=0.6
        ))

    # Passive soil
    ax.add_patch(Rectangle(
        (x0 + Lh_s + Tsb_s + gap, y0 + Th_s + gap),
        Lt_s - gap, Hp_s - gap,
        fc="#b7e4c7", ec="none"
    ))

    # Concrete
    ax.add_patch(Rectangle(
        (x0, y0), base_L, Th_s,
        fc="0.85", ec="black"
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh_s, y0 + Th_s),
        Tsb_s, Ha_s,
        fc="0.85", ec="black"
    ))

    # Dimensions
    draw_dimension(ax, (x0, y0 + Th_s), (x0, y0 + Th_s + Ha_s), "Ha", -0.7, True)
    draw_dimension(ax, (x0 + base_L, y0 + Th_s),
                   (x0 + base_L, y0 + Th_s + Hp_s), "Hp", 0.7, True)
    draw_dimension(ax, (x0, y0), (x0 + Lh_s, y0), "Lh", -0.6)
    draw_dimension(ax, (x0 + Lh_s + Tsb_s, y0),
                   (x0 + base_L, y0), "Lt", -0.6)
    draw_dimension(ax, (x0, y0), (x0, y0 + Th_s), "Th", -0.5, True)
    draw_dimension(ax, (x0 + Lh_s, y0 + Th_s),
                   (x0 + Lh_s + Tsb_s, y0 + Th_s), "Tsb", 0.3)

    # Ground surface
    ax.plot([xL, xR], [yTL, yTR], "--", color="black")
    ax.text((xL + xR) / 2, (yTL + yTR) / 2 + 0.1,
            f"β = {beta:.0f}°", ha="center")

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

# =======================
# STREAMLIT UI
# =======================
st.title("🧱 Retaining Wall Geometry Tool")

st.sidebar.header("Surface Load")
q = st.sidebar.number_input("Uniform surcharge q (kPa)", 0.0, 500.0, 0.0, 5.0)

st.sidebar.header("Geometry")
Ha = st.sidebar.number_input("Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Hp", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Th", 0.2, 2.0, 0.8)
Lh = st.sidebar.number_input("Lh", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Lt", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Tsb", 0.2, 2.0, 0.4)
beta = st.sidebar.number_input("β (deg)", 0.0, 45.0, 10.0)

st.sidebar.header("Active soil")
gamma_a = st.sidebar.number_input("γₐ", 14.0, 25.0, 18.0)
phi_a = st.sidebar.number_input("φₐ", 0.0, 45.0, 30.0)
c_a = st.sidebar.number_input("cₐ", 0.0, 50.0, 0.0)

st.sidebar.header("Passive soil")
gamma_p = st.sidebar.number_input("γₚ", 14.0, 25.0, 18.0)
phi_p = st.sidebar.number_input("φₚ", 0.0, 45.0, 35.0)
c_p = st.sidebar.number_input("cₚ", 0.0, 50.0, 0.0)

st.pyplot(draw_wall(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, c_a,
    gamma_p, phi_p, c_p
))

# =======================
# RANKINE RESULTS
# =======================
st.header("📐 Rankine Earth Pressure Coefficients")

Ka = rankine_active_coefficient(phi_a, beta)
Kp = rankine_passive_coefficient(phi_p)

st.latex(
    r"K_a = \cos\beta \frac{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}"
    r"{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}"
)
st.success(f"Ka = {Ka:.4f}")

st.latex(
    r"K_p = \cos\beta \frac{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}"
    r"{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}"
)
st.success(f"Kp = {Kp:.4f}")

# =======================
# EFFECTIVE VERTICAL STRESS – THEORY
# =======================
st.header("Vertical stress calculation")
st.markdown(
    """
    **Effective vertical stress** represents the portion of the total stress
    that is transmitted through the soil skeleton.
    It governs shear strength, settlement, and earth pressure.

    In saturated soil, pore water pressure does not contribute to strength
    and therefore reduces the effective stress.
    """
)

# ---- Governing equations ----
st.latex(r"\sigma_{v,\text{soil}}(z) = \gamma \, z")
st.latex(r"\sigma_{v,\text{surcharge}}(z) = q")
st.latex(r"\sigma_{v,\text{water}}(z) = -\gamma_w (z - z_w), \quad z > z_w")
st.latex(r"z_w = H_a - H_w")

st.latex(
    r"\sigma_v(z) = \sigma_{v,\text{soil}}"
    r" + \sigma_{v,\text{surcharge}}"
    r" + \sigma_{v,\text{water}}"
)

st.latex(r"\boxed{\sigma'_v(z) = \sigma_v(z)}")

# ---- Symbol definitions ----
st.markdown("### Definition of symbols")

st.markdown(
    """
    - **\( z \)** – Depth below ground surface *(m)*  
    - **\( H_a \)** – Total soil / wall height *(m)*  
    - **\( H_w \)** – Height of water above the base *(m)*  
    - **\( z_w \)** – Depth to water table *(m)*  
      \\[
      z_w = H_a - H_w
      \\]

    - **\( \gamma \)** – Unit weight of soil *(kN/m³)*  
    - **\( \gamma_w \)** – Unit weight of water *(≈ 9.81 kN/m³)*  
    - **\( q \)** – Uniform surface surcharge *(kPa)*  

    - **\( \sigma_v \)** – Total vertical stress *(kPa)*  
    - **\( \sigma'_v \)** – Effective vertical stress *(kPa)*  
    - **\( u \)** – Pore water pressure *(kPa)*
    """
)

st.header("📐 Effective Vertical Stress Calculation")

st.latex(r"\sigma_{v,\text{soil}}(z) = \gamma z")
st.latex(r"\sigma_{v,\text{surcharge}}(z) = q")
st.latex(r"\sigma_{v,\text{water}}(z) = -\gamma_w (z - z_w), \quad z > z_w")
st.latex(r"z_w = H_a - H_w")

st.latex(
    r"\sigma_v(z) = \sigma_{v,\text{soil}}"
    r" + \sigma_{v,\text{surcharge}}"
    r" + \sigma_{v,\text{water}}"
)

st.latex(r"\boxed{\sigma'_v(z) = \sigma_v(z)}")

# =======================
# VERTICAL STRESS TABLE (0.1 m SLICES)
# =======================
import pandas as pd

dz = 0.1  # slice thickness (m)

# Depth array from ground surface to base
z = np.arange(0, Ha + dz, dz)

# Water table depth
z_wt = Ha - Hw
gamma_w = 9.81  # kN/m³

# Vertical stresses (kPa)
sigma_v_soil = gamma_a * z
sigma_v_surcharge = q * np.ones_like(z)
sigma_v_water = -gamma_w * np.maximum(0, z - z_wt)

# Total vertical stress (for completeness)
sigma_v_total = sigma_v_soil + sigma_v_surcharge + sigma_v_water

# Create table
stress_table = pd.DataFrame({
    "Depth z (m)": z,
    "Soil stress γ·z (kPa)": sigma_v_soil,
    "Surcharge stress q (kPa)": sigma_v_surcharge,
    "Water pressure −γw·h (kPa)": sigma_v_water,
    "Total vertical stress σv (kPa)": sigma_v_total
})


st.markdown("Vertical stress distribution ")

st.dataframe(
    stress_table.style.format({
        "Depth z (m)": "{:.2f}",
        "Soil stress γ·z (kPa)": "{:.2f}",
        "Surcharge stress q (kPa)": "{:.2f}",
        "Water pressure −γw·h (kPa)": "{:.2f}",
        "Total vertical stress σv (kPa)": "{:.2f}"
    }),
    use_container_width=True
)

