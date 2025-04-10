# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="📊 Etsy Inventory Pro", 
    layout="wide",
    page_icon="📊"
)

# Rest of imports
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- Streamlit Style Setup ---
st.markdown("""
<style>
    .metric-box {
        background: #000000;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
        color: white !important;
    }
    .stPlotlyChart {
        border: none !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("📊 Professional Inventory Dashboard")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
        sales_col = next((col for col in df.columns if any(x in col.lower() for x in ['units', 'sales', 'qty'])), 'units_sold')
        product_col = next((col for col in df.columns if 'product' in col.lower()), 'product')
        
        df = df.rename(columns={
            date_col: 'date',
            sales_col: 'units_sold',
            product_col: 'product'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.error(f"❌ Data Error: {str(e)}")
        st.stop()

# --- Tile Heatmap Visualization ---
def create_tile_heatmap(df):
    # Prepare monthly sales data
    monthly_sales = df.copy()
    monthly_sales['month'] = monthly_sales['date'].dt.to_period('M').astype(str)
    heatmap_data = monthly_sales.groupby(['product', 'month'])['units_sold'].sum().reset_index()
    
    # Create tile heatmap
    fig = px.scatter(
        heatmap_data,
        x='month',
        y='product',
        size='units_sold',
        color='units_sold',
        color_continuous_scale='Viridis',
        size_max=40,
        hover_name='product',
        hover_data={'month': True, 'units_sold': True, 'product': False}
    )
    
    # Customize layout
    fig.update_layout(
        title='Sales Volume by Product and Month',
        xaxis_title='Month',
        yaxis_title='Product',
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode='closest'
    )
    
    # Make tiles square-like
    fig.update_traces(
        marker=dict(
            sizemode='area',
            line=dict(width=1, color='DarkSlateGrey')
        )
    )
    
    return fig

# --- [Keep all other existing functions exactly the same] ---
# (Keep create_forecast_chart, run_forecast functions from previous example)

# --- Main App ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # --- Tile Heatmap Section ---
    st.subheader("🧱 Sales Volume Tiles")
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <small>Tile size represents sales volume (larger = more units sold)</small>
    </div>
    """, unsafe_allow_html=True)
    heatmap_fig = create_tile_heatmap(df)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # --- [Keep all remaining existing code exactly the same] ---
    # (Keep product selection, inventory controls, forecasting, etc.)

else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
    if st.button("📥 Download Sample CSV"):
        sample_data = pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=90).strftime('%Y-%m-%d'),
            'units_sold': np.random.normal(15, 3, 90).clip(5, 30).astype(int),
            'product': ["Lavender Essential Oil"]*30 + ["Tea Tree Oil"]*30 + ["Eucalyptus Oil"]*30
        }).to_csv(index=False)
        st.download_button(
            label="⬇️ Download Now",
            data=sample_data,
            file_name="sample_sales_data.csv",
            mime="text/csv"
        )
