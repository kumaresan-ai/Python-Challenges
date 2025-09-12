import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import requests
import json

# Configure page
st.set_page_config(
    page_title="Universal Unit Converter",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and modern UI
st.markdown("""
<style>
    .main > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00d4ff;
        margin: 0.5rem 0;
    }
    
    .conversion-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .header-style {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for conversion history
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

# Main title
st.markdown('<h1 class="header-style">⚖️ Universal Unit Converter</h1>', unsafe_allow_html=True)

# Conversion definitions
CONVERSIONS = {
    "Length": {
        "Meter": 1.0,
        "Centimeter": 100.0,
        "Millimeter": 1000.0,
        "Kilometer": 0.001,
        "Inch": 39.3701,
        "Feet": 3.28084,
        "Yard": 1.09361,
        "Mile": 0.000621371,
        "Nautical Mile": 0.000539957
    },
    "Weight": {
        "Kilogram": 1.0,
        "Gram": 1000.0,
        "Pound": 2.20462,
        "Ounce": 35.274,
        "Stone": 0.157473,
        "Ton": 0.001,
        "Carat": 5000.0
    },
    "Temperature": {
        "Celsius": "C",
        "Fahrenheit": "F",
        "Kelvin": "K",
        "Rankine": "R"
    },
    "Area": {
        "Square Meter": 1.0,
        "Square Centimeter": 10000.0,
        "Square Kilometer": 0.000001,
        "Square Inch": 1550.0,
        "Square Feet": 10.7639,
        "Square Yard": 1.19599,
        "Acre": 0.000247105,
        "Hectare": 0.0001
    },
    "Volume": {
        "Liter": 1.0,
        "Milliliter": 1000.0,
        "Gallon (US)": 0.264172,
        "Gallon (UK)": 0.219969,
        "Quart": 1.05669,
        "Pint": 2.11338,
        "Cup": 4.22675,
        "Fluid Ounce": 33.814,
        "Cubic Meter": 0.001,
        "Cubic Centimeter": 1000.0
    },
    "Speed": {
        "Meter/Second": 1.0,
        "Kilometer/Hour": 3.6,
        "Mile/Hour": 2.23694,
        "Knot": 1.94384,
        "Feet/Second": 3.28084
    },
    "Energy": {
        "Joule": 1.0,
        "Kilojoule": 0.001,
        "Calorie": 0.239006,
        "Kilocalorie": 0.000239006,
        "BTU": 0.000947817,
        "Watt Hour": 0.000277778,
        "Kilowatt Hour": 2.77778e-7
    },
    "Currency": {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0,
        "INR": 83.0,
        "CNY": 6.5,
        "CAD": 1.25,
        "AUD": 1.35,
        "CHF": 0.92,
        "SEK": 8.5
    }
}

def convert_temperature(value, from_unit, to_unit):
    """Convert temperature between different units"""
    # Convert to Celsius first
    if from_unit == "Fahrenheit":
        celsius = (value - 32) * 5/9
    elif from_unit == "Kelvin":
        celsius = value - 273.15
    elif from_unit == "Rankine":
        celsius = (value - 491.67) * 5/9
    else:  # Celsius
        celsius = value
    
    # Convert from Celsius to target unit
    if to_unit == "Fahrenheit":
        return celsius * 9/5 + 32
    elif to_unit == "Kelvin":
        return celsius + 273.15
    elif to_unit == "Rankine":
        return celsius * 9/5 + 491.67
    else:  # Celsius
        return celsius

def convert_units(value, category, from_unit, to_unit):
    """Convert units within a category"""
    if category == "Temperature":
        return convert_temperature(value, from_unit, to_unit)
    else:
        conversion_factors = CONVERSIONS[category]
        # Convert to base unit first, then to target unit
        base_value = value / conversion_factors[from_unit]
        result = base_value * conversion_factors[to_unit]
        return result

def add_to_history(category, value, from_unit, to_unit, result):
    """Add conversion to history"""
    st.session_state.conversion_history.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Input": f"{value} {from_unit}",
        "Output": f"{result:.6f} {to_unit}",
        "Conversion": f"{value} {from_unit} = {result:.6f} {to_unit}"
    })

def create_pdf_report():
    """Create PDF report of conversion history"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=1,
        spaceAfter=30
    )
    title = Paragraph("Unit Conversion History Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    if st.session_state.conversion_history:
        # Create table data
        data = [["Timestamp", "Category", "Conversion"]]
        for item in st.session_state.conversion_history:
            data.append([
                item["Timestamp"],
                item["Category"],
                item["Conversion"]
            ])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        no_data = Paragraph("No conversion history available.", styles['Normal'])
        elements.append(no_data)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar for category selection
with st.sidebar:
    st.markdown("## 🎛️ Conversion Settings")
    
    # Category selection with modern selectbox
    category = st.selectbox(
        "Select Category",
        options=list(CONVERSIONS.keys()),
        index=0,
        help="Choose the type of units you want to convert"
    )
    
    st.markdown("---")
    
    # History section
    st.markdown("## 📊 Conversion History")
    if st.session_state.conversion_history:
        st.metric("Total Conversions", len(st.session_state.conversion_history))
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download PDF", use_container_width=True):
                pdf_buffer = create_pdf_report()
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        with col2:
            if st.session_state.conversion_history:
                df = pd.DataFrame(st.session_state.conversion_history)
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.conversion_history = []
            st.rerun()
    else:
        st.info("No conversions yet. Start converting to see history!")

# Main conversion interface
col1, col2, col3 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 📥 From")
    
    # Input value with modern number input
    input_value = st.number_input(
        "Enter value",
        value=1.0,
        step=0.01,
        format="%.6f",
        help="Enter the value you want to convert"
    )
    
    # From unit selection
    from_unit = st.selectbox(
        "From unit",
        options=list(CONVERSIONS[category].keys()),
        key="from_unit"
    )

with col2:
    st.markdown("### ")
    st.markdown("<div style='text-align: center; font-size: 3rem; margin-top: 1rem;'>→</div>", unsafe_allow_html=True)

with col3:
    st.markdown("### 📤 To")
    
    # To unit selection
    to_unit = st.selectbox(
        "To unit",
        options=list(CONVERSIONS[category].keys()),
        key="to_unit",
        index=1 if len(CONVERSIONS[category]) > 1 else 0
    )
    
    # Convert button with modern styling
    if st.button("🔄 Convert", type="primary", use_container_width=True):
        if from_unit != to_unit:
            try:
                result = convert_units(input_value, category, from_unit, to_unit)
                
                # Display result in a fancy container
                st.markdown(f"""
                <div class="conversion-result">
                    <div style="font-size: 0.9rem; opacity: 0.8;">Result</div>
                    <div style="font-size: 1.8rem; margin: 0.5rem 0;">{result:.6f}</div>
                    <div style="font-size: 1rem;">{to_unit}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to history
                add_to_history(category, input_value, from_unit, to_unit, result)
                
                # Show success message
                st.success(f"✅ {input_value} {from_unit} = {result:.6f} {to_unit}")
                
            except Exception as e:
                st.error(f"❌ Conversion error: {str(e)}")
        else:
            st.warning("⚠️ Please select different units for conversion")

# Display recent conversions
if st.session_state.conversion_history:
    st.markdown("---")
    st.markdown("## 📜 Recent Conversions")
    
    # Show last 5 conversions in expandable format
    with st.expander("View Recent History", expanded=True):
        recent_conversions = st.session_state.conversion_history[-5:]
        
        for i, conversion in enumerate(reversed(recent_conversions)):
            col1, col2, col3, col4 = st.columns([2, 1, 3, 2])
            
            with col1:
                st.markdown(f"**{conversion['Timestamp']}**")
            with col2:
                st.markdown(f"`{conversion['Category']}`")
            with col3:
                st.markdown(f"**{conversion['Conversion']}**")
            with col4:
                st.markdown("✅")
            
            if i < len(recent_conversions) - 1:
                st.markdown("---")

# Footer with additional info
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; opacity: 0.7;">
    <p>🔧 Universal Unit Converter | Built with Streamlit</p>
    <p>💡 Tip: Use the sidebar to download your conversion history as PDF or Excel</p>
</div>
""", unsafe_allow_html=True)

# Display current rates for currency (if currency category is selected)
if category == "Currency":
    st.markdown("---")
    st.markdown("## 💱 Current Exchange Rates (Base: USD)")
    
    # Create currency rate display
    currency_cols = st.columns(5)
    currencies = list(CONVERSIONS["Currency"].keys())
    
    for i, currency in enumerate(currencies):
        with currency_cols[i % 5]:
            if currency != "USD":
                rate = CONVERSIONS["Currency"][currency]
                st.metric(
                    label=f"USD to {currency}",
                    value=f"{rate:.2f}",
                    help=f"1 USD = {rate} {currency}"
                )

# Quick conversion examples based on category
st.markdown("---")
st.markdown(f"## 📋 Quick {category} Examples")

examples = {
    "Length": [
        "1 Meter = 3.281 Feet",
        "1 Kilometer = 0.621 Miles", 
        "1 Inch = 2.540 Centimeters"
    ],
    "Weight": [
        "1 Kilogram = 2.205 Pounds",
        "1 Pound = 453.592 Grams",
        "1 Ounce = 28.350 Grams"
    ],
    "Temperature": [
        "0°C = 32°F",
        "100°C = 212°F",
        "20°C = 68°F"
    ],
    "Currency": [
        "1 USD = 83 INR",
        "1 EUR = 1.18 USD",
        "1 GBP = 1.37 USD"
    ],
    "Volume": [
        "1 Liter = 0.264 Gallons (US)",
        "1 Gallon = 3.785 Liters",
        "1 Cup = 236.588 Milliliters"
    ]
}

example_cols = st.columns(3)
category_examples = examples.get(category, ["No examples available"])

for i, example in enumerate(category_examples[:3]):
    with example_cols[i]:
        st.info(example)