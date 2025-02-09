# 股票策略回测系统

一个简单易用的股票策略回测H5应用，让无编程经验的投资者也能快速验证自己的交易策略。

## 功能特点

- 简单直观的策略配置界面
- 灵活的择时设置
- 可视化的回测结果展示
- AI策略分析与评分
- 完全基于H5，无需安装，随时可用

## 已完成功能

### 数据采集模块
- [x] 股票列表获取与更新
- [x] 日线历史数据下载 (已完成1000+支股票)
- [x] 30分钟数据采集
- [x] 实时行情数据接口对接
- [x] 数据自动更新机制

### 策略回测模块
- [x] 策略参数配置界面
- [x] 时间周期设置
- [x] 交易成本计算
- [x] 回测引擎核心逻辑
- [x] 回测结果分析

### 可视化展示
- [x] K线图表展示
- [x] 交易记录明细
- [x] 收益率曲线
- [x] 策略绩效分析
- [x] 热力图分析

### 实时监控
- [x] 实时行情展示
- [x] 策略实时信号
- [x] 持仓盈亏统计

## 技术栈

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Plotly
- Tushare (股票数据API)

## 项目结构

```
├── public/               # 静态资源
│   └── daily_stock_data/ # 股票历史数据
├── streamlit_app/       # 应用源代码
│   ├── pages/          # 页面组件
│   ├── strategies/     # 策略实现
│   └── utils/          # 工具函数
├── requirements.txt    # Python依赖
├── setup.sh           # Streamlit配置脚本
└── Procfile          # 部署配置文件
```

## 本地开发

1. 克隆仓库
```bash
git clone [repository-url]
cd stock-backtest
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
streamlit run streamlit_app/app.py
```

## 部署到云平台

### Streamlit Cloud

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用GitHub账号登录
3. 选择此仓库和主分支
4. 点击"Deploy"按钮

### Heroku

1. 安装 Heroku CLI
2. 登录 Heroku
```bash
heroku login
```

3. 创建应用
```bash
heroku create your-app-name
```

4. 设置环境变量
```bash
heroku config:set TUSHARE_TOKEN=your_token
```

5. 部署应用
```bash
git push heroku main
```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交之前，请确保：

1. 代码遵循项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 本地测试通过

## 许可证

MIT License 