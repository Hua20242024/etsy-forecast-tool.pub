# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="Ventory",
    layout="centered",
    page_icon="📊"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Giant centered title */
    .main-title {
        font-size: 7.5rem !important;  /* 3x bigger (original was ~2.5rem) */
        text-align: center;
        margin: 1rem 0;
        color: #6F36FF;
        font-weight: 800;
        letter-spacing: -2px;
        line-height: 1;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Clean upload box */
    [data-testid="stFileUploader"] {
        border: 2px dashed #6F36FF;
        border-radius: 15px;
        padding: 4rem;
        margin: 0 auto;
        width: 70%;
        background: #FAFAFA;
    }
    
    /* Hide all uploader text */
    [data-testid="stFileUploader"] section div span {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Minimal Interface ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Instant inventory analysis</div>', unsafe_allow_html=True)

# --- Invisible Uploader ---
uploaded_file = st.file_uploader(
    " ",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# [Your existing analysis code below]
if uploaded_file:
    st.success("File uploaded successfully!")
