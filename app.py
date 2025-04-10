import streamlit as st
import pandas as pd
import etsy_forecast as ef  # Import the forecast processing logic

# Set page title
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

# File upload widget (without the "Upload CSV or Excel" label)
uploaded_file = st.file_uploader("", type=["csv", "xlsx"], key="file_uploader")

if uploaded_file is not None:
    st.success("File successfully uploaded!")
    # Process the file
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Display first 5 rows
    st.write("### Uploaded Data", df.head())

    # Process the data and generate forecast
    forecast_results = ef.process_sales_data(df)  # Assuming this function processes and forecasts data
    
    # Display forecast results (example)
    st.write("### Forecast Results")
    for product, result in forecast_results.items():
        st.write(f"#### Product: {product}")
        st.write(result['forecast'])  # Display the forecast data (can be a table)
        st.plotly_chart(result['graph'], use_container_width=True)  # Display the forecast graph

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
