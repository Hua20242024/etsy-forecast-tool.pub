import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.utilities import regressor_coefficients

# --- App Setup ---
st.set_page_config(page_title="Universal Product Forecaster", layout="wide")
st.title("🌐 Universal Product Demand Forecaster")

# --- Data Input ---
uploaded_file = st.file_uploader("Upload your sales CSV (columns: date, units_sold, product)", type=["csv"])

# --- Sample Data Generator ---
def generate_sample_data():
    base_date = pd.to_datetime("2024-01-01")
    products = ["Lavender Oil", "Peppermint Oil", "Tea Tree Oil"]
    data = []
    
    for day in range(30):
        date = base_date + pd.Timedelta(days=day)
        for product in products:
            base_sales = 5 + hash(product) % 10  # Unique base for each product
            sales = base_sales + (day % 7)  # Weekly pattern
            data.append({
                "date": date.date(),
                "units_sold": max(1, sales),  # Ensure no zero/negative sales
                "product": product
            })
    
    return pd.DataFrame(data)

# --- Data Processing ---
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File successfully uploaded!")
    except Exception as e:
        st.error(f"❌ Failed to read CSV: {str(e)}")
        st.stop()
else:
    df = generate_sample_data()
    st.info("ℹ️ Using sample data. Upload your CSV for real analysis")

# --- Data Validation ---
required_cols = {"date", "units_sold", "product"}
if not required_cols.issubset(df.columns):
    missing = required_cols - set(df.columns)
    st.error(f"❌ Missing required columns: {', '.join(missing)}")
    st.stop()

try:
    df["date"] = pd.to_datetime(df["date"])
    if df["date"].isnull().any():
        st.error("❌ Invalid date values detected")
        st.stop()
        
    df["units_sold"] = pd.to_numeric(df["units_sold"])
    if df["units_sold"].isnull().any():
        st.error("❌ Invalid sales values detected")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Data conversion error: {str(e)}")
    st.stop()

# --- Product Selection ---
products = sorted(df["product"].unique())
selected_products = st.multiselect(
    "Select products to forecast",
    products,
    default=products[:min(3, len(products))]
)

# --- Forecasting ---
for product in selected_products:
    st.subheader(f"📊 {product}")
    product_df = df[df["product"] == product].copy()
    
    with st.expander("View Raw Data"):
        st.dataframe(product_df)
    
    try:
        # Prepare Prophet data
        prophet_df = product_df.rename(columns={"date": "ds", "units_sold": "y"})
        prophet_df = prophet_df[["ds", "y"]].dropna()
        
        # Auto-configure model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=len(prophet_df) > 180,
            changepoint_prior_scale=0.05
        )
        
        # Train and predict
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(forecast.set_index("ds")[["yhat"]])
        with col2:
            st.metric("Average Daily Demand", f"{forecast['yhat'].mean():.1f} units")
            st.download_button(
                label="Download Forecast",
                data=forecast.to_csv().encode(),
                file_name=f"{product.replace(' ', '_')}_forecast.csv"
            )
            
    except Exception as e:
        st.error(f"⚠️ Forecast failed for {product}: {str(e)}")
        continue

# --- CSV Download ---
sample_csv = generate_sample_data().to_csv(index=False)
st.download_button(
    label="Download Sample CSV",
    data=sample_csv,
    file_name="sample_product_sales.csv",
    mime="text/csv"
)
