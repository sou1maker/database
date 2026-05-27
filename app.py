# -*- coding: utf-8 -*-
"""
校园外卖两段式配送 · 实时数据监控大屏 v4.0
Flask + 原生 HTML/ECharts 前端
"""
import os
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from db import get_connection

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

app = Flask(__name__)
CORS(app)


# ================================================================
# 数据查询 API
# ================================================================

def _range_filter(r):
    """根据range参数生成SQL日期条件"""
    if r == "today":
        return "DATE(o.created_at) = CURDATE()"
    elif r == "7d":
        return "o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    elif r == "30d":
        return "o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    elif r == "month":
        return "DATE_FORMAT(o.created_at, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m')"
    else:
        return "1=1"


@app.route("/api/today_stats")
def today_stats():
    conn = get_connection()
    try:
        stats = {}
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE()")
            stats["today_orders"] = cur.fetchone()[0]
            cur.execute("""
                SELECT IFNULL(SUM(total_amount), 0) FROM orders
                WHERE DATE(created_at) = CURDATE() AND order_status = 'Completed'
            """)
            stats["today_revenue"] = float(cur.fetchone()[0])
            cur.execute("""
                SELECT COUNT(DISTINCT rider_id) FROM (
                    SELECT stage1_rider_id AS rider_id FROM orders
                    WHERE order_status NOT IN ('Completed','Cancelled') AND stage1_rider_id IS NOT NULL
                    UNION
                    SELECT stage2_rider_id AS rider_id FROM orders
                    WHERE order_status NOT IN ('Completed','Cancelled') AND stage2_rider_id IS NOT NULL
                ) AS active
            """)
            stats["active_riders"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(DISTINCT merchant_id) FROM orders WHERE DATE(created_at) = CURDATE()")
            stats["active_merchants"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM vw_pickup_point_analytics WHERE saturation_pct > 80")
            stats["overflow_points"] = cur.fetchone()[0]
        return jsonify(stats)
    finally:
        conn.close()


@app.route("/api/order_status")
def order_status():
    r = request.args.get("range", "today")
    filt = _range_filter(r)
    conn = get_connection()
    try:
        sql = f"""
            SELECT order_status, COUNT(*) AS cnt FROM orders o
            WHERE {filt} GROUP BY order_status ORDER BY cnt DESC
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify([{"status": row[0], "count": row[1]} for row in rows])
    finally:
        conn.close()


@app.route("/api/pickup_points")
def pickup_points():
    conn = get_connection()
    try:
        sql = """
            SELECT point_name, max_capacity, current_packages, saturation_pct, backlog_count
            FROM vw_pickup_point_analytics
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify([{
            "name": row[0].replace("智能寄存柜", "").strip(),
            "capacity": row[1], "packages": row[2],
            "saturation": round(float(row[3]), 1), "backlog": row[4],
        } for row in rows])
    finally:
        conn.close()


@app.route("/api/merchant_rank")
def merchant_rank():
    r = request.args.get("range", "today")
    filt = _range_filter(r).replace("o.created_at", "o.created_at")
    conn = get_connection()
    try:
        sql = f"""
            SELECT m.merchant_name, COUNT(DISTINCT o.order_id) AS orders,
                   IFNULL(SUM(o.total_amount), 0) AS sales
            FROM merchants m
            LEFT JOIN orders o ON m.merchant_id = o.merchant_id
                AND o.order_status = 'Completed' AND {filt}
            GROUP BY m.merchant_id
            ORDER BY sales DESC LIMIT 10
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify([{"name": row[0], "orders": row[1], "sales": float(row[2])} for row in rows])
    finally:
        conn.close()


@app.route("/api/recent_orders")
def recent_orders():
    limit = request.args.get("limit", 20, type=int)
    conn = get_connection()
    try:
        sql = f"""
            SELECT o.order_id, u.username, m.merchant_name, o.total_amount,
                   o.order_status, DATE_FORMAT(o.created_at, '%Y-%m-%d %H:%i') AS t
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN merchants m ON o.merchant_id = m.merchant_id
            ORDER BY o.created_at DESC LIMIT {limit}
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify([{
            "id": row[0], "user": row[1], "merchant": row[2],
            "amount": float(row[3]), "status": row[4], "time": row[5],
        } for row in rows])
    finally:
        conn.close()


@app.route("/api/hourly_dist")
def hourly_dist():
    r = request.args.get("range", "today")
    filt = _range_filter(r)
    conn = get_connection()
    try:
        sql = f"""
            SELECT HOUR(o.created_at) AS h, COUNT(*) AS cnt,
                   ROUND(AVG(o.total_amount), 2) AS avg_amount
            FROM orders o WHERE {filt}
            GROUP BY HOUR(o.created_at) ORDER BY h
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify([{"hour": row[0], "count": row[1], "avg_amount": float(row[2])} for row in rows])
    finally:
        conn.close()


@app.route("/api/side_tables")
def side_tables():
    conn = get_connection()
    try:
        result = {}
        with conn.cursor() as cur:
            cur.execute("SELECT merchant_id, merchant_name, phone, rating FROM merchants ORDER BY merchant_id")
            result["merchants"] = [{"id": r[0], "name": r[1], "phone": r[2], "rating": float(r[3])} for r in cur.fetchall()]
            cur.execute("SELECT user_id, username, phone, dorm_building, balance FROM users ORDER BY user_id")
            result["users"] = [{"id": r[0], "name": r[1], "phone": r[2], "dorm": r[3], "balance": float(r[4])} for r in cur.fetchall()]
            cur.execute("""
                SELECT d.dish_name, d.price, d.stock, m.merchant_name
                FROM dishes d JOIN merchants m ON d.merchant_id = m.merchant_id
                ORDER BY m.merchant_name
            """)
            result["dishes"] = [{"name": r[0], "price": float(r[1]), "stock": r[2], "merchant": r[3]} for r in cur.fetchall()]
            cur.execute("SELECT rider_name, phone, rider_type, status FROM riders ORDER BY rider_id")
            result["riders"] = [{"name": r[0], "phone": r[1], "type": r[2], "status": r[3]} for r in cur.fetchall()]
            cur.execute("SELECT point_name, location, capacity, current_packages FROM pickup_points ORDER BY point_id")
            result["points"] = [{"name": r[0], "location": r[1], "capacity": r[2], "packages": r[3]} for r in cur.fetchall()]
        return jsonify(result)
    finally:
        conn.close()


# ================================================================
# AI Text-to-SQL (DeepSeek)
# ================================================================

DB_SCHEMA = """数据库：campus_delivery_db（校园外卖两段式配送）
表：users(user_id,username,phone,dorm_building,room_number,balance)
merchants(merchant_id,merchant_name,phone,address,rating)
dishes(dish_id,merchant_id,dish_name,price,stock,status)
pickup_points(point_id,point_name,location,capacity,current_packages)
riders(rider_id,rider_name,phone,rider_type,status)
orders(order_id,user_id,merchant_id,pickup_point_id,total_amount,order_status,stage1_rider_id,stage2_rider_id,created_at,stage1_completed_at,stage2_completed_at)
order_items(item_id,order_id,dish_id,quantity,price_at_order)
视图：vw_pickup_point_analytics, vw_merchant_sales_rank
只允许SELECT。金额单位元。金额统计只看Completed。字段用中文别名。只返回SQL不加markdown。"""


@app.route("/api/ai_query", methods=["POST"])
def ai_query():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"success": False, "error": "问题不能为空"})

    if not DEEPSEEK_API_KEY:
        return jsonify({"success": False, "error": "DeepSeek API Key 未配置"})

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=10)
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": f"你是Text-to-SQL助手。Schema:\n{DB_SCHEMA}"},
                {"role": "user", "content": question}
            ],
            temperature=0.1, max_tokens=1000, timeout=10,
        )
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        if not sql.upper().startswith("SELECT"):
            return jsonify({"success": False, "sql": sql, "error": "非查询语句已拦截"})

        dangerous = ["INSERT ","UPDATE ","DELETE ","DROP ","ALTER ","TRUNCATE ","CREATE ","EXEC "]
        for kw in dangerous:
            if kw in sql.upper():
                return jsonify({"success": False, "sql": sql, "error": f"危险关键字 {kw.strip()}"})

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
            return jsonify({"success": True, "sql": sql, "columns": cols, "rows": [list(r) for r in rows]})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ================================================================
# 主页面
# ================================================================

@app.route("/")
def index():
    now = datetime.now()
    return render_template_string(HTML_TEMPLATE, now=now)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>校园外卖配送 · 实时数据监控大屏</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:"Microsoft YaHei","PingFang SC","Helvetica Neue",sans-serif;
  background:#0b0f19;color:#e2e8f0;min-height:100vh;
}
/* 顶部栏 */
.header{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 32px;background:linear-gradient(135deg,#131a2c 0%,#1a2740 100%);
  border-bottom:1px solid rgba(99,102,241,0.2);
}
.header-left{display:flex;align-items:center;gap:14px}
.live-dot{width:11px;height:11px;background:#ef4444;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.6)}50%{box-shadow:0 0 0 10px rgba(239,68,68,0)}}
.header h1{font-size:1.35rem;font-weight:700;letter-spacing:2px}
.header-right{display:flex;align-items:center;gap:20px;font-size:0.85rem;color:#94a3b8}

/* Tab导航 */
.tab-nav{
  display:flex;gap:0;padding:0 32px;
  background:linear-gradient(135deg,#131a2c 0%,#1a2740 100%);
  border-bottom:1px solid rgba(255,255,255,0.06);
}
.tab-nav button{
  padding:12px 24px;border:none;background:transparent;color:#64748b;
  cursor:pointer;font-size:0.88rem;font-family:inherit;font-weight:600;
  border-bottom:3px solid transparent;transition:all 0.2s;
  white-space:nowrap;
}
.tab-nav button:hover{color:#cbd5e1}
.tab-nav button.active{color:#e2e8f0;border-bottom-color:#6366f1}

/* Tab内容 */
.tab-content{display:none}
.tab-content.active{display:block}

/* KPI行 */
.kpi-row{display:flex;gap:16px;padding:20px 32px}
.kpi-card{
  flex:1;background:linear-gradient(135deg,#131a2c 0%,#1a2740 100%);
  border-radius:16px;padding:22px 16px;text-align:center;
  border:1px solid rgba(255,255,255,0.06);transition:transform 0.2s;
}
.kpi-card:hover{transform:translateY(-4px)}
.kpi-card.danger{border-color:rgba(239,68,68,0.3);animation:danger-glow 2s infinite}
@keyframes danger-glow{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.12)}50%{box-shadow:0 0 14px 4px rgba(239,68,68,0.12)}}
.kpi-value{font-size:2.1rem;font-weight:800;line-height:1.2}
.kpi-label{font-size:0.78rem;color:#94a3b8;margin-top:4px;letter-spacing:1px}

/* 范围按钮 */
.range-row{display:flex;gap:6px;align-items:center;padding:0 32px 12px}
.range-btn{
  padding:7px 18px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);
  background:transparent;color:#94a3b8;cursor:pointer;font-size:0.84rem;
  transition:all 0.2s;font-family:inherit;
}
.range-btn:hover,.range-btn.active{
  background:rgba(99,102,241,0.2);border-color:#6366f1;color:#e2e8f0;
}

/* 图表网格 */
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:0 32px 20px}
.chart-panel{
  background:linear-gradient(135deg,#131a2c 0%,#1a2740 100%);
  border-radius:16px;padding:20px;border:1px solid rgba(255,255,255,0.06);
}
.chart-panel.wide{grid-column:1/-1}
.chart-title{
  font-size:0.95rem;font-weight:700;color:#e2e8f0;margin-bottom:14px;
  padding-left:12px;border-left:3px solid #6366f1;
}
.chart-box{width:100%;height:380px}
.chart-box.tall{width:100%;height:440px}

/* 表格通用 */
.data-table{width:100%;border-collapse:collapse;font-size:0.84rem}
.data-table thead{position:sticky;top:0;z-index:1}
.data-table th{
  text-align:left;padding:10px 12px;color:#94a3b8;font-weight:600;
  border-bottom:2px solid rgba(255,255,255,0.1);background:rgba(19,26,44,0.95);
}
.data-table td{padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.04)}
.data-table tbody tr:hover{background:rgba(99,102,241,0.06)}
.status-tag{padding:3px 12px;border-radius:14px;font-size:0.76rem;font-weight:500;white-space:nowrap}
/* 爆仓 */
.alert-box{margin-top:12px}
.alert-item{
  background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
  border-radius:10px;padding:12px 16px;margin-bottom:6px;
  color:#fca5a5;font-size:0.88rem;font-weight:600;
}
/* AI助手 */
.ai-section{padding:0 32px 28px}
.ai-panel{background:linear-gradient(135deg,#131a2c 0%,#1a2740 100%);border-radius:16px;padding:20px;border:1px solid rgba(255,255,255,0.06)}
.ai-input-row{display:flex;gap:12px;margin:12px 0}
.ai-input{
  flex:1;padding:12px 16px;border-radius:10px;
  background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
  color:#e2e8f0;font-size:0.9rem;font-family:inherit;outline:none;
}
.ai-input:focus{border-color:#6366f1}
.ai-btn{
  padding:12px 24px;border-radius:10px;border:none;cursor:pointer;
  font-weight:600;font-size:0.88rem;font-family:inherit;transition:all 0.2s;
}
.ai-btn.primary{background:#6366f1;color:#fff}
.ai-btn.primary:hover{background:#4f46e5}
.ai-btn.secondary{background:rgba(255,255,255,0.08);color:#94a3b8}
.ai-btn.secondary:hover{background:rgba(255,255,255,0.15)}
.quick-btns{display:flex;gap:8px;margin-bottom:12px}
.quick-btn{
  padding:6px 16px;border-radius:8px;border:1px solid rgba(99,102,241,0.3);
  background:rgba(99,102,241,0.08);color:#a5b4fc;cursor:pointer;
  font-size:0.82rem;font-family:inherit;transition:all 0.2s;
}
.quick-btn:hover{background:rgba(99,102,241,0.2)}
.ai-result{margin-top:12px}
.ai-sql{
  background:rgba(0,0,0,0.3);padding:12px 16px;border-radius:8px;
  font-family:'Consolas','Courier New',monospace;font-size:0.82rem;
  color:#fbbf24;overflow-x:auto;margin:8px 0;
}
.ai-table{width:100%;border-collapse:collapse;font-size:0.84rem;margin-top:8px}
.ai-table th{text-align:left;padding:8px 12px;background:rgba(99,102,241,0.1);color:#94a3b8}
.ai-table td{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,0.04)}

/* 数据明细表 */
.table-wrap{max-height:72vh;overflow-y:auto}
.table-wrap .data-table{font-size:0.82rem}
.table-wrap .data-table th{font-size:0.78rem;padding:12px 14px}
.table-wrap .data-table td{padding:10px 14px}

/* 页脚 */
.footer{
  text-align:center;color:#475569;font-size:0.8rem;
  padding:18px 0 12px;border-top:1px solid rgba(255,255,255,0.06);
  margin:0 32px;
}
</style>
</head>
<body>

<!-- 顶部 -->
<div class="header">
  <div class="header-left">
    <span class="live-dot" id="liveDot"></span>
    <h1>校园外卖两段式配送 · 实时数据监控大屏</h1>
  </div>
  <div class="header-right">
    <span id="clock">--</span>
    <span style="color:#6366f1">|</span>
    <span>数据源: campus_delivery_db</span>
    <span style="color:#6366f1">|</span>
    <span>自动刷新 30s</span>
  </div>
</div>

<!-- Tab导航 -->
<div class="tab-nav">
  <button class="active" data-tab="dashboard">数据大屏</button>
  <button data-tab="merchants">商户信息</button>
  <button data-tab="students">学生用户</button>
  <button data-tab="dishes">菜品信息</button>
  <button data-tab="riders">骑手信息</button>
  <button data-tab="pickup">寄存站点</button>
</div>

<!-- ========== 数据大屏 Tab ========== -->
<div id="tab-dashboard" class="tab-content active">
  <div class="kpi-row" id="kpiRow"></div>

  <div class="range-row">
    <span style="color:#94a3b8;font-size:0.85rem;margin-right:8px;">时间范围</span>
    <button class="range-btn active" data-range="today">今天</button>
    <button class="range-btn" data-range="7d">近7天</button>
    <button class="range-btn" data-range="30d">近30天</button>
    <button class="range-btn" data-range="month">本月</button>
    <button class="range-btn" data-range="all">全部</button>
    <span style="color:#64748b;font-size:0.76rem;margin-left:14px;" id="rangeHint">
      实时模式 · 展示今天实时配送状态
    </span>
  </div>

  <div class="chart-grid">
    <div class="chart-panel">
      <div class="chart-title">订单状态分布</div>
      <div class="chart-box" id="chartStatus"></div>
    </div>
    <div class="chart-panel">
      <div class="chart-title">近期订单流水</div>
      <div id="recentOrders" style="max-height:380px;overflow-y:auto;"></div>
    </div>
    <div class="chart-panel wide">
      <div class="chart-title">寄存点饱和度实时监控</div>
      <div class="chart-box tall" id="chartPickup"></div>
      <div class="alert-box" id="overflowAlerts"></div>
    </div>
    <div class="chart-panel">
      <div class="chart-title">商户销售排行 Top 10</div>
      <div class="chart-box" id="chartMerchant"></div>
    </div>
    <div class="chart-panel">
      <div class="chart-title">时段订单分布 · 高峰分析</div>
      <div class="chart-box" id="chartHourly"></div>
    </div>
  </div>

  <div class="ai-section">
    <div class="ai-panel">
      <div class="chart-title">AI 智能数据助手 <span style="font-weight:400;font-size:0.8rem;color:#94a3b8;">DeepSeek Text-to-SQL</span></div>
      <div class="quick-btns">
        <button class="quick-btn" onclick="askAI('哪个商家销售额最高？')">哪个商家销售额最高？</button>
        <button class="quick-btn" onclick="askAI('今天各时段订单分布？')">今天各时段订单分布？</button>
        <button class="quick-btn" onclick="askAI('各寄存点饱和度情况？')">各寄存点饱和度情况？</button>
      </div>
      <div class="ai-input-row">
        <input class="ai-input" id="aiInput" placeholder="输入中文问题，AI自动生成SQL..." onkeydown="if(event.key==='Enter')askAI()">
        <button class="ai-btn primary" onclick="askAI()">发送</button>
        <button class="ai-btn secondary" onclick="document.getElementById('aiResult').innerHTML=''">清除</button>
      </div>
      <div class="ai-result" id="aiResult"></div>
    </div>
  </div>
</div>

<!-- ========== 数据明细 Tabs ========== -->
<div id="tab-merchants" class="tab-content"><div style="padding:24px 32px"><div class="chart-title" style="margin-bottom:14px">商户信息一览</div><div class="table-wrap" id="tableMerchants"></div></div></div>
<div id="tab-students" class="tab-content"><div style="padding:24px 32px"><div class="chart-title" style="margin-bottom:14px">学生用户一览</div><div class="table-wrap" id="tableStudents"></div></div></div>
<div id="tab-dishes" class="tab-content"><div style="padding:24px 32px"><div class="chart-title" style="margin-bottom:14px">菜品信息一览</div><div class="table-wrap" id="tableDishes"></div></div></div>
<div id="tab-riders" class="tab-content"><div style="padding:24px 32px"><div class="chart-title" style="margin-bottom:14px">骑手信息一览</div><div class="table-wrap" id="tableRiders"></div></div></div>
<div id="tab-pickup" class="tab-content"><div style="padding:24px 32px"><div class="chart-title" style="margin-bottom:14px">寄存站点一览</div><div class="table-wrap" id="tablePickup"></div></div></div>

<div class="footer">
  校园外卖两段式配送数据库系统 · 期末答辩项目 · Flask + ECharts + MySQL + DeepSeek AI · v4.0
</div>

<script>
let currentRange = "today";
let refreshTimer = null;
let statusChart, pickupChart, merchantChart, hourlyChart;
let sideDataCache = null;

// ================================================================
// 初始化
// ================================================================
document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  loadDashboard();
  startClock();
  startAutoRefresh();

  // Tab切换
  document.querySelectorAll(".tab-nav button").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-nav button").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
      document.getElementById("tab-"+btn.dataset.tab).classList.add("active");
      const tab = btn.dataset.tab;
      if (tab === "dashboard") {
        [statusChart,pickupChart,merchantChart,hourlyChart].forEach(c => c && c.resize());
      } else if (!sideDataCache) {
        loadSideData().then(() => renderSideTable(tab));
      } else {
        renderSideTable(tab);
      }
    });
  });

  // 范围按钮
  document.querySelectorAll(".range-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".range-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentRange = btn.dataset.range;
      const hints = {today:"实时模式 · 展示今天实时配送状态","7d":"历史模式 · 近7天数据统计","30d":"历史模式 · 近30天数据统计",month:"本月数据统计",all:"全部历史数据统计"};
      document.getElementById("rangeHint").textContent = hints[currentRange] || "";
      document.getElementById("liveDot").style.display = currentRange==="today"?"inline-block":"none";
      loadDashboard();
    });
  });

  window.addEventListener("resize", () => {
    [statusChart,pickupChart,merchantChart,hourlyChart].forEach(c => c && c.resize());
  });
});

function initCharts() {
  statusChart = echarts.init(document.getElementById("chartStatus"));
  pickupChart = echarts.init(document.getElementById("chartPickup"));
  merchantChart = echarts.init(document.getElementById("chartMerchant"));
  hourlyChart = echarts.init(document.getElementById("chartHourly"));
}

function startClock() {
  const tick = () => {
    const d = new Date();
    document.getElementById("clock").textContent =
      d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+
      String(d.getDate()).padStart(2,"0")+" "+String(d.getHours()).padStart(2,"0")+":"+
      String(d.getMinutes()).padStart(2,"0")+":"+String(d.getSeconds()).padStart(2,"0");
  };
  tick(); setInterval(tick,1000);
}

function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => { if (currentRange==="today") loadDashboard(); }, 30000);
}

async function loadDashboard() {
  await Promise.all([loadKPIs(),loadOrderStatus(),loadRecentOrders(),loadPickupPoints(),loadMerchantRank(),loadHourlyDist()]);
}

async function loadKPIs() {
  const res = await fetch("/api/today_stats");
  const s = await res.json();
  const items = [
    {label:"今日订单", value:s.today_orders.toLocaleString(), color:"#6366f1", danger:false},
    {label:"今日营业额", value:"¥"+Math.round(s.today_revenue).toLocaleString(), color:"#06b6d4", danger:false},
    {label:"在途骑手", value:s.active_riders+" 人", color:"#f59e0b", danger:false},
    {label:"活跃商家", value:s.active_merchants+" 家", color:"#10b981", danger:false},
    {label:"爆仓预警", value:s.overflow_points > 0 ? s.overflow_points+" 个站点" : "无预警", color:"#ef4444", danger:s.overflow_points > 0},
  ];
  document.getElementById("kpiRow").innerHTML = items.map(i =>
    `<div class="kpi-card${i.danger?' danger':''}">
      <div class="kpi-value" style="color:${i.color}">${i.value}</div>
      <div class="kpi-label">${i.label}</div>
    </div>`
  ).join("");
}

async function loadRecentOrders() {
  const res = await fetch("/api/recent_orders?limit=15");
  const data = await res.json();
  const labels = {Paid:"已支付",Stage1_Assigned:"干线配送",Arrived_At_Point:"寄存待取",Stage2_Assigned:"楼栋配送",Completed:"已完成",Cancelled:"已取消"};
  const colors = {Paid:"#f59e0b",Stage1_Assigned:"#3b82f6",Arrived_At_Point:"#8b5cf6",Stage2_Assigned:"#06b6d4",Completed:"#22c55e",Cancelled:"#ef4444"};
  document.getElementById("recentOrders").innerHTML = `
    <table class="data-table"><thead><tr>
      <th>订单号</th><th>学生</th><th>商家</th><th>金额</th><th>状态</th><th>时间</th>
    </tr></thead><tbody>
    ${data.map(d => `<tr>
      <td>#${d.id}</td><td>${d.user}</td><td>${d.merchant}</td>
      <td style="font-weight:600">¥${d.amount.toFixed(2)}</td>
      <td><span class="status-tag" style="background:${colors[d.status]}20;color:${colors[d.status]}">${labels[d.status]||d.status}</span></td>
      <td>${d.time}</td>
    </tr>`).join("")}
    </tbody></table>`;
}


// ================================================================
// 数据明细表
// ================================================================
async function loadSideData() {
  const res = await fetch("/api/side_tables");
  sideDataCache = await res.json();
}

function renderSideTable(tab) {
  let html = "";
  const d = sideDataCache;
  if (tab === "merchants" && d.merchants) {
    html = `<table class="data-table"><thead><tr><th>编号</th><th>店铺名称</th><th>联系电话</th><th>评分</th></tr></thead><tbody>
      ${d.merchants.map(r=>`<tr><td>${r.id}</td><td>${r.name}</td><td>${r.phone}</td><td>${r.rating}</td></tr>`).join("")}
    </tbody></table>`;
  } else if (tab === "students" && d.users) {
    html = `<table class="data-table"><thead><tr><th>学号</th><th>姓名</th><th>手机号</th><th>宿舍楼栋</th><th>余额</th></tr></thead><tbody>
      ${d.users.map(r=>`<tr><td>${r.id}</td><td>${r.name}</td><td>${r.phone}</td><td>${r.dorm}</td><td>¥${r.balance.toFixed(2)}</td></tr>`).join("")}
    </tbody></table>`;
  } else if (tab === "dishes" && d.dishes) {
    html = `<table class="data-table"><thead><tr><th>菜品名称</th><th>单价</th><th>库存</th><th>所属商家</th></tr></thead><tbody>
      ${d.dishes.map(r=>`<tr><td>${r.name}</td><td>¥${r.price.toFixed(2)}</td><td>${r.stock}</td><td>${r.merchant}</td></tr>`).join("")}
    </tbody></table>`;
  } else if (tab === "riders" && d.riders) {
    const tmap = {Stage1_Trunk:"干线骑手",Stage2_Floor:"楼栋骑手"};
    const smap = {Idle:"空闲",Delivering:"配送中",Offline:"离线"};
    html = `<table class="data-table"><thead><tr><th>姓名</th><th>电话</th><th>分工</th><th>状态</th></tr></thead><tbody>
      ${d.riders.map(r=>`<tr><td>${r.name}</td><td>${r.phone}</td><td>${tmap[r.type]||r.type}</td><td>${smap[r.status]||r.status}</td></tr>`).join("")}
    </tbody></table>`;
  } else if (tab === "pickup" && d.points) {
    html = `<table class="data-table"><thead><tr><th>站点名称</th><th>位置</th><th>容量</th><th>在库件数</th><th>饱和度</th></tr></thead><tbody>
      ${d.points.map(r=>`<tr><td>${r.name}</td><td>${r.location}</td><td>${r.capacity}</td><td>${r.packages}</td><td>${(r.packages/r.capacity*100).toFixed(1)}%</td></tr>`).join("")}
    </tbody></table>`;
  }
  const el = document.getElementById("table" + tab.charAt(0).toUpperCase() + tab.slice(1));
  if (el) el.innerHTML = html;
}

// ================================================================
// 图表渲染（加大grid边距防止溢出）
// ================================================================

async function loadOrderStatus() {
  const res = await fetch("/api/order_status?range=" + currentRange);
  const data = await res.json();
  const labels = {Paid:"已支付",Stage1_Assigned:"干线配送",Arrived_At_Point:"寄存待取",Stage2_Assigned:"楼栋配送",Completed:"已完成",Cancelled:"已取消"};
  const colors = {Paid:"#94a3b8",Stage1_Assigned:"#3b82f6",Arrived_At_Point:"#8b5cf6",Stage2_Assigned:"#06b6d4",Completed:"#10b981",Cancelled:"#ef4444"};
  const total = data.reduce((s,d) => s+d.count, 0);
  statusChart.setOption({
    tooltip:{trigger:"item",formatter:"{b}: {c} 单 ({d}%)",backgroundColor:"rgba(19,26,44,0.95)",borderColor:"rgba(99,102,241,0.3)",textStyle:{color:"#e2e8f0",fontSize:13}},
    legend:{orient:"vertical",right:"5%",top:"center",textStyle:{color:"#94a3b8",fontSize:12},itemGap:12},
    series:[{
      type:"pie",radius:["48%","72%"],center:["38%","50%"],
      itemStyle:{borderColor:"#131a2c",borderWidth:3},
      label:{show:false},
      emphasis:{label:{show:true,fontSize:15,fontWeight:"bold",color:"#e2e8f0"},scaleSize:8},
      data:data.map(d => ({name:labels[d.status]||d.status,value:d.count,itemStyle:{color:colors[d.status]||"#94a3b8"}}))
    }],
    graphic:[
      {type:"text",left:"32%",top:"43%",style:{text:total.toString(),textAlign:"center",fontSize:28,fontWeight:"bold",fill:"#e2e8f0"}},
      {type:"text",left:"32%",top:"56%",style:{text:"订单总数",textAlign:"center",fontSize:12,fill:"#94a3b8"}},
    ],
  }, true);
}

async function loadPickupPoints() {
  const res = await fetch("/api/pickup_points");
  const data = await res.json();
  const names = data.map(d => d.name);
  const values = data.map(d => d.saturation);
  const barData = values.map(v => ({
    value:v,
    itemStyle:{color:v>80?"#ef4444":v>60?"#f59e0b":"#10b981",borderRadius:[0,6,6,0]}
  }));
  pickupChart.setOption({
    tooltip:{trigger:"axis",axisPointer:{type:"shadow"},backgroundColor:"rgba(19,26,44,0.95)",borderColor:"rgba(99,102,241,0.3)",textStyle:{color:"#e2e8f0"}},
    grid:{left:"16%",right:"14%",top:"5%",bottom:"5%"},
    xAxis:{type:"value",max:110,axisLabel:{color:"#94a3b8",formatter:"{value}%",fontSize:11},splitLine:{lineStyle:{color:"rgba(255,255,255,0.05)"}}},
    yAxis:{type:"category",data:names,axisLabel:{color:"#cbd5e1",fontSize:12}},
    series:[{
      type:"bar",data:barData,barWidth:"55%",
      label:{show:true,position:"right",color:"#cbd5e1",fontSize:11,formatter:"{c}%"},
      markLine:{
        silent:true,symbol:"none",
        lineStyle:{type:"dashed",width:1.5},
        data:[
          {xAxis:80,lineStyle:{color:"#ef4444"},label:{formatter:"爆仓线 80%",color:"#ef4444",fontSize:10}},
          {xAxis:60,lineStyle:{color:"#f59e0b"},label:{formatter:"预警线 60%",color:"#f59e0b",fontSize:10}},
        ],
      },
    }],
  }, true);

  const overflow = data.filter(d => d.saturation > 80);
  document.getElementById("overflowAlerts").innerHTML = overflow.map(d =>
    `<div class="alert-item">爆仓! ${d.name} 饱和度 ${d.saturation}%，在库 ${d.packages}/${d.capacity}</div>`
  ).join("");
}

async function loadMerchantRank() {
  const res = await fetch("/api/merchant_rank?range=" + currentRange);
  const data = await res.json();
  const rev = [...data].reverse();
  const blues = ["#1e3a5f","#1e4d8c","#2563eb","#3b82f6","#60a5fa","#3b82f6","#2563eb","#1e4d8c","#1e3a5f","#1e40af"].slice(0, rev.length).reverse();
  merchantChart.setOption({
    tooltip:{trigger:"axis",axisPointer:{type:"shadow"},backgroundColor:"rgba(19,26,44,0.95)",borderColor:"rgba(99,102,241,0.3)",textStyle:{color:"#e2e8f0"}},
    grid:{left:"26%",right:"16%",top:"5%",bottom:"5%"},
    xAxis:{type:"value",axisLabel:{color:"#94a3b8",formatter:"{value}元",fontSize:11},splitLine:{lineStyle:{color:"rgba(255,255,255,0.05)"}}},
    yAxis:{type:"category",data:rev.map(d=>d.name),axisLabel:{color:"#cbd5e1",fontSize:12,width:120,overflow:"truncate"}},
    series:[{
      type:"bar",barWidth:"55%",
      data:rev.map((d,i)=>({value:d.sales,itemStyle:{color:blues[i],borderRadius:[0,6,6,0]}})),
      label:{show:true,position:"right",color:"#cbd5e1",fontSize:10,formatter:"{c}元"},
    }],
  }, true);
}

async function loadHourlyDist() {
  const res = await fetch("/api/hourly_dist?range=" + currentRange);
  const data = await res.json();
  const hours = data.map(d => d.hour+":00");
  const counts = data.map(d => d.count);
  const amounts = data.map(d => d.avg_amount);
  hourlyChart.setOption({
    tooltip:{trigger:"axis",backgroundColor:"rgba(19,26,44,0.95)",borderColor:"rgba(99,102,241,0.3)",textStyle:{color:"#e2e8f0"}},
    legend:{data:["订单量","客单价"],textStyle:{color:"#94a3b8",fontSize:12},top:5},
    grid:{left:"10%",right:"10%",top:"18%",bottom:"8%"},
    xAxis:{type:"category",data:hours,axisLabel:{color:"#94a3b8",fontSize:11},axisLine:{lineStyle:{color:"rgba(255,255,255,0.1)"}}},
    yAxis:[
      {type:"value",name:"订单量",nameTextStyle:{color:"#94a3b8",fontSize:11},axisLabel:{color:"#94a3b8"},splitLine:{lineStyle:{color:"rgba(255,255,255,0.05)"}}},
      {type:"value",name:"客单价(元)",nameTextStyle:{color:"#94a3b8",fontSize:11},axisLabel:{color:"#94a3b8"},splitLine:{show:false}},
    ],
    series:[
      {name:"订单量",type:"bar",data:counts,barWidth:"55%",itemStyle:{color:"#6366f1",borderRadius:[6,6,0,0]}},
      {name:"客单价",type:"line",yAxisIndex:1,data:amounts,lineStyle:{color:"#f59e0b",width:3},itemStyle:{color:"#f59e0b"},symbol:"circle",symbolSize:8,smooth:true},
    ],
  }, true);
}

// ================================================================
// AI助手
// ================================================================

async function askAI(question) {
  const q = question || document.getElementById("aiInput").value.trim();
  if (!q) return;
  if (!question) document.getElementById("aiInput").value = "";
  const resultDiv = document.getElementById("aiResult");
  resultDiv.innerHTML = '<div style="color:#94a3b8;padding:12px">AI 思考中...</div>';
  try {
    const res = await fetch("/api/ai_query", {
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({question:q}),
    });
    const data = await res.json();
    if (data.success) {
      let html = `<div style="color:#10b981;font-weight:600;margin-bottom:6px">查询成功，共 ${data.rows.length} 条</div>`;
      if (data.sql) html += `<div class="ai-sql">${data.sql}</div>`;
      if (data.rows.length > 0) {
        html += `<table class="ai-table"><thead><tr>${data.columns.map(c=>`<th>${c}</th>`).join("")}</tr></thead><tbody>`;
        html += data.rows.map(r => `<tr>${r.map(v=>`<td>${v??""}</td>`).join("")}</tr>`).join("");
        html += `</tbody></table>`;
        if (data.rows.length > 1) {
          html += `<button class="quick-btn" onclick="downloadCSV('${encodeURIComponent(JSON.stringify(data))}')" style="margin-top:10px">下载 CSV</button>`;
        }
      }
      resultDiv.innerHTML = html;
    } else {
      resultDiv.innerHTML = `<div style="color:#ef4444;font-weight:600">错误: ${data.error||"未知错误"}</div>${data.sql?`<div class="ai-sql">${data.sql}</div>`:""}`;
    }
  } catch(e) {
    resultDiv.innerHTML = `<div style="color:#ef4444">请求失败: ${e.message}</div>`;
  }
}

function downloadCSV(encoded) {
  const data = JSON.parse(decodeURIComponent(encoded));
  let csv = "﻿"+data.columns.join(",") + "\n";
  data.rows.forEach(r => { csv += r.map(v=>'"'+(v||"").toString().replace(/"/g,'""')+'"').join(",") + "\n"; });
  const blob = new Blob([csv], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "query_result.csv"; a.click();
  URL.revokeObjectURL(a.href);
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    print("\n  校园外卖配送 · 实时监控大屏 v4.0")
    print("  Flask + 原生 ECharts 前端")
    print("  http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
