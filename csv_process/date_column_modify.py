# 将csv文件中的时间列修改为指定起始时间的秒级时间戳
import pandas as pd

def regenerate_timestamps(input_csv, output_csv, start_time):
    """
    重新生成指定起始时间的秒级时间戳
    参数：
    input_csv: 输入文件路径
    output_csv: 输出文件路径
    start_time: 起始时间字符串，格式：'YYYY-MM-DD HH:MM:SS'
    """
    # 读取原始数据（仅保留数据列）
    df = pd.read_csv(input_csv)
    
    # 生成新时间列（高效向量化操作）
    new_dates = pd.date_range(
        start=start_time,
        periods=len(df),
        freq='S'  # 按秒递增
    )
    
    # 替换时间列并保存
    df['date'] = new_dates
    df.to_csv(output_csv, index=False)
    print(f"时间列已重置，从 {start_time} 开始每秒递增")

# 使用示例
if __name__ == "__main__":
    regenerate_timestamps(
        input_csv='D:/Python_Project/toolscript/csvfile/up_outside/up_outside_fuse_all.csv',
        output_csv='D:/Python_Project/toolscript/csvfile/up_outside/ETTh1_unsampled.csv',
        start_time='2023-07-01 00:00:00'  # 在此修改起始时间
    )
