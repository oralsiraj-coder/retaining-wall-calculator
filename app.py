import streamlit as st
st.set_page_config(layout="wide")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np
import math

# =======================
# VIEWPORT & STYLE
# =======================
VIEW_W = 7.0
VIEW_H = 7.0
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

st.sidebar.header("Coefficient of friction")
mu = st.sidebar.number_input("Coefficient of friction μ ", 0.0, 1.0, 0.0, 0.01)

st.sidebar.header("Geometry")
Ha = st.sidebar.number_input("Height of active soil (Ha)", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Depth of water table from top surface (Hw)", 0.0, Ha, 2.0)                #depth of water table from top of wall
Hp = st.sidebar.number_input("Height of active soil (Hp)", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Thickness of the heel (Th)", 0.2, 2.0, 0.8)
Lh = st.sidebar.number_input("Length of the heel (Lh)", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Length of the Toe (Lt)", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Thickness of the stem (Tsb)", 0.2, 2.0, 0.4)
beta = st.sidebar.number_input("Inclination angle of the soil β (deg)", 0.0, 45.0, 10.0)

st.sidebar.header("Active soil")
gamma_a = st.sidebar.number_input("Saturated desnity of soil (γₐ)", 14.0, 25.0, 18.0)
phi_a = st.sidebar.number_input("Friction angle of soil (φₐ)", 0.0, 45.0, 30.0)
c_a = st.sidebar.number_input("Cohesion of soil (cₐ)( neglected in this calculation )", 0.0, 50.0, 0.0)

st.sidebar.header("Passive soil")
gamma_p = st.sidebar.number_input("Desnity of soil (γₚ)", 14.0, 25.0, 18.0)
phi_p = st.sidebar.number_input("Friction angle of soil (φ)ₚ", 0.0, 45.0, 35.0)
c_p = st.sidebar.number_input("Cohesion of soil (cp)( neglected in this calculation )", 0.0, 50.0, 0.0)

st.pyplot(draw_wall(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, c_a,
    gamma_p, phi_p, c_p
))
#========================================================================================================
#Calculation of lateral earth pressure coefficient
#========================================================================================================

st.title(" Calculation of lateral earth pressure coefficient ")

#calculation of rankine active coefficient
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
Ka = rankine_active_coefficient(phi_a, beta)
Kp = rankine_passive_coefficient(phi_p)
#================================================================rendering equations 
st.markdown("### Active earth coefficient")
# Rendering the equation of active earth pressure coefficient
st.latex(
    rf"""
    K_a =
    \cos\beta \frac{{\cos\beta - \sqrt{{\cos^2\beta - \cos^2\varphi}}}}{{\cos\beta + \sqrt{{\cos^2\beta - \cos^2\varphi}}}}
    \;=\;
    \cos({beta:.1f}^\circ)\,\frac{{\cos({beta:.1f}^\circ) - \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_a:.1f}^\circ)}}}}{{\cos({beta:.1f}^\circ) + \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_a:.1f}^\circ)}}}}
    \;=\;
    \mathbf{{{Ka:.4f}}}
    """
)

st.markdown("### Passive earth coefficient")

st.latex(
    rf"""
    K_p =
    \cos\beta \frac{{\cos\beta + \sqrt{{\cos^2\beta - \cos^2\varphi}}}}{{\cos\beta - \sqrt{{\cos^2\beta - \cos^2\varphi}}}}
    \;=\;
    \cos({beta:.1f}^\circ)\,
    \frac{{\cos({beta:.1f}^\circ) + \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_p:.1f}^\circ)}}}}
         {{\cos({beta:.1f}^\circ) - \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_p:.1f}^\circ)}}}}
    \;=\;
    \mathbf{{{Kp:.4f}}}
    """
)
# ================================================================================
# EFFECTIVE VERTICAL STRESS – THEORY AND EQUATIONS 
# ================================================================================
st.header("Effective Vertical stress calculation")
st.markdown(
    """
    Effective vertical stress represents the portion of the total stress
    that is transmitted through the soil skeleton.
    """
)

# ---- Governing equations ----
st.markdown(r"""
Vertical stress due to self weight of soil :  
$\sigma_{v,\text{soil}}(z) = \gamma z$

Vertical stress due surcharge :  
$\sigma_{v,\text{surcharge}}(z) = q$

Vertical stress due to water table (uplift pressure) :  
$\sigma_{v,\text{water}}(z) = \gamma_w z_w$

Effective vertical stress :  
$\sigma_v(z) = \sigma_{v,\text{soil}} + \sigma_{v,\text{surcharge}} - \sigma_{v,\text{water}}$
""")

# ---- Symbol definitions ----
st.markdown("Where:")
st.markdown(r"""
$\sigma_{v,\text{soil}}(z):$ &nbsp; Vertical stress due to self weight of soil  
$\sigma_{v,\text{surcharge}}(z):$ &nbsp; Vertical stress due surcharge  
$\sigma_{v,\text{water}}(z):$ &nbsp; Vertical stress due water table  
$z_w:$ &nbsp;&nbsp; Water table depth  
$\sigma_v(z):$ &nbsp; Effective vertical stress  
""")
#==========================================================================================================
# =======================
# EFFECTIVE VERTICAL STRESS CALCULATIONS
# =======================
# ---- Depth ----
z = -np.arange(0, Ha, 0.1)

# ---- Water table ----
z_wt = -Hw

# ---- Material constants ----
gamma_w = 9.81

# ---- Stress components ----
sigma_v_soil = gamma_a * (-z)
sigma_v_surcharge = q * np.ones_like(z)
sigma_v_water = -gamma_w * np.maximum(0, z_wt - z)
sigma_v_effective = sigma_v_soil + sigma_v_water

# ---- Effective stress ----
sigma_v_effective_total = (
    sigma_v_soil +
    sigma_v_surcharge +
    sigma_v_water
)

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

fig_eff, ax_eff = plt.subplots(figsize=(4, 2))

# ---- Plot components ----
ax_eff.plot(sigma_v_soil, z, linestyle="--", color="brown", label="Soil self-weight")
ax_eff.plot(sigma_v_water, z, linestyle="--", color="cyan", label="Water")
ax_eff.plot(sigma_v_surcharge, z, linestyle="--", color="green", label="surcharge")
ax_eff.plot(sigma_v_effective, z, linestyle="--", color="blue", label="Effective stress ")

# ---- Effective stress (main curve) ----
ax_eff.plot(
    sigma_v_effective_total, z,
    linewidth=2.5, color="black",
    label="Toral effective stress"
)

# ---- Reference lines ----
ax_eff.axhline(z_wt, color="blue", linestyle=":", linewidth=1.5, label="Water table")
ax_eff.axvline(0, color="black", linewidth=1)

# ---- Fill effective stress (nice visual) ----
ax_eff.fill_betweenx(z, 0, sigma_v_effective_total, color="gray", alpha=0.2)

# ---- Axis limits (VERY IMPORTANT) ----
ax_eff.set_ylim(0, z.min())   # negative depth downward

xmin = min(sigma_v_water.min(), sigma_v_effective.min(), 0)
xmax = max(sigma_v_soil.max(), sigma_v_effective.max())
ax_eff.set_xlim(xmin, xmax)

# ---- Labels ----
ax_eff.set_xlabel("Stress (kPa)")
ax_eff.set_ylabel("Elevation z (m)")
ax_eff.set_title("Effective Vertical Stress Distribution")

# ---- Grid (professional style) ----
ax_eff.yaxis.set_major_locator(MultipleLocator(1))
ax_eff.yaxis.set_minor_locator(MultipleLocator(0.25))

ax_eff.grid(True, which='major', linestyle='-', linewidth=0.8)
ax_eff.grid(True, which='minor', linestyle=':', linewidth=0.5)

# ---- Legend ----
ax_eff.legend(loc="best")
ax_eff.invert_yaxis()
# ---- Show ----
st.pyplot(fig_eff)

# =======================
# VERTICAL STRESS TABLE (0.1 m SLICES)
# =======================
import pandas as pd

#dz = 0.1  # slice thickness (m)

# Depth array from ground surface to base
#z = np.arange(0, Ha + dz, dz)

# Water table depth
#z_wt = Ha - Hw
#gamma_w = 9.81  # kN/m³

# Vertical stresses (kPa)
#sigma_v_soil = gamma_a * z
#sigma_v_surcharge = q * np.ones_like(z)
#sigma_v_water = -gamma_w * np.maximum(0, z - z_wt)

# Total vertical stress (for completeness)
#sigma_v_total = sigma_v_soil + sigma_v_surcharge + sigma_v_water

# Create table
stress_table = pd.DataFrame({
    "Depth z (m)": z,
    "Soil self-weight (kPa)": sigma_v_soil,
    "Surcharge (kPa)": sigma_v_surcharge,
    "Water table (kPa)": sigma_v_water,
    "Effective stress(kPa)": sigma_v_effective
})


st.markdown("Vertical stress distribution ")

st.dataframe(
    stress_table.style.format({
        "Depth z (m)": "{:.2f}",
        "Soil self-weight (kPa)": "{:.2f}",
        "Surcharge (kPa)": "{:.2f}",
        "Water table (kPa)": "{:.2f}",
        "Effective stress(kPa)": "{:.2f}"
    }),
    use_container_width=True
)

#=========================================================================================================

# =======================
# HORIZONTAL EARTH STRESS
# =======================
st.header("Horizontal Earth Stress Calculation")

# ---- Short calculation-note explanation ----
st.markdown(
    """
    In this step, the **horizontal earth stress acting on the retaining wall
    is calculated a. 
    """
)

# ---- Governing equations ----
st.markdown(r"""
Horizontal stress due to self weight of soil :  
$\sigma_{h,\text{soil}}(z) = K \, \sigma_{v,\text{soil}}(z)$

Horizontal stress due surcharge :  
$\sigma_{h,\text{surcharge}}(z) = K \, \sigma_{v,\text{surcharge}}(z)$

Horizontal stress due to water table :  
$\sigma_{h,\text{water}}(z) = \sigma_{v,\text{water}}(z) = u(z)$
""")
st.markdown("Where:")
st.markdown(r"""
$\sigma_{v,\text{soil}}(z):$ &nbsp; Vertical stress due to self weight of soil  
$\sigma_{v,\text{surcharge}}(z):$ &nbsp; Vertical stress due surcharge  
$\sigma_{v,\text{water}}(z):$ &nbsp; Vertical stress due water table  
$z_w:$ &nbsp;&nbsp; Water table depth  
$\sigma_v(z):$ &nbsp; Effective vertical stress  
""")

# =======================
# HORIZONTAL STRESS DISTRIBUTION
# =======================

sigma_h_soil_self_weight = Ka * sigma_v_soil
sigma_h_surcharge = Ka * sigma_v_surcharge
sigma_h_water = -sigma_v_water
sigma_h_effective = Ka * sigma_v_effective
sigma_h_total = sigma_h_effective + sigma_h_surcharge + sigma_h_water

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

fig_h, ax_h = plt.subplots(figsize=(6, 5))

# ---- Plot components ----
ax_h.plot(sigma_h_soil_self_weight, z, linestyle="--", color="brown", label="Soil self-weight")
ax_h.plot(sigma_h_water, z, linestyle="--", color="Blue", label="Water table")
ax_h.plot(sigma_h_surcharge, z, linestyle="--", color="green", label="Surcharge")
ax_h.plot(sigma_h_effective, z, linestyle="--", color="red", label="effective stress ")
# ---- Total horizontal stress (main curve) ----
ax_h.plot(
    sigma_h_total, z,
    linewidth=2.5, color="black",
    label="Total horizontal stress"
)

# ---- Reference lines ----
ax_h.axhline(z_wt, color="blue", linestyle=":", linewidth=1.5, label="Water level")
ax_h.axvline(0, color="black", linewidth=1)

# ---- Fill area ----
ax_h.fill_betweenx(z, 0, sigma_h_total, color="gray", alpha=0.2)

# ---- Axis limits ----
ax_h.set_ylim(0, z.min())   # keep your negative depth convention

xmin = min(sigma_h_water.min(), sigma_h_total.min(), 0)
xmax = max(sigma_h_soil_self_weight.max(), sigma_h_total.max())
ax_h.set_xlim(xmin, xmax)

# ---- Labels ----
ax_h.set_xlabel("Horizontal stress σh (kPa)")
ax_h.set_ylabel("Elevation z (m)")
ax_h.set_title("Horizontal Stress Distribution")

# ---- Grid ----
ax_h.yaxis.set_major_locator(MultipleLocator(1))
ax_h.yaxis.set_minor_locator(MultipleLocator(0.25))

ax_h.grid(True, which='major', linestyle='-', linewidth=0.8)
ax_h.grid(True, which='minor', linestyle=':', linewidth=0.5)

# ---- Legend ----
ax_h.legend(loc="best")

ax_h.invert_yaxis()

# ---- Show ----
st.pyplot(fig_h)
#========================================================================================================================
# =======================
# WALL + FULL HORIZONTAL STRESS DIAGRAM
# =======================

st.header("Wall with Full Horizontal Stress Components")

fig_ws, ax_ws = plt.subplots(figsize=(10, 10))

# ---- Geometry scaling ----
scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

Ha_s = Ha * scale
Th_s = Th * scale
Lh_s = Lh * scale
Lt_s = Lt * scale
Tsb_s = Tsb * scale

base_L = Lh_s + Tsb_s + Lt_s

x0 = (VIEW_W - base_L) / 2
y0 = 0.8

# ---- Draw wall ----
ax_ws.add_patch(Rectangle((x0, y0), base_L, Th_s,
                          fc="0.85", ec="black"))

ax_ws.add_patch(Rectangle((x0 + Lh_s, y0 + Th_s),
                          Tsb_s, Ha_s,
                          fc="0.85", ec="black"))

# ---- Stress components (IMPORTANT) ----
sigma_h_eff = Ka * sigma_v_effective          # effective horizontal stress
sigma_h_water = -sigma_v_water                # pore water pressure (positive)
sigma_h_total = sigma_h_eff + sigma_h_water + Ka * sigma_v_surcharge


# ---- Scale stress ----
stress_scale = (VIEW_W * 0.25) / max(abs(sigma_h_total))

x_eff = sigma_h_eff * stress_scale
x_water = sigma_h_water * stress_scale
x_total = sigma_h_total * stress_scale

# Wall back face
x_wall = x0 + Lh_s + Tsb_s

# Depth → plot coordinates
y_plot = y0 + Th_s - z * scale

# =======================
# DRAW COMPONENTS
# =======================

# =======================
# SEPARATION GAP
# =======================
gap = 2.0

x_total_offset = x_wall
x_eff_offset   = x_wall + 1 * gap
x_water_offset = x_wall + 2 * gap

# =======================
# TOTAL STRESS (FIRST AFTER WALL)
# =======================
ax_ws.plot(x_total_offset + x_total, y_plot,
           color="red", linewidth=2.5)

ax_ws.fill_betweenx(
    y_plot,
    x_total_offset,
    x_total_offset + x_total,
    color="red",
    alpha=0.25,
    label="Total σh"
)

# =======================
# EFFECTIVE STRESS (SECOND)
# =======================
ax_ws.plot(x_eff_offset + x_eff, y_plot,
           color="orange", linestyle='--', linewidth=2)

ax_ws.fill_betweenx(
    y_plot,
    x_eff_offset,
    x_eff_offset + x_eff,
    color="orange",
    alpha=0.4,
    label="Effective (Kₐ·σ'v)"
)

# =======================
# WATER PRESSURE (LAST)
# =======================
ax_ws.plot(x_water_offset + x_water, y_plot,
           color="blue", linestyle='--', linewidth=2)

ax_ws.fill_betweenx(
    y_plot,
    x_water_offset,
    x_water_offset + x_water,
    color="blue",
    alpha=0.3,
    label="Water pressure (u)"
)

# =======================
# WALL LINE
# =======================
ax_ws.plot([x_wall, x_wall],
           [y0 + Th_s, y0 + Th_s + Ha_s],
           color="black", linewidth=2)

# =======================
# LABELS ABOVE DIAGRAMS
# =======================
top_y = y0 + Th_s + Ha_s + 0.3

ax_ws.text(x_total_offset, top_y,
           "Total", color="red", ha="left")

ax_ws.text(x_eff_offset, top_y,
           "Effective", color="orange", ha="left")

ax_ws.text(x_water_offset, top_y,
           "Water", color="blue", ha="left")

# ---- Axis ----
ax_ws.set_xlim(0, VIEW_W)
ax_ws.set_ylim(0, VIEW_H)
ax_ws.set_aspect("equal")
ax_ws.axis("off")

ax_ws.set_title("Retaining Wall with Horizontal Stress Components")

ax_ws.legend(loc="upper right")

# ---- Show figure ----
st.pyplot(fig_ws)


#=============================================================================

# =======================
# REFERENCE DIAGRAM
# =======================
st.header("Reference Earth Pressure Diagram")

st.image("image.png", caption="Classical earth pressure decomposition", use_container_width=True)

#=====================================================================================
# =======================
# EARTH PRESSURE FORCES
# =======================
st.header("Earth Pressure Resultants")

# --------------------------------------------------
# Pa1 – Soil
# --------------------------------------------------
st.subheader("1. Horizontal force due to soil (Pa₁)")    
Pa1 = 0.5 * Ka * gamma_a * Ha**2
st.latex(r"P_{a1} = \frac{1}{2} K_a \gamma_a H_a^2")      
st.latex( rf"P_{{a1}} = \frac{{1}}{{2}} \cdot {Ka:.3f} \cdot {gamma_a:.1f} \cdot {Ha:.1f}^2 = {Pa1:.2f}")
st.latex(rf"P_{{a1}} = {Pa1:.2f}")
st.latex(r"y_{a1} = \frac{H_a}{3}")
st.latex(rf"y_{{a1}} = \frac{{{Ha:.1f}}}{{3}}")
st.latex(rf"y_{{a1}} = {Ha/3:.2f}")
# --------------------------------------------------
# Pa2 – Water
# --------------------------------------------------
st.subheader("2. Horizontal force due to water table (Pa₂)")
Pa2 = 0.5 * gamma_w * (Ha - Hw)**2
st.latex(r"P_{a2} = \frac{1}{2} \gamma_w (H_a-H_w)^2")
st.latex(rf"P_{{a2}} = \frac{{1}}{{2}} \cdot {gamma_w:.2f} \cdot ({Ha:.1f} - {Hw:.1f})^2 = {Pa2:.2f}")
st.latex(r"y_{a2} = \frac{(H_a-H_w)}{3}")
st.latex( rf"y_{{a2}} = \frac{{({Ha:.1f} - {Hw:.1f})}}{{3}} = {(Ha - Hw)/3:.2f}")
# --------------------------------------------------
# Pa3 – Surcharge
# --------------------------------------------------
st.subheader("3. Horizontal force due to surcharge (Pa₃)")
Pa3 = Ka * q * Ha
st.latex(r"P_{a3} = K_a q H_a")
st.latex(rf"P_{{a3}} = {Ka:.3f} \cdot {q:.1f} \cdot {Ha:.1f} = {Pa3:.2f}")
st.latex(rf"P_{{a3}} = {Ka:.3f} \cdot {q:.1f} \cdot {Ha:.1f} = {Pa3:.2f}")
st.latex(r"y_{a3} = \frac{(H_a)}{2}")
st.latex(rf"y_{{a3}} = \frac{{{Ha:.1f}}}{{2}} = {Ha/2:.2f}")

st.subheader("Gravity loads ")
st.markdown("""A cantilever retaining wall relies on gravity loads to provide stabilizing forces against sliding and overturning failure. These stabilizing actions arise mainly from the self-weight of the wall, the weight of the retained soil above the heel, and any additional surcharge loads applied at the ground surface.""")
#================================================================================== work here 

st.markdown("""Sliding.  """)
st.markdown("""The resistance against sliding of a retaining wall is provided by two primary mechanisms: the frictional resistance mobilized at the interface between the base of the wall and the foundation soil, and the passive earth pressure developed in front of the wall.
The frictional resistance is proportional to the total vertical load acting on the base of the wall, which includes the self-weight of the wall and the weight of the soil retained above the base slab. This resistance is governed by the coefficient of friction between the wall base and the supporting soil.
In addition, passive earth pressure develops in front of the wall due to the confinement of the soil, providing an stabilizing force.""")

st.markdown("""Calculation the gravity loads on a unite length of the wall  """)
# -----------------------------
# COMPUTE WEIGHTS
# -----------------------------
gamma_c= 25
W1 = Lt * Hp * gamma_p
W2 = Th * (Tsb + Lh + Lt) * gamma_c
W3 = Ha * Tsb * gamma_c
W4 = Lh * Hw * gamma_a
W5 = Lh * (Ha - Hw) * (gamma_a - gamma_w)
N  = W1+W2+W3+W4+W5
R_f = mu * N
Pp = 0.5 * Kp * gamma_p * Hp**2
R_d = R_f + Pp
H_d = Pa1+Pa2+Pa3
FS = R_d / H_d
# -----------------------------
# RENDER EQUATIONS
# -----------------------------
st.latex(
rf"""
\begin{{aligned}}
W_1 &= L_t H_p \gamma_p \\
    &= {Lt:.2f} \cdot {Hp:.2f} \cdot {gamma_p:.1f} = {W1:.2f}
\end{{aligned}}
"""
)

st.latex(
rf"""
\begin{{aligned}}
W_2 &= T_h (T_{{sb}} + L_h + L_t) \gamma_c \\
    &= {Th:.2f} \cdot ({Tsb:.2f} + {Lh:.2f} + {Lt:.2f}) \cdot {gamma_c:.1f} = {W2:.2f}
\end{{aligned}}
"""
)

st.latex(
rf"""
\begin{{aligned}}
W_3 &= H_a T_{{sb}} \gamma_c \\
    &= {Ha:.2f} \cdot {Tsb:.2f} \cdot {gamma_c:.1f} = {W3:.2f}
\end{{aligned}}
"""
)

st.latex(
rf"""
\begin{{aligned}}
W_4 &= L_h H_w \gamma_a \\
    &= {Lh:.2f} \cdot {Hw:.2f} \cdot {gamma_a:.1f} = {W4:.2f}
\end{{aligned}}
"""
)

st.latex(
    rf"""

\begin{{aligned}}
W_5 &= L_h (H_a - H_w)(\gamma_a - \gamma_w) \\
    &= {Lh:.2f} \cdot ({Ha:.2f} - {Hw:.2f}) \cdot ({gamma_a:.1f} - {gamma_w:.2f}) = {W5:.2f}
\end{{aligned}}
"""
)

#Friction resistance 
st.latex(r"""N = W_1 + W_2 + W_3 + W_4 + W_5""")
st.latex(rf"""N = {W1:.2f} + {W2:.2f} + {W3:.2f} + {W4:.2f} + {W5:.2f} = {N:.2f}""")
st.latex(r"""R_f = \mu \, N""")
st.latex(rf"""R_f = {mu:.2f} \times {N:.2f} = {R_f:.2f}""")


#Passive earth pressure 

st.latex(r"""P_p = \frac{1}{2} K_p \gamma_p H_p^2""")
st.latex(rf"""P_p =\frac{{1}}{{2}} \cdot {Kp:.3f} \cdot {gamma_p:.1f} \cdot {Hp:.1f}^2= {Pp:.2f}""")

# Siding resistance 
st.latex(r""" R_d = R_{f} + P_{p} """)
st.latex(rf"""R_d = {R_f:.2f} + {Pp:.2f}={R_d:.2f}""")

st.latex(r"""H_d = P_{a1} + P_{a2} + P_{a3}""")
st.latex(rf""" H_d = {Pa1:.2f} + {Pa2:.2f} + {Pa3:.2f}= {H_d:.2f}""")


st.latex(r"""FS = \frac{R_d}{H_d}""")
st.latex(rf"""FS =\frac{{{R_d:.2f}}}{{{H_d:.2f}}}= {FS:.2f}""")
if FS >= 1.5:
    st.success("✅ Sliding check: OK")
else:
    st.error("❌ Sliding check: NOT OK")


# ---- Compute lever arm ----
X_W_1 = Lt / 2
X_W_2 = Lt + Tsb / 2
X_W_3 = (Lt + Tsb + Lh) / 2
X_W_4 = Lt + Tsb + Lh / 2
X_W_5 = Lt + Tsb + Lh / 2


# =======================
# X_W1
# =======================
st.markdown("**Lever arm of weight W₁**")

st.latex(r"X_{W1} = \frac{L_t}{2}")

st.latex(rf"X_{{W1}} = \frac{{{Lt:.2f}}}{{2}} = {X_W_1:.2f}")


# =======================
# X_W2
# =======================
st.markdown("**Lever arm of weight W₂**")

st.latex(r"X_{W2} = L_t + \frac{T_{sb}}{2}")

st.latex(rf"X_{{W2}} = {Lt:.2f} + \frac{{{Tsb:.2f}}}{{2}} = {X_W_2:.2f}")


# =======================
# X_W3
# =======================
st.markdown("**Lever arm of weight W₃**")

st.latex(r"X_{W3} = \frac{L_t + T_{sb} + L_h}{2}")

st.latex(rf"X_{{W3}} = \frac{{{Lt:.2f} + {Tsb:.2f} + {Lh:.2f}}}{{2}} = {X_W_3:.2f}")


# =======================
# X_W4
# =======================
st.markdown("**Lever arm of weight W₄**")

st.latex(r"X_{W4} = L_t + T_{sb} + \frac{L_h}{2}")

st.latex(rf"X_{{W4}} = {Lt:.2f} + {Tsb:.2f} + \frac{{{Lh:.2f}}}{{2}} = {X_W_4:.2f}")


# =======================
# X_W5
# =======================
st.markdown("**Lever arm of weight W₅**")

st.latex(r"X_{W5} = L_t + T_{sb} + \frac{L_h}{2}")

st.latex(rf"X_{{W5}} = {Lt:.2f} + {Tsb:.2f} + \frac{{{Lh:.2f}}}{{2}} = {X_W_5:.2f}")
#===============================================================































# =======================
# MOMENTS (ABOUT TOE)
# =======================

M1 = W1 * X_W_1
M2 = W2 * X_W_2
M3 = W3 * X_W_3
M4 = W4 * X_W_4
M5 = W5 * X_W_5

y_a1 = Ha / 3
y_a2 = (Ha-Hw)/3
y_a3 = Ha/2

M_overturning = Pa1 * y_a1+ Pa2 * y_a2 + Pa3 * y_a3
M_resisting = M1+M2+M3+M4+M5
FS_OT = M_resisting / M_overturning




st.latex(
rf"""
\begin{{aligned}}
M_1&=W_1 X_{{W1}} = {W1:.2f}\cdot {X_W_1:.2f} = {M1:.2f}\\
M_2&=W_2 X_{{W2}} = {W2:.2f}\cdot {X_W_2:.2f} = {M2:.2f}\\
M_3&=W_3 X_{{W3}} = {W3:.2f}\cdot {X_W_3:.2f} = {M3:.2f}\\
M_4&=W_4 X_{{W4}} = {W4:.2f}\cdot {X_W_4:.2f} = {M4:.2f}\\
M_5&=W_5 X_{{W5}} = {W5:.2f}\cdot {X_W_5:.2f} = {M5:.2f}
\end{{aligned}}
"""
)

st.latex(r"""M_{\text{resisting}} = M_1 + M_2 + M_3 + M_4 + M_5""")

st.latex(rf"""M_{{resisting}} ={M1:.2f} + {M2:.2f} + {M3:.2f} + {M4:.2f} + {M5:.2f}= {(M1 + M2 + M3 + M4 + M5):.2f}""")


st.subheader("Overturning moment")

st.latex(r"""M_{overturning} =P_{a1} \cdot y_{a1}+ P_{a2} \cdot y_{a2}+ P_{a3} \cdot y_{a3}""")
st.latex(rf"""M_{{overturning}} ={Pa1:.2f} \cdot {y_a1:.2f}+{Pa2:.2f} \cdot {y_a2:.2f}+{Pa3:.2f} \cdot {y_a3:.2f}={M_overturning:.2f}""")

st.latex(r"""FS_{OT} = \frac{M_{stabilizing}}{M_{overturning}}""")
st.latex(rf"""FS_{{OT}} =\frac{{{M_resisting:.2f}}}{{{M_overturning:.2f}}}={FS_OT:.2f} """)


if FS_OT >= 1.5:
    st.success("✅ Stability against overturning is satisfied")
else:
    st.error("❌ Stability against overturning is NOT satisfied")










import pandas as pd

summary = pd.DataFrame({
    "Component": ["W1", "W2", "W3", "W4", "W5"],
    "Force (kN)": [W1, W2, W3, W4, W5],
    "Lever Arm (m)": [X_W_1, X_W_2, X_W_3, X_W_4, X_W_5],
    "Moment (kNm)": [M1, M2, M3, M4, M5]
})

st.subheader("Summary Table")

st.dataframe(
    summary.style.format({
        "Force (kN)": "{:.2f}",
        "Lever Arm (m)": "{:.2f}",
        "Moment (kNm)": "{:.2f}"
    }),
    use_container_width=True
)


