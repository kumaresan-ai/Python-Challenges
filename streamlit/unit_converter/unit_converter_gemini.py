import streamlit as st
import pandas as pd
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Universal Unit Converter",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a modern, dark theme look ---
st.markdown("""
<style>
    /* Main body and text colors for dark mode */
    .stApp {
        background-color: #0c0d12;
        color: #e0e0e0;
    }

    /* Container styling for a card-like effect */
    .stContainer {
        border-radius: 12px;
        padding: 30px;
        background-color: #1a1c24;
        border: 1px solid #2e303e;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input and select box styling */
    .stSelectbox, .stNumberInput {
        background-color: #2e303e !important;
        border-radius: 8px;
        color: #e0e0e0;
    }
    .stSelectbox div[role="button"], .stNumberInput input {
        background-color: #2e303e;
        color: #e0e0e0;
        border: none;
    }
    .stSelectbox div[aria-selected="true"], .stSelectbox div:hover {
        background-color: #3e4152 !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: #1a1c24;
        border-radius: 10px 10px 0 0;
        gap: 12px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
        border: 1px solid #2e303e;
        font-weight: bold;
        color: #8c909e;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2e303e;
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e303e;
        border-bottom: 3px solid #6495ED; /* A nice blue highlight */
        color: #e0e0e0;
    }

    /* Metric styling */
    div[data-testid="metric-container"] {
        background-color: rgba(26, 28, 36, 0.7);
        border: 1px solid rgba(46, 48, 62, 0.7);
        padding: 20px;
        border-radius: 12px;
        color: #e0e0e0;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #6495ED;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        color: #e0e0e0;
        font-weight: bold;
    }

    /* Download button styling */
    .stDownloadButton button {
        background-color: #6495ED;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stDownloadButton button:hover {
        background-color: #507cc7;
    }

</style>
""", unsafe_allow_html=True)

# --- Conversion Logic ---
CONVERSION_FACTORS = {
    "Length": {
        "Centimeter (cm)": {"meter": 0.01, "feet": 0.0328084, "inch": 0.393701},
        "Meter (m)": {"centimeter": 100, "feet": 3.28084, "inch": 39.3701},
        "Feet (ft)": {"centimeter": 30.48, "meter": 0.3048, "inch": 12},
        "Inch (in)": {"centimeter": 2.54, "meter": 0.0254, "feet": 0.0833333},
    },
    "Weight": {
        "Kilogram (kg)": {"pound": 2.20462, "gram": 1000, "ounce": 35.274},
        "Pound (lb)": {"kilogram": 0.453592, "gram": 453.592, "ounce": 16},
        "Gram (g)": {"kilogram": 0.001, "pound": 0.00220462, "ounce": 0.035274},
        "Ounce (oz)": {"kilogram": 0.0283495, "pound": 0.0625, "gram": 28.3495},
    },
    "Currency": {
        "US Dollar ($)": {"indian rupee": 83.0, "euro": 0.92, "japanese yen": 156.0},
        "Indian Rupee (₹)": {"us dollar": 0.012, "euro": 0.011, "japanese yen": 1.88},
        "Euro (€)": {"us dollar": 1.09, "indian rupee": 90.0, "japanese yen": 169.0},
        "Japanese Yen (¥)": {"us dollar": 0.0064, "indian rupee": 0.53, "euro": 0.0059},
    }
}

def convert_unit(value, from_unit, to_unit, category):
    """Performs unit conversion based on a predefined dictionary."""
    if category == "Temperature":
        return convert_temperature(value, from_unit, to_unit)
    
    # Generic linear conversion
    try:
        if from_unit == to_unit:
            return value
        
        # Normalize keys for lookup
        from_key = from_unit.split(" ")[0].lower()
        to_key = to_unit.split(" ")[0].lower()
        
        # Handle cases where direct conversion factor is missing
        if to_key in CONVERSION_FACTORS[category][from_unit]:
            return value * CONVERSION_FACTORS[category][from_unit][to_key]
        else:
            # Pivot through a base unit, e.g., kg for weight
            base_unit = list(CONVERSION_FACTORS[category].keys())[0]
            value_in_base = convert_unit(value, from_unit, base_unit, category)
            return convert_unit(value_in_base, base_unit, to_unit, category)

    except KeyError:
        return None

def convert_temperature(value, from_unit, to_unit):
    """Handles temperature conversion using specific formulas."""
    if from_unit == to_unit:
        return value
    
    # Convert all to Celsius first
    if from_unit == "Celsius (°C)":
        celsius = value
    elif from_unit == "Fahrenheit (°F)":
        celsius = (value - 32) * 5/9
    elif from_unit == "Kelvin (K)":
        celsius = value - 273.15
    else:
        return None # Unsupported unit

    # Convert from Celsius to the target unit
    if to_unit == "Celsius (°C)":
        return celsius
    elif to_unit == "Fahrenheit (°F)":
        return (celsius * 9/5) + 32
    elif to_unit == "Kelvin (K)":
        return celsius + 273.15
    else:
        return None # Unsupported unit

# --- Main UI ---
st.title("Universal Unit Converter 🔄")
st.markdown("Easily convert between different units with a modern and interactive interface. ")

tabs = st.tabs(["📏 Length", "⚖️ Weight", "💲 Currency", "🌡️ Temperature"])

# Helper function to render a tab
def render_tab(tab, category):
    with tab:
        st.subheader(f"Convert {category}")
        
        # Get units for the current category
        if category == "Temperature":
            units = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]
        else:
            units = list(CONVERSION_FACTORS[category].keys())

        col1, col2 = st.columns(2)
        with col1:
            from_unit = st.selectbox("From Unit", units, key=f"{category}_from_unit")
        with col2:
            to_unit = st.selectbox("To Unit", units, key=f"{category}_to_unit")
            
        value = st.number_input(f"Enter a value in {from_unit}", value=1.0, step=0.01, format="%.2f", key=f"{category}_value")
        
        if value is not None and value > 0:
            converted_value = convert_unit(value, from_unit, to_unit, category)
            if converted_value is not None:
                st.metric(label=f"Result", value=f"{converted_value:,.2f} {to_unit.split(' ')[0]}")
                
                # Prepare data for download
                data = {
                    "Category": [category],
                    "Input Value": [value],
                    "From Unit": [from_unit],
                    "To Unit": [to_unit],
                    "Converted Value": [converted_value]
                }
                df = pd.DataFrame(data)
                
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, sheet_name="Conversion_Report")
                excel_buffer.seek(0)
                
                st.download_button(
                    label="Download Report as Excel",
                    data=excel_buffer,
                    file_name=f"{category.lower().replace(' ', '_')}_conversion.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.error("Conversion not supported or invalid units selected.")
        else:
            st.warning("Please enter a valid positive number to convert.")

# Render each tab
render_tab(tabs[0], "Length")
render_tab(tabs[1], "Weight")
render_tab(tabs[2], "Currency")
render_tab(tabs[3], "Temperature")
