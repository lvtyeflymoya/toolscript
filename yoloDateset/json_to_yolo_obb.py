"""
将 xanylabeling 的json旋转框标注格式转换为 YOLO-OBB 格式

输入：JSON 文件（shape_type=rotation）
输出：YOLO-OBB txt 文件（cls x1 y1 x2 y2 x3 y3 x4 y4 x5 y5 x6 y6 x7 y7 x8 y8）

python yoloDateset/json_to_yolo_obb.py --input E:/work/drawing_analysis/dataset/obb_all_graphes/annotation/ab_af_c_c_d_labels/x_json --output E:/work/drawing_analysis/dataset/obb_all_graphes/annotation/ab_af_c_c_d_labels/txt
"""

import json
import os
from pathlib import Path


# 类别映射

LABEL2ID = {
    "angelSteelBack": 0,
    "angelSteelFront": 1,
    "clamp": 2,
    "LConnection": 3,
    "TConnection": 4,
    "dimension": 5,
    "angelSteelNumber": 6,
    "clampNumber": 7,
    "endMark": 8
}


def convert_labelme_to_yolo_obb(json_file: str, output_dir: str = None) -> str:
    """
    转换单个 JSON 文件到 YOLO-OBB 格式

    Args:
        json_file: JSON 文件路径
        output_dir: 输出目录，默认为 None（与 JSON 同目录）

    Returns:
        输出的 txt 文件路径
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image_width = data.get('imageWidth', 0)
    image_height = data.get('imageHeight', 0)

    if image_width == 0 or image_height == 0:
        print(f"警告：{json_file} 图像尺寸无效，跳过")
        return None

    # 获取输出文件路径
    json_path = Path(json_file)
    txt_file = json_path.with_suffix('.txt')

    # 如果指定了输出目录，则修改输出路径
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        txt_file = output_path / txt_file.name

    lines = []
    for shape in data.get('shapes', []):
        # 只处理 rotation 类型的标注
        if shape.get('shape_type') != 'rotation':
            continue

        label = shape.get('label')
        if label not in LABEL2ID:
            print(f"警告：未知类别 '{label}'，跳过")
            continue

        class_id = LABEL2ID[label]
        points = shape.get('points', [])

        if len(points) != 4:
            print(f"警告：{json_file} 中 {label} 的标注点不是 4 个，跳过")
            continue

        # 归一化坐标并格式化输出
        # 格式：cls x1 y1 x2 y2 x3 y3 x4 y4
        normalized_points = []
        for px, py in points:
            nx = px / image_width
            ny = py / image_height
            normalized_points.extend([nx, ny])

        # 格式化：保留 6 位小数
        coords_str = ' '.join([f'{v:.6f}' for v in normalized_points])
        lines.append(f'{class_id} {coords_str}')

    # 写入 txt 文件
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"已转换：{json_file} -> {txt_file}")
    return str(txt_file)


def convert_directory(json_dir: str, output_dir: str = None):
    """
    批量转换目录下所有 JSON 文件

    Args:
        json_dir: 包含 JSON 文件的目录
        output_dir: 输出目录，默认为 None（与 JSON 同目录）
    """
    print(f"使用类别映射：{LABEL2ID}")

    json_dir = Path(json_dir)
    json_files = list(json_dir.glob('*.json'))

    print(f"找到 {len(json_files)} 个 JSON 文件")

    converted = 0
    for json_file in json_files:
        result = convert_labelme_to_yolo_obb(str(json_file), output_dir)
        if result:
            converted += 1

    print(f"转换完成：{converted}/{len(json_files)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='labelme 旋转框转 YOLO-OBB 格式')
    parser.add_argument('--input', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\x_json",
                        help='输入的 JSON 文件或目录')
    parser.add_argument('--output', '-o', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\yolo_txt",
                        help='输出目录，默认为 None（与输入 JSON 同目录）')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        convert_labelme_to_yolo_obb(str(input_path), args.output)
    elif input_path.is_dir():
        convert_directory(str(input_path), args.output)
    else:
        print(f"错误：{args.input} 不存在")
