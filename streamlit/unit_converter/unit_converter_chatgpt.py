import streamlit as st
import pandas as pd
import math
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# -------------------
# Page config & dark theme
# -------------------
st.set_page_config(page_title="Modern Unit Converter", layout="centered", initial_sidebar_state="expanded")

# Dark theme CSS (modern look)
st.markdown(
    """
    <style>
        :root { --bg: #0b1220; --card: #0f1724; --muted: #94a3b8; --accent: #7c3aed; --glass: rgba(255,255,255,0.03); }
        .stApp { background: linear-gradient(180deg, var(--bg), #071021); color: #e6eef8; }
        .block-container { padding: 1rem 2rem; }
        .stButton>button { background: linear-gradient(90deg, #7c3aed, #06b6d4); border: none; }
        .stDownloadButton>button { background: linear-gradient(90deg, #06b6d4, #7c3aed); border: none; }
        .card { background: var(--card); border-radius: 12px; padding: 12px; box-shadow: 0 6px 18px rgba(2,6,23,0.6); }
        .muted { color: var(--muted); }
        .small { font-size: 0.9rem }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------
# Conversion helpers
# -------------------
# All categories convert via a common base unit. We'll convert input -> base -> target

CONVERSION_TABLE = {
    "Length": {
        # base: meter
        "meter": 1.0,
        "m": 1.0,
        "kilometer": 1000.0,
        "km": 1000.0,
        "centimeter": 0.01,
        "cm": 0.01,
        "millimeter": 0.001,
        "mm": 0.001,
        "micrometer": 1e-6,
        "mile": 1609.344,
        "yard": 0.9144,
        "foot": 0.3048,
        "feet": 0.3048,
        "inch": 0.0254,
    },
    "Area": {
        # base: square meter
        "square_meter": 1.0,
        "sqm": 1.0,
        "square_kilometer": 1e6,
        "sqkm": 1e6,
        "square_centimeter": 1e-4,
        "sqcm": 1e-4,
        "square_mile": 2589988.110336,
        "acre": 4046.8564224,
        "hectare": 10000.0,
    },
    "Volume": {
        # base: cubic meter
        "cubic_meter": 1.0,
        "m3": 1.0,
        "liter": 0.001,
        "l": 0.001,
        "milliliter": 1e-6,
        "ml": 1e-6,
        "cubic_centimeter": 1e-6,
        "cc": 1e-6,
        "gallon_us": 0.003785411784,
        "quart_us": 0.000946352946,
        "pint_us": 0.000473176473,
    },
    "Mass": {
        # base: kilogram
        "kilogram": 1.0,
        "kg": 1.0,
        "gram": 0.001,
        "g": 0.001,
        "milligram": 1e-6,
        "mg": 1e-6,
        "pound": 0.45359237,
        "lb": 0.45359237,
        "ounce": 0.028349523125,
        "oz": 0.028349523125,
    },
    "Temperature": {
        # special handling
        "celsius": "c",
        "fahrenheit": "f",
        "kelvin": "k",
    },
    "Speed": {
        # base: meter / second
        "m/s": 1.0,
        "km/h": 1000.0/3600.0,
        "kph": 1000.0/3600.0,
        "mph": 1609.344/3600.0,
        "foot/s": 0.3048,
    },
    "Time": {
        # base: second
        "second": 1.0,
        "s": 1.0,
        "minute": 60.0,
        "min": 60.0,
        "hour": 3600.0,
        "day": 86400.0,
    },
    "Data": {
        # base: byte
        "byte": 1,
        "b": 1,
        "kilobyte": 1024,
        "kb": 1024,
        "megabyte": 1024**2,
        "mb": 1024**2,
        "gigabyte": 1024**3,
        "gb": 1024**3,
        "terabyte": 1024**4,
        "tb": 1024**4,
    },
    "Energy": {
        # base: joule
        "joule": 1.0,
        "j": 1.0,
        "kilojoule": 1000.0,
        "kj": 1000.0,
        "calorie": 4.184,
        "kcal": 4184.0,
        "wh": 3600.0,
        "kwh": 3.6e6,
    },
    "Pressure": {
        # base: pascal
        "pascal": 1.0,
        "pa": 1.0,
        "bar": 1e5,
        "atm": 101325.0,
        "psi": 6894.757293168,
    },
    "Angle": {
        # base: radian
        "radian": 1.0,
        "rad": 1.0,
        "degree": math.pi/180.0,
        "deg": math.pi/180.0,
    },
}

# Currency: we'll use USD as base. Provide editable rates in settings
DEFAULT_CURRENCY_RATES = {
    "USD": 1.0,
    "INR": 86.0,  # sample fewshot
    "EUR": 0.92,
    "GBP": 0.80,
}


# Temperature conversion helpers
def temp_to_kelvin(value, unit):
    u = unit.lower()
    if u in ("celsius", "c"):
        return value + 273.15
    if u in ("fahrenheit", "f"):
        return (value - 32) * 5/9 + 273.15
    if u in ("kelvin", "k"):
        return value
    raise ValueError("Unknown temperature unit")


def kelvin_to_target(kelvin, unit):
    u = unit.lower()
    if u in ("celsius", "c"):
        return kelvin - 273.15
    if u in ("fahrenheit", "f"):
        return (kelvin - 273.15) * 9/5 + 32
    if u in ("kelvin", "k"):
        return kelvin
    raise ValueError("Unknown temperature unit")


# Generic conversion
def convert(category, from_unit, to_unit, value, currency_rates=None):
    if category == "Temperature":
        k = temp_to_kelvin(value, from_unit)
        return kelvin_to_target(k, to_unit)

    if category == "Currency":
        # Expect from_unit and to_unit as currency codes
        if currency_rates is None:
            currency_rates = DEFAULT_CURRENCY_RATES
        from_rate = currency_rates.get(from_unit.upper())
        to_rate = currency_rates.get(to_unit.upper())
        if from_rate is None or to_rate is None:
            raise ValueError("Unknown currency code or missing rate")
        # convert to USD base then to target
        value_in_usd = value / from_rate
        return value_in_usd * to_rate

    # Generic: use base units
    table = CONVERSION_TABLE.get(category)
    if table is None:
        raise ValueError("Unknown category")
    # normalize unit keys (some categories have hyphens etc.)
    # For safety, compare lowercase and common synonyms
    def find_key(u):
        lu = u.lower()
        for k in table.keys():
            if k.lower() == lu:
                return k
        # try simple replacements
        aliases = {
            "m": "meter", "km": "kilometer", "cm": "centimeter", "mm": "millimeter",
            "kg": "kilogram", "g": "gram", "lb": "pound", "lbs": "pound", "oz": "ounce",
            "s": "second", "min": "minute", "h": "hour",
            "l": "liter", "ml": "milliliter",
            "b": "byte", "kb": "kilobyte", "mb": "megabyte",
        }
        if lu in aliases and aliases[lu] in table:
            return aliases[lu]
        raise ValueError(f"Unit '{u}' not supported for category {category}")

    fk = find_key(from_unit)
    tk = find_key(to_unit)
    base_from = table[fk]
    base_to = table[tk]
    # numeric factors (convert value -> base -> target)
    result_in_base = value * base_from
    result = result_in_base / base_to
    return result


# -------------------
# UI - Single page, modern components
# -------------------
st.title("✨ Modern Unit Converter — Single Page")
st.caption("Convert between more than a dozen unit categories. Dark theme. Export results to Excel or PDF.")

with st.expander("Settings & Rates", expanded=False):
    st.markdown("<div class='small muted'>Edit currency rates (base = USD). These rates are static unless you update them.</div>", unsafe_allow_html=True)
    cols = st.columns([1,1,1,1])
    rates = {}
    rates["USD"] = cols[0].number_input("USD (base)", value=float(DEFAULT_CURRENCY_RATES.get("USD",1.0)), format="%.6f")
    rates["INR"] = cols[1].number_input("INR", value=float(DEFAULT_CURRENCY_RATES.get("INR",86.0)), format="%.6f")
    rates["EUR"] = cols[2].number_input("EUR", value=float(DEFAULT_CURRENCY_RATES.get("EUR",0.92)), format="%.6f")
    rates["GBP"] = cols[3].number_input("GBP", value=float(DEFAULT_CURRENCY_RATES.get("GBP",0.80)), format="%.6f")
    st.markdown("<div class='muted small'>Tip: To add more currencies, type their 3-letter codes in the conversion fields and include rates above by editing the code. You can also paste rates as a JSON in advanced mode.</div>", unsafe_allow_html=True)

# Layout: left column controls, right column results
controls, results = st.columns([1.1, 1])

with controls:
    category = st.selectbox("Choose category", [
        "Length","Area","Volume","Mass","Temperature","Speed","Time","Data","Energy","Pressure","Angle","Currency"
    ])

    input_value = st.number_input("Input value", value=1.0, format="%.6f")

    # Prepare unit options dynamically
    if category == "Currency":
        currency_list = list(rates.keys())
        from_unit = st.selectbox("From currency", currency_list, index=0)
        to_unit = st.selectbox("To currency", currency_list, index=1 if len(currency_list)>1 else 0)
    else:
        units = list(CONVERSION_TABLE[category].keys())
        # present pretty labels
        from_unit = st.selectbox("From unit", units, index=0)
        to_unit = st.selectbox("To unit", units, index=1 if len(units)>1 else 0)

    precision = st.slider("Result precision (decimal places)", min_value=0, max_value=8, value=4)

    convert_button = st.button("Convert")

    # Keep history in session state
    if "history" not in st.session_state:
        st.session_state.history = []

with results:
    st.subheader("Result")
    card = st.container()

if convert_button:
    try:
        result = convert(category, from_unit, to_unit, input_value, currency_rates=rates if category=="Currency" else None)
        formatted = f"{round(result, precision):.{precision}f}"
        # Display metrics + nice layout
        results.success(f"{input_value} {from_unit} = {formatted} {to_unit}")
        results.metric(label="Converted value", value=formatted)

        # Save to history
        rec = {
            "Category": category,
            "From": from_unit,
            "To": to_unit,
            "Input": input_value,
            "Output": float(result),
        }
        st.session_state.history.insert(0, rec)
    except Exception as e:
        results.error(f"Conversion error: {e}")

# Show history and export
st.markdown("---")

st.subheader("Conversion History")
if len(st.session_state.history) == 0:
    st.info("No conversions yet. Perform a conversion to populate history.")
else:
    df = pd.DataFrame(st.session_state.history)
    # show interactive dataframe
    st.dataframe(df)

    # Exports
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        # Excel
        to_write = BytesIO()
        with pd.ExcelWriter(to_write, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Conversions")
        st.download_button("Download Excel", data=to_write.getvalue(), file_name="conversions.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        # CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_bytes, file_name="conversions.csv", mime="text/csv")
    with col3:
        # PDF (simple)
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        text_object = c.beginText(40, 750)
        text_object.setFont("Helvetica", 10)
        text_object.textLine("Conversion History")
        text_object.textLine("")
        for r in st.session_state.history:
            line = f"{r['Category']}: {r['Input']} {r['From']} -> {round(r['Output'], precision)} {r['To']}"
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()
        pdf_bytes = pdf_buffer.getvalue()
        st.download_button("Download PDF", data=pdf_bytes, file_name="conversions.pdf", mime="application/pdf")

# Footer - quick examples and tips
st.markdown("---")
st.markdown("**Quick examples (fewshots):** 30 centimeter = 1 foot (approx), 1 dollar = 86 rupee (editable), 1 kilogram = 2.20462 pound")
st.markdown("<div class='muted small'>Want live currency rates or extra unit categories (like optics, chemistry units), or SOCKS theme instead of dark? Reply and I will extend the script.</div>", unsafe_allow_html=True)
