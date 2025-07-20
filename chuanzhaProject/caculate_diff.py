import pandas as pd

# 读取 CSV 文件
file_path = 'D:\Python_Project\cluster\modified_data.csv'
df = pd.read_csv(file_path)

# 计算水位高度的差值
df['diff222'] = df['modified_water_level'].diff()
# import numpy as np
# df['diff222'] = np.random.randint(0, 2, size=len(df)

# 将结果保存到新的 CSV 文件
output_file = 'D:\Python_Project\cluster\modified_data2222.csv'
df.to_csv(output_file, index=False)

print(f"处理完成，结果已保存到 {output_file}")
