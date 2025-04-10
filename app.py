import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.express as px

# ====================== #
#      PAGE CONFIG       #
# ====================== #
st.set_page_config(
    page_title="Ventory",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ====================== #
#       CSS STYLES       #
# ====================== #
st.markdown("""
<style>
    /* Main title */
    .main-title {
        font-size: 5rem;
        text-align: center;
        color: #6F36FF;
        font-weight: 800;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Subtitle */
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    
    /* LinkedIn logo */
    .linkedin-logo {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        text-align: center;
    }
    .linkedin-logo svg {
        width: 32px;
        height: 32px;
        fill: #0A66C2;
        opacity: 0.8;
    }
    
    /* Hide uploader text */
    [data-testid="stFileUploader"] div:first-child div:first-child {
        visibility: hidden;
        height: 0;
    }
    
    /* Style the upload button */
    [data-testid="stFileUploader"] div:first-child {
        background: #6F36FF;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        width: fit-content;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# ====================== #
#      DASHBOARD        #
# ====================== #
def show_dashboard(df):
    st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)
    
    # Your original analysis code here
    with st.expander("⚙️ INVENTORY SETTINGS", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            current_stock = st.number_input("CURRENT STOCK", min_value=0, value=500)
        with col2:
            safety_stock = st.number_input("SAFETY STOCK", min_value=0, value=20)
        with col3:
            lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)
    
    # Forecasting
    model = Prophet()
    model.fit(df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    # Show charts
    st.plotly_chart(px.line(forecast, x='ds', y='yhat', title="Sales Forecast"))
    st.plotly_chart(px.bar(df, x='date', y='units_sold', title="Historical Sales"))

# ====================== #
#      UPLOAD PAGE       #
# ====================== #
def show_upload():
    st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your sales and inventory partner</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["csv", "xlsx"], key="file_uploader")
    
    # LinkedIn logo
    st.markdown("""
    <div class="linkedin-logo">
        <a href="https://www.linkedin.com" target="_blank">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    return uploaded_file

# ====================== #
#      APP LOGIC         #
# ====================== #
if 'df' not in st.session_state:
    uploaded_file = show_upload()
    if uploaded_file:
        try:
            st.session_state.df = pd.read_csv(uploaded_file)  # or read_excel()
            st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")
else:
    show_dashboard(st.session_state.df)
