import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="股票策略回测系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Svanik-yan/trading-backtest',
        'Report a bug': 'https://github.com/Svanik-yan/trading-backtest/issues',
        'About': '# 股票策略回测系统\n 一个简单易用的股票策略回测系统。'
    }
)

# 设置主题和样式
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container {
        background: #f5f5f5;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 处理页面跳转
if "should_redirect" in st.session_state and st.session_state["should_redirect"]:
    selected_page = st.session_state["redirect_page"]
    # 清除跳转标志
    st.session_state["should_redirect"] = False
    del st.session_state["redirect_page"]
else:
    selected_page = "策略配置"

# 侧边栏导航
with st.sidebar:
    selected = option_menu(
        menu_title="主菜单",
        options=[
            "实时行情（开发中）", 
            "策略配置",
            "回测分析",
            "交易记录",
            "绩效分析"
        ],
        icons=[
            "graph-up",
            "gear",
            "calculator",
            "journal-text",
            "pie-chart"
        ],
        menu_icon="cast",
        default_index=1 if selected_page == "策略配置" else 2,  # 根据跳转状态设置默认页面
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

# 主页面内容
st.title("股票策略回测系统")

if selected == "实时行情（开发中）":
    st.info("实时行情模块正在开发中，敬请期待...")
    
elif selected == "策略配置":
    from pages.strategy_config import render_strategy_config
    render_strategy_config()
    
elif selected == "回测分析":
    from pages.backtest_analysis import render_backtest_analysis
    render_backtest_analysis()
    
elif selected == "交易记录":
    from pages.trade_records import render_trade_records
    render_trade_records()
    
elif selected == "绩效分析":
    from pages.performance_analysis import render_performance_analysis
    render_performance_analysis() 