import streamlit as st
import pandas as pd
from math import sqrt

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RC Beam Calculator",
    layout="wide"
)

st.title("Reinforced Concrete Beam Calculator")
st.caption("ACI 318-19 Rectangular RC Beam Design")

# =========================================================
# INPUTS
# =========================================================

st.header("Inputs")

col1, col2 = st.columns(2)

with col1:

    f_prime_c = st.number_input(
        "Concrete strength f'c (psi)",
        value=4000.0
    )

    f_yl = st.number_input(
        "Steel yield strength fy (psi)",
        value=40000.0
    )

    b = st.number_input(
        "Beam width b (in)",
        value=12.0
    )

    h = st.number_input(
        "Beam depth h (in)",
        value=19.0
    )

    cover = st.number_input(
        "Concrete cover (in)",
        value=2.0
    )

with col2:

    db_l = st.selectbox(
        "Longitudinal bar size",
        [4, 5, 6, 7, 8, 9, 10, 11],
        index=4
    )

    db_t = st.selectbox(
        "Stirrup bar size",
        [4, 5, 6, 7, 8, 9, 10, 11],
        index=0
    )

    n_tensionbar = st.number_input(
        "Number of tension bars",
        value=7,
        step=1
    )

    n_leg = st.number_input(
        "Number of stirrup legs",
        value=2,
        step=1
    )

    s = st.number_input(
        "Stirrup spacing s (in)",
        value=6.0
    )

# =========================================================
# CONSTANTS
# =========================================================

epsilon_cmax = 0.003
epsilon_y = 0.002
alpha_1 = 0.85
phi_v = 0.75
f_yt = 40000.0
Nu = 0.0

# =========================================================
# REBAR DATABASE
# =========================================================

USrebar = pd.DataFrame({
    'size #': [4, 5, 6, 7, 8, 9, 10, 11],
    'area': [0.20, 0.31, 0.44, 0.60, 0.79, 1.00, 1.27, 1.56]
})

As_bar = float(
    USrebar.loc[
        USrebar['size #'] == db_l,
        'area'
    ].iloc[0]
)

Av_bar = float(
    USrebar.loc[
        USrebar['size #'] == db_t,
        'area'
    ].iloc[0]
)

As = As_bar * n_tensionbar

Av = Av_bar * n_leg

# =========================================================
# SECTION PROPERTIES
# =========================================================

Ag = b * h

d = h - cover - db_t / 8 - db_l / 16

rho = As / (b * d)

# =========================================================
# BETA 1
# =========================================================

if f_prime_c < 4000:
    beta_1 = 0.85

elif f_prime_c < 8000:
    beta_1 = 0.85 - 0.05 * (f_prime_c - 4000) / 1000

else:
    beta_1 = 0.65

# =========================================================
# FLEXURAL ANALYSIS
# =========================================================

a = (f_yl * As) / (alpha_1 * f_prime_c * b)

c = a / beta_1

epsilon_t = epsilon_cmax * (d - c) / c

if epsilon_t > (epsilon_y + 0.003):

    phi_b = 0.90

elif epsilon_t > epsilon_y:

    phi_b = 0.65 + 0.25 * (epsilon_t - epsilon_y) / 0.003

else:

    phi_b = 0.65

Mn = phi_b * As * f_yl * (d - a / 2) / 12 / 1000

# =========================================================
# SHEAR ANALYSIS
# =========================================================

d_shear = max(d, 0.8 * h)

rho_w = As / (b * d_shear)

lambda_s = min(sqrt(2 / (1 + d_shear / 10)), 1)

Av_min = max(
    0.75 * sqrt(f_prime_c) * b * s / f_yt,
    50 * b * s / f_yt
)

Vc_a = ((2 * sqrt(f_prime_c) + Nu / 6 / Ag) * b * d_shear) / 1000

Vc_b = (
    (
        8 * rho_w ** (1 / 3) * sqrt(f_prime_c)
        + Nu / 6 / Ag
    )
    * b
    * d_shear
) / 1000

if Av > Av_min:

    Vc = max(Vc_a, Vc_b) / 1000

else:

    Vc = (
        (
            8 * lambda_s * rho_w ** (1 / 3) * sqrt(f_prime_c)
            + Nu / 6 / Ag
        )
        * b
        * d_shear
    ) / 1000

Vs = (Av * f_yt * d_shear) / s / 1000

Vn = Vc + Vs

V_factored = phi_v * Vn

# =========================================================
# RESULTS
# =========================================================

st.header("Results")

col3, col4 = st.columns(2)

with col3:

    st.metric("As (in²)", f"{As:.3f}")
    st.metric("Effective depth d (in)", f"{d:.3f}")
    st.metric("Reinforcement ratio ρ", f"{rho:.5f}")
    st.metric("β1", f"{beta_1:.3f}")
    st.metric("Compression block depth a (in)", f"{a:.3f}")
    st.metric("Neutral axis depth c (in)", f"{c:.3f}")

with col4:

    st.metric("Tensile strain εt", f"{epsilon_t:.5f}")
    st.metric("Flexural reduction factor ϕb", f"{phi_b:.3f}")
    st.metric("Factored Moment Capacity ϕMn (kip-ft)", f"{Mn:.2f}")
    st.metric("Concrete Shear Capacity Vc (kips)", f"{Vc:.2f}")
    st.metric("Steel Shear Capacity Vs (kips)", f"{Vs:.2f}")
    st.metric("Factored Shear Capacity ϕVn (kips)", f"{V_factored:.2f}")

# =========================================================
# DETAILED CALCULATIONS
# =========================================================

st.header("Detailed Calculations")

# =========================================================
# FLEXURAL CALCULATIONS
# =========================================================

st.subheader("Flexural Design")

st.latex(rf"""
A_g = b h = ({b})({h}) = {Ag:.2f}\ in^2
""")

st.latex(rf"""
d = h - cover - \frac{{d_bt}}{{8}} - \frac{{d_bl}}{{16}}
""")

st.latex(rf"""
d = {h} - {cover} - \frac{{{db_t}}}{{8}} - \frac{{{db_l}}}{{16}}
= {d:.3f}\ in
""")

st.latex(rf"""
A_s = ({As_bar:.2f})({n_tensionbar}) = {As:.3f}\ in^2
""")

st.latex(rf"""
\rho = \frac{{A_s}}{{bd}}
= \frac{{{As:.3f}}}{{({b})({d:.3f})}}
= {rho:.5f}
""")

st.latex(rf"""
a = \frac{{f_y A_s}}{{\alpha_1 f'_c b}}
= \frac{{({f_yl})({As:.3f})}}{{({alpha_1})({f_prime_c})({b})}}
= {a:.3f}\ in
""")

st.latex(rf"""
c = \frac{{a}}{{\beta_1}}
= \frac{{{a:.3f}}}{{{beta_1:.3f}}}
= {c:.3f}\ in
""")

st.latex(rf"""
\epsilon_t = \epsilon_{{cmax}}\left(\frac{{d-c}}{{c}}\right)
= ({epsilon_cmax})\left(\frac{{{d:.3f}-{c:.3f}}}{{{c:.3f}}}\right)
= {epsilon_t:.5f}
""")

st.latex(rf"""
\phi M_n = \phi_b A_s f_y \left(d - \frac{{a}}{{2}}\right)
""")

st.latex(rf"""
\phi M_n = ({phi_b:.3f})({As:.3f})({f_yl})
\left({d:.3f} - \frac{{{a:.3f}}}{{2}}\right)
\times \frac{{1}}{{12}} \times \frac{{1}}{{1000}}
= {Mn:.2f}\ kip-ft
""")

# =========================================================
# SHEAR CALCULATIONS
# =========================================================

st.subheader("Shear Design")

st.latex(rf"""
d_{{shear}} = \max(d,0.8h)
= \max({d:.3f},0.8({h}))
= {d_shear:.3f}\ in
""")

st.latex(rf"""
\rho_w = \frac{{A_s}}{{bd}}
= \frac{{{As:.3f}}}{{({b})({d_shear:.3f})}}
= {rho_w:.5f}
""")

st.latex(rf"""
\lambda_s = \min\left(\sqrt{{\frac{{2}}{{1+d/10}}}},1\right)
= {lambda_s:.3f}
""")

st.latex(rf"""
A_v = ({Av_bar:.2f})({n_leg})
= {Av:.3f}\ in^2
""")

st.latex(rf"""
V_s = \frac{{A_v f_{{yt}} d}}{{s}}
= \frac{{({Av:.3f})({f_yt})({d_shear:.3f})}}{{{s}}}
\times \frac{{1}}{{1000}}
= {Vs:.2f}\ kips
""")

st.latex(rf"""
V_n = V_c + V_s
= {Vc:.2f} + {Vs:.2f}
= {Vn:.2f}\ kips
""")

st.latex(rf"""
\phi V_n = ({phi_v})({Vn:.2f})
= {V_factored:.2f}\ kips
""")