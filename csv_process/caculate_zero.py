# 计算某列中有多少个0
import pandas as pd

def find_zero_values(csv_path, column_name):
    """查找指定列中值为0的行并输出详细信息"""
    df = pd.read_csv(csv_path)
    
    # 查找指定列中值为0的行
    zero_rows = df[df[column_name] == 0]
    
    if not zero_rows.empty:
        print(f"在列 '{column_name}' 中发现 {len(zero_rows)} 个零值")
        # for index, row in zero_rows.iterrows():
        #     # 使用正确的width参数并格式化输出
        #     print(f"行号 {index}: {row.to_string().replace('\n', ' ')}")  # <- 修正这里
    else:
        print(f"列 '{column_name}' 中没有发现零值")

def remove_last_column(csv_path, output_path=None):
    """删除CSV文件的最后一列并保存"""
    df = pd.read_csv(csv_path)
    
    if len(df.columns) < 1:
        print("错误：文件没有可删除的列")
        return
    
    # 获取并删除最后一列
    last_column = df.columns[-1]
    df.drop(columns=last_column, inplace=True)
    
    # 设置默认输出路径
    if output_path is None:
        output_path = csv_path.replace(".csv", "_modified.csv")
    
    df.to_csv(output_path, index=False)
    print(f"已删除列 '{last_column}'，保存文件至：{output_path}")

# 使用示例
# remove_last_column('D:/Python_Project/cluster/modified_data.csv')  # 默认生成input_modified.csv
# remove_last_column('input.csv', 'output.csv')  # 指定输出路径

# 使用示例（请修改为实际文件路径和列名）
find_zero_values('D:/Python_Project/cluster/test_dataset/upoutside_unsamped/modified_data_cluster.csv', 'is_tampered')
