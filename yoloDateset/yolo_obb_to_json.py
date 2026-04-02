"""
将 YOLO-OBB 格式转换为 xanylabeling 的 JSON 旋转框标注格式

输入：YOLO-OBB txt 文件（class_id x1 y1 x2 y2 x3 y3 x4 y4）
输出：JSON 文件（shape_type=rotation）

python yoloDateset/yolo_obb_to_json.py --input E:/work/drawing_analysis/dataset/obb_all_graphes/annotation/all_labels副本/ --output yoloDateset/output/json --width 1915 --height 1660
"""

import json
import os
from pathlib import Path


# 类别映射（ID到名称）
ID2LABEL = {
    0:"angelSteelBack",
    1:"angelSteelFront",
    2:"clamp",
    3:"LConnection",
    4:"TConnection",
    5:"tiltedConnection",
    6:"dimension",
    7:"arrowhead",
}


def convert_yolo_obb_to_json(txt_file: str, image_width: int, image_height: int,
                             output_dir: str = None, image_path: str = None) -> str:
    """
    转换单个 YOLO-OBB txt 文件到 JSON 格式

    Args:
        txt_file: YOLO-OBB txt 文件路径
        image_width: 图像宽度
        image_height: 图像高度
        output_dir: 输出目录，默认为 None（与 txt 同目录）
        image_path: 图像路径，默认为 None（自动生成）

    Returns:
        输出的 JSON 文件路径
    """
    if image_width <= 0 or image_height <= 0:
        print(f"错误：图像尺寸无效 (width={image_width}, height={image_height})")
        return None

    # 读取 YOLO-OBB 文件
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 构建 shapes 列表
    shapes = []
    for line_idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) != 9:  # class_id + 8个坐标值
            print(f"警告：{txt_file} 第 {line_idx+1} 行格式错误（应有9个值，实际{len(parts)}个），跳过")
            continue

        try:
            class_id = int(parts[0])
            coords = [float(x) for x in parts[1:]]
        except ValueError as e:
            print(f"警告：{txt_file} 第 {line_idx+1} 行数据解析失败: {e}，跳过")
            continue

        if class_id not in ID2LABEL:
            print(f"警告：{txt_file} 第 {line_idx+1} 行包含未知类别 ID '{class_id}'，跳过")
            continue

        # 将归一化坐标转换为像素坐标
        points = []
        for i in range(0, len(coords), 2):
            px = coords[i] * image_width
            py = coords[i+1] * image_height
            points.append([px, py])

        # 构建 shape 对象
        shape = {
            "label": ID2LABEL[class_id],
            "points": points,
            "group_id": None,
            "shape_type": "rotation",
            "flags": {}
        }
        shapes.append(shape)

    # 获取输出文件路径
    txt_path = Path(txt_file)
    json_file = txt_path.with_suffix('.json')

    # 如果指定了输出目录，则修改输出路径
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        json_file = output_path / json_file.name

    # 如果没有指定图像路径，使用默认路径
    if image_path is None:
        # 使用与 txt 文件同名的图像文件（假设扩展名为 .png）
        image_path = txt_path.with_suffix('.png').name

    # 构建 JSON 数据结构
    json_data = {
        "version": "5.0.1",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path,
        "imageData": None,
        "imageHeight": image_height,
        "imageWidth": image_width
    }

    # 写入 JSON 文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"已转换：{txt_file} -> {json_file} (共 {len(shapes)} 个标注)")
    return str(json_file)


def convert_directory(txt_dir: str, image_width: int, image_height: int,
                     output_dir: str = None):
    """
    批量转换目录下所有 txt 文件

    Args:
        txt_dir: 包含 txt 文件的目录
        image_width: 图像宽度
        image_height: 图像高度
        output_dir: 输出目录，默认为 None（与 txt 同目录）
    """
    print(f"使用类别映射：{ID2LABEL}")

    txt_dir = Path(txt_dir)
    txt_files = list(txt_dir.glob('*.txt'))

    print(f"找到 {len(txt_files)} 个 txt 文件")

    converted = 0
    for txt_file in txt_files:
        result = convert_yolo_obb_to_json(str(txt_file), image_width, image_height, output_dir)
        if result:
            converted += 1

    print(f"转换完成：{converted}/{len(txt_files)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='YOLO-OBB 格式转 labelme 旋转框')
    parser.add_argument('--input', type=str, required=True,
                        help='输入的 txt 文件或目录')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出目录，默认为 None（与输入 txt 同目录）')
    parser.add_argument('--width', '-W', type=int, required=True,
                        help='图像宽度（像素）')
    parser.add_argument('--height', '-H', type=int, required=True,
                        help='图像高度（像素）')
    parser.add_argument('--image-path', type=str, default=None,
                        help='图像路径（仅用于单文件转换，默认使用同名 .png 文件）')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        convert_yolo_obb_to_json(str(input_path), args.width, args.height,
                                args.output, args.image_path)
    elif input_path.is_dir():
        convert_directory(str(input_path), args.width, args.height, args.output)
    else:
        print(f"错误：{args.input} 不存在")
