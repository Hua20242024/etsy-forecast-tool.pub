# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="📊 Etsy Inventory Pro", 
    layout="wide",
    page_icon="📊"
)

# Rest of imports
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from random import uniform
import math

# --- [Keep all your existing style and setup code until the bubble chart function] ---

# --- Simplified Auto-Animated Bubble Chart ---
def create_product_bubbles(df):
    # Get last month's sales for each product
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    monthly_sales = df[df['date'].dt.strftime('%Y-%m') == last_month]
    
    if monthly_sales.empty:
        st.warning(f"No sales data for {last_month}")
        return None
    
    # Aggregate sales
    product_sales = monthly_sales.groupby('product')['units_sold'].sum().reset_index()
    
    # Create base positions (equally spaced)
    n = len(product_sales)
    base_positions = np.linspace(0, 100, n)
    
    # Generate frames with gentle movement
    frames = []
    for i in range(10):  # Number of animation frames
        frame = product_sales.copy()
        frame['x_pos'] = base_positions + np.random.uniform(-5, 5, n)  # Small horizontal movement
        frame['y_pos'] = frame['units_sold'] * (1 + np.random.uniform(-0.03, 0.03, n))  # Slight vertical variation
        frame['size'] = frame['units_sold'] * (1 + np.random.uniform(-0.05, 0.05, n))  # Gentle pulsing
        frames.append(frame)
    
    # Create figure with all frames
    fig = go.Figure()
    
    # Add traces for each product
    for i, product in enumerate(product_sales['product']):
        fig.add_trace(go.Scatter(
            x=[f['x_pos'].iloc[i] for f in frames],
            y=[f['y_pos'].iloc[i] for f in frames],
            mode='markers+text',
            marker=dict(
                size=[f['size'].iloc[i] for f in frames],
                sizemode='diameter',
                color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)],
                opacity=0.8,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=product,
            textposition='middle center',
            name=product,
            hoverinfo='text',
            hovertext=f"{product}<br>Units Sold: {product_sales['units_sold'].iloc[i]}"
        ))
    
    # Animation settings
    fig.update_layout(
        title=f"Last Month's Sales ({last_month})",
        xaxis=dict(visible=False, range=[-10, 110]),
        yaxis=dict(range=[0, product_sales['units_sold'].max() * 1.3]),
        showlegend=False,
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            buttons=[dict(
                label='',
                method='animate',
                args=[None, dict(frame=dict(duration=300, redraw=True), 
                                fromcurrent=True, 
                                mode='immediate')]
            )]
        )]
    )
    
    # Create animation frames
    fig.frames = [go.Frame(
        data=[go.Scatter(
            x=[frame['x_pos'].iloc[i] for i in range(n)],
            y=[frame['y_pos'].iloc[i] for i in range(n)],
            marker=dict(size=[frame['size'].iloc[i] for i in range(n)])
        )],
        name=str(k)
    ) for k, frame in enumerate(frames)]
    
    return fig

# --- [Rest of your existing code remains unchanged] ---
