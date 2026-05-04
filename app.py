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
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
        ))
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=LW_EXT, color="black")
        ax.plot([p2[0], x], [p2[1], p2[1]], lw=LW_EXT, color="black")
        ax.text(x - 0.15, (p1[1] + p2[1]) / 2,
                label, rotation=90, ha="center", va="center", fontsize=8)
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch(
            (p1[0], y), (p2[0], y),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
        ))
        ax.plot([p1[0], p1[0]], [p1[1], y], lw=LW_EXT, color="black")
        ax.plot([p2[0], p2[0]], [p2[1], y], lw=LW_EXT, color="black")
        ax.text((p1[0] + p2[0]) / 2, y + 0.1,
                label, ha="center", va="bottom", fontsize=8)

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base_L = Lh + Tsb + Lt
    total_H = Th + max(Ha, Hp)
    return min((VIEW_W * MARGIN) / base_L,
               (VIEW_H * MARGIN) / total_H)

# =======================
# RANKINE COEFFICIENTS
# =======================
def rankine_active_coefficient(phi_deg, beta_deg):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)
    if beta > phi:
        raise ValueError("Rankine theory invalid: β must be ≤ φ")
    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)
    return math.cos(beta) * (math.cos(beta) - term) / (math.cos(beta) + term)

def rankine_passive_coefficient(phi_deg, beta_deg=0.0):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)
    if beta > phi:
        raise ValueError("Rankine theory invalid: β must be ≤ φ")
    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)
    return math.cos(beta) * (math.cos(beta) + term) / (math.cos(beta) - term)

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s, Hw_s, Hp_s = Ha*scale, Hw*scale, Hp*scale
    Th_s = Th*scale
    Lh_s, Lt_s, Tsb_s = Lh*scale, Lt*scale, Tsb*scale

    base_L = Lh_s + Tsb_s + Lt_s
    x0 = (VIEW_W - base_L) / 2
    y0 = 0.8
    gap = DRAFT_GAP
    beta_rad = np.deg2rad(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    xL, xR = x0 + gap, x0 + Lh_s - gap
    yB = y0 + Th_s + gap
    yTL = yB + Ha_s
    yTR = yTL - Lh_s * np.tan(beta_rad)

    ax.add_patch(Polygon([(xL,yB),(xR,yB),(xR,yTR),(xL,yTL)],
                         fc="#f4a261", ec="none", alpha=0.85))

    if Hw > 0:
        ax.add_patch(Polygon(
            [(xL,yTL-Hw_s),(xR,yTR-Hw_s),(xR,yTR),(xL,yTL)],
            fc="#74c0fc", ec="none", alpha=0.6
        ))

    ax.add_patch(Rectangle((x0+Lh_s+Tsb_s+gap,y0+Th_s+gap),
                           Lt_s-gap,Hp_s-gap,fc="#b7e4c7",ec="none"))

    ax.add_patch(Rectangle((x0,y0),base_L,Th_s,fc="0.85",ec="black"))
    ax.add_patch(Rectangle((x0+Lh_s,y0+Th_s),Tsb_s,Ha_s,fc="0.85",ec="black"))

    draw_dimension(ax,(x0,y0+Th_s),(x0,y0+Th_s+Ha_s),"Ha",-0.7,True)
    draw_dimension(ax,(x0+base_L,y0+Th_s),(x0+base_L,y0+Th_s+Hp_s),"Hp",0.7,True)
    draw_dimension(ax,(x0,y0),(x0+Lh_s,y0),"Lh",-0.6)
    draw_dimension(ax,(x0+Lh_s+Tsb_s,y0),(x0+base_L,y0),"Lt",-0.6)
    draw_dimension(ax,(x0,y0),(x0,y0+Th_s),"Th",-0.5,True)
    draw_dimension(ax,(x0+Lh_s,y0+Th_s),(x0+Lh_s+Tsb_s,y0+Th_s),"Tsb",0.3)

    ax.plot([xL,xR],[yTL,yTR],"--",color="black")
    ax.text((xL+xR)/2,(yTL+yTR)/2+0.1,f"β={beta:.0f}°",ha="center")

    ax.set_xlim(0,VIEW_W)
    ax.set_ylim(0,VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

# =======================
# STREAMLIT UI
# =======================
st.title("🧱 Retaining Wall Geometry Tool")

st.sidebar.header("Surface Loads")
q = st.sidebar.number_input("Uniform surcharge q (kPa)",0.0,500.0,0.0,5.0)

st.sidebar.header("Geometry")
Ha = st.sidebar.number_input("Ha",1.0,20.0,6.0)
Hw = st.sidebar.number_input("Hw",0.0,Ha,2.0)
Hp = st.sidebar.number_input("Hp",0.0,20.0,3.0)
Th = st.sidebar.number_input("Th",0.2,2.0,0.8)
Lh = st.sidebar.number_input("Lh",0.5,15.0,3.0)
Lt = st.sidebar.number_input("Lt",0.5,15.0,2.0)
Tsb = st.sidebar.number_input("Tsb",0.2,2.0,0.4)
beta = st.sidebar.number_input("β (deg)",0.0,45.0,10.0)

st.sidebar.header("Active soil")
gamma_a = st.sidebar.number_input("γₐ",14.0,25.0,18.0)
phi_a = st.sidebar.number_input("φₐ",0.0,45.0,30.0)
c_a = st.sidebar.number_input("cₐ",0.0,50.0,0.0)

st.sidebar.header("Passive soil")
gamma_p = st.sidebar.number_input("γₚ",14.0,25.0,18.0)
phi_p = st.sidebar.number_input("φₚ",0.0,45.0,35.0)
c_p = st.sidebar.number_input("cₚ",0.0,50.0,0.0)

st.pyplot(draw_wall(
    Ha,Hw,Hp,Th,Lh,Lt,Tsb,beta,
    gamma_a,phi_a,c_a,
    gamma_p,phi_p,c_p
))

st.header("📐 Rankine Earth Pressure Coefficients")

Ka = rankine_active_coefficient(phi_a,beta)
Kp = rankine_passive_coefficient(phi_p)

st.latex(r"K_a = \cos\beta \frac{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}")
st.success(f"Ka = {Ka:.4f}")

st.latex(r"K_p = \cos\beta \frac{\cos\beta + \sqrt{\cos^2\beta - \cos^2\varphi}}{\cos\beta - \sqrt{\cos^2\beta - \cos^2\varphi}}")
st.success(f"Kp = {Kp:.4f}")
``
