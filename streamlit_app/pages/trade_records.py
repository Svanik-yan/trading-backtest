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
        
        # 更新布局，添加缩放和交互功能
        fig.update_layout(
            title=f"{config['stock_code']} K线图与交易点",
            yaxis_title="价格",
            xaxis_title="日期",
            height=600,
            xaxis_rangeslider_visible=True,  # 添加下方的范围滑块
            dragmode='zoom',  # 启用框选缩放
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            modebar=dict(
                add=[
                    'drawline',
                    'drawopenpath',
                    'drawclosedpath',
                    'drawcircle',
                    'drawrect',
                    'eraseshape'
                ]
            ),
            modebar_add=[
                'zoom',
                'pan',
                'select',
                'zoomIn',
                'zoomOut',
                'autoScale',
                'resetScale'
            ]
        )
        
        # 配置Y轴
        fig.update_yaxes(
            fixedrange=False,  # 允许Y轴缩放
            showgrid=True,     # 显示网格
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.3)'
        )
        
        # 配置X轴
        fig.update_xaxes(
            showgrid=True,     # 显示网格
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.3)',
            rangeslider=dict(visible=True)  # 显示下方的范围滑块
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
        
    # 在底部添加免责声明
    st.markdown("---")
    st.caption("本网站的信息仅供参考，不构成任何投资建议。")

if __name__ == "__main__":
    render_trade_records() 