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
    /* Giant title */
    .main-title {
        font-size: 7.5rem;
        text-align: center;
        color: #6F36FF;
        font-weight: 800;
        margin: 1rem 0 0 0;
    }
    
    /* Visible upload button */
    .upload-btn {
        background: #6F36FF;
        color: white !important;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        border-radius: 8px;
        margin: 2rem auto;
        display: block;
        cursor: pointer;
        transition: all 0.2s;
    }
    .upload-btn:hover {
        background: #5C2ECC;
        transform: scale(1.02);
    }
    
    /* Twitter/X logo at bottom */
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
        fill: #000000;
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

# Visible upload button
uploaded_file = st.file_uploader(
    "Upload inventory file",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# Custom styled button (triggers the hidden uploader)
st.markdown(
    '<div class="upload-btn">Upload Spreadsheet</div>',
    unsafe_allow_html=True
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
