# -*- coding: utf-8 -*-
"""
校园外卖两段式配送系统 · 答辩汇报 PPT v6.0
白底蓝标题 · 文字精简 · 关键代码 · 一页一图 · 图片不拉伸
"""
import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image as PILImage

# ============================================================
# DESIGN CONSTANTS (from CLAUDE.md)
# ============================================================
W = Inches(13.333)
H = Inches(7.5)
BLUE   = RGBColor(0x2F, 0x54, 0x96)  # 深蓝标题栏
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GREEN  = RGBColor(0x00, 0xB0, 0x50)
RED    = RGBColor(0xCC, 0x33, 0x33)
ORANGE = RGBColor(0xFF, 0x98, 0x00)
DARK   = RGBColor(0x33, 0x33, 0x33)
GRAY   = RGBColor(0x88, 0x88, 0x88)
LIGHT  = RGBColor(0xF4, 0xF6, 0xF9)
CODE_BG = RGBColor(0xF0, 0xF2, 0xF5)
TITLE_H = Inches(0.85)
FN = '微软雅黑'
MONO = 'Consolas'

IMG = os.path.join(os.path.dirname(__file__), 'images', 'screenshots')
ER  = os.path.join(os.path.dirname(__file__), 'images', 'er_diagram.png')

def S(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def bar(slide, title, num=None):
    """Blue title bar"""
    b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), W, TITLE_H)
    b.fill.solid(); b.fill.fore_color.rgb = BLUE; b.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.12), Inches(12), Inches(0.6))
    p = tb.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(26); p.font.color.rgb = WHITE; p.font.bold = True; p.font.name = FN
    if num is not None:
        t2 = slide.shapes.add_textbox(Inches(12.2), Inches(7.0), Inches(0.8), Inches(0.35))
        p2 = t2.text_frame.paragraphs[0]
        p2.text = str(num); p2.font.size = Pt(10); p2.font.color.rgb = GRAY; p2.font.name = FN; p2.alignment = PP_ALIGN.RIGHT

def section(prs, num, title, sub):
    """White section divider with blue accents"""
    sl = S(prs)
    # Left blue bar
    lb = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), H)
    lb.fill.solid(); lb.fill.fore_color.rgb = BLUE; lb.line.fill.background()
    # Number
    t = sl.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(2), Inches(1.5))
    p = t.text_frame.paragraphs[0]
    p.text = num; p.font.size = Pt(72); p.font.color.rgb = BLUE; p.font.bold = True; p.font.name = FN
    # Title
    t2 = sl.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(11), Inches(1.0))
    p2 = t2.text_frame.paragraphs[0]
    p2.text = title; p2.font.size = Pt(34); p2.font.color.rgb = DARK; p2.font.bold = True; p2.font.name = FN
    # Sub
    t3 = sl.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(11), Inches(0.5))
    p3 = t3.text_frame.paragraphs[0]
    p3.text = sub; p3.font.size = Pt(14); p3.font.color.rgb = GRAY; p3.font.name = FN
    return sl

def txt(slide, left, top, width, height, text, size=14, color=DARK, bold=False, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(size); p.font.color.rgb = color; p.font.bold = bold; p.font.name = FN; p.alignment = align
    return tf

def mtxt(slide, left, top, width, height, lines, size=14, color=DARK, spacing=Pt(6)):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size); p.font.color.rgb = color; p.font.name = FN; p.space_after = spacing
    return tf

def code(slide, left, top, width, height, lines, size=10):
    """Code block - light gray bg, monospace, short"""
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    box.fill.solid(); box.fill.fore_color.rgb = CODE_BG
    box.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD); box.line.width = Pt(0.5)
    tb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.08), Inches(width - 0.3), Inches(height - 0.16))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size); p.font.name = MONO
        p.font.color.rgb = RGBColor(0x2F, 0x54, 0x96) if line.strip().startswith('--') else RGBColor(0x44, 0x44, 0x44)
        p.space_after = Pt(1)
    return tf

def card(slide, left, top, width, height, title, lines, accent=BLUE):
    """Info card with colored top bar"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0); bg.line.width = Pt(0.5)
    bar_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.05))
    bar_shape.fill.solid(); bar_shape.fill.fore_color.rgb = accent; bar_shape.line.fill.background()
    txt(slide, left + 0.15, top + 0.12, width - 0.3, 0.3, title, 14, accent, True)
    mtxt(slide, left + 0.15, top + 0.5, width - 0.3, height - 0.55, lines, 11, DARK)

def img(slide, path, left, top, width=None):
    """Insert image - width only, preserve aspect ratio (NO stretching)"""
    if not os.path.exists(path):
        txt(slide, left, top, 4, 0.5, f'[missing: {os.path.basename(path)}]', 10, RED)
        return None
    if width:
        return slide.shapes.add_picture(path, Inches(left), Inches(top), Inches(width))
    else:
        return slide.shapes.add_picture(path, Inches(left), Inches(top))

def img_w(slide, path, left, top, width):
    """Insert image with specified width, auto height"""
    return img(slide, path, left, top, width)

def number_badge(slide, left, top, n, clr=BLUE):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(0.5), Inches(0.5))
    c.fill.solid(); c.fill.fore_color.rgb = clr; c.line.fill.background()
    p = c.text_frame.paragraphs[0]
    p.text = str(n); p.font.size = Pt(16); p.font.color.rgb = WHITE; p.font.bold = True; p.font.name = FN; p.alignment = PP_ALIGN.CENTER

def tbl(slide, left, top, col_w, hdrs, rows, fs=10):
    n = len(rows) + 1
    nc = len(hdrs)
    tw = sum(col_w)
    s = slide.shapes.add_table(n, nc, Inches(left), Inches(top), Inches(tw), Inches(0.3 * n))
    t = s.table
    for ci, cw in enumerate(col_w):
        t.columns[ci].width = Inches(cw)
    for ci, h in enumerate(hdrs):
        c = t.cell(0, ci); c.text = h
        for p in c.text_frame.paragraphs:
            p.font.size = Pt(fs); p.font.bold = True; p.font.color.rgb = WHITE; p.font.name = FN; p.alignment = PP_ALIGN.CENTER
        c.fill.solid(); c.fill.fore_color.rgb = BLUE
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.cell(ri + 1, ci); c.text = str(val)
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(fs - 1); p.font.color.rgb = DARK; p.font.name = FN
            if ri % 2 == 0:
                c.fill.solid(); c.fill.fore_color.rgb = LIGHT


# ============================================================
# BUILD
# ============================================================

def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    pg = [0]
    def p(add=1):
        pg[0] += add
        return pg[0]

    # ---- SLIDE 1: COVER ----
    sl = S(prs)
    # Blue left panel
    lp = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.5), H)
    lp.fill.solid(); lp.fill.fore_color.rgb = BLUE; lp.line.fill.background()
    txt(sl, 0.8, 1.5, 3.5, 0.5, '数据库系统课程项目', 14, RGBColor(0xBB, 0xCC, 0xEE))
    txt(sl, 0.8, 2.2, 3.5, 1.5, '校园外卖\n两段式配送\n数据库系统', 34, WHITE, True)
    txt(sl, 0.8, 4.5, 3.5, 0.5, '答辩汇报', 18, WHITE)
    # Right side
    txt(sl, 5.2, 2.5, 7, 0.5, 'MySQL 8.0    Flask    ECharts    DeepSeek AI', 14, GRAY)
    items = ['7 张表 · 严格 3NF', '4 个 B-Tree 索引', '7 个触发器 · 防护盾', '4 个存储过程 · 事务管理', '2 个分析视图', 'AI Text-to-SQL 自然语言查询']
    mtxt(sl, 5.2, 3.2, 7, 2.5, items, 15, DARK, Pt(8))
    txt(sl, 5.2, 6.2, 7, 0.4, '2026 年 6 月', 13, GRAY)
    p()

    # ---- SLIDE 2: TOC ----
    sl = S(prs)
    bar(sl, '目录', p())
    toc = [
        ('01', '项目背景与需求分析', '3'),
        ('02', '系统设计与数据库架构', '7'),
        ('03', '索引策略与性能优化', '15'),
        ('04', '七重触发器防护盾', '18'),
        ('05', '存储过程与事务管理', '28'),
        ('06', '视图与窗口函数', '32'),
        ('07', '系统大屏与可视化展示', '35'),
        ('08', '创新点总结与成果交付', '41'),
    ]
    for i, (num, title, page) in enumerate(toc):
        y = 1.3 + i * 0.7
        txt(sl, 1.0, y, 1.0, 0.5, num, 28, BLUE, True)
        txt(sl, 2.2, y, 7.0, 0.5, title, 18, DARK)
        txt(sl, 10.5, y, 2.0, 0.5, f'································ {page}', 14, GRAY)

    # ---- SLIDE 3: SECTION 01 ----
    section(prs, '01', '项目背景与需求分析', '校园外卖市场 · 传统痛点 · 两段式配送模型')
    p()

    # ---- SLIDE 4: Market ----
    sl = S(prs); bar(sl, '校园外卖市场概览', p())
    for i, (n, t, sub, clr) in enumerate([
        ('4,500亿+', '中国外卖市场规模 (2025)', '年增长 22.4%', BLUE),
        ('70%+', '高校外卖渗透率', '大学生是消费主力', GREEN),
        ('120万单/日', '头部高校日均外卖量', '高峰期配送压力巨大', ORANGE),
    ]):
        x = 0.8 + i * 4.1
        c = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.8), Inches(3.6), Inches(2.0))
        c.fill.solid(); c.fill.fore_color.rgb = WHITE
        c.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0); c.line.width = Pt(0.5)
        txt(sl, x + 0.2, 1.95, 3.2, 0.6, n, 30, clr, True)
        txt(sl, x + 0.2, 2.7, 3.2, 0.4, t, 14, DARK, True)
        txt(sl, x + 0.2, 3.1, 3.2, 0.4, sub, 11, GRAY)
    txt(sl, 0.8, 4.3, 11, 0.5, '传统模式的问题', 18, BLUE, True)
    pains = ['[1] 校门禁入 — 校外骑手无法进入宿舍区，学生需步行数百米取餐',
             '[2] 高峰拥堵 — 30+ 骑手同时在校门口，配送时效无法保证',
             '[3] 丢失错拿 — 外卖堆放地上，无管理无追溯，日均丢失率 3%-5%']
    mtxt(sl, 0.8, 4.9, 11.5, 2.0, pains, 14, DARK, Pt(10))

    # ---- SLIDE 5: Two-Stage Model ----
    sl = S(prs); bar(sl, '两段式配送模型', p())
    txt(sl, 0.5, 1.2, 12, 0.5, '核心思路：一条配送链拆为两段，宿舍楼寄存柜作为中转枢纽', 16, BLUE, True)
    # Stage 1
    s1 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(2.0), Inches(6.0), Inches(2.8))
    s1.fill.solid(); s1.fill.fore_color.rgb = LIGHT
    s1.line.color.rgb = BLUE; s1.line.width = Pt(2)
    txt(sl, 0.6, 2.15, 5.4, 0.4, '第一段：干线配送（商家  >  寄存点）', 16, BLUE, True)
    mtxt(sl, 0.6, 2.7, 5.4, 1.8, [
        '骑手：Stage1_Trunk（干线骑手 ×8）',
        '商家取餐  >  送达宿舍寄存柜',
        '技术：FOR UPDATE 行级锁防超卖',
        '约束：chk_capacity 物理容积上限',
    ], 13, DARK, Pt(6))
    # Stage 2
    s2 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.0), Inches(6.0), Inches(2.8))
    s2.fill.solid(); s2.fill.fore_color.rgb = LIGHT
    s2.line.color.rgb = GREEN; s2.line.width = Pt(2)
    txt(sl, 7.1, 2.15, 5.4, 0.4, '第二段：楼栋配送（寄存点  >  寝室）', 16, GREEN, True)
    mtxt(sl, 7.1, 2.7, 5.4, 1.8, [
        '骑手：Stage2_Floor（楼栋骑手 ×7）',
        '寄存柜取件  >  配送至学生寝室门口',
        '技术：骑手类型 ENUM 约束 + 自动状态管理',
        '优势：熟人熟路，一次可取多件批量配送',
    ], 13, DARK, Pt(6))
    txt(sl, 0.5, 5.2, 12, 1.0, '核心价值：校外骑手只送到寄存点（不进入宿舍区），楼栋骑手负责最后 100 米  ——  安全、高效、可追溯', 14, DARK, True)

    # ---- SLIDE 6: Six-State Machine ----
    sl = S(prs); bar(sl, '六态订单状态机', p())
    states = [
        ('Paid', '已支付\n待指派', BLUE),
        ('Stage1\nAssigned', '干线骑手\n已接单', RGBColor(0x45, 0x60, 0x97)),
        ('Arrived\nAt_Point', '已送达\n寄存点', GREEN),
        ('Stage2\nAssigned', '楼栋骑手\n已接单', RGBColor(0x2E, 0x7D, 0x32)),
        ('Completed', '已完成', RGBColor(0x1B, 0x5E, 0x20)),
        ('Cancelled', '已取消', RED),
    ]
    for i, (name, desc, clr) in enumerate(states):
        x = 0.2 + i * 2.15
        bx = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.0), Inches(1.8), Inches(1.3))
        bx.fill.solid(); bx.fill.fore_color.rgb = clr; bx.line.fill.background()
        tp = bx.text_frame.paragraphs[0]
        tp.text = name; tp.font.size = Pt(14); tp.font.color.rgb = WHITE; tp.font.bold = True; tp.font.name = FN; tp.alignment = PP_ALIGN.CENTER
        txt(sl, x, 3.45, 1.8, 0.5, desc, 9, GRAY, align=PP_ALIGN.CENTER)
        if i < len(states) - 2:
            txt(sl, x + 1.8, 2.3, 0.35, 0.4, '>', 16, GRAY)
    # Audit trail
    txt(sl, 0.5, 4.3, 12, 0.4, '全链路审计', 16, BLUE, True)
    mtxt(sl, 0.5, 4.8, 12, 2.0, [
        'created_at (下单)  >  stage1_completed_at (干线送达寄存柜)  >  stage2_completed_at (最终送达学生)',
        '三个 TIMESTAMP 精准追踪每一单的配送时效，任意环节出问题即可定位到具体订单和骑手',
        '订单状态与骑手状态联动：订单状态变更  >  触发器自动更新骑手 Idle / Delivering',
    ], 13, DARK, Pt(8))

    # ---- SLIDE 7: SECTION 02 ----
    section(prs, '02', '系统设计与数据库架构', '三层架构 · 技术栈 · ER 图 · 7 表 3NF')
    p()

    # ---- SLIDE 8: System Architecture ----
    sl = S(prs); bar(sl, '系统三层架构', p())
    arch = [
        ('展现层', 'Flask + ECharts', 'localhost:5000 实时监控\n3 个 Tab：总览 | 订单管理 | 爆仓预警', BLUE),
        ('业务层', 'Python + 4 存储过程', 'sp_create_order / sp_arrive / sp_stage2 / sp_cancel\nAI Text-to-SQL (DeepSeek)', GREEN),
        ('数据层', 'MySQL 8.0 InnoDB', '7 表 | 4 索引 | 7 触发器 | 2 视图\nFOR UPDATE 行级锁 | CHECK 约束 | FK 级联', ORANGE),
    ]
    for i, (layer, tech, desc, clr) in enumerate(arch):
        y = 1.5 + i * 1.8
        bx = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(11.5), Inches(1.4))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE
        bx.line.color.rgb = clr; bx.line.width = Pt(2)
        bd = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(1.8), Inches(1.4))
        bd.fill.solid(); bd.fill.fore_color.rgb = clr; bd.line.fill.background()
        tp = bd.text_frame.paragraphs[0]
        tp.text = layer; tp.font.size = Pt(18); tp.font.color.rgb = WHITE; tp.font.bold = True; tp.font.name = FN; tp.alignment = PP_ALIGN.CENTER
        txt(sl, 2.9, y + 0.1, 1.8, 0.4, tech, 14, clr, True)
        mtxt(sl, 5.0, y + 0.15, 7, 1.0, desc.split('\n'), 12, DARK, Pt(4))

    # ---- SLIDE 9: Tech Stack ----
    sl = S(prs); bar(sl, '技术栈', p())
    techs = [
        ('MySQL 8.0', 'InnoDB · FOR UPDATE · 窗口函数', BLUE),
        ('Python + Flask', 'REST API · PyMySQL · AI 集成', GREEN),
        ('ECharts', '3 个功能 Tab · 30 秒自动刷新', ORANGE),
        ('DeepSeek', 'Text-to-SQL · Schema 注入', RGBColor(0x7B, 0x1F, 0xA2)),
        ('Cloudflare', '公网隧道 · 扫码即访问', RGBColor(0x00, 0x96, 0x88)),
    ]
    for i, (name, desc, clr) in enumerate(techs):
        x = 0.3 + i * 2.55
        card(sl, x, 1.5, 2.3, 2.2, name, desc.split('·'), clr)

    txt(sl, 0.5, 4.2, 12, 0.4, '数据库层核心技术栈', 18, BLUE, True)
    db_items = [
        '7 张表 · 严格 3NF  ·  5 个外键级联约束',
        '4 个 B-Tree 索引 · 含 2 个复合索引覆盖高频查询',
        '7 个触发器（防护盾）· FOR UPDATE 行级锁 · SIGNAL 异常拦截 · 骑手状态自动管理',
        '4 个存储过程 · EXPLICIT TRANSACTION + ROLLBACK · 游标遍历恢复库存',
        '2 个分析视图 · RANK() OVER 窗口函数 · 饱和度预警',
    ]
    mtxt(sl, 0.5, 4.8, 12, 2.5, db_items, 13, DARK, Pt(8))

    # ---- SLIDE 10: ER Diagram ----
    sl = S(prs); bar(sl, '数据库 E-R 图：7 张核心表 · 严格 3NF', p())
    img_w(sl, ER, 0.5, 1.1, 12.3)

    # ---- SLIDE 11: 7 Tables Overview ----
    sl = S(prs); bar(sl, '7 张核心表概览', p())
    rows = [
        ['users', '学生用户', 'user_id PK, username, phone(UNIQUE), balance CHECK(>=0)'],
        ['merchants', '商家', 'merchant_id PK, rating CHECK(1~5)'],
        ['dishes', '菜品', 'dish_id PK, stock CHECK(>=0), status CHECK(0/1), FK -> merchants'],
        ['pickup_points', '寄存点', 'point_id PK, capacity, current_packages, chk_capacity CHECK'],
        ['riders', '骑手', 'rider_id PK, rider_type ENUM, status ENUM(Idle/Delivering/Offline)'],
        ['orders', '订单', 'order_id PK, 6态ENUM, 双骑手FK, 3时间戳, 5个FK'],
        ['order_items', '订单明细', 'item_id PK, quantity, price_at_order, FK -> orders(CASCADE)'],
    ]
    # Split table into two columns
    tbl(sl, 0.3, 1.3, [1.6, 1.3, 3.2, 6.0], ['表名', '中文', '核心约束', '关键字段'], rows, 11)
    txt(sl, 0.5, 5.2, 12, 0.5, '设计原则', 16, BLUE, True)
    mtxt(sl, 0.5, 5.8, 12, 1.0, [
        '严格 3NF 消除冗余 · 5 个外键级联保证引用完整 · CHECK 约束在数据库层强制执行业务规则 · ENUM 类型限死合法值',
    ], 13, DARK)

    # ---- SLIDE 12: pickup_points detail ----
    sl = S(prs); bar(sl, '关键表：pickup_points —— 物理容积硬约束', p())
    code(sl, 0.5, 1.3, 6.0, 2.5, [
        'CREATE TABLE pickup_points (',
        '  point_id   INT PRIMARY KEY AUTO_INCREMENT,',
        '  point_name VARCHAR(50)  NOT NULL,         -- 寄存点名称',
        '  capacity   INT          NOT NULL,          -- 最大格子数',
        '  current_packages INT DEFAULT 0',
        '    CHECK (current_packages >= 0),',
        '',
        '  CONSTRAINT chk_capacity                   -- ← 核心约束',
        '    CHECK (current_packages <= capacity)     -- 80格绝不81包',
        ');',
    ], 12)
    txt(sl, 0.5, 3.9, 6.0, 0.4, '设计要点', 15, BLUE, True)
    mtxt(sl, 0.5, 4.4, 6.0, 2.5, [
        'chk_capacity 是物理底限  ——  80 个格子绝不允许 81 个包裹写入',
        'current_packages 由存储过程 +1/-1 维护，不开放直接修改',
        '12 个寄存点覆盖全校宿舍区，容量从 50 到 120 格',
    ], 13, DARK, Pt(6))
    txt(sl, 7.0, 1.3, 5.5, 0.4, 'riders —— 两段式特种骑手', 15, BLUE, True)
    code(sl, 7.0, 1.9, 5.5, 1.8, [
        'CREATE TABLE riders (',
        '  rider_id   INT PRIMARY KEY AUTO_INCREMENT,',
        "  rider_type ENUM('Stage1_Trunk',           -- 干线",
        "                     'Stage2_Floor') NOT NULL, -- 楼栋",
        "  status     ENUM('Idle','Delivering',",
        "                     'Offline') DEFAULT 'Idle',",
        ');',
    ], 12)
    txt(sl, 7.0, 3.9, 5.5, 0.4, '设计要点', 15, BLUE, True)
    mtxt(sl, 7.0, 4.4, 5.5, 2.5, [
        'ENUM 在数据库层强制分工  ——  Stage1_Trunk 不能做楼栋配送',
        'status 由触发器自动管理，应用层无需手动更新',
        '8 干线 + 7 楼栋 = 15 骑手，两个骑手独立绑定同一订单',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 13: orders detail ----
    sl = S(prs); bar(sl, '核心表：orders —— 六态状态机 + 双骑手 + 三时间戳', p())
    code(sl, 0.3, 1.2, 7.0, 4.5, [
        'CREATE TABLE orders (',
        '  order_id        INT PRIMARY KEY AUTO_INCREMENT,',
        '',
        '  -- 六态状态机',
        "  order_status    ENUM('Paid', 'Stage1_Assigned',",
        "       'Arrived_At_Point','Stage2_Assigned',",
        "       'Completed','Cancelled'),",
        '',
        '  -- 双骑手绑定',
        '  stage1_rider_id INT,  -- FK -> riders  干线骑手',
        '  stage2_rider_id INT,  -- FK -> riders  楼栋骑手',
        '',
        '  -- 全链路审计',
        '  created_at            TIMESTAMP,  -- 下单时间',
        '  stage1_completed_at   TIMESTAMP,  -- 干线送达',
        '  stage2_completed_at   TIMESTAMP,  -- 最终送达',
        '',
        '  -- 5 个外键: users, merchants, pickup_points,',
        '  --           stage1_rider, stage2_rider',
        ');',
    ], 11)

    txt(sl, 7.6, 1.2, 5.2, 0.4, '六态状态机流转', 15, BLUE, True)
    flow = [
        'Paid  >  Stage1_Assigned  >  Arrived_At_Point',
        '  >  Stage2_Assigned  >  Completed',
        '',
        '任意非终态  >  Cancelled（退款 + 恢复库存）',
    ]
    mtxt(sl, 7.6, 1.7, 5.2, 1.5, flow, 13, DARK, Pt(6))

    txt(sl, 7.6, 3.3, 5.2, 0.4, '设计亮点', 15, BLUE, True)
    highlights = [
        'ENUM 限死 6 种合法状态，杜绝脏数据',
        '双骑手独立绑定，同时追踪两段配送进度',
        '3 个时间戳精准审计全链路时效',
        '5 个外键保证引用完整性',
    ]
    mtxt(sl, 7.6, 3.8, 5.2, 2.5, highlights, 13, DARK, Pt(6))

    # ---- SLIDE 14: Six-state flow detail ----
    sl = S(prs); bar(sl, '状态机流转详解', p())
    # Show each state with what triggers
    flow_data = [
        ('Paid', '已支付，待指派干线骑手', 'sp_create_order 创建'),
        ('Stage1_Assigned', '干线骑手接单，前往商家取餐', '指派 stage1_rider_id'),
        ('Arrived_At_Point', '干线骑手送达寄存柜（包裹入库）', 'sp_arrive_at_pickup_point'),
        ('Stage2_Assigned', '楼栋骑手接单，从柜中取件', '指派 stage2_rider_id'),
        ('Completed', '楼栋骑手送达学生手中', 'sp_stage2_deliver'),
        ('Cancelled', '订单取消，退款+恢复库存', 'sp_cancel_order'),
    ]
    tbl(sl, 0.3, 1.3, [2.0, 3.2, 3.5, 3.5], ['状态', '含义', '触发操作', '骑手状态联动'],
        [[s, m, t, ''] for s, m, t in flow_data], 11)
    txt(sl, 0.5, 4.8, 12, 0.4, '自动联动', 15, BLUE, True)
    mtxt(sl, 0.5, 5.3, 12, 1.5, [
        '订单 Stage1_Assigned  >  触发器  >  干线骑手 status = Delivering',
        '订单 Arrived_At_Point  >  触发器  >  干线骑手 status = Idle（释放）',
        '订单 Completed  >  触发器  >  楼栋骑手 status = Idle（释放）',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 15: SECTION 03 ----
    section(prs, '03', '索引策略与性能优化', '4 个 B-Tree 索引 · 复合索引 · 覆盖查询 · 视图加速')
    p()

    # ---- SLIDE 16: Indexes ----
    sl = S(prs); bar(sl, '4 个 B-Tree 索引', p())
    idx_rows = [
        ['idx_orders_status', 'orders', 'order_status', '大屏按状态筛选（最高频查询）'],
        ['idx_orders_created', 'orders', 'created_at', '时间范围查询（今日/近7天/近30天）'],
        ['idx_dishes_merchant', 'dishes', 'merchant_id, status', '点餐页"查某商家在售菜品"'],
        ['idx_orders_point_status', 'orders', 'pickup_point_id, order_status', '容量检查 + 视图 LEFT JOIN 加速'],
    ]
    tbl(sl, 0.3, 1.3, [2.6, 1.2, 2.6, 6.0], ['索引名', '表', '索引列', '加速场景'], idx_rows, 12)
    txt(sl, 0.5, 4.0, 12, 0.4, '为什么需要 idx_orders_point_status？', 15, GREEN, True)
    mtxt(sl, 0.5, 4.5, 12, 2.0, [
        '这是本次新增的第 4 个索引。原因是 vw_pickup_point_analytics 视图的核心查询是：',
        "  SELECT ... FROM orders WHERE order_status IN ('Arrived_At_Point','Stage2_Assigned') GROUP BY pickup_point_id",
        '没有索引时，这条查询需要全表扫描 orders（5000+ 行）做 WHERE 过滤再 GROUP BY，每次大屏刷新都重复',
        '加上复合索引 (pickup_point_id, order_status) 后，MySQL 直接用索引覆盖查询，不需要回表，查询时间从 ~50ms 降到 ~2ms',
        '同时加速 sp_create_order 中的 SELECT...FOR UPDATE 容量预检 —— 索引定位行更快，锁持有时间更短',
    ], 12, DARK, Pt(6))

    # ---- SLIDE 17: SECTION 04 ----
    section(prs, '04', '七重触发器防护盾', 'FOR UPDATE 行级锁 · 库存防超卖 · 骑手约束 · 状态管理 · 容量预检')
    p()

    # ---- SLIDE 18: FOR UPDATE concept ----
    sl = S(prs); bar(sl, 'FOR UPDATE 行级锁：并发的正确解法', p())
    # Left: problem
    txt(sl, 0.5, 1.2, 5.5, 0.4, '问题：传统 SELECT 有竞态窗口', 16, RED, True)
    code(sl, 0.5, 1.7, 5.5, 1.3, [
        '-- T1: Session A 读库存',
        "SELECT stock FROM dishes WHERE dish_id=1;     -- stock=1",
        '-- T2: Session B 读库存',
        "SELECT stock FROM dishes WHERE dish_id=1;     -- stock=1",
        '',
        '-- 两个都看到 stock=1  →  两个都下单  →  超卖!',
    ], 11)
    txt(sl, 0.5, 3.2, 5.5, 1.0, '原因：SELECT 和 UPDATE 之间有时间差\n两个事务同时读到旧值，都判断库存够', 13, RED)
    # Right: solution
    txt(sl, 7.0, 1.2, 5.5, 0.4, '解决：FOR UPDATE 排他锁', 16, GREEN, True)
    code(sl, 7.0, 1.7, 5.5, 1.8, [
        '-- Session A',
        'SELECT stock FROM dishes',
        '  WHERE dish_id=1 FOR UPDATE;   -- 加 X 锁',
        '',
        '-- Session B（并发执行）',
        'SELECT stock FROM dishes',
        '  WHERE dish_id=1 FOR UPDATE;   -- 阻塞等待!',
        '',
        '-- A 提交后 B 读到新值 stock=0  →  正确拒绝',
    ], 11)
    txt(sl, 7.0, 3.7, 5.5, 1.5, 'FOR UPDATE 将"读-判断-写"原子化\nA 加锁  >  B 等待  >  A 提交释放  >  B 读新值\n这是数据库层解决并发超卖的唯一正确手段', 13, GREEN)

    txt(sl, 0.5, 4.5, 12, 0.4, '在本系统的实际应用', 15, BLUE, True)
    mtxt(sl, 0.5, 5.0, 12, 1.8, [
        '触发器 1 (trg_check_dish_stock_before_order)：BEFORE INSERT ON order_items 时 FOR UPDATE 锁定菜品行，读库存+判断+拒绝一气呵成',
        '触发器 7 (trg_check_pickup_point_capacity)：BEFORE INSERT ON orders 时 FOR UPDATE 锁定寄存点行，查容量+判断满否+拒绝',
        'sp_create_order：下单流程中 FOR UPDATE 锁定寄存点行做容量预检',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 19: Trigger 1-2 Stock ----
    sl = S(prs); bar(sl, '触发器 1-2：库存防超卖', p())
    # Trigger 1
    txt(sl, 0.3, 1.2, 6.0, 0.3, 'trg_check_dish_stock_before_order', 15, BLUE, True)
    txt(sl, 0.3, 1.55, 6.0, 0.25, 'BEFORE INSERT ON order_items', 11, GRAY)
    code(sl, 0.3, 1.9, 6.0, 1.2, [
        'SELECT stock, status INTO v_stock, v_status',
        'FROM dishes WHERE dish_id = NEW.dish_id',
        'FOR UPDATE;  -- 排他锁锁定该菜品行',
        '',
        'IF v_status = 0 THEN           -- 下架检查',
        "  SIGNAL '商品已下架!';",
        'END IF;',
        'IF v_stock < NEW.quantity THEN  -- 库存检查',
        "  SIGNAL '库存不足!';",
        'END IF;',
    ], 11)

    txt(sl, 0.3, 3.3, 6.0, 0.3, '解决了什么问题？', 14, GREEN, True)
    mtxt(sl, 0.3, 3.7, 6.0, 1.5, [
        '并发超卖：两个用户同时买最后一份库存',
        '  >  FOR UPDATE 让第二个事务等待第一个释放',
        '  >  第二个读到库存=0，正确拒绝',
        '下架保护：已下架菜品自动拦截，无需应用层判断',
    ], 12, DARK, Pt(4))

    # Trigger 2
    txt(sl, 6.8, 1.2, 5.5, 0.3, 'trg_reduce_dish_stock_after_order', 15, BLUE, True)
    txt(sl, 6.8, 1.55, 5.5, 0.25, 'AFTER INSERT ON order_items', 11, GRAY)
    code(sl, 6.8, 1.9, 5.5, 0.7, [
        'UPDATE dishes',
        'SET stock = stock - NEW.quantity',
        'WHERE dish_id = NEW.dish_id;',
    ], 11)
    txt(sl, 6.8, 2.8, 5.5, 0.3, '为什么 AFTER 而不是 BEFORE？', 14, GREEN, True)
    mtxt(sl, 6.8, 3.2, 5.5, 2.0, [
        '只有 Trig 1 通过所有校验后才执行',
        'Trig 1 拒绝  >  Trig 2 不触发  >  不扣库存',
        '两个触发器在同一事务内，保证原子性',
    ], 12, DARK, Pt(4))

    # ---- SLIDE 20: Trigger 3-4 Rider Type ----
    sl = S(prs); bar(sl, '触发器 3-4：骑手类型约束', p())
    txt(sl, 0.5, 1.15, 12, 0.35, '解决什么问题？防止把楼栋骑手错误指派为干线骑手（或反过来），业务全乱', 14, DARK)
    txt(sl, 0.3, 1.7, 6.0, 0.3, 'trg_check_rider_type_before_insert', 15, BLUE, True)
    code(sl, 0.3, 2.1, 6.0, 1.2, [
        'BEFORE INSERT ON orders FOR EACH ROW',
        '',
        'IF NEW.stage1_rider_id IS NOT NULL THEN',
        '  IF NOT EXISTS (SELECT 1 FROM riders',
        "    WHERE rider_id=NEW.stage1_rider_id",
        "      AND rider_type='Stage1_Trunk') THEN",
        "    SIGNAL '干线骑手必须是 Stage1_Trunk!';",
        '  END IF;',
        'END IF;',
        '-- 同理检查 stage2_rider_id -> Stage2_Floor',
    ], 11)
    txt(sl, 0.3, 3.5, 6.0, 0.3, 'trg_check_rider_type_before_update', 15, GREEN, True)
    code(sl, 0.3, 3.9, 6.0, 1.0, [
        'BEFORE UPDATE ON orders FOR EACH ROW',
        '-- 仅在骑手ID变化时校验（性能优化）',
        'IF NEW.stage1_rider_id != OLD.stage1_rider_id',
        '   OR OLD.stage1_rider_id IS NULL THEN',
        '  -- 检查新骑手类型',
        'END IF;',
    ], 11)
    txt(sl, 6.8, 1.7, 5.5, 3.0, '', 12, DARK)
    mtxt(sl, 6.8, 1.7, 5.5, 3.0, [
        'INSERT + UPDATE 双触发器覆盖所有指派路径：',
        '',
        '新建订单同时指派骑手  >  INS 触发器拦截',
        '已有订单更换骑手    >  UPD 触发器拦截',
        '',
        '与 riders 表的 ENUM 形成双重保护：',
        'ENUM 保证 rider_type 只有合法值',
        '触发器保证用法正确（对的类型做对的活）',
    ], 12, DARK, Pt(6))

    # ---- SLIDE 21: Trigger 5-6 Rider Status ----
    sl = S(prs); bar(sl, '触发器 5-6：骑手状态自动管理', p())
    txt(sl, 0.5, 1.15, 12, 0.35, '解决什么问题？应用层不需要手动 UPDATE riders SET status，所有状态转换由数据库自动完成，杜绝遗漏', 14, DARK)
    rows = [
        ['指派干线骑手', 'Paid  >  Stage1_Assigned', 'Idle  >  Delivering', 'AFTER INSERT/UPDATE'],
        ['干线送达', 'Stage1_Assigned  >  Arrived_At_Point', 'Delivering  >  Idle', 'AFTER UPDATE 检测状态'],
        ['指派楼栋骑手', 'Arrived_At_Point  >  Stage2_Assigned', 'Idle  >  Delivering', 'AFTER UPDATE 检测新骑手'],
        ['楼栋送达', 'Stage2_Assigned  >  Completed', 'Delivering  >  Idle', 'AFTER UPDATE 检测状态'],
        ['订单取消', '任意  >  Cancelled', 'Delivering  >  Idle', 'AFTER UPDATE 释放所有骑手'],
    ]
    tbl(sl, 0.3, 1.7, [2.0, 3.5, 3.0, 3.5], ['事件', '订单状态变化', '骑手状态转换', '触发方式'], rows, 11)
    txt(sl, 0.5, 4.5, 12, 0.4, '代码示意', 15, BLUE, True)
    code(sl, 0.5, 5.0, 5.8, 1.5, [
        '-- trg_rider_delivering_update 核心逻辑',
        '',
        '-- [1] 新指派  >  Delivering',
        'IF stage1_rider_id 发生变化 THEN',
        "  UPDATE riders SET status='Delivering';",
        'END IF;',
        '',
        '-- [2] Stage1 完成  >  释放干线骑手',
        "IF NEW.order_status='Arrived_At_Point' THEN",
        "  UPDATE riders SET status='Idle';",
        'END IF;',
    ], 11)
    txt(sl, 7.0, 5.0, 5.5, 1.5, '核心价值：状态一改，骑手自动释放\n触发器 = 状态机的执行器\n省去所有应用层的手动状态同步代码', 14, GREEN)

    # ---- SLIDE 22: Trigger 7 Capacity Pre-Check ----
    sl = S(prs); bar(sl, '触发器 7：寄存点容量预检 —— 防止骑手白跑', p())
    txt(sl, 0.3, 1.2, 6.0, 0.3, 'trg_check_pickup_point_capacity（新增）', 15, BLUE, True)
    txt(sl, 0.3, 1.55, 6.0, 0.25, 'BEFORE INSERT ON orders', 11, GRAY)
    code(sl, 0.3, 1.9, 6.0, 1.1, [
        'SELECT current_packages, capacity',
        'INTO v_pt_current, v_pt_capacity',
        'FROM pickup_points',
        'WHERE point_id = NEW.pickup_point_id',
        'FOR UPDATE;  -- 锁定寄存点行',
        '',
        'IF v_pt_current >= v_pt_capacity THEN',
        "  SIGNAL '该寄存点已满!';",
        'END IF;',
    ], 11)

    txt(sl, 0.3, 3.2, 6.0, 0.3, '之前的问题', 14, RED, True)
    mtxt(sl, 0.3, 3.6, 6.0, 1.0, [
        '只有 chk_capacity — 入库时才拦截',
        '骑手已完成配送，扫码入库  >  柜满  >  ROLLBACK',
        '骑手白跑一趟，成果被抹掉',
    ], 12, DARK, Pt(4))
    txt(sl, 0.3, 4.8, 6.0, 0.3, '加入后的效果', 14, GREEN, True)
    mtxt(sl, 0.3, 5.2, 6.0, 1.0, [
        '下单时 FOR UPDATE 查容量  >  满  >  直接拒绝',
        '用户换邻近寄存点，骑手不会送到一个满柜',
    ], 12, DARK, Pt(4))

    # Right: two-layer protection
    txt(sl, 6.8, 1.2, 5.5, 0.3, '两层防护体系', 16, BLUE, True)
    # Layer 1
    l1 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.5), Inches(1.2))
    l1.fill.solid(); l1.fill.fore_color.rgb = RGBColor(0xE8, 0xF5, 0xE9)
    l1.line.color.rgb = GREEN; l1.line.width = Pt(2)
    txt(sl, 7.0, 1.9, 5.1, 0.3, '第一层：下单容量预检（主动）', 14, GREEN, True)
    mtxt(sl, 7.0, 2.3, 5.1, 0.6, [
        'trg + sp_create_order  双保险',
        'FOR UPDATE 防并发容量击穿',
    ], 11, DARK, Pt(3))
    # Layer 2
    l2 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(3.3), Inches(5.5), Inches(1.2))
    l2.fill.solid(); l2.fill.fore_color.rgb = RGBColor(0xFF, 0xEB, 0xEE)
    l2.line.color.rgb = RED; l2.line.width = Pt(2)
    txt(sl, 7.0, 3.4, 5.1, 0.3, '第二层：物理硬约束（被动兜底）', 14, RED, True)
    mtxt(sl, 7.0, 3.8, 5.1, 0.6, [
        'chk_capacity CHECK 约束',
        '极端并发绕过时最后一关',
    ], 11, DARK, Pt(3))
    # Answer the key question
    txt(sl, 6.8, 5.0, 5.5, 1.5, '爆仓 = 柜子满了不让订这个柜\n不是不让订外卖，是引导\n用户选别的寄存点', 16, DARK)

    # ---- SLIDE 23: 7 Triggers Summary ----
    sl = S(prs); bar(sl, '七重触发器总览', p())
    srows = [
        ['1', '库存防超卖 (检查)', 'BEFORE INSERT', 'order_items', 'FOR UPDATE 锁行  >  验库存+下架  >  SIGNAL'],
        ['2', '库存防超卖 (扣减)', 'AFTER INSERT', 'order_items', 'stock = stock - quantity'],
        ['3', '骑手类型校验', 'BEFORE INSERT', 'orders', 'stage1 必须是 Trunk, stage2 必须是 Floor'],
        ['4', '骑手类型校验', 'BEFORE UPDATE', 'orders', '同 #3，仅在骑手变更时触发（性能优化）'],
        ['5', '骑手状态管理', 'AFTER INSERT', 'orders', '指派骑手  >  自动设为 Delivering'],
        ['6', '骑手状态管理', 'AFTER UPDATE', 'orders', '完成/取消  >  自动释放为 Idle'],
        ['7', '容量预检 (NEW!)', 'BEFORE INSERT', 'orders', 'FOR UPDATE 查柜容量  >  满则拒'],
    ]
    tbl(sl, 0.3, 1.3, [0.4, 2.8, 1.6, 1.6, 6.0], ['#', '功能', '时机', '表', '核心逻辑'], srows, 10)
    txt(sl, 0.5, 5.5, 12, 1.0, '分类：库存管理 x2 | 骑手类型约束 x2 | 状态自动管理 x2 | 容量预检 x1\n技术：FOR UPDATE 行级锁 | SIGNAL 异常拦截 | OLD/NEW 状态对比 | ENUM+NOT EXISTS', 12, GRAY)

    # ---- SLIDE 24: Trigger detail - stock FOR UPDATE in practice ----
    sl = S(prs); bar(sl, 'FOR UPDATE 实测：并发下单场景演示', p())
    code(sl, 0.3, 1.2, 3.8, 2.5, [
        '-- 同一道菜，只剩 1 份库存',
        '-- 两个学生同时下单',
        '',
        '-- Session A（先到，加锁成功）',
        'START TRANSACTION;',
        'SELECT stock FROM dishes',
        "  WHERE dish_id=1 FOR UPDATE;  -- stock=1",
        "INSERT INTO order_items ...     -- 扣到 0",
        'COMMIT;                       -- 释放锁',
    ], 11)
    code(sl, 4.3, 1.2, 3.8, 2.5, [
        '-- Session B（后到，等待锁）',
        'START TRANSACTION;',
        'SELECT stock FROM dishes',
        "  WHERE dish_id=1 FOR UPDATE;  -- 阻塞...",
        '-- A 提交后，B 获得锁',
        "  -- stock=0 < quantity=1",
        "  -- SIGNAL '库存不足!'",
        'ROLLBACK;',
        '-- B 的下单请求被正确拒绝',
    ], 11)
    txt(sl, 8.5, 1.2, 4.5, 0.3, '没有 FOR UPDATE 会怎样？', 14, RED, True)
    mtxt(sl, 8.5, 1.7, 4.3, 2.0, [
        'A: SELECT stock=1',
        'B: SELECT stock=1  (也读到 1)',
        'A: INSERT + stock=0',
        'B: INSERT + stock=-1  !!!',
        '超卖！库存变成负数！',
    ], 12, DARK, Pt(4))
    txt(sl, 0.5, 4.2, 12, 0.3, '核心结论', 15, BLUE, True)
    mtxt(sl, 0.5, 4.7, 12, 2.0, [
        'FOR UPDATE 是数据库课程的核心考点 —— 将"读-判断-写"三步变成原子的一个操作',
        '应用层 synchronized / Redis 分布式锁 / 乐观锁重试 —— 都不如数据库层的 FOR UPDATE 简洁可靠',
        '本系统在两个关键场景使用它：库存检查（触发器1）和容量预检（触发器7 + sp_create_order）',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 25: SECTION 05 ----
    section(prs, '05', '存储过程与事务管理', '4 个存储过程 · ACID 事务 · ROLLBACK 回滚 · 游标')
    p()

    # ---- SLIDE 26: sp_create_order ----
    sl = S(prs); bar(sl, 'sp_create_order：原子下单（四步一事务）', p())
    steps = [
        ('[1] 容量预检', 'FOR UPDATE 锁寄存点行 > 查 capacity > 满则拒', BLUE),
        ('[2] 余额检查', '查 users.balance > 不足 SIGNAL', BLUE),
        ('[3] 扣款 + 插订单', 'UPDATE balance + INSERT INTO orders', GREEN),
        ('[4] 插明细（触发锁库存）', 'INSERT INTO order_items > 触发 Trig 1(FOR UPDATE 验库存) > 触发 Trig 2(扣库存)', GREEN),
    ]
    for i, (title, desc, clr) in enumerate(steps):
        y = 1.3 + i * 0.9
        number_badge(sl, 0.5, y + 0.05, i + 1, clr)
        txt(sl, 1.2, y + 0.05, 3.0, 0.4, title, 15, clr, True)
        txt(sl, 4.5, y + 0.05, 8.0, 0.5, desc, 13, DARK)
    txt(sl, 0.5, 5.0, 12, 0.4, '事务保护', 15, BLUE, True)
    mtxt(sl, 0.5, 5.5, 12, 1.5, [
        'START TRANSACTION > 四步全部成功 > COMMIT',
        '任一环节失败 > EXIT HANDLER 捕获 > ROLLBACK（扣款+订单+明细全撤销）> RESIGNAL 向上抛错',
        '这是 ACID 中 A（原子性）的教科书级实现',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 27: Two-stage SPs ----
    sl = S(prs); bar(sl, '两段配送存储过程', p())
    # Left: Stage1 Arrival
    txt(sl, 0.3, 1.2, 6.0, 0.3, 'sp_arrive_at_pickup_point —— 干线入库', 15, BLUE, True)
    code(sl, 0.3, 1.6, 6.0, 2.0, [
        'START TRANSACTION;',
        '',
        '-- Step 1: 状态跳转 + 打时间戳',
        "UPDATE orders SET order_status='Arrived_At_Point',",
        '  stage1_completed_at=CURRENT_TIMESTAMP',
        '  WHERE order_id=p_order_id;',
        '',
        '-- Step 2: 寄存点计数 +1（触发 chk_capacity）',
        'UPDATE pickup_points',
        '  SET current_packages=current_packages+1',
        '  WHERE point_id=v_point_id;',
        '',
        '-- 触发器自动: 干线骑手  >  Idle',
        'COMMIT;',
    ], 11)

    txt(sl, 0.3, 3.8, 6.0, 0.3, '爆仓时', 14, RED, True)
    mtxt(sl, 0.3, 4.2, 6.0, 1.5, [
        'Step 2 中 chk_capacity 拒绝  >  ROLLBACK',
        'Step 1 的状态和时间戳也回滚',
        '订单回到 Stage1_Assigned',
        '改进方向：引入"已到达等空位"中间态',
    ], 12, DARK, Pt(4))

    # Right: Stage2 Delivery
    txt(sl, 6.8, 1.2, 5.5, 0.3, 'sp_stage2_deliver —— 最终送达', 15, GREEN, True)
    code(sl, 6.8, 1.6, 5.5, 1.3, [
        'START TRANSACTION;',
        '',
        "UPDATE orders SET order_status='Completed',",
        '  stage2_completed_at=CURRENT_TIMESTAMP',
        '  WHERE order_id=p_order_id;',
        '',
        'UPDATE pickup_points',
        '  SET current_packages=current_packages-1',
        '  WHERE point_id=v_point_id',
        '    AND current_packages>0;  -- 保护',
        '',
        '-- 触发器自动: 楼栋骑手  >  Idle',
        'COMMIT;',
    ], 11)

    txt(sl, 6.8, 3.2, 5.5, 0.3, 'sp_cancel_order —— 取消退款', 15, BLUE, True)
    mtxt(sl, 6.8, 3.6, 5.5, 2.5, [
        '用游标遍历 order_items > 逐道菜恢复库存',
        '已入库的包裹 > current_packages - 1',
        '退款到学生钱包',
        '触发器自动释放所有骑手  >  Idle',
    ], 12, DARK, Pt(4))

    # ---- SLIDE 28: SECTION 06 ----
    section(prs, '06', '视图与窗口函数', '饱和度预警 · RANK() OVER · AI Text-to-SQL')
    p()

    # ---- SLIDE 29: Views ----
    sl = S(prs); bar(sl, '2 个分析视图', p())
    # View 1
    txt(sl, 0.3, 1.2, 6.0, 0.3, 'vw_pickup_point_analytics —— 饱和度预警', 15, BLUE, True)
    code(sl, 0.3, 1.6, 6.0, 2.0, [
        'CREATE VIEW vw_pickup_point_analytics AS',
        'SELECT',
        '  p.point_name,',
        '  p.capacity AS max_capacity,',
        '  p.current_packages,',
        '  ROUND(p.current_packages/p.capacity*100, 2)',
        '    AS saturation_pct,       -- 饱和度%',
        '  sub.backlog_count',
        'FROM pickup_points p',
        'LEFT JOIN (',
        "  SELECT pickup_point_id, COUNT(*) cnt",
        '  FROM orders',
        "  WHERE order_status IN ('Arrived_At_Point',",
        "                          'Stage2_Assigned')",
        '  GROUP BY pickup_point_id',
        ') sub ON p.point_id=sub.pickup_point_id;',
    ], 9)
    mtxt(sl, 0.3, 3.8, 6.0, 2.0, [
        '驱动大屏"爆仓预警" Tab',
        '> 80% = 黄色预警  |  = 100% = 红色爆仓',
        '每 30 秒查询一次，数据实时更新',
    ], 12, DARK, Pt(4))

    # View 2
    txt(sl, 6.8, 1.2, 5.5, 0.3, 'vw_merchant_sales_rank —— 销售排行', 15, GREEN, True)
    code(sl, 6.8, 1.6, 5.5, 1.3, [
        'CREATE VIEW vw_merchant_sales_rank AS',
        'SELECT',
        '  m.merchant_name,',
        '  COUNT(DISTINCT o.order_id) orders,',
        '  SUM(o.total_amount) total_sales,',
        '  RANK() OVER (',
        '    ORDER BY SUM(o.total_amount) DESC',
        '  ) AS sales_rank',
        'FROM merchants m',
        'LEFT JOIN orders o',
        "  ON m.merchant_id=o.merchant_id",
        "  AND o.order_status='Completed'",
        'GROUP BY m.merchant_id;',
    ], 9)
    txt(sl, 6.8, 3.2, 5.5, 0.3, 'RANK() OVER 窗口函数', 14, GREEN, True)
    mtxt(sl, 6.8, 3.6, 5.5, 2.5, [
        '一行 SQL 完成排名，数据库引擎优化执行',
        '传统做法：子查询 + 变量，复杂且易错',
        'RANK()：同销售额并列排名（1,2,2,4）',
        '仅统计 Completed 订单，排除未完成干扰',
    ], 12, DARK, Pt(4))

    # ---- SLIDE 30: AI Text-to-SQL ----
    sl = S(prs); bar(sl, 'AI Text-to-SQL：自然语言查数据', p())
    txt(sl, 0.5, 1.2, 12, 0.4, '集成 DeepSeek API，搜索框输入中文  >  AI 生成 SQL  >  数据库执行  >  返回结果', 15, BLUE, True)
    # Examples
    examples = [
        ('输入', 'AI 生成的 SQL', '结果'),
        ('"今天卖了多少钱？"', 'SELECT SUM(total_amount) FROM orders WHERE...', '12,580 元'),
        ('"哪个寄存点快满了？"', 'SELECT point_name,saturation_pct FROM vw_pickup...', '3期 = 100%'),
        ('"哪个商家最受欢迎？"', 'SELECT * FROM vw_merchant_sales_rank LIMIT 1', '蜜雪冰城'),
    ]
    tbl(sl, 0.5, 1.9, [3.0, 5.5, 3.5], examples[0], examples[1:], 11)
    txt(sl, 0.5, 4.0, 12, 0.4, '技术实现', 15, BLUE, True)
    mtxt(sl, 0.5, 4.5, 12, 2.0, [
        'Schema 注入：系统提示词包含完整的 7 张表结构、字段说明、ENUM 值、视图信息',
        '安全限制：仅允许 SELECT 语句，禁止 INSERT/UPDATE/DELETE/DROP — 防止 AI 幻觉导致数据损坏',
        '透明展示：前端同时显示生成的 SQL 和查询结果，用户可以看到 AI 的逻辑',
        '成本极低：DeepSeek API，单次查询 < 0.01 元人民币',
    ], 13, DARK, Pt(6))

    # ---- SLIDE 31: SECTION 07 ----
    section(prs, '07', '系统大屏与可视化展示', 'Flask + ECharts 实时监控 · 3 个功能 Tab')
    p()

    # ---- SLIDE 32: Dashboard Overview ----
    sl = S(prs); bar(sl, '大屏总览', p())
    img_w(sl, os.path.join(IMG, '01_dashboard_overview.png'), 0.3, 1.1, 12.5)

    # ---- SLIDE 33: KPI + Order Section ----
    sl = S(prs); bar(sl, 'KPI 指标卡', p())
    img_w(sl, os.path.join(IMG, '04_kpi_top.png'), 0.3, 1.1, 12.0)
    txt(sl, 0.5, 6.0, 12, 0.5, '今日订单数 · 今日营收 · 活跃骑手 · 活跃商家 · 爆仓点数  —  5 个 KPI 卡片，30 秒自动刷新', 13, GRAY)

    # ---- SLIDE 34: Order Management ----
    sl = S(prs); bar(sl, '订单管理', p())
    img_w(sl, os.path.join(IMG, '02_order_section.png'), 0.3, 1.1, 12.0)
    txt(sl, 0.5, 6.0, 12, 0.5, '按状态筛选（6 态）+ 实时数据表格，支撑运营决策', 13, GRAY)

    # ---- SLIDE 35: Overflow Warning ----
    sl = S(prs); bar(sl, '爆仓预警', p())
    img_w(sl, os.path.join(IMG, '10_overflow_dashboard.png'), 0.3, 1.1, 8.0)
    img_w(sl, os.path.join(IMG, '11_overflow_pickup.png'), 8.6, 1.1, 4.2)
    txt(sl, 0.5, 5.8, 12, 0.5, '饱和度柱状图：> 80% 黄色预警  |  = 100% 红色爆仓  |  实时监控 12 个寄存点', 13, GRAY)

    # ---- SLIDE 36: Pickup Points Management ----
    sl = S(prs); bar(sl, '寄存点管理', p())
    img_w(sl, os.path.join(IMG, '03_pickup_points.png'), 0.3, 1.1, 12.0)

    # ---- SLIDE 37: More Management Pages ----
    sl = S(prs); bar(sl, '管理页面：商家 / 学生 / 骑手 / 菜品', p())
    pages = [
        ('05_merchants.png', 0.3, 1.1, 6.0),
        ('06_students.png', 6.8, 1.1, 6.0),
        ('07_riders.png', 0.3, 3.6, 6.0),
        ('08_dishes.png', 6.8, 3.6, 6.0),
    ]
    for f, x, y, w in pages:
        img_w(sl, os.path.join(IMG, f), x, y, w)

    # ---- SLIDE 38: SECTION 08 ----
    section(prs, '08', '创新点总结与成果交付', '7 大创新 · 项目交付物 · 未来展望')
    p()

    # ---- SLIDE 39: Innovations ----
    sl = S(prs); bar(sl, '七大创新点', p())
    inno = [
        ('FOR UPDATE 行级锁防超卖', 'SELECT...FOR UPDATE 原子化"读-判断-写"，高并发场景下单库存绝不超卖', BLUE),
        ('七重触发器防护体系', '库存(2) + 骑手类型(2) + 状态管理(2) + 容量预检(1)，数据库层全自动', BLUE),
        ('两段式配送状态机', '6 态 ENUM + 双骑手 + 3 时间戳，覆盖全流程从下单到签收', GREEN),
        ('chk_capacity 物理硬约束', 'CHECK(current<=capacity) + 容量预检双层防护，80 格绝不 81 包', GREEN),
        ('RANK() OVER 窗口函数', '一行 SQL 完成商户销售排行，比应用层排序更快更准确', ORANGE),
        ('AI Text-to-SQL', 'DeepSeek + Schema 注入，自然语言查数据，仅允许 SELECT', ORANGE),
        ('Cloudflare Tunnel 部署', '免费隧道，localhost 映射公网，评委手机扫码即访问', RGBColor(0x7B, 0x1F, 0xA2)),
    ]
    for i, (t, d, clr) in enumerate(inno):
        y = 1.1 + i * 0.85
        number_badge(sl, 0.5, y + 0.02, i + 1, clr)
        txt(sl, 1.2, y + 0.05, 3.5, 0.4, t, 14, clr, True)
        txt(sl, 4.8, y + 0.05, 7.5, 0.6, d, 11, DARK)

    # ---- SLIDE 40: Deliverables ----
    sl = S(prs); bar(sl, '项目交付成果', p())
    deliverables = [
        ('数据库设计', 'campus_delivery_db.sql\n7 表 · 4 索引 · 7 触发器\n4 存储过程 · 2 视图', BLUE),
        ('模拟数据', 'generate_mock_data.py\n5000 条订单\n容量感知生成器', GREEN),
        ('Flask 大屏', 'app.py + 模板\n3 Tab + ECharts\nAI Text-to-SQL', ORANGE),
        ('文档', '实践报告 .docx\n答辩 PPT .pptx\nREADME.md', RGBColor(0x7B, 0x1F, 0xA2)),
        ('部署', 'Cloudflare Tunnel\n公网访问\n扫码即看', RED),
    ]
    for i, (t, d, clr) in enumerate(deliverables):
        x = 0.3 + i * 2.55
        card(sl, x, 1.5, 2.35, 3.5, t, d.split('\n'), clr)
    txt(sl, 0.5, 5.5, 12, 0.5, 'Git 仓库 · 全部代码已提交推送 · 分支: master', 13, GRAY)

    # ---- SLIDE 41: Future ----
    sl = S(prs); bar(sl, '改进方向与未来展望', p())
    future = [
        ('柜满排队', '骑手已送到但柜满的包裹进入"等待空位"队列，不抹掉骑手成果', BLUE),
        ('智能调度', '下单时自动推荐邻近有空位的寄存点，用户一键切换', GREEN),
        ('路线优化', '楼栋骑手多单拼单路径规划，一次取 5-8 件集中配送', ORANGE),
        ('实时追踪', '接入地图 API，用户实时看包裹位置（商家 > 寄存点 > 寝室）', RGBColor(0x7B, 0x1F, 0xA2)),
        ('全链路压测', 'sysbench 测试 QPS 上限，验证 FOR UPDATE 并发性能瓶颈', RED),
    ]
    for i, (t, d, clr) in enumerate(future):
        x = 0.3 + i * 2.55
        card(sl, x, 1.5, 2.35, 2.5, t, [d], clr)

    # ---- SLIDE 42: Thanks ----
    sl = S(prs); bar(sl, '感谢聆听！', p())
    txt(sl, 1.0, 2.5, 11, 1.0, '校园外卖两段式配送数据库系统', 32, BLUE, True, PP_ALIGN.CENTER)
    txt(sl, 1.0, 3.8, 11, 0.5, '欢迎扫码访问实时大屏  |  GitHub: sou1maker', 16, GRAY, align=PP_ALIGN.CENTER)
    txt(sl, 1.0, 5.0, 11, 0.5, 'MySQL 8.0 · Flask · ECharts · DeepSeek AI  |  2026 年 6 月', 13, GRAY, align=PP_ALIGN.CENTER)

    p()

    # ===== SAVE =====
    out = os.path.join(os.path.dirname(__file__), '校园外卖两段式配送系统_答辩汇报.pptx')
    prs.save(out)
    print(f'Done: {out}')
    print(f'Slides: {len(prs.slides)}')

if __name__ == '__main__':
    build()
