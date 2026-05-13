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
