# 画出水位线曲线图
import plotly.graph_objects as go
import pandas as pd
import webbrowser

def create_standalone_plot(df):
    # 创建基础图表对象
    fig = go.Figure()
    
    # 采样策略（保持原始数据分辨率）
    ts = df.set_index('date')['down_inside_fuse']
    sample_step = max(1, len(ts)//100000)  # 控制约10万数据点
    sampled_ts = ts.iloc[::sample_step]
    
    # 添加轨迹（使用WebGL加速）
    fig.add_trace(go.Scattergl(
        x=sampled_ts.index,
        y=sampled_ts.values,
        mode='lines',
        name='上游外部水位',  # 新增轨迹名称作为表格标题
        line=dict(width=0.8, color='#2c7bb6')
    ))

    # 设置交互组件
    fig.update_layout(
        title=dict(
            text='上游外部水位',  # 修改主标题
            x=0.5,  # 标题居中
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
        height=800
    )
    
    # 保存为交互式HTML
    html_path = 'interactive_plot.html'
    fig.write_html(html_path, auto_open=False)
    return html_path

# 新增数据读取函数
def load_csv_data(csv_path):
    # 优化内存使用的读取方式
    df = pd.read_csv(
        csv_path,
        parse_dates=['date'],          # 解析日期列
        usecols=['date', 'down_inside_fuse'],  # 仅读取所需列
        dtype={'down_inside_fuse': 'float32'}  # 使用较小数据类型
    )
    return df

# 修改最后执行部分
if __name__ == "__main__":
    csv_path = 'D:/Python_Project/toolscript/1111.csv'  # ← 替换为实际CSV路径
    try:
        df = load_csv_data(csv_path)
        html_file = create_standalone_plot(df)
        webbrowser.open(html_file)
    except FileNotFoundError:
        print(f"错误：文件未找到，请检查路径 {csv_path}")
    except MemoryError:
        print("内存不足！建议使用分块读取:")
        print("1. 安装Dask: pip install dask")
        print("2. 用 dd.read_csv() 替代 pd.read_csv()")