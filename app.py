from dataclasses import dataclass

@dataclass
class Geometry:
    Ha: float
    Hw: float
    Hp: float
    Th: float
    Lh: float
    Lt: float
    Tsb: float
    beta: float

@dataclass
class Soil:
    gamma: float
    phi: float
    c: float

@dataclass
class Load:
    q: float
    mu: float

#==============================STEP 2
import math

def rankine_active(phi_deg, beta_deg):
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)

    if beta > phi:
        raise ValueError("Rankine: β must be ≤ φ")

    term = math.sqrt(math.cos(beta)**2 - math.cos(phi)**2)
    return math.cos(beta) * (math.cos(beta) - term) / (math.cos(beta) + term)

def rankine_passive(phi_deg):
    phi = math.radians(phi_deg)
    term = math.sqrt(1 - math.cos(phi)**2)
    return (1 + term) / (1 - term)

#=============================Step 3
import numpy as np

def compute_depth(geom):
    return -np.arange(0, geom.Ha, 0.1)

def vertical_stress(z, soil, load, geom):
    gamma_w = 9.81
    z_wt = -geom.Hw

    soil_stress = soil.gamma * (-z)
    surcharge = load.q * np.ones_like(z)
    water = -gamma_w * np.maximum(0, z_wt - z)

    effective = soil_stress + water
    total = effective + surcharge

    return {
        "soil": soil_stress,
        "surcharge": surcharge,
        "water": water,
        "effective": effective,
        "total": total
    }

def horizontal_stress(Ka, stress):
    return {
        "soil": Ka * stress["soil"],
        "surcharge": Ka * stress["surcharge"],
        "water": -stress["water"],
        "effective": Ka * stress["effective"],
        "total": Ka * stress["effective"] + Ka * stress["surcharge"] - stress["water"]
    }
#=============================Step 4
def compute_forces(geom, soil_a, soil_p, load, Ka, Kp):
    gamma_w = 9.81
    gamma_c = 25

    Ha, Hw, Hp = geom.Ha, geom.Hw, geom.Hp
    Lh, Lt, Tsb, Th = geom.Lh, geom.Lt, geom.Tsb, geom.Th

    # Active forces
    Pa1 = 0.5 * Ka * soil_a.gamma * Ha**2
    Pa2 = 0.5 * gamma_w * (Ha - Hw)**2
    Pa3 = Ka * load.q * Ha

    # Weights
    W1 = Lt * Hp * soil_p.gamma
    W2 = Th * (Tsb + Lh + Lt) * gamma_c
    W3 = Ha * Tsb * gamma_c
    W4 = Lh * Hw * soil_a.gamma
    W5 = Lh * (Ha - Hw) * (soil_a.gamma - gamma_w)

    N = W1 + W2 + W3 + W4 + W5
    Rf = load.mu * N
    Pp = 0.5 * Kp * soil_p.gamma * Hp**2

    Rd = Rf + Pp
    Hd = Pa1 + Pa2 + Pa3

    FS = Rd / Hd if Hd != 0 else 0

    return {
        "Pa": (Pa1, Pa2, Pa3),
        "weights": (W1, W2, W3, W4, W5),
        "FS_sliding": FS
    }

#===============================Step 5

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import numpy as np

VIEW_W, VIEW_H = 10, 10

def compute_scale(geom):
    base_L = geom.Lh + geom.Tsb + geom.Lt
    total_H = geom.Th + max(geom.Ha, geom.Hp)
    return min(8/base_L, 8/total_H)

def draw_wall(geom):
    scale = compute_scale(geom)

    Ha = geom.Ha * scale
    Th = geom.Th * scale
    Lh = geom.Lh * scale
    Lt = geom.Lt * scale
    Tsb = geom.Tsb * scale

    base_L = Lh + Tsb + Lt

    fig, ax = plt.subplots(figsize=(6,6))

    ax.add_patch(Rectangle((2,2), base_L, Th, fc="0.8"))
    ax.add_patch(Rectangle((2+Lh,2+Th), Tsb, Ha, fc="0.8"))

    ax.set_xlim(0, VIEW_W)
    ax.set_ylim(0, VIEW_H)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

#=================================Step 6

import matplotlib.pyplot as plt

def plot_vertical(z, stress):
    fig, ax = plt.subplots()

    ax.plot(stress["total"], z, label="Total", lw=2)
    ax.plot(stress["soil"], z, "--", label="Soil")

    ax.invert_yaxis()
    ax.legend()
    ax.grid()

    return fig

def plot_horizontal(z, stress):
    fig, ax = plt.subplots()

    ax.plot(stress["total"], z, label="Total", lw=2)
    ax.plot(stress["effective"], z, "--", label="Effective")

    ax.invert_yaxis()
    ax.legend()
    ax.grid()

    return fig


