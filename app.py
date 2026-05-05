# ============================================================
# Retaining Wall – Geometry & Earth Pressure Tool
# Refactored clean version
# ============================================================

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import streamlit as st

# ============================================================
# CONSTANTS & STYLE
# ============================================================

VIEW_W, VIEW_H = 10.0, 10.0
MARGIN = 0.85

LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4
DRAFT_GAP = 0.1

GAMMA_W = 9.81  # kN/m³

# ============================================================
# BASIC HELPERS
# ============================================================

def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base_L = Lh + Tsb + Lt
    total_H = Th + max(Ha, Hp)
    return min(
        (VIEW_W * MARGIN) / base_L,
        (VIEW_H * MARGIN) / total_H
    )

# ============================================================
# RANKINE COEFFICIENTS (c = 0)
# ============================================================

def rankine_active(phi_deg, beta_deg):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)

    if beta > phi:
        raise ValueError("Rankine active invalid: β ≤ φ required")

    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)
    return (
        math.cos(beta) * (math.cos(beta) - term)
        / (math.cos(beta) + term)
    )


def rankine_passive(phi_deg):
    phi = math.radians(phi_deg)
    return math.tan(math.pi / 4 + phi / 2)**2

# ============================================================
# DIMENSION DRAWING
# ============================================================

def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch(
            (x, p1[1]), (x, p2[1]),
            arrowstyle="<->", lw=LW_DIM, color="black"
        ))
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [p2[1], p2[1]], lw=LW_EXT, color="black")
        ax.text(x - 0.12, (p1[1] + p2[1]) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch(
            (p1[0], y), (p2[0], y),
            arrowstyle="<->", lw=LW_DIM, color="black"
        ))
        ax.plot([p1[0], p1[0]], [p1[1], y], lw=LW_EXT, color="black")
        ax.plot([p2[0], p2[0]], [p2[1], y], lw=LW_EXT, color="black")
        ax.text((p1[0] + p2[0]) / 2, y + 0.08,
                label, ha="center", va="bottom", fontsize=8)

# ============================================================
# FORCE ARROWS
# ============================================================

def draw_horizontal_force(ax, x, y, F, scale, direction, label, color):
    L = F * scale
    x2 = x + L if direction == "right" else x - L
    ha = "left" if direction == "right" else "right"

    ax.add_patch(FancyArrowPatch(
        (x, y), (x2, y),
        arrowstyle="-|>", lw=1.6, color=color
    ))

    ax.text(x2 + (0.06 if direction == "right" else -0.06),
            y, label, va="center", ha=ha, fontsize=8, color=color)

# ============================================================
# WALL + FORCE VISUALIZATION
# ============================================================

def draw_wall(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, gamma_p, phi_p, q
):
    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s, Hw_s, Hp_s = Ha*scale, Hw*scale, Hp*scale
    Th_s, Lh_s, Lt_s, Tsb_s = Th*scale, Lh*scale, Lt*scale, Tsb*scale

    base_L = Lh_s + Tsb_s + Lt_s
    x0, y0 = (VIEW_W - base_L) / 2, 0.8
    beta_rad = np.deg2rad(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    # Active soil
    xL, xR = x0 + DRAFT_GAP, x0 + Lh_s - DRAFT_GAP
    yB = y0 + Th_s + DRAFT_GAP
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
        (x0 + Lh_s + Tsb_s + DRAFT_GAP, y0 + Th_s + DRAFT_GAP),
        Lt_s, Hp_s,
        fc="#b7e4c7", ec="none"
    ))

    # Concrete
    ax.add_patch(Rectangle((x0, y0), base_L, Th_s,
                           fc="0.85", ec="black"))
    ax.add_patch(Rectangle((x0 + Lh_s, y0 + Th_s),
                           Tsb_s, Ha_s, fc="0.85", ec="black"))

    # ======================= Forces =======================

    Ka = rankine_active(phi_a, beta)
    Kp = rankine_passive(phi_p)

    Faγ = 0.5 * Ka * gamma_a * Ha**2
    Faq = Ka * q * Ha
    Fw  = 0.5 * GAMMA_W * Hw**2
    Fpγ = 0.5 * Kp * gamma_p * Hp**2

    maxF = max(Faγ + Faq + Fw, Fpγ, 1.0)
    force_scale = 0.2 * VIEW_W / maxF

    y_base = y0 + Th_s
    xA = x0 + Lh_s
    xP = x0 + Lh_s + Tsb_s

    draw_horizontal_force(ax, xA, y_base + (Ha/3)*scale,
                          Faγ, force_scale, "right", "Fa,γ", "crimson")
    draw_horizontal_force(ax, xA, y_base + (Ha/2)*scale,
                          Faq, force_scale, "right", "Fa,q", "darkorange")

    if Hw > 0:
        draw_horizontal_force(ax, xA, y_base + (Hw/3)*scale,
                              Fw, force_scale, "right", "Fw", "royalblue")

    draw_horizontal_force(ax, xP, y_base + (Hp/3)*scale,
                          Fpγ, force_scale, "left", "Fp,γ", "seagreen")

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

# ============================================================
# STREAMLIT UI
# ============================================================

st.title("🧱 Retaining Wall – Earth Pressure Tool")

st.sidebar.header("Geometry")
Ha = st.sidebar.number_input("Active height Ha (m)", 1.0, 20.0, 6.0)
Hw = st.sidebar.number_input("Water height Hw (m)", 0.0, Ha, 2.0)
Hp = st.sidebar.number_input("Passive height Hp (m)", 0.0, 20.0, 3.0)
Th = st.sidebar.number_input("Base thickness Th (m)", 0.2, 2.0, 0.8)
Lh = st.sidebar.number_input("Heel length Lh (m)", 0.5, 15.0, 3.0)
Lt = st.sidebar.number_input("Toe length Lt (m)", 0.5, 15.0, 2.0)
Tsb = st.sidebar.number_input("Stem thickness Tsb (m)", 0.2, 2.0, 0.4)
beta = st.sidebar.number_input("Backfill slope β (deg)", 0.0, 45.0, 10.0)

st.sidebar.header("Loads & Soil")
q = st.sidebar.number_input("Uniform surcharge q (kPa)", 0.0, 500.0, 0.0)

gamma_a = st.sidebar.number_input("γa (kN/m³)", 14.0, 25.0, 18.0)
phi_a   = st.sidebar.number_input("φa (deg)", 0.0, 45.0, 30.0)

gamma_p = st.sidebar.number_input("γp (kN/m³)", 14.0, 25.0, 18.0)
phi_p   = st.sidebar.number_input("φp (deg)", 0.0, 45.0, 35.0)

st.pyplot(draw_wall(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, gamma_p, phi_p, q
))
