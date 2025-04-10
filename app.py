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
    
    /* Completely hide uploader widget text */
    [data-testid="stFileUploader"] div:first-child {
        visibility: hidden;
        height: 0;
        padding: 0 !important;
    }
    
    /* Custom upload zone */
    .upload-zone {
        border: 2px dashed #6F36FF;
        border-radius: 15px;
        padding: 5rem;
        margin: 2rem auto;
        width: 70%;
        background: #FAFAFA;
        text-align: center;
        position: relative;
    }
    
    /* Our visible prompt text */
    .upload-prompt {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #888;
        pointer-events: none;
    }
    
    /* Small BlueSky logo */
    .bluesky-logo {
        text-align: center;
        margin-top: 3rem;
    }
    .bluesky-logo img {
        width: 24px;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# --- BlueSky Logo ---
bluesky_logo = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0085FF">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
</svg>
"""

# --- App Content ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)

# File uploader (will be hidden but clickable)
uploaded_file = st.file_uploader(
    "Upload your inventory file",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# Visible upload zone
st.markdown("""
<div class="upload-zone">
    <div class="upload-prompt">Click anywhere to upload file</div>
</div>
""", unsafe_allow_html=True)

# BlueSky logo
st.markdown(
    f'<div class="bluesky-logo"><a href="https://bsky.app" target="_blank">{bluesky_logo}</a></div>',
    unsafe_allow_html=True
)

# [Your existing analysis code]
if uploaded_file:
    st.success("File uploaded successfully!")
