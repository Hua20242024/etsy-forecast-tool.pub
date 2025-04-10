# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="Ventory.io - Instant Inventory Insights",
    layout="centered",
    page_icon="📊"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Modern minimalist style */
    [data-testid="stFileUploader"] {
        border: 2px dashed #E0E0E0;
        border-radius: 15px;
        padding: 3rem;
        background: #FAFAFA;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #8E8E8E;
    }
    /* Hide uploader after file selection */
    .upload-hidden div:first-child {
        display: none;
    }
    .logo {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #6C63FF 0%, #FF6584 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: -0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---
def analyze_data(df):
    """Your existing analysis code goes here"""
    st.success("✅ Analysis complete!")
    
    # Example metrics (replace with your actual analysis)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${df['sales'].sum():,.0f}")
    col2.metric("Avg. Daily", f"${df['sales'].mean():,.0f}")
    col3.metric("Top Product", df['product'].mode()[0])
    
    # Example chart
    st.line_chart(df.set_index('date')['sales'])

# --- Homepage or Analysis ---
if 'file_uploaded' not in st.session_state:
    # LANDING PAGE
    st.markdown('<div class="logo">Ventory.io</div>', unsafe_allow_html=True)
    st.caption("Instant inventory insights • No setup required")
    
    uploaded_file = st.file_uploader(
        " ",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
        help="Drag & drop your sales spreadsheet here"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)  # Add your actual data loading logic
            st.session_state.file_uploaded = True
            st.session_state.df = df
            st.rerun()  # Refresh to show analysis
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    st.markdown("---")
    st.caption("💡 Works with Etsy, Shopify, and Excel exports")
    
else:
    # ANALYSIS PAGE
    st.button("← Upload new file", on_click=lambda: st.session_state.clear())
    st.title("Your Inventory Insights")
    analyze_data(st.session_state.df)
