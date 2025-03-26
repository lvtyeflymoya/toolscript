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
