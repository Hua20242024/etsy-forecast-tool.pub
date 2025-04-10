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
    
    /* Full-page invisible uploader */
    [data-testid="stFileUploader"] {
        opacity: 0;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: pointer;
        z-index: 9999;
    }
    
    /* Butterfly logo styling */
    .bluesky-logo {
        text-align: center;
        margin-top: 3rem;
    }
    .bluesky-butterfly {
        width: 32px;
        height: 32px;
    }
</style>
""", unsafe_allow_html=True)

# --- BlueSky Butterfly Logo ---
butterfly_logo = """
<svg class="bluesky-butterfly" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path fill="#0085FF" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15v-4H7v-2h3V7h2v4h3v2h-3v4h-2z"/>
  <path fill="#0085FF" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
</svg>
"""

# --- App Content ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)

# Invisible full-page uploader (MUST come before logo)
uploaded_file = st.file_uploader(
    "Upload your inventory file",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# BlueSky butterfly logo at bottom
st.markdown(
    f'<div class="bluesky-logo"><a href="https://bsky.app" target="_blank">{butterfly_logo}</a></div>',
    unsafe_allow_html=True
)

# [Your analysis code here]
if uploaded_file:
    st.success("File uploaded successfully!")
