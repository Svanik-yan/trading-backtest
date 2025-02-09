import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_loader import DataLoader

def render_kline_chart():
    st.title("K线图表")
    
    # 初始化数据加载器
    loader = DataLoader()
    
    # 创建左右两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 添加搜索框
        search_text = st.text_input("搜索股票代码或名称", key="stock_search")
        
        # 获取股票列表并应用搜索过滤
        stock_list = loader.load_stock_list(search_text)
        
        if stock_list.empty:
            st.warning("未找到匹配的股票")
            return
            
        # 股票选择
        selected_stock = st.selectbox(
            "选择股票",
            options=stock_list['ts_code'].tolist(),
            format_func=lambda x: f"{x} - {stock_list[stock_list['ts_code']==x]['name'].values[0]}"
        )
    
    with col2:
        # 技术指标选择
        indicators = st.multiselect(
            "选择技术指标",
            ["MA", "MACD", "RSI"],
            default=["MA"]
        )
    
    # 加载股票数据
    df = loader.load_daily_data(selected_stock.split('.')[0])
    
    if df is not None:
        # 计算技术指标
        df = loader.calculate_technical_indicators(df)
        
        # 创建K线图
        fig = go.Figure()
        
        # 添加K线数据
        fig.add_trace(go.Candlestick(
            x=df['trade_date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="K线"
        ))
        
        # 添加选中的技术指标
        if "MA" in indicators:
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['MA5'], name="MA5", line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['MA10'], name="MA10", line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['MA20'], name="MA20", line=dict(color='purple')))
        
        if "MACD" in indicators:
            # 创建子图显示MACD
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['MACD'], name="MACD", yaxis="y2"))
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['Signal'], name="Signal", yaxis="y2"))
            fig.add_trace(go.Bar(x=df['trade_date'], y=df['Histogram'], name="Histogram", yaxis="y2"))
        
        if "RSI" in indicators:
            # 创建子图显示RSI
            fig.add_trace(go.Scatter(x=df['trade_date'], y=df['RSI'], name="RSI", yaxis="y3"))
            
        # 更新布局
        fig.update_layout(
            title=f"{selected_stock} K线图",
            yaxis_title="价格",
            xaxis_title="日期",
            height=800,
            yaxis2=dict(title="MACD", overlaying="y", side="right") if "MACD" in indicators else None,
            yaxis3=dict(title="RSI", overlaying="y", side="right") if "RSI" in indicators else None,
            xaxis_rangeslider_visible=False
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示交易数据表格
        st.subheader("历史数据")
        st.dataframe(
            df[['trade_date', 'open', 'high', 'low', 'close', 'volume']].sort_values('trade_date', ascending=False),
            use_container_width=True
        )
    else:
        st.error("获取股票数据失败，请检查股票代码是否正确")

if __name__ == "__main__":
    render_kline_chart() 