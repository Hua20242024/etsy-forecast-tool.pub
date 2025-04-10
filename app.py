import streamlit as st
from PIL import Image
import io

# Set page config
st.set_page_config(
    page_title="Ventory",
    layout="centered",
    page_icon="📊"
)

# Custom CSS to hide all uploader text
st.markdown("""
<style>
    /* Hide all uploader text */
    [data-testid="stFileUploader"] div:first-child div:first-child div:first-child {
        visibility: hidden;
        height: 0;
        padding: 0 !important;
    }
    
    /* Style the upload button */
    [data-testid="stFileUploader"] div:first-child {
        background: #6F36FF;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        width: fit-content;
        margin: 0 auto;
    }
    
    /* Main title */
    .main-title {
        font-size: 5rem;
        text-align: center;
        color: #6F36FF;
        font-weight: 800;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Twitter logo */
    .twitter-logo {
        text-align: center;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Create Twitter/X logo
def create_twitter_logo():
    img = Image.new('RGB', (100, 100), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # Draw Twitter X logo
    d.line((20, 20, 80, 80), fill=(29, 161, 242), width=8)
    d.line((80, 20, 20, 80), fill=(29, 161, 242), width=8)
    return img

# App content
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)

# File uploader with hidden text
uploaded_file = st.file_uploader(
    " ",  # Empty string for label
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

# Display Twitter logo
logo = create_twitter_logo()
st.image(logo, width=40, output_format='PNG', use_column_width=False, 
         caption='', clamp=False, channels='RGB', 
         output_format='auto')

# File processing
if uploaded_file:
    st.success("File uploaded!")
    # Your analysis code here
