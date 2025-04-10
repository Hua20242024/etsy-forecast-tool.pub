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
    /* Giant title (now clickable) */
    .main-title {
        font-size: 7.5rem;
        text-align: center;
        color: #6F36FF;
        font-weight: 800;
        margin: 1rem 0 0 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .main-title:hover {
        opacity: 0.9;
        transform: scale(1.01);
    }
    
    /* Completely hidden uploader */
    [data-testid="stFileUploader"] {
        display: none !important;
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
    
    /* Subtle upload hint */
    .upload-hint {
        text-align: center;
        color: #666;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Twitter/X Logo ---
twitter_logo = """
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
</svg>
"""

# --- Hidden File Uploader ---
uploaded_file = st.file_uploader(
    "Upload inventory file",
    type=["csv", "xlsx"],
    label_visibility="collapsed",
    key="hidden_uploader"
)

# --- App Content ---
st.markdown(
    '<div class="main-title" onclick="document.getElementById(\'hidden_uploader\').click()">Ventory</div>', 
    unsafe_allow_html=True
)

# Subtle hint (disappears after upload)
if not uploaded_file:
    st.markdown(
        '<div class="upload-hint">click title to upload</div>',
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
