# -*- coding: utf-8 -*-
"""
==================================================================
项目名称：校园外卖两段式配送数据库系统 (campus_delivery_db)
文件名称：dashboard_app.py
功能描述：Streamlit 宽屏网格数据大屏（期末答辩展示）
          + AI 智能数据助手（DeepSeek Text-to-SQL）
设计风格：现代企业级数据大屏 · 玻璃态卡片 · 动态渐变 · 爆仓预警
适用环境：Python 3.8+ / streamlit / pymysql / pandas / matplotlib / openai
==================================================================
"""

import streamlit as st
import pandas as pd
import sys
import io

# ---- 解决 Windows 终端中文乱码 ----
if sys.platform == "win32":
    try:
        if sys.stdout.buffer and not sys.stdout.buffer.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if sys.stderr.buffer and not sys.stderr.buffer.closed:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        pass

import seaborn as sns
from datetime import datetime, timedelta
import os
import json
import traceback
from dotenv import load_dotenv
from openai import OpenAI

# ================================================================
# 加载 .env 文件
# ================================================================
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ================================================================
# 导入数据库连接池模块
# ================================================================
from db import get_connection, check_connection

# ---------------------------------------------------------------
# Matplotlib 中文字体配置
# ---------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams['axes.unicode_minus'] = False


def _setup_chinese_font():
    """配置 Matplotlib 中文字体"""
    _candidate_families = [
        "Microsoft YaHei", "SimHei", "Noto Sans SC",
        "Noto Sans CJK SC", "SimSun", "KaiTi", "FangSong",
    ]

    # 扫描 C:\Windows\Fonts 目录添加所有字体
    _font_dir = r"C:\Windows\Fonts"
    if os.path.isdir(_font_dir):
        for _f in fm.findSystemFonts(fontpaths=[_font_dir]):
            try:
                fm.fontManager.addfont(_f)
            except Exception:
                pass

    _found_family = None
    for _fam in _candidate_families:
        try:
            _fp = fm.FontProperties(family=_fam)
            _test_path = fm.findfont(_fp, fallback_to_default=False)
            if _test_path and os.path.exists(_test_path):
                _found_family = _fam
                break
        except Exception:
            continue

    if _found_family:
        plt.rcParams['font.sans-serif'] = [_found_family, 'DejaVu Sans', 'Arial']
        plt.rcParams['font.family'] = 'sans-serif'
        return fm.FontProperties(family=_found_family)
    else:
        for _f in fm.fontManager.ttflist:
            if _f.name in _candidate_families:
                plt.rcParams['font.sans-serif'] = [_f.name, 'DejaVu Sans']
                plt.rcParams['font.family'] = 'sans-serif'
                return fm.FontProperties(family=_f.name)
        return fm.FontProperties()


FONT_PROP = _setup_chinese_font()

# ================================================================
# DeepSeek AI 配置 — 从 .env 读取
# ================================================================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ---- 全局配色方案（现代企业级配色） ----
COLOR_PRIMARY = "#6366F1"
COLOR_ACCENT = "#06B6D4"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_BG = "#F1F5F9"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT = "#1E293B"
COLOR_TEXT_SEC = "#64748B"

# ---- Streamlit 页面配置 ----
st.set_page_config(
    page_title="校园外卖两段式配送 · 实时数据监控大屏",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- 自定义全局 CSS（现代企业级大屏风格） ----
st.markdown(f"""
<style>
    /* ========== 全局底色与字体 ========== */
    .stApp {{
        background: linear-gradient(180deg, #F1F5F9 0%, #E8ECF1 100%);
        font-family: "Microsoft YaHei", "Segoe UI", "Noto Sans SC", sans-serif;
    }}

    /* ========== 顶部标题栏 — 深色玻璃态 ========== */
    .header-container {{
        background: linear-gradient(135deg, #1E293B 0%, #334155 40%, #1E3A5F 100%);
        padding: 2.5rem 2rem 2rem;
        border-radius: 24px;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(30,41,59,0.35), 0 2px 8px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }}
    .header-container::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .header-container::after {{
        content: '';
        position: absolute;
        bottom: -30%;
        left: 5%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .header-title {{
        color: #F1F5F9;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .header-sub {{
        color: #94A3B8;
        text-align: center;
        font-size: 0.9rem;
        margin-top: 0.6rem;
        position: relative;
        z-index: 1;
    }}

    /* ========== KPI 指标卡片 — 玻璃态悬浮 ========== */
    .kpi-card {{
        background: {COLOR_CARD};
        padding: 1.4rem 1.2rem;
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04), 0 1px 4px rgba(0,0,0,0.06);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 20px 20px 0 0;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.06);
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }}
    .kpi-label {{
        font-size: 0.85rem;
        color: {COLOR_TEXT_SEC};
        margin-top: 0.3rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}

    /* ========== 图表卡片 — 清爽白底 ========== */
    .chart-card {{
        background: {COLOR_CARD};
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04), 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 1.2rem;
        transition: box-shadow 0.2s;
    }}
    .chart-card:hover {{
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }}
    .chart-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {COLOR_TEXT};
        margin-bottom: 1rem;
        padding-left: 0.8rem;
        border-left: 4px solid {COLOR_PRIMARY};
        letter-spacing: 0.5px;
    }}

    /* ========== AI 对话区域 ========== */
    .ai-chat-container {{
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }}
    .ai-message {{
        padding: 0.8rem 1rem;
        border-radius: 14px;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    .ai-message.user {{
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border-left: 4px solid {COLOR_PRIMARY};
        color: #1E293B;
    }}
    .ai-message.assistant {{
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid {COLOR_SUCCESS};
        color: #1E293B;
    }}
    .ai-message.sql {{
        background: #F8FAFC;
        border-left: 4px solid {COLOR_WARNING};
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 0.82rem;
        color: #334155;
        white-space: pre-wrap;
        overflow-x: auto;
    }}
    .ai-message.error {{
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 4px solid {COLOR_DANGER};
        color: #991B1B;
    }}

    /* ========== 页脚 ========== */
    .footer {{
        text-align: center;
        color: #94A3B8;
        font-size: 0.82rem;
        padding: 2rem 0 1rem;
        border-top: 1px solid #E2E8F0;
        margin-top: 2.5rem;
    }}

    /* ========== Streamlit 原生组件微调 ========== */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    .stSelectbox [data-baseweb="select"] {{
        border-radius: 12px !important;
    }}
    .stTextInput > div > div > input {{
        border-radius: 12px !important;
    }}
    div[data-testid="stExpander"] {{
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ================================================================
# 数据库连接与缓存查询
# ================================================================



def _get_date_option():
    """获取当前选中的时间范围选项"""
    return st.session_state.get("date_filter_opt", "全部数据")


def _build_date_filter_generic(table_alias="o", date_option=None):
    """根据选中的时间范围生成通用 SQL 条件，可指定表别名"""
    if date_option is None:
        date_option = _get_date_option()
    col = f"{table_alias}.created_at"
    today_sql = f"DATE({col}) = CURDATE()"
    week_sql = f"{col} >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    month_sql = f"{col} >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    month_cal = f"DATE_FORMAT({col}, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m')"
    mapping = {
        "今天": " AND " + today_sql,
        "最近 7 天": " AND " + week_sql,
        "最近 30 天": " AND " + month_sql,
        "本月": " AND " + month_cal,
        "全部数据": "",
    }
    return mapping.get(date_option, "")


@st.cache_data(ttl=60)
def load_pickup_analytics():
    """读取寄存点饱和度分析（查询视图 vw_pickup_point_analytics）"""
    conn = get_connection()
    try:
        sql = """
            SELECT 
                point_name,
                max_capacity,
                current_packages,
                saturation_pct,
                backlog_count
            FROM vw_pickup_point_analytics
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty and 'point_name' in df.columns:
            df['point_name'] = df['point_name'].astype(str)
        return df
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_merchant_sales_rank():
    """读取商户销售排行（查询视图 vw_merchant_sales_rank）"""
    conn = get_connection()
    try:
        sql = """
            SELECT 
                merchant_name,
                total_orders,
                total_sales,
                sales_rank
            FROM vw_merchant_sales_rank
            ORDER BY sales_rank
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_order_status_distribution(date_option="全部数据"):
    """读取订单状态分布（支持动态时间筛选）"""
    conn = get_connection()
    try:
        date_filter = _build_date_filter_generic("o", date_option)
        query = f"""
            SELECT o.order_status, COUNT(*) AS order_count
            FROM orders o
            WHERE 1=1 {date_filter}
            GROUP BY o.order_status
            ORDER BY order_count DESC
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_basic_stats(date_option="全部数据"):
    """读取基本统计指标（支持动态时间筛选）"""
    conn = get_connection()
    try:
        date_filter_orders = _build_date_filter_generic("o", date_option)
        stats = {}
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            stats["total_users"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM merchants")
            stats["total_merchants"] = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM orders o WHERE 1=1 {date_filter_orders}")
            stats["total_orders"] = cursor.fetchone()[0]
            cursor.execute(f"""
                SELECT IFNULL(SUM(o.total_amount), 0) 
                FROM orders o 
                WHERE o.order_status = 'Completed' {date_filter_orders}
            """)
            stats["total_revenue"] = cursor.fetchone()[0]
            # 在运骑手：骑手状态为 Delivering，或有关联的未完成订单
            cursor.execute("""
                SELECT COUNT(DISTINCT r.rider_id)
                FROM riders r
                WHERE r.status = 'Delivering'
                   OR r.rider_id IN (
                       SELECT stage1_rider_id FROM orders
                       WHERE order_status NOT IN ('Completed', 'Cancelled') AND stage1_rider_id IS NOT NULL
                       UNION
                       SELECT stage2_rider_id FROM orders
                       WHERE order_status NOT IN ('Completed', 'Cancelled') AND stage2_rider_id IS NOT NULL
                   )
            """)
            stats["active_riders"] = cursor.fetchone()[0]
            cursor.execute(f"""
                SELECT COUNT(*) FROM orders o 
                WHERE DATE(o.created_at) = CURDATE() {date_filter_orders}
            """)
            stats["today_orders"] = cursor.fetchone()[0]
        return stats
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_recent_orders(limit=10, date_option="全部数据"):
    """读取最近订单（支持动态时间筛选，查询 orders 表）
    使用 Pandas 的 .dt.strftime('%m-%d %H:%M') 正确格式化时间
    """
    conn = get_connection()
    try:
        date_filter = _build_date_filter_generic("o", date_option)
        query = f"""
            SELECT 
                o.order_id AS '订单号',
                u.username AS '学生',
                m.merchant_name AS '商家',
                o.total_amount AS '金额(元)',
                o.order_status AS '状态',
                o.created_at AS '下单时间_raw'
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN merchants m ON o.merchant_id = m.merchant_id
            WHERE 1=1 {date_filter}
            ORDER BY o.created_at DESC
            LIMIT {limit}
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty and '下单时间_raw' in df.columns:
            # 正确格式化：%M 是大写 M 表示分钟（Python 标准）
            df['下单时间'] = pd.to_datetime(df['下单时间_raw']).dt.strftime('%m-%d %H:%M')
            df = df.drop(columns=['下单时间_raw'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_time_period_distribution(date_option="全部数据"):
    """读取时段订单分布（支持动态时间筛选）"""
    conn = get_connection()
    try:
        date_filter = _build_date_filter_generic("o", date_option)
        query = f"""
            SELECT
                CASE
                    WHEN HOUR(o.created_at) BETWEEN 6 AND 8 THEN '06-09 早餐'
                    WHEN HOUR(o.created_at) BETWEEN 9 AND 10 THEN '09-11 上午'
                    WHEN HOUR(o.created_at) BETWEEN 11 AND 13 THEN '11-13 午餐高峰'
                    WHEN HOUR(o.created_at) BETWEEN 14 AND 16 THEN '14-17 下午'
                    WHEN HOUR(o.created_at) BETWEEN 17 AND 19 THEN '17-19 晚餐高峰'
                    WHEN HOUR(o.created_at) BETWEEN 20 AND 22 THEN '20-22 夜宵'
                    ELSE '其他时段'
                END AS time_period,
                COUNT(*) AS order_count,
                ROUND(AVG(o.total_amount), 2) AS avg_amount
            FROM orders o
            WHERE 1=1 {date_filter}
            GROUP BY time_period
            ORDER BY MIN(HOUR(o.created_at))
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_merchant_info():
    """读取商户信息列表（Pandas 格式化时间）"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                merchant_id AS '编号',
                merchant_name AS '店铺名称',
                phone AS '联系电话',
                rating AS '评分',
                created_at AS '入驻时间_raw'
            FROM merchants
            ORDER BY merchant_id
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty and '入驻时间_raw' in df.columns:
            df['入驻时间'] = pd.to_datetime(df['入驻时间_raw']).dt.strftime('%Y-%m-%d')
            df = df.drop(columns=['入驻时间_raw'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_student_info():
    """读取学生用户信息列表（Pandas 格式化时间）"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                user_id AS '学号',
                username AS '姓名',
                phone AS '手机号',
                dorm_building AS '宿舍楼栋',
                balance AS '校园卡余额(元)',
                created_at AS '注册时间_raw'
            FROM users
            ORDER BY user_id
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty and '注册时间_raw' in df.columns:
            df['注册时间'] = pd.to_datetime(df['注册时间_raw']).dt.strftime('%Y-%m-%d')
            df = df.drop(columns=['注册时间_raw'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_merchant_dishes():
    """读取所有菜品信息"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                d.dish_id AS '菜品编号',
                d.dish_name AS '菜品名称',
                d.price AS '单价(元)',
                d.stock AS '库存',
                m.merchant_name AS '所属商家'
            FROM dishes d
            JOIN merchants m ON d.merchant_id = m.merchant_id
            ORDER BY m.merchant_name, d.dish_id
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_rider_info():
    """读取骑手信息列表"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                rider_id AS '编号',
                rider_name AS '姓名',
                phone AS '联系电话',
                rider_type AS '分工',
                status AS '状态'
            FROM riders
            ORDER BY rider_id
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            # 将英文状态映射为中文
            type_map = {'Stage1_Trunk': '干线骑手', 'Stage2_Floor': '楼栋骑手'}
            status_map = {'Idle': '空闲', 'Delivering': '配送中', 'Offline': '离线'}
            df['分工'] = df['分工'].map(type_map).fillna(df['分工'])
            df['状态'] = df['状态'].map(status_map).fillna(df['状态'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_pickup_point_info():
    """读取寄存点信息列表"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                point_id AS '编号',
                point_name AS '站点名称',
                location AS '位置',
                capacity AS '最大容量',
                current_packages AS '当前在库'
            FROM pickup_points
            ORDER BY point_id
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df['饱和度'] = (df['当前在库'] / df['最大容量'] * 100).round(1).astype(str) + '%'
        return df
    finally:
        conn.close()



# ================================================================
# AI 智能数据助手 — DeepSeek Text-to-SQL
# ================================================================

DB_SCHEMA_DESCRIPTION = """
数据库名称：campus_delivery_db（校园外卖两段式配送系统）

表结构说明：

1. users（学生用户表）
   - user_id: 学生唯一ID (INT, PK)
   - username: 姓名 (VARCHAR)
   - phone: 手机号 (VARCHAR)
   - dorm_building: 宿舍楼栋 (VARCHAR, 如: 1期5栋)
   - room_number: 房间号 (VARCHAR)
   - balance: 校园卡钱包余额 (DECIMAL)
   - created_at: 注册时间 (TIMESTAMP)

2. merchants（商家信息表）
   - merchant_id: 商家唯一ID (INT, PK)
   - merchant_name: 店铺名称 (VARCHAR)
   - phone: 联系电话 (VARCHAR)
   - address: 档口地址 (VARCHAR)
   - rating: 商家评分 (DECIMAL, 1.0-5.0)
   - created_at: 入驻时间 (TIMESTAMP)

3. dishes（菜品表）
   - dish_id: 菜品唯一ID (INT, PK)
   - merchant_id: 所属商家ID (INT, FK)
   - dish_name: 菜品名称 (VARCHAR)
   - price: 单价 (DECIMAL)
   - stock: 当前实时库存 (INT)
   - status: 上架状态 (TINYINT, 0下架/1上架)

4. pickup_points（寄存中转点表）
   - point_id: 寄存点唯一ID (INT, PK)
   - point_name: 寄存点名称 (VARCHAR)
   - location: 具体位置 (VARCHAR)
   - capacity: 最大格子容积 (INT)
   - current_packages: 当前在库件数 (INT)

5. riders（两段式骑手表）
   - rider_id: 骑手唯一ID (INT, PK)
   - rider_name: 骑手姓名 (VARCHAR)
   - phone: 联系电话 (VARCHAR)
   - rider_type: 骑手分工 (ENUM: 'Stage1_Trunk'干线/'Stage2_Floor'楼栋)
   - status: 工作状态 (ENUM: 'Idle'空闲/'Delivering'配送中/'Offline'离线)

6. orders（订单主表 - 核心表）
   - order_id: 订单唯一流水号 (INT, PK)
   - user_id: 下单学生ID (INT, FK)
   - merchant_id: 下单商家ID (INT, FK)
   - pickup_point_id: 指派寄存点ID (INT, FK)
   - total_amount: 总金额 (DECIMAL)
   - order_status: 订单状态 (ENUM: 'Paid'/'Stage1_Assigned'/'Arrived_At_Point'/'Stage2_Assigned'/'Completed'/'Cancelled')
   - stage1_rider_id: 干线骑手ID (INT, FK, nullable)
   - stage2_rider_id: 楼栋骑手ID (INT, FK, nullable)
   - created_at: 下单时间 (TIMESTAMP)
   - stage1_completed_at: 干线送达时间 (TIMESTAMP, nullable)
   - stage2_completed_at: 最终送达时间 (TIMESTAMP, nullable)

7. order_items（订单明细表）
   - item_id: 明细项ID (INT, PK)
   - order_id: 关联订单ID (INT, FK)
   - dish_id: 关联菜品ID (INT, FK)
   - quantity: 购买数量 (INT)
   - price_at_order: 购买时单价快照 (DECIMAL)

重要视图：
- vw_pickup_point_analytics: 寄存点饱和度分析
- vw_merchant_sales_rank: 商户销售排行

注意事项：
- 查询时请使用中文别名
- 金额单位是元（人民币）
- 只允许执行 SELECT 查询，禁止修改数据
"""


def init_deepseek_client():
    """初始化 DeepSeek 客户端（超时 10 秒防止卡死）"""
    if not DEEPSEEK_API_KEY:
        return None
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        timeout=10,
    )


def ai_text_to_sql(user_question: str) -> dict:
    """
    将用户的中文自然语言问题转换为 SQL 并执行
    返回: {"success": bool, "sql": str, "result": list[dict], "error": str}
    """
    client = init_deepseek_client()
    if not client:
        return {
            "success": False,
            "sql": "",
            "result": [],
            "error": "DeepSeek API Key 未配置！请在 .env 文件中设置 DEEPSEEK_API_KEY"
        }

    system_prompt = f"""你是一个专业的 Text-to-SQL 助手。你的任务是将用户的中文问题转换为 MySQL SQL 查询语句。

数据库 Schema：
{DB_SCHEMA_DESCRIPTION}

要求：
1. 只生成 SELECT 查询语句，绝不生成 INSERT/UPDATE/DELETE/DROP/ALTER 等修改语句
2. 给字段起中文别名（使用 AS）
3. 如果问题涉及金额统计，注意只统计 order_status='Completed' 的已完成订单
4. 如果问题不明确，选择最合理的解释
5. 只返回 SQL 语句本身，不要加任何解释或 markdown 标记
6. SQL 语句要兼容 MySQL 8.0 语法"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.1,
            max_tokens=1000,
            timeout=10,
        )
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            return {
                "success": False,
                "sql": sql,
                "result": [],
                "error": "AI 生成的不是查询语句，已拦截执行"
            }

        # 二次安全检查：拦截危险关键字（INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/EXEC/SHUTDOWN）
        dangerous_keywords = [
            "INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ",
            "TRUNCATE ", "CREATE ", "EXEC ", "SHUTDOWN", "INTO OUTFILE",
            "INTO DUMPFILE", "LOAD DATA", "SET @", "@@",
        ]
        for kw in dangerous_keywords:
            if kw in sql_upper:
                return {
                    "success": False,
                    "sql": sql,
                    "result": [],
                    "error": f"检测到危险关键字 '{kw.strip()}'，已拦截执行"
                }

        # 检查是否含有分号（多语句注入防护）
        if ";" in sql.rstrip(";"):
            return {
                "success": False,
                "sql": sql,
                "result": [],
                "error": "检测到多条 SQL 语句（含分号），已拦截执行"
            }

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            result = df.to_dict(orient="records")
            return {
                "success": True,
                "sql": sql,
                "result": result,
                "columns": columns,
                "row_count": len(result),
                "error": ""
            }
        except Exception as e:
            return {
                "success": False,
                "sql": sql,
                "result": [],
                "error": f"SQL 执行错误：{str(e)}"
            }
        finally:
            conn.close()

    except Exception as e:
        return {
            "success": False,
            "sql": "",
            "result": [],
            "error": f"AI 调用失败：{str(e)}"
        }


# ================================================================
# 图表美化工具函数
# ================================================================

def style_axis(ax):
    """统一坐标轴美化"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors='#64748B', labelsize=10)


def render_kpi_row(stats):
    """渲染顶部 KPI 指标行"""
    kpi_items = [
        ("总订单量", f"{int(stats['total_orders']):,}", COLOR_PRIMARY),
        ("活跃商家", f"{int(stats['total_merchants'])} 家", COLOR_ACCENT),
        ("在途骑手", f"{int(stats['active_riders'])} 人", COLOR_WARNING),
        ("总营业额", f"¥{float(stats['total_revenue']):,.0f}", COLOR_SUCCESS),
    ]
    cols = st.columns(4)
    for col, (label, value, color) in zip(cols, kpi_items):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 3px solid {color};">
                <div style="width:10px;height:10px;border-radius:50%;background:{color};display:inline-block;margin-bottom:0.4rem;"></div>
                <div class="kpi-value" style="color: {color};">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_pickup_saturation_chart(df_points):
    """渲染寄存点饱和度柱状图 + 爆仓预警"""
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    names = df_points['point_name'].tolist()
    values = df_points['saturation_pct'].tolist()
    colors_bar = ['#10B981' if v < 60 else '#F59E0B' if v < 80 else '#EF4444' for v in values]
    bars = ax.bar(names, values, color=colors_bar, width=0.6,
                  edgecolor='white', linewidth=1.5, zorder=3)
    ax.axhline(y=80, color='#EF4444', linestyle='--', linewidth=2,
               alpha=0.5, label='Overload Threshold 80%', zorder=2)
    ax.axhline(y=60, color='#F59E0B', linestyle='--', linewidth=1.5,
               alpha=0.35, label='Warning Threshold 60%', zorder=2)
    for bar, v in zip(bars, values):
        color = '#EF4444' if v > 80 else '#475569'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2.5,
                f'{v:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=color,
                fontproperties=FONT_PROP)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontproperties=FONT_PROP, fontsize=9)
    ax.set_ylim(0, 110)
    style_axis(ax)
    ax.grid(axis='y', alpha=0.25, linestyle='-', linewidth=0.5, zorder=0, color='#CBD5E1')
    ax.legend(fontsize=8, loc='upper right', framealpha=0.95, prop=FONT_PROP,
              edgecolor='#E2E8F0', labelspacing=0.5)
    ax.set_ylabel('Saturation (%)', fontsize=10, color=COLOR_TEXT_SEC, fontproperties=FONT_PROP)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig, width='stretch')
    plt.close()

    overflow_points = df_points[df_points['saturation_pct'] > 80]
    if not overflow_points.empty:
        for _, row in overflow_points.iterrows():
            st.error(
                f"OVERLOAD: **{row['point_name']}** saturation {row['saturation_pct']:.1f}%, "
                f"used {int(row['current_packages'])}/{int(row['max_capacity'])}, "
                f"backlog {int(row['backlog_count'])}"
            )


def render_merchant_rank_chart(df_merchants):
    """渲染商户销售排行水平柱状图"""
    top10 = df_merchants.head(10).iloc[::-1].copy()
    top10['total_sales'] = top10['total_sales'].astype(float)
    top10['total_orders'] = top10['total_orders'].astype(int)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    import numpy as np
    n = len(top10)
    # 专业蓝色系渐变
    colors = [plt.cm.Blues(0.3 + 0.7 * i / n) for i in range(n)][::-1]
    bars = ax.barh(top10['merchant_name'], top10['total_sales'],
                   color=colors, edgecolor='white', linewidth=1.5, height=0.65, zorder=3)
    max_sales = top10['total_sales'].max()
    for bar, (_, row) in zip(bars, top10.iterrows()):
        w = bar.get_width()
        ax.text(w + max_sales * 0.015, bar.get_y() + bar.get_height()/2,
                f'¥{w:,.0f}  ({int(row["total_orders"])}单)',
                ha='left', va='center', fontsize=9, fontweight='600',
                color='#475569', fontproperties=FONT_PROP)
    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10['merchant_name'], fontproperties=FONT_PROP, fontsize=10)
    ax.set_xlim(0, max_sales * 1.3)
    style_axis(ax)
    ax.grid(axis='x', alpha=0.25, linestyle='-', linewidth=0.5, zorder=0, color='#CBD5E1')
    ax.set_xlabel('总销售额 (CNY)', fontsize=10, color=COLOR_TEXT_SEC, fontproperties=FONT_PROP)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig, width='stretch')
    plt.close()


def render_order_status_pie(df_status):
    """渲染订单状态分布环形饼图"""
    # 专业配色：蓝绿暖色系
    status_colors = {
        "Paid": "#94A3B8",
        "Stage1_Assigned": "#3B82F6",
        "Arrived_At_Point": "#8B5CF6",
        "Stage2_Assigned": "#06B6D4",
        "Completed": "#10B981",
        "Cancelled": "#EF4444",
    }
    status_labels = {
        "Paid": "已支付", "Stage1_Assigned": "干线配送",
        "Arrived_At_Point": "寄存待取", "Stage2_Assigned": "楼栋配送",
        "Completed": "已完成", "Cancelled": "已取消",
    }
    df_status['display_name'] = df_status['order_status'].map(status_labels)
    df_status['color'] = df_status['order_status'].map(status_colors)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_facecolor('#FFFFFF')
    colors_pie = df_status['color'].tolist()
    wedges, texts, autotexts = ax.pie(
        df_status['order_count'],
        labels=df_status['display_name'],
        autopct='%1.1f%%',
        colors=colors_pie,
        startangle=140,
        pctdistance=0.78,
        wedgeprops={'edgecolor': 'white', 'linewidth': 3},
        textprops={'fontsize': 9, 'color': '#475569', 'fontproperties': FONT_PROP},
    )
    for at in autotexts:
        at.set_fontweight('bold')
        at.set_fontsize(10)
        at.set_color('#1E293B')
    centre_circle = plt.Circle((0, 0), 0.48, fc='white', alpha=0.9)
    ax.add_artist(centre_circle)
    ax.text(0, 0, f'{df_status["order_count"].sum()}\nTotal',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#1E293B', fontproperties=FONT_PROP)
    plt.tight_layout()
    st.pyplot(fig, width='stretch')
    plt.close()


def render_time_period_chart(df_period):
    """渲染时段订单分布柱状图"""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    import numpy as np
    n = len(df_period)
    gradient = plt.cm.Blues(np.linspace(0.35, 0.9, n))
    bars = ax.bar(df_period['time_period'], df_period['order_count'],
                  color=gradient, width=0.55,
                  edgecolor='white', linewidth=2, zorder=3)
    for bar, (_, row) in zip(bars, df_period.iterrows()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(df_period['order_count']) * 0.02,
                f'{int(row["order_count"])}', ha='center', va='bottom',
                fontsize=10, fontweight='600', color='#475569',
                fontproperties=FONT_PROP)
    ax.set_xticks(range(len(df_period)))
    ax.set_xticklabels(df_period['time_period'], fontproperties=FONT_PROP, fontsize=9, rotation=25, ha='right')
    style_axis(ax)
    ax.grid(axis='y', alpha=0.25, linestyle='-', linewidth=0.5, zorder=0, color='#CBD5E1')
    ax.set_ylabel('订单量', fontsize=10, color=COLOR_TEXT_SEC, fontproperties=FONT_PROP)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig, width='stretch')
    plt.close()


def render_recent_orders_table(df_recent):
    """渲染近期订单流水表格"""
    import html as _html

    def _escape_html(val):
        """转义 HTML 特殊字符，防止 XSS 或渲染错乱"""
        return _html.escape(str(val))

    def style_status(s):
        color_map = {
            'Paid': ('已支付', '#F59E0B'),
            'Stage1_Assigned': ('干线配送中', '#3B82F6'),
            'Arrived_At_Point': ('已到寄存点', '#8B5CF6'),
            'Stage2_Assigned': ('楼栋配送中', '#06B6D4'),
            'Completed': ('已完成', '#22C55E'),
            'Cancelled': ('已取消', '#EF4444'),
        }
        label, color = color_map.get(s, (s, '#94A3B8'))
        return f'<span style="background:{color}20;color:{color};padding:2px 12px;border-radius:20px;font-size:0.8rem;font-weight:500;">{_escape_html(label)}</span>'

    html = '<table style="width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
    html += '<tr style="background:#F8FAFC;">'
    for col in df_recent.columns:
        html += f'<th style="padding:10px 12px;text-align:left;font-size:0.85rem;color:#64748B;font-weight:600;">{col}</th>'
    html += '</tr>'
    for _, row in df_recent.iterrows():
        html += '<tr style="border-top:1px solid #F1F5F9;">'
        for col in df_recent.columns:
            val = row[col]
            if col == '状态':
                val = style_status(val)
                html += f'<td style="padding:10px 12px;font-size:0.9rem;">{val}</td>'
            elif col == '金额(元)':
                html += f'<td style="padding:10px 12px;font-size:0.9rem;font-weight:600;">¥{val:.2f}</td>'
            else:
                html += f'<td style="padding:10px 12px;font-size:0.9rem;">{val}</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


# ================================================================
# 页面主程序
# ================================================================

def main():
    # ==================== 数据库连接预检 ====================
    ok, msg = check_connection()
    if not ok:
        st.error(f"数据库连接失败，大屏无法启动")
        st.info("请检查：\n1. MySQL 服务是否已启动（`net start MySQL80`）\n2. `.env` 文件中的密码是否正确")
        st.code(f"错误详情: {msg}")
        return

    # ==================== 侧边栏：明细数据 ====================
    with st.sidebar:
        st.markdown("### 系统导航")
        st.caption("数据明细 · 信息一览")

        with st.expander("商户信息一览", expanded=False):
            try:
                df_mer_info = load_merchant_info()
                if df_mer_info.empty:
                    st.info("暂无商户数据。请先运行 `python generate_mock_data.py`")
                else:
                    st.dataframe(df_mer_info, width='stretch', hide_index=True)
            except Exception as e:
                st.error("加载商户信息失败")
                st.code(traceback.format_exc())

        with st.expander("学生用户信息一览", expanded=False):
            try:
                df_stu = load_student_info()
                if df_stu.empty:
                    st.info("暂无学生数据。")
                else:
                    st.dataframe(df_stu, width='stretch', hide_index=True)
            except Exception as e:
                st.error("加载学生信息失败")
                st.code(traceback.format_exc())

        with st.expander("菜品信息一览", expanded=False):
            try:
                df_dishes = load_merchant_dishes()
                if df_dishes.empty:
                    st.info("暂无菜品数据。")
                else:
                    st.dataframe(df_dishes, width='stretch', hide_index=True)
            except Exception as e:
                st.error("加载菜品信息失败")
                st.code(traceback.format_exc())

        st.divider()

        with st.expander("骑手信息一览", expanded=False):
            try:
                df_riders = load_rider_info()
                if df_riders.empty:
                    st.info("暂无骑手数据。")
                else:
                    st.dataframe(df_riders, width='stretch', hide_index=True)
            except Exception as e:
                st.error("加载骑手信息失败")
                st.code(traceback.format_exc())

        with st.expander("寄存站点信息一览", expanded=False):
            try:
                df_points_info = load_pickup_point_info()
                if df_points_info.empty:
                    st.info("暂无站点数据。")
                else:
                    st.dataframe(df_points_info, width='stretch', hide_index=True)
            except Exception as e:
                st.error("加载站点信息失败")
                st.code(traceback.format_exc())

        st.divider()
        st.caption(f"数据更新: {datetime.now().strftime('%m-%d %H:%M:%S')}")
        st.caption("校园外卖两段式配送数据库系统")
        st.caption("期末答辩项目 v2.0")

    # ==================== 顶部标题 ====================
    now = datetime.now()
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">校园外卖两段式配送 · 实时数据监控大屏</div>
        <div class="header-sub">
            {now.year}年{now.month:02d}月{now.day:02d}日 {now:%H:%M:%S} &nbsp;|&nbsp;
            数据源: campus_delivery_db &nbsp;|&nbsp;
            校园两段式配送系统
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==================== 时间范围筛选 ====================
    col_fl, col_fs = st.columns([1.5, 6])
    with col_fl:
        st.markdown('<div style="padding-top:6px;font-weight:700;color:#6366F1;font-size:0.95rem;">时间范围</div>', unsafe_allow_html=True)
    with col_fs:
        date_options = ["今天", "最近 7 天", "最近 30 天", "本月", "全部数据"]
        current_opt = _get_date_option()
        selected_date = st.selectbox(
            "时间范围", date_options,
            index=date_options.index(current_opt) if current_opt in date_options else 4,
            key="date_filter_opt",
            label_visibility="collapsed",
        )
    date_option = _get_date_option()

    # ==================== 数据加载与空值检测 ====================
    try:
        stats = load_basic_stats(date_option)
    except Exception as e:
        st.error(f"数据加载失败！请确认已运行 `python generate_mock_data.py` 生成模拟数据。")
        st.code(f"错误信息: {e}")
        return

    if stats.get("total_orders", 0) == 0:
        st.warning("数据库中没有订单数据！请先运行：\n\n```bash\npython reinit_db.py\npython generate_mock_data.py\n```")
        st.info("reinit_db.py — 创建数据库表结构 + 种子数据\ngenerate_mock_data.py — 生成 5000 条模拟订单流水")
        return

    # ==================== KPI 指标行 ====================
    render_kpi_row(stats)

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # ==================== 宽屏网格布局 ====================
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">商户销售排行 Top 10</div>', unsafe_allow_html=True)
        try:
            df_merchants = load_merchant_sales_rank()
            if df_merchants.empty:
                st.info("暂无商户数据。请运行 generate_mock_data.py")
            else:
                render_merchant_rank_chart(df_merchants)
        except Exception as e:
            st.error("加载商户排行数据失败")
            st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">订单状态分布</div>', unsafe_allow_html=True)
        try:
            df_status = load_order_status_distribution(date_option)
            if df_status.empty:
                st.info("暂无订单数据。")
            else:
                render_order_status_pie(df_status)
        except Exception as e:
            st.error("加载订单状态数据失败")
            st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 近期订单流水（全宽） ====================
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">近期订单流水（最新 10 条）</div>', unsafe_allow_html=True)
    try:
        df_recent = load_recent_orders(10, date_option)
        if df_recent.empty:
            st.info("暂无订单数据。")
        else:
            render_recent_orders_table(df_recent)
    except Exception as e:
        st.error("加载近期订单数据失败")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 寄存点饱和度监控（全宽） ====================
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">寄存点饱和度实时监控</div>', unsafe_allow_html=True)
    try:
        df_points = load_pickup_analytics()
        if df_points.empty:
            st.info("暂无寄存点数据。")
        else:
            df_points['point_name'] = df_points['point_name'].str.replace('智能寄存柜', '', regex=False).str.strip()
            render_pickup_saturation_chart(df_points)
    except Exception as e:
        st.error("加载寄存点数据失败")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 时段订单分布（全宽） ====================
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">时段订单分布 · 高峰分析</div>', unsafe_allow_html=True)
    try:
        df_period = load_time_period_distribution(date_option)
        if df_period.empty:
            st.info("暂无订单数据。")
        else:
            render_time_period_chart(df_period)
            peak_mask = df_period['time_period'].str.contains('高峰|夜宵')
            peak_orders = int(df_period[peak_mask]['order_count'].sum())
            total_orders = int(df_period['order_count'].sum())
            peak_pct = round(peak_orders / total_orders * 100, 1) if total_orders > 0 else 0
            st.markdown(
                f'<div style="text-align:center;color:{COLOR_TEXT_SEC};font-size:0.88rem;padding:0.5rem;">'
                f'高峰+夜宵时段订单占比: <strong style="color:{COLOR_DANGER};font-size:1.1rem;">{peak_pct}%</strong> '
                f'（{peak_orders:,} / {total_orders:,} 单）'
                f'</div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error("加载时段分布数据失败")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== AI 智能数据助手 ====================
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">AI 智能数据助手 <span style="font-weight:400;font-size:0.8rem;color:#64748B;">DeepSeek Text-to-SQL</span></div>', unsafe_allow_html=True)

    if not DEEPSEEK_API_KEY:
        st.warning("DeepSeek API Key 未配置！请在 `.env` 文件中添加 `DEEPSEEK_API_KEY=your_key`")
    else:
        st.markdown("""
            <div style="font-size:0.9rem;color:#64748B;margin-bottom:1rem;">
            输入中文自然语言问题，AI 自动转换为 SQL 查询并返回结果。
            例如: "哪个商家销售额最高？" "各寄存点饱和度情况"
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 初始化聊天历史
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    st.markdown("##### 快捷问题")
    example_cols = st.columns(3)
    examples = [
        "哪个商家销售额最高？",
        "共有多少学生注册？",
        "各寄存点饱和度如何？",
    ]
    for i, (col, example) in enumerate(zip(example_cols, examples)):
        with col:
            if st.button(example, key=f"ai_example_{i}", width='stretch'):
                st.session_state.ai_input = example

    col_input, col_btns = st.columns([5, 1.5])
    with col_input:
        user_input = st.text_input(
            "请输入您的问题:", key="ai_input",
            placeholder="例如: 哪个商家销售额最高？",
            label_visibility="collapsed",
        )
    with col_btns:
        col_send, col_clear = st.columns(2)
        with col_send:
            submit_clicked = st.button("发送", type="primary", width='stretch')
        with col_clear:
            if st.button("清除", width='stretch'):
                st.session_state.ai_chat_history = []
                st.rerun()

    if submit_clicked and user_input:
        with st.spinner("🤔 AI 正在思考并生成 SQL..."):
            result = ai_text_to_sql(user_input)

        st.session_state.ai_chat_history.append({
            "role": "user", "content": user_input,
        })

        if result["success"]:
            st.session_state.ai_chat_history.append({
                "role": "assistant",
                "content": f"查询成功！共找到 {result['row_count']} 条记录",
                "sql": result["sql"],
                "result": result["result"],
                "columns": result["columns"],
            })
        else:
            st.session_state.ai_chat_history.append({
                "role": "assistant",
                "content": result["error"],
                "sql": result.get("sql", ""),
                "result": [],
                "columns": [],
                "is_error": True,
            })

    for msg in st.session_state.ai_chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="ai-message user"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            if msg.get("is_error"):
                st.markdown(f'<div class="ai-message error"><strong>Error:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message assistant"><strong>AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("sql"):
                st.markdown(f'<div class="ai-message sql"><strong>生成的 SQL:</strong>\n{msg["sql"]}</div>', unsafe_allow_html=True)
            if msg.get("result") and len(msg["result"]) > 0:
                df_result = pd.DataFrame(msg["result"])
                st.dataframe(df_result, width='stretch', hide_index=True)
                num_cols = df_result.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if len(num_cols) >= 1 and len(df_result) > 1:
                    with st.expander("查看图表"):
                        ct1, ct2 = st.columns(2)
                        with ct1:
                            st.caption("柱状图")
                            try:
                                first_text_col = df_result.select_dtypes(exclude=['float64', 'int64']).columns[0]
                                st.bar_chart(df_result.set_index(first_text_col)[num_cols[0]], width='stretch')
                            except Exception:
                                pass
                        with ct2:
                            if len(num_cols) > 1:
                                st.caption("折线图")
                                try:
                                    first_text_col = df_result.select_dtypes(exclude=['float64', 'int64']).columns[0]
                                    st.line_chart(df_result.set_index(first_text_col)[num_cols[:3]], width='stretch')
                                except Exception:
                                    pass
                csv_data = df_result.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下载 CSV",
                    data=csv_data,
                    file_name=f"ai_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    # ---- 页脚 ----
    st.markdown("""
    <div class="footer">
        校园外卖两段式配送数据库系统 &nbsp;·&nbsp; 期末答辩项目 &nbsp;·&nbsp;
        Streamlit + MySQL + DeepSeek AI &nbsp;·&nbsp; v2.0
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
