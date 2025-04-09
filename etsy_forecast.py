import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- App Setup ---
st.set_page_config(page_title="📊 Etsy Inventory Pro", layout="wide", page_icon="📊")
st.title("📊 Smart Inventory Manager")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
        sales_col = next((col for col in df.columns if any(x in col.lower() for x in ['units', 'sales', 'qty']), 'units_sold')
        product_col = next((col for col in df.columns if 'product' in col.lower()), 'product')
        
        df = df.rename(columns={
            date_col: 'date',
            sales_col: 'units_sold',
            product_col: 'product'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# --- Forecasting & Inventory Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    train_df = product_df.rename(columns={'date':'ds', 'units_sold':'y'})[['ds','y']]
    
    model = Prophet(
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    model.fit(train_df)
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    avg_daily = forecast['yhat'].mean()
    avg_monthly = avg_daily * 30
    weekly_seasonality = (forecast['weekly'].max() - forecast['weekly'].min()) * 100
    
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = (current_stock - reorder_point) / avg_daily if avg_daily > 0 else 0
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'avg_monthly': round(avg_monthly),
        'weekly_seasonality': round(weekly_seasonality),
        'reorder_point': round(reorder_point),
        'days_remaining': max(0, round(days_remaining)),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/avg_daily)).strftime('%b %d') if avg_daily > 0 else "N/A"
    }

# --- Plotly Visualization ---
def create_plotly_chart(product_df, forecast):
    fig = go.Figure()
    
    # Actual sales
    fig.add_trace(go.Scatter(
        x=product_df['date'],
        y=product_df['units_sold'],
        mode='markers+lines',
        name='Actual Sales',
        marker=dict(color='#636EFA', size=8),
        line=dict(color='#636EFA', width=1, dash='dot'),
        hovertemplate='<b>%{x|%b %d}</b><br>%{y} units'
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#FF7F0E', width=2),
        hovertemplate='<b>%{x|%b %d}</b><br>%{y:.1f} units'
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(255, 127, 14, 0.2)',
        name='Confidence',
        hovertemplate='<b>%{x|%b %d}</b><br>Range: %{y:.1f} units'
    ))
    
    # Today's line
    fig.add_vline(
        x=datetime.now().timestamp() * 1000,
        line_dash="dash",
        line_color="gray",
        annotation_text="Today",
        annotation_position="top right"
    )
    
    # Layout
    fig.update_layout(
        title='6-Month Sales Forecast',
        xaxis_title='Date',
        yaxis_title='Units Sold',
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV (date, units_sold, product)", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Product selection
    product = st.selectbox("Select product", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory controls
    col1, col2, col3 = st.columns(3)
    with col1:
        current_stock = st.number_input("Current inventory (units)", min_value=0, value=50)
    with col2:
        safety_stock = st.number_input("Safety stock (units)", min_value=0, value=10)
    with col3:
        lead_time = st.number_input("Lead time (days)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # --- Dashboard ---
    st.subheader("📊 Inventory Dashboard")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Daily", f"{results['avg_daily']} units", 
             help="Average units sold per day")
    m2.metric("Avg Monthly", f"{results['avg_monthly']} units",
             help="Projected monthly sales")
    m3.metric("Weekly Fluctuation", f"±{results['weekly_seasonality']}%",
             help="Typical week-to-week variation")
    
    st.markdown("---")
    
    # Plotly chart
    st.plotly_chart(
        create_plotly_chart(product_df, results['forecast']), 
        use_container_width=True
    )
    
    # Alerts
    if current_stock <= results['reorder_point']:
        st.error(f"""
        🚨 **URGENT REORDER NEEDED**  
        - Suggested quantity: {results['order_qty']} units  
        - Stockout in: ~{results['days_remaining']} days  
        - Projected stockout date: {results['stockout_date']}
        """)
    else:
        st.success(f"""
        ✅ **Inventory Healthy**  
        - Reorder point: {results['reorder_point']} units  
        - Current stock lasts: {results['days_remaining'] + lead_time} days  
        - Suggested order date: {(datetime.now() + timedelta(days=results['days_remaining'])).strftime('%b %d')}
        """)

else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
    st.download_button(
        "📥 Download sample CSV",
        pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=30).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 30),
            'product': "Example Product"
        }).to_csv(index=False),
        "sample_sales_data.csv"
    )
