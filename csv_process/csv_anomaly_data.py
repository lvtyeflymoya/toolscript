import csv

def find_outliers(csv_file, column_index, threshold, output_file):
    outliers = []
    prev_value = 0
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # 读取表头
        for row_num, row in enumerate(reader, start=1):
            try:
                current_value = float(row[column_index]) if row[column_index].strip() else 0
            except (IndexError, ValueError):
                current_value = 0
            diff = abs(current_value - prev_value)
            if diff > threshold:
                outliers.append(row)
            prev_value = current_value

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # 写入表头
        writer.writerows(outliers)

# 使用示例
csv_file = "D:/Python_Project/toolscript/csvfile/up_inside/ETTh1_unsampled.csv"  # 输入的CSV文件
column_index = 1  # 要处理的列的索引，从0开始
threshold = 0.2  # 设定的阈值
output_file = 'output.csv'  # 输出的CSV文件

find_outliers(csv_file, column_index, threshold, output_file)
