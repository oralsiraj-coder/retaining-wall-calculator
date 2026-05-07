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
Hw = st.sidebar.number_input("Hw", 0.0, Ha, 2.0)                #depth of water table from top of wall
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

st.markdown(
    """Active earth coefficient""")
    
# Render the equation with symboles
st.latex(
    r"K_a = \cos\beta \frac{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}"
    r"{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}"
)
#Render the equation with numbers 
st.latex(
    rf"K_a = \cos({beta:.1f}^\circ) \cdot \frac{{\cos({beta:.1f}^\circ) - \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_a:.1f}^\circ)}}}}{{\cos({beta:.1f}^\circ) + \sqrt{{\cos^2({beta:.1f}^\circ) - \cos^2({phi_a:.1f}^\circ)}}}}"
)

#Print the result 

st.success(f"Ka = {Ka:.4f}")

st.markdown(
    """Passive earth coefficient""")
    
# Render the equation with symboles
st.latex(
    r"K_p = \cos\beta \frac{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}"
    r"{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}"
)

#Render the equation with numbers
st.latex(
    rf"K_p = \cos(0^\circ) \cdot \frac{{\cos(0^\circ) + \sqrt{{\cos^2(0^\circ) - \cos^2({phi_p:.1f}^\circ)}}}}{{\cos(0^\circ) - \sqrt{{\cos^2(0^\circ) - \cos^2({phi_p:.1f}^\circ)}}}}"
)
#Print the result
st.success(f"Kp = {Kp:.4f}")




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

# ---- Effective stress ----
sigma_v_effective = (
    sigma_v_soil +
    sigma_v_surcharge +
    sigma_v_water
)

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

fig_eff, ax_eff = plt.subplots(figsize=(6, 5))

# ---- Plot components ----
ax_eff.plot(sigma_v_soil, z, linestyle="--", color="brown", label="Soil self-weight")
ax_eff.plot(sigma_v_water, z, linestyle="--", color="cyan", label="Water")
ax_eff.plot(sigma_v_surcharge, z, linestyle="--", color="green", label="surcharge")


# ---- Effective stress (main curve) ----
ax_eff.plot(
    sigma_v_effective, z,
    linewidth=2.5, color="black",
    label="Effective stress σ′ᵥ"
)

# ---- Reference lines ----
ax_eff.axhline(z_wt, color="blue", linestyle=":", linewidth=1.5, label="Water table")
ax_eff.axvline(0, color="black", linewidth=1)

# ---- Fill effective stress (nice visual) ----
ax_eff.fill_betweenx(z, 0, sigma_v_effective, color="gray", alpha=0.2)

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
#==============================================================Working zone ==============================================================================
# =======================
# HORIZONTAL STRESS DISTRIBUTION
# =======================

sigma_h_soil = Ka * sigma_v_soil
sigma_h_surcharge = Ka * sigma_v_surcharge
sigma_h_water = sigma_v_water

sigma_h_total = sigma_h_soil + sigma_h_surcharge + sigma_h_water

#fig_h, ax_h = plt.subplots(figsize=(6, 8))

#ax_h.plot(sigma_h_soil, z, label="Soil: K·γz")
#ax_h.plot(sigma_h_surcharge, z, label="Surcharge: K·q")
#ax_h.plot(sigma_h_water, z, label="Water: γw(z − zw)")
#ax_h.plot(sigma_h_total, z, linewidth=2.5, label="Resultant σh")

#ax_h.invert_yaxis()
#ax_h.set_xlabel("Horizontal stress σh (kPa)")
#ax_h.set_ylabel("Depth z (m)")
#ax_h.set_title("Horizontal Stress Distribution")
#ax_h.grid(True)
#ax_h.legend()

#st.pyplot(fig_h)

#===============================================================================
# =======================
# HORIZONTAL FORCE RESULTANTS
# =======================
st.header("🧮 Horizontal Force Resultants")

gamma_w = 9.81

Ka = rankine_active_coefficient(phi_a, beta)
Kp = rankine_passive_coefficient(phi_p)

# ---- Active forces ----
Fa_soil = 0.5 * Ka * gamma_a * Ha**2
Fa_surcharge = Ka * q * Ha
Fw = 0.5 * gamma_w * Hw**2

Fa_total = Fa_soil + Fa_surcharge + Fw

# ---- Passive force ----
Fp_soil = 0.5 * Kp * gamma_p * Hp**2

# ---- Resultant ----
F_resultant = Fa_total - Fp_soil

# =======================
# EQUATIONS (RENDERED)
# =======================
st.latex(r"F_{a,\gamma} = \frac{1}{2} K_a \gamma_a H_a^2")
st.latex(r"F_{a,q} = K_a q H_a")
st.latex(r"F_w = \frac{1}{2} \gamma_w H_w^2")
st.latex(r"F_{p,\gamma} = \frac{1}{2} K_p \gamma_p H_p^2")
st.latex(
    r"\boxed{F_{\text{resultant}}"
    r"= (F_{a,\gamma}+F_{a,q}+F_w)-F_{p,\gamma}}"
)

# =======================
# RESULTS TABLE
# =======================
import pandas as pd

force_table = pd.DataFrame({
    "Component": [
        "Active – soil self‑weight",
        "Active – surcharge",
        "Water pressure",
        "Total active force",
        "Passive – soil self‑weight",
        "Resultant horizontal force"
    ],
    "Horizontal force (kN/m)": [
        Fa_soil,
        Fa_surcharge,
        Fw,
        Fa_total,
        Fp_soil,
        F_resultant
    ]
})

st.subheader("📊 Horizontal Force Summary (per meter wall length)")
st.dataframe(
    force_table.style.format({"Horizontal force (kN/m)": "{:.2f}"}),
    use_container_width=True
)

# =======================
# DESIGN INTERPRETATION
# =======================
st.markdown(
    f"""
    ✅ **Total active force:** {Fa_total:.2f} kN/m  
    ✅ **Total passive resistance:** {Fp_soil:.2f} kN/m  

    ### ➤ **Resultant horizontal force**
    **{F_resultant:.2f} kN/m**

    *(Positive → wall pushed toward passive side)*  
    """
)


#===================================================================================================

# =======================
# LOCATION OF HORIZONTAL FORCES
# =======================
st.header("📍 Location of Horizontal Forces")

# ---- Individual force locations (from base) ----
z_Fa_soil = Ha / 3
z_Fa_surcharge = Ha / 2
z_Fw = Hw / 3
z_Fp_soil = Hp / 3

# ---- Resultant active force location ----
z_Fa_resultant = (
    Fa_soil * z_Fa_soil
    + Fa_surcharge * z_Fa_surcharge
    + Fw * z_Fw
) / Fa_total

# =======================
# EQUATIONS (RENDERED)
# =======================
st.latex(r"z_{a,\gamma} = \frac{H_a}{3}")
st.latex(r"z_{a,q} = \frac{H_a}{2}")
st.latex(r"z_w = \frac{H_w}{3}")
st.latex(r"z_{p,\gamma} = \frac{H_p}{3}")

st.latex(
    r"z_{a,\text{res}} = "
    r"\frac{F_{a,\gamma} z_{a,\gamma} + F_{a,q} z_{a,q} + F_w z_w}"
    r"{F_{a,\gamma} + F_{a,q} + F_w}"
)

# =======================
# RESULTS TABLE
# =======================
import pandas as pd

location_table = pd.DataFrame({
    "Force component": [
        "Active – soil self‑weight",
        "Active – surcharge",
        "Water pressure",
        "Resultant active force",
        "Passive – soil self‑weight"
    ],
    "Force (kN/m)": [
        Fa_soil,
        Fa_surcharge,
        Fw,
        Fa_total,
        Fp_soil
    ],
    "Location above base (m)": [
        z_Fa_soil,
        z_Fa_surcharge,
        z_Fw,
        z_Fa_resultant,
        z_Fp_soil
    ]
})

st.subheader("📊 Force Locations Summary")
st.dataframe(
    location_table.style.format({
        "Force (kN/m)": "{:.2f}",
        "Location above base (m)": "{:.2f}"
    }),
    use_container_width=True
)

# =======================
# INTERPRETATION
# =======================
st.markdown(
    f"""
    ✅ **Resultant active force acts at:**  
    **{z_Fa_resultant:.2f} m above base**

    This value is used directly for:
    - Overturning moment calculation  
    - Stability verification  
    - Structural wall design
    """
)

#====================================================
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
        ax.text(x - 0.15, (p1[1] + p2[1]) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)
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
        ax.text((p1[0] + p2[0]) / 2, y + 0.1,
                label, ha="center", va="bottom", fontsize=8)


# =======================
# HORIZONTAL FORCE ARROW
# =======================
def draw_horizontal_force(ax, x, y, F, scale,
                          direction="right", label="", color="crimson"):
    L = F * scale

    if direction == "right":
        x2 = x + L
        ha = "left"
        tx = x2 + 0.05
    else:
        x2 = x - L
        ha = "right"
        tx = x2 - 0.05

    ax.add_patch(FancyArrowPatch(
        (x, y), (x2, y),
        arrowstyle="-|>",
        mutation_scale=12,
        lw=1.6,
        color=color
    ))

    ax.text(tx, y, label, va="center", ha=ha,
            fontsize=8, color=color)


# =======================
# DRAW WALL + FORCES
# =======================
def draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s, Hw_s, Hp_s = Ha * scale, Hw * scale, Hp * scale
    Th_s, Lh_s, Lt_s, Tsb_s = Th * scale, Lh * scale, Lt * scale, Tsb * scale

    base_L = Lh_s + Tsb_s + Lt_s
    x0, y0 = (VIEW_W - base_L) / 2, 0.8
    gap = DRAFT_GAP
    beta_rad = np.deg2rad(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    # ----- ACTIVE SOIL -----
    xL, xR = x0 + gap, x0 + Lh_s - gap
    yB = y0 + Th_s + gap
    yTL = yB + Ha_s
    yTR = yTL - Lh_s * np.tan(beta_rad)

    ax.add_patch(Polygon(
        [(xL, yB), (xR, yB), (xR, yTR), (xL, yTL)],
        fc="#f4a261", ec="none", alpha=0.85
    ))

    # ----- WATER -----
    if Hw > 0:
        ax.add_patch(Polygon(
            [(xL, yTL - Hw_s), (xR, yTR - Hw_s),
             (xR, yTR), (xL, yTL)],
            fc="#74c0fc", ec="none", alpha=0.6
        ))

    # ----- PASSIVE SOIL -----
    ax.add_patch(Rectangle(
        (x0 + Lh_s + Tsb_s + gap, y0 + Th_s + gap),
        Lt_s - gap, Hp_s - gap,
        fc="#b7e4c7", ec="none"
    ))

    # ----- CONCRETE -----
    ax.add_patch(Rectangle((x0, y0), base_L, Th_s, fc="0.85", ec="black"))
    ax.add_patch(Rectangle((x0 + Lh_s, y0 + Th_s),
                           Tsb_s, Ha_s, fc="0.85", ec="black"))

    # =======================
    # HORIZONTAL FORCES
    # =======================
    Ka = rankine_active_coefficient(phi_a, beta)
    Kp = rankine_passive_coefficient(phi_p)
    gamma_w = 9.81

    # Forces
    Fa_soil = 0.5 * Ka * gamma_a * Ha**2
    Fa_q = Ka * q * Ha
    Fw = 0.5 * gamma_w * Hw**2
    Fp = 0.5 * Kp * gamma_p * Hp**2

    # Locations (from base)
    z_Fa_soil = Ha / 3
    z_Fa_q = Ha / 2
    z_Fw = Hw / 3
    z_Fp = Hp / 3

    y_base = y0 + Th_s
    force_scale = 0.02 * scale

    x_active = x0 + Lh_s
    x_passive = x0 + Lh_s + Tsb_s

    # Active forces →
    draw_horizontal_force(ax, x_active, y_base + z_Fa_soil * scale,
                          Fa_soil, force_scale, "right", "Fa,γ", "crimson")

    draw_horizontal_force(ax, x_active, y_base + z_Fa_q * scale,
                          Fa_q, force_scale, "right", "Fa,q", "darkorange")

    if Hw > 0:
        draw_horizontal_force(ax, x_active, y_base + z_Fw * scale,
                              Fw, force_scale, "right", "Fw", "royalblue")

    # Passive force ←
    draw_horizontal_force(ax, x_passive, y_base + z_Fp * scale,
                          Fp, force_scale, "left", "Fp,γ", "seagreen")

    # ----- VIEW SETTINGS -----
    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig
