# MUST BE FIRST COMMAND
import streamlit as st
from PIL import Image  # For logo handling
import io

st.set_page_config(
    page_title="Ventory - Inventory Intelligence",
    layout="centered",
    page_icon="📊"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Big centered title */
    .main-title {
        font-size: 4.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #0077B6 0%, #00B4D8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    
    /* Logo positioning */
    .logo-container {
        position: absolute;
        top: 20px;
        right: 20px;
    }
    
    /* Uploader styling */
    [data-testid="stFileUploader"] {
        width: 80%;
        margin: 0 auto;
        border: 2px dashed #B0E0E6;
        border-radius: 15px;
        padding: 3rem;
        background: #F8FDFF;
    }
    
    /* Hide uploader label */
    [data-testid="stFileUploader"] label {
        visibility: hidden;
    }
    
    /* Placeholder text */
    .upload-placeholder::before {
        content: "Click or drag your inventory file here";
        color: #7FB3D5;
        font-size: 1.1rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
</style>
""", unsafe_allow_html=True)

# --- Logo Setup ---
def load_logo():
    # Create a simple blue sky logo (replace with your actual logo later)
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (100, 100), color=(255,255,255))
    d = ImageDraw.Draw(img)
    d.ellipse((10, 10, 90, 90), fill=(173, 216, 230))  # Light blue circle
    d.ellipse((30, 30, 70, 70), fill=(135, 206, 250))  # Sky blue center
    return img

logo = load_logo()

# --- Landing Page ---
col1, col2 = st.columns([4,1])
with col1:
    st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)
    st.caption('<div style="text-align: center; font-size: 1.2rem;">AI-powered inventory insights</div>', 
               unsafe_allow_html=True)
    
with col2:
    st.image(logo, width=80)

# --- Centered Uploader ---
st.markdown('<div class="upload-placeholder"></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    " ",
    type=["csv", "xlsx"],
    label_visibility="collapsed",
    help="Supports Etsy, Shopify, and Excel exports"
)

# --- App Logic (Add your analysis code here) ---
if uploaded_file:
    st.success("File uploaded successfully!")
    # Your analysis code would go here
    # Example:
    # df = pd.read_csv(uploaded_file)
    # show_dashboard(df)
