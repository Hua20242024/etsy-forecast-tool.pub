import streamlit as st
import pandas as pd
import etsy_forecast as ef
import plotly.express as px
import plotly.graph_objects as go

# Set page title
st.set_page_config(page_title="📊 Etsy Inventory Pro", layout="wide", page_icon="📊")

# Custom CSS to style the page
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

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Rename columns for consistency
    df.rename(columns={'Date': 'date', 'Units Sold': 'units_sold', 'Product Type': 'product'}, inplace=True)
    
    # Show the first few rows of the uploaded data
    st.write(df.head())

    # --- Tile Heatmap Section ---
    st.subheader("🧱 Sales Volume Heatmap")
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <small>Tile size and color represent sales volume (larger/green = better sales)</small>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Display the heatmap
    st.plotly_chart(fig, use_container_width=True)

    # --- Inventory Settings ---
    st.sidebar.header("⚙️ Inventory Settings")
    current_stock = st.sidebar.number_input("Current Stock (Units)", min_value=0, value=500)
    safety_stock = st.sidebar.number_input("Safety Stock (Units)", min_value=0, value=20)
    lead_time = st.sidebar.number_input("Lead Time (Days)", min_value=1, value=7)

    # --- Product Selection ---
    product = st.selectbox("SELECT PRODUCT FOR DETAILED ANALYSIS", df['product'].unique())
    product_df = df[df['product'] == product]

    # --- Forecasting Logic ---
    try:
        results = ef.run_forecast(product_df, current_stock, safety_stock, lead_time)
        st.success("Forecasting complete!")
        
        # Display results (you can adjust this based on what data you want to show)
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
            ef.create_forecast_chart(product_df, results['forecast']),
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
        st.error(f"❌ Error while running forecast: {str(e)}")

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
