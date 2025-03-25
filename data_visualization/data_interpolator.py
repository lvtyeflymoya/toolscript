import pandas as pd

def interpolate_and_save(input_path, output_path, freq='S', limit=3600):  # 修改1：默认按秒采样
    """
    独立插值处理函数
    参数：
    input_path: 原始数据路径
    output_path: 输出文件路径
    freq: 重采样频率，默认5分钟
    limit: 最大连续插值点数
    """
    # 分块读取大文件
    chunk_iter = pd.read_csv(input_path, 
                           parse_dates=['date'],
                           chunksize=100000)
    
    full_df = []
    for chunk in chunk_iter:
        # 修改2：按秒重采样
        chunk = chunk.set_index('date').resample(freq).asfreq()
        chunk['up_inside_fuse'] = chunk['up_inside_fuse'].interpolate(method='linear', limit=limit)
        full_df.append(chunk.reset_index())
    
    # 合并并保存结果
    pd.concat(full_df).to_csv(output_path, index=False)
    print(f"插值完成，文件已保存至: {output_path}")

if __name__ == "__main__":
    input_file = 'D:/Python_Project/toolscript/csvfile/up_inside/ETTh1_umsampled.csv'
    output_file = 'D:/Python_Project/toolscript/csvfile/up_inside/ETTh1_unsampled_interpolated.csv'
    # 修改3：调整参数适配秒级数据
    interpolate_and_save(
        input_path=input_file,
        output_path=output_file,
        freq='S',       # 设置为秒级频率
        limit=36000      # 允许最大连续填充1小时（3600秒）
    )