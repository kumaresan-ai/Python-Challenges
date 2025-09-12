import streamlit as st
import pandas as pd
from datetime import datetime
import pdfkit
import tempfile
import os

# Set page config first - must be the first Streamlit command
st.set_page_config(
    page_title="Universal Unit Converter",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme with modern UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.1);
    }
    
    .unit-card {
        background-color: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid #334155;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .unit-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stSelectbox, .stNumberInput {
        border-radius: 12px;
        border: 1px solid #334155;
        background-color: #1e293b;
        color: #e2e8f0;
    }
    
    .result-box {
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #475569;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border-left: 4px solid #667eea;
    }
    
    .conversion-history {
        background-color: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid #334155;
    }
    
    .download-btn {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1.5rem;
    }
    
    .stRadio > div {
        flex-direction: row;
        gap: 1rem;
    }
    
    .stRadio label {
        background-color: #1e293b;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stRadio label:hover {
        background-color: #334155;
        border-color: #667eea;
    }
    
    .stRadio input:checked + label {
        background-color: #667eea;
        border-color: #667eea;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #334155;
    }
    
    .stAlert {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 12px;
    }
    
    /* Modern toggle switch */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    </style>
""", unsafe_allow_html=True)

# Title with gradient effect
st.markdown('<h1 class="main-header">🌐 Universal Unit Converter</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>Convert between currencies, temperatures, lengths, weights and more with elegance</p>", unsafe_allow_html=True)

# Define conversion functions
def convert_currency(amount, from_unit, to_unit):
    # Exchange rates (as of a recent date, update as needed)
    rates = {
        'USD': 1.0,
        'EUR': 0.92,
        'GBP': 0.79,
        'INR': 83.5,
        'JPY': 149.5,
        'CAD': 1.36,
        'AUD': 1.52,
        'CHF': 0.89,
        'CNY': 7.22,
        'MXN': 18.3,
        'BRL': 5.05,
        'SGD': 1.34
    }
    
    if from_unit == to_unit:
        return amount
    
    if from_unit in rates and to_unit in rates:
        # Convert from source to USD, then USD to target
        usd_amount = amount / rates[from_unit]
        result = usd_amount * rates[to_unit]
        return round(result, 4)
    else:
        return None

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    
    # Convert to Celsius first
    if from_unit == "Celsius (°C)":
        celsius = value
    elif from_unit == "Fahrenheit (°F)":
        celsius = (value - 32) * 5/9
    elif from_unit == "Kelvin (K)":
        celsius = value - 273.15
    else:
        return None
    
    # Convert from Celsius to target
    if to_unit == "Celsius (°C)":
        return round(celsius, 4)
    elif to_unit == "Fahrenheit (°F)":
        return round((celsius * 9/5) + 32, 4)
    elif to_unit == "Kelvin (K)":
        return round(celsius + 273.15, 4)
    else:
        return None

def convert_length(value, from_unit, to_unit):
    # Convert to meters first
    to_meters = {
        'Millimeter (mm)': 0.001,
        'Centimeter (cm)': 0.01,
        'Meter (m)': 1.0,
        'Kilometer (km)': 1000.0,
        'Inch (in)': 0.0254,
        'Foot (ft)': 0.3048,
        'Yard (yd)': 0.9144,
        'Mile (mi)': 1609.34
    }
    
    if from_unit == to_unit:
        return value
    
    if from_unit in to_meters and to_unit in to_meters:
        meters = value * to_meters[from_unit]
        result = meters / to_meters[to_unit]
        return round(result, 6)
    else:
        return None

def convert_weight(value, from_unit, to_unit):
    # Convert to kilograms first
    to_kg = {
        'Milligram (mg)': 0.000001,
        'Gram (g)': 0.001,
        'Kilogram (kg)': 1.0,
        'Metric ton (t)': 1000.0,
        'Ounce (oz)': 0.0283495,
        'Pound (lb)': 0.453592,
        'Stone (st)': 6.35029
    }
    
    if from_unit == to_unit:
        return value
    
    if from_unit in to_kg and to_unit in to_kg:
        kg = value * to_kg[from_unit]
        result = kg / to_kg[to_unit]
        return round(result, 6)
    else:
        return None

def convert_area(value, from_unit, to_unit):
    # Convert to square meters first
    to_sqm = {
        'Square millimeter (mm²)': 0.000001,
        'Square centimeter (cm²)': 0.0001,
        'Square meter (m²)': 1.0,
        'Square kilometer (km²)': 1000000.0,
        'Square inch (in²)': 0.00064516,
        'Square foot (ft²)': 0.092903,
        'Square yard (yd²)': 0.836127,
        'Acre': 4046.86,
        'Hectare (ha)': 10000.0
    }
    
    if from_unit == to_unit:
        return value
    
    if from_unit in to_sqm and to_unit in to_sqm:
        sqm = value * to_sqm[from_unit]
        result = sqm / to_sqm[to_unit]
        return round(result, 6)
    else:
        return None

def convert_volume(value, from_unit, to_unit):
    # Convert to cubic meters first
    to_cubic_m = {
        'Cubic millimeter (mm³)': 1e-9,
        'Cubic centimeter (cm³)': 1e-6,
        'Cubic meter (m³)': 1.0,
        'Liter (L)': 0.001,
        'Milliliter (mL)': 1e-6,
        'US gallon (gal)': 0.00378541,
        'US quart (qt)': 0.000946353,
        'US pint (pt)': 0.000473176,
        'US cup': 0.000236588,
        'Imperial gallon': 0.00454609,
        'Imperial quart': 0.00113652,
        'Imperial pint': 0.000568261
    }
    
    if from_unit == to_unit:
        return value
    
    if from_unit in to_cubic_m and to_unit in to_cubic_m:
        cubic_m = value * to_cubic_m[from_unit]
        result = cubic_m / to_cubic_m[to_unit]
        return round(result, 6)
    else:
        return None

# Unit categories
categories = {
    "Currency": {
        "options": ["USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD", "CHF", "CNY", "MXN", "BRL", "SGD"],
        "converter": convert_currency,
        "symbol": "$"
    },
    "Temperature": {
        "options": ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
        "converter": convert_temperature,
        "symbol": "°"
    },
    "Length": {
        "options": ["Millimeter (mm)", "Centimeter (cm)", "Meter (m)", "Kilometer (km)", 
                   "Inch (in)", "Foot (ft)", "Yard (yd)", "Mile (mi)"],
        "converter": convert_length,
        "symbol": ""
    },
    "Weight": {
        "options": ["Milligram (mg)", "Gram (g)", "Kilogram (kg)", "Metric ton (t)", 
                   "Ounce (oz)", "Pound (lb)", "Stone (st)"],
        "converter": convert_weight,
        "symbol": ""
    },
    "Area": {
        "options": ["Square millimeter (mm²)", "Square centimeter (cm²)", "Square meter (m²)", 
                   "Square kilometer (km²)", "Square inch (in²)", "Square foot (ft²)", 
                   "Square yard (yd²)", "Acre", "Hectare (ha)"],
        "converter": convert_area,
        "symbol": ""
    },
    "Volume": {
        "options": ["Cubic millimeter (mm³)", "Cubic centimeter (cm³)", "Cubic meter (m³)", 
                   "Liter (L)", "Milliliter (mL)", "US gallon (gal)", "US quart (qt)", 
                   "US pint (pt)", "US cup", "Imperial gallon", "Imperial quart", "Imperial pint"],
        "converter": convert_volume,
        "symbol": ""
    }
}

# Initialize session state for history
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

# Create a container for the main content
with st.container():
    # Category selection
    category = st.radio("Select Conversion Type", list(categories.keys()), horizontal=True)
    
    # Get selected category data
    cat_data = categories[category]
    options = cat_data["options"]
    converter_func = cat_data["converter"]
    symbol = cat_data["symbol"]
    
    # Create two columns for from/to units
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### From")
        from_unit = st.selectbox("From Unit", options, key="from_unit")
        from_value = st.number_input(f"Enter {category} value", min_value=0.0, value=1.0, step=0.1, key="from_value")
    
    with col2:
        st.markdown("### To")
        to_unit = st.selectbox("To Unit", options, key="to_unit")
        st.write("")  # Empty space for alignment
        st.write("")  # Empty space for alignment
        convert_btn = st.button("🔄 Convert", use_container_width=True)
    
    # Perform conversion
    result = None
    if convert_btn:
        try:
            result = converter_func(from_value, from_unit, to_unit)
            if result is not None:
                # Add to history
                history_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "category": category,
                    "from_value": from_value,
                    "from_unit": from_unit,
                    "to_value": result,
                    "to_unit": to_unit
                }
                st.session_state.conversion_history.append(history_entry)
                
                # Display result
                st.markdown(f"""
                    <div class="result-box">
                        {from_value:.4f} {from_unit.split('(')[0].strip()} = {result:.4f} {to_unit.split('(')[0].strip()}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Conversion not supported for selected units.")
        except Exception as e:
            st.error(f"Error performing conversion: {str(e)}")
    
    # Show result if available
    if result is not None and convert_btn:
        # Show formatted result
        unit_name = from_unit.split('(')[0].strip()
        result_unit_name = to_unit.split('(')[0].strip()
        
        # Add some visual feedback
        st.success(f"✅ Successfully converted {from_value} {unit_name} to {result:.4f} {result_unit_name}")
    
    # Download options
    if result is not None and convert_btn:
        st.markdown("### 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            df = pd.DataFrame([{
                "Category": category,
                "From Value": from_value,
                "From Unit": from_unit,
                "To Value": result,
                "To Unit": to_unit,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            excel_buffer = pd.ExcelWriter("conversion_result.xlsx", engine='xlsxwriter')
            df.to_excel(excel_buffer, index=False, sheet_name='Conversion Result')
            excel_buffer.close()
            
            with open("conversion_result.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Download as Excel",
                    data=f.read(),
                    file_name="unit_conversion_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="excel_download"
                )
        
        with col2:
            # PDF download
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Unit Conversion Result</title>
                <style>
                    body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 40px; }}
                    .container {{ max-width: 800px; margin: 0 auto; background-color: #1e293b; padding: 40px; border-radius: 16px; }}
                    h1 {{ color: #667eea; text-align: center; }}
                    .result {{ font-size: 24px; text-align: center; margin: 30px 0; padding: 20px; background-color: #334155; border-radius: 12px; }}
                    .details {{ margin-top: 30px; }}
                    .details p {{ margin: 10px 0; }}
                    footer {{ margin-top: 50px; text-align: center; color: #64748b; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Unit Conversion Result</h1>
                    <div class="result">
                        {from_value:.4f} {from_unit.split('(')[0].strip()} = {result:.4f} {to_unit.split('(')[0].strip()}
                    </div>
                    <div class="details">
                        <p><strong>Category:</strong> {category}</p>
                        <p><strong>From:</strong> {from_value} {from_unit}</p>
                        <p><strong>To:</strong> {result:.4f} {to_unit}</p>
                        <p><strong>Date & Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                    <footer>
                        Universal Unit Converter © {datetime.now().year}
                    </footer>
                </div>
            </body>
            </html>
            """
            
            # Save HTML to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                tmp_file.write(html_content.encode('utf-8'))
                tmp_file_path = tmp_file.name
            
            # Convert HTML to PDF
            try:
                pdf_path = tmp_file_path.replace('.html', '.pdf')
                pdfkit.from_file(tmp_file_path, pdf_path)
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Download as PDF",
                        data=f.read(),
                        file_name="unit_conversion_result.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
                    
                # Clean up temporary files
                os.unlink(tmp_file_path)
                os.unlink(pdf_path)
                
            except Exception as e:
                st.warning("PDF generation requires wkhtmltopdf. Try installing it or use Excel instead.")

# History section
if len(st.session_state.conversion_history) > 0:
    st.markdown("---")
    st.markdown('<div class="conversion-history"><h3>🕒 Recent Conversions</h3></div>', unsafe_allow_html=True)
    
    # Display history as a table
    history_df = pd.DataFrame(st.session_state.conversion_history)
    history_df = history_df[['timestamp', 'category', 'from_value', 'from_unit', 'to_value', 'to_unit']]
    history_df.columns = ['Timestamp', 'Category', 'From Value', 'From Unit', 'To Value', 'To Unit']
    
    # Format numbers for better readability
    history_df['From Value'] = history_df['From Value'].apply(lambda x: f"{x:.4f}")
    history_df['To Value'] = history_df['To Value'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.conversion_history = []
        st.rerun()

# Footer
st.markdown("""
    <div class="footer">
        Universal Unit Converter • Powered by Streamlit • All conversions are accurate to 6 decimal places
    </div>
""", unsafe_allow_html=True)

# Additional information cards
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
    <div class="unit-card">
        <h3>💡 Quick Tips</h3>
        <ul style="color: #94a3b8; font-size: 0.95rem;">
            <li>Use decimal points for precise values</li>
            <li>Results are rounded to 4-6 decimal places</li>
            <li>Download results in Excel or PDF format</li>
            <li>History is saved automatically</li>
        </ul>
    </div>
    <div class="unit-card">
        <h3>⚡ Examples</h3>
        <ul style="color: #94a3b8; font-size: 0.95rem;">
            <li>30 cm = 1 ft</li>
            <li>1 USD = 83.5 INR</li>
            <li>1 kg = 2.2046 lb</li>
            <li>0°C = 32°F = 273.15 K</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)