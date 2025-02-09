import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import DataLoader
from strategies.implementations import create_strategy

def render_backtest_analysis():
    st.title("回测分析")
    
    # 检查是否有策略配置
    if 'strategy_config' not in st.session_state:
        st.warning("请先在策略配置页面设置交易策略")
        return
        
    config = st.session_state.strategy_config
    
    # 显示策略信息
    st.subheader("策略信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("股票代码", config['stock_code'])
    with col2:
        st.metric("策略类型", config['strategy_type'])
    with col3:
        st.metric("初始资金", f"¥{config['initial_capital']:,.2f}")
        
    # 加载数据
    try:
        loader = DataLoader()
        # 从股票代码中提取纯数字部分
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
        try:
            strategy = create_strategy(
                config['strategy_type'],
                data,
                **strategy_params
            )
            
            results = strategy.run_backtest()
            
            if not results or 'equity_curve' not in results:
                st.error("策略回测未返回有效结果")
                return
                
            # 计算关键指标
            equity_curve = results['equity_curve']
            final_equity = equity_curve.iloc[-1]  # 使用 iloc 访问最后一个元素
            total_return = (final_equity / config['initial_capital'] - 1) * 100
            annual_return = total_return * (252 / len(equity_curve))
            
            # 计算最大回撤
            peak = equity_curve.expanding(min_periods=1).max()
            drawdown = (equity_curve - peak) / peak * 100
            max_drawdown = drawdown.min()
            
            # 计算夏普比率
            daily_returns = equity_curve.pct_change().dropna()
            sharpe_ratio = np.sqrt(252) * (daily_returns.mean() / daily_returns.std()) if len(daily_returns) > 0 else 0
            
            # 显示关键指标
            st.subheader("回测结果")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总收益率", f"{total_return:.2f}%")
            with col2:
                st.metric("年化收益率", f"{annual_return:.2f}%")
            with col3:
                st.metric("最大回撤", f"{max_drawdown:.2f}%")
            with col4:
                st.metric("夏普比率", f"{sharpe_ratio:.2f}")
                
            # 绘制权益曲线和回撤
            st.subheader("权益曲线与回撤分析")
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              subplot_titles=('权益曲线', '回撤分析'),
                              vertical_spacing=0.12, row_heights=[0.7, 0.3])
                              
            # 添加权益曲线
            fig.add_trace(
                go.Scatter(x=equity_curve.index,
                          y=equity_curve.values,
                          name="权益曲线",
                          line=dict(color='rgb(49,130,189)')),
                row=1, col=1
            )
            
            # 添加回撤曲线
            fig.add_trace(
                go.Scatter(x=drawdown.index,
                          y=drawdown.values,
                          name="回撤",
                          fill='tozeroy',
                          line=dict(color='rgba(255,0,0,0.5)')),
                row=2, col=1
            )
            
            fig.update_layout(height=800, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # 绘制收益分布直方图
            if len(daily_returns) > 0:
                st.subheader("收益分布")
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=daily_returns * 100,
                    nbinsx=50,
                    name="日收益率分布",
                    histnorm='probability',
                    marker_color='rgb(49,130,189)'
                ))
                fig.update_layout(
                    title="日收益率分布直方图",
                    xaxis_title="日收益率 (%)",
                    yaxis_title="概率",
                    bargap=0.1
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 显示交易记录
            if results.get('trades') and len(results['trades']) > 0:
                st.subheader("最近交易记录")
                trades_df = pd.DataFrame(results['trades'])
                trades_df['profit'] = trades_df['profit'].round(2)
                trades_df['commission'] = trades_df['commission'].round(2)
                st.dataframe(trades_df.tail(10))
                
        except Exception as e:
            st.error(f"策略执行错误: {str(e)}")
            st.exception(e)
            
    except Exception as e:
        st.error(f"回测过程中发生错误: {str(e)}")
        st.exception(e)
        
if __name__ == "__main__":
    render_backtest_analysis() 