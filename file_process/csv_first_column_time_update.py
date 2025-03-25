# 将CSV文件的第一列按照固定时间间隔依次增加进行重新编写
import csv
from datetime import datetime, timedelta

def update_first_column_with_time_interval(input_file, output_file, start_time_str, time_interval):
    """
    该函数用于将CSV文件的第一列按照固定时间间隔依次增加进行重新编写
    :param input_file: 输入的CSV文件路径
    :param output_file: 输出的CSV文件路径
    :param start_time_str: 起始时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
    :param time_interval: 时间间隔（秒）
    """
    # 将起始时间字符串转换为datetime对象
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        # 写入表头
        header = next(reader)
        writer.writerow(header)
        # 从起始时间开始，按固定时间间隔更新第一列
        current_time = start_time
        for row in reader:
            # 将更新后的时间转换为字符串
            row[0] = current_time.strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(row)
            # 增加时间间隔
            current_time += timedelta(seconds=time_interval)

# 使用示例
if __name__ == "__main__":
    input_file = 'D:/Python_Project/toolscript/ETTh1.csv'
    output_file = 'output.csv'
    start_time_str = '2023-07-01 00:00:00'
    time_interval = 60  # 时间间隔为60秒
    update_first_column_with_time_interval(input_file, output_file, start_time_str, time_interval)

