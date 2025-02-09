import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from utils.data_loader import DataLoader

def calculate_metrics(equity_curve):
    """计算回测指标"""
    returns = equity_curve['equity'].pct_change()
    
    # 计算年化收益率
    total_days = (equity_curve.index[-1] - equity_curve.index[0]).days
    annual_return = (equity_curve['equity'].iloc[-1] / equity_curve['equity'].iloc[0]) ** (365/total_days) - 1
    
    # 计算最大回撤
    rolling_max = equity_curve['equity'].expanding().max()
    drawdowns = equity_curve['equity'] / rolling_max - 1
    max_drawdown = drawdowns.min()
    
    # 计算夏普比率
    risk_free_rate = 0.03  # 假设无风险利率为3%
    excess_returns = returns - risk_free_rate/252
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()
    
    # 计算胜率
    win_rate = len(returns[returns > 0]) / len(returns[returns != 0])
    
    return {
        "年化收益率": f"{annual_return:.2%}",
        "最大回撤": f"{max_drawdown:.2%}",
        "夏普比率": f"{sharpe_ratio:.2f}",
        "胜率": f"{win_rate:.2%}"
    }

def render_backtest_analysis():
    st.title("回测分析")
    
    if "strategy_config" not in st.session_state:
        st.warning("请先在策略配置页面设置并运行策略")
        return
    
    # 获取策略配置
    config = st.session_state["strategy_config"]
    
    # 显示策略信息
    st.subheader("策略信息")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"股票代码: {config['stock_code']}")
        st.info(f"策略类型: {config['strategy_type']}")
    
    with col2:
        st.info(f"起始日期: {config['start_date']}")
        st.info(f"结束日期: {config['end_date']}")
    
    with col3:
        st.info(f"初始资金: ¥{config['initial_capital']:,.2f}")
        st.info(f"手续费率: {config['commission_rate']:.4%}")
    
    # 加载数据
    loader = DataLoader()
    df = loader.load_daily_data(config['stock_code'].split('.')[0])
    
    if df is not None:
        # 模拟回测结果（这里需要根据实际策略实现）
        df = df[(df['trade_date'] >= pd.to_datetime(config['start_date'])) & 
               (df['trade_date'] <= pd.to_datetime(config['end_date']))]
        
        # 创建回测结果
        equity_curve = pd.DataFrame(index=df['trade_date'])
        equity_curve['equity'] = np.random.normal(loc=1.0002, scale=0.01, size=len(df)).cumprod() * config['initial_capital']
        equity_curve['benchmark'] = df['close'] / df['close'].iloc[0] * config['initial_capital']
        
        # 计算回测指标
        metrics = calculate_metrics(equity_curve)
        
        # 显示回测指标
        st.subheader("回测指标")
        cols = st.columns(len(metrics))
        for col, (metric, value) in zip(cols, metrics.items()):
            col.metric(metric, value)
        
        # 创建回测图表
        st.subheader("收益曲线")
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=("策略收益vs基准收益", "回撤分析"),
                           vertical_spacing=0.12,
                           row_heights=[0.7, 0.3])
        
        # 添加策略收益曲线
        fig.add_trace(
            go.Scatter(x=equity_curve.index, y=equity_curve['equity'],
                      name="策略收益", line=dict(color='rgb(0,176,146)')),
            row=1, col=1
        )
        
        # 添加基准收益曲线
        fig.add_trace(
            go.Scatter(x=equity_curve.index, y=equity_curve['benchmark'],
                      name="基准收益", line=dict(color='rgb(250,128,114)')),
            row=1, col=1
        )
        
        # 计算并添加回撤曲线
        rolling_max = equity_curve['equity'].expanding().max()
        drawdowns = (equity_curve['equity'] / rolling_max - 1) * 100
        
        fig.add_trace(
            go.Scatter(x=equity_curve.index, y=drawdowns,
                      name="回撤", fill='tozeroy',
                      line=dict(color='rgba(255,0,0,0.3)')),
            row=2, col=1
        )
        
        # 更新布局
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="回测分析结果"
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示每日收益分布
        st.subheader("收益分布")
        daily_returns = equity_curve['equity'].pct_change().dropna()
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=daily_returns,
            nbinsx=50,
            name="日收益分布",
            histnorm='probability'
        ))
        
        fig_dist.update_layout(
            title="日收益分布直方图",
            xaxis_title="日收益率",
            yaxis_title="概率",
            showlegend=True
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
        
    else:
        st.error("获取股票数据失败，请检查股票代码是否正确")

if __name__ == "__main__":
    render_backtest_analysis() 