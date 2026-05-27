# -*- coding: utf-8 -*-
"""
校园外卖配送 · 实时监控大屏 v4.0
启动方式: python app.py  或  python dashboard_app.py
现已迁移至 Flask + 原生 ECharts 前端，不再使用 Streamlit。
"""
from app import app

if __name__ == "__main__":
    print("\n  校园外卖配送 · 实时监控大屏 v4.0")
    print("  Flask + ECharts 原生前端 · http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
