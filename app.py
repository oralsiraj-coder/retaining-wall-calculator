st.header("📄 Earth Pressure Calculation Report")
st.markdown("---")

# =======================
# 1. PROJECT DESCRIPTION
# =======================
st.subheader("1. Project Description")

st.markdown("""
This report summarizes the **input parameters** for the analysis of a
**retaining wall subjected to active and passive earth pressures**.

The purpose of this section is to clearly document all **geometric and soil inputs**
used in the analysis prior to any calculations.
""")

# =======================
# 2. METHOD & ASSUMPTIONS
# =======================
st.subheader("2. Method and Assumptions")

st.markdown("""
The earth pressure analysis will be based on **Rankine earth pressure theory**
with the following assumptions:

- Vertical wall back face  
- Smooth wall (no wall friction)  
- Homogeneous, isotropic soil  
- Plane failure surfaces within the soil  
- Backfill surface inclined at an angle β from the horizontal  
- Passive soil surface assumed horizontal  
- Groundwater effects considered separately  
""")

# =======================
# 3. GEOMETRY INPUTS
# =======================
st.subheader("3. Geometry Input Parameters")

st.table({
    "Symbol": ["Ha", "Hw", "Hp", "Th", "Lh", "Lt", "Tsb", "β"],
    "Description": [
        "Active soil height at wall back face",
        "Water table height above base slab",
        "Passive soil height in front of wall",
        "Concrete base slab thickness",
        "Heel length behind the wall",
        "Toe length in front of the wall",
        "Wall stem thickness",
        "Backfill surface inclination from horizontal (downward)"
    ],
    "Value": [
        f"{Ha:.2f} m",
        f"{Hw:.2f} m",
        f"{Hp:.2f} m",
        f"{Th:.2f} m",
        f"{Lh:.2f} m",
        f"{Lt:.2f} m",
        f"{Tsb:.2f} m",
        f"{beta:.1f}°"
    ]
})

# =======================
# 4. ACTIVE SOIL PARAMETERS
# =======================
st.subheader("4. Active Soil Parameters")

st.table({
    "Parameter": ["γₐ", "φₐ", "cₐ"],
    "Description": [
        "Unit weight of active soil",
        "Internal friction angle of active soil",
        "Cohesion of active soil"
    ],
    "Value": [
        f"{gamma_a:.1f} kN/m³",
        f"{phi_a:.1f}°",
        f"{c_a:.1f} kPa"
    ]
})

# =======================
# 5. PASSIVE SOIL PARAMETERS
# =======================
st.subheader("5. Passive Soil Parameters")

st.table({
    "Parameter": ["γₚ", "φₚ", "cₚ"],
    "Description": [
        "Unit weight of passive soil",
        "Internal friction angle of passive soil",
        "Cohesion of passive soil"
    ],
    "Value": [
        f"{gamma_p:.1f} kN/m³",
        f"{phi_p:.1f}°",
        f"{c_p:.1f} kPa"
    ]
})

# =======================
# 6. NOTES
# =======================
st.subheader("6. Notes")

st.markdown("""
- All parameters shown above are **user-defined inputs**.
- No calculations have been performed in this section.
- Subsequent sections will compute earth pressure coefficients,
  pressure distributions, and stability checks using these inputs.
""")
