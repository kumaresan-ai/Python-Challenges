import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Advanced BMI Calculator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bmi-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stSlider>div>div>div {
        background: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

class BMICalculator:
    def __init__(self):
        self.bmi_categories = {
            (0, 18.4): ("Underweight", "#ff6b6b", "⚠️"),
            (18.5, 24.9): ("Normal weight", "#51cf66", "✅"),
            (25, 29.9): ("Overweight", "#fcc419", "⚠️"),
            (30, 34.9): ("Obesity Class I", "#ff922b", "🔴"),
            (35, 39.9): ("Obesity Class II", "#f76707", "🔴"),
            (40, float('inf')): ("Obesity Class III", "#e03131", "🔴")
        }
    
    def calculate_bmi(self, weight, height, unit_system):
        """Calculate BMI based on weight, height, and unit system"""
        if unit_system == "Metric (kg/m)":
            height_m = height / 100  # Convert cm to meters
            bmi = weight / (height_m ** 2)
        else:  # Imperial (lbs/in)
            bmi = (weight / (height ** 2)) * 703
        return round(bmi, 1)
    
    def get_category(self, bmi):
        """Get BMI category and corresponding color"""
        for (low, high), (category, color, icon) in self.bmi_categories.items():
            if low <= bmi <= high:
                return category, color, icon
        return "Unknown", "#666666", "❓"
    
    def calculate_ideal_weight(self, height, unit_system):
        """Calculate ideal weight range"""
        if unit_system == "Metric (kg/m)":
            height_m = height / 100
            min_weight = 18.5 * (height_m ** 2)
            max_weight = 24.9 * (height_m ** 2)
            return round(min_weight, 1), round(max_weight, 1)
        else:
            min_weight = (18.5 * (height ** 2)) / 703
            max_weight = (24.9 * (height ** 2)) / 703
            return round(min_weight, 1), round(max_weight, 1)

def main():
    # Initialize calculator
    calculator = BMICalculator()
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ Advanced BMI Calculator</h1>', unsafe_allow_html=True)
    
    # Sidebar for additional options
    with st.sidebar:
        st.header("⚙️ Settings")
        unit_system = st.radio("Measurement System", ["Metric (kg/m)", "Imperial (lbs/in)"])
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        show_charts = st.checkbox("Show Charts", True)
        save_history = st.checkbox("Save Calculation History", True)
        
        st.header("📊 About BMI")
        st.info("""
        Body Mass Index (BMI) is a measure of body fat based on height and weight.
        
        **Categories:**
        - Underweight: < 18.5
        - Normal: 18.5 - 24.9
        - Overweight: 25 - 29.9
        - Obesity: ≥ 30
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📏 Enter Your Details")
        
        if unit_system == "Metric (kg/m)":
            weight = st.slider("Weight (kg)", 30.0, 200.0, 70.0, 0.1)
            height = st.slider("Height (cm)", 100.0, 250.0, 170.0, 0.1)
        else:
            weight = st.slider("Weight (lbs)", 66.0, 440.0, 154.0, 0.1)
            height = st.slider("Height (inches)", 39.0, 98.0, 67.0, 0.1)
        
        # Age and gender
        age = st.slider("Age", 2, 100, 30)
        gender = st.radio("Gender", ["Male", "Female", "Other"])
        
        # Calculate button
        calculate_clicked = st.button("Calculate BMI", use_container_width=True)
    
    with col2:
        if calculate_clicked:
            # Calculate BMI
            bmi = calculator.calculate_bmi(weight, height, unit_system)
            category, color, icon = calculator.get_category(bmi)
            
            # Display results
            st.markdown(f"""
            <div class="bmi-result">
                <h2>Your BMI: {bmi}</h2>
                <h3>{icon} {category}</h3>
                <p>Based on WHO classification</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional metrics
            min_ideal, max_ideal = calculator.calculate_ideal_weight(height, unit_system)
            weight_unit = "kg" if unit_system == "Metric (kg/m)" else "lbs"
            
            st.markdown("""
            <div class="metric-card">
                <h4>💡 Ideal Weight Range</h4>
                <p>For your height: {min_ideal} - {max_ideal} {weight_unit}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Health recommendations
            if category == "Underweight":
                recommendation = "Consider consulting a nutritionist for healthy weight gain strategies."
            elif category == "Normal weight":
                recommendation = "Maintain your current healthy lifestyle with balanced diet and regular exercise."
            elif category == "Overweight":
                recommendation = "Focus on gradual weight loss through diet and exercise. Consult a healthcare provider."
            else:
                recommendation = "Please consult with a healthcare professional for personalized advice."
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Health Recommendation</h4>
                <p>{recommendation}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # BMI chart
            if show_charts:
                st.subheader("📈 BMI Chart")
                categories = ["Underweight", "Normal", "Overweight", "Obesity I", "Obesity II", "Obesity III"]
                ranges = [18.4, 24.9, 29.9, 34.9, 39.9, 100]
                colors = ["#ff6b6b", "#51cf66", "#fcc419", "#ff922b", "#f76707", "#e03131"]
                
                fig = go.Figure()
                
                for i in range(len(ranges)):
                    low = 0 if i == 0 else ranges[i-1]
                    high = ranges[i]
                    fig.add_trace(go.Bar(
                        x=[categories[i]],
                        y=[high - low],
                        name=categories[i],
                        marker_color=colors[i],
                        hovertemplate=f"BMI: {low}-{high}<extra></extra>"
                    ))
                
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color='black'),
                    name=f'Your BMI: {bmi}'
                ))
                
                fig.update_layout(
                    barmode='stack',
                    title="BMI Categories",
                    showlegend=True,
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Save to history
            if save_history:
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                st.session_state.history.append({
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'bmi': bmi,
                    'category': category,
                    'weight': weight,
                    'height': height,
                    'unit_system': unit_system
                })
    
    # Display history if available
    if 'history' in st.session_state and st.session_state.history:
        st.header("📋 Calculation History")
        
        # Convert history to DataFrame for better display
        history_df = pd.DataFrame(st.session_state.history)
        
        # Display as table
        st.dataframe(
            history_df.style.apply(
                lambda x: ['background: #f0f8ff' if i % 2 == 0 else '' for i in range(len(x))],
                axis=0
            ),
            use_container_width=True
        )
        
        # Progress chart
        if len(st.session_state.history) > 1:
            st.subheader("📊 BMI Trend")
            trend_fig = px.line(
                history_df, 
                x='date', 
                y='bmi',
                title="Your BMI Over Time",
                markers=True
            )
            trend_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="BMI",
                showlegend=False
            )
            st.plotly_chart(trend_fig, use_container_width=True)
        
        # Clear history button
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

if __name__ == "__main__":
    main()