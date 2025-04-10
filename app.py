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
    
    /* Twitter/X logo styling */
    .twitter-logo {
        text-align: center;
        margin-top: 3rem;
    }
    .twitter-logo svg {
        width: 28px;
        height: 28px;
        fill: #000000;
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

# Invisible full-page uploader (MUST come before logo)
uploaded_file = st.file_uploader(
    "Upload your inventory file",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
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
    # Example:
    # df = pd.read_csv(uploaded_file)
    # st.dataframe(df.head())
else:
    st.markdown(
        '<div style="text-align: center; color: #666; margin-top: 1rem;">Click anywhere to upload file</div>',
        unsafe_allow_html=True
    )
