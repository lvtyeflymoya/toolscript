# 选择指定列生成新CSV
import pandas as pd

def select_columns(input_path, output_path, selected_columns):
    """选择指定列生成新CSV"""
    try:
        # 自动检测编码读取
        try:
            df = pd.read_csv(input_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(input_path, encoding='gbk')
        
        # 验证列是否存在
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            available = ', '.join(df.columns)
            print(f"错误：以下列不存在 {missing_cols}\n可用列：{available}")
            return
        
        # 生成新数据集
        new_df = df[selected_columns]
        
        # 保存新CSV（保持原有编码）
        new_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"成功生成新文件，包含 {len(new_df)} 行数据")
        
    except FileNotFoundError:
        print(f"错误：输入文件 {input_path} 不存在")

# 使用示例
if __name__ == "__main__":
    input_file = "D:/Python_Project/tsai/trainResult/experiment34/test/predictions.csv"  # 替换输入路径
    output_file = "1111.csv"  # 替换输出路径
    target_columns = ["date", "down_inside_fuse"]  # 替换目标列名
    
    select_columns(input_file, output_file, target_columns)
