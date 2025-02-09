import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import DataLoader

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
        
        # 模拟生成交易记录
        trades = pd.DataFrame({
            'trade_date': pd.date_range(start=config['start_date'], end=config['end_date'], freq='B')[:20],
            'type': ['买入', '卖出'] * 10,
            'price': [100 + i * 0.1 for i in range(20)],
            'volume': [100] * 20,
            'amount': [10000 + i * 10 for i in range(20)],
            'commission': [30] * 20,
            'profit': [-30] + [100 * (i % 5) for i in range(19)]
        })
        
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
            filtered_trades = filtered_trades.sort_values('trade_date', ascending=False)
        elif sort_by == '按时间升序':
            filtered_trades = filtered_trades.sort_values('trade_date', ascending=True)
        elif sort_by == '按收益降序':
            filtered_trades = filtered_trades.sort_values('profit', ascending=False)
        else:
            filtered_trades = filtered_trades.sort_values('profit', ascending=True)
        
        # 格式化数据
        display_trades = filtered_trades.copy()
        display_trades['trade_date'] = display_trades['trade_date'].dt.strftime('%Y-%m-%d')
        display_trades['price'] = display_trades['price'].apply(lambda x: f"¥{x:,.2f}")
        display_trades['amount'] = display_trades['amount'].apply(lambda x: f"¥{x:,.2f}")
        display_trades['commission'] = display_trades['commission'].apply(lambda x: f"¥{x:,.2f}")
        display_trades['profit'] = display_trades['profit'].apply(lambda x: f"¥{x:,.2f}")
        
        # 显示交易记录
        st.dataframe(
            display_trades,
            use_container_width=True
        )
        
        # 收益分布图
        st.subheader("收益分布")
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=filtered_trades['profit'],
            name="收益分布",
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
        
        fig.update_layout(
            title="交易收益分布",
            yaxis_title="收益(¥)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 导出功能
        if st.button("导出交易记录"):
            # 转换日期格式为字符串
            export_trades = filtered_trades.copy()
            export_trades['trade_date'] = export_trades['trade_date'].dt.strftime('%Y-%m-%d')
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