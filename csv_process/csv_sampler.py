# 每个固定行数取一条数据
import csv

def sample_csv(input_path, output_path, interval=6):
    """每隔指定行数采样数据"""
    with open(input_path, 'r', newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 保留标题行
        header = next(reader)
        writer.writerow(header)
        
        # 数据采样逻辑
        for index, row in enumerate(reader, start=1):
            if index % interval == 0:
                writer.writerow(row)

if __name__ == '__main__':
    sample_csv('D:/Python_Project/toolscript/csvfile/up_inside/ETTh1_unsampled.csv', 
               'D:/Python_Project/toolscript/csvfile/up_inside/ETTh1.csv', interval=60)
