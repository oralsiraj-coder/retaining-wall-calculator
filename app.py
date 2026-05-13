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
