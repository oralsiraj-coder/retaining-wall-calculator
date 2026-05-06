import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np
import pandas as pd
import math

# =======================
# CONSTANTS
# =======================
VIEW_W, VIEW_H = 10.0, 10.0
MARGIN = 0.85

LW_DIM = 0.6
LW_EXT = 0.4
DRAFT_GAP = 0.1
GAMMA_W = 9.81


# =======================
# RANKINE COEFFICIENTS
# =======================
def rankine_active(phi_deg, beta_deg):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)

    if beta > phi:
        raise ValueError("Rankine invalid: β must be ≤ φ")

    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)

    return math.cos(beta) * (math.cos(beta) - term) / (math.cos(beta) + term)


def rankine_passive(phi_deg):
    phi = math.radians(phi_deg)
    term = math.cos(phi)
    return (1 + term) / (1 - term)


# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base = Lh + Tsb + Lt
    height = Th + max(Ha, Hp)
    return min((VIEW_W * MARGIN) / base, (VIEW_H * MARGIN) / height)


# =======================
# DRAW HELPERS
# =======================
def draw_dimension(ax, p1, p2, label, offset=0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch((x, p1[1]), (x, p2[1]),
                                     arrowstyle="<->", lw=LW_DIM))
        ax.text(x - 0.15, (p1[1]+p2[1])/2, label,
                rotation=90, ha="center", va="center", fontsize=8)
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch((p1[0], y), (p2[0], y),
                                     arrowstyle="<->", lw=LW_DIM))
        ax.text((p1[0]+p2[0])/2, y + 0.1, label,
                ha="center", fontsize=8)


def draw_force(ax, x, y, F, scale, direction="right", label=""):
    L = F * scale
    x2 = x + L if direction == "right" else x - L

    ax.add_patch(FancyArrowPatch((x, y), (x2, y),
                                 arrowstyle="-|>", lw=1.5, color="crimson"))

    ax.text(x2, y, f" {label}", va="center",
            ha="left" if direction == "right" else "right", fontsize=8)


# =======================
# FORCE CALCULATION
# =======================
def compute_forces(Ha, Hp, Hw, gamma_a, gamma_p, phi_a, phi_p, beta, q):
    Ka = rankine_active(phi_a, beta)
    Kp = rankine_passive(phi_p)

    Fa_soil = 0.5 * Ka * gamma_a * Ha**2
    Fa_q = Ka * q * Ha
    Fw = 0.5 * GAMMA_W * Hw**2
    Fa_total = Fa_soil + Fa_q + Fw

    Fp = 0.5 * Kp * gamma_p * Hp**2
    F_result = Fa_total - Fp

    return {
        "Ka": Ka, "Kp": Kp,
        "Fa_soil": Fa_soil,
        "Fa_q": Fa_q,
        "Fw": Fw,
        "Fa_total": Fa_total,
        "Fp": Fp,
        "F_result": F_result,
    }


# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
              gamma_a, phi_a, gamma_p, phi_p, q):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s, Hw_s, Hp_s = Ha*scale, Hw*scale, Hp*scale
    Th_s, Lh_s, Lt_s, Tsb_s = Th*scale, Lh*scale, Lt*scale, Tsb*scale

    base = Lh_s + Tsb_s + Lt_s
    x0, y0 = (VIEW_W - base)/2, 0.8

    fig, ax = plt.subplots(figsize=(7, 7))

    # Soil polygon
    beta_rad = np.deg2rad(beta)
    xL, xR = x0, x0 + Lh_s
    yB = y0 + Th_s
    yT = yB + Ha_s

    ax.add_patch(Polygon(
        [(xL, yB), (xR, yB),
         (xR, yT - Lh_s*np.tan(beta_rad)), (xL, yT)],
        color="#f4a261", alpha=0.8
    ))

    # Water
    if Hw > 0:
        ax.add_patch(Rectangle((xL, yT-Hw_s), Lh_s, Hw_s,
                               color="#74c0fc", alpha=0.5))

    # Concrete
    ax.add_patch(Rectangle((x0, y0), base, Th_s, fc="0.85", ec="black"))
    ax.add_patch(Rectangle((x0 + Lh_s, y0 + Th_s),
                           Tsb_s, Ha_s, fc="0.85", ec="black"))

    # Forces
    F = compute_forces(Ha, Hp, Hw, gamma_a, gamma_p, phi_a, phi_p, beta, q)

    y_base = y0 + Th_s
    f_scale = 0.02 * scale

    draw_force(ax, x0+Lh_s, y_base + Ha_s/3, F["Fa_soil"], f_scale, "right", "Faγ")
    draw_force(ax, x0+Lh_s, y_base + Ha_s/2, F["Fa_q"], f_scale, "right", "Faq")

    if Hw > 0:
        draw_force(ax, x0+Lh_s, y_base + Hw_s/3, F["Fw"], f_scale, "right", "Fw")

    draw_force(ax, x0+Lh_s+Tsb_s, y_base + Hp_s/3,
               F["Fp"], f_scale, "left", "Fp")

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig, F


# =======================
# STREAMLIT UI
# =======================
st.title("🧱 Retaining Wall Tool")

# Sidebar inputs
q = st.sidebar.number_input("Surcharge q", 0.0, 500.0, 0.0)

Ha = st.sidebar.number_input("Ha", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Hw", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Hp", 0.0, 20.0, 3.0)

Th = st.sidebar.number_input("Th", 0.2, 2.0, 0.8)
Lh = st.sidebar.number_input("Lh", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Lt", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Tsb", 0.2, 2.0, 0.4)

beta = st.sidebar.number_input("β", 0.0, 45.0, 10.0)

gamma_a = st.sidebar.number_input("γa", 14.0, 25.0, 18.0)
phi_a = st.sidebar.number_input("φa", 0.0, 45.0, 30.0)

gamma_p = st.sidebar.number_input("γp", 14.0, 25.0, 18.0)
phi_p = st.sidebar.number_input("φp", 0.0, 45.0, 35.0)

# Draw
fig, F = draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
                   gamma_a, phi_a, gamma_p, phi_p, q)

st.pyplot(fig)

# Results
st.header("📊 Forces")

st.write(f"Ka = {F['Ka']:.3f}")
st.write(f"Kp = {F['Kp']:.3f}")

st.write(f"Active total = {F['Fa_total']:.2f} kN/m")
st.write(f"Passive = {F['Fp']:.2f} kN/m")
st.write(f"Resultant = {F['F_result']:.2f} kN/m")

df = pd.DataFrame({
    "Component": ["Soil", "Surcharge", "Water", "Passive"],
    "Force (kN/m)": [F["Fa_soil"], F["Fa_q"], F["Fw"], F["Fp"]]
})

st.dataframe(df)
