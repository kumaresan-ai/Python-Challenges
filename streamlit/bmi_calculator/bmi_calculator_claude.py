import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="BMI Calculator Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .health-tip {
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for history
if 'bmi_history' not in st.session_state:
    st.session_state.bmi_history = []

def calculate_bmi(weight, height_m):
    """Calculate BMI and return value with category"""
    bmi = weight / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "#3498db"
        risk = "Low"
    elif 18.5 <= bmi < 25:
        category = "Normal Weight"
        color = "#2ecc71"
        risk = "Low"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "#f39c12"
        risk = "Moderate"
    elif 30 <= bmi < 35:
        category = "Obesity Class I"
        color = "#e74c3c"
        risk = "High"
    elif 35 <= bmi < 40:
        category = "Obesity Class II"
        color = "#c0392b"
        risk = "Very High"
    else:
        category = "Obesity Class III"
        color = "#8b0000"
        risk = "Extremely High"
    
    return round(bmi, 1), category, color, risk

def get_health_recommendations(bmi, category):
    """Get personalized health recommendations based on BMI category"""
    recommendations = {
        "Underweight": [
            "🍎 Focus on nutrient-dense, calorie-rich foods",
            "💪 Include strength training exercises",
            "🥛 Consider healthy weight gain strategies",
            "👨‍⚕️ Consult with a healthcare provider"
        ],
        "Normal Weight": [
            "✅ Maintain current healthy lifestyle",
            "🏃‍♂️ Continue regular physical activity",
            "🥗 Keep balanced nutrition habits",
            "📊 Monitor weight regularly"
        ],
        "Overweight": [
            "🍽️ Create a moderate caloric deficit",
            "🚶‍♂️ Increase daily physical activity",
            "💧 Stay well hydrated",
            "📱 Consider tracking food intake"
        ],
        "Obesity Class I": [
            "🎯 Aim for 5-10% weight loss initially",
            "🏋️‍♀️ Combine cardio and strength training",
            "🥬 Focus on whole, unprocessed foods",
            "👥 Consider professional guidance"
        ],
        "Obesity Class II": [
            "⚕️ Consult healthcare provider for comprehensive plan",
            "📉 Set realistic, gradual weight loss goals",
            "🍳 Work with a registered dietitian",
            "🏊‍♂️ Start with low-impact exercises"
        ],
        "Obesity Class III": [
            "🚨 Seek immediate medical consultation",
            "🏥 Consider medically supervised weight loss",
            "💊 Discuss potential medical interventions",
            "👥 Build a healthcare support team"
        ]
    }
    return recommendations.get(category, [])

def create_bmi_gauge(bmi, category, color):
    """Create a BMI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"BMI: {category}"},
        delta = {'reference': 22.5, 'position': "top"},
        gauge = {
            'axis': {'range': [None, 45], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 18.5], 'color': '#e3f2fd'},
                {'range': [18.5, 25], 'color': '#e8f5e8'},
                {'range': [25, 30], 'color': '#fff3e0'},
                {'range': [30, 35], 'color': '#ffebee'},
                {'range': [35, 40], 'color': '#fce4ec'},
                {'range': [40, 45], 'color': '#f3e5f5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': bmi
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def create_bmi_categories_chart():
    """Create BMI categories reference chart"""
    categories = ['Underweight', 'Normal', 'Overweight', 'Obesity I', 'Obesity II', 'Obesity III']
    ranges = ['< 18.5', '18.5 - 24.9', '25.0 - 29.9', '30.0 - 34.9', '35.0 - 39.9', '≥ 40.0']
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#c0392b', '#8b0000']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=[18.5, 6.4, 4.9, 4.9, 4.9, 10],  # Heights for visualization
            marker_color=colors,
            text=ranges,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="BMI Categories Reference",
        xaxis_title="Category",
        yaxis_title="BMI Range",
        height=400,
        showlegend=False
    )
    
    return fig

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">⚖️ BMI Calculator Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    st.sidebar.header("📊 Input Your Details")
    
    # Personal Information
    st.sidebar.subheader("Personal Info")
    name = st.sidebar.text_input("Name (Optional)", placeholder="Enter your name")
    age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    
    # Unit selection
    st.sidebar.subheader("⚖️ Measurement Units")
    unit_system = st.sidebar.radio("Choose Unit System", ["Metric (kg/cm)", "Imperial (lbs/ft-in)"])
    
    # Weight input
    st.sidebar.subheader("Weight")
    if unit_system == "Metric (kg/cm)":
        weight = st.sidebar.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
        weight_kg = weight
    else:
        weight_lbs = st.sidebar.number_input("Weight (lbs)", min_value=1.0, max_value=1100.0, value=154.0, step=0.1)
        weight_kg = weight_lbs * 0.453592
    
    # Height input
    st.sidebar.subheader("Height")
    if unit_system == "Metric (kg/cm)":
        height_input_type = st.sidebar.radio("Height Input", ["Centimeters", "Meters"])
        if height_input_type == "Centimeters":
            height_cm = st.sidebar.number_input("Height (cm)", min_value=30.0, max_value=300.0, value=170.0, step=0.1)
            height_m = height_cm / 100
        else:
            height_m = st.sidebar.number_input("Height (m)", min_value=0.3, max_value=3.0, value=1.70, step=0.01)
    else:
        col1, col2 = st.sidebar.columns(2)
        feet = col1.number_input("Feet", min_value=1, max_value=9, value=5)
        inches = col2.number_input("Inches", min_value=0, max_value=11, value=7)
        height_m = (feet * 12 + inches) * 0.0254
    
    # Activity Level
    st.sidebar.subheader("💪 Activity Level")
    activity_level = st.sidebar.selectbox(
        "Select your activity level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
    )
    
    # Calculate BMI
    if st.sidebar.button("Calculate BMI", type="primary"):
        bmi, category, color, risk = calculate_bmi(weight_kg, height_m)
        
        # Store in history
        entry = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'name': name if name else 'Anonymous',
            'bmi': bmi,
            'category': category,
            'weight': weight_kg,
            'height': height_m
        }
        st.session_state.bmi_history.append(entry)
        
        # Main content area
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # BMI Result
            st.markdown(f"""
            <div class="metric-card">
                <h2>Your BMI: {bmi}</h2>
                <h3>{category}</h3>
                <p>Health Risk Level: {risk}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display gauge
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(create_bmi_gauge(bmi, category, color), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_bmi_categories_chart(), use_container_width=True)
        
        # Health recommendations
        st.subheader("🎯 Personalized Health Recommendations")
        recommendations = get_health_recommendations(bmi, category)
        
        for rec in recommendations:
            st.markdown(f"""
            <div class="health-tip">
                {rec}
            </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics
        st.subheader("📈 Additional Health Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Ideal weight range
        ideal_weight_min = 18.5 * (height_m ** 2)
        ideal_weight_max = 24.9 * (height_m ** 2)
        
        with col1:
            st.metric("Ideal Weight Range", f"{ideal_weight_min:.1f} - {ideal_weight_max:.1f} kg")
        
        with col2:
            weight_to_lose = max(0, weight_kg - ideal_weight_max)
            weight_to_gain = max(0, ideal_weight_min - weight_kg)
            change_needed = weight_to_lose if weight_to_lose > 0 else -weight_to_gain
            st.metric("Weight Change Needed", f"{change_needed:+.1f} kg")
        
        # BMR calculation (Mifflin-St Jeor Equation)
        if gender == "Male":
            bmr = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age - 161
        
        # Activity multipliers
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Extremely Active": 1.9
        }
        
        tdee = bmr * activity_multipliers[activity_level]
        
        with col3:
            st.metric("BMR (Calories/day)", f"{bmr:.0f}")
        
        with col4:
            st.metric("TDEE (Calories/day)", f"{tdee:.0f}")
        
        # BMI History
        if len(st.session_state.bmi_history) > 1:
            st.subheader("📊 BMI History")
            
            history_df = pd.DataFrame(st.session_state.bmi_history)
            history_df['date'] = pd.to_datetime(history_df['date'])
            
            fig = px.line(history_df, x='date', y='bmi', 
                         title='BMI Trend Over Time',
                         markers=True)
            fig.add_hline(y=18.5, line_dash="dash", line_color="blue", annotation_text="Underweight")
            fig.add_hline(y=25, line_dash="dash", line_color="green", annotation_text="Normal")
            fig.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="Overweight")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # History table
            with st.expander("View Detailed History"):
                st.dataframe(history_df[['date', 'name', 'bmi', 'category']].sort_values('date', ascending=False))
    
    # BMI Information
    st.subheader("ℹ️ About BMI")
    
    tab1, tab2, tab3 = st.tabs(["What is BMI?", "Limitations", "Health Tips"])
    
    with tab1:
        st.write("""
        **Body Mass Index (BMI)** is a measure of body fat based on height and weight. 
        It's calculated as weight in kilograms divided by height in meters squared (kg/m²).
        
        BMI categories:
        - **Underweight**: BMI less than 18.5
        - **Normal weight**: BMI 18.5-24.9
        - **Overweight**: BMI 25-29.9
        - **Obesity**: BMI 30 or greater
        """)
    
    with tab2:
        st.write("""
        BMI has some limitations:
        - Doesn't distinguish between muscle and fat mass
        - May not be accurate for athletes with high muscle mass
        - Doesn't account for fat distribution
        - May not be suitable for certain ethnic groups
        - Doesn't consider age-related changes in body composition
        """)
    
    with tab3:
        st.write("""
        General health tips:
        - Maintain a balanced, nutritious diet
        - Engage in regular physical activity
        - Stay hydrated
        - Get adequate sleep (7-9 hours for adults)
        - Manage stress levels
        - Regular health check-ups
        - Avoid smoking and limit alcohol consumption
        """)
    
    # Clear history button
    if st.session_state.bmi_history:
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.bmi_history = []
            st.success("History cleared!")
            st.experimental_rerun()

if __name__ == "__main__":
    main()