import csv
from datetime import datetime

def remove_data_in_time_range(input_file, output_file, start_time, end_time):
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 写入表头
        header = next(reader)
        writer.writerow(header)

        for row in reader:
            # 假设第一列是时间
            time_str = row[0]
            current_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            # 如果当前时间不在指定范围内，则写入新文件
            if current_time < start or current_time > end:
                writer.writerow(row)

# 使用示例
input_file = 'D:/Python_Project/cluster/test_dataset/upoutside_unsamped/up_outside_vision_denoised_savgol.csv'
output_file = 'D:/Python_Project/cluster/test_dataset/upoutside_unsamped/up_outside_vision_denoised.csv'
start_time = '2023-07-03 10:00:00'
end_time = '2023-07-03 19:00:00'

remove_data_in_time_range(input_file, output_file, start_time, end_time)
