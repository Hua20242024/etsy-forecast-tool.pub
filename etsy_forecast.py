import streamlit as st
import pandas as pd
from prophet import Prophet
import io

# --- App Setup ---
st.set_page_config(layout="wide")
st.title("🛍️ Universal Product Restocking System")

# --- Data Upload ---
uploaded_file = st.file_uploader(
    "Upload your sales CSV (required columns: date, units_sold, product)", 
    type="csv"
)

# --- Dynamic Demo Data ---
if uploaded_file is None:
    st.info("💡 Using demo data. Upload your CSV for real analysis")
    
    # Let users customize demo products
    custom_products = st.text_input(
        "Enter demo products (comma separated)", 
        "Organic Argan Oil, Lavender Oil, Peppermint Oil"
    ).split(",")
    
    # Generate data for any user-specified products
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
    demo_data = []
    
    for product in custom_products:
        product = product.strip()
        if not product: continue
        
        # Unique sales pattern per product
        base = abs(hash(product)) % 15 + 5  # Random base between 5-20
        sales = [base + (i%7)*2 for i in range(len(dates))]  # Weekly pattern
        
        demo_data.append(pd.DataFrame({
            "date": dates,
            "units_sold": sales,
            "product": product
        }))
    
    df = pd.concat(demo_data) if demo_data else pd.DataFrame()
    st.success(f"Generated demo data for: {', '.join([p.strip() for p in custom_products if p.strip()])}")

else:
    df = pd.read_csv(uploaded_file)

# --- Data Validation ---
if not df.empty:
    required_cols = {"date", "units_sold", "product"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        st.error(f"❌ Missing columns: {', '.join(missing)}")
        st.stop()
    
    try:
        df["date"] = pd.to_datetime(df["date"])
        if df["date"].isnull().any():
            st.error("❌ Invalid date format. Use YYYY-MM-DD")
            st.stop()
            
        if df["product"].isnull().any():
            st.error("❌ Product names cannot be empty")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Data processing error: {str(e)}")
        st.stop()

# --- Product Selection ---
if not df.empty:
    all_products = sorted(df["product"].unique())
    selected_products = st.multiselect(
        "Select products to analyze",
        all_products,
        default=all_products[:min(3, len(all_products))]
    )
    
    # --- Forecasting ---
    for product in selected_products:
        st.subheader(f"📊 {product}")
        product_df = df[df["product"] == product].copy()
        
        with st.expander("View Raw Data"):
            st.dataframe(product_df)
        
        # Auto-configure Prophet
        model = Prophet(
            weekly_seasonality=True,
            yearly_seasonity=len(product_df) > 180,
            changepoint_prior_scale=0.05
        )
        
        try:
            model.fit(product_df.rename(columns={"date": "ds", "units_sold": "y"}))
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            col1, col2 = st.columns(2)
            with col1:
                st.line_chart(forecast.set_index("ds")["yhat"])
            with col2:
                st.metric("Avg Daily Demand", f"{forecast['yhat'].mean():.1f} units")
                st.download_button(
                    label="Download Forecast",
                    data=forecast.to_csv().encode(),
                    file_name=f"{product}_forecast.csv"
                )
                
        except Exception as e:
            st.error(f"Forecast failed for {product}: {str(e)}")
