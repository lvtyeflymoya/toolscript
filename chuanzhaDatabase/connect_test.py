import pymysql

def connect_to_mysql():
    # 数据库连接配置（请替换为实际参数）
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'moya6589',
        'database': 'waterlevel'
    }

    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**config)
        
        # 创建游标对象验证连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # 连接成功输出信息
        print(f"成功连接到MySQL数据库！")
        print(f"主机: {config['host']}:{config['port']}")
        print(f"数据库: {config['database']}")
        
    except pymysql.Error as e:
        print(f"连接失败: {e}")
    finally:
        # 确保关闭连接
        if connection:
            connection.close()

if __name__ == "__main__":
    connect_to_mysql()