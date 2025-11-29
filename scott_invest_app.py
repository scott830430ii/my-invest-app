import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Alpha Pocket", layout="wide", initial_sidebar_state="collapsed")

# --- 2. Vibe CSS (維持暗黑高質感) ---
st.markdown("""
    <style>
        .stApp {background-color: #0f1115; color: #e0e0e0;}
        header, #MainMenu, footer {visibility: hidden;}
        .block-container {padding: 1rem 1rem 5rem 1rem !important;}
        
        /* 隱藏預設的 radio 按鈕圓圈，改成按鈕樣式 */
        div[role="radiogroup"] > label > div:first-of-type {display: none;}
        div[role="radiogroup"] {flex-direction: row; overflow-x: auto; gap: 10px;}
        div[role="radiogroup"] label {
            background: #181b21; border: 1px solid #2d3748; padding: 8px 16px;
            border-radius: 20px; color: #9ca3af; white-space: nowrap; transition: 0.2s;
        }
        div[role="radiogroup"] label:hover {border-color: #6366f1; color: white;}
        /* 被選中的樣式 (這比較難抓，用一般文字顏色代替) */
        
        /* 卡片與指標 */
        .metric-card {background-color: #181b21; border-radius: 12px; padding: 15px; border: 1px solid #2d3748; margin-bottom: 10px;}
        div[data-testid="stMetricValue"] {font-size: 28px; color: #ffffff; font-family: 'SF Mono', monospace;}
    </style>
""", unsafe_allow_html=True)

# --- 3. 真實數據邏輯 (The Engine) ---

# 設定你的持倉 (你可以在這裡修改真實的股數)
MY_PORTFOLIO = {
    "TSLA": {"shares": 50, "avg_cost": 210},
    "NVDA": {"shares": 20, "avg_cost": 450},
    "AAPL": {"shares": 100, "avg_cost": 175},
    "BTC-USD": {"shares": 0.5, "avg_cost": 65000}, # 比特幣
}

@st.cache_data(ttl=60) # 快取 60 秒，避免一直重複抓
def fetch_data():
    tickers = list(MY_PORTFOLIO.keys())
    # 一次抓取所有股票的當日數據
    data = yf.download(tickers, period="1mo", interval="1d", group_by='ticker')
    return data

try:
    with st.spinner('Connecting to Wall Street...'):
        market_data = fetch_data()
        
    # 計算總資產
    total_balance = 0
    total_prev_balance = 0
    assets_display = []

    for ticker, info in MY_PORTFOLIO.items():
        # 處理單一股票數據
        if len(MY_PORTFOLIO) == 1:
            stock_df = market_data
        else:
            stock_df = market_data[ticker]
            
        # 取得最新價格與前一日價格
        current_price = stock_df['Close'].iloc[-1]
        prev_price = stock_df['Close'].iloc[-2]
        
        # 計算價值
        value = current_price * info['shares']
        prev_value = prev_price * info['shares']
        
        total_balance += value
        total_prev_balance += prev_value
        
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        assets_display.append({
            "ticker": ticker,
            "shares": info['shares'],
            "price": current_price,
            "value": value,
            "change_pct": change_pct,
            "history": stock_df # 存起來畫圖用
        })

    # 計算總損益
    daily_pnl = total_balance - total_prev_balance
    daily_pnl_pct = (daily_pnl / total_prev_balance) * 100

except Exception as e:
    st.error(f"Data Fetch Error: {e}")
    st.stop()

# --- 4. UI 呈現 ---

# 頂部：總資產
st.markdown('<p style="color:#9ca3af; font-size:12px; margin-bottom:0;">TOTAL BALANCE</p>', unsafe_allow_html=True)
st.markdown(f'<h1 style="margin-top:0; font-size:36px; font-family:monospace; font-weight:bold;">${total_balance:,.2f}</h1>', unsafe_allow_html=True)

# 損益顯示
pnl_color = "#10b981" if daily_pnl >= 0 else "#ef4444"
sign = "+" if daily_pnl >= 0 else ""
st.markdown(f"""
    <div style="background-color: {pnl_color}20; padding: 8px 12px; border-radius: 8px; display: inline-block; margin-bottom: 20px;">
        <span style="color: {pnl_color}; font-weight: bold; font-family: monospace;">
            {sign}${abs(daily_pnl):,.2f} ({sign}{daily_pnl_pct:.2f}%)
        </span>
        <span style="color: #6b7280; font-size: 12px; margin-left: 5px;">Today</span>
    </div>
""", unsafe_allow_html=True)

# 互動選單：選擇要查看的股票
st.markdown('<br>', unsafe_allow_html=True)
selected_ticker = st.selectbox("Select Asset", list(MY_PORTFOLIO.keys()), label_visibility="collapsed")

# 找出選中股票的歷史數據
selected_asset = next(item for item in assets_display if item["ticker"] == selected_ticker)
history_df = selected_asset['history']

# 繪製圖表 (Area Chart)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=history_df.index, 
    y=history_df['Close'],
    mode='lines',
    line=dict(color='#6366f1', width=2),
    fill='tozeroy',
    fillcolor='rgba(99, 102, 241, 0.1)'
))
fig.update_layout(
    margin=dict(l=0, r=0, t=10, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=250,
    xaxis=dict(showgrid=False, tickformat='%m/%d'), # 簡化日期顯示
    yaxis=dict(showgrid=True, gridcolor='#2d3748', side='right'), # 網格線暗色
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 資產列表
st.markdown('<h3 style="font-size:16px; color:#9ca3af; margin-top:20px; margin-bottom:10px;">YOUR ASSETS</h3>', unsafe_allow_html=True)

for asset in assets_display:
    color = "#10b981" if asset['change_pct'] > 0 else "#ef4444"
    pct_sign = "+" if asset['change_pct'] > 0 else ""
    
    # 判斷是否為當前選中，加上不同邊框
    border_style = "2px solid #6366f1" if asset['ticker'] == selected_ticker else "1px solid #2d3748"
    
    st.markdown(f"""
    <div style="background-color: #181b21; padding: 15px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: {border_style};">
        <div style="display:flex; align-items:center;">
            <div style="background-color: #2d3748; width: 40px; height: 40px; border-radius: 8px; display:flex; align-items:center; justify-content:center; margin-right: 12px; font-weight:bold; color:white;">
                {asset['ticker'][0]}
            </div>
            <div>
                <div style="font-weight: bold; color: white;">{asset['ticker']}</div>
                <div style="font-size: 12px; color: #9ca3af;">{asset['shares']} Shares</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: bold; color: white; font-family: monospace;">${asset['price']:,.2f}</div>
            <div style="font-size: 12px; color: {color}; font-weight: bold;">{pct_sign}{asset['change_pct']:.2f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 重新整理按鈕 (因為 Streamlit 預設是靜態的)
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()
