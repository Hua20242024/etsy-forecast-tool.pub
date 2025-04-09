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
import plotly.graph_objects as go

# --- Streamlit Style Setup ---
st.markdown("""
<style>
    .metric-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
    }
    .stPlotlyChart {
        border: 1px solid #f0f2f6;
        border-radius: 8px;
        padding: 10px;
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
        title='Sales Forecast & Inventory Projection',
        xaxis_title='Date',
        yaxis_title='Units Sold',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig

# --- Forecasting Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    model = Prophet(weekly_seasonality=True, daily_seasonality=False)
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    avg_daily = forecast['yhat'].mean()
    avg_monthly = avg_daily * 30
    weekly_seasonality = (forecast['weekly'].max() - forecast['weekly'].min()) * 100
    
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = max(0, (current_stock - reorder_point) / avg_daily) if avg_daily > 0 else 0
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'avg_monthly': round(avg_monthly),
        'weekly_seasonality': round(weekly_seasonality),
        'reorder_point': round(reorder_point),
        'days_remaining': days_remaining,
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/avg_daily)).strftime('%b %d')
    }

# --- Main App ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    product = st.selectbox("SELECT PRODUCT", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory controls
    with st.expander("⚙️ INVENTORY SETTINGS", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            current_stock = st.number_input("CURRENT STOCK (UNITS)", min_value=0, value=50)
        with col2:
            safety_stock = st.number_input("SAFETY STOCK (UNITS)", min_value=0, value=10)
        with col3:
            lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # --- Metrics Dashboard ---
    st.subheader("📊 Key Metrics")
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"""
    <div class="metric-box">
        <h3>Avg Daily Sales</h3>
        <h2>{results['avg_daily']} units</h2>
    </div>
    """, unsafe_allow_html=True)
    
    m2.markdown(f"""
    <div class="metric-box">
        <h3>Avg Monthly Sales</h3>
        <h2>{results['avg_monthly']} units</h2>
    </div>
    """, unsafe_allow_html=True)
    
    m3.markdown(f"""
    <div class="metric-box">
        <h3>Weekly Fluctuation</h3>
        <h2>±{results['weekly_seasonality']}%</h2>
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
            'date': pd.date_range(end=datetime.today(), periods=30).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 30),
            'product': "Lavender Essential Oil"
        }).to_csv(index=False)
        st.download_button(
            label="⬇️ Download Now",
            data=sample_data,
            file_name="sample_sales_data.csv",
            mime="text/csv"
        )
