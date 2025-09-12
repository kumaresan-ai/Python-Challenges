# Requirements: Run the following in your terminal before executing this script:
# pip install streamlit pint fpdf pandas openpyxl requests

import streamlit as st
import requests
from pint import UnitRegistry
from fpdf import FPDF
import pandas as pd
import io

# Set page config for wide layout
st.set_page_config(layout="wide", page_title="Unit Converter")

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: white;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
    }
    .stSelectbox > div > div > div {
        background-color: #333333;
        color: white;
    }
    .stNumberInput > div > div > input {
        background-color: #333333;
        color: white;
    }
    .stMetric {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 10px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    .stSidebar .stSidebarContent {
        background-color: #252525;
    }
</style>
""", unsafe_allow_html=True)

# Define categories and units
categories = ["Length", "Weight", "Temperature", "Area", "Volume", "Speed", "Time", "Currency"]

units = {
    "Length": {
        "Meter": "meter",
        "Centimeter": "centimeter",
        "Millimeter": "millimeter",
        "Kilometer": "kilometer",
        "Inch": "inch",
        "Foot": "foot",
        "Yard": "yard",
        "Mile": "mile",
    },
    "Weight": {
        "Gram": "gram",
        "Kilogram": "kilogram",
        "Milligram": "milligram",
        "Pound": "pound",
        "Ounce": "ounce",
        "Ton": "ton",
    },
    "Temperature": {
        "Celsius": "degC",
        "Fahrenheit": "degF",
        "Kelvin": "kelvin",
    },
    "Area": {
        "Square Meter": "meter**2",
        "Square Centimeter": "centimeter**2",
        "Square Foot": "foot**2",
        "Square Inch": "inch**2",
        "Acre": "acre",
    },
    "Volume": {
        "Liter": "liter",
        "Milliliter": "milliliter",
        "Cubic Meter": "meter**3",
        "Gallon (US)": "us_gallon",
        "Pint (US)": "us_pint",
        "Cup (US)": "us_cup",
    },
    "Speed": {
        "Meter per Second": "meter/second",
        "Kilometer per Hour": "kilometer/hour",
        "Mile per Hour": "mile/hour",
    },
    "Time": {
        "Second": "second",
        "Minute": "minute",
        "Hour": "hour",
        "Day": "day",
    },
    "Currency": {
        "USD": "USD",
        "EUR": "EUR",
        "GBP": "GBP",
        "INR": "INR",
        "JPY": "JPY",
        "CAD": "CAD",
        "AUD": "AUD",
        "CNY": "CNY",
        "BTC": "BTC",  # Note: BTC may not be supported by the API, handle errors gracefully
    }
}

# Main title
st.title("🧮 Modern Unit Converter")
st.write("Select a category and units in the sidebar to perform conversions. Real-time currency rates are fetched from a reliable API.")

# Sidebar for inputs
with st.sidebar:
    st.header("Conversion Options")
    category = st.selectbox("Category", categories, help="Choose the type of unit to convert.")
    unit_labels = list(units[category].keys())
    from_unit_label = st.selectbox("From Unit", unit_labels)
    to_unit_label = st.selectbox("To Unit", unit_labels)
    value = st.number_input("Value to Convert", value=1.0, step=0.01, format="%.2f")
    convert_button = st.button("Convert", type="primary")

# Perform conversion if button is clicked
if convert_button:
    if category == "Currency":
        from_curr = units[category][from_unit_label]
        to_curr = units[category][to_unit_label]
        url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            rate = response.json()["rates"][to_curr]
            result = value * rate
        except Exception as e:
            st.error(f"Error fetching currency rate: {e}")
            result = None
    else:
        ur = UnitRegistry()
        from_pint_unit = units[category][from_unit_label]
        to_pint_unit = units[category][to_unit_label]
        try:
            qty = value * ur(from_pint_unit)
            converted = qty.to(to_pint_unit)
            result = converted.magnitude
        except Exception as e:
            st.error(f"Conversion error: {e}")
            result = None

    if result is not None:
        # Display result with modern metric component
        st.metric(label=f"{value:.2f} {from_unit_label} in {to_unit_label}", value=f"{result:.4f} {to_unit_label}", delta=None)

        # Prepare downloads
        conversion_text = f"{value:.2f} {from_unit_label} = {result:.4f} {to_unit_label}"

        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Unit Conversion Result", ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=conversion_text, ln=1, align="C")
        pdf_output = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            label="📄 Download PDF",
            data=pdf_output,
            file_name="unit_conversion.pdf",
            mime="application/pdf",
            help="Download the conversion result as a PDF file."
        )

        # Excel Download
        df = pd.DataFrame({
            "Category": [category],
            "Input Value": [value],
            "From Unit": [from_unit_label],
            "Converted Value": [result],
            "To Unit": [to_unit_label]
        })
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📊 Download Excel",
            data=buffer,
            file_name="unit_conversion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the conversion result as an Excel file."
        )