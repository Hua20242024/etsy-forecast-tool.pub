# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="Ventory.io - Inventory Insights",
    layout="centered",
    page_icon="📊"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Original color scheme */
    :root {
        --primary: #6F36FF;
        --secondary: #FF7E33;
    }
    
    /* Uploader styling */
    [data-testid="stFileUploader"] {
        border: 2px dashed #E0E0E0;
        border-radius: 15px;
        padding: 3rem;
        background: #FAFAFA;
        width: 80%;
        margin: 0 auto;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #6F36FF;
    }
    
    /* Hide uploader label */
    [data-testid="stFileUploader"] label {
        display: none;
    }
    
    /* Placeholder text */
    .upload-container::before {
        content: "Upload your inventory file";
        color: #888;
        font-size: 1.1rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
</style>
""", unsafe_allow_html=True)

# --- Minimalist Upload Interface ---
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #6F36FF; font-size: 2.5rem;">Ventory.io</h1>
    <p style="color: #666;">Instant inventory analysis</p>
</div>
""", unsafe_allow_html=True)

# --- Centered Search/Upload Bar ---
st.markdown('<div class="upload-container"></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    " ",
    type=["csv", "xlsx"],
    label_visibility="collapsed",
    help="Supports CSV and Excel files"
)

# --- Your Existing Analysis Logic ---
if uploaded_file:
    st.success("File uploaded! Analyzing...")
    # Your original dashboard code here
