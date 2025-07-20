# 画出水位线曲线图
import plotly.graph_objects as go
import pandas as pd
import webbrowser

def create_standalone_plot(df, columns_to_plot=['down_inside_fuse'], shift_column=None, shift_distance=0, date_type='index'):
    # 创建基础图表对象
    fig = go.Figure()
    
    # 采样策略（保持原始数据分辨率）
    ts = df.set_index('date')[columns_to_plot]
    sample_step = max(1, len(ts)//300000)
    sampled_ts = ts.iloc[::sample_step]

    # 颜色循环列表（使用Plotly默认颜色）
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
             '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    # 添加多个轨迹
    for i, column in enumerate(columns_to_plot):
        x_data = sampled_ts.index
        if column == shift_column:
            if date_type == 'index':
                # 平移指定列的 x 轴数据
                x_data = x_data + shift_distance
            elif date_type == 'date':
                # 若为日期类型，使用 timedelta 进行平移
                import pandas as pd
                x_data = x_data + pd.Timedelta(shift_distance, unit='D')  # 假设单位为天

        fig.add_trace(go.Scattergl(
            x=x_data,
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
            title='日期' if date_type == 'date' else '索引',  # 根据 date_type 修改X轴标题
            rangeslider=dict(visible=True),
            type="date" if date_type == 'date' else "linear"  # 根据 date_type 修改 x 轴类型
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
def load_csv_data(csv_path, columns_to_plot=['date', 'down_inside_fuse'], date_type='index'):
    # 合并 dtype 参数
    dtype_dict = {col: 'float32' for col in columns_to_plot if col != 'date'}
    if date_type == 'index':
        dtype_dict['date'] = 'int64'  # 指定 date 列为整数类型
        parse_dates = False
    elif date_type == 'date':
        parse_dates = ['date']
        # 自定义日期解析函数，这里假设日期格式为 'YYYY-MM-DD'
        def date_parser(x):
            return pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S')
    else:
        raise ValueError("date_type 参数必须是 'index' 或 'date'")

    df = pd.read_csv(
        csv_path,
        parse_dates=parse_dates,
        usecols=['date'] + [col for col in columns_to_plot if col != 'date'],
        dtype=dtype_dict,
        date_parser=date_parser if date_type == 'date' else None  # 指定日期解析函数
    )
    return df

# 修改执行部分
if __name__ == "__main__":
    csv_path = "D:/Python_Project/cluster/modified_data.csv"
    # 指定需要绘制的列（可单个或多个）
    columns_to_plot = ['up_inside_fuse', 'modified_water_level']  # ← 在此处修改需要绘制的列
    # columns_to_plot = ['down_inside_fuse']
    # 指定要平移的列和距离
    shift_column = None
    shift_distance = 0  # 平移距离
    # 让用户选择 date 列的数据类型
    date_type = input("请选择 date 列的数据类型 ('index' 或 'date'): ")
    
    try:
        df = load_csv_data(csv_path, columns_to_plot, date_type = date_type)
        # 传递 date_type 到 create_standalone_plot 函数
        html_file = create_standalone_plot(df, columns_to_plot, shift_column, shift_distance, date_type=date_type)
        webbrowser.open(html_file)
    except FileNotFoundError:
        print(f"错误：文件未找到，请检查路径 {csv_path}")
    except MemoryError:
        print("内存不足！建议使用分块读取:")
        print("1. 安装Dask: pip install dask")
        print("2. 用 dd.read_csv() 替代 pd.read_csv()")
    except ValueError as e:
        print(f"错误：{e}")