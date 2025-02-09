import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from utils.data_loader import DataLoader
from strategies.implementations import create_strategy

def calculate_performance_metrics(returns):
    """计算绩效指标"""
    # 计算累积收益
    cumulative_returns = (1 + returns).cumprod()
    
    # 计算年化收益率
    annual_return = (cumulative_returns.iloc[-1]) ** (252/len(returns)) - 1
    
    # 计算波动率
    volatility = returns.std() * np.sqrt(252)
    
    # 计算夏普比率
    risk_free_rate = 0.03  # 假设无风险利率为3%
    sharpe_ratio = (annual_return - risk_free_rate) / volatility
    
    # 计算最大回撤
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = cumulative_returns / rolling_max - 1
    max_drawdown = drawdowns.min()
    
    # 计算Calmar比率
    calmar_ratio = annual_return / abs(max_drawdown)
    
    # 计算Sortino比率
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252)
    sortino_ratio = (annual_return - risk_free_rate) / downside_std
    
    return {
        "累积收益率": f"{(cumulative_returns.iloc[-1] - 1):.2%}",
        "年化收益率": f"{annual_return:.2%}",
        "年化波动率": f"{volatility:.2%}",
        "夏普比率": f"{sharpe_ratio:.2f}",
        "最大回撤": f"{max_drawdown:.2%}",
        "Calmar比率": f"{calmar_ratio:.2f}",
        "Sortino比率": f"{sortino_ratio:.2f}"
    }

def render_performance_analysis():
    st.title("绩效分析")
    
    if "strategy_config" not in st.session_state:
        st.warning("请先在策略配置页面设置交易策略")
        return
        
    if "backtest_results" not in st.session_state:
        st.warning("请先在回测分析页面运行策略")
        return
    
    # 获取策略配置和回测结果
    config = st.session_state["strategy_config"]
    results = st.session_state["backtest_results"]
    
    # 显示策略信息
    st.subheader("策略信息")
    st.info(f"股票: {config['stock_code']} | 策略: {config['strategy_type']} | 周期: {config['start_date'].strftime('%Y-%m-%d')} 至 {config['end_date'].strftime('%Y-%m-%d')}")
    
    try:
        if not results or 'equity_curve' not in results:
            st.error("策略回测未返回有效结果")
            return
            
        # 计算关键指标
        equity_curve = results['equity_curve']
        final_equity = equity_curve.iloc[-1]
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
        st.subheader("绩效指标")
        col1, col2, col3 = st.columns(3)
        
        metrics = calculate_performance_metrics(daily_returns)
        metrics_list = list(metrics.items())
        for i, (metric, value) in enumerate(metrics_list):
            with [col1, col2, col3][i % 3]:
                st.metric(metric, value)
        
        # 创建月度收益热力图
        st.subheader("月度收益热力图")
        
        # 计算月度收益
        monthly_returns = daily_returns.groupby([daily_returns.index.year, daily_returns.index.month]).sum()
        monthly_returns_matrix = monthly_returns.unstack()
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=monthly_returns_matrix.values,
            x=monthly_returns_matrix.columns,
            y=monthly_returns_matrix.index,
            colorscale='RdYlGn',
            text=np.round(monthly_returns_matrix.values * 100, 2),
            texttemplate='%{text}%',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="月度收益热力图",
            xaxis_title="月份",
            yaxis_title="年份"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 创建滚动分析图表
        st.subheader("滚动分析")
        
        # 计算滚动指标
        windows = [20, 60, 120]  # 滚动窗口大小
        
        fig = make_subplots(rows=3, cols=1,
                           subplot_titles=("滚动收益率", "滚动波动率", "滚动夏普比率"),
                           vertical_spacing=0.1,
                           row_heights=[0.33, 0.33, 0.33])
        
        # 添加滚动收益率
        for window in windows:
            rolling_returns = daily_returns.rolling(window).mean() * 252
            fig.add_trace(
                go.Scatter(x=daily_returns.index, y=rolling_returns,
                          name=f'{window}日滚动收益率',
                          line=dict(width=1)),
                row=1, col=1
            )
        
        # 添加滚动波动率
        for window in windows:
            rolling_vol = daily_returns.rolling(window).std() * np.sqrt(252)
            fig.add_trace(
                go.Scatter(x=daily_returns.index, y=rolling_vol,
                          name=f'{window}日滚动波动率',
                          line=dict(width=1)),
                row=2, col=1
            )
        
        # 添加滚动夏普比率
        for window in windows:
            rolling_returns = daily_returns.rolling(window).mean() * 252
            rolling_vol = daily_returns.rolling(window).std() * np.sqrt(252)
            rolling_sharpe = (rolling_returns - 0.03) / rolling_vol
            fig.add_trace(
                go.Scatter(x=daily_returns.index, y=rolling_sharpe,
                          name=f'{window}日滚动夏普比率',
                          line=dict(width=1)),
                row=3, col=1
            )
        
        fig.update_layout(height=900, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # 风险分析
        st.subheader("风险分析")
        
        # 计算VaR和CVaR
        confidence_levels = [0.99, 0.95, 0.90]
        var_data = []
        
        for level in confidence_levels:
            var = np.percentile(daily_returns, (1 - level) * 100)
            cvar = daily_returns[daily_returns <= var].mean()
            var_data.append({
                "置信水平": f"{level:.0%}",
                "VaR": f"{-var:.2%}",
                "CVaR": f"{-cvar:.2%}"
            })
        
        # 显示VaR和CVaR表格
        st.table(pd.DataFrame(var_data))
        
        # 下载分析报告
        if st.button("导出分析报告"):
            report = pd.DataFrame([metrics])
            csv = report.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name=f"performance_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"绩效分析过程中发生错误: {str(e)}")
        st.exception(e)
        
    # 在底部添加免责声明
    st.markdown("---")
    st.caption("本网站的信息仅供参考，不构成任何投资建议。")

if __name__ == "__main__":
    render_performance_analysis() 