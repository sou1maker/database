"""在现有数据库基础上，增加寄存点和骑手"""
import sys
import io

# ---- 解决 Windows 终端中文乱码 ----
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pymysql, os
from dotenv import load_dotenv
load_dotenv('.env')

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE", "campus_delivery_db"),
    charset="utf8mb4",
)

with conn.cursor() as cur:
    # 1. 增加 6 个新寄存点
    extra_points = [
        ('7期智能寄存柜', '7期3栋一楼楼梯间', 60),
        ('8期智能寄存柜', '8期北门快递站旁', 120),
        ('A区智能寄存柜', 'A区综合服务大厅', 100),
        ('B区智能寄存柜', 'B区图书馆负一层', 90),
        ('C区智能寄存柜', 'C区体育馆入口处', 70),
        ('D区智能寄存柜', 'D区研究生公寓大堂', 80),
    ]
    inserted = 0
    for name, loc, cap in extra_points:
        cur.execute("SELECT COUNT(*) FROM pickup_points WHERE point_name=%s", (name,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO pickup_points (point_name, location, capacity, current_packages) VALUES (%s,%s,%s,0)", (name, loc, cap))
            inserted += 1
    print(f"新增 {inserted} 个寄存点")

    # 2. 增加 12 名新骑手（5名干线 + 7名楼栋）
    extra_riders = [
        ('李大力', '15599994444', 'Stage1_Trunk'),
        ('周小飞', '15599995555', 'Stage1_Trunk'),
        ('刘强东', '15599996666', 'Stage1_Trunk'),
        ('吴勇军', '15599997777', 'Stage1_Trunk'),
        ('郑明达', '15599998888', 'Stage1_Trunk'),
        ('黄启航', '15599999999', 'Stage1_Trunk'),
        ('马小跳', '15611111111', 'Stage2_Floor'),
        ('林志远', '15611112222', 'Stage2_Floor'),
        ('张小凡', '15611113333', 'Stage2_Floor'),
        ('陈奕迅', '15611114444', 'Stage2_Floor'),
        ('李逍遥', '15611115555', 'Stage2_Floor'),
        ('赵灵儿', '15611116666', 'Stage2_Floor'),
    ]
    inserted_r = 0
    for name, phone, rtype in extra_riders:
        cur.execute("SELECT COUNT(*) FROM riders WHERE phone=%s", (phone,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO riders (rider_name, phone, rider_type, status) VALUES (%s,%s,%s,'Idle')", (name, phone, rtype))
            inserted_r += 1
    print(f"新增 {inserted_r} 名骑手")
    conn.commit()

    # 验证
    cur.execute("SELECT COUNT(*) FROM pickup_points")
    print(f"寄存点总数: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM riders")
    print(f"骑手总数: {cur.fetchone()[0]}")

conn.close()
