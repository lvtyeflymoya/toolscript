import pandas as pd

def denoise_column(csv_path, column_name, method='savgol', output_path=None, **params):
    """对指定列进行去噪处理并保存结果"""
    df = pd.read_csv(csv_path)
    
    if column_name not in df.columns:
        raise ValueError(f"列 '{column_name}' 不存在于文件中")
    
    # 新增适用于水位数据的去噪方法
    if method == 'savgol':
        # Savitzky-Golay 滤波器 (适合保留趋势的平滑)
        from scipy.signal import savgol_filter
        window_length = params.get('window_length', 15)  # 滑动窗口长度（奇数）
        polyorder = params.get('polyorder', 2)           # 多项式阶数
        df[column_name] = savgol_filter(df[column_name], 
                                      window_length, 
                                      polyorder)
        filtered = df
        
    elif method == 'moving_avg':
        # 移动平均法
        window_size = params.get('window_size', 5)
        df[column_name] = df[column_name].rolling(
            window=window_size, 
            min_periods=1, 
            center=True
        ).mean()
        filtered = df
        
   
    # 确保数据在物理范围内（0-7米）
    filtered[column_name] = filtered[column_name].clip(lower=0, upper=7)
    
    if output_path is None:
        output_path = csv_path.replace(".csv", f"_denoised_{method}.csv")
    
    filtered.to_csv(output_path, index=False)
    print(f"去噪完成，保存至：{output_path}")
    return filtered
# 使用示例（水位数据推荐参数）：
denoise_column('D:/Python_Project/cluster/upoutside_unsamped/up_outside_vision.csv', 
               'up_outside_vision', method='savgol', window_length=21, polyorder=2)
# denoise_column('data.csv', 'water_level', method='moving_avg', window_size=7)
