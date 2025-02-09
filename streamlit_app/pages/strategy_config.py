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
            ["双均线交叉", "MACD金叉死叉", "RSI超买超卖", "布林带突破"],
            index=1  # 默认选择"MACD金叉死叉"
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
                default=["MACD金叉"],  # 默认选中MACD金叉
                key="buy_indicators"
            )
            
            # 添加指标的逻辑关系
            if len(buy_indicators) > 1:
                buy_logic = st.radio(
                    "条件关系",
                    ["AND (所有条件都满足)", "OR (满足任意条件)"],
                    key="buy_logic"
                )
            
            # 自定义买入条件（禁用）
            custom_buy_condition = st.text_input(
                "自定义买入条件（开发中）",
                key="custom_buy_condition",
                disabled=True
            )
        
        with sell_col:
            st.markdown("##### 卖出条件")
            
            # 技术指标选择（卖出）
            sell_indicators = st.multiselect(
                "选择技术指标",
                ["MACD死叉", "RSI超买", "MA交叉向下", "布林带上轨"],
                default=["MACD死叉"],  # 默认选中MACD死叉
                key="sell_indicators"
            )
            
            # 添加指标的逻辑关系
            if len(sell_indicators) > 1:
                sell_logic = st.radio(
                    "条件关系",
                    ["AND (所有条件都满足)", "OR (满足任意条件)"],
                    key="sell_logic"
                )
            
            # 自定义卖出条件（禁用）
            custom_sell_condition = st.text_input(
                "自定义卖出条件（开发中）",
                key="custom_sell_condition",
                disabled=True
            )
        
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
            with col_vol2:
                is_full_position = st.checkbox("满仓", value=True)
            with col_vol1:
                if is_full_position:
                    # 如果选择了满仓，计算最大可交易手数
                    if selected_stock:
                        # 加载股票数据
                        stock_data = loader.load_daily_data(selected_stock.split('.')[0])
                        if stock_data is not None and not stock_data.empty:
                            # 获取开始日期最近的收盘价
                            start_datetime = pd.to_datetime(start_date)
                            filtered_data = stock_data[stock_data['trade_date'] >= start_datetime]
                            
                            if filtered_data.empty:
                                st.error(f"在{start_date}之后没有找到交易数据，请选择更早的开始日期")
                                fixed_volume = 100
                            else:
                                closest_price = filtered_data['close'].iloc[0]
                                
                                # 计算最大可交易手数
                                # 考虑手续费和滑点的成本
                                total_cost_rate = commission_rate + slippage
                                max_volume = int((initial_capital * (1 - total_cost_rate)) / (closest_price * 100)) * 100
                                
                                fixed_volume = st.number_input(
                                    "每次交易手数（自动计算）",
                                    min_value=100,
                                    value=max_volume,
                                    step=100,
                                    disabled=True
                                )
                                st.caption(f"基于初始资金 {initial_capital:,.0f} 元")
                                st.caption(f"最近交易日收盘价 {closest_price:.2f} 元")
                                st.caption(f"考虑成本后可交易 {max_volume:,d} 股")
                        else:
                            st.error("无法获取股票数据，请检查股票代码或选择其他股票")
                            fixed_volume = 100
                    else:
                        fixed_volume = st.number_input(
                            "每次交易手数（请先选择股票）",
                            min_value=100,
                            value=100,
                            step=100,
                            disabled=True
                        )
                else:
                    fixed_volume = st.number_input(
                        "每次交易手数",
                        min_value=100,
                        value=100,
                        step=100
                    )
        elif position_type == "固定资金":
            fixed_amount = st.number_input("每次交易金额", min_value=1000, value=10000)
        else:
            position_ratio = st.slider("资金使用比例", 0.0, 1.0, 0.3)
        
        # 提交按钮区域
        col_submit1, col_submit2, col_submit3, col_submit4 = st.columns(4)
        
        with col_submit1:
            submitted = st.form_submit_button("开始回测")
            
        with col_submit2:
            ai_submitted = st.form_submit_button(
                "AI回测（开发中）",
                disabled=True
            )
            
        if submitted:
            # 验证必填字段
            if not selected_stock:
                st.error("请选择股票")
                return
                
            if start_date >= end_date:
                st.error("开始日期必须早于结束日期")
                return
                
            if initial_capital <= 0:
                st.error("初始资金必须大于0")
                return
                
            # 保存策略配置
            try:
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
                    if fast_period >= slow_period:
                        st.error("快线周期必须小于慢线周期")
                        return
                    strategy_config.update({
                        "strategy_params": {
                            "fast_period": fast_period,
                            "slow_period": slow_period
                        }
                    })
                elif strategy_type == "MACD金叉死叉":
                    if fast_ema >= slow_ema:
                        st.error("快线EMA必须小于慢线EMA")
                        return
                    strategy_config.update({
                        "strategy_params": {
                            "fast_ema": fast_ema,
                            "slow_ema": slow_ema,
                            "signal_period": signal_period
                        }
                    })
                elif strategy_type == "RSI超买超卖":
                    if oversold >= overbought:
                        st.error("超卖阈值必须小于超买阈值")
                        return
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
                    if fixed_amount <= 0:
                        st.error("交易金额必须大于0")
                        return
                    strategy_config["position_params"] = {"fixed_amount": fixed_amount}
                else:
                    if position_ratio <= 0 or position_ratio > 1:
                        st.error("资金使用比例必须在0到1之间")
                        return
                    strategy_config["position_params"] = {"position_ratio": position_ratio}
                
                # 将配置保存到session state
                st.session_state["strategy_config"] = strategy_config
                
                # 设置跳转标志
                st.session_state["should_redirect"] = True
                st.session_state["redirect_page"] = "回测分析"
                
                # 显示成功消息并自动跳转
                st.success("策略配置已保存，正在跳转到回测分析页面...")
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"保存策略配置时发生错误: {str(e)}")
                st.exception(e)
            
    # 在底部添加免责声明
    st.markdown("---")
    st.caption("本网站的信息仅供参考，不构成任何投资建议。")

if __name__ == "__main__":
    render_strategy_config() 