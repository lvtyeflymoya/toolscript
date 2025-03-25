import pymysql
import random
import datetime
import string
import sys

# 连接到 MySQL 数据库
try:
    mydb = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="moya6589",
        database="waterlevel"
    )
    mycursor = mydb.cursor()
    print("数据库连接成功，服务信息：")
except pymysql.Error as err:
    print(f"数据库连接失败: {err}")
    sys.exit(1)

# 初始化起始时间
current_time = datetime.datetime.now().replace(microsecond=0)

# 生成随机数据并插入表中
for _ in range(10000):
    # 使用当前时间
    time = current_time
    data = (
        time,
        *[random.uniform(0, 100) for _ in range(16)],  # 16个浮点型传感器数据
        *[random.randint(0, 1) for _ in range(4)],     # 4个警报区域状态
        *[random.randint(0, 100) for _ in range(2)],   # 上下闸门状态
        *[random.uniform(0, 100) for _ in range(4)]    # 4个应变传感器数据
    )

    sql = """INSERT INTO WaterLine (
        time, down_outside_fuse, down_outside_vision, down_outside_laser, down_outside_pressure,
        down_outside_alertarea, down_gate, down_inside_fuse, down_inside_vision, down_inside_laser,
        down_inside_pressure, down_inside_alertarea, up_inside_fuse, up_inside_vision, up_inside_laser,
        up_inside_pressure, up_inside_alertarea, up_gate, up_outside_fuse, up_outside_vision,
        up_outside_laser, up_outside_pressure, up_outside_alertarea, up_strain1, up_strain2,
        down_strain3, down_strain4
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    mycursor.execute(sql, data)
    # 将时间增加一分钟
    current_time = current_time + datetime.timedelta(minutes=1)

# 提交更改
mydb.commit()

print(mycursor.rowcount, "记录插入成功。")

# 关闭连接
mycursor.close()
mydb.close()