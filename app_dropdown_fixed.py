
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drug Dosage Calculator", layout="centered")

# Custom styles
st.markdown("""
    <style>
    * {
        font-family: 'TH Sarabun New', sans-serif;
    }
    h1 {
        font-size: 30pt !important;
        font-weight: bold !important;
        color: black;
    }
    label, .stSelectbox label, .stTextInput label {
        font-size: 25pt !important;
    }
    .orange-button > button {
        background-color: #FFA500 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 22pt !important;
        height: 3em;
        width: 100%;
        border: none;
        border-radius: 8px;
    }
    .pink-button > button {
        background-color: #FF9997 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 22pt !important;
        height: 3em;
        width: 100%;
        border: none;
        border-radius: 8px;
    }
    thead tr th {
        background-color: #d4e6f1 !important;
        color: black !important;
        font-size: 20px;
        text-align: center;
        width: 50%;
    }
    tbody td {
        font-size: 18px;
        text-align: center;
        width: 50%;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    </style>
""", unsafe_allow_html=True)

st.title("คำนวณอัตราการให้ยา (mcg/kg/min → ml/hr)")

# Drug data and concentration (mg/ml)
drug_data = {
    "NTG": {"1:1": 1000, "1:2": 500, "1:5": 200, "1:10": 100},
    "Dobutamine": {"1:1": 1000, "2:1": 2000, "4:1": 4000},
    "Dopamine": {"1:1": 1000, "2:1": 2000, "4:1": 4000},
    "Adrenaline": {"2:50": 40, "4:50": 80, "8:50": 160},
    "Levophed": {"2:50": 40, "4:50": 80, "8:50": 160},
    "Primacor": {"1mg/ml": 1000}
}

dose_ranges = {
    "NTG": [x / 2 for x in range(1, 11)],
    "Dobutamine": list(range(1, 16)),
    "Dopamine": list(range(1, 16)),
    "Adrenaline": [round(x * 0.01, 2) for x in list(range(1, 11)) + [20, 30, 40, 50]],
    "Levophed": [round(x * 0.01, 2) for x in list(range(1, 11)) + [20, 30, 40, 50]],
    "Primacor": [0.25, 0.35, 0.5, 0.75, 1, 1.2, 1.5]
}

# Session state default values
if "weight" not in st.session_state:
    st.session_state.weight = ""
if "drug" not in st.session_state:
    st.session_state.drug = list(drug_data.keys())[0]
if "concentration" not in st.session_state:
    st.session_state.concentration = list(drug_data[st.session_state.drug].keys())[0]

# Drug selection
st.session_state.drug = st.selectbox("เลือกชนิดยา", list(drug_data.keys()), index=list(drug_data.keys()).index(st.session_state.drug))

# Update concentration options dynamically based on selected drug
concentration_options = list(drug_data[st.session_state.drug].keys())
if st.session_state.concentration not in concentration_options:
    st.session_state.concentration = concentration_options[0]
st.session_state.concentration = st.selectbox("เลือกรูปแบบความเข้มข้น", concentration_options, index=concentration_options.index(st.session_state.concentration))

# Input form
with st.form(key="dose_form"):
    weight_input = st.text_input("น้ำหนักผู้ป่วย (kg)", value=st.session_state.weight, max_chars=10)
    col1, col2 = st.columns([3, 1])
    with col1:
        calculate = st.form_submit_button("คลิกที่นี่เพื่อคำนวณ")
    with col2:
        reset = st.form_submit_button("ล้างข้อมูล")

    # Styling buttons
    st.markdown("""
    <script>
    const buttons = window.parent.document.querySelectorAll('button');
    if (buttons.length > 1) {
        buttons[0].classList.add('orange-button');
        buttons[1].classList.add('pink-button');
    }
    </script>
    """, unsafe_allow_html=True)

# Reset values
if reset:
    st.session_state.weight = ""
    st.session_state.drug = list(drug_data.keys())[0]
    st.session_state.concentration = list(drug_data[st.session_state.drug].keys())[0]
    st.experimental_rerun()

# Calculate
if calculate:
    st.session_state.weight = weight_input

    if not weight_input:
        st.warning("กรุณาระบุน้ำหนัก")
    else:
        try:
            weight = float(weight_input)
            drug = st.session_state.drug
            concentration = st.session_state.concentration
            conc_mcg_per_ml = drug_data[drug][concentration]
            doses = dose_ranges[drug]
            ml_hr_results = [(f"{dose:.2f}", f"{(weight * dose * 60 / conc_mcg_per_ml):.2f}") for dose in doses]
            df = pd.DataFrame(ml_hr_results, columns=["mcg/kg/min", "ml/hr"])

            st.subheader(f"ผลการคำนวณสำหรับ {drug} ({concentration})")
            st.write(df.to_html(index=False), unsafe_allow_html=True)

            if drug == "Primacor":
                loading_mcg = weight * 50
                volume_ml = round(loading_mcg / 1000, 2)
                st.markdown("---")
                st.subheader("Primacor Loading Dose")
                st.markdown(f"- Loading dose via pump = **{loading_mcg:.0f} mcg**")
                st.markdown(f"- ปริมาณยาที่ต้องเตรียม (1mg/ml) = **{volume_ml} ml**")

            st.markdown("""
            <br>
            <form action="javascript:window.print()">
                <button style="background-color: #FFA500; color: black; font-weight: bold; font-size: 22pt; height: 3em; width: 100%; border: none; border-radius: 8px;">
                    Print
                </button>
            </form>
            """, unsafe_allow_html=True)
        except ValueError:
            st.error("กรุณาระบุน้ำหนักเป็นตัวเลข เช่น 60.00")
