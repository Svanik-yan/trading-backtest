import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_loader import DataLoader

def render_strategy_config():
    st.title("策略配置")
    
    # 初始化数据加载器
    loader = DataLoader()
    
    # 获取股票列表
    stock_list = loader.load_stock_list()
    
    if stock_list.empty:
        st.warning("未找到股票数据")
        return
        
    # 创建表单
    with st.form("strategy_config_form"):
        # 基本设置
        st.subheader("基本设置")
        col1, col2 = st.columns(2)
        
        with col1:
            # 股票选择，不设置默认值
            selected_stock = st.selectbox(
                "选择股票",
                options=[""] + stock_list['ts_code'].tolist(),
                format_func=lambda x: "" if x == "" else f"{x} - {stock_list[stock_list['ts_code']==x]['name'].values[0]}"
            )
            
            # 回测周期 - 默认结束日期为今天，开始日期为一年前
            today = datetime.now()
            one_year_ago = today - timedelta(days=365)
            
            start_date = st.date_input(
                "开始日期",
                value=one_year_ago
            )
            end_date = st.date_input(
                "结束日期",
                value=today
            )
        
        with col2:
            # 资金设置
            initial_capital = st.number_input(
                "初始资金",
                min_value=1000,
                value=100000,
                step=1000
            )
            
            # 交易成本设置
            commission_rate = st.slider(
                "手续费率",
                min_value=0.0,
                max_value=0.01,
                value=0.0003,
                format="%0.4f"
            )
            slippage = st.slider(
                "滑点",
                min_value=0.0,
                max_value=0.01,
                value=0.0002,
                format="%0.4f"
            )
            
            # 成交价格设置
            price_type = st.radio(
                "成交价格",
                ["收盘价", "开盘价"],
                index=0  # 默认使用收盘价
            )
        
        # 策略参数设置
        st.subheader("策略参数")
        
        # 选择策略类型
        strategy_type = st.selectbox(
            "策略类型",
            ["双均线交叉", "MACD金叉死叉", "RSI超买超卖", "布林带突破"]
        )
        
        # 买入条件和卖出条件设置
        st.subheader("交易条件")
        buy_col, sell_col = st.columns(2)
        
        with buy_col:
            st.markdown("##### 买入条件")
            
            # 技术指标选择（买入）
            buy_indicators = st.multiselect(
                "选择技术指标",
                ["MACD金叉", "RSI超卖", "MA交叉向上", "布林带下轨"],
                key="buy_indicators"
            )
            
            # 添加指标的逻辑关系
            if len(buy_indicators) > 1:
                buy_logic = st.radio(
                    "条件关系",
                    ["AND (所有条件都满足)", "OR (满足任意条件)"],
                    key="buy_logic"
                )
            
            # 自定义买入条件
            custom_buy_condition = st.text_input("自定义买入条件", key="custom_buy_condition")
        
        with sell_col:
            st.markdown("##### 卖出条件")
            
            # 技术指标选择（卖出）
            sell_indicators = st.multiselect(
                "选择技术指标",
                ["MACD死叉", "RSI超买", "MA交叉向下", "布林带上轨"],
                key="sell_indicators"
            )
            
            # 添加指标的逻辑关系
            if len(sell_indicators) > 1:
                sell_logic = st.radio(
                    "条件关系",
                    ["AND (所有条件都满足)", "OR (满足任意条件)"],
                    key="sell_logic"
                )
            
            # 自定义卖出条件
            custom_sell_condition = st.text_input("自定义卖出条件", key="custom_sell_condition")
        
        # 根据策略类型显示不同的参数设置
        if strategy_type == "双均线交叉":
            col3, col4 = st.columns(2)
            with col3:
                fast_period = st.slider("快线周期", 1, 50, 5)
            with col4:
                slow_period = st.slider("慢线周期", 2, 100, 20)
                
        elif strategy_type == "MACD金叉死叉":
            col3, col4, col5 = st.columns(3)
            with col3:
                fast_ema = st.slider("快线EMA", 1, 50, 12)
            with col4:
                slow_ema = st.slider("慢线EMA", 2, 100, 26)
            with col5:
                signal_period = st.slider("信号周期", 1, 50, 9)
                
        elif strategy_type == "RSI超买超卖":
            col3, col4 = st.columns(2)
            with col3:
                rsi_period = st.slider("RSI周期", 1, 50, 14)
            with col4:
                overbought = st.slider("超买阈值", 50, 100, 70)
                oversold = st.slider("超卖阈值", 0, 50, 30)
                
        elif strategy_type == "布林带突破":
            col3, col4 = st.columns(2)
            with col3:
                bb_period = st.slider("布林带周期", 1, 50, 20)
            with col4:
                bb_std = st.slider("标准差倍数", 1.0, 3.0, 2.0)
        
        # 仓位管理
        st.subheader("仓位管理")
        position_type = st.radio(
            "仓位模式",
            ["固定手数", "固定资金", "资金百分比"]
        )
        
        if position_type == "固定手数":
            col_vol1, col_vol2 = st.columns([3, 1])
            with col_vol1:
                fixed_volume = st.number_input("每次交易手数", min_value=1, value=1)
            with col_vol2:
                is_full_position = st.checkbox("满仓", value=True)
        elif position_type == "固定资金":
            fixed_amount = st.number_input("每次交易金额", min_value=1000, value=10000)
        else:
            position_ratio = st.slider("资金使用比例", 0.0, 1.0, 0.3)
        
        # 提交按钮
        submitted = st.form_submit_button("开始回测")
        
        if submitted:
            # 保存策略配置
            strategy_config = {
                "stock_code": selected_stock,
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": initial_capital,
                "commission_rate": commission_rate,
                "slippage": slippage,
                "price_type": price_type,
                "strategy_type": strategy_type,
                "position_type": position_type,
                "buy_conditions": {
                    "indicators": buy_indicators,
                    "logic": buy_logic if len(buy_indicators) > 1 else None,
                    "custom": custom_buy_condition
                },
                "sell_conditions": {
                    "indicators": sell_indicators,
                    "logic": sell_logic if len(sell_indicators) > 1 else None,
                    "custom": custom_sell_condition
                }
            }
            
            # 根据策略类型添加特定参数
            if strategy_type == "双均线交叉":
                strategy_config.update({
                    "strategy_params": {
                        "fast_period": fast_period,
                        "slow_period": slow_period
                    }
                })
            elif strategy_type == "MACD金叉死叉":
                strategy_config.update({
                    "strategy_params": {
                        "fast_ema": fast_ema,
                        "slow_ema": slow_ema,
                        "signal_period": signal_period
                    }
                })
            elif strategy_type == "RSI超买超卖":
                strategy_config.update({
                    "strategy_params": {
                        "rsi_period": rsi_period,
                        "overbought": overbought,
                        "oversold": oversold
                    }
                })
            elif strategy_type == "布林带突破":
                strategy_config.update({
                    "strategy_params": {
                        "bb_period": bb_period,
                        "bb_std": bb_std
                    }
                })
            
            # 添加仓位管理参数
            if position_type == "固定手数":
                strategy_config["position_params"] = {
                    "fixed_volume": fixed_volume,
                    "is_full_position": is_full_position
                }
            elif position_type == "固定资金":
                strategy_config["position_params"] = {"fixed_amount": fixed_amount}
            else:
                strategy_config["position_params"] = {"position_ratio": position_ratio}
            
            # 将配置保存到session state
            st.session_state["strategy_config"] = strategy_config
            st.success("策略配置已保存，请前往回测分析页面查看结果")

if __name__ == "__main__":
    render_strategy_config() 