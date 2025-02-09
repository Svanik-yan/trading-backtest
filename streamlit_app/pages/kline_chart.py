import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_loader import DataLoader

def render_kline_chart():
    st.title("K线图表")
    
    try:
        # 初始化数据加载器
        loader = DataLoader()
        
        # 创建左右两列布局
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 股票选择
            stock_list = loader.load_stock_list()
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
        
        if df is not None and not df.empty:
            # 确保日期列格式正确
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 确保数值列为浮点数
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
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
                for ma, color in [("MA5", "blue"), ("MA10", "orange"), ("MA20", "purple")]:
                    if ma in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df['trade_date'],
                            y=df[ma],
                            name=ma,
                            line=dict(color=color)
                        ))
            
            if "MACD" in indicators and all(x in df.columns for x in ['MACD', 'Signal', 'Histogram']):
                # 创建子图显示MACD
                fig.add_trace(go.Scatter(x=df['trade_date'], y=df['MACD'], name="MACD", yaxis="y2"))
                fig.add_trace(go.Scatter(x=df['trade_date'], y=df['Signal'], name="Signal", yaxis="y2"))
                fig.add_trace(go.Bar(x=df['trade_date'], y=df['Histogram'], name="Histogram", yaxis="y2"))
            
            if "RSI" in indicators and 'RSI' in df.columns:
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
            display_df = df[['trade_date', 'open', 'high', 'low', 'close', 'volume']].copy()
            display_df['trade_date'] = display_df['trade_date'].dt.strftime('%Y-%m-%d')
            st.dataframe(
                display_df.sort_values('trade_date', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("暂无历史数据，请检查股票代码是否正确或稍后重试")
            
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        st.error("请检查数据格式是否正确或稍后重试")

if __name__ == "__main__":
    render_kline_chart() 