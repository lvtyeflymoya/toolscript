# 将数据库sql文件转成csv文件
import re
import csv
from tqdm import tqdm

def sql_to_csv(sql_path, csv_path):
    # 提取表结构中的列名
    column_pattern = re.compile(r'`(\w+)`')
    columns = []
    
    # 第一次扫描获取列名
    with open(sql_path, 'r', encoding='utf-8') as sql_file:
        create_table_found = False
        for line in sql_file:
            if 'CREATE TABLE' in line.upper():
                create_table_found = True
                continue
            if create_table_found:
                if line.strip().startswith(')'):
                    break
                match = column_pattern.search(line)
                if match:
                    columns.append(match.group(1))
    
    # 写入CSV文件
    with open(sql_path, 'r', encoding='utf-8') as sql_file, \
         open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        
        writer = csv.writer(csv_file)
        writer.writerow(columns)  # 写入表头
        
        insert_pattern = re.compile(
            r'INSERT\s+INTO\s+`?\w+`?\s+VALUES\s+(.+?);?$',
            re.IGNORECASE
        )
        
        value_pattern = re.compile(
            r'''((?:[^,'"]*(?:(?<!')'[^']*'(?!')|(?<!")"[^"]*"(?!")|[^,'"]*))+)''',
            re.DOTALL
        )

        # 使用tqdm添加进度条
        for line in tqdm(sql_file, desc='处理进度', unit='行'):
            if not line.strip().upper().startswith('INSERT'):
                continue
                
            # 提取VALUES部分
            values_match = insert_pattern.search(line)
            if not values_match:
                continue
                
            values_str = values_match.group(1)
            
            # 分割多个值元组
            for tuple_str in re.split(r'(?<=\S)\)\s*,\s*\(\s*(?=\S)', values_str):
                tuple_str = tuple_str.strip(' ()')
                values = []
                current = []
                in_quote = False
                quote_char = None
                
                # 精确分割带引号的值
                for char in tuple_str:
                    if char in ("'", '"') and not in_quote:
                        in_quote = True
                        quote_char = char
                    elif char == quote_char and in_quote:
                        in_quote = False
                        quote_char = None
                    elif char == ',' and not in_quote:
                        values.append(''.join(current).strip())
                        current = []
                        continue
                    current.append(char)
                if current:
                    values.append(''.join(current).strip())
                
                # 去除引号并处理空值
                cleaned = []
                for val in values:
                    val = val.strip()
                    if val.startswith(("'", '"')) and val.endswith(("'", '"')):
                        val = val[1:-1]
                    cleaned.append(val if val != 'NULL' else '')
                
                writer.writerow(cleaned)

if __name__ == '__main__':
    sql_to_csv("C:/Users/Zhang/Desktop/2023_07.sql", 'C:/Users/Zhang/Desktop/output.csv')
