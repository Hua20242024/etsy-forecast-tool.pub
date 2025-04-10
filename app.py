import streamlit as st
import pandas as pd
import etsy_forecast as ef  # Import logic from etsy_forecast.py

# Set page title and layout
st.set_page_config(page_title="Ventory", page_icon="🔍", layout="centered")

# Custom CSS to style the page
st.markdown(
    """
    <style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }

    .header {
        font-size: 64px;
        font-weight: bold;
        color: #6a1b9a;  /* Purple color */
        text-align: center;
        margin-top: 50px;
    }

    .subheader {
        font-size: 18px;  /* Increased from 12px */
        text-align: center;
        color: #333333;
        margin-bottom: 30px;
        font-weight: 500;
    }

    .upload-btn {
        display: block;
        margin: 0 auto;
        background-color: #ffffff;
        color: #000000;
        font-size: 16px;
        padding: 10px 20px;
        border: 2px solid #0078d4;
        border-radius: 5px;
        cursor: pointer;
    }

    .upload-btn:hover {
        background-color: #0078d4;
        color: #ffffff;
    }

    .footer {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        text-align: center;
    }

    .footer a {
        text-decoration: none;
        color: #0078d4;
        font-size: 16px;
    }
    
    /* LinkedIn logo styling */
    .linkedin-logo {
        width: 32px;
        height: 32px;
        transition: transform 0.2s;
    }
    .linkedin-logo:hover {
        transform: scale(1.1);
    }
    </style>
    """, unsafe_allow_html=True
)

# Main page content
st.markdown('<div class="header">Ventory</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your sales and inventory partner</div>', unsafe_allow_html=True)

# File upload widget
uploaded_file = st.file_uploader("", type=["csv", "xlsx"], key="file_uploader")

if uploaded_file is not None:
    st.success("File successfully uploaded!")

    # Load the data
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Display the columns to help identify them
    st.write("Dataframe columns:", df.columns)

    # Try to find the 'product' column dynamically
    product_col = next((col for col in df.columns if 'product' in col.lower()), None)

    if product_col is None:
        st.error("No 'product' column found in the data.")
        st.stop()

    # Show the first few rows of the dataframe
    st.write(df.head())

    # Product selection
    product = st.selectbox("SELECT PRODUCT FOR DETAILED ANALYSIS", df[product_col].unique())
    product_df = df[df[product_col] == product]

    # Inventory settings
    current_stock = st.number_input("CURRENT STOCK (UNITS)", min_value=0, value=500)
    safety_stock = st.number_input("SAFETY STOCK (UNITS)", min_value=0, value=20)
    lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)

    # Run forecasting logic from etsy_forecast.py
    results = ef.run_forecast(product_df, current_stock, safety_stock, lead_time)

    # Display results (sales metrics)
    st.subheader("Sales Performance Metrics")
    m1, m2, m3, m4 = st.columns(4)

    m1.markdown(f"""
    <div class="metric-box">
        <h3>Historical Daily Average</h3>
        <h2>{results['hist_avg']} units</h2>
        <div class="variation">± {results['hist_std']} units variation</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="metric-box">
        <h3>Historical Monthly Average</h3>
        <h2>{round(results['hist_avg'] * 30)} units</h2>
        <div class="variation">± {round(results['hist_std'] * 30)} units variation</div>
    </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
    <div class="metric-box">
        <h3>Projected Daily Average</h3>
        <h2>{results['forecast_avg']} units</h2>
        <div class="variation">± {results['forecast_std']} units expected</div>
    </div>
    """, unsafe_allow_html=True)

    m4.markdown(f"""
    <div class="metric-box">
        <h3>Projected Monthly Average</h3>
        <h2>{round(results['forecast_avg'] * 30)} units</h2>
        <div class="variation">± {round(results['forecast_std'] * 30)} units expected</div>
    </div>
    """, unsafe_allow_html=True)

    # Forecast chart
    st.plotly_chart(ef.create_forecast_chart(product_df, results['forecast']), use_container_width=True)

    # Inventory Alerts
    st.subheader("Inventory Status")
    if current_stock <= results['reorder_point']:
        st.error(f"""
        🚨 **URGENT REORDER NEEDED**  
        - Suggested Quantity: **{results['order_qty']} units**  
        - Stockout in: **~{results['days_remaining']:.0f} days**  
        - Projected Stockout Date: **{results['stockout_date']}**
        """)
    else:
        st.success(f"""
        ✅ **INVENTORY HEALTHY**  
        - Reorder Point: **{results['reorder_point']} units**  
        - Current Stock Lasts: **{results['days_remaining'] + lead_time:.0f} days**  
        - Suggested Order Date: **{(datetime.now() + timedelta(days=results['days_remaining'])).strftime('%b %d')}**
        """)

# Footer with LinkedIn logo (fixed at bottom)
st.markdown(
    """
    <div class="footer">
        <a href="https://www.linkedin.com" target="_blank">
            <svg class="linkedin-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0A66C2">
                <path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True
)
