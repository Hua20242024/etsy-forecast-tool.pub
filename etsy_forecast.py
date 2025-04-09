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
import math

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
        background: transparent !important;
    }
    .floating-bubbles {
        background-color: transparent !important;
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

# --- Floating Bubbles Visualization ---
def create_floating_bubbles(df):
    # Get last month's sales
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    monthly_sales = df[df['date'].dt.strftime('%Y-%m') == last_month]
    
    if monthly_sales.empty:
        st.warning(f"No sales data for {last_month}")
        return None
    
    product_sales = monthly_sales.groupby('product')['units_sold'].sum().reset_index()
    n = len(product_sales)
    
    # Create initial positions in a circle
    radius = 40
    center_x, center_y = 50, 50
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    x_pos = center_x + radius * np.cos(angles)
    y_pos = center_y + radius * np.sin(angles)
    
    # Create figure
    fig = go.Figure()
    
    # Add bubbles with colored borders
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    for i in range(n):
        fig.add_trace(go.Scatter(
            x=[x_pos[i]],
            y=[y_pos[i]],
            mode='markers+text',
            marker=dict(
                size=product_sales['units_sold'].iloc[i]/product_sales['units_sold'].max()*50 + 30,
                color='rgba(0,0,0,0)',  # Transparent center
                line=dict(width=3, color=colors[i % len(colors)]),
                opacity=0.8
            ),
            text=product_sales['product'].iloc[i],
            textposition='middle center',
            hoverinfo='text',
            hovertext=f"{product_sales['product'].iloc[i]}<br>{last_month} Sales: {product_sales['units_sold'].iloc[i]} units",
            name=''
        ))
    
    # Animation settings - bubbles will float gently
    frames = []
    for t in range(0, 360, 5):
        # Slightly vary the radius and angle for organic movement
        varied_radius = radius * (0.95 + 0.1 * np.sin(math.radians(t)))
        frame_x = center_x + varied_radius * np.cos(angles + math.radians(t/3))
        frame_y = center_y + varied_radius * np.sin(angles + math.radians(t/4))
        
        frames.append(go.Frame(
            data=[go.Scatter(
                x=[frame_x[i]],
                y=[frame_y[i]],
                marker=dict(
                    size=product_sales['units_sold'].iloc[i]/product_sales['units_sold'].max()*50 + 30 * 
                        (0.9 + 0.2 * math.sin(math.radians(t + i*30)))  # Gentle pulsing
                )
            ) for i in range(n)],
            name=f"frame_{t}"
        ))
    
    fig.frames = frames
    
    # Layout without axes
    fig.update_layout(
        title=f"Product Sales - {last_month}",
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(visible=False, range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=0, r=0, t=60, b=0),
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [{
                "args": [None, {"frame": {"duration": 50, "redraw": True},
                              "fromcurrent": True,
                              "transition": {"duration": 0}}],
                "label": "",
                "method": "animate"
            }]
        }]
    )
    
    # Auto-start animation
    fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, buttons=[])])
    fig['layout']['updatemenus'][0]['buttons'].append(
        dict(method='animate',
             args=[None, dict(frame=dict(duration=50, redraw=True), 
                            fromcurrent=True, 
                            mode='immediate')],
             label=''))
    
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
    
    # --- Floating Bubbles Section ---
    st.subheader("🌍 Product Sales Visualization")
    with st.container():
        bubble_fig = create_floating_bubbles(df)
        if bubble_fig:
            st.plotly_chart(bubble_fig, use_container_width=True, config={'displayModeBar': False})
    
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
