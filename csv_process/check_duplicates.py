import pandas as pd

def check_duplicate_timestamps(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['date'])
    
    # 改进的重复值检测逻辑
    # 获取出现次数大于1的时间戳
    timestamp_counts = df['date'].value_counts()
    duplicate_timestamps = timestamp_counts[timestamp_counts > 1]
    
    if not duplicate_timestamps.empty:
        print(f"发现 {len(duplicate_timestamps)} 个独立重复时间戳")
        print(f"总重复行数：{duplicate_timestamps.sum()}")
        print("各重复值出现次数：")
        print(duplicate_timestamps)
    else:
        print("没有发现重复的时间戳")

# 使用示例（请确认文件路径是否正确）

check_duplicate_timestamps('d:/Python_Project/tsai/trainResult/experiment34/test/predictions.csv')


def find_zero_values(csv_path, column_name):
    """查找指定列中值为0的行并输出详细信息"""
    df = pd.read_csv(csv_path)
    
    # 查找指定列中值为0的行
    zero_rows = df[df[column_name] == 0]
    
    if not zero_rows.empty:
        print(f"在列 '{column_name}' 中发现 {len(zero_rows)} 个零值")
        for index, row in zero_rows.iterrows():
            print(f"\n行号 {index}:")
            print(row.to_string())
    else:
        print(f"列 '{column_name}' 中没有发现零值")

# 使用示例（请修改为实际文件路径和列名）
# find_zero_values('d:/Python_Project/tsai/trainResult/experiment34/test/predictions.csv', 'target_column')