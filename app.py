import streamlit as st

# Set page title
st.set_page_config(page_title="Ventory", page_icon="🔍", layout="centered")

# Custom CSS to style the page
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f0;  /* Set a light gray background color */
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }

    .overlay {
        background: rgba(255, 255, 255, 0.8);  /* Opaque white overlay */
        height: 100vh;
        padding-top: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .header {
        font-size: 64px;
        font-weight: bold;
        color: #6a1b9a;  /* Purple color */
        text-align: center;
    }

    .subheader {
        font-size: 12px;
        text-align: center;
        color: #333333;
        margin-bottom: 20px;
    }

    .upload-btn {
        display: block;
        margin: 0 auto;
        background-color: #ffffff;
        color: #000000;
        font-size: 16px;
        padding: 10px 20px;
        border: 2px solid #0078d4;
        border-radius: 5px;
        cursor: pointer;
    }

    .upload-btn:hover {
        background-color: #0078d4;
        color: #ffffff;
    }

    .footer {
        text-align: center;
        margin-top: 50px;
    }

    .footer a {
        text-decoration: none;
        color: #0078d4;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Add an overlay to ensure text stands out on the background
st.markdown('<div class="overlay">', unsafe_allow_html=True)

# Main page content
st.markdown('<div class="header">Ventory</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your sales and inventory partner</div>', unsafe_allow_html=True)

# File upload widget (without the "Upload CSV or Excel" label)
uploaded_file = st.file_uploader("", type=["csv", "xlsx"], key="file_uploader")

if uploaded_file is not None:
    st.write("File successfully uploaded!")
    # You can process the file here (e.g., read and display it)
    if uploaded_file.type == "text/csv":
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        st.write(df.head())  # Display first 5 rows
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        import pandas as pd
        df = pd.read_excel(uploaded_file)
        st.write(df.head())  # Display first 5 rows

# Footer with LinkedIn logo and link
st.markdown(
    """
    <div class="footer">
        <a href="https://www.linkedin.com" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7a/LinkedIn_logo_2023.svg" width="100" alt="LinkedIn Logo"/>
        </a>
    </div>
    """, unsafe_allow_html=True
)

# End the overlay div
st.markdown('</div>', unsafe_allow_html=True)
