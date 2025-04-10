import streamlit as st

# Set page config
st.set_page_config(
    page_title="Ventory",
    page_icon="📊",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    /* Main content */
    .header {
        font-size: 5rem;
        font-weight: 800;
        color: #6F36FF;
        text-align: center;
        margin: 1rem 0 0 0;
    }
    
    .subheader {
        font-size: 1rem;
        text-align: center;
        color: #666666;
        margin-bottom: 3rem;
    }
    
    /* Upload button */
    [data-testid="stFileUploader"] {
        width: 200px;
        margin: 0 auto;
    }
    
    [data-testid="stFileUploader"] div:first-child {
        background: #6F36FF;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    /* Twitter/X logo */
    .twitter-logo {
        text-align: center;
        margin-top: 3rem;
    }
    
    .twitter-logo svg {
        width: 24px;
        height: 24px;
        fill: #000000;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# Twitter/X Logo SVG
twitter_logo = """
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
</svg>
"""

# App Content
st.markdown('<div class="header">Ventory</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your sales and inventory manager</div>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "Upload spreadsheet",
    type=["csv", "xlsx"],
    label_visibility="visible"
)

# Twitter logo footer
st.markdown(
    f'<div class="twitter-logo"><a href="https://twitter.com" target="_blank">{twitter_logo}</a></div>',
    unsafe_allow_html=True
)

# File processing
if uploaded_file:
    st.success("File uploaded successfully!")
    # Add your analysis code here
