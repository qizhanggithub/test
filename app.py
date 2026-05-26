# Streamlit App - Moment Curvature Analysis using OpenSeesPy

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

import openseespy.opensees as ops
import opsvis as opsv

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Rectangular Section Moment Curvature Analysis",
    layout="wide"
)

st.title("Rectangular Section Moment Curvature Analysis")
st.write("Moment-curvature analysis using OpenSeesPy")

# =========================================================
# SIDEBAR INPUTS
# =========================================================

st.sidebar.header("Section Geometry")

colWidth = st.sidebar.number_input(
    "Section Width (m)",
    value=1.6,
    step=0.1,
    format="%.3f"
)

colDepth = st.sidebar.number_input(
    "Section Depth (m) - Parallel to load direction",
    value=1.4,
    step=0.1,
    format="%.3f"
)

cover = st.sidebar.number_input(
    "Concrete Clear Cover (m)",
    value=0.04,
    step=0.005,
    format="%.3f"
)



# =========================================================
# STEEL
# =========================================================

st.sidebar.header("Rebar")

fy = st.sidebar.number_input(
    "Steel Yield Strength fy (kPa)",
    value=400 * 1e3 * 1.1,
    step=1000.0,
    format="%.1f"
)

E = st.sidebar.number_input(
    "Steel Elastic Modulus E (kPa)",
    value=200 * 1e6,
    step=1e6,
    format="%.1f"
)

number_of_top_bars = st.sidebar.number_input(
    "Number of Top Bars",
    value=9,
    step=1
)

number_of_bot_bars = st.sidebar.number_input(
    "Number of Bottom Bars",
    value=9,
    step=1
)

bar_sizes = {
    "10M": 100e-6,
    "15M": 200e-6,
    "20M": 300e-6,
    "25M": 500e-6,
    "30M": 700e-6,
    "35M": 1000e-6,
    "45M": 1500e-6,
    "55M": 2500e-6
}

# top bars
top_bar_size = st.sidebar.selectbox(
    "Top Bar Size",
    options=list(bar_sizes.keys()),
    index=5   # default = 35M
)

# bottom bars
bot_bar_size = st.sidebar.selectbox(
    "Bottom Bar Size",
    options=list(bar_sizes.keys()),
    index=5   # default = 35M
)

# individual bar areas
As_top = bar_sizes[top_bar_size]
As_bot = bar_sizes[bot_bar_size]

# total reinforcement areas
Astotal_top = As_top * number_of_top_bars
Astotal_bot = As_bot * number_of_bot_bars


# =========================================================
# CONFINED CONCRETE
# =========================================================

st.sidebar.header("Confined Concrete Core")

fpc_confined = st.sidebar.number_input(
    "Confined concrete compressive strength at 28 days (kPa)",
    value=-35 * 1e3 * 1.25,
    step=1000.0,
    format="%.1f"
)

epsc0_confined = st.sidebar.number_input(
    "Confined concrete strain at maximum strength",
    value=-0.002,
    format="%.5f"
)

fpcu_confined = st.sidebar.number_input(
    "Confined concrete crushing strength, (kPa)",
    value=0.0,
    format="%.1f"
)

epsU_confined = st.sidebar.number_input(
    "Confined concrete strain at crushing strength",
    value=-0.006,
    format="%.5f"
)

# =========================================================
# UNCONFINED CONCRETE
# =========================================================

st.sidebar.header("Unconfined Concrete Cover")

fpc = st.sidebar.number_input(
    "Compressive strength at 28 days (kPa)",
    value=-35 * 1e3 * 1.25,
    step=1000.0,
    format="%.1f"
)

epsc0 = st.sidebar.number_input(
    "Strain at maximum strength",
    value=-0.002,
    format="%.5f"
)

fpcu = st.sidebar.number_input(
    "Crushing strength, (kPa)",
    value=0.0,
    format="%.1f"
)

epsU = st.sidebar.number_input(
    "Strain at crushing strength",
    value=-0.006,
    format="%.5f"
)

# =========================================================
# ANALYSIS PARAMETERS
# =========================================================

st.sidebar.header("Axial Load and Analysis Parameters")

axial_load_ratio = st.sidebar.number_input(
    "Axial Load Ratio",
    value=0.04,
    step=0.01,
    format="%.2f"
)

mu = st.sidebar.number_input(
    "Target Curvature Ductility",
    value=80,
    step=2
)

numIncr = st.sidebar.number_input(
    "Number of Increments",
    value=2000,
    step=100
)

# =========================================================
# COMPUTED AXIAL LOAD
# =========================================================

P = fpc * colWidth * colDepth * axial_load_ratio

st.sidebar.markdown("---")
st.sidebar.write("### Axial Load (kN)")
st.sidebar.write(f"P = {P:,.2f}")

# =========================================================
# RUN BUTTON
# =========================================================

run_analysis = st.button("Run Analysis")

# =========================================================
# MAIN ANALYSIS
# =========================================================

if run_analysis:

    try:

        # -------------------------------------------------
        # CLEAR MODEL
        # -------------------------------------------------

        ops.wipe()

        # -------------------------------------------------
        # MODEL
        # -------------------------------------------------

        ops.model('basic', '-ndm', 2, '-ndf', 3)

        # -------------------------------------------------
        # MATERIALS
        # -------------------------------------------------

        ops.uniaxialMaterial(
            'Concrete01',
            1,
            fpc_confined,
            epsc0_confined,
            fpcu_confined,
            epsU_confined
        )

        ops.uniaxialMaterial(
            'Concrete01',
            2,
            fpc,
            epsc0,
            fpcu,
            epsU
        )

        ops.uniaxialMaterial(
            'Steel01',
            3,
            fy,
            E,
            0.001
        )

        # -------------------------------------------------
        # SECTION GEOMETRY
        # -------------------------------------------------

        y1 = colDepth / 2
        z1 = colWidth / 2

        fib_sec_1 = [

            ['section', 'Fiber', 1, '-GJ', 1.0e6],

            ['patch', 'rect',
             1,
             30,
             30,
             cover - y1,
             cover - z1,
             y1 - cover,
             z1 - cover],

            ['patch', 'rect',
             2,
             30,
             2,
             -y1,
             z1 - cover,
             y1,
             z1],

            ['patch', 'rect',
             2,
             30,
             2,
             -y1,
             -z1,
             y1,
             cover - z1],

            ['patch', 'rect',
             2,
             2,
             30,
             -y1,
             cover - z1,
             cover - y1,
             z1 - cover],

            ['patch', 'rect',
             2,
             2,
             30,
             y1 - cover,
             cover - z1,
             y1,
             z1 - cover],

            ['layer', 'straight',
             3,
             number_of_top_bars,
             As_top,
             y1 - cover,
             z1 - cover,
             y1 - cover,
             cover - z1],

            ['layer', 'straight',
             3,
             number_of_bot_bars,
             As_bot,
             cover - y1,
             z1 - cover,
             cover - y1,
             cover - z1]

        ]

        opsv.fib_sec_list_to_cmds(fib_sec_1)

        # -------------------------------------------------
        # FIBER SECTION PLOT
        # -------------------------------------------------
        # -------------------------------------------------
        # FIBER SECTION PLOT
        # -------------------------------------------------

        st.subheader("Fiber Section")

        # create a new matplotlib figure
        plt.figure(figsize=(6, 6))

        matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']

        # plot section
        opsv.plot_fiber_section(
            fib_sec_1,
            matcolor=matcolor
        )

        plt.axis('equal')

        # get current figure
        fig1 = plt.gcf()

        # display in streamlit
        st.pyplot(fig1)

        # close figure to avoid duplication
        plt.close(fig1)



        # -------------------------------------------------
        # ESTIMATE YIELD CURVATURE
        # -------------------------------------------------

        d = colDepth - cover

        epsy = fy / E

        Ky = epsy / (0.7 * d * 39)

        # -------------------------------------------------
        # NODES
        # -------------------------------------------------

        ops.node(1, 0, 0)
        ops.node(2, 0, 0)

        ops.fix(1, 1, 1, 1)
        ops.fix(2, 0, 1, 0)

        # -------------------------------------------------
        # ELEMENT
        # -------------------------------------------------

        ops.element(
            'zeroLengthSection',
            1,
            1,
            2,
            1
        )

        # -------------------------------------------------
        # APPLY AXIAL LOAD
        # -------------------------------------------------

        ops.timeSeries('Constant', 1)

        ops.pattern('Plain', 1, 1)

        ops.load(2, P, 0, 0)

        # -------------------------------------------------
        # ANALYSIS SETUP
        # -------------------------------------------------

        ops.integrator('LoadControl', 0)

        ops.system('SparseGeneral', '-piv')

        ops.test('NormUnbalance', 1e-9, 50)

        ops.numberer('Plain')

        ops.constraints('Plain')

        ops.algorithm('Newton')

        ops.analysis('Static')

        ops.analyze(1)

        # -------------------------------------------------
        # MOMENT CURVATURE ANALYSIS
        # -------------------------------------------------

        ops.timeSeries('Linear', 2)

        ops.pattern('Plain', 2, 2)

        ops.load(2, 0, 0, 1)

        maxK = Ky * mu

        dK = maxK / numIncr

        ops.integrator(
            'DisplacementControl',
            2,
            3,
            dK,
            1,
            dK,
            dK
        )

        # -------------------------------------------------
        # RECORDER FILE
        # -------------------------------------------------

        import uuid

        output_file = f"moment_curvature_{uuid.uuid4().hex}.txt"
        # delete previous file if exists
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass

        ops.recorder(
            'Node',
            '-file',
            output_file,
            '-time',
            '-node',
            2,
            '-dof',
            3,
            'disp'
        )

        # -------------------------------------------------
        # RUN ANALYSIS
        # -------------------------------------------------

        ok = ops.analyze(numIncr)

        # Important: release OpenSees file lock
        ops.wipe()

        if ok != 0:

            st.error("Analysis failed to converge.")

        else:

            # -------------------------------------------------
            # LOAD RESULTS
            # -------------------------------------------------

            data = np.loadtxt(output_file)

            moment = data[:, 0]
            curvature = data[:, 1]

            max_moment = np.max(moment)

            # -------------------------------------------------
            # RESULTS SUMMARY
            # -------------------------------------------------

            st.subheader("Results")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Maximum Moment",
                f"{max_moment:,.2f}"
            )

            c2.metric(
                "Yield Curvature",
                f"{Ky:.6e}"
            )

            c3.metric(
                "Maximum Curvature",
                f"{maxK:.6e}"
            )

            # -------------------------------------------------
            # MOMENT-CURVATURE PLOT
            # -------------------------------------------------

            st.subheader("Moment-Curvature Plot")

            fig2, ax2 = plt.subplots(figsize=(10, 6))

            ax2.plot(
                curvature,
                moment,
                linewidth=2
            )

            ax2.set_xlabel("Curvature (1/m)")
            ax2.set_ylabel("Moment")

            ax2.set_title(
                "Moment-Curvature Relationship"
            )

            ax2.grid(True)

            st.pyplot(fig2)

            # -------------------------------------------------
            # DATA TABLE
            # -------------------------------------------------

            st.subheader("Moment-Curvature Data")

            df = pd.DataFrame({
                "Curvature": curvature,
                "Moment": moment
            })

            st.dataframe(df)

    except Exception as e:

        st.error(f"Error: {e}")
    
    if os.path.exists(output_file):
    os.remove(output_file)