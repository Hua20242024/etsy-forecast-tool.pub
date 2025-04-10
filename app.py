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
        margin: 1rem 0;
    }
    
    /* Hidden uploader */
    [data-testid="stFileUploader"] {
        opacity: 0;
        position: absolute;
        width: 100%;
        height: 200px;
        top: 50%;
        left: 0;
        cursor: pointer;
    }
    
    /* Visible click area */
    .upload-zone {
        border: 2px dashed #6F36FF;
        border-radius: 15px;
        padding: 5rem;
        margin: 2rem auto;
        width: 70%;
        background: #FAFAFA;
        text-align: center;
        color: #888;
    }
    
    /* BlueSky logo container */
    .bluesky-logo {
        text-align: center;
        margin-top: 3rem;
    }
    
    /* Logo image styling */
    .bluesky-logo img {
        width: 40px;
        opacity: 0.8;
        transition: all 0.2s;
    }
    
    .bluesky-logo img:hover {
        opacity: 1;
        transform: scale(1.1);
    }
</style>
""", unsafe_allow_html=True)

# --- BlueSky Logo (Base64 encoded) ---
bluesky_logo = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0085FF">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
</svg>
"""

# --- App Content ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)

# Hidden uploader
uploaded_file = st.file_uploader(
    " ",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# Visible click prompt
st.markdown(
    '<div class="upload-zone">Click anywhere to upload file</div>', 
    unsafe_allow_html=True
)

# BlueSky logo link (centered bottom)
st.markdown(
    f"""
    <div class="bluesky-logo">
        <a href="https://bsky.app" target="_blank">
            {bluesky_logo}
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# [Your existing analysis code]
if uploaded_file:
    st.success("File uploaded!")
