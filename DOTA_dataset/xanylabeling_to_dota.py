"""
xanylabeling JSON -> DOTA格式转换脚本

输入：xanylabeling标注的JSON文件（shape_type=rotation）
输出：DOTA格式txt文件

DOTA格式每行：x1 y1 x2 y2 x3 y3 x4 y4 category_name difficult

使用方法：
    python DOTA_dataset/xanylabeling_to_dota.py --input path/to/json --output path/to/output
    python DOTA_dataset/xanylabeling_to_dota.py --input path/to/json_dir --output path/to/output_dir
"""

import json
import os
from pathlib import Path
from typing import Optional


def convert_json_to_dota(
    json_file: str,
    output_dir: Optional[str] = None,
    imagesource: Optional[str] = None,
    gsd: Optional[str] = None
) -> Optional[str]:
    """
    转换单个JSON文件到DOTA格式

    Args:
        json_file: 输入JSON文件路径
        output_dir: 输出目录，默认与JSON同目录
        imagesource: 图像来源（可选）
        gsd: 地面采样距离（可选）

    Returns:
        输出的txt文件路径，失败返回None
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 获取输出文件路径
    json_path = Path(json_file)
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        txt_file = output_path / (json_path.stem + '.txt')
    else:
        txt_file = json_path.with_suffix('.txt')

    lines = []

    # 添加头部信息（可选）
    if imagesource:
        lines.append(f'imagesource:{imagesource}')
    if gsd:
        lines.append(f'gsd:{gsd}')

    # 处理每个shape
    for shape in data.get('shapes', []):
        # 只处理rotation类型的标注
        if shape.get('shape_type') != 'rotation':
            continue

        label = shape.get('label', '')
        points = shape.get('points', [])

        if len(points) != 4:
            print(f"警告：{json_file} 中 {label} 的标注点不是4个，跳过")
            continue

        # 获取difficult标记
        difficult = 1 if shape.get('difficult', False) else 0

        # 格式化坐标：x1 y1 x2 y2 x3 y3 x4 y4（取整）
        coords = []
        for px, py in points:
            coords.extend([int(px), int(py)])

        coords_str = ' '.join([str(c) for c in coords])
        lines.append(f'{coords_str} {label} {difficult}')

    # 写入txt文件
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"已转换：{json_file} -> {txt_file}")
    return str(txt_file)


def convert_directory(
    json_dir: str,
    output_dir: Optional[str] = None,
    imagesource: Optional[str] = None,
    gsd: Optional[str] = None
):
    """
    批量转换目录下所有JSON文件

    Args:
        json_dir: 包含JSON文件的目录
        output_dir: 输出目录
        imagesource: 图像来源（可选）
        gsd: 地面采样距离（可选）
    """
    json_dir = Path(json_dir)
    json_files = list(json_dir.glob('*.json'))

    print(f"找到 {len(json_files)} 个JSON文件")

    converted = 0
    for json_file in json_files:
        result = convert_json_to_dota(
            str(json_file),
            output_dir,
            imagesource,
            gsd
        )
        if result:
            converted += 1

    print(f"转换完成：{converted}/{len(json_files)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='xanylabeling JSON转DOTA格式')
    parser.add_argument('--input', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\x_json",
                        help='输入的JSON文件或目录')
    parser.add_argument('--output', '-o', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\dota_txt",
                        help='输出目录，默认与输入JSON同目录')
    parser.add_argument('--imagesource', type=str, default="drawings",
                        help='图像来源（可选）')
    parser.add_argument('--gsd', type=str, default=0.15,
                        help='地面采样距离（可选）')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        convert_json_to_dota(
            str(input_path),
            args.output,
            args.imagesource,
            args.gsd
        )
    elif input_path.is_dir():
        convert_directory(
            str(input_path),
            args.output,
            args.imagesource,
            args.gsd
        )
    else:
        print(f"错误：{args.input} 不存在")
