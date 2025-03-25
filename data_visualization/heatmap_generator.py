# 生成水位线数据热图
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

def generate_heatmap(df):
    # 创建画布
    plt.figure(figsize=(20, 10))
    
    # 数据准备
    dates = df['date'].astype(np.int64) // 10**9  # 转换为Unix时间戳
    values = df['down_inside_fuse']
    
    # 分箱设置
    time_bins = 500  # 时间轴分箱数
    value_bins = 100  # 数值轴分箱数
    
    # 生成热图数据（可选两种模式）
    # 模式1：密度热图
    heatmap, xedges, yedges = np.histogram2d(
        dates, values, bins=[time_bins, value_bins], density=True)
    
    # 模式2：数值热图（显示平均水位）
    # heatmap, xedges, yedges = np.histogram2d(
    #     dates, values, bins=[time_bins, value_bins], weights=values)
    
    # 转换为对数刻度增强对比度
    log_heatmap = np.log1p(heatmap.T)
    
    # 创建时间刻度标签
    date_ticks = pd.to_datetime(xedges[::50] * 1e9)  # 每50个bin显示一个标签
    
    # 绘制热图
    plt.imshow(log_heatmap, aspect='auto', cmap='viridis',
              extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
    
    # 时间轴格式化
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(xedges[::50], date_ticks, rotation=45)
    
    # 图表元素
    plt.colorbar(label='数据密度（对数刻度）')
    plt.title('时间-水位热力图')
    plt.xlabel('时间')
    plt.ylabel('水位值')
    plt.tight_layout()
    
    # 保存输出
    plt.savefig('heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

# 使用示例
if __name__ == "__main__":
    df = pd.read_csv('D:/Python_Project/toolscript/down_inside_fuse_all.csv',
                    parse_dates=['date'])
    generate_heatmap(df)
