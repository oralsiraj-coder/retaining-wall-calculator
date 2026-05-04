import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon, Patch
from matplotlib.lines import Line2D
import numpy as np
import math
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# ============================================================
# GLOBAL STYLE
# ============================================================
VIEW_W = 10.0
VIEW_H = 10.0
MARGIN = 0.85

LW_CONCRETE = 1.2
LW_DIM = 0.6
LW_EXT = 0.4
DRAFT_GAP = 0.1


# ============================================================
# DIMENSION DRAWING
# ============================================================
def draw_dimension(ax, p1, p2, label, offset=0.0, vertical=False):
    if vertical:
        x = p1[0] + offset
        ax.add_patch(FancyArrowPatch(
            (x, p1[1]), (x, p2[1]),
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
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
            arrowstyle="<->", lw=LW_DIM, mutation_scale=8, color="black"
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


# ============================================================
# DRAW WALL GEOMETRY
# ============================================================
def compute_scale(Ha, Hp, Th, Lh, Lt, Tsb):
    base_L = Lh + Tsb + Lt
    total_H = Th + max(Ha, Hp)
    return min((VIEW_W * MARGIN) / base_L,
               (VIEW_H * MARGIN) / total_H)


def draw_wall(Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
              gamma_a, phi_a, c_a,
              gamma_p, phi_p, c_p,
              show_labels):

    scale = compute_scale(Ha, Hp, Th, Lh, Lt, Tsb)

    Ha_s, Hw_s, Hp_s = Ha*scale, Hw*scale, Hp*scale
    Th_s = Th*scale
    Lh_s, Lt_s, Tsb_s = Lh*scale, Lt*scale, Tsb*scale

    x0 = (VIEW_W - (Lh_s + Tsb_s + Lt_s)) / 2
    y0 = 0.8
    gap = DRAFT_GAP
    beta_rad = math.radians(beta)

    fig, ax = plt.subplots(figsize=(7, 7))

    # Active soil
    xL = x0 + gap
    xR = x0 + Lh_s - gap
    yB = y0 + Th_s + gap
    yTL = yB + Ha_s
    yTR = yTL - Lh_s * math.tan(beta_rad)

    ax.add_patch(Polygon(
        [(xL, yB), (xR, yB), (xR, yTR), (xL, yTL)],
        fc="#f4a261", ec="none", alpha=0.85
    ))

    if show_labels:
        ax.text(
            xL + 0.45*Lh_s, yB + 0.55*Ha_s,
            f"Active soil\nγ={gamma_a:.1f}\nφ={phi_a:.0f}°\nc={c_a:.1f}",
            ha="center", va="center", fontsize=8
        )

    # Water
    if Hw > 0:
        ax.add_patch(Polygon(
            [(xL, yTL-Hw_s), (xR, yTR-Hw_s),
             (xR, yTR), (xL, yTL)],
            fc="#74c0fc", ec="none", alpha=0.6
        ))
        ax.plot([xL, xR], [yTL, yTR], "--", color="#1c7ed6")

        if show_labels:
            draw_dimension(ax,
                (xL-0.5, yTL-Hw_s), (xL-0.5, yTL),
                "Hw", vertical=True)

    # Passive soil
    ax.add_patch(Rectangle(
        (x0 + Lh_s + Tsb_s + gap, y0 + Th_s + gap),
        Lt_s-gap, Hp_s-gap,
        fc="#b7e4c7", ec="none", alpha=0.85
    ))

    if show_labels:
        ax.text(
            x0 + Lh_s + Tsb_s + 0.5*Lt_s,
            y0 + Th_s + 0.5*Hp_s,
            f"Passive soil\nγ={gamma_p:.1f}\nφ={phi_p:.0f}°\nc={c_p:.1f}",
            ha="center", va="center", fontsize=8
        )

    # Concrete
    ax.add_patch(Rectangle(
        (x0, y0), Lh_s+Tsb_s+Lt_s, Th_s,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))
    ax.add_patch(Rectangle(
        (x0 + Lh_s, y0 + Th_s), Tsb_s, Ha_s,
        fc="0.85", ec="black", lw=LW_CONCRETE
    ))

    if show_labels:
        draw_dimension(ax, (x0, y0), (x0, y0+Th_s),
                       "Th", offset=-0.5, vertical=True)
        draw_dimension(ax, (x0, y0), (x0+Lh_s, y0),
                       "Lh", offset=-0.6)
        draw_dimension(ax, (x0+Lh_s+Tsb_s, y0),
                       (x0+Lh_s+Tsb_s+Lt_s, y0),
                       "Lt", offset=-0.6)
        draw_dimension(ax, (x0+Lh_s, y0+Th_s),
                       (x0+Lh_s+Tsb_s, y0+Th_s),
                       "Tsb", offset=0.3)
        draw_dimension(ax, (x0, y0+Th_s),
                       (x0, y0+Th_s+Ha_s),
                       "Ha", offset=-0.7, vertical=True)
        draw_dimension(ax, (x0+Lh_s+Tsb_s+Lt_s, y0+Th_s),
                       (x0+Lh_s+Tsb_s+Lt_s, y0+Th_s+Hp_s),
                       "Hp", offset=0.7, vertical=True)
        ax.text((xL+xR)/2, (yTL+yTR)/2+0.15,
                f"β={beta:.0f}°", ha="center", fontsize=8)

    ax.plot([xL, xR], [yTL, yTR], "--", color="black")

    legend_items = [
        Patch(facecolor="#f4a261", label="Active soil"),
        Patch(facecolor="#b7e4c7", label="Passive soil"),
        Patch(facecolor="#74c0fc", label="Water"),
        Patch(facecolor="0.85", edgecolor="black", label="Concrete"),
        Line2D([0],[0], linestyle="--", color="black",
               label="Ground surface")
    ]
    ax.legend(handles=legend_items, loc="upper right",
              fontsize=8, title="Legend")

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retaining Wall Geometry")

    return fig


# ============================================================
# PDF REPORT (INPUTS ONLY)
# ============================================================
def generate_input_report_pdf(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, c_a,
    gamma_p, phi_p, c_p
):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = A4[1] - 25*mm

    def line(txt):
        nonlocal y
        c.drawString(25*mm, y, txt)
        y -= 6*mm

    c.setFont("Helvetica-Bold", 14)
    line("Earth Pressure Analysis – Input Report")
    y -= 5*mm

    c.setFont("Helvetica", 10)
    line("Retaining wall geometry and soil parameters")
    y -= 8*mm

    c.setFont("Helvetica-Bold", 11)
    line("Geometry Inputs")
    y -= 4*mm
    c.setFont("Helvetica", 10)
    for txt in [
        f"Ha = {Ha:.2f} m   (Active height)",
        f"Hw = {Hw:.2f} m   (Water height)",
        f"Hp = {Hp:.2f} m   (Passive height)",
        f"Th = {Th:.2f} m   (Base slab thickness)",
        f"Lh = {Lh:.2f} m   (Heel length)",
        f"Lt = {Lt:.2f} m   (Toe length)",
        f"Tsb = {Tsb:.2f} m (Stem thickness)",
        f"β = {beta:.1f}°   (Backfill slope)"
    ]:
        line(txt)

    y -= 6*mm
    c.setFont("Helvetica-Bold", 11)
    line("Active Soil")
    y -= 4*mm
    c.setFont("Helvetica", 10)
    line(f"γₐ = {gamma_a:.1f} kN/m³")
    line(f"φₐ = {phi_a:.1f}°")
    line(f"cₐ = {c_a:.1f} kPa")

    y -= 6*mm
    c.setFont("Helvetica-Bold", 11)
    line("Passive Soil")
    y -= 4*mm
    c.setFont("Helvetica", 10)
    line(f"γₚ = {gamma_p:.1f} kN/m³")
    line(f"φₚ = {phi_p:.1f}°")
    line(f"cₚ = {c_p:.1f} kPa")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ============================================================
# STREAMLIT UI
# ============================================================
st.title("🧱 Retaining Wall – Geometry & Inputs Report")

st.sidebar.header("Display")
show_labels = st.sidebar.checkbox("Show labels & dimensions", True)

st.sidebar.header("Geometry (m)")
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
    gamma_p, phi_p, c_p,
    show_labels
))

st.header("📄 Input Report (No Calculations)")
st.markdown("This section documents all analysis inputs prior to calculations.")

pdf = generate_input_report_pdf(
    Ha, Hw, Hp, Th, Lh, Lt, Tsb, beta,
    gamma_a, phi_a, c_a,
    gamma_p, phi_p, c_p
)

st.download_button(
    "Download input report (PDF)",
    pdf,
    file_name="retaining_wall_input_report.pdf",
    mime="application/pdf"
)
