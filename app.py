import streamlit as st
import pandas as pd
from etsy_forecast import run_forecast  # Importing the forecasting logic

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

# --- File Upload Section ---
uploaded_file = st.file_uploader("📤 Upload Your Sales Data (CSV)", type=["csv"])

if uploaded_file:
    try:
        # Load the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Renaming columns as expected by the forecasting logic
        df = df.rename(columns={'Date': 'date', 'Units Sold': 'units_sold', 'Product Type': 'product'})
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Display a preview of the data (kept as is for visual consistency)
        st.subheader("📈 Data Preview")
        st.write(df.head())

        # --- Tile Heatmap Section ---
        st.subheader("🧱 Sales Volume Heatmap")
        # The original heatmap function would go here to show the sales data as a heatmap
        # For example, create_tile_heatmap(df) would work here to display the heatmap
        # Example placeholder: st.plotly_chart(heatmap_fig, use_container_width=True)

        # --- Product Selection ---
        product = st.selectbox("SELECT PRODUCT FOR DETAILED ANALYSIS", df['product'].unique())

        # Filter data for selected product
        product_df = df[df['product'] == product]

        # --- Inventory Settings ---
        with st.expander("⚙️ Inventory Settings", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                current_stock = st.number_input("Current Stock (Units)", min_value=0, value=100)
            with col2:
                safety_stock = st.number_input("Safety Stock (Units)", min_value=0, value=50)
            with col3:
                lead_time = st.number_input("Lead Time (Days)", min_value=1, value=7)

        # --- Run Forecast ---
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

    except Exception as e:
        st.error(f"Error processing the file: {e}")

else:
    st.info("ℹ️ Please upload a CSV file with columns: Date, Units Sold, Product Type")
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
