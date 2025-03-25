import pymysql
import csv

# 数据库配置（需要根据实际修改）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'moya6589',
    'db': 'waterlevel',
    'charset': 'utf8mb4'
}

TABLE_NAME = 'WaterLine'

    # 连接数据库
connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    # 执行查询
    sql = f"SELECT `time`, `down_outside_fuse` FROM `{TABLE_NAME}`"
    cursor.execute(sql)
    results = cursor.fetchall()
    # 写入CSV文件
    with open('waterline_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'down_outside_fuse'])  # 写入表头
        for row in results:
            writer.writerow([row['time'], row['down_outside_fuse']])
connection.close()