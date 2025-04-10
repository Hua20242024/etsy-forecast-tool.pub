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
    /* Main container */
    .stApp {
        background-color: #000000;
        color: white;
    }
    
    /* Giant title */
    .main-title {
        font-size: 7.5rem;
        text-align: center;
        color: #6F36FF;
        font-weight: 800;
        margin: 1rem 0 0 0;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: white;
        font-size: 1rem;
        margin-bottom: 3rem;
        opacity: 0.8;
    }
    
    /* Upload button styling */
    [data-testid="stFileUploader"] {
        width: 200px;
        margin: 0 auto;
    }
    [data-testid="stFileUploader"] div:first-child {
        background: #6F36FF;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    /* White Twitter logo */
    .twitter-logo {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        text-align: center;
    }
    .twitter-logo svg {
        width: 24px;
        height: 24px;
        fill: white;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# --- Twitter/X Logo ---
twitter_logo = """
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
</svg>
"""

# --- App Content ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your sales and inventory manager</div>', unsafe_allow_html=True)

# Standard file uploader
uploaded_file = st.file_uploader(
    "Upload spreadsheet",
    type=["csv", "xlsx"],
    label_visibility="visible"
)

# Twitter logo at bottom
st.markdown(
    f'<div class="twitter-logo"><a href="https://twitter.com" target="_blank">{twitter_logo}</a></div>',
    unsafe_allow_html=True
)

# --- File Processing ---
if uploaded_file:
    st.success("File uploaded successfully!")
    # [Your existing analysis code here]
