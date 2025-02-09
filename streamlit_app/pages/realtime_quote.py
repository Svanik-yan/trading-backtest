import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils.data_loader import DataLoader
import time

def render_realtime_quote():
    st.title("实时行情")
    
    # 初始化数据加载器
    loader = DataLoader()
    
    # 股票选择
    stock_list = loader.load_stock_list()
    selected_stock = st.selectbox(
        "选择股票",
        options=stock_list['ts_code'].tolist(),
        format_func=lambda x: f"{x} - {stock_list[stock_list['ts_code']==x]['name'].values[0]}"
    )
    
    # 自动刷新设置
    col1, col2 = st.columns([1, 2])
    with col1:
        auto_refresh = st.checkbox("自动刷新", value=True)
    with col2:
        refresh_interval = st.slider("刷新间隔(秒)", min_value=5, max_value=60, value=10)
    
    # 获取实时数据
    quote_data = loader.get_realtime_quote(selected_stock.split('.')[0])
    
    if quote_data is not None:
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            # 显示基本信息
            try:
                price_delta = float(quote_data['price'].values[0]) - float(quote_data.get('pre_close', quote_data['open']).values[0])
                st.metric(
                    label="当前价格",
                    value=f"¥{quote_data['price'].values[0]}",
                    delta=f"{price_delta:.2f}"
                )
            except:
                st.metric(
                    label="当前价格",
                    value=f"¥{quote_data['price'].values[0]}"
                )
            
            # 创建价格变动图表
            try:
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode="number+delta",
                    value=float(quote_data['price'].values[0]),
                    delta={'reference': float(quote_data.get('pre_close', quote_data['open']).values[0])},
                    title={'text': "价格变动"}
                ))
                st.plotly_chart(fig)
            except:
                st.warning("价格变动数据暂不可用")
        
        with col2:
            # 显示交易信息
            st.metric("成交量", f"{quote_data['volume'].values[0]}")
            st.metric("成交额", f"{quote_data['amount'].values[0]}")
            st.metric("今开", f"¥{quote_data['open'].values[0]}")
            st.metric("最高", f"¥{quote_data['high'].values[0]}")
            st.metric("最低", f"¥{quote_data['low'].values[0]}")
        
        # 显示详细数据表格
        st.subheader("交易详情")
        display_cols = ['code', 'name', 'price', 'volume', 'amount', 'time']
        st.dataframe(
            quote_data[display_cols],
            use_container_width=True
        )
        
        # 显示最新交易时间
        st.caption(f"最后更新时间: {quote_data['time'].values[0]}")
        
        # 添加自动刷新
        if auto_refresh:
            time.sleep(1)  # 避免立即刷新
            st.experimental_rerun()
    else:
        st.error("获取实时数据失败，请稍后重试")

if __name__ == "__main__":
    render_realtime_quote() 