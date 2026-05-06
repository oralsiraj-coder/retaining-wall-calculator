import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
import numpy as np
import math

# =======================
# CONSTANTS
# =======================
VIEW_W, VIEW_H = 10, 10
MARGIN = 0.85
LW_DIM = 0.6
LW_EXT = 0.4
GAMMA_W = 9.81

# =======================
# SCALE
# =======================
def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base = Lh + Tsb + Lt
    height = Th + max(Ha, Hp)
    return min((VIEW_W*MARGIN)/base, (VIEW_H*MARGIN)/height)

# =======================
# DIMENSIONS
# =======================
def draw_dimension(ax, p1, p2, txt, offset=0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch((x,p1[1]), (x,p2[1]),
                                     arrowstyle="<->", lw=LW_DIM))
        ax.plot([p1[0],x],[p1[1],p1[1]], lw=LW_EXT)
        ax.plot([p2[0],x],[p2[1],p2[1]], lw=LW_EXT)
        ax.text(x-0.15, (p1[1]+p2[1])/2, txt, rotation=90,
                ha="center", fontsize=8)
    else:
        y = p1[1] + offset
        ax.add_patch(FancyArrowPatch((p1[0],y),(p2[0],y),
                                     arrowstyle="<->", lw=LW_DIM))
        ax.plot([p1[0],p1[0]],[p1[1],y], lw=LW_EXT)
        ax.plot([p2[0],p2[0]],[p2[1],y], lw=LW_EXT)
        ax.text((p1[0]+p2[0])/2, y+0.1, txt,
                ha="center", fontsize=8)

# =======================
# RANKINE
# =======================
def Ka(phi, beta):
    phi = math.radians(phi)
    beta = math.radians(beta)
    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)
    return math.cos(beta)*(math.cos(beta)-term)/(math.cos(beta)+term)

def Kp(phi):
    phi = math.radians(phi)
    return (1+math.sin(phi))/(1-math.sin(phi))

# =======================
# DRAW WALL
# =======================
def draw_wall(Ha,Hw,Hp,Th,Lh,Lt,Tsb,beta,q,gamma_a,phi_a,gamma_p,phi_p):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    # Scaled
    Ha_s, Hw_s, Hp_s = Ha*scale, Hw*scale, Hp*scale
    Th_s, Lh_s, Lt_s, Tsb_s = Th*scale, Lh*scale, Lt*scale, Tsb*scale

    base = Lh_s + Tsb_s + Lt_s
    x0 = (VIEW_W-base)/2
    y0 = 0.8

    fig, ax = plt.subplots(figsize=(7,7))

    # ===== ACTIVE SOIL =====
    beta_r = np.deg2rad(beta)
    y_top_L = y0+Th_s+Ha_s
    y_top_R = y_top_L - Lh_s*np.tan(beta_r)

    ax.add_patch(Polygon([
        (x0, y0+Th_s),
        (x0+Lh_s, y0+Th_s),
        (x0+Lh_s, y_top_R),
        (x0, y_top_L)
    ], color="#f4a261"))

    # ===== WATER =====
    if Hw > 0:
        ax.add_patch(Rectangle(
            (x0, y_top_L-Hw_s),
            Lh_s,
            Hw_s,
            color="blue", alpha=0.3
        ))

    # ===== PASSIVE =====
    ax.add_patch(Rectangle(
        (x0+Lh_s+Tsb_s, y0+Th_s),
        Lt_s,
        Hp_s,
        color="#b7e4c7"
    ))

    # ===== CONCRETE =====
    ax.add_patch(Rectangle((x0,y0), base, Th_s, ec='black', fc='0.85'))
    ax.add_patch(Rectangle((x0+Lh_s,y0+Th_s), Tsb_s, Ha_s, ec='black', fc='0.85'))

    # ===== DIMENSIONS =====
    draw_dimension(ax,(x0,y0),(x0+Lh_s,y0),"Lh", -0.6)
    draw_dimension(ax,(x0+Lh_s+Tsb_s,y0),(x0+base,y0),"Lt",-0.6)
    draw_dimension(ax,(x0,y0),(x0,y0+Th_s),"Th",-0.5,True)
    draw_dimension(ax,(x0,y0+Th_s),(x0,y0+Th_s+Ha_s),"Ha",-0.7,True)
    draw_dimension(ax,(x0+base,y0+Th_s),(x0+base,y0+Th_s+Hp_s),"Hp",0.7,True)

    # ===== GROUND LINE =====
    ax.plot([x0,x0+Lh_s],[y_top_L,y_top_R],'--')
    ax.text(x0+Lh_s/2,(y_top_L+y_top_R)/2,f"β={beta}°")

    # ===== SCALE TEXT =====
    ax.text(0.5, 0.2, f"Scale ≈ {1/scale:.1f} m/unit",
            transform=ax.transAxes)

    ax.set_xlim(0,VIEW_W)
    ax.set_ylim(0,VIEW_H)
    ax.set_aspect("equal")
    ax.axis('off')

    return fig

# =======================
# UI
# =======================
st.title("🧱 Retaining Wall Tool")

q = st.sidebar.number_input("q (kPa)",0.0,500.0,0.0)

Ha = st.sidebar.number_input("Ha",1.0,20.0,6.0)
Hw = st.sidebar.number_input("Hw",0.0,Ha,2.0)
Hp = st.sidebar.number_input("Hp",0.0,20.0,3.0)

Th = st.sidebar.number_input("Th",0.2,2.0,0.8)
Lh = st.sidebar.number_input("Lh",0.5,15.0,3.0)
Lt = st.sidebar.number_input("Lt",0.5,15.0,2.0)
Tsb = st.sidebar.number_input("Tsb",0.2,2.0,0.4)

beta = st.sidebar.number_input("β",0.0,45.0,10.0)

gamma_a = st.sidebar.number_input("γa",14.0,25.0,18.0)
phi_a = st.sidebar.number_input("φa",0.0,45.0,30.0)

gamma_p = st.sidebar.number_input("γp",14.0,25.0,18.0)
phi_p = st.sidebar.number_input("φp",0.0,45.0,35.0)

# DRAW
st.pyplot(draw_wall(Ha,Hw,Hp,Th,Lh,Lt,Tsb,beta,q,gamma_a,phi_a,gamma_p,phi_p))

# =======================
# EQUATIONS
# =======================
st.header("📐 Rankine Theory")

st.latex(r"K_a = \cos\beta \cdot \frac{\cos\beta - \sqrt{\cos^2\beta - \cos^2\phi}}{\cos\beta + \sqrt{\cos^2\beta - \cos^2\phi}}")
st.latex(r"K_p = \frac{1 + \sin\phi}{1 - \sin\phi}")
st.latex(r"\sigma_h = K \cdot \sigma'_v")
st.latex(r"\sigma'_v = \gamma z + q - \gamma_w (z - z_w)")
``
