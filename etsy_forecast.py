import streamlit as st
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

# --- App Setup ---
st.set_page_config(page_title="📦 Inventory Optimizer", layout="wide")
st.title("📦 Smart Inventory Management System")

# --- Data Input ---
uploaded_file = st.file_uploader("Upload sales CSV (date, units_sold, product)", type=["csv"])

# --- Sample Data Generator ---
def generate_sample_data():
    products = ["Lavender Oil", "Peppermint Oil", "Tea Tree Oil"]
    dates = pd.date_range(end=datetime.today(), periods=30)
    data = []
    
    for product in products:
        base = 5 + hash(product) % 15  # Unique base demand
        for i, date in enumerate(dates):
            # Weekly pattern + random fluctuation
            units = base + (i % 7) + int(np.random.normal(0, 2))
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "units_sold": max(1, units),
                "product": product
            })
    return pd.DataFrame(data)

# --- Data Processing ---
df = pd.read_csv(uploaded_file) if uploaded_file else generate_sample_data()

# --- Data Validation ---
try:
    df['date'] = pd.to_datetime(df['date'])
    required_cols = {'date', 'units_sold', 'product'}
    assert required_cols.issubset(df.columns)
except:
    st.error("❌ Invalid data format. Need columns: date, units_sold, product")
    st.stop()

# --- Inventory Settings ---
st.sidebar.header("Inventory Parameters")
lead_time = st.sidebar.slider("Lead time (days)", 1, 30, 7)
safety_stock = st.sidebar.slider("Safety stock (%)", 0, 50, 20)
reorder_frequency = st.sidebar.selectbox("Reorder frequency", ["Weekly", "Bi-weekly", "Monthly"])

# --- Forecasting & Reorder Logic ---
products = sorted(df['product'].unique())
selected_products = st.multiselect("Select products", products, default=products)

for product in selected_products:
    st.subheader(f"🧴 {product}")
    product_df = df[df['product'] == product].copy()
    
    # Train Prophet model
    model = Prophet(weekly_seasonality=True, daily_seasonality=False)
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    
    # Forecast
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    # Calculate reorder point
    avg_daily_demand = forecast['yhat'].mean()
    std_demand = forecast['yhat'].std()
    
    reorder_point = (avg_daily_demand * lead_time) * (1 + safety_stock/100)
    optimal_order_qty = max(avg_daily_demand * 14, 10)  # At least 2 weeks supply
    
    # Display
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(forecast.set_index('ds')['yhat'])
        
    with col2:
        current_stock = st.number_input(
            f"Current {product} inventory", 
            min_value=0, 
            value=int(reorder_point * 1.5),
            key=f"stock_{product}"
        )
        
        days_remaining = current_stock / avg_daily_demand if avg_daily_demand > 0 else 0
        
        st.metric("Avg Daily Demand", f"{avg_daily_demand:.1f} units")
        st.metric("Reorder Point", f"{int(reorder_point)} units")
        st.metric("Projected Stockout", f"{int(days_remaining)} days remaining")
        
        if current_stock <= reorder_point:
            st.error(f"""
            🚨 TIME TO REORDER!
            - Suggested quantity: {int(optimal_order_qty)} units
            - Expected delivery date: {(datetime.now() + timedelta(days=lead_time)).strftime('%b %d')}
            """)
        else:
            st.success(f"""
            ✅ Inventory sufficient
            - Next reorder in ~{int(days_remaining - lead_time)} days
            """)

# --- CSV Export ---
st.sidebar.download_button(
    "Download Sample CSV",
    generate_sample_data().to_csv(index=False),
    "sample_inventory_data.csv"
)
