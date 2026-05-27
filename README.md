<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/ECharts-5.5%2B-AA344D?style=for-the-badge&logo=apacheecharts&logoColor=white" alt="ECharts">
  <img src="https://img.shields.io/badge/MySQL-8.0%2B-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/DeepSeek-Text--to--SQL-4F46E5?style=for-the-badge" alt="DeepSeek AI">
  <img src="https://img.shields.io/badge/Status-Defense%20Passed-22C55E?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Status">
</p>

<h1 align="center">校园外卖两段式配送数据库系统</h1>

<p align="center">
  <strong>Campus Delivery Two-Stage Distribution Database System</strong><br>
  期末答辩项目 · Flask + ECharts + MySQL + DeepSeek AI 实时监控大屏
</p>

---

## 项目概述

本项目设计并实现了一个**校园外卖两段式配送数据库系统**，融合了数据库工程、实时数据可视化和 AI 自然语言查询能力：

| 核心功能 | 说明 |
|---------|------|
| **两段式配送模型** | 干线骑手（商家到寄存点）+ 楼栋骑手（寄存点到宿舍），解决校园外卖"最后 500 米"难题 |
| **高并发防超卖机制** | MySQL 行级锁（`SELECT ... FOR UPDATE`）+ 触发器双重保障，高并发下单安全扣库存 |
| **全生命周期状态机** | 6 种精细化的订单状态流转，双骑手复合追踪，全流程可视化 |
| **实时数据大屏** | Flask + 原生 ECharts 前端，深色主题专业监控大屏，30秒自动刷新 |
| **双模式数据查询** | 实时模式（今天数据动态刷新）+ 历史模式（过去数据全部已完成统计） |
| **AI 智能数据查询** | 集成 DeepSeek Text-to-SQL：输入中文问题，自动生成 SQL 并返回结果表格 |

---

## 项目结构

```
campus_delivery_project/
├── app.py                       # Flask 后端 + API 接口 + 内嵌 HTML 大屏（主入口）
├── dashboard_app.py             # 启动器（等价于 python app.py）
├── db.py                        # MySQL 连接池模块
├── campus_delivery_db.sql       # 完整数据库建库脚本（DDL + 存储过程 + 触发器 + 视图 + 种子数据）
├── reinit_db.py                 # Python 版数据库重建脚本
├── generate_mock_data.py        # 模拟数据生成器（100学生/20商家/5000订单，历史全Completed + 今日实时状态）
├── requirements.txt             # Python 依赖列表
├── .env                         # 环境变量配置（不提交 Git）
└── README.md                    # 项目说明文档
```

---

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+
- DeepSeek API Key（可选，用于 AI 助手）

### 第一步：配置数据库

```bash
# 方式一：SQL 脚本
mysql -u root -p < campus_delivery_db.sql

# 方式二：Python 脚本
python reinit_db.py
```

### 第二步：配置环境变量

编辑 `.env` 文件：
```ini
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=campus_delivery_db
MYSQL_CHARSET=utf8mb4

# 可选：DeepSeek AI
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

### 第四步：生成模拟数据

```bash
python generate_mock_data.py
```

生成 5000 条订单：3500 条历史（全部 Completed）+ 1500 条今日（实时配送状态）。

### 第五步：启动大屏

```bash
python app.py
```

浏览器访问 **http://localhost:5000**

---

## 大屏功能

| 模块 | 功能 | 技术实现 |
|------|------|----------|
| **时间范围切换** | 今天 / 近7天 / 近30天 / 本月 / 全部，图表联动 | JS fetch API + 动态 SQL |
| **KPI 指标卡** | 今日订单、营业额、在途骑手、活跃商家、爆仓预警 | 5 卡片布局 + 爆仓红色呼吸灯 |
| **订单状态分布** | 今日实时配送状态环形图 | ECharts 环形饼图 |
| **近期订单流水** | 最新 15 条订单，彩色状态标签 | 原生 HTML 表格 + CSS 标签 |
| **寄存点饱和度监控** | 12 个寄存点横向柱状图 + 爆仓预警线 | ECharts 条件着色 + markLine |
| **商户销售排行** | Top 10 商户横向柱状图 | ECharts 蓝色渐变柱状图 |
| **时段订单分布** | 各时段订单量柱状图 + 客单价折线 | ECharts 双轴混合图 |
| **数据明细查询** | Tab 切换查看商户/学生/菜品/骑手/寄存点 | 页面内 Table 直接展示 |
| **AI 智能数据助手** | 中文问题 → SQL → 结果表格 | DeepSeek Text-to-SQL |

### 实时 vs 历史双模式

- **点"今天"**：红色脉冲灯亮，30 秒自动刷新，显示配送中/寄存待取等实时状态
- **点"近7天/30天/全部"**：脉冲灯熄，切换为历史模式，所有订单显示已完成（外卖时效性）

---

## 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.8+** | 后端逻辑 |
| **Flask** | Web 服务器 + REST API |
| **ECharts 5.5** | 前端图表渲染（CDN 引入） |
| **MySQL 8.0+** | 关系型数据库 |
| **DeepSeek Chat** | AI Text-to-SQL |
| **Pandas** | 数据处理 |
| **PyMySQL + DBUtils** | 数据库连接池 |
| **Faker** | 模拟数据生成 |
| **python-dotenv** | 环境变量管理 |

---

<p align="center">
  校园外卖两段式配送数据库系统 · 期末答辩项目<br>
  Flask + ECharts + MySQL + DeepSeek AI · v4.0
</p>
