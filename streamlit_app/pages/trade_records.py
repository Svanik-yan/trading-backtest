import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import DataLoader
from strategies.implementations import create_strategy

def render_trade_records():
    st.title("交易记录")
    
    if "strategy_config" not in st.session_state:
        st.warning("请先在策略配置页面设置并运行策略")
        return
    
    # 获取策略配置
    config = st.session_state["strategy_config"]
    
    try:
        # 显示策略信息
        st.subheader("策略信息")
        st.info(f"股票: {config['stock_code']} | 策略: {config['strategy_type']} | 周期: {config['start_date'].strftime('%Y-%m-%d')} 至 {config['end_date'].strftime('%Y-%m-%d')}")
        
        # 加载数据并运行策略获取交易记录
        loader = DataLoader()
        stock_code = config['stock_code'].split('.')[0]
        data = loader.load_daily_data(stock_code)
        
        if data is None or data.empty:
            st.error("无法加载股票数据，请检查股票代码是否正确")
            return
            
        # 确保数据按日期排序
        data = data.sort_values('trade_date')
        data.set_index('trade_date', inplace=True)
        
        # 准备策略参数
        strategy_params = {
            'initial_capital': config['initial_capital'],
            'commission_rate': config['commission_rate'],
            'slippage': config['slippage'],
            'price_type': config['price_type']
        }
        
        # 添加特定策略的参数
        if 'strategy_params' in config:
            strategy_params.update(config['strategy_params'])
            
        # 添加仓位管理参数
        if 'position_params' in config:
            strategy_params.update(config['position_params'])
            
        # 添加交易条件
        strategy_params['buy_conditions'] = config.get('buy_conditions', {})
        strategy_params['sell_conditions'] = config.get('sell_conditions', {})
        
        # 创建并运行策略
        strategy = create_strategy(
            config['strategy_type'],
            data,
            **strategy_params
        )
        
        results = strategy.run_backtest()
        
        if not results or 'trades' not in results or not results['trades']:
            st.warning("没有找到交易记录")
            return
            
        trades = pd.DataFrame(results['trades'])
        
        # 绘制K线图和交易点
        st.subheader("交易K线图")
        
        # 创建K线图
        fig = go.Figure()
        
        # 添加K线数据
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="K线"
        ))
        
        # 添加买入点
        buy_trades = trades[trades['type'] == '买入']
        if not buy_trades.empty:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(buy_trades['date']),
                y=buy_trades['price'],
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='red',
                    line=dict(width=2)
                ),
                name="买入点"
            ))
        
        # 添加卖出点
        sell_trades = trades[trades['type'] == '卖出']
        if not sell_trades.empty:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(sell_trades['date']),
                y=sell_trades['price'],
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='green',
                    line=dict(width=2)
                ),
                name="卖出点"
            ))
        
        # 更新布局
        fig.update_layout(
            title=f"{config['stock_code']} K线图与交易点",
            yaxis_title="价格",
            xaxis_title="日期",
            height=600,
            xaxis_rangeslider_visible=False
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 交易统计
        st.subheader("交易统计")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总交易次数", len(trades))
            
        with col2:
            buy_count = len(trades[trades['type'] == '买入'])
            sell_count = len(trades[trades['type'] == '卖出'])
            st.metric("买入/卖出次数", f"{buy_count}/{sell_count}")
            
        with col3:
            total_commission = trades['commission'].sum()
            st.metric("总手续费", f"¥{total_commission:,.2f}")
            
        with col4:
            total_profit = trades['profit'].sum()
            st.metric("总收益", f"¥{total_profit:,.2f}")
        
        # 交易记录表格
        st.subheader("交易明细")
        
        # 添加筛选器
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_type = st.multiselect(
                "交易类型",
                options=['买入', '卖出'],
                default=['买入', '卖出']
            )
        
        with col2:
            profit_filter = st.radio(
                "收益筛选",
                ['全部', '盈利', '亏损']
            )
        
        with col3:
            sort_by = st.selectbox(
                "排序方式",
                ['按时间降序', '按时间升序', '按收益降序', '按收益升序']
            )
        
        # 应用筛选
        filtered_trades = trades[trades['type'].isin(trade_type)]
        
        if profit_filter == '盈利':
            filtered_trades = filtered_trades[filtered_trades['profit'] > 0]
        elif profit_filter == '亏损':
            filtered_trades = filtered_trades[filtered_trades['profit'] < 0]
        
        # 应用排序
        if sort_by == '按时间降序':
            filtered_trades = filtered_trades.sort_values('date', ascending=False)
        elif sort_by == '按时间升序':
            filtered_trades = filtered_trades.sort_values('date', ascending=True)
        elif sort_by == '按收益降序':
            filtered_trades = filtered_trades.sort_values('profit', ascending=False)
        else:
            filtered_trades = filtered_trades.sort_values('profit', ascending=True)
        
        # 格式化数据用于显示
        display_trades = filtered_trades.copy()
        display_trades['date'] = pd.to_datetime(display_trades['date']).dt.strftime('%Y-%m-%d')
        display_trades['price'] = display_trades['price'].apply(lambda x: f"¥{x:,.4f}")
        display_trades['amount'] = display_trades['amount'].apply(lambda x: f"¥{x:,.2f}")
        display_trades['commission'] = display_trades['commission'].apply(lambda x: f"¥{x:,.2f}")
        display_trades['profit'] = display_trades['profit'].apply(lambda x: f"¥{x:,.2f}")
        
        # 显示交易记录
        st.dataframe(
            display_trades,
            use_container_width=True
        )
        
        # 导出功能
        if st.button("导出交易记录"):
            # 转换日期格式为字符串
            export_trades = filtered_trades.copy()
            export_trades['date'] = pd.to_datetime(export_trades['date']).dt.strftime('%Y-%m-%d')
            csv = export_trades.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name=f"trade_records_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"处理交易记录时发生错误: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    render_trade_records() 