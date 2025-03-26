# 画出水位线曲线图
import plotly.graph_objects as go
import pandas as pd
import webbrowser

def create_standalone_plot(df, columns_to_plot=['down_inside_fuse']):
    # 创建基础图表对象
    fig = go.Figure()
    
    # 采样策略（保持原始数据分辨率）
    ts = df.set_index('date')[columns_to_plot]
    sample_step = max(1, len(ts)//100000)
    sampled_ts = ts.iloc[::sample_step]

    # 颜色循环列表（使用Plotly默认颜色）
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
             '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    # 添加多个轨迹
    for i, column in enumerate(columns_to_plot):
        fig.add_trace(go.Scattergl(
            x=sampled_ts.index,
            y=sampled_ts[column],
            mode='lines',
            name=column,  # 使用列名作为图例名称
            line=dict(width=0.8, color=colors[i % len(colors)])
        ))

    # 更新布局设置
    fig.update_layout(
        title=dict(
            text='多参数水位监测' if len(columns_to_plot)>1 else '单参数水位监测',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='日期',  # 新增X轴标题
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(
            title='水位值 (米)'  # 新增Y轴标题
        ),
        height=800,  # 在此处添加缺失的逗号
        showlegend=True  # 显示图例
    )
    
    # 保存为交互式HTML
    html_path = 'interactive_plot.html'
    fig.write_html(html_path, auto_open=False)
    return html_path

# 修改数据读取函数
def load_csv_data(csv_path, columns_to_plot=['date', 'down_inside_fuse']):
    df = pd.read_csv(
        csv_path,
        parse_dates=['date'],
        usecols=['date'] + [col for col in columns_to_plot if col != 'date'],
        dtype={col: 'float32' for col in columns_to_plot if col != 'date'}
    )
    return df

# 修改执行部分
if __name__ == "__main__":
    csv_path = 'D:/Python_Project/tsai/trainResult/experiment16/test/full_predictions.csv'
    # 指定需要绘制的列（可单个或多个）
    columns_to_plot = ['true', 'pred']  # ← 在此处修改需要绘制的列
    
    try:
        df = load_csv_data(csv_path, columns_to_plot)
        html_file = create_standalone_plot(df, columns_to_plot)
        webbrowser.open(html_file)
    except FileNotFoundError:
        print(f"错误：文件未找到，请检查路径 {csv_path}")
    except MemoryError:
        print("内存不足！建议使用分块读取:")
        print("1. 安装Dask: pip install dask")
        print("2. 用 dd.read_csv() 替代 pd.read_csv()")