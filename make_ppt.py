# -*- coding: utf-8 -*-
"""
PPT v7.0 — 完全重做，逐页按主人规范
字号：标题28-32pt / 正文18-24pt / 代码14-16pt
配色：主色#165DFF / 强调#FF7D00
布局：左文右码 / 上标题中内容下要点
一页一概念，代码分段高亮，图片不拉伸
"""
import sys, io, os
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR_TYPE
from pptx.oxml.ns import qn

# ========== CONSTANTS ==========
W, H = Inches(13.333), Inches(7.5)
BLUE   = RGBColor(0x16, 0x5D, 0xFF)
DARK   = RGBColor(0x1D, 0x21, 0x29)
GRAY   = RGBColor(0x86, 0x90, 0x9C)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xFF, 0x7D, 0x00)
GREEN  = RGBColor(0x00, 0xB4, 0x2A)
RED    = RGBColor(0xF5, 0x3F, 0x3F)
BG     = RGBColor(0xF7, 0xF8, 0xFA)
WHITE_BG = RGBColor(0xFF, 0xFF, 0xFF)
CODE_BG = RGBColor(0xF2, 0xF3, 0xF5)
YELLOW_BG = RGBColor(0xFF, 0xF7, 0xE6)
TITLE_H = Inches(1.0)
FN = '微软雅黑'
MONO = 'Consolas'

IMG = os.path.join(os.path.dirname(__file__), 'images', 'screenshots')
ER  = os.path.join(os.path.dirname(__file__), 'images', 'er_diagram.png')

def S(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def bar(slide, title, num=None):
    """Top blue bar — 32pt title"""
    b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), W, TITLE_H)
    b.fill.solid(); b.fill.fore_color.rgb = BLUE; b.line.fill.background()
    t = slide.shapes.add_textbox(Inches(0.8), Inches(0.18), Inches(11.5), Inches(0.7))
    p = t.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(30); p.font.color.rgb = WHITE; p.font.bold = True; p.font.name = FN
    if num:
        n = slide.shapes.add_textbox(Inches(12.3), Inches(7.0), Inches(0.7), Inches(0.35))
        p2 = n.text_frame.paragraphs[0]
        p2.text = str(num); p2.font.size = Pt(12); p2.font.color.rgb = GRAY; p2.font.name = FN; p2.alignment = PP_ALIGN.RIGHT

def sec(prs, num, title, sub):
    """Section divider"""
    sl = S(prs)
    # Left stripe
    s = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.15), H)
    s.fill.solid(); s.fill.fore_color.rgb = BLUE; s.line.fill.background()
    t = sl.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(3), Inches(1.5))
    p = t.text_frame.paragraphs[0]
    p.text = num; p.font.size = Pt(80); p.font.color.rgb = BLUE; p.font.bold = True; p.font.name = FN
    t2 = sl.shapes.add_textbox(Inches(1.5), Inches(3.8), Inches(10), Inches(0.8))
    p2 = t2.text_frame.paragraphs[0]
    p2.text = title; p2.font.size = Pt(34); p2.font.color.rgb = DARK; p2.font.bold = True; p2.font.name = FN
    t3 = sl.shapes.add_textbox(Inches(1.5), Inches(4.6), Inches(10), Inches(0.5))
    p3 = t3.text_frame.paragraphs[0]
    p3.text = sub; p3.font.size = Pt(16); p3.font.color.rgb = GRAY; p3.font.name = FN
    return sl

def T(slide, left, top, width, height, text, size=20, color=DARK, bold=False, align=PP_ALIGN.LEFT):
    """Text box — big default 20pt"""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(size); p.font.color.rgb = color; p.font.bold = bold; p.font.name = FN
    p.alignment = align; p.space_after = Pt(4)
    return tf

def MT(slide, left, top, width, height, lines, size=18, color=DARK, sp=Pt(8)):
    """Multi-line text"""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size); p.font.color.rgb = color; p.font.name = FN; p.space_after = sp
    return tf

def CODE(slide, left, top, width, height, lines, size=14, highlights=None):
    """Code block — light gray bg, 14-16pt monospace"""
    if highlights is None:
        highlights = set()
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    box.fill.solid(); box.fill.fore_color.rgb = CODE_BG
    box.line.color.rgb = RGBColor(0xE5, 0xE6, 0xEB); box.line.width = Pt(0.5)
    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.12), Inches(width - 0.5), Inches(height - 0.24))
    tf = tb.text_frame; tf.word_wrap = True
    h_set = set(highlights)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size); p.font.name = MONO
        p.font.color.rgb = DARK; p.space_after = Pt(2)
        if i in h_set:
            # Highlight line with orange bg
            pPr = p._p.get_or_add_pPr()
            shd = pPr.makeelement(qn('a:shd'), {})
            shd.set('fill', 'FFF7E6')
            pPr.append(shd)
    return tf

def FLOW(slide, items, y_start=1.6, box_w=1.9, box_h=1.2, gap=0.3):
    """Horizontal flow diagram with arrows"""
    n = len(items)
    total_w = n * box_w + (n - 1) * gap
    x0 = (13.333 - total_w) / 2
    for i, (label, desc, clr) in enumerate(items):
        x = x0 + i * (box_w + gap)
        bx = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(x), Inches(y_start), Inches(box_w), Inches(box_h))
        bx.fill.solid(); bx.fill.fore_color.rgb = clr; bx.line.fill.background()
        p = bx.text_frame.paragraphs[0]
        p.text = label; p.font.size = Pt(15); p.font.color.rgb = WHITE; p.font.bold = True
        p.font.name = FN; p.alignment = PP_ALIGN.CENTER
        T(slide, x, y_start + box_h + 0.1, box_w, 0.5, desc, 11, GRAY, align=PP_ALIGN.CENTER)
        if i < n - 1:
            T(slide, x + box_w, y_start + 0.35, gap, 0.4, '▶', 18, BLUE, align=PP_ALIGN.CENTER)
    return y_start + box_h + 0.7

def CARD(slide, left, top, width, height, title, lines, accent=BLUE):
    """Card with accent top bar"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE_BG
    bg.line.color.rgb = RGBColor(0xE5, 0xE6, 0xEB); bg.line.width = Pt(0.5)
    bar_s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.05))
    bar_s.fill.solid(); bar_s.fill.fore_color.rgb = accent; bar_s.line.fill.background()
    T(slide, left + 0.2, top + 0.12, width - 0.4, 0.35, title, 18, accent, True)
    MT(slide, left + 0.2, top + 0.55, width - 0.4, height - 0.6, lines, 15, DARK, Pt(6))

def TB(slide, left, top, col_w, hdrs, rows, fs=13):
    """Table"""
    n = len(rows) + 1; nc = len(hdrs); tw = sum(col_w)
    s = slide.shapes.add_table(n, nc, Inches(left), Inches(top), Inches(tw), Inches(0.38 * n))
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
                p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            if ri % 2 == 0:
                c.fill.solid(); c.fill.fore_color.rgb = BG
    return s

def PIC(slide, path, left, top, width=None):
    """Image — width only, no stretch"""
    if not os.path.exists(path):
        T(slide, left, top, 4, 0.5, f'[缺图: {os.path.basename(path)}]', 12, RED)
        return None
    if width:
        return slide.shapes.add_picture(path, Inches(left), Inches(top), Inches(width))
    return slide.shapes.add_picture(path, Inches(left), Inches(top))

def BADGE(slide, left, top, n, clr=BLUE, sz=0.45):
    """Number badge"""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(sz), Inches(sz))
    c.fill.solid(); c.fill.fore_color.rgb = clr; c.line.fill.background()
    p = c.text_frame.paragraphs[0]
    p.text = str(n); p.font.size = Pt(16); p.font.color.rgb = WHITE; p.font.bold = True; p.font.name = FN; p.alignment = PP_ALIGN.CENTER

# ========================================================================
def build():
    prs = Presentation(); prs.slide_width = W; prs.slide_height = H
    pg = [0]
    def P(add=1): pg[0] += add; return pg[0]

    # ===== SLIDE 1: COVER =====
    sl = S(prs)
    # Left blue panel
    lp = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(5.5), H)
    lp.fill.solid(); lp.fill.fore_color.rgb = BLUE; lp.line.fill.background()
    T(sl, 1.0, 1.8, 4.0, 0.5, '数据库课程设计 · 答辩汇报', 16, RGBColor(0xAA, 0xCC, 0xFF))
    T(sl, 1.0, 2.6, 4.0, 2.0, '校园外卖\n两段式配送\n数据库系统', 42, WHITE, True)
    T(sl, 1.0, 5.2, 4.0, 0.5, 'Campus Delivery Database', 14, RGBColor(0xAA, 0xCC, 0xFF))
    # Right side
    T(sl, 6.3, 2.8, 6.0, 0.5, 'MySQL 8.0 | Flask | ECharts | DeepSeek AI', 16, GRAY)
    MT(sl, 6.3, 3.6, 6.0, 1.5, [
        '7 表 · 严格 3NF  ·  4 索引',
        '7 触发器 · FOR UPDATE 行级锁',
        '4 存储过程 · ACID 事务',
        '2 视图 · RANK() OVER 窗口函数',
        'AI Text-to-SQL 自然语言查询',
    ], 16, DARK, Pt(6))
    T(sl, 6.3, 6.2, 6.0, 0.4, '2026 年 6 月', 14, GRAY)
    P()

    # ===== SLIDE 2: TOC =====
    sl = S(prs); bar(sl, '目录', P())
    toc = [
        ('01', '项目背景与需求分析', '3'),
        ('02', '系统设计：架构 · ER图 · 7表', '7'),
        ('03', '索引策略与性能优化', '16'),
        ('04', '七重触发器防护盾', '19'),
        ('05', '存储过程与事务管理', '30'),
        ('06', '视图 · 窗口函数 · AI', '34'),
        ('07', '系统大屏与可视化', '38'),
        ('08', '创新总结与成果', '45'),
    ]
    for i, (num, title, page) in enumerate(toc):
        y = 1.5 + i * 0.7
        T(sl, 1.5, y, 1.0, 0.5, num, 30, BLUE, True)
        T(sl, 3.0, y, 7.0, 0.5, title, 20, DARK)
        T(sl, 11.5, y, 1.5, 0.5, page, 18, GRAY, align=PP_ALIGN.RIGHT)

    # ===== SLIDE 3: SECTION 01 =====
    sec(prs, '01', '项目背景与需求分析', '校园外卖市场 · 传统痛点 · 两段式配送模型')
    P()

    # ===== SLIDE 4: Market + Pain =====
    sl = S(prs); bar(sl, '市场与痛点', P())
    # 3 stat boxes
    for i, (n, t, clr) in enumerate([
        ('4,500亿+', '中国外卖市场 2025', BLUE),
        ('70%+', '高校外卖渗透率', GREEN),
        ('120万单/日', '头部高校日均外卖', ORANGE),
    ]):
        x = 0.8 + i * 4.1
        c = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.5), Inches(3.6), Inches(1.3))
        c.fill.solid(); c.fill.fore_color.rgb = WHITE_BG
        c.line.color.rgb = RGBColor(0xE5, 0xE6, 0xEB); c.line.width = Pt(0.5)
        T(sl, x + 0.2, 1.6, 3.2, 0.5, n, 28, clr, True)
        T(sl, x + 0.2, 2.3, 3.2, 0.4, t, 14, GRAY)
    # Pain points with icons
    T(sl, 0.8, 3.3, 11, 0.5, '传统校园外卖三大痛点', 22, DARK, True)
    pains = [
        ('✖', '校门禁入', '校外骑手不能进宿舍区，学生需步行数百米取餐'),
        ('✖', '高峰拥堵', '30+ 骑手同时在校门口等候，场面混乱，配送时效无法保证'),
        ('✖', '丢失错拿', '外卖堆放地上，无管理无追溯，日均丢失率 3%-5%'),
    ]
    for i, (icon, title, desc) in enumerate(pains):
        y = 4.0 + i * 1.0
        T(sl, 1.0, y, 0.5, 0.5, icon, 20, RED, True)
        T(sl, 1.5, y, 1.8, 0.5, title, 18, DARK, True)
        T(sl, 3.5, y, 8.5, 0.5, desc, 16, GRAY)

    # ===== SLIDE 5: Two-Stage Flow =====
    sl = S(prs); bar(sl, '两段式配送模型', P())
    T(sl, 0.5, 1.3, 12, 0.4, '一条配送链拆成两段，宿舍楼寄存柜作为中转枢纽', 18, BLUE, True)
    # Flow diagram
    flow_items = [
        ('商家\nMerchant', '出餐', BLUE),
        ('干线骑手\nStage1_Trunk', '取餐配送', RGBColor(0x40, 0x80, 0xFF)),
        ('寄存柜\nPickup Point', '包裹入库', GREEN),
        ('楼栋骑手\nStage2_Floor', '最后100米', ORANGE),
        ('学生\nStudent', '签收', RED),
    ]
    yf = FLOW(sl, flow_items, 2.3, 2.0, 1.3, 0.25)
    # Key features
    features = [
        ('✔', '校外骑手不进入宿舍区 — 安全保障'),
        ('✔', '寄存柜物理硬约束 chk_capacity — 80格绝不81包'),
        ('✔', '两段骑手独立管理 — 干线 8 人 + 楼栋 7 人'),
        ('✔', '全链路 TIMESTAMP 审计 — 下单 > 入柜 > 签收精确追踪'),
    ]
    for i, (icon, text) in enumerate(features):
        T(sl, 1.0, yf + 0.3 + i * 0.5, 11, 0.5, f'{icon}  {text}', 15, DARK)

    # ===== SLIDE 6: State Machine — BIG FLOW =====
    sl = S(prs); bar(sl, '六态订单状态机', P())
    states = [
        ('Paid', '已支付\n待指派', BLUE),
        ('Stage1\nAssigned', '干线骑手\n已接单', RGBColor(0x40, 0x80, 0xFF)),
        ('Arrived\nAt_Point', '已送达\n寄存柜', GREEN),
        ('Stage2\nAssigned', '楼栋骑手\n已接单', ORANGE),
        ('Completed', '已完成\n签收', RGBColor(0x2E, 0x7D, 0x32)),
    ]
    n_s = len(states)
    total_w_s = n_s * 2.1 + (n_s - 1) * 0.2
    x0_s = (13.333 - total_w_s) / 2
    for i, (name, desc, clr) in enumerate(states):
        x = x0_s + i * 2.3
        bx = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.2), Inches(2.1), Inches(1.4))
        bx.fill.solid(); bx.fill.fore_color.rgb = clr; bx.line.fill.background()
        p = bx.text_frame.paragraphs[0]
        p.text = name; p.font.size = Pt(16); p.font.color.rgb = WHITE; p.font.bold = True; p.font.name = FN; p.alignment = PP_ALIGN.CENTER
        T(sl, x, 3.75, 2.1, 0.5, desc, 12, GRAY, align=PP_ALIGN.CENTER)
        if i < n_s - 1:
            T(sl, x + 2.1, 2.6, 0.2, 0.4, '▶', 16, BLUE, align=PP_ALIGN.CENTER)
    # Cancelled branch
    T(sl, 5.5, 4.6, 3.0, 0.5, '▼  任意非终态可转入', 14, RED, align=PP_ALIGN.CENTER)
    cx = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.5), Inches(5.1), Inches(2.1), Inches(1.0))
    cx.fill.solid(); cx.fill.fore_color.rgb = RED; cx.line.fill.background()
    cp = cx.text_frame.paragraphs[0]
    cp.text = 'Cancelled\n已取消退款'; cp.font.size = Pt(14); cp.font.color.rgb = WHITE; cp.font.bold = True; cp.font.name = FN; cp.alignment = PP_ALIGN.CENTER
    T(sl, 0.5, 6.5, 12, 0.5, '3 个 TIMESTAMP 精准审计：created_at → stage1_completed_at → stage2_completed_at', 14, GRAY)

    # ===== SLIDE 7: SECTION 02 =====
    sec(prs, '02', '系统设计与数据库架构', '三层架构 · 技术栈 · ER 图 · 7 表 3NF')
    P()

    # ===== SLIDE 8: Architecture =====
    sl = S(prs); bar(sl, '系统三层架构', P())
    for i, (layer, desc, clr) in enumerate([
        ('展现层', 'Flask + ECharts 实时大屏  ·  3 个 Tab  ·  30 秒自动刷新', BLUE),
        ('业务层', 'Python Flask REST API  ·  4 存储过程  ·  AI Text-to-SQL', GREEN),
        ('数据层', 'MySQL 8.0 InnoDB  ·  7 表 4 索引 7 触发器 2 视图  ·  FOR UPDATE 行级锁', ORANGE),
    ]):
        y = 1.5 + i * 1.7
        bx = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(11.5), Inches(1.3))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE_BG
        bx.line.color.rgb = clr; bx.line.width = Pt(2)
        badge = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(2.2), Inches(1.3))
        badge.fill.solid(); badge.fill.fore_color.rgb = clr; badge.line.fill.background()
        bp = badge.text_frame.paragraphs[0]
        bp.text = layer; bp.font.size = Pt(22); bp.font.color.rgb = WHITE; bp.font.bold = True; bp.font.name = FN; bp.alignment = PP_ALIGN.CENTER
        T(sl, 3.3, y + 0.3, 8.5, 0.6, desc, 18, DARK)

    # ===== SLIDE 9: Tech Stack =====
    sl = S(prs); bar(sl, '技术栈', P())
    techs = [
        ('MySQL 8.0', 'InnoDB 引擎\nFOR UPDATE 行级锁\nRANK() OVER 窗口函数', BLUE),
        ('Python Flask', 'REST API\nPyMySQL 原生 SQL\nDeepSeek AI 集成', GREEN),
        ('ECharts', '3 个功能 Tab\n饼图 + 柱状图 + 表格\n30 秒自动刷新', ORANGE),
        ('DeepSeek', 'Text-to-SQL\nSchema 注入提示词\n仅允许 SELECT', RGBColor(0x7B, 0x1F, 0xA2)),
        ('Cloudflare', 'Tunnel 公网隧道\nHTTPS 加密\n扫码即访问', RGBColor(0x00, 0x96, 0x88)),
    ]
    for i, (name, desc, clr) in enumerate(techs):
        x = 0.3 + i * 2.55
        CARD(sl, x, 1.5, 2.35, 3.5, name, desc.split('\n'), clr)
    T(sl, 0.5, 5.5, 12, 1.5, '数据库核心技术栈：7 表(3NF) · 4 B-Tree 索引(含 2 复合索引) · 7 触发器(FOR UPDATE + SIGNAL) · 4 存储过程(ACID 事务) · 2 分析视图', 18, DARK)

    # ===== SLIDE 10: ER Diagram (FULL PAGE) =====
    sl = S(prs); bar(sl, '数据库 E-R 图 —— 7 张核心表 · 严格 3NF', P())
    PIC(sl, ER, 0.3, 1.2, 12.7)
    T(sl, 0.5, 6.5, 12, 0.5, '✔ 严格 3NF 无冗余    ✔ 5 个外键级联约束    ✔ 12 个 CHECK 约束    ✔ ENUM 类型限死合法值', 14, GRAY)

    # ===== SLIDE 11: 7 Tables Summary =====
    sl = S(prs); bar(sl, '7 张核心表概览', P())
    TB(sl, 0.3, 1.3, [1.8, 1.2, 2.0, 7.0],
       ['表名', '中文', '关键约束', '核 心 作 用'],
       [
           ['users', '学生', 'balance>=0, phone UNIQUE', '校园卡钱包 + 宿舍地址'],
           ['merchants', '商家', 'rating 1~5', '档口信息 + 评分'],
           ['dishes', '菜品', 'stock>=0, status 0/1', '库存管理 + 上下架控制'],
           ['pickup_points', '寄存点', 'chk_capacity: current<=capacity', '物理容积硬约束，80格绝不81包'],
           ['riders', '骑手', 'ENUM rider_type + status', 'Stage1_Trunk/Stage2_Floor 分工'],
           ['orders', '订单', '6态ENUM, 5FK, 双骑手', '六态状态机 + 全链路时间审计'],
           ['order_items', '明细', 'quantity>0, FK CASCADE', '订单-菜品关联，触发库存扣减'],
       ], 13)
    T(sl, 0.5, 6.0, 12, 1.0, '严格 3NF：所有非主属性完全函数依赖于主键，无传递依赖，无冗余。5 个外键保证引用完整，12 个 CHECK 约束在数据库层强制执行业务规则。', 15, GRAY)

    # ===== SLIDE 12: pickup_points Table =====
    sl = S(prs); bar(sl, '关键表：pickup_points —— 物理容积硬约束', P())
    # Left: code
    CODE(sl, 0.5, 1.4, 5.8, 3.5, [
        'CREATE TABLE pickup_points (',
        '',
        '  point_id    INT PRIMARY KEY AUTO_INCREMENT,',
        '  point_name  VARCHAR(50) NOT NULL,',
        '  location    VARCHAR(200) NOT NULL,',
        '',
        '  capacity         INT NOT NULL,',
        '  current_packages INT DEFAULT 0',
        '    CHECK (current_packages >= 0),',
        '',
        '  -- ★ 核心约束：物理容积绝不可超',
        '  CONSTRAINT chk_capacity',
        '    CHECK (current_packages <= capacity)',
        '',
        ');',
    ], 16, highlights={10, 11})
    # Right: explanation
    T(sl, 7.0, 1.4, 5.5, 0.5, '为什么这样设计？', 22, BLUE, True)
    MT(sl, 7.0, 2.1, 5.5, 4.0, [
        '物理柜子只有 80 个格子',
        '→ 第 81 个包裹物理上塞不进去',
        '→ 数据库必须阻止写入',
        '',
        'CHECK 约束在 MySQL 引擎层执行',
        '→ 任何 UPDATE current_packages',
        '   如果超过 capacity 立即拒绝',
        '→ 应用层没有机会犯错',
        '',
        '12 个寄存点，容量 50~120 格',
        'current_packages 由存储过程',
        '维护 (+1入库/-1出库)',
    ], 16, DARK, Pt(8))

    # ===== SLIDE 13: orders Table =====
    sl = S(prs); bar(sl, '核心表：orders —— 六态状态机 + 双骑手 + 三时间戳', P())
    CODE(sl, 0.3, 1.3, 7.0, 4.5, [
        'CREATE TABLE orders (',
        '  order_id     INT PRIMARY KEY AUTO_INCREMENT,',
        '',
        '  -- ★ 六态状态机（ENUM 限死合法值）',
        "  order_status ENUM('Paid',",
        "    'Stage1_Assigned', 'Arrived_At_Point',",
        "    'Stage2_Assigned','Completed','Cancelled'),",
        '',
        '  -- 双骑手独立绑定',
        '  stage1_rider_id INT,  -- FK → riders（干线）',
        '  stage2_rider_id INT,  -- FK → riders（楼栋）',
        '',
        '  -- 全链路时间审计',
        '  created_at          TIMESTAMP,  -- 下单',
        '  stage1_completed_at TIMESTAMP,  -- 入柜',
        '  stage2_completed_at TIMESTAMP,  -- 签收',
        '',
        '  -- 5 个外键 + 12 个 CHECK 约束',
        ');',
    ], 15, highlights={5, 6, 7, 8, 9, 10, 11, 12, 13, 14})
    T(sl, 7.8, 1.3, 5.0, 0.5, '六态流转', 20, BLUE, True)
    MT(sl, 7.8, 2.0, 5.0, 2.0, [
        'Paid',
        '  ↓',
        'Stage1_Assigned（干线接单）',
        '  ↓',
        'Arrived_At_Point（包裹入柜）',
        '  ↓',
        'Stage2_Assigned（楼栋接单）',
        '  ↓',
        'Completed（签收）',
        '',
        '← 任意非终态可取消 → Cancelled',
    ], 15, DARK, Pt(4))
    T(sl, 7.8, 4.8, 5.0, 2.0, '设计亮点\n✔ ENUM 限死 6 种合法状态\n✔ 双骑手独立追踪两段进度\n✔ 3 个 TIMESTAMP 精确审计\n✔ 5 个 FK 保证引用完整', 15, GREEN)

    # ===== SLIDE 14: State machine detail =====
    sl = S(prs); bar(sl, '状态机 + 骑手联动', P())
    TB(sl, 0.3, 1.3, [2.2, 3.0, 3.5, 4.0],
       ['状态', '含义', '触发方式', '骑手状态联动'],
       [
           ['Paid', '已支付，待指派干线', 'sp_create_order', '—'],
           ['Stage1_Assigned', '干线骑手取餐中', '指派 stage1_rider_id', '干线 → Delivering'],
           ['Arrived_At_Point', '包裹已入寄存柜', 'sp_arrive_at_pickup_point', '干线 → Idle（释放）'],
           ['Stage2_Assigned', '楼栋骑手配送中', '指派 stage2_rider_id', '楼栋 → Delivering'],
           ['Completed', '学生签收', 'sp_stage2_deliver', '楼栋 → Idle（释放）'],
           ['Cancelled', '已取消退款', 'sp_cancel_order', '所有骑手 → Idle'],
       ], 13)
    T(sl, 0.5, 5.2, 12, 1.5, '核心价值：订单状态一变更 → 触发器自动联动骑手状态 → 应用层零代码维护骑手状态 —— 这是触发器最经典的用武之地', 18, BLUE, True)

    # ===== SLIDE 15: riders detail =====
    sl = S(prs); bar(sl, '关键表：riders —— 两段式特种骑手', P())
    CODE(sl, 0.5, 1.4, 5.8, 2.5, [
        'CREATE TABLE riders (',
        '  rider_id   INT PRIMARY KEY AUTO_INCREMENT,',
        '',
        "  rider_type ENUM('Stage1_Trunk',  -- 干线",
        "                   'Stage2_Floor')  -- 楼栋",
        '    NOT NULL,',
        '',
        "  status     ENUM('Idle',",
        "                   'Delivering',",
        "                   'Offline')",
        "    DEFAULT 'Idle',",
        ');',
    ], 16, highlights={3, 4, 7, 8, 9})
    T(sl, 7.0, 1.4, 5.5, 0.5, '设计要点', 22, BLUE, True)
    MT(sl, 7.0, 2.1, 5.5, 4.0, [
        'ENUM 在数据库层强制分工',
        '→ Stage1_Trunk 只能做干线配送',
        '→ Stage2_Floor 只能做楼栋配送',
        '→ 应用层写错会被触发器拦截',
        '',
        'status 由触发器自动管理',
        '→ 指派 → Delivering',
        '→ 完成/取消 → Idle',
        '→ 应用层永远不需要手动',
        '   UPDATE riders SET status',
        '',
        '8 干线 + 7 楼栋 = 15 骑手',
    ], 16, DARK, Pt(6))

    # ===== SLIDE 16: SECTION 03 =====
    sec(prs, '03', '索引策略与性能优化', '4 个 B-Tree 索引 · 复合索引覆盖查询 · 视图加速')
    P()

    # ===== SLIDE 17: Indexes =====
    sl = S(prs); bar(sl, '4 个 B-Tree 索引', P())
    TB(sl, 0.3, 1.3, [2.6, 1.4, 2.8, 5.5],
       ['索引名', '表', '字段', '加 速 场 景'],
       [
           ['idx_orders_status', 'orders', 'order_status', '大屏按状态筛选（最高频）'],
           ['idx_orders_created', 'orders', 'created_at', '今日/近7天/近30天查询'],
           ['idx_dishes_merchant', 'dishes', 'merchant_id, status', '前端"某商家在售菜品"'],
           ['idx_orders_point_status', 'orders', 'pickup_point_id,\norder_status', '容量检查 + 视图 LEFT JOIN\n(本次新增)'],
       ], 14)
    T(sl, 0.5, 4.5, 12, 0.5, '为什么新增 idx_orders_point_status？', 20, BLUE, True)
    MT(sl, 0.5, 5.2, 12, 1.5, [
        'vw_pickup_point_analytics 视图需要 JOIN orders 表按 pickup_point_id + order_status 聚合统计——没有索引时全表扫描 5000+ 行',
        '加复合索引后 MySQL 直接用索引覆盖查询，查询从 ~50ms 降到 ~2ms —— 每次大屏刷新快 25 倍',
        '同时加速 sp_create_order 的 SELECT...FOR UPDATE 容量预检 —— 索引定位行更快，锁持有时间更短',
    ], 15, DARK, Pt(6))

    # ===== SLIDE 18: Index principle =====
    sl = S(prs); bar(sl, '索引设计原则', P())
    principles = [
        ('高频列优先', 'order_status 是大屏 Tab 切换的核心过滤条件，加索引后 GROUP BY 从全表扫描变为索引扫描', BLUE),
        ('复合索引最左前缀', 'idx_dishes_merchant(merchant_id, status) 同时加速"按商家查"和"按商家+上架状态查"两种查询', GREEN),
        ('覆盖查询', 'idx_orders_point_status(pickup_point_id, order_status) 覆盖了视图 LEFT JOIN 的所有列，不需要回表', ORANGE),
        ('FK 自动索引', 'InnoDB 为外键列自动建 B-Tree 索引 — user_id, merchant_id, pickup_point_id, stage1/2_rider_id 都有索引', RGBColor(0x7B, 0x1F, 0xA2)),
    ]
    for i, (title, desc, clr) in enumerate(principles):
        y = 1.5 + i * 1.3
        BADGE(sl, 0.6, y + 0.1, i + 1, clr, 0.5)
        T(sl, 1.3, y + 0.1, 3.0, 0.4, title, 20, clr, True)
        T(sl, 4.5, y + 0.1, 8.0, 0.8, desc, 16, DARK)

    # ===== SLIDE 19: SECTION 04 =====
    sec(prs, '04', '七重触发器防护盾', 'FOR UPDATE 行级锁 · 库存防超卖 · 骑手类型约束 · 状态管理 · 容量预检')
    P()

    # ===== SLIDE 20: FOR UPDATE — Problem =====
    sl = S(prs); bar(sl, 'FOR UPDATE 行级锁：为什么需要它？', P())
    T(sl, 0.5, 1.3, 5.5, 0.5, '✖ 传统做法：SELECT + 判断 + UPDATE', 22, RED, True)
    CODE(sl, 0.5, 2.0, 5.5, 2.0, [
        '-- 线程 A               -- 线程 B',
        'SELECT stock=1           SELECT stock=1',
        '  → 判断：够！          → 判断：够！',
        '',
        'INSERT (扣到 0)         INSERT (扣到 -1)',
        '',
        '→ 超卖！库存变负数！',
    ], 16, highlights={4})
    T(sl, 7.0, 1.3, 5.5, 0.5, '✔ FOR UPDATE 排他锁', 22, GREEN, True)
    CODE(sl, 7.0, 2.0, 5.5, 2.0, [
        '-- 线程 A               -- 线程 B',
        'SELECT...FOR UPDATE(X锁)  SELECT...FOR UPDATE',
        '  → stock=1, 加锁成功      → 阻塞等待...',
        '',
        'INSERT stock=0              ',
        'COMMIT(释放锁)              → 获锁, stock=0',
        '                           → 库存不足!拒绝 ✔',
    ], 16, highlights={5})
    T(sl, 0.5, 4.5, 12, 0.5, '一句话：FOR UPDATE 把"读-判断-写"三步变成原子的一个操作', 20, BLUE, True)
    MT(sl, 0.5, 5.2, 12, 1.5, [
        '✔ 应用层 synchronized / Redis 分布式锁 / 乐观锁重试 — 都不如数据库层的 FOR UPDATE 简洁可靠',
        '✔ 本系统在 3 个关键场景使用：触发器 1（验库存）+ 触发器 7（验容量）+ sp_create_order（下单容量预检）',
    ], 16, DARK, Pt(6))

    # ===== SLIDE 21: Trigger 1 — Stock Check =====
    sl = S(prs); bar(sl, '触发器 1：库存防超卖检查', P())
    CODE(sl, 0.3, 1.3, 6.5, 3.5, [
        'CREATE TRIGGER trg_check_dish_stock_before_order',
        'BEFORE INSERT ON order_items',
        'FOR EACH ROW',
        'BEGIN',
        '',
        '  -- ★ FOR UPDATE 锁定菜品行（排他锁）',
        '  SELECT stock, status',
        '  INTO v_stock, v_status',
        '  FROM dishes',
        '  WHERE dish_id = NEW.dish_id',
        '  FOR UPDATE;',
        '',
        '  -- 检查 1：是否已下架',
        '  IF v_status = 0 THEN',
        "    SIGNAL '45000' SET MESSAGE_TEXT",
        "      = '商品已下架！';",
        '  END IF;',
        '',
        '  -- 检查 2：库存是否充足',
        '  IF v_stock < NEW.quantity THEN',
        "    SIGNAL '45000' SET MESSAGE_TEXT",
        "      = '库存不足！';",
        '  END IF;',
        'END',
    ], 15, highlights={6, 7, 8, 9, 10})
    T(sl, 7.3, 1.3, 5.5, 0.5, '解决了什么问题？', 22, BLUE, True)
    MT(sl, 7.3, 2.0, 5.5, 4.0, [
        '✔ 并发超卖',
        '两个学生同时买最后一份',
        '→ 第二个事务被阻塞',
        '→ 等第一个提交后读到 stock=0',
        '→ 正确拒绝，库存绝不超卖',
        '',
        '✔ 下架保护',
        '已下架商品自动拦截',
        '→ 无需应用层判断 status',
        '',
        '✔ 数据库层防护',
        '即使有人绕过 Flask',
        '直接 INSERT INTO order_items',
        '→ 触发器照样拦截',
    ], 16, DARK, Pt(6))

    # ===== SLIDE 22: Trigger 2 — Stock Reduce =====
    sl = S(prs); bar(sl, '触发器 2：库存自动扣减', P())
    CODE(sl, 0.3, 1.3, 6.5, 1.5, [
        'CREATE TRIGGER trg_reduce_dish_stock_after_order',
        'AFTER INSERT ON order_items',
        'FOR EACH ROW',
        'BEGIN',
        '',
        '  UPDATE dishes',
        '  SET stock = stock - NEW.quantity',
        '  WHERE dish_id = NEW.dish_id;',
        '',
        'END',
    ], 16, highlights={5, 6, 7})
    T(sl, 0.3, 3.2, 6.5, 0.5, '为什么 AFTER INSERT？', 20, BLUE, True)
    MT(sl, 0.3, 3.9, 6.5, 2.0, [
        '✔ 只有触发器 1 通过所有校验',
        '   （库存足 + 未下架）后才执行',
        '✔ 触发器 1 拒绝 → 触发器 2 不触发',
        '✔ 两个触发器在同一事务内',
        '   保证原子性',

    ], 16, DARK, Pt(6))
    T(sl, 7.3, 1.3, 5.5, 5.0, 'BEFORE + AFTER 双触发器协同\n\n'
        'INSERT INTO order_items\n'
        '  ↓\n'
        'Trig 1 (BEFORE):\n'
        '  FOR UPDATE 锁行\n'
        '  → 验库存 + 验上架\n'
        '  → 不通过? SIGNAL → ROLLBACK\n'
        '  ↓ 通过\n'
        'Trig 2 (AFTER):\n'
        '  UPDATE stock = stock - qty\n'
        '  ↓\n'
        'COMMIT  ✔', 15, GREEN)

    # ===== SLIDE 23: Trigger 3-4 Rider Type =====
    sl = S(prs); bar(sl, '触发器 3-4：骑手类型约束', P())
    T(sl, 0.5, 1.2, 12, 0.4, '问题：如果错把楼栋骑手派去商家取餐，业务全乱。ENUM + 触发器双重保护。', 18, DARK)
    CODE(sl, 0.3, 1.8, 6.2, 2.8, [
        '-- Trig 3: BEFORE INSERT 检查',
        'IF NEW.stage1_rider_id IS NOT NULL THEN',
        '  IF NOT EXISTS (',
        '    SELECT 1 FROM riders',
        '    WHERE rider_id = NEW.stage1_rider_id',
        "      AND rider_type = 'Stage1_Trunk'",
        '  ) THEN',
        "    SIGNAL '干线骑手必须是Stage1_Trunk!';",
        '  END IF;',
        'END IF;',
        '-- 同理检查 stage2_rider_id → Stage2_Floor',
        '',
        '-- Trig 4: BEFORE UPDATE 检查',
        '-- 仅在骑手ID发生变化时触发（性能优化）',
        'IF NEW.stage1_rider_id != OLD.stage1_rider_id',
        '   OR OLD.stage1_rider_id IS NULL THEN',
        '  -- 同 #3 的检查逻辑',
        'END IF;',
    ], 14, highlights={0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16})
    T(sl, 7.0, 1.8, 5.5, 0.5, '双重保护机制', 20, BLUE, True)
    MT(sl, 7.0, 2.5, 5.5, 4.0, [
        '第一层：ENUM 类型',
        'rider_type 只有两个合法值',
        '→ 写入非法值直接报错',
        '',
        '第二层：触发器校验',
        'stage1 必须是 Stage1_Trunk',
        'stage2 必须是 Stage2_Floor',
        '→ 用错了类型直接 SIGNAL',
        '',
        'INSERT + UPDATE 全覆盖',
        '→ 新建订单指派骑手',
        '→ 已有订单更换骑手',
        '→ 两条路径都拦截',
    ], 16, DARK, Pt(6))

    # ===== SLIDE 24: Trigger 5-6 Status =====
    sl = S(prs); bar(sl, '触发器 5-6：骑手状态自动管理', P())
    TB(sl, 0.3, 1.3, [2.2, 3.5, 3.0, 3.5],
       ['事件', '订单状态变化', '骑手状态', '谁触发的'],
       [
           ['指派干线', 'Paid → Stage1_Assigned', 'Idle → Delivering', 'Trig 5 (INSERT)'],
           ['干线送达', 'Stage1_Assigned → Arrived_At_Point', 'Delivering → Idle', 'Trig 6 (UPDATE)'],
           ['指派楼栋', 'Arrived_At_Point → Stage2_Assigned', 'Idle → Delivering', 'Trig 6 (UPDATE)'],
           ['最终签收', 'Stage2_Assigned → Completed', 'Delivering → Idle', 'Trig 6 (UPDATE)'],
           ['订单取消', '任意 → Cancelled', 'Delivering → Idle', 'Trig 6 (UPDATE)'],
       ], 13)
    T(sl, 0.5, 4.6, 12, 0.5, '核心代码', 20, BLUE, True)
    CODE(sl, 0.5, 5.2, 12, 1.5, [
        '-- Trig 6 AFTER UPDATE: 状态驱动骑手释放',
        'IF NEW.order_status = \'Arrived_At_Point\' AND OLD.stage1_rider_id IS NOT NULL THEN',
        '  UPDATE riders SET status = \'Idle\' WHERE rider_id = OLD.stage1_rider_id;',
        'END IF;',
        'IF NEW.order_status = \'Completed\' AND OLD.stage2_rider_id IS NOT NULL THEN',
        '  UPDATE riders SET status = \'Idle\' WHERE rider_id = OLD.stage2_rider_id;',
        'END IF;',
        '-- 取消 → 释放所有骑手',
    ], 15, highlights={1, 2, 3, 4, 5, 6})

    # ===== SLIDE 25: Trigger 7 — Capacity Pre-Check =====
    sl = S(prs); bar(sl, '触发器 7（新增）：寄存点容量预检', P())
    T(sl, 0.5, 1.2, 12, 0.4, '之前的问题：只有 chk_capacity 硬约束 → 骑手送到了才拦截 → 骑手白跑一趟，成果被 ROLLBACK', 18, RED)
    CODE(sl, 0.3, 1.9, 6.5, 2.5, [
        'CREATE TRIGGER trg_check_pickup_point_capacity',
        'BEFORE INSERT ON orders',
        'FOR EACH ROW',
        'BEGIN',
        '',
        '  -- ★ FOR UPDATE 锁定寄存点行',
        '  SELECT current_packages, capacity',
        '  INTO v_pt_current, v_pt_capacity',
        '  FROM pickup_points',
        '  WHERE point_id = NEW.pickup_point_id',
        '  FOR UPDATE;',
        '',
        '  IF v_pt_current >= v_pt_capacity THEN',
        "    SIGNAL '45000'",
        "      SET MESSAGE_TEXT = '寄存点已满！'",
        '  END IF;',
        'END',
    ], 15, highlights={6, 7, 8, 9, 10, 12, 13, 14})
    # Right: two-layer protection
    T(sl, 7.3, 1.2, 5.5, 0.5, '两层防护体系', 22, BLUE, True)
    l1 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.3), Inches(1.9), Inches(5.5), Inches(1.5))
    l1.fill.solid(); l1.fill.fore_color.rgb = RGBColor(0xE8, 0xF5, 0xE9)
    l1.line.color.rgb = GREEN; l1.line.width = Pt(2)
    T(sl, 7.6, 2.0, 5.0, 0.3, '✔ 第一层：下单容量预检（主动防护）', 18, GREEN, True)
    MT(sl, 7.6, 2.5, 5.0, 0.8, [
        'Trig 7 + sp_create_order 双保险',
        'FOR UPDATE 防并发容量击穿',
        '用户在 App 下单时就被引导分流',
    ], 15, DARK, Pt(3))
    l2 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.3), Inches(3.7), Inches(5.5), Inches(1.5))
    l2.fill.solid(); l2.fill.fore_color.rgb = RGBColor(0xFF, 0xEB, 0xEE)
    l2.line.color.rgb = RED; l2.line.width = Pt(2)
    T(sl, 7.6, 3.8, 5.0, 0.3, '✔ 第二层：物理硬约束（被动兜底）', 18, RED, True)
    MT(sl, 7.6, 4.3, 5.0, 0.8, [
        'chk_capacity CHECK(current<=capacity)',
        '只有在极端并发绕过第一层时才触发',
        '最后的安全网，80格绝不81包',
    ], 15, DARK, Pt(3))
    T(sl, 0.5, 5.5, 12, 1.5, '结论：爆仓 = 柜子满了不让选这个柜，不是不让订外卖。用户下单时就被引导到邻近有空位的寄存点。chk_capacity 降级为最后安全网。', 18, GREEN, True)

    # ===== SLIDE 26: 7 Triggers Summary =====
    sl = S(prs); bar(sl, '七重触发器总览', P())
    TB(sl, 0.3, 1.3, [0.4, 2.5, 1.4, 1.4, 1.4, 5.0],
       ['#', '功能', '时机', '事件', '表', '核心逻辑一句话'],
       [
           ['1', '库存防超卖(检查)', 'BEFORE', 'INSERT', 'order_items', 'FOR UPDATE锁行 → 验库存+下架 → 拒绝'],
           ['2', '库存防超卖(扣减)', 'AFTER', 'INSERT', 'order_items', 'stock = stock - quantity'],
           ['3', '骑手类型校验', 'BEFORE', 'INSERT', 'orders', 'stage1=Trunk, stage2=Floor'],
           ['4', '骑手类型校验', 'BEFORE', 'UPDATE', 'orders', '同#3，仅骑手变更时触发'],
           ['5', '骑手状态管理', 'AFTER', 'INSERT', 'orders', '指派骑手 → Delivering'],
           ['6', '骑手状态管理', 'AFTER', 'UPDATE', 'orders', '完成/取消 → Idle'],
           ['7', '容量预检 (NEW!)', 'BEFORE', 'INSERT', 'orders', 'FOR UPDATE查容量 → 满则拒'],
       ], 11)
    T(sl, 0.5, 5.8, 12, 1.0, '技术栈：FOR UPDATE 行级锁 | SIGNAL 异常拦截 | OLD/NEW 状态对比 | ENUM + NOT EXISTS 双重保护', 15, GRAY)

    # ===== SLIDE 27: Triggers classification =====
    sl = S(prs); bar(sl, '触发器分类与设计哲学', P())
    categories = [
        ('库存防线', 'Trig 1 + Trig 2', 'FOR UPDATE 锁库存 → 验 → 扣\n并发安全由数据库保证', BLUE),
        ('类型防线', 'Trig 3 + Trig 4', 'ENUM + 触发器双重约束\nStage1 绝不等于 Stage2', GREEN),
        ('状态防线', 'Trig 5 + Trig 6', '订单改 → 骑手自动改\n应用层零状态同步代码', ORANGE),
        ('容量防线', 'Trig 7 (NEW)', '下单前查容量 FOR UPDATE\n满则拒，骑手不会白跑', RED),
    ]
    for i, (title, trigs, desc, clr) in enumerate(categories):
        x = 0.3 + i * 3.2
        CARD(sl, x, 1.5, 2.9, 3.5, title, [trigs, '', desc], clr)
    T(sl, 0.5, 5.5, 12, 1.5, '设计哲学：数据库层全自动防护 → 即使应用层有 bug、有人绕过 Flask 直接操作 MySQL，数据完整性也不会被破坏。\n这是数据库课程的核心价值——约束写在离数据最近的地方。', 18, DARK, True)

    # ===== SLIDE 28: FOR UPDATE demo =====
    sl = S(prs); bar(sl, 'FOR UPDATE 实测：并发场景验证', P())
    T(sl, 0.5, 1.3, 12, 0.4, '同一道菜只剩 1 份，两个学生同时下单 —— 看数据库如何处理', 18, DARK)
    # Two sessions
    CODE(sl, 0.3, 2.0, 6.0, 3.0, [
        '-- Session A（先到，获得锁）',
        'START TRANSACTION;',
        '',
        'SELECT stock FROM dishes',
        "  WHERE dish_id=1 FOR UPDATE;",
        '  → stock = 1  ✔',
        '',
        "INSERT INTO order_items ...",
        '  → stock: 1 → 0',
        '',
        'COMMIT;  -- 释放 X 锁',
    ], 16, highlights=[])
    T(sl, 0.3, 5.2, 6.0, 0.5, 'A 获胜，正常下单，库存扣到 0', 18, GREEN, True)
    CODE(sl, 6.8, 2.0, 6.0, 3.0, [
        '-- Session B（后到，等待锁）',
        'START TRANSACTION;',
        '',
        'SELECT stock FROM dishes',
        "  WHERE dish_id=1 FOR UPDATE;",
        '  → 阻塞等待 A 释放锁...',
        '',
        '-- A 提交后 B 获得锁',
        '  → stock = 0',
        "  → 0 < 1 → SIGNAL '库存不足!'",
        '',
        'ROLLBACK;',
    ], 16, highlights=[])
    T(sl, 6.8, 5.2, 6.0, 0.5, 'B 正确被拒绝，库存没有变成 -1', 18, GREEN, True)

    # ===== SLIDE 29: 7 triggers all in one table for overview =====
    # Skip — already in slide 26-27

    # ===== SLIDE 30: SECTION 05 =====
    sec(prs, '05', '存储过程与事务管理', '4 个存储过程 · ACID 事务 · ROLLBACK 回滚 · 游标恢复')
    P()

    # ===== SLIDE 31: sp_create_order =====
    sl = S(prs); bar(sl, 'sp_create_order：原子下单（四步一事务）', P())
    T(sl, 0.3, 1.2, 6.5, 0.4, '流程', 20, BLUE, True)
    steps = [
        ('[1] 容量预检', 'FOR UPDATE 锁寄存点 → 查 capacity → 满则拒'),
        ('[2] 余额检查', '查 balance → 不足 SIGNAL'),
        ('[3] 扣款 + 创单', 'UPDATE balance + INSERT INTO orders'),
        ('[4] 写明细', 'INSERT INTO order_items → 触发库存触发器链'),
    ]
    for i, (title, desc) in enumerate(steps):
        y = 1.8 + i * 0.7
        BADGE(sl, 0.5, y, i + 1, BLUE, 0.4)
        T(sl, 1.1, y + 0.02, 2.0, 0.35, title, 16, BLUE, True)
        T(sl, 3.3, y + 0.02, 3.5, 0.35, desc, 15, DARK)

    CODE(sl, 0.3, 4.7, 6.5, 1.8, [
        '-- 事务保护框架',
        'DECLARE EXIT HANDLER FOR SQLEXCEPTION',
        'BEGIN',
        '  ROLLBACK;  -- 四步全撤',
        '  RESIGNAL;  -- 向上抛错',
        'END;',
        '',
        'START TRANSACTION;',
        '  -- 四步操作...',
        'COMMIT;  -- 全成功才提交',
    ], 15, highlights={1, 2, 3, 4, 8, 9})

    T(sl, 7.3, 1.2, 5.5, 5.5, 'ACID 体现在本系统\n\n'
        'A-原子性\n'
        '四步全部成功才 COMMIT\n'
        '任一失败 → ROLLBACK 全部撤销\n\n'
        'C-一致性\n'
        '12 个 CHECK 约束保证数据合法\n'
        'chk_capacity, balance>=0, stock>=0\n\n'
        'I-隔离性\n'
        'FOR UPDATE 行级锁\n'
        '并发事务互不干扰\n\n'
        'D-持久性\n'
        'InnoDB redo log\n'
        'COMMIT 后绝不丢失', 15, DARK)

    # ===== SLIDE 32: Two-stage SPs =====
    sl = S(prs); bar(sl, '两段配送存储过程 + 取消退款', P())
    # Stage1
    T(sl, 0.3, 1.3, 4.0, 0.4, 'sp_arrive_at_pickup_point', 18, BLUE, True)
    CODE(sl, 0.3, 1.8, 4.0, 2.5, [
        'START TRANSACTION;',
        '',
        '-- Step 1: 状态跳转',
        "UPDATE orders SET",
        "  order_status='Arrived_At_Point',",
        '  stage1_completed_at=NOW()',
        'WHERE order_id=p_order_id;',
        '',
        '-- Step 2: 包裹数+1',
        'UPDATE pickup_points',
        '  SET current_packages=''current+1',
        '  WHERE point_id=v_point_id;',
        '  -- → chk_capacity 执行检查',
        '',
        '-- Trig: 干线骑手 → Idle',
        'COMMIT;',
    ], 14)

    # Stage2
    T(sl, 4.6, 1.3, 4.0, 0.4, 'sp_stage2_deliver', 18, GREEN, True)
    CODE(sl, 4.6, 1.8, 4.0, 1.5, [
        'START TRANSACTION;',
        '',
        "UPDATE orders SET",
        "  order_status='Completed',",
        '  stage2_completed_at=NOW()',
        'WHERE order_id=p_order_id;',
        '',
        'UPDATE pickup_points',
        '  SET current_packages=''current-1',
        '  WHERE point_id=v_point_id',
        '    AND current_packages>0;',
        '',
        '-- Trig: 楼栋骑手 → Idle',
        'COMMIT;',
    ], 14)

    # Cancel
    T(sl, 8.9, 1.3, 4.0, 0.4, 'sp_cancel_order', 18, RED, True)
    MT(sl, 8.9, 1.8, 4.0, 3.0, [
        '✔ 检查状态',
        'Completed/Cancelled 不能取消',
        '',
        '✔ 退款',
        'UPDATE balance + total',
        '',
        '✔ 恢复库存',
        '游标遍历 order_items',
        '→ 逐菜品 stock + qty',
        '',
        '✔ 释放包裹',
        '已入库→ current-1',
        '',
        '✔ 标记取消',
        'Trig → 释放所有骑手',
    ], 14, DARK, Pt(4))

    T(sl, 0.5, 5.5, 12, 1.5, '每个 SP 都有 EXIT HANDLER FOR SQLEXCEPTION → ROLLBACK → RESIGNAL。ACID 的教科书级实现。', 16, GREEN, True)

    # ===== SLIDE 33: Transaction & Capacity =====
    sl = S(prs); bar(sl, '事务回滚与爆仓处理流程', P())
    T(sl, 0.5, 1.3, 12, 0.4, '爆仓时的完整回滚链路', 20, RED, True)
    MT(sl, 0.5, 1.9, 5.5, 4.5, [
        '[1] 用户下单',
        'sp_create_order',
        '→ FOR UPDATE 查容量 → 80/80 满!',
        '→ SIGNAL → 用户看到:',
        '"该寄存点已满，请选邻近寄存点"',
        '→ 用户换 2 期寄存点下单 ✔',
        '',
        '[2] 极端情况（绕过第一层）',
        'sp_arrive_at_pickup_point',
        '→ UPDATE current_packages=81',
        '→ chk_capacity: 81 > 80!',
        '→ ROLLBACK (状态+时间戳全回退)',
        '→ 订单回到 Stage1_Assigned',
        '→ 正常情况走不到这一步',
    ], 15, DARK, Pt(6))
    T(sl, 6.5, 1.9, 6.0, 4.5, '两层防护总结\n\n'
        '✔ 第一层（主动）\n'
        '下单时 FOR UPDATE 查容量\n'
        '满 → 拒绝 + 引导换柜\n'
        '防的是 99.9% 的场景\n\n'
        '✔ 第二层（被动）\n'
        '入库时 chk_capacity 硬约束\n'
        '超 → ROLLBACK\n'
        '防的是 0.1% 的极端并发\n\n'
        '两层之间有 FOR UPDATE\n'
        '保证各自的检查是原子的\n'
        '不会出现"同时看到最后一格"', 15, DARK)

    # ===== SLIDE 34: SECTION 06 =====
    sec(prs, '06', '视图 · 窗口函数 · AI 查询', '饱和度预警 · RANK() OVER · DeepSeek Text-to-SQL')
    P()

    # ===== SLIDE 35: View 1 — Saturation =====
    sl = S(prs); bar(sl, '视图 1：vw_pickup_point_analytics —— 饱和度预警', P())
    CODE(sl, 0.3, 1.3, 7.0, 3.5, [
        'CREATE VIEW vw_pickup_point_analytics AS',
        'SELECT',
        '  p.point_name,',
        '  p.capacity AS max_capacity,',
        '  p.current_packages,',
        '  ROUND(p.current_packages/p.capacity*100, 2)',
        '    AS saturation_pct,          -- 饱和度%',
        '  COALESCE(sub.backlog_count, 0)',
        '    AS backlog_count            -- 溞留件数',
        'FROM pickup_points p',
        'LEFT JOIN (',
        "  SELECT pickup_point_id, COUNT(*) AS cnt",
        '  FROM orders',
        "  WHERE order_status IN ('Arrived_At_Point',",
        "                          'Stage2_Assigned')",
        '  GROUP BY pickup_point_id',
        ') sub ON p.point_id = sub.pickup_point_id;',
    ], 14)
    T(sl, 7.8, 1.3, 5.0, 0.5, '驱动大屏爆仓预警 Tab', 20, ORANGE, True)
    MT(sl, 7.8, 2.0, 5.0, 4.0, [
        '大屏每 30 秒查询一次',
        '',
        'saturation_pct > 80%',
        '→ 黄色预警',
        '→ "接近爆仓，注意调度"',
        '',
        'saturation_pct = 100%',
        '→ 红色爆仓',
        '→ "已满，新订单请换寄存点"',
        '',
        'backlog_count = current_packages',
        '→ chk_capacity 保证绝不超容',
        '',
        '视图 = 把复杂 JOIN 封装成',
        '一条简单的 SELECT',
    ], 15, DARK, Pt(6))

    # ===== SLIDE 36: View 2 — Sales Rank =====
    sl = S(prs); bar(sl, '视图 2：vw_merchant_sales_rank + RANK() OVER 窗口函数', P())
    CODE(sl, 0.3, 1.3, 7.0, 3.0, [
        'CREATE VIEW vw_merchant_sales_rank AS',
        'SELECT',
        '  m.merchant_name,',
        '  COUNT(DISTINCT o.order_id) AS total_orders,',
        '  IFNULL(SUM(o.total_amount), 0) AS total_sales,',
        '',
        '  RANK() OVER (',
        '    ORDER BY SUM(o.total_amount) DESC',
        '  ) AS sales_rank    -- ★ 窗口函数',
        '',
        'FROM merchants m',
        'LEFT JOIN orders o',
        "  ON m.merchant_id = o.merchant_id",
        "  AND o.order_status = 'Completed'",
        'GROUP BY m.merchant_id;',
    ], 14, highlights={7, 8, 9})
    T(sl, 7.8, 1.3, 5.0, 0.5, 'RANK() OVER 是什么？', 20, ORANGE, True)
    MT(sl, 7.8, 2.0, 5.0, 4.0, [
        '窗口函数 = 在结果集的"窗口"',
        '上做计算，不改变行数',
        '',
        '传统做法：',
        '子查询 + @变量漂移',
        '复杂、易出错、性能差',
        '',
        'RANK() OVER：',
        '一行 SQL 搞定排名',
        '数据库引擎优化执行',
        '',
        'RANK() vs ROW_NUMBER()：',
        'RANK: 同分同名次 (1,2,2,4)',
        'DENSE_RANK: 连续名次 (1,2,2,3)',
        'ROW_NUMBER: 无并列 (1,2,3,4)',
    ], 15, DARK, Pt(5))

    # ===== SLIDE 37: AI Text-to-SQL =====
    sl = S(prs); bar(sl, 'AI Text-to-SQL：自然语言查数据库', P())
    TB(sl, 0.5, 1.3, [3.0, 5.5, 3.5],
       ['用户输入', 'AI 生成 SQL', '结果'],
       [
           ['"今天卖了多少钱？"', 'SELECT SUM(total_amount) FROM orders\nWHERE DATE(created_at)=CURDATE()\nAND order_status=\'Completed\'', '12,580 元'],
           ['"哪个寄存点快满了？"', 'SELECT point_name, saturation_pct\nFROM vw_pickup_point_analytics\nORDER BY saturation_pct DESC', '3期 = 100%'],
           ['"最受欢迎商家是谁？"', 'SELECT * FROM vw_merchant_sales_rank\nLIMIT 1', '蜜雪冰城'],
       ], 13)
    T(sl, 0.5, 4.0, 12, 0.5, '技术实现', 20, BLUE, True)
    MT(sl, 0.5, 4.6, 12, 2.0, [
        '✔ Schema 注入：系统提示词包含完整的 7 张表结构 + 字段说明 + ENUM 值 + 视图信息 → AI 准确理解数据库',
        '✔ 安全限制：仅允许 SELECT，禁止 INSERT/UPDATE/DELETE/DROP → AI 幻觉不会破坏数据',
        '✔ 透明展示：前端同时显示生成的 SQL + 查询结果 → 用户可验证 AI 逻辑',
        '✔ 成本极低：DeepSeek API 单次查询 < 0.01 元人民币',
    ], 15, DARK, Pt(6))

    # ===== SLIDE 38: SECTION 07 =====
    sec(prs, '07', '系统大屏与可视化展示', 'Flask + ECharts 实时监控 · 3 个功能 Tab')
    P()

    # ===== SLIDE 39: Dashboard Overview =====
    sl = S(prs); bar(sl, '大屏总览', P())
    PIC(sl, os.path.join(IMG, '01_dashboard_overview.png'), 0.3, 1.3, 12.7)

    # ===== SLIDE 40: KPI Cards =====
    sl = S(prs); bar(sl, 'KPI 指标卡', P())
    PIC(sl, os.path.join(IMG, '04_kpi_top.png'), 0.3, 1.3, 12.7)
    T(sl, 0.5, 6.3, 12, 0.5, '今日订单数 · 今日营收 · 活跃骑手 · 活跃商家 · 爆仓点数 —— 5 个 KPI 卡片，30 秒自动刷新', 16, GRAY)

    # ===== SLIDE 41: Order Management =====
    sl = S(prs); bar(sl, '订单管理', P())
    PIC(sl, os.path.join(IMG, '02_order_section.png'), 0.3, 1.3, 12.7)
    T(sl, 0.5, 6.3, 12, 0.5, '按六态状态筛选 + 实时数据表格 — 每个订单的全程状态一目了然', 16, GRAY)

    # ===== SLIDE 42: Overflow Warning =====
    sl = S(prs); bar(sl, '爆仓预警', P())
    PIC(sl, os.path.join(IMG, '10_overflow_dashboard.png'), 0.3, 1.3, 8.5)
    PIC(sl, os.path.join(IMG, '11_overflow_pickup.png'), 9.2, 1.3, 3.7)
    T(sl, 0.5, 6.3, 12, 0.5, '饱和度柱状图：> 80% 黄色预警  |  100% 红色爆仓  |  实时监控 12 个寄存点', 16, GRAY)

    # ===== SLIDE 43: Pickup Points =====
    sl = S(prs); bar(sl, '寄存点管理', P())
    PIC(sl, os.path.join(IMG, '03_pickup_points.png'), 0.3, 1.3, 12.7)

    # ===== SLIDE 44: More Pages =====
    sl = S(prs); bar(sl, '管理页面', P())
    pages = [('05_merchants.png', 0.3, 1.3, 6.0),
             ('06_students.png', 6.8, 1.3, 6.0),
             ('07_riders.png', 0.3, 4.0, 6.0),
             ('08_dishes.png', 6.8, 4.0, 6.0)]
    for f, x, y, w in pages:
        PIC(sl, os.path.join(IMG, f), x, y, w)

    # ===== SLIDE 45: SECTION 08 =====
    sec(prs, '08', '创新总结与成果交付', '7 大创新 · 项目交付物 · 未来展望')
    P()

    # ===== SLIDE 46: Innovations =====
    sl = S(prs); bar(sl, '七大创新点', P())
    inno = [
        ('FOR UPDATE 行级锁防超卖', 'SELECT...FOR UPDATE 原子化"读-判断-写"，高并发绝不超卖', BLUE),
        ('七重触发器防护体系', '库存(2)+骑手类型(2)+状态管理(2)+容量预检(1)，全自动', BLUE),
        ('两段式配送状态机', '6态ENUM+双骑手+3时间戳，全链路追踪', GREEN),
        ('chk_capacity 硬约束', 'CHECK(current<=capacity)，80格绝不81包，双层防护', GREEN),
        ('RANK() OVER 窗口函数', '一行SQL排名，比应用层更快更准，MySQL 8.0新特性', ORANGE),
        ('AI Text-to-SQL', 'DeepSeek+Schema注入，自然语言查数据，仅允许SELECT', ORANGE),
        ('Cloudflare Tunnel', '免费公网隧道，评委扫码即看实时大屏', RGBColor(0x7B, 0x1F, 0xA2)),
    ]
    for i, (t, d, clr) in enumerate(inno):
        y = 1.2 + i * 0.85
        BADGE(sl, 0.5, y + 0.02, i + 1, clr, 0.45)
        T(sl, 1.2, y + 0.05, 4.0, 0.4, t, 18, clr, True)
        T(sl, 5.5, y + 0.05, 7.0, 0.6, d, 15, DARK)

    # ===== SLIDE 47: Deliverables =====
    sl = S(prs); bar(sl, '项目交付成果', P())
    deliverables = [
        ('数据库', 'campus_delivery_db.sql\n7表 4索引 7触发器\n4SP 2视图', BLUE),
        ('模拟数据', 'generate_mock_data.py\n5000条订单\n容量感知生成器', GREEN),
        ('Flask 大屏', 'app.py + 模板\nREST API + ECharts\nAI Text-to-SQL', ORANGE),
        ('文档', '实践报告.docx\n答辩 PPT.pptx\nREADME.md', RGBColor(0x7B, 0x1F, 0xA2)),
        ('部署', 'Cloudflare Tunnel\n公网访问\n扫码即看', RED),
    ]
    for i, (title, desc, clr) in enumerate(deliverables):
        x = 0.3 + i * 2.55
        CARD(sl, x, 1.8, 2.35, 3.5, title, desc.split('\n'), clr)
    T(sl, 0.5, 6.0, 12, 0.5, 'GitHub: sou1maker/database  |  全部代码已提交推送  |  master 分支', 16, GRAY, align=PP_ALIGN.CENTER)

    # ===== SLIDE 48: Future + Thanks =====
    sl = S(prs); bar(sl, '改进方向', P())
    future = [
        ('柜满排队', '骑手送到的包裹进入等待队列，不抹掉已完成工作', BLUE),
        ('智能调度', '下单时自动推荐邻近有空位的寄存点', GREEN),
        ('路线优化', '楼栋骑手一次取5-8件，路径规划批量配送', ORANGE),
        ('实时追踪', '接入地图API，用户看包裹从商家到寝室', RGBColor(0x7B, 0x1F, 0xA2)),
        ('压测验证', 'sysbench测试QPS上限，验证FOR UPDATE瓶颈', RED),
    ]
    for i, (t, d, clr) in enumerate(future):
        x = 0.3 + i * 2.55
        CARD(sl, x, 1.8, 2.35, 2.5, t, [d], clr)
    T(sl, 1.0, 5.5, 11, 1.0, '感谢各位老师聆听！欢迎扫码访问实时大屏', 24, BLUE, True, PP_ALIGN.CENTER)
    T(sl, 1.0, 6.2, 11, 0.5, 'MySQL 8.0  ·  Flask  ·  ECharts  ·  DeepSeek AI  |  2026 年 6 月', 14, GRAY, align=PP_ALIGN.CENTER)

    P()

    # ===== SAVE =====
    out = os.path.join(os.path.dirname(__file__), '校园外卖两段式配送系统_答辩汇报.pptx')
    prs.save(out)
    print(f'Done: {out}')
    print(f'Slides: {len(prs.slides)}')

if __name__ == '__main__':
    build()
