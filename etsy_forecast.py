import streamlit as st
import pandas as pd
import numpy as np  # <-- Missing import added
from prophet import Prophet
from datetime import datetime, timedelta

# --- App Setup ---
st.set_page_config(page_title="📦 Inventory Optimizer", layout="wide")
st.title("📦 Smart Inventory Management System")

# --- Sample Data Generator ---
def generate_sample_data():
    products = ["Lavender Oil", "Peppermint Oil", "Tea Tree Oil"]
    dates = pd.date_range(end=datetime.today(), periods=30)
    data = []
    
    for product in products:
        base = 5 + hash(product) % 15  # Unique base demand
        for i, date in enumerate(dates):
            # Weekly pattern + random fluctuation
            units = base + (i % 7) + int(np.random.normal(0, 2))  # Now works with np imported
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "units_sold": max(1, units),
                "product": product
            })
    return pd.DataFrame(data)

# --- Data Input ---
uploaded_file = st.file_uploader("Upload sales CSV (date, units_sold, product)", type=["csv"])

# --- Data Processing ---
try:
    df = pd.read_csv(uploaded_file) if uploaded_file else generate_sample_data()
except Exception as e:
    st.error(f"❌ Data loading error: {str(e)}")
    st.stop()

# --- Data Validation ---
try:
    df['date'] = pd.to_datetime(df['date'])
    required_cols = {'date', 'units_sold', 'product'}
    assert required_cols.issubset(df.columns)
    assert not df[['date', 'units_sold']].isnull().any().any()
except Exception as e:
    st.error("❌ Invalid data. Required columns: date, units_sold, product")
    st.stop()

# --- Inventory Settings ---
st.sidebar.header("🛠️ Inventory Parameters")
lead_time = st.sidebar.slider("Lead time (days)", 1, 30, 7)
safety_stock = st.sidebar.slider("Safety stock (%)", 0, 50, 20)
current_stocks = {}

# --- Forecasting & Reorder Logic ---
products = sorted(df['product'].unique())
selected_products = st.multiselect("Select products", products, default=products)

for product in selected_products:
    st.subheader(f"🧴 {product}")
    product_df = df[df['product'] == product].copy()
    
    # Train model
    try:
        model = Prophet(weekly_seasonality=True)
        model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Calculate metrics
        avg_demand = forecast['yhat'].mean()
        std_demand = forecast['yhat'].std()
        reorder_point = (avg_demand * lead_time) * (1 + safety_stock/100)
        optimal_qty = max(avg_demand * 14, 10)  # 2-week supply minimum
        
        # Display
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(forecast.set_index('ds')['yhat'])
            
        with col2:
            current_stock = st.number_input(
                f"Current {product} stock", 
                min_value=0, 
                value=int(reorder_point * 1.5),
                key=f"stock_{product}"
            )
            
            days_remaining = current_stock / avg_demand if avg_demand > 0 else 0
            
            st.metric("Average Demand", f"{avg_demand:.1f} ± {std_demand:.1f} units/day")
            st.metric("Reorder Trigger", f"{int(reorder_point)} units")
            
            if current_stock <= reorder_point:
                st.error(f"""
                🚨 URGENT: Reorder {optimal_qty} units
                **Stockout in:** {max(0, int(days_remaining))} days
                **Delivery by:** {(datetime.now() + timedelta(days=lead_time)).strftime('%b %d')}
                """)
            else:
                st.success(f"""
                ✅ OK for {int(days_remaining - lead_time)} more days
                **Next reorder:** ~{(datetime.now() + timedelta(days=days_remaining - lead_time)).strftime('%b %d')}
                """)
                
    except Exception as e:
        st.error(f"⚠️ Failed to forecast {product}: {str(e)}")

# --- Data Export ---
st.sidebar.download_button(
    "Download Sample CSV",
    generate_sample_data().to_csv(index=False),
    "inventory_sample.csv",
    help="Template with correct formatting"
)
