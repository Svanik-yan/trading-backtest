import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MovingAverageCrossStrategy(BaseStrategy):
    def __init__(self, data, fast_period=5, slow_period=20, **kwargs):
        super().__init__(data, **kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self):
        """生成双均线交叉信号"""
        # 计算快慢均线
        fast_ma = self.data['close'].rolling(self.fast_period).mean()
        slow_ma = self.data['close'].rolling(self.slow_period).mean()
        
        # 生成交易信号
        signals = pd.Series(0, index=self.data.index)
        signals[fast_ma > slow_ma] = 100  # 做多信号
        signals[fast_ma < slow_ma] = 0   # 平仓信号
        
        return signals

class MACDStrategy(BaseStrategy):
    def __init__(self, data, fast_ema=12, slow_ema=26, signal_period=9, **kwargs):
        super().__init__(data, **kwargs)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.signal_period = signal_period
        
    def generate_signals(self):
        """生成MACD金叉死叉信号"""
        # 计算MACD
        exp1 = self.data['close'].ewm(span=self.fast_ema, adjust=False).mean()
        exp2 = self.data['close'].ewm(span=self.slow_ema, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        
        # 生成交易信号
        signals = pd.Series(0, index=self.data.index)
        signals[macd > signal] = 100  # 金叉做多
        signals[macd < signal] = 0   # 死叉平仓
        
        return signals

class RSIStrategy(BaseStrategy):
    def __init__(self, data, rsi_period=14, overbought=70, oversold=30, **kwargs):
        super().__init__(data, **kwargs)
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """生成RSI超买超卖信号"""
        # 计算RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 生成交易信号
        signals = pd.Series(0, index=self.data.index)
        signals[rsi < self.oversold] = 100  # 超卖做多
        signals[rsi > self.overbought] = 0  # 超买平仓
        
        return signals

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, data, bb_period=20, bb_std=2.0, **kwargs):
        super().__init__(data, **kwargs)
        self.bb_period = bb_period
        self.bb_std = bb_std
        
    def generate_signals(self):
        """生成布林带突破信号"""
        # 计算布林带
        rolling_mean = self.data['close'].rolling(window=self.bb_period).mean()
        rolling_std = self.data['close'].rolling(window=self.bb_period).std()
        upper_band = rolling_mean + (rolling_std * self.bb_std)
        lower_band = rolling_mean - (rolling_std * self.bb_std)
        
        # 生成交易信号
        signals = pd.Series(0, index=self.data.index)
        signals[self.data['close'] < lower_band] = 100  # 下轨做多
        signals[self.data['close'] > upper_band] = 0    # 上轨平仓
        
        return signals

def create_strategy(strategy_type, data, **kwargs):
    """策略工厂函数"""
    strategy_map = {
        "双均线交叉": MovingAverageCrossStrategy,
        "MACD金叉死叉": MACDStrategy,
        "RSI超买超卖": RSIStrategy,
        "布林带突破": BollingerBandsStrategy
    }
    
    if strategy_type not in strategy_map:
        raise ValueError(f"不支持的策略类型: {strategy_type}")
        
    strategy_class = strategy_map[strategy_type]
    return strategy_class(data, **kwargs) 