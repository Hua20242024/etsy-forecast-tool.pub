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
    .metric-box h3 {
        color: #AAAAAA !important;
        font-size: 14px !important;
        margin-bottom: 5px !important;
    }
    .metric-box h2 {
        color: white !important;
        font-size: 24px !important;
        margin-top: 0 !important;
    }
    .metric-box .variation {
        font-size: 12px !important;
        color: #CCCCCC !important;
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
    
    # Create tile heatmap with red-to-green color scale
    fig = px.scatter(
        heatmap_data,
        x='month',
        y='product',
        size='units_sold',
        color='units_sold',
        color_continuous_scale=['#FF0000', '#FFFF00', '#00FF00'],  # Red -> Yellow -> Green
        size_max=50,
        hover_name='product',
        hover_data={'month': True, 'units_sold': True, 'product': False},
        title='<b>Sales Volume by Product and Month</b><br><i>Size and color indicate units sold</i>'
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Product',
        height=600,
        margin=dict(l=0, r=0, t=100, b=0),
        hovermode='closest',
        coloraxis_colorbar=dict(title='Units Sold')
    )
    
    # Make tiles square-like
    fig.update_traces(
        marker=dict(
            sizemode='area',
            line=dict(width=1, color='DarkSlateGrey'),
            opacity=0.8
        )
    )
    
    return fig

# --- Enhanced Plotly Visualization ---
def create_forecast_chart(actual_df, forecast_df):
    fig = go.Figure()
    
    # Convert datetime to timestamp for vline
    today_timestamp = datetime.now().timestamp() * 1000
    
    # Actual sales
    fig.add_trace(go.Scatter(
        x=actual_df['date'],
        y=actual_df['units_sold'],
        mode='markers+lines',
        name='Actual Sales',
        line=dict(color='#636EFA', dash='dot', width=1),
        marker=dict(size=5)
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#FF7F0E', width=2)
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat_upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat_lower'],
        fill='tonexty',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(width=0),
        name='Confidence Range'
    ))
    
    # Today's line
    fig.add_vline(
        x=today_timestamp,
        line_dash="dash",
        line_color="gray",
        annotation_text="Today",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title='Sales Forecast',
        xaxis_title='Date',
        yaxis_title='Units Sold',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

# --- Forecasting Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    model = Prophet(weekly_seasonality=True, daily_seasonality=False)
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    # Historical stats
    hist_avg = product_df['units_sold'].mean()
    hist_std = product_df['units_sold'].std()
    
    # Forecast stats
    forecast_avg = forecast['yhat'].mean()
    forecast_std = forecast['yhat'].std()
    next_30_days = forecast[forecast['ds'] <= (datetime.now() + timedelta(days=30))]['yhat'].mean()
    
    reorder_point = (forecast_avg * lead_time) + safety_stock
    days_remaining = max(0, (current_stock - reorder_point) / forecast_avg) if forecast_avg > 0 else 0
    
    return {
        'forecast': forecast,
        'hist_avg': round(hist_avg, 1),
        'hist_std': round(hist_std, 1),
        'forecast_avg': round(forecast_avg, 1),
        'forecast_std': round(forecast_std, 1),
        'next_30_days': round(next_30_days, 1),
        'reorder_point': round(reorder_point),
        'days_remaining': days_remaining,
        'order_qty': max(round(forecast_avg * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/forecast_avg)).strftime('%b %d')
    }

# --- Main App ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # --- Tile Heatmap Section ---
    st.subheader("🧱 Sales Volume Heatmap")
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <small>Tile size and color represent sales volume (larger/green = better sales)</small>
    </div>
    """, unsafe_allow_html=True)
    heatmap_fig = create_tile_heatmap(df)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # --- Product Selection ---
    product = st.selectbox("SELECT PRODUCT FOR DETAILED ANALYSIS", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory controls
    with st.expander("⚙️ INVENTORY SETTINGS", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            current_stock = st.number_input("CURRENT STOCK (UNITS)", min_value=0, value=500)
        with col2:
            safety_stock = st.number_input("SAFETY STOCK (UNITS)", min_value=0, value=20)
        with col3:
            lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # --- Metrics Dashboard ---
    st.subheader("📊 Sales Performance Metrics")
    m1, m2, m3, m4 = st.columns(4)
    
    # Historical Daily
    m1.markdown(f"""
    <div class="metric-box">
        <h3>Historical Daily Average</h3>
        <h2>{results['hist_avg']} units</h2>
        <div class="variation">± {results['hist_std']} units variation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Historical Monthly
    m2.markdown(f"""
    <div class="metric-box">
        <h3>Historical Monthly Average</h3>
        <h2>{round(results['hist_avg'] * 30)} units</h2>
        <div class="variation">± {round(results['hist_std'] * 30)} units variation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Projected Daily
    m3.markdown(f"""
    <div class="metric-box">
        <h3>Projected Daily Average</h3>
        <h2>{results['forecast_avg']} units</h2>
        <div class="variation">± {results['forecast_std']} units expected</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Projected Monthly
    m4.markdown(f"""
    <div class="metric-box">
        <h3>Projected Monthly Average</h3>
        <h2>{round(results['forecast_avg'] * 30)} units</h2>
        <div class="variation">± {round(results['forecast_std'] * 30)} units expected</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Forecast Visualization ---
    st.plotly_chart(
        create_forecast_chart(product_df, results['forecast']),
        use_container_width=True
    )
    
    # --- Inventory Alerts ---
    st.subheader("🛒 Inventory Status")
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
