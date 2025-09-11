import streamlit as st

def calculate_bmi(weight, height, unit):
    """
    Calculates BMI based on weight and height in the specified unit.
    """
    if unit == 'Metric':
        # BMI formula: kg / m^2
        return weight / ((height / 100) ** 2)
    elif unit == 'US':
        # BMI formula: (lbs / in^2) * 703
        return (weight / (height ** 2)) * 703
    return None

def get_health_category(bmi):
    """
    Returns the health category based on BMI value.
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

def get_category_color(category):
    """
    Returns a color for the health category for better UI.
    """
    if category == "Underweight":
        return "orange"
    elif category == "Normal weight":
        return "green"
    elif category == "Overweight":
        return "yellow"
    else:
        return "red"

# --- Main Streamlit App ---

st.set_page_config(
    page_title="BMI Calculator",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Header with a modern look
st.title("Body Mass Index (BMI) Calculator ⚖️")
st.markdown("---")

# User input section
with st.container():
    st.header("Enter Your Details")
    
    # Unit selection: Metric or US
    unit_system = st.radio(
        "Select your preferred unit system:",
        ('Metric', 'US'),
        horizontal=True
    )

    if unit_system == 'Metric':
        st.info("Input height in centimeters (cm) and weight in kilograms (kg).")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, step=0.1, format="%.1f")
        with col2:
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, step=0.1, format="%.1f")
    else:
        st.info("Input height in inches (in) and weight in pounds (lbs).")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (in)", min_value=20.0, max_value=100.0, step=0.1, format="%.1f")
        with col2:
            weight = st.number_input("Weight (lbs)", min_value=1.0, max_value=1000.0, step=0.1, format="%.1f")

# Calculate button
st.markdown("---")
if st.button("Calculate BMI", use_container_width=True, type="primary"):
    if height > 0 and weight > 0:
        bmi_value = calculate_bmi(weight, height, unit_system)
        category = get_health_category(bmi_value)
        color = get_category_color(category)

        st.balloons()
        
        # Output section
        st.header("Results 📈")
        
        # Display BMI value with a stylish metric
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Your BMI is", value=f"{bmi_value:.2f}")
        with col2:
            st.markdown(f"### Health Category: <span style='color:{color};'>**{category}**</span>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Detailed health information
        st.subheader("BMI Categories")
        st.markdown("""
        - **Underweight**: BMI below 18.5
        - **Normal weight**: BMI of 18.5 to 24.9
        - **Overweight**: BMI of 25 to 29.9
        - **Obesity**: BMI of 30 or greater
        """)
    else:
        st.error("Please enter valid positive values for height and weight.")

# Footer/Sidebar with extra info
st.sidebar.title("About this app")
st.sidebar.info(
    "This is a simple BMI calculator built with Streamlit. "
    "BMI is a quick way to screen for weight categories, but it is not a diagnostic tool. "
    "Consult with a healthcare professional for a more comprehensive health assessment."
)