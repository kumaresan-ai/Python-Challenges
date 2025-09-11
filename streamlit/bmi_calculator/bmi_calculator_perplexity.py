import streamlit as st

# --- UI CONFIG ---
st.set_page_config(page_title="BMI Calculator", page_icon="⚖️", layout="centered")

# --- SIDEBAR ---
st.sidebar.title("BMI Calculator Options")
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
unit_height = st.sidebar.radio("Height unit", ["Centimeters", "Meters", "Feet/Inches"])
unit_weight = st.sidebar.radio("Weight unit", ["Kilograms", "Pounds"])
st.sidebar.markdown("#### Try different inputs and view instant BMI feedback.")

# --- MAIN TITLE ---
st.title("⚖️ Modern BMI Calculator")

# --- OPTIONAL: Age and Gender ---
col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender (optional)", ["Not specified", "Female", "Male", "Other"])
with col2:
    age = st.number_input("Age (optional)", min_value=0, max_value=120, step=1, value=25)

# --- HEIGHT INPUT ---
if unit_height == "Centimeters":
    height = st.number_input("Height (cm)", min_value=50.0, max_value=300.0, value=170.0)
    height_m = height / 100
elif unit_height == "Meters":
    height = st.number_input("Height (m)", min_value=0.5, max_value=3.0, value=1.70)
    height_m = height
else:
    feet = st.number_input("Height (feet)", min_value=2, max_value=9, value=5)
    inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=7)
    height_m = (feet * 12 + inches) * 0.0254

# --- WEIGHT INPUT ---
if unit_weight == "Kilograms":
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
else:
    weight_lbs = st.number_input("Weight (lbs)", min_value=22.0, max_value=661.0, value=154.0)
    weight = weight_lbs * 0.453592

# --- BMI CALCULATION ---
bmi = None
if height_m > 0:
    bmi = weight / (height_m ** 2)
    bmi_rounded = round(bmi, 2)
else:
    st.error("Please enter a valid, non-zero height.")

# --- BMI CATEGORY & COLOR ---
def bmi_category(bmi):
    if bmi is None:
        return "-", "gray"
    elif bmi < 16:
        return "Severe Underweight", "#bb2124"
    elif 16 <= bmi < 17:
        return "Moderate Underweight", "#e65100"
    elif 17 <= bmi < 18.5:
        return "Mild Underweight", "#fbb13c"
    elif 18.5 <= bmi < 25:
        return "Normal Weight", "#329932"
    elif 25 <= bmi < 30:
        return "Overweight", "#ff9800"
    elif 30 <= bmi < 35:
        return "Obesity Class I", "#f44336"
    elif 35 <= bmi < 40:
        return "Obesity Class II", "#b71c1c"
    else:
        return "Obesity Class III", "#8d0158"

cat, color = bmi_category(bmi)

# --- BMI RESULT ---
st.markdown("---")
if bmi:
    st.markdown(f"<h2 style='color:{color};'>Your BMI: {bmi_rounded}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:{color};'>{cat}</h4>", unsafe_allow_html=True)
    st.progress(min(bmi/40,1.0))
else:
    st.info("Input your height and weight to calculate BMI.")

# --- BMI CATEGORIES TABLE ---
st.markdown("#### BMI Categories Reference")
bmi_table = """
| Category                | BMI Range (kg/m²) |
|-------------------------|-------------------|
| Severe Underweight      | < 16              |
| Moderate Underweight    | 16 - 17           |
| Mild Underweight        | 17 - 18.5         |
| Normal Weight           | 18.5 - 25         |
| Overweight              | 25 - 30           |
| Obesity Class I         | 30 - 35           |
| Obesity Class II        | 35 - 40           |
| Obesity Class III       | > 40              |
"""
st.markdown(bmi_table)

st.caption("BMI is a useful screening tool but does not diagnose body fat percentage or overall health status.")

# --- STYLING: Optional for more advanced UI ---
if theme == "Dark":
    st.markdown(
        """
        <style>
        .reportview-container { background: #222; color: #ddd; }
        .sidebar .sidebar-content { background: #111; }
        </style>
        """, unsafe_allow_html=True)

