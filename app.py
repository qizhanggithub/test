import streamlit as st
import pandas as pd
from math import sqrt

st.set_page_config(page_title="RC Beam Calculator")

st.title("Reinforced Concrete Beam Calculator")

# =========================
# INPUTS
# =========================

st.header("Inputs")

col1, col2 = st.columns(2)

with col1:
    f_prime_c = st.number_input("Concrete strength f'c (psi)", value=4000.0)
    f_yl = st.number_input("Steel yield strength fyl (psi)", value=40000.0)
    b = st.number_input("Beam width b (in)", value=12.0)
    h = st.number_input("Beam depth h (in)", value=19.0)
    cover = st.number_input("Cover (in)", value=2.0)

with col2:
    db_l = st.selectbox("Longitudinal bar size", [4,5,6,7,8,9,10,11], index=4)
    db_t = st.selectbox("Stirrup bar size", [4,5,6,7,8,9,10,11], index=0)
    n_tensionbar = st.number_input("Number of tension bars", value=7, step=1)
    n_leg = st.number_input("Number of stirrup legs", value=2, step=1)
    s = st.number_input("Stirrup spacing s (in)", value=6.0)

epsilon_cmax = 0.003
epsilon_y = 0.002
alpha_1 = 0.85
phi_v = 0.75
f_yt = 40000.0
Nu = 0.0

# =========================
# REBAR DATABASE
# =========================

USrebar = pd.DataFrame({
    'size #': [4,5,6,7,8,9,10,11],
    'area': [0.2,0.31,0.44,0.6,0.79,1.0,1.27,1.56]
})

As_bar = float(
    USrebar.loc[USrebar['size #'] == db_l, 'area'].iloc[0]
)

Av_bar = float(
    USrebar.loc[USrebar['size #'] == db_t, 'area'].iloc[0]
)

As = As_bar * n_tensionbar
Av = Av_bar * n_leg

# =========================
# SECTION PROPERTIES
# =========================

Ag = b * h

d = h - cover - db_t/8 - db_l/16

rho = As / (b * d)

# =========================
# BETA 1
# =========================

if f_prime_c < 4000:
    beta_1 = 0.85
elif f_prime_c < 8000:
    beta_1 = 0.85 - 0.05 * (f_prime_c - 4000) / 1000
else:
    beta_1 = 0.65

# =========================
# FLEXURAL ANALYSIS
# =========================

a = (f_yl * As) / (alpha_1 * f_prime_c * b)

c = a / beta_1

epsilon_t = epsilon_cmax * (d - c) / c

if epsilon_t > (epsilon_y + 0.003):
    phi_b = 0.9
elif epsilon_t > epsilon_y:
    phi_b = 0.65 + 0.25 * (epsilon_t - epsilon_y) / 0.003
else:
    phi_b = 0.65

Mn = phi_b * As * f_yl * (d - a/2) / 12 / 1000

# =========================
# SHEAR ANALYSIS
# =========================

d_shear = max(d, 0.8 * h)

rho_w = As / (b * d_shear)

lambda_s = min(sqrt(2 / (1 + d_shear / 10)), 1)

Av_min = max(
    0.75 * sqrt(f_prime_c) * b * s / f_yt,
    50 * b * s / f_yt
)

Vc_a = (2 * sqrt(f_prime_c) + Nu / 6 / Ag) * b * d_shear / 1000

Vc_b = (8 * rho_w**(1/3) * sqrt(f_prime_c) + Nu / 6 / Ag) * b * d_shear / 1000

if Av > Av_min:
    Vc = max(Vc_a, Vc_b) / 1000
else:
    Vc = (8 * lambda_s * rho_w**(1/3) * sqrt(f_prime_c) + Nu / 6 / Ag) * b * d_shear / 1000

Vs = (Av * f_yt * d_shear) / s / 1000

Vn = Vc + Vs

V_factored = phi_v * Vn

# =========================
# RESULTS
# =========================

st.header("Results")

col5, col6 = st.columns(2)

with col5:
    st.metric("As (in²)", f"{As:.3f}")
    st.metric("Effective depth d (in)", f"{d:.3f}")
    st.metric("Reinforcement ratio ρ", f"{rho:.5f}")
    st.metric("Beta 1", f"{beta_1:.3f}")
    st.metric("a (in)", f"{a:.3f}")
    st.metric("c (in)", f"{c:.3f}")

with col6:
    st.metric("Tensile strain εt", f"{epsilon_t:.5f}")
    st.metric("Flexural phi factor ϕb", f"{phi_b:.3f}")
    st.metric("Factored Moment Capacity ϕMn (kip-ft)", f"{Mn:.2f}")
    st.metric("Concrete Shear Capacity Vc (kips)", f"{Vc:.2f}")
    st.metric("Steel Shear Capacity Vs (kips)", f"{Vs:.2f}")
    st.metric("Factored Shear Capacity ϕVn (kips)", f"{V_factored:.2f}")

# =========================
# CALCULATION SUMMARY
# =========================

st.header("Calculation Summary")

calculation_text = f'''
Ag = b × h = {b:.2f} × {h:.2f} = {Ag:.2f} in²

d = {d:.3f} in

As = {As:.3f} in²

ρ = {rho:.5f}

a = {a:.3f} in

c = {c:.3f} in

εt = {epsilon_t:.5f}

ϕMn = {Mn:.2f} kip-ft

Vs = {Vs:.2f} kips

ϕVn = {V_factored:.2f} kips
'''

st.code(calculation_text)