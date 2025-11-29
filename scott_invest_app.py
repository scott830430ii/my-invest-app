import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. 系統設定 (必須在第一行) ---
st.set_page_config(page_title="Alpha Pocket", layout="wide", initial_sidebar_state="collapsed")

# --- 2. Vibe CSS (暗黑高質感 UI) ---
st.markdown("""
    <style>
        /* 全域設定 */
        .stApp {background-color: #0f1115; color: #e0e0e0;}
        
        /* 隱藏預設元件 */
        header, #MainMenu, footer {visibility: hidden;}
        .block-container {padding: 1rem 1rem 5rem 1rem !important;}
        
        /* 自定義 Tabs 樣式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #181b21;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #2d3748;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 8px;
            color: #9ca3af;
            font-weight: bold;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6366f1 !important;
            color: white !important;
        }
        
        /* 輸入框樣式 */
        .stTextInput > div > div > input {
            background-color: #181b21;
            color: white;
            border: 1px solid #2d3748;
            border-radius: 10px;
        }
        
        /* 搜尋結果卡片 */
        .search-card {
            background-color: #1f2937;
            border: 1px solid #6366f1;
            padding: 15px;
            border-radius: 12px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. 初始化數據結構 (Session State) ---
# 這是為了讓 App 記住您的分類，預設先給您兩個分類
if 'watchlists' not in st.session_state:
    st.session_state['watchlists'] = {
        "🚀 核心持股": ["TSLA", "2330.TW", "NVDA"],
        "👀 觀察清單": ["0050.TW", "AAPL", "BTC-USD"]
    }

# --- 4. 核心功能函數 ---

def get_stock_info(ticker_input):
    """取得單一股票的即時資訊"""
    # 智慧判斷：如果是 4 位數字，預設為台股
    ticker = ticker_input.upper().strip()
    if ticker.isdigit() and len(ticker) == 4:
        ticker = f"{ticker}.TW"
    
    try:
        stock = yf.Ticker(ticker)
        # 取得極短期的歷史數據來抓現價
        hist = stock.history(period="5d")
        
        if hist.empty:
            return None, "找不到此股票，請確認代號。"
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change = current_price - prev_price
        pct_change = (change / prev_price) * 100
        
        info = {
            "symbol": ticker,
            "name": stock.info.get('shortName', ticker),
            "price": current_price,
            "change": change,
            "pct_change": pct_change,
            "history": hist
        }
        return info, None
    except Exception as e:
        return None, str(e)

def draw_mini_chart(hist_df):
    """繪製迷你走勢圖"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_df.index, y=hist_df['Close'],
        mode='lines',
        line=dict(color='#6366f1', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

# --- 5. UI 佈局 ---

# 使用 Tabs 分頁切換功能
tab1, tab2 = st.tabs(["📊 我的關注", "🔍 搜尋 & 新增"])

# === Tab 1: 監控儀表板 ===
with tab1:
    # 選擇要看的分類
    categories = list(st.session_state['watchlists'].keys())
    selected_category = st.selectbox("選擇分類", categories, label_visibility="collapsed")
    
    current_tickers = st.session_state['watchlists'][selected_category]
    
    if not current_tickers:
        st.info("這個分類還沒有股票，去「搜尋」頁面加一點吧！")
    else:
        # 這裡我們一次抓取分類裡的所有股票數據 (Batch Fetch)
        try:
            # 顯示標題
            st.markdown(f"<div style='color:#6366f1; font-size:14px; font-weight:bold; margin-bottom:10px;'>{selected_category} ({len(current_tickers)})</div>", unsafe_allow_html=True)
            
            for ticker in current_tickers:
                # 為了示範流暢度，這裡逐個抓取 (實際生產環境可用 batch download 優化)
                info, err = get_stock_info(ticker)
                
                if info:
                    color = "#10b981" if info['pct_change'] >= 0 else "#ef4444"
                    sign = "+" if info['pct_change'] >= 0 else ""
                    
                    # 卡片 UI
                    col_text, col_chart = st.columns([3, 2])
                    with col_text:
                        st.markdown(f"""
                        <div style="background-color: #181b21; padding: 12px; border-radius: 12px 0 0 12px; border: 1px solid #2d3748; border-right: none; height: 120px; display: flex; flex-direction: column; justify-content: center;">
                            <div style="font-weight: bold; color: white; font-size: 18px;">{info['symbol']}</div>
                            <div style="font-size: 12px; color: #9ca3af; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{info['name']}</div>
                            <div style="margin-top: 8px;">
                                <span style="font-family: monospace; font-size: 20px; font-weight: bold; color: white;">${info['price']:,.2f}</span>
                            </div>
                            <div style="font-size: 12px; color: {color}; font-weight: bold;">
                                {sign}{info['change']:.2f} ({sign}{info['pct_change']:.2f}%)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_chart:
                        # 顯示圖表
                        st.markdown(f"""<div style="background-color: #181b21; border: 1px solid #2d3748; border-left: none; border-radius: 0 12px 12px 0; height: 120px; padding-top: 10px;">""", unsafe_allow_html=True)
                        st.plotly_chart(draw_mini_chart(info['history']), use_container_width=True, config={'displayModeBar': False})
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"連線錯誤: {e}")

# === Tab 2: 搜尋與新增 ===
with tab2:
    st.markdown("### 搜尋股票")
    st.markdown("<p style='color:#6b7280; font-size:12px;'>支援美股代號 (AAPL) 或 台股代碼 (2330)</p>", unsafe_allow_html=True)
    
    search_query = st.text_input("輸入代號", placeholder="例如: NVDA 或 2330", label_visibility="collapsed")
    
    if search_query:
        with st.spinner("Searching..."):
            info, error = get_stock_info(search_query)
            
        if error:
            st.error(error)
        elif info:
            # 顯示搜尋結果
            st.markdown(f"""
                <div class="search-card">
                    <h3 style="margin:0; color:white;">{info['symbol']}</h3>
                    <p style="color:#9ca3af; font-size:14px;">{info['name']}</p>
                    <h2 style="color:#6366f1; font-family:monospace;">${info['price']:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 新增到分類的功能
            st.markdown("##### 加入收藏")
            
            # 新增分類功能
            new_cat = st.text_input("建立新分類 (選填)", placeholder="例如: 高股息存股")
            target_cat_options = list(st.session_state['watchlists'].keys())
            
            if new_cat:
                target_cat = new_cat # 如果有填寫新分類，就用新的
            else:
                target_cat = st.selectbox("選擇現有分類", target_cat_options)
            
            if st.button("➕ 加入追蹤清單"):
                # 邏輯：處理新分類或現有分類
                if new_cat and new_cat not in st.session_state['watchlists']:
                    st.session_state['watchlists'][new_cat] = []
                    target_cat = new_cat
                
                # 避免重複加入
                if info['symbol'] not in st.session_state['watchlists'][target_cat]:
                    st.session_state['watchlists'][target_cat].append(info['symbol'])
                    st.toast(f"已將 {info['symbol']} 加入 {target_cat}!", icon="✅")
                else:
                    st.warning(f"{info['symbol']} 已經在 {target_cat} 裡面囉！")

# 頁尾說明
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#4b5563; font-size:12px;'>Data provided by Yahoo Finance</div>", unsafe_allow_html=True)
