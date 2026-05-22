"""用 Python 重建完整数据库（兼容 pymysql，跳过 DELIMITER 语法）"""
import sys
import io

# ---- 解决 Windows 终端中文乱码 ----
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pymysql, os
from dotenv import load_dotenv
load_dotenv('.env')

PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("MYSQL_HOST", "localhost")
USER = os.getenv("MYSQL_USER", "root")

conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, charset="utf8mb4")
cur = conn.cursor()
cur.execute("DROP DATABASE IF EXISTS campus_delivery_db")
cur.execute("CREATE DATABASE campus_delivery_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
cur.execute("USE campus_delivery_db")

# 手动创建所有表（不含存储过程）
tables = [
    # users
    """CREATE TABLE users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE,
        dorm_building VARCHAR(20) NOT NULL,
        room_number VARCHAR(10) NOT NULL,
        balance DECIMAL(10,2) DEFAULT 100.00 CHECK (balance >= 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # merchants
    """CREATE TABLE merchants (
        merchant_id INT AUTO_INCREMENT PRIMARY KEY,
        merchant_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        address VARCHAR(200) NOT NULL,
        rating DECIMAL(2,1) DEFAULT 5.0 CHECK (rating >= 1.0 AND rating <= 5.0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # dishes
    """CREATE TABLE dishes (
        dish_id INT AUTO_INCREMENT PRIMARY KEY,
        merchant_id INT NOT NULL,
        dish_name VARCHAR(100) NOT NULL,
        price DECIMAL(8,2) NOT NULL CHECK (price > 0),
        stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
        status TINYINT DEFAULT 1 CHECK (status IN (0, 1)),
        CONSTRAINT fk_dish_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id) ON DELETE RESTRICT ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # pickup_points
    """CREATE TABLE pickup_points (
        point_id INT AUTO_INCREMENT PRIMARY KEY,
        point_name VARCHAR(50) NOT NULL,
        location VARCHAR(200) NOT NULL,
        capacity INT NOT NULL,
        current_packages INT DEFAULT 0 CHECK (current_packages >= 0),
        CONSTRAINT chk_capacity CHECK (current_packages <= capacity)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # riders
    """CREATE TABLE riders (
        rider_id INT AUTO_INCREMENT PRIMARY KEY,
        rider_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE,
        rider_type ENUM('Stage1_Trunk', 'Stage2_Floor') NOT NULL,
        status ENUM('Idle', 'Delivering', 'Offline') DEFAULT 'Idle'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # orders
    """CREATE TABLE orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        merchant_id INT NOT NULL,
        pickup_point_id INT NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        order_status ENUM('Paid','Stage1_Assigned','Arrived_At_Point','Stage2_Assigned','Completed','Cancelled') DEFAULT 'Paid',
        stage1_rider_id INT DEFAULT NULL,
        stage2_rider_id INT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        stage1_completed_at TIMESTAMP NULL DEFAULT NULL,
        stage2_completed_at TIMESTAMP NULL DEFAULT NULL,
        CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users(user_id),
        CONSTRAINT fk_order_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
        CONSTRAINT fk_order_point FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(point_id),
        CONSTRAINT fk_order_rider1 FOREIGN KEY (stage1_rider_id) REFERENCES riders(rider_id),
        CONSTRAINT fk_order_rider2 FOREIGN KEY (stage2_rider_id) REFERENCES riders(rider_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    # order_items
    """CREATE TABLE order_items (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        dish_id INT NOT NULL,
        quantity INT NOT NULL CHECK (quantity > 0),
        price_at_order DECIMAL(8,2) NOT NULL,
        CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        CONSTRAINT fk_item_dish FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]

for t in tables:
    cur.execute(t)

# 建索引
cur.execute("CREATE INDEX idx_orders_status ON orders(order_status)")
cur.execute("CREATE INDEX idx_orders_created ON orders(created_at)")
cur.execute("CREATE INDEX idx_dishes_merchant ON dishes(merchant_id, status)")

# 种子数据：3个学生
for u in [('张三','13800138001','1期5栋','A302',250.00),('李四','13800138002','1期5栋','B511',15.00),('王五','13800138003','2期12栋','404',500.00)]:
    cur.execute("INSERT INTO users (username,phone,dorm_building,room_number,balance) VALUES (%s,%s,%s,%s,%s)", u)

# 种子数据：3个商家
for m in [('一号黄焖鸡米饭','17711112222','丁香餐厅一楼3号档口',4.8),('川湘木桶饭','17711113333','玫瑰餐厅二楼核心区',4.6),('蜜雪冰城校园店','17711114444','下沉广场天桥旁',4.9)]:
    cur.execute("INSERT INTO merchants (merchant_name,phone,address,rating) VALUES (%s,%s,%s,%s)", m)

# 种子数据：4个菜品
cur.execute("INSERT INTO dishes (merchant_id,dish_name,price,stock,status) VALUES (1,'经典大份黄焖鸡(配饭)',18.00,50,1)")
cur.execute("INSERT INTO dishes (merchant_id,dish_name,price,stock,status) VALUES (1,'香辣金针菇肥牛饭',22.00,0,1)")
cur.execute("INSERT INTO dishes (merchant_id,dish_name,price,stock,status) VALUES (2,'辣椒炒肉木桶饭',15.00,100,1)")
cur.execute("INSERT INTO dishes (merchant_id,dish_name,price,stock,status) VALUES (3,'冰鲜柠檬水(超大杯)',4.00,200,1)")

# 12个寄存点
points = [
    ('1期智能寄存柜','1期5栋与6栋之间车棚旁',80),
    ('2期智能寄存柜','2期12栋宿管值班室对面',80),
    ('3期智能寄存柜','3期8栋楼下大厅',80),
    ('4期智能寄存柜','4期2栋架空层',80),
    ('5期智能寄存柜','5期生活广场东侧',100),
    ('6期智能寄存柜','6期食堂旁',50),
    ('7期智能寄存柜','7期3栋一楼楼梯间',60),
    ('8期智能寄存柜','8期北门快递站旁',120),
    ('A区智能寄存柜','A区综合服务大厅',100),
    ('B区智能寄存柜','B区图书馆负一层',90),
    ('C区智能寄存柜','C区体育馆入口处',70),
    ('D区智能寄存柜','D区研究生公寓大堂',80),
]
for n,l,c in points:
    cur.execute("INSERT INTO pickup_points (point_name,location,capacity,current_packages) VALUES (%s,%s,%s,0)", (n,l,c))

# 15名骑手
riders = [
    ('赵铁柱','15599991111','Stage1_Trunk'),
    ('王大锤','15599992222','Stage1_Trunk'),
    ('李大力','15599994444','Stage1_Trunk'),
    ('周小飞','15599995555','Stage1_Trunk'),
    ('刘强东','15599996666','Stage1_Trunk'),
    ('吴勇军','15599997777','Stage1_Trunk'),
    ('郑明达','15599998888','Stage1_Trunk'),
    ('黄启航','15599999999','Stage1_Trunk'),
    ('牛干劲','15599993333','Stage2_Floor'),
    ('马小跳','15611111111','Stage2_Floor'),
    ('林志远','15611112222','Stage2_Floor'),
    ('张小凡','15611113333','Stage2_Floor'),
    ('陈奕迅','15611114444','Stage2_Floor'),
    ('李逍遥','15611115555','Stage2_Floor'),
    ('赵灵儿','15611116666','Stage2_Floor'),
]
for n,p,t in riders:
    cur.execute("INSERT INTO riders (rider_name,phone,rider_type,status) VALUES (%s,%s,%s,'Idle')", (n,p,t))

conn.commit()
cur.close()
conn.close()
print("[OK] 数据库重建成功！")
print("  - 12 个寄存点")
print("  - 15 名骑手")
print("  现在请运行: python generate_mock_data.py")
