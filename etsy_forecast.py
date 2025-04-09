import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.utilities import regressor_coefficients

st.title("📦 Etsy Restock Pro: AI-Powered Inventory Alerts")

# --- 1. Data Upload with Validation ---
uploaded_file = st.file_uploader("Upload your Etsy sales CSV (required columns: 'date', 'units_sold')")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_cols = {'date', 'units_sold'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            st.error(f"❌ Missing required columns: {', '.join(missing)}")
            st.stop()
            
        # Prepare DataFrame
        df = df.rename(columns={'date': 'ds', 'units_sold': 'y'})
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
        
        # Check for invalid dates
        if df['ds'].isnull().any():
            st.error("❌ Invalid date format detected. Please use YYYY-MM-DD format.")
            st.stop()
            
        # Remove zeros if needed (comment out if zeros are valid)
        df = df[df['y'] > 0]
        
        # Check minimum data requirements
        if len(df) < 7:
            st.error("⚠️ Need at least 7 days of data for forecasting")
            st.stop()

        # --- 2. Model Configuration ---
        with st.spinner("🔮 Generating smart forecast..."):
            days_of_data = (df['ds'].max() - df['ds'].min()).days
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=days_of_data >= 14,
                yearly_seasonality=days_of_data >= 365,
                changepoint_prior_scale=0.05 if days_of_data < 60 else 0.2,
                seasonality_mode='additive'
            )
            
            # Fit model with progress
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=90)
            forecast = model.predict(future)

        # --- 3. Display Results ---
        tab1, tab2 = st.tabs(["📊 Forecast", "📦 Inventory Plan"])
        
        with tab1:
            fig = model.plot(forecast)
            st.pyplot(fig)
            
            # Show trend components
            st.subheader("Trend Analysis")
            fig2 = model.plot_components(forecast)
            st.pyplot(fig2)
        
        with tab2:
            # Inventory configuration
            col1, col2 = st.columns(2)
            with col1:
                lead_time = st.slider("Supplier lead time (days)", 1, 30, 7)
            with col2:
                safety_stock = st.slider("Safety stock buffer", 0, 100, 20)
                
            current_stock = st.number_input("Current inventory level", min_value=0, value=100)
            
            # Calculate reorder point
            avg_daily_sales = forecast['yhat'].mean()
            reorder_point = int(avg_daily_sales * lead_time) + safety_stock
            
            # Inventory status
            inventory_ratio = min(1.0, current_stock / reorder_point)
            st.progress(inventory_ratio)
            
            if current_stock <= reorder_point:
                st.error(f"""
                🚨 Time to Reorder!
                - Projected stockout in: {lead_time} days
                - Suggested order quantity: {int(reorder_point * 1.5)} units
                """)
            else:
                days_remaining = int((current_stock - reorder_point) / avg_daily_sales)
                st.success(f"""
                ✅ Inventory Healthy
                - Reorder when stock reaches: {reorder_point} units
                - Approx. {days_remaining} days until reorder needed
                """)
                
    except Exception as e:
        st.error(f"""
        ❌ Error in processing your data:
        {str(e)}
        
        Please check:
        1. Date format (YYYY-MM-DD)
        2. No missing values
        3. At least 7 days of data
        """)
        st.stop()

else:
    # Demo section when no file uploaded
    st.markdown("""
    ## How to Use:
    1. Export your Etsy sales data as CSV
    2. Ensure columns are named: `date` and `units_sold`
    3. Upload to generate forecasts
    
    Sample CSV format:
    ```
    date,units_sold
    2024-01-01,5
    2024-01-02,3
    2024-01-03,7
    ```
    """)
