import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Page config
st.set_page_config(
    page_title="Advanced BMI Calculator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0052a3;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .bmi-category {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .underweight { background-color: #ff9999; color: #7a0000; }
    .normal { background-color: #99ff99; color: #006600; }
    .overweight { background-color: #ffff99; color: #996600; }
    .obese { background-color: #ff9999; color: #7a0000; }
    .header {
        text-align: center;
        padding: 20px 0;
        color: #333;
    }
    .info-box {
        background-color: #e6f7ff;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'unit_system' not in st.session_state:
    st.session_state.unit_system = "Metric (kg/cm)"
if 'show_trend' not in st.session_state:
    st.session_state.show_trend = False

# BMI calculation function
def calculate_bmi(weight, height, unit_system="metric"):
    """
    Calculate BMI based on weight and height
    Returns BMI value and category
    """
    if unit_system == "Metric (kg/cm)":
        height_m = height / 100  # Convert cm to m
        bmi = weight / (height_m ** 2)
    else:  # Imperial (lb/in)
        bmi = (weight * 703) / (height ** 2)
    
    # Determine category
    if bmi < 18.5:
        category = "Underweight"
        color_class = "underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        color_class = "normal"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color_class = "overweight"
    else:
        category = "Obese"
        color_class = "obese"
    
    return round(bmi, 2), category, color_class

# Save calculation to history
def save_to_history(weight, height, bmi, category, unit_system):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "category": category,
        "unit_system": unit_system
    }
    st.session_state.history.append(record)

# Export history function
def export_history():
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        return df.to_csv(index=False).encode('utf-8')
    return None

# BMI visualization function
def create_bmi_gauge(bmi_value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "BMI Value", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 18.5], 'color': '#ff9999'},
                {'range': [18.5, 25], 'color': '#99ff99'},
                {'range': [25, 30], 'color': '#ffff99'},
                {'range': [30, 50], 'color': '#ff9999'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': bmi_value
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# Health recommendations based on BMI
def get_health_recommendations(category, bmi):
    recommendations = {
        "Underweight": [
            "💡 Increase calorie intake with nutrient-dense foods",
            "💪 Focus on strength training to build muscle mass",
            "🥗 Eat more frequently (5-6 small meals per day)",
            "🥜 Include healthy fats like nuts, avocados, and olive oil",
            "🥛 Consider protein supplements if needed"
        ],
        "Normal weight": [
            "✅ Maintain your current healthy lifestyle",
            "🏃 Continue regular exercise (150 mins moderate activity per week)",
            "🥦 Eat a balanced diet with plenty of fruits and vegetables",
            "💧 Stay hydrated and get adequate sleep",
            "🩺 Schedule regular health check-ups"
        ],
        "Overweight": [
            "📉 Aim for gradual weight loss (1-2 lbs per week)",
            "🚶 Increase daily physical activity",
            "🍽️ Practice portion control and mindful eating",
            "🚭 Limit processed foods, sugar, and saturated fats",
            "💤 Ensure 7-9 hours of quality sleep per night"
        ],
        "Obese": [
            "🆘 Consult with a healthcare professional for guidance",
            "📉 Set realistic weight loss goals",
            "🏋️ Start with low-impact exercises (walking, swimming)",
            "📝 Keep a food diary to track eating patterns",
            "🧘 Consider behavioral therapy or support groups"
        ]
    }
    return recommendations.get(category, [])

# Main app
def main():
    st.markdown("<h1 class='header'>⚖️ Advanced BMI Calculator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Calculate your Body Mass Index with comprehensive analysis</p>", unsafe_allow_html=True)
    
    # Sidebar for settings and history
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Unit system selection
        unit_options = ["Metric (kg/cm)", "Imperial (lb/in)"]
        st.session_state.unit_system = st.selectbox(
            "Select Unit System",
            unit_options,
            index=0 if st.session_state.unit_system == "Metric (kg/cm)" else 1
        )
        
        st.markdown("---")
        st.header("📊 History")
        
        # Show history toggle
        st.session_state.show_trend = st.checkbox("Show BMI Trend Chart", value=st.session_state.show_trend)
        
        # Display history
        if len(st.session_state.history) > 0:
            st.write(f"Total calculations: {len(st.session_state.history)}")
            
            # Export button
            csv = export_history()
            st.download_button(
                label="📥 Export History (CSV)",
                data=csv,
                file_name="bmi_history.csv",
                mime="text/csv"
            )
            
            # Clear history button
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.experimental_rerun()
        else:
            st.info("No calculations yet. Your history will appear here.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📏 Enter Your Measurements")
        
        # Input fields based on unit system
        if st.session_state.unit_system == "Metric (kg/cm)":
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
        else:
            weight = st.number_input("Weight (lb)", min_value=2.2, max_value=1100.0, value=154.0, step=0.1)
            height = st.number_input("Height (in)", min_value=20.0, max_value=100.0, value=67.0, step=0.1)
        
        # Calculate button
        if st.button("🧮 Calculate BMI", use_container_width=True):
            bmi, category, color_class = calculate_bmi(weight, height, st.session_state.unit_system)
            
            # Save to history
            save_to_history(weight, height, bmi, category, st.session_state.unit_system)
            
            # Display results
            st.markdown(f"### 📊 Your Results")
            
            # Create columns for results display
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>BMI Value</h3>
                    <h1 style='color: #0066cc;'>{bmi}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                st.plotly_chart(create_bmi_gauge(bmi), use_container_width=True)
            
            with res_col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Category</h3>
                    <div class='bmi-category {color_class}'>
                        {category}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Ideal weight range
                if st.session_state.unit_system == "Metric (kg/cm)":
                    height_m = height / 100
                    ideal_min = 18.5 * (height_m ** 2)
                    ideal_max = 24.9 * (height_m ** 2)
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>Ideal Weight Range</h3>
                        <h4>{round(ideal_min, 1)} - {round(ideal_max, 1)} kg</h4>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    ideal_min = (18.5 * (height ** 2)) / 703
                    ideal_max = (24.9 * (height ** 2)) / 703
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>Ideal Weight Range</h3>
                        <h4>{round(ideal_min, 1)} - {round(ideal_max, 1)} lb</h4>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Health recommendations
            st.markdown("### 💡 Health Recommendations")
            recommendations = get_health_recommendations(category, bmi)
            for rec in recommendations:
                st.markdown(f"{rec}")
    
    with col2:
        st.markdown("### ℹ️ BMI Categories")
        st.markdown("""
        <div class='info-box'>
        <strong>Understanding BMI Categories:</strong><br>
        • < 18.5: Underweight<br>
        • 18.5-24.9: Normal weight<br>
        • 25-29.9: Overweight<br>
        • ≥ 30: Obese
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📚 What is BMI?")
        st.markdown("""
        Body Mass Index (BMI) is a measure of body fat based on height and weight. 
        While not perfect, it's widely used as a screening tool to identify potential weight problems.
        
        **Note:** BMI doesn't directly measure body fat and may not be accurate for athletes, 
        pregnant women, children, or the elderly.
        """)
        
        # BMI formula
        st.markdown("### 🧮 BMI Formula")
        if st.session_state.unit_system == "Metric (kg/cm)":
            st.latex(r"BMI = \frac{weight(kg)}{[height(m)]^2}")
        else:
            st.latex(r"BMI = \frac{weight(lb) \times 703}{[height(in)]^2}")

    # Show trend chart if enabled and history exists
    if st.session_state.show_trend and len(st.session_state.history) > 0:
        st.markdown("### 📈 Your BMI Trend")
        
        # Create trend chart
        df = pd.DataFrame(st.session_state.history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['bmi'],
            mode='lines+markers',
            name='BMI',
            line=dict(color='#0066cc', width=3),
            marker=dict(size=8, color='#0066cc')
        ))
        
        # Add category reference lines
        fig.add_hline(y=18.5, line_dash="dash", line_color="red", annotation_text="Underweight threshold")
        fig.add_hline(y=25, line_dash="dash", line_color="green", annotation_text="Normal threshold")
        fig.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="Overweight threshold")
        
        fig.update_layout(
            title="BMI Trend Over Time",
            xaxis_title="Date",
            yaxis_title="BMI Value",
            hovermode="x unified",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show recent history table
        st.markdown("### 📋 Recent Calculations")
        display_df = df.tail(5)[['date', 'weight', 'height', 'bmi', 'category']].copy()
        display_df.columns = ['Date', 'Weight', 'Height', 'BMI', 'Category']
        st.dataframe(display_df.style.format({
            'Weight': '{:.1f}',
            'Height': '{:.1f}',
            'BMI': '{:.2f}'
        }), use_container_width=True)

if __name__ == "__main__":
    main()