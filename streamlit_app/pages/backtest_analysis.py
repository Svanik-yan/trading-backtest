import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
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

def render_backtest_analysis():
    st.title("回测分析")
    
    # 检查是否有策略配置
    if 'strategy_config' not in st.session_state:
        st.warning("请先在策略配置页面设置交易策略")
        return
        
    if "backtest_results" not in st.session_state:
        st.info("正在运行策略回测...")
        
        try:
            # 获取策略配置
            config = st.session_state["strategy_config"]
            
            # 加载股票数据
            loader = DataLoader()
            stock_data = loader.load_daily_data(config['stock_code'].split('.')[0])
            
            if stock_data is None or stock_data.empty:
                st.error("无法加载股票数据，请检查股票代码是否正确")
                return
                
            # 确保数据按日期排序
            stock_data = stock_data.sort_values('trade_date')
            stock_data.set_index('trade_date', inplace=True)
            
            # 创建并运行策略
            strategy = create_strategy(
                config['strategy_type'],
                stock_data,
                **{k: v for k, v in config.items() if k not in ['strategy_type', 'stock_code', 'start_date', 'end_date']}
            )
            
            # 运行回测
            results = strategy.run_backtest()
            
            # 保存回测结果到session state
            st.session_state["backtest_results"] = results
            st.experimental_rerun()
            
        except Exception as e:
            st.error(f"运行回测时发生错误: {str(e)}")
            st.exception(e)
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
            
        # 创建选项卡
        tab1, tab2, tab3 = st.tabs(["回测概览", "交易记录", "绩效分析"])
        
        with tab1:
            render_overview_tab(results, config)
            
        with tab2:
            render_trades_tab(results, config)
            
        with tab3:
            render_performance_tab(results, config)
            
    except Exception as e:
        st.error(f"分析过程中发生错误: {str(e)}")
        st.exception(e)
        
    # 在底部添加免责声明
    st.markdown("---")
    st.caption("本网站的信息仅供参考，不构成任何投资建议。")

def render_overview_tab(results, config):
    """渲染回测概览选项卡"""
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

def render_trades_tab(results, config):
    """渲染交易记录选项卡"""
    if not results.get('trades') or len(results['trades']) == 0:
        st.warning("没有找到交易记录")
        return
        
    trades = pd.DataFrame(results['trades'])
    
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
    
    # 添加样式
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] td:nth-child(1) {
        font-weight: bold;
    }
    [data-testid="stDataFrame"] td:nth-child(1):contains("买入") {
        color: #ff4b4b !important;
    }
    [data-testid="stDataFrame"] td:nth-child(1):contains("卖出") {
        color: #00c853 !important;
    }
    [data-testid="stDataFrame"] td {
        text-align: right;
    }
    [data-testid="stDataFrame"] th {
        text-align: center;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 重命名列以匹配所需格式
    display_trades = display_trades.rename(columns={
        'date': '交易时间',
        'type': '交易类型',
        'price': '价格',
        'volume': '数量',
        'amount': '金额',
        'profit': '收益率'
    })
    
    # 格式化数据
    display_trades['交易时间'] = pd.to_datetime(display_trades['交易时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
    display_trades['价格'] = display_trades['价格'].apply(lambda x: f"{x:.2f}")
    display_trades['数量'] = display_trades['数量'].astype(int)  # 确保数量为整数
    display_trades['金额'] = display_trades['金额'].apply(lambda x: f"¥{x:,.2f}")
    
    # 计算收益率和总资产
    current_equity = config['initial_capital']
    prev_equity = current_equity  # 初始化前一次的总资产
    
    for idx, row in display_trades.iterrows():
        amount = float(row['金额'].replace('¥', '').replace(',', ''))
        if row['交易类型'] == '买入':
            current_equity -= amount
            profit = 0
        else:  # 卖出
            current_equity += amount
            profit = amount - float(filtered_trades.iloc[idx]['amount'])  # 使用原始数据计算收益
        
        # 计算增长率
        growth_rate = ((current_equity - prev_equity) / prev_equity * 100) if prev_equity != 0 else 0.0
        display_trades.at[idx, '增长率'] = growth_rate
        
        # 更新总资产和前一次总资产
        display_trades.at[idx, '总资产'] = current_equity
        display_trades.at[idx, 'profit'] = profit  # 保存收益用于后续计算
        prev_equity = current_equity  # 更新前一次总资产
    
    # 格式化收益率、增长率和总资产显示
    display_trades['收益率'] = display_trades.apply(
        lambda row: f"{(row['profit'] / float(row['金额'].replace('¥', '').replace(',', '')) * 100):.2f}%" if row['交易类型'] == '卖出' else "0.00%",
        axis=1
    )
    display_trades['增长率'] = display_trades['增长率'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "0.00%")
    display_trades['总资产'] = display_trades['总资产'].apply(lambda x: f"¥{x:,.2f}")
    
    # 删除临时的profit列
    display_trades = display_trades.drop('profit', axis=1)
    
    # 设置列顺序
    columns_order = ['交易类型', '价格', '数量', '金额', '收益率', '增长率', '总资产', '交易时间']
    display_trades = display_trades[columns_order]
    
    # 使用st.dataframe显示表格，添加样式
    st.dataframe(
        display_trades,
        use_container_width=True,
        hide_index=True,
        column_config={
            "交易类型": st.column_config.Column(
                width="small",
                help="买入或卖出交易",
            ),
            "价格": st.column_config.NumberColumn(
                width="small",
                help="交易价格",
                format="%.2f"
            ),
            "数量": st.column_config.NumberColumn(
                width="medium",
                help="交易数量",
                format=None  # 移除格式化，使用原始整数
            ),
            "金额": st.column_config.NumberColumn(
                width="medium",
                help="交易金额",
                format="¥%,.2f"
            ),
            "收益率": st.column_config.Column(
                width="small",
                help="交易收益率"
            ),
            "增长率": st.column_config.Column(
                width="small",
                help="总资产增长率"
            ),
            "总资产": st.column_config.NumberColumn(
                width="medium",
                help="交易后总资产",
                format="¥%,.2f"
            ),
            "交易时间": st.column_config.DatetimeColumn(
                width="medium",
                help="交易发生时间",
                format="YYYY-MM-DD HH:mm:ss"
            )
        }
    )

def render_performance_tab(results, config):
    """渲染绩效分析选项卡"""
    equity_curve = results['equity_curve']
    daily_returns = equity_curve.pct_change().dropna()
    
    # 计算绩效指标
    metrics = calculate_performance_metrics(daily_returns)
    
    # 显示绩效指标
    st.subheader("绩效指标")
    col1, col2, col3 = st.columns(3)
    
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

if __name__ == "__main__":
    render_backtest_analysis() 