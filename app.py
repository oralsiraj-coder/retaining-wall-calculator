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
``
