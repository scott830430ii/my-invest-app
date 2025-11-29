import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. 頁面設定 (必須在最前面) ---
st.set_page_config(
    page_title="Alpha Pocket",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Vibe CSS 注入 (讓它看起來像 App 的關鍵) ---
# 這段 CSS 會隱藏 Streamlit 的預設選單，調整邊距，並強制套用暗黑風格
st.markdown("""
    <style>
        /* 全域背景 */
        .stApp {
            background-color: #0f1115;
            color: #e0e0e0;
        }
        
        /* 隱藏頂部 Header 和漢堡選單 (讓畫面更乾淨) */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 調整手機版面邊距 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* 卡片樣式 */
        .css-1r6slb0, .css-12oz5g7 {
            background-color: #181b21;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #2d3748;
        }
        
        /* 數據指標優化 */
        div[data-testid="stMetricValue"] {
            font-size: 28px;
            color: #ffffff;
            font-family: 'SF Mono', monospace;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 14px;
        }
        
        /* 按鈕樣式 */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            background-color: #6366f1;
            color: white;
            border: none;
            height: 50px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #4f46e5;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. 模擬數據生成 (Mock Data) ---
def get_mock_data():
    dates = pd.date_range(end=datetime.today(), periods=30)
    base_price = 120000
    prices = [base_price + np.random.randint(-2000, 2500) for _ in range(30)]
    # 讓最後幾天呈現上漲趨勢，看起來比較爽
    for i in range(1, 6):
        prices[-i] = prices[-(i+1)] * (1 + np.random.uniform(0.005, 0.02))
    return pd.DataFrame({'Date': dates, 'Value': prices})

df = get_mock_data()
current_balance = df['Value'].iloc[-1]
prev_balance = df['Value'].iloc[-2]
daily_change = current_balance - prev_balance
daily_pct = (daily_change / prev_balance) * 100

# --- 4. UI 佈局 ---

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p style="color:#9ca3af; font-size:12px; margin-bottom:0;">TOTAL BALANCE</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="margin-top:0; font-size:32px; font-family:monospace;">${current_balance:,.2f}</h1>', unsafe_allow_html=True)
with col2:
    # 這裡顯示一個簡單的頭像或狀態
    st.markdown('<div style="text-align:right; font-size:24px;">🚀</div>', unsafe_allow_html=True)

# PNL Badge
if daily_change > 0:
    pnl_color = "#10b981" # Green
    sign = "+"
else:
    pnl_color = "#ef4444" # Red
    sign = ""

st.markdown(f"""
    <div style="background-color: {pnl_color}20; padding: 8px 12px; border-radius: 8px; display: inline-block; margin-bottom: 20px;">
        <span style="color: {pnl_color}; font-weight: bold; font-family: monospace;">
            {sign}${abs(daily_change):,.2f} ({sign}{daily_pct:.2f}%)
        </span>
        <span style="color: #6b7280; font-size: 12px; margin-left: 5px;">Today</span>
    </div>
""", unsafe_allow_html=True)

# Chart Section (Plotly)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['Date'], 
    y=df['Value'],
    mode='lines',
    line=dict(color='#6366f1', width=3),
    fill='tozeroy', # 填充顏色
    fillcolor='rgba(99, 102, 241, 0.2)' # 漸層透明度
))
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=250,
    xaxis=dict(showgrid=False, showticklabels=False),
    yaxis=dict(showgrid=False, showticklabels=False)
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Assets List Section
st.markdown('<h3 style="font-size:16px; color:#9ca3af; margin-top:20px; margin-bottom:10px;">PORTFOLIO</h3>', unsafe_allow_html=True)

assets = [
    {"name": "Tesla", "ticker": "TSLA", "price": 245.30, "change": 3.42},
    {"name": "Nvidia", "ticker": "NVDA", "price": 485.09, "change": 1.15},
    {"name": "Bitcoin", "ticker": "BTC", "price": 94200.00, "change": -0.85},
    {"name": "Apple", "ticker": "AAPL", "price": 191.50, "change": -0.21},
]

for asset in assets:
    color = "#10b981" if asset['change'] > 0 else "#ef4444"
    bg_color = "#181b21"
    
    # 這裡用 HTML 模擬手機 List Item
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 15px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #2d3748;">
        <div style="display:flex; align-items:center;">
            <div style="background-color: #2d3748; width: 40px; height: 40px; border-radius: 8px; display:flex; align-items:center; justify-content:center; margin-right: 12px; font-weight:bold;">
                {asset['ticker'][0]}
            </div>
            <div>
                <div style="font-weight: bold; color: white;">{asset['ticker']}</div>
                <div style="font-size: 12px; color: #9ca3af;">{asset['name']}</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: bold; color: white; font-family: monospace;">${asset['price']:,}</div>
            <div style="font-size: 12px; color: {color}; font-weight: bold;">{asset['change'] > 0 and '+' or ''}{asset['change']}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Action Buttons
st.markdown("<br>", unsafe_allow_html=True)
col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("BUY"):
        st.toast("Order placed! (Simulated)", icon="🚀")
with col_act2:
    if st.button("ANALYZE"):
        st.toast("Running AI Analysis...", icon="🤖")