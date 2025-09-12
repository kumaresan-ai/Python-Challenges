import streamlit as st
import pandas as pd
import json
from io import BytesIO
from fpdf import FPDF
import tempfile

# Page configuration
st.set_page_config(
    page_title="Universal Unit Converter",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and modern styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #262730;
        color: white;
        border-radius: 8px;
    }
    .stNumberInput input {
        background-color: #262730;
        color: white;
        border-radius: 8px;
    }
    .conversion-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #777;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Conversion data
conversion_data = {
    "Length": {
        "meter": 1,
        "kilometer": 1000,
        "centimeter": 0.01,
        "millimeter": 0.001,
        "mile": 1609.34,
        "yard": 0.9144,
        "foot": 0.3048,
        "inch": 0.0254
    },
    "Weight": {
        "kilogram": 1,
        "gram": 0.001,
        "milligram": 0.000001,
        "pound": 0.453592,
        "ounce": 0.0283495,
        "ton": 1000
    },
    "Temperature": {
        "celsius": {"formula": lambda x, to: (x * 9/5) + 32 if to == "fahrenheit" else x + 273.15 if to == "kelvin" else x},
        "fahrenheit": {"formula": lambda x, to: (x - 32) * 5/9 if to == "celsius" else (x - 32) * 5/9 + 273.15 if to == "kelvin" else x},
        "kelvin": {"formula": lambda x, to: x - 273.15 if to == "celsius" else (x - 273.15) * 9/5 + 32 if to == "fahrenheit" else x}
    },
    "Currency": {
        "USD": 1,
        "EUR": 1.12,
        "GBP": 1.27,
        "INR": 0.012,
        "JPY": 0.0069,
        "CAD": 0.74,
        "AUD": 0.67
    },
    "Volume": {
        "liter": 1,
        "milliliter": 0.001,
        "gallon": 3.78541,
        "quart": 0.946353,
        "pint": 0.473176,
        "cup": 0.24,
        "tablespoon": 0.0147868,
        "teaspoon": 0.00492892
    },
    "Time": {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 2629800,
        "year": 31557600
    }
}

# App title and description
st.title("🔁 Universal Unit Converter")
st.markdown("Convert between various units with this modern, easy-to-use tool.")

# Category selection
category = st.selectbox(
    "Select Conversion Type",
    list(conversion_data.keys()),
    help="Choose the type of units you want to convert"
)

# Initialize session state for conversion history
if 'history' not in st.session_state:
    st.session_state.history = []

# Conversion logic
def convert_units(value, from_unit, to_unit, category):
    if category == "Temperature":
        # Special handling for temperature
        return conversion_data[category][from_unit]["formula"](value, to_unit)
    else:
        # Convert to base unit first, then to target unit
        base_value = value * conversion_data[category][from_unit]
        return base_value / conversion_data[category][to_unit]

# Input section
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    value = st.number_input("Enter value", min_value=0.0, value=1.0, step=0.1, format="%.6f")

with col2:
    units = list(conversion_data[category].keys())
    from_unit = st.selectbox("From", units, index=0)

with col3:
    to_unit = st.selectbox("To", units, index=1 if len(units) > 1 else 0)

# Perform conversion
if st.button("Convert", use_container_width=True):
    try:
        result = convert_units(value, from_unit, to_unit, category)
        
        # Format result based on magnitude
        if abs(result) < 0.001:
            formatted_result = f"{result:.8f}"
        elif abs(result) < 1:
            formatted_result = f"{result:.6f}"
        elif abs(result) < 1000:
            formatted_result = f"{result:.4f}"
        else:
            formatted_result = f"{result:.2f}"
            
        # Display result in a nice card
        st.markdown(f"""
        <div class="conversion-card">
            <h3>{value} {from_unit} = {formatted_result} {to_unit}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Add to history
        st.session_state.history.append({
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": result,
            "category": category
        })
        
    except Exception as e:
        st.error(f"Error during conversion: {str(e)}")

# History section
if st.session_state.history:
    st.subheader("Conversion History")
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel export
        def convert_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Conversion History')
            processed_data = output.getvalue()
            return processed_data
        
        excel_data = convert_to_excel(history_df)
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name="conversion_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # PDF export
        def convert_to_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Conversion History", ln=True, align='C')
            pdf.ln(10)
            
            # Add table headers
            col_width = pdf.w / (len(df.columns) + 1)
            for col in df.columns:
                pdf.cell(col_width, 10, txt=str(col), border=1)
            pdf.ln()
            
            # Add table rows
            for index, row in df.iterrows():
                for item in row:
                    pdf.cell(col_width, 10, txt=str(item), border=1)
                pdf.ln()
                
            return pdf.output(dest='S').encode('latin1')
        
        pdf_data = convert_to_pdf(history_df)
        st.download_button(
            label="Download as PDF",
            data=pdf_data,
            file_name="conversion_history.pdf",
            mime="application/pdf"
        )

# Clear history button
if st.session_state.history:
    if st.button("Clear History", use_container_width=True):
        st.session_state.history = []
        st.experimental_rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>Built with Streamlit • Universal Unit Converter</p>
</div>
""", unsafe_allow_html=True)