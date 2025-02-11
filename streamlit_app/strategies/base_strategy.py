from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    def __init__(self, data, initial_capital=1000000, commission_rate=0.0003, slippage=0.002, price_type="收盘价", **kwargs):
        """
        初始化策略基类
        
        参数:
            data (pd.DataFrame): 包含OHLCV数据的DataFrame
            initial_capital (float): 初始资金
            commission_rate (float): 手续费率
            slippage (float): 滑点率
            price_type (str): 交易价格类型，"收盘价"或"开盘价"
        """
        self.data = data
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.price_type = price_type
        self.position = 0
        self.cash = initial_capital
        self.trades = []
        
    @abstractmethod
    def generate_signals(self):
        """
        生成交易信号
        
        返回:
            pd.Series: 包含每个时间点的仓位信号(0-100)的Series
        """
        pass
        
    def calculate_trade_price(self, price, is_buy):
        """
        计算考虑滑点的成交价格
        
        参数:
            price (float): 基准价格
            is_buy (bool): 是否为买入
            
        返回:
            float: 考虑滑点后的成交价格
        """
        slippage_factor = 1 + self.slippage if is_buy else 1 - self.slippage
        return price * slippage_factor
        
    def calculate_commission(self, price, volume):
        """
        计算交易手续费
        
        参数:
            price (float): 成交价格
            volume (float): 成交数量
            
        返回:
            float: 手续费金额
        """
        return price * volume * self.commission_rate
        
    def execute_trade(self, date, price, target_position):
        """
        执行交易
        
        参数:
            date (pd.Timestamp): 交易日期
            price (float): 基准价格
            target_position (float): 目标仓位
            
        返回:
            float: 交易产生的收益(可能为负)
        """
        if target_position == self.position:
            return 0
            
        # 计算需要交易的数量
        volume = abs(target_position - self.position)
        is_buy = target_position > self.position
        
        # 计算实际成交价格
        trade_price = self.calculate_trade_price(price, is_buy)
        
        # 计算手续费
        commission = self.calculate_commission(trade_price, volume)
        
        # 计算交易金额
        trade_amount = trade_price * volume
        
        # 验证资金和持仓
        if is_buy:
            # 买入时验证资金是否足够
            total_cost = trade_amount + commission
            if total_cost > self.cash:
                return 0  # 资金不足，放弃交易
        else:
            # 卖出时验证持仓是否足够
            if volume > self.position:
                return 0  # 持仓不足，放弃交易
        
        # 更新现金和仓位
        if is_buy:
            self.cash -= (trade_amount + commission)
            self.position = target_position
        else:
            self.cash += (trade_amount - commission)
            self.position = target_position
            
        # 记录交易
        self.trades.append({
            'date': date,
            'type': '买入' if is_buy else '卖出',
            'price': trade_price,
            'volume': volume,
            'amount': trade_amount,
            'commission': commission,
            'profit': -commission  # 初始利润为负的手续费
        })
        
        return -commission
        
    def run_backtest(self):
        """
        运行回测
        
        返回:
            dict: 包含回测结果的字典，包括:
                - equity_curve: 权益曲线
                - trades: 交易记录列表
        """
        # 生成交易信号
        signals = self.generate_signals()
        
        # 初始化结果
        equity_curve = pd.Series(index=self.data.index, dtype=float)
        equity_curve.iloc[0] = self.initial_capital
        
        # 遍历每个交易日
        for i in range(1, len(self.data)):
            date = self.data.index[i]
            # 根据设置选择使用开盘价或收盘价
            price = self.data['open'].iloc[i] if self.price_type == "开盘价" else self.data['close'].iloc[i]
            
            # 获取目标仓位
            signal = signals.iloc[i]
            if signal > 0:  # 买入信号
                # 计算最大可买入数量（考虑手续费）
                max_shares = int(self.cash / (price * (1 + self.slippage + self.commission_rate)))
                target_shares = max_shares if self.position == 0 else self.position
            else:  # 卖出信号
                target_shares = 0  # 满仓卖出
            
            # 执行交易
            profit = self.execute_trade(date, price, target_shares)
            
            # 计算当前持仓市值
            position_value = self.position * price
            
            # 更新权益曲线
            equity_curve.iloc[i] = self.cash + position_value
            
            # 更新最后一笔交易的收益
            if self.trades and i > 0:
                prev_price = self.data['close'].iloc[i-1]
                price_change = price - prev_price
                position_profit = self.position * price_change
                self.trades[-1]['profit'] += position_profit
        
        # 确保交易记录不为空
        if not self.trades:
            self.trades = []  # 确保返回空列表而不是None
        
        return {
            'equity_curve': equity_curve,
            'trades': self.trades
        } 