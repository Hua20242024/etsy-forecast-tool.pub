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
</style>
""", unsafe_allow_html=True)

# --- App Content ---
st.markdown('<div class="main-title">Ventory</div>', unsafe_allow_html=True)

# Hidden uploader (invisible but clickable)
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

# [Your existing analysis code]
if uploaded_file:
    st.success("File uploaded!")
