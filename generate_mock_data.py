# -*- coding: utf-8 -*-
"""
=================================================================
校园外卖两段式配送数据库系统 · 模拟数据生成器 v3.0
- 历史订单（今天之前）：全部 Completed（外卖时效性）
- 今日订单：真实各种配送状态（实时监控模拟）
- 2个寄存点爆仓（>80%饱和度）
=================================================================
"""

import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import random
import time
from datetime import datetime, timedelta
import os

import pymysql
from faker import Faker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "campus_delivery_db"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
    "cursorclass": pymysql.cursors.DictCursor,
}

fake = Faker("zh_CN")

CAMPUS_NAMES = [
    "张伟", "王芳", "李娜", "刘洋", "陈静", "杨磊", "赵敏", "黄磊",
    "周杰", "吴昊", "徐明", "孙丽", "马超", "朱婷", "胡涛", "郭晶",
    "林峰", "何雪", "高峰", "罗强", "梁敏", "宋阳", "唐燕", "韩冰",
    "曹鑫", "邓丽", "许杰", "彭娟", "苏畅", "潘浩", "田甜", "董亮",
    "范琪", "蔡健", "袁媛", "夏雨", "方静", "石磊", "谭飞", "汪洁",
    "余波", "廖辉", "邹霞", "陆勇", "孔慧", "白梅", "邱毅", "龚倩",
    "岳鹏", "顾雪", "段鑫", "雷杰", "侯涛", "龙敏", "向晨", "文静",
    "姜涛", "乔羽", "安琪", "司马悦",
]
DORM_ZONES = ["1期","2期","3期","4期","5期","6期","7期","8期","A区","B区","C区","D区"]


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def clean_old_data(conn):
    print("=" * 60)
    print("[步骤 0] 清理旧数据……")
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE order_items")
        cursor.execute("TRUNCATE TABLE orders")
        cursor.execute("TRUNCATE TABLE dishes")
        cursor.execute("TRUNCATE TABLE merchants")
        cursor.execute("TRUNCATE TABLE users")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("[完成] 旧数据已清空")


def generate_users(conn, num=100):
    print(f"\n[步骤 1] 生成 {num} 个学生用户……")
    sql = """INSERT INTO users (username, phone, dorm_building, room_number, balance)
             VALUES (%s, %s, %s, %s, %s)"""
    data = []
    used_phones = set()
    for i in range(num):
        username = CAMPUS_NAMES[i % len(CAMPUS_NAMES)]
        while True:
            phone = f"1{random.choice(['38','39','55','77','88','35','36','50','51','52'])}{random.randint(10000000,99999999):08d}"[:11]
            if phone not in used_phones:
                used_phones.add(phone)
                break
        building = f"{random.choice(DORM_ZONES)}{random.randint(1,18)}栋"
        room = f"{random.randint(1,7)}{random.choice(['A','B','C','D'])}{random.randint(1,35):02d}"
        balance = round(random.uniform(30, 800), 2)
        data.append((username, phone, building, room, balance))
    with conn.cursor() as cursor:
        cursor.executemany(sql, data)
    conn.commit()
    print(f"[完成] {num} 个学生用户")


def generate_merchants(conn, num=20):
    print(f"\n[步骤 2] 生成 {num} 个商家……")
    prefixes = ["好再来","天天","一品","香满园","味美滋","食尚","舌尖","小当家","阿妈",
                "旺角","老街","校园","学子","翰林","状元","川湘","粤港","东北","西北","江南"]
    suffixes = ["麻辣烫","黄焖鸡","奶茶店","饺子馆","盖浇饭","米线店","炸鸡店","烘焙坊",
                "水果捞","面馆","煲仔饭","寿司店","麻辣香锅","烤鱼店","煎饼果子",
                "冒菜馆","螺蛳粉","炒饭店","瓦罐汤","烤串店"]
    sql = """INSERT INTO merchants (merchant_name, phone, address, rating)
             VALUES (%s, %s, %s, %s)"""
    data = []
    used_names = set()
    used_phones = set()
    for _ in range(num):
        while True:
            name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
            if name not in used_names:
                used_names.add(name)
                break
        while True:
            phone = f"1{random.choice(['38','39','55','77','88'])}{random.randint(10000000,99999999):08d}"[:11]
            if phone not in used_phones:
                used_phones.add(phone)
                break
        addr = f"{random.choice(['丁香餐厅','玫瑰餐厅','紫荆餐厅','下沉广场','综合楼','学子餐厅'])}{random.choice(['一楼','二楼','三楼','负一楼','负二楼'])}{random.choice(['核心区','侧廊','尽头','入口处','天桥旁'])}"
        rating = round(random.uniform(3.5, 5.0), 1)
        data.append((name, phone, addr, rating))
    with conn.cursor() as cursor:
        cursor.executemany(sql, data)
    conn.commit()
    print(f"[完成] {num} 个商家")


def generate_dishes(conn, dishes_per_merchant=8):
    print(f"\n[步骤 3] 每个商家生成 {dishes_per_merchant} 道菜品……")
    dish_names = [
        "经典麻辣烫","番茄牛腩面","宫保鸡丁饭","鱼香肉丝饭","糖醋里脊饭",
        "酸菜鱼米线","香辣鸡腿堡","珍珠奶茶","芒果冰沙","鸡蛋灌饼",
        "牛肉拉面","蛋炒饭(加蛋)","葱油拌面","小笼包(8只)","煎饺(12只)",
        "烤冷面(加肠)","手抓饼(加蛋)","皮蛋瘦肉粥","豆浆油条套餐","卤肉饭",
        "咖喱鸡肉饭","黑椒牛柳意面","芝士焗饭","日式拉面","韩式拌饭",
        "铁板牛肉饭","红烧排骨饭","酸辣土豆丝","干锅手撕包菜","麻婆豆腐饭",
        "水煮鱼片","蒜蓉生蚝(6个)","烤茄子","羊肉串(10串)","章鱼小丸子",
        "双皮奶","杨枝甘露","烧仙草","芋圆奶茶","抹茶拿铁",
        "奥尔良烤鸡腿","盐酥鸡","甘梅地瓜条","花甲粉丝","锡纸金针菇",
        "螺蛳粉(经典)","炸酱面","热干面","担担面","油泼面",
    ]
    with conn.cursor() as cursor:
        cursor.execute("SELECT merchant_id FROM merchants")
        merchant_ids = [row["merchant_id"] for row in cursor.fetchall()]
    sql = """INSERT INTO dishes (merchant_id, dish_name, price, stock, status)
             VALUES (%s, %s, %s, %s, %s)"""
    data = []
    idx = 0
    for mid in merchant_ids:
        for _ in range(dishes_per_merchant):
            name = dish_names[idx % len(dish_names)]
            idx += 1
            price = round(random.uniform(8, 35), 2)
            stock = random.choice([100, 150, 200, 300, 500, 800, 1000])
            data.append((mid, name, price, stock, 1))
    with conn.cursor() as cursor:
        cursor.executemany(sql, data)
    conn.commit()
    print(f"[完成] {len(data)} 道菜品")


def generate_orders(conn):
    """生成订单：历史全部Completed + 今天各种实时状态"""
    NUM_TODAY = 1500
    NUM_HISTORY = 3500
    TOTAL = NUM_TODAY + NUM_HISTORY
    print(f"\n[步骤 4] 生成 {TOTAL} 条订单（{NUM_HISTORY}历史 + {NUM_TODAY}今日）……")

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row["user_id"] for row in cursor.fetchall()]
        cursor.execute("SELECT merchant_id FROM merchants")
        merchant_ids = [row["merchant_id"] for row in cursor.fetchall()]
        cursor.execute("SELECT point_id, point_name, capacity FROM pickup_points")
        points_data = cursor.fetchall()
        cursor.execute("SELECT dish_id, merchant_id, price FROM dishes")
        dishes_data = cursor.fetchall()
        cursor.execute("SELECT rider_id, rider_type FROM riders")
        riders_data = cursor.fetchall()

    trunk_riders = [r["rider_id"] for r in riders_data if r["rider_type"] == "Stage1_Trunk"]
    floor_riders = [r["rider_id"] for r in riders_data if r["rider_type"] == "Stage2_Floor"]

    dishes_by_merchant = {}
    for d in dishes_data:
        dishes_by_merchant.setdefault(d["merchant_id"], []).append(d)

    # 找爆仓目标寄存点：3期（容量80）和6期（容量50）
    overload_targets = []
    for p in points_data:
        if "3期" in p["point_name"]:
            overload_targets.append((p["point_id"], p["capacity"], "3期"))
        if "6期" in p["point_name"]:
            overload_targets.append((p["point_id"], p["capacity"], "6期"))

    # 今日订单状态权重（模拟实时配送流）
    today_statuses = (
        ["Paid"] * 10 +
        ["Stage1_Assigned"] * 15 +
        ["Arrived_At_Point"] * 15 +
        ["Stage2_Assigned"] * 20 +
        ["Completed"] * 38 +
        ["Cancelled"] * 2
    )

    order_sql = """INSERT INTO orders
        (user_id, merchant_id, pickup_point_id, total_amount, order_status,
         stage1_rider_id, stage2_rider_id,
         created_at, stage1_completed_at, stage2_completed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    item_sql = """INSERT INTO order_items
        (order_id, dish_id, quantity, price_at_order)
        VALUES (%s, %s, %s, %s)"""

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Track backlog per point (Arrived_At_Point + Stage2_Assigned)
    # Enforce: no point exceeds its capacity
    point_backlog = {p["point_id"]: 0 for p in points_data}

    # Target overload: 3期 and 6期 fill to ~85% for dashboard demo
    overload_target_ids = [pid for pid, _, _ in overload_targets]
    overload_target_fill = {pid: int(cap * 0.85) for pid, cap, _ in overload_targets}

    with conn.cursor() as cursor:
        for i in range(TOTAL):
            user_id = random.choice(user_ids)
            merchant_id = random.choice(merchant_ids)

            if i < NUM_HISTORY:
                # ---- 历史订单：全部 Completed ----
                days_ago = random.randint(1, 30)
                hour = random.randint(8, 22)
                minute = random.randint(0, 59)
                created_at = today_start - timedelta(days=days_ago, hours=24-hour, minutes=minute)
                created_at = created_at.replace(second=random.randint(0, 59))
                order_status = "Completed"
                stage1_completed_at = created_at + timedelta(minutes=random.randint(10, 40))
                stage2_completed_at = stage1_completed_at + timedelta(minutes=random.randint(5, 25))
                stage1_rider = None
                stage2_rider = None
                point_id = random.choice(points_data)["point_id"]
            else:
                # ---- 今日订单：真实配送状态 ----
                order_status = random.choice(today_statuses)
                # 时间分布在今天 8:00 到现在
                max_hour = now.hour
                max_minute = now.minute
                if max_hour < 8:
                    max_hour = 8
                    max_minute = 0
                hour = random.randint(8, max_hour) if max_hour > 8 else 8
                if hour == max_hour:
                    minute = random.randint(0, max_minute)
                else:
                    minute = random.randint(0, 59)
                created_at = today_start.replace(hour=hour, minute=minute, second=random.randint(0, 59))

                # 寄存点容量约束：Arrived_At_Point / Stage2_Assigned 算入当前包裹数
                # 模拟真实 sp_arrive_at_pickup_point 的 chk_capacity CHECK 约束
                point_id = random.choice(points_data)["point_id"]
                if order_status in ("Arrived_At_Point", "Stage2_Assigned"):
                    # 优先把爆仓目标点填充到 ~85%（展示大屏预警效果）
                    for pid in overload_target_ids:
                        if point_backlog[pid] < overload_target_fill[pid]:
                            point_id = pid
                            break
                    # 如果选中点已满，找还有空位的点
                    point_cap = next(p["capacity"] for p in points_data if p["point_id"] == point_id)
                    if point_backlog[point_id] >= point_cap:
                        available_points = [p for p in points_data if point_backlog[p["point_id"]] < p["capacity"]]
                        if available_points:
                            point_id = random.choice(available_points)["point_id"]
                        else:
                            # 所有点都满了 → 此状态无法入仓，降级为 Completed
                            order_status = "Completed"
                    if order_status in ("Arrived_At_Point", "Stage2_Assigned"):
                        point_backlog[point_id] += 1

                # Rider assignment — follow real flow:
                # Paid: no rider
                # Stage1_Assigned: trunk rider assigned
                # Arrived_At_Point: trunk rider stays (trigger releases him when status changes)
                # Stage2_Assigned: floor rider assigned
                # Completed/Cancelled: no riders active
                stage1_rider = None
                stage2_rider = None
                if order_status == "Stage1_Assigned":
                    stage1_rider = random.choice(trunk_riders) if trunk_riders else None
                elif order_status == "Arrived_At_Point":
                    # Inherit trunk rider from Stage1 so trigger can release him
                    stage1_rider = random.choice(trunk_riders) if trunk_riders else None
                elif order_status == "Stage2_Assigned":
                    stage2_rider = random.choice(floor_riders) if floor_riders else None
                elif order_status == "Completed":
                    # Completed orders passed through both stages, keep rider IDs for history
                    stage1_rider = random.choice(trunk_riders) if trunk_riders else None
                    stage2_rider = random.choice(floor_riders) if floor_riders else None

                # 时间戳
                stage1_completed_at = None
                stage2_completed_at = None
                if order_status in ("Arrived_At_Point", "Stage2_Assigned", "Completed"):
                    stage1_completed_at = created_at + timedelta(minutes=random.randint(10, 40))
                if order_status == "Completed":
                    base = stage1_completed_at or created_at
                    stage2_completed_at = base + timedelta(minutes=random.randint(5, 25))

            # 拼装菜品
            available = dishes_by_merchant.get(merchant_id, [])
            if not available:
                continue
            dish = random.choice(available)
            qty = random.randint(1, 3)
            price = float(dish["price"])
            total = round(price * qty, 2)

            cursor.execute(order_sql, (
                user_id, merchant_id, point_id, total, order_status,
                stage1_rider, stage2_rider,
                created_at, stage1_completed_at, stage2_completed_at,
            ))
            cursor.execute("SELECT LAST_INSERT_ID()")
            order_id = list(cursor.fetchone().values())[0]
            cursor.execute(item_sql, (order_id, dish["dish_id"], qty, price))

            if (i + 1) % 500 == 0 or i == TOTAL - 1:
                conn.commit()
                print(f"   [进度] {i+1}/{TOTAL} ({ (i+1)*100//TOTAL }%)")

    # Sync rider status: triggers auto-manage Delivering on assignment.
    # Bulk INSERT fires AFTER INSERT trigger which skips Completed/Cancelled/Arrived_At_Point.
    # But we also need to handle riders on stage1 who should be Delivering.
    # Simple approach: set ALL riders Idle, then explicitly set Delivering for active ones.
    print("\n   [Riders] Syncing rider status...")
    with conn.cursor() as cursor:
        cursor.execute("UPDATE riders SET status = 'Idle'")
        cursor.execute("""
            UPDATE riders r SET r.status = 'Delivering'
            WHERE r.rider_id IN (
                SELECT o.stage1_rider_id FROM orders o
                WHERE o.order_status IN ('Paid','Stage1_Assigned') AND o.stage1_rider_id IS NOT NULL
                UNION
                SELECT o.stage2_rider_id FROM orders o
                WHERE o.order_status IN ('Arrived_At_Point','Stage2_Assigned') AND o.stage2_rider_id IS NOT NULL
            )
        """)
        conn.commit()
        cursor.execute("SELECT COUNT(*) AS cnt FROM riders WHERE status = 'Delivering'")
        print(f"   [Riders] {cursor.fetchone()['cnt']} riders delivering")


    # 同步寄存点包裹计数（backlog <= capacity 由生成阶段保证）
    print("\n   [寄存点] 同步包裹计数……")
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT pp.point_id, pp.point_name, pp.capacity, COUNT(o.pickup_point_id) AS cnt
            FROM pickup_points pp
            LEFT JOIN orders o ON pp.point_id = o.pickup_point_id
                AND o.order_status IN ('Arrived_At_Point', 'Stage2_Assigned')
            GROUP BY pp.point_id, pp.point_name, pp.capacity
        """)
        overflow_count = 0
        for row in cursor.fetchall():
            cnt = row["cnt"]
            # assert: cnt <= capacity (enforced during generation)
            cursor.execute("UPDATE pickup_points SET current_packages = %s WHERE point_id = %s",
                           (cnt, row["point_id"]))
            pct = cnt / row["capacity"] * 100 if row["capacity"] > 0 else 0
            flag = "  << 爆仓!" if pct > 80 else ""
            if pct > 80:
                overflow_count += 1
            print(f"   {row['point_name']}: {cnt}/{row['capacity']} = {pct:.1f}%{flag}")
        conn.commit()

    print(f"\n[完成] {TOTAL} 条订单生成完毕")


def main():
    start = time.time()
    print("\n" + "=" * 50)
    print("  校园外卖模拟数据生成器 v3.0")
    print("  历史订单=全部已完成 | 今日订单=实时状态")
    print("=" * 50)

    conn = get_connection()
    try:
        clean_old_data(conn)
        generate_users(conn, 100)
        generate_merchants(conn, 20)
        generate_dishes(conn, 8)
        generate_orders(conn)
        elapsed = time.time() - start
        print(f"\n{'=' * 50}")
        print(f"  全部完成! 耗时 {elapsed:.1f} 秒")
        print(f"{'=' * 50}")
    except Exception as e:
        print(f"\n[错误] {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
