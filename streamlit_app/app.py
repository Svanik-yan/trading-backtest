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

# 侧边栏导航
with st.sidebar:
    # 定义页面选项
    options = [
        "实时行情（开发中）", 
        "策略配置",
        "回测分析"
    ]
    
    # 初始化selected在session_state中
    if 'selected_page' not in st.session_state:
        st.session_state['selected_page'] = "策略配置"
        
    selected = option_menu(
        menu_title="主菜单",
        options=options,
        icons=[
            "graph-up",
            "gear",
            "calculator"
        ],
        menu_icon="cast",
        default_index=options.index(st.session_state['selected_page']),  # 使用保存的页面索引
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )
    # 更新selected_page
    st.session_state['selected_page'] = selected

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