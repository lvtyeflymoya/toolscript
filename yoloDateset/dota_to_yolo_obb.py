"""
DOTA格式 -> YOLO-OBB格式 转换脚本

输入：DOTA格式标注文件（绝对坐标 + 类别名称）
输出：YOLO-OBB格式标注文件（归一化坐标 + 类别ID）

DOTA格式每行：  x1 y1 x2 y2 x3 y3 x4 y4 category_name difficult
YOLO-OBB每行：  class_id nx1 ny1 nx2 ny2 nx3 ny3 nx4 ny4

使用方法：
    python dota_to_yolo_obb.py --input path/to/dota/labels --images path/to/images --output path/to/yolo/labels
    python dota_to_yolo_obb.py --input path/to/label.txt --images path/to/image.png --output path/to/output_dir
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path
from typing import Optional


# 类别映射（与 yoloDateset/json_to_yolo_obb.py 保持一致）
LABEL2ID = {
    "angelSteelBack": 0,
    "angelSteelFront": 1,
    "clamp": 2,
    "LConnection": 3,
    "TConnection": 4,
    "tiltedConnection": 5,
    "dimension": 6,
    "arrowhead": 7
}

# 支持的图像后缀
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}


def get_image_size(image_path: str) -> Optional[tuple]:
    """
    读取图像尺寸，兼容中文路径

    Returns:
        (width, height) 或 None
    """
    img = cv2.imread(image_path)
    if img is None:
        # 尝试解决中文路径问题
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return None
    h, w = img.shape[:2]
    return w, h


def find_image(txt_path: str, image_dir: str) -> Optional[str]:
    """
    根据txt文件名在图像目录中查找对应的图像文件

    Args:
        txt_path: 标注文件路径
        image_dir: 图像目录

    Returns:
        图像文件路径，找不到返回None
    """
    stem = Path(txt_path).stem
    for ext in IMAGE_EXTS:
        image_path = os.path.join(image_dir, stem + ext)
        if os.path.exists(image_path):
            return image_path
    return None


def convert_dota_to_yolo(
    txt_file: str,
    image_path: str,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    转换单个DOTA标注文件到YOLO-OBB格式

    Args:
        txt_file: DOTA格式标注文件路径
        image_path: 对应图像文件路径
        output_dir: 输出目录，默认与标注文件同目录

    Returns:
        输出的txt文件路径，失败返回None
    """
    # 获取图像尺寸
    size = get_image_size(image_path)
    if size is None:
        print(f"错误：无法读取图像 {image_path}")
        return None
    img_w, img_h = size

    # 读取DOTA标注
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    yolo_lines = []
    skipped = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过DOTA头部信息
        if line.startswith('imagesource:') or line.startswith('gsd:'):
            continue

        parts = line.split()
        if len(parts) < 9:
            skipped += 1
            continue

        # DOTA格式：x1 y1 x2 y2 x3 y3 x4 y4 category_name [difficult]
        coords = [float(x) for x in parts[:8]]
        category = parts[8]

        # 类别映射
        if category not in LABEL2ID:
            print(f"警告：未知类别 '{category}'，跳过")
            skipped += 1
            continue

        class_id = LABEL2ID[category]

        # 归一化坐标
        normalized = []
        for i in range(0, 8, 2):
            nx = coords[i] / img_w
            ny = coords[i + 1] / img_h
            normalized.extend([nx, ny])

        coords_str = ' '.join([f'{v:.6f}' for v in normalized])
        yolo_lines.append(f'{class_id} {coords_str}')

    if skipped > 0:
        print(f"警告：{txt_file} 跳过了 {skipped} 行")

    # 确定输出路径
    txt_path = Path(txt_file)
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / (txt_path.stem + '.txt')
    else:
        out_file = txt_path.with_suffix('.txt')

    # 写入YOLO格式
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(yolo_lines))

    print(f"已转换：{txt_file} -> {out_file} ({len(yolo_lines)} 个标注)")
    return str(out_file)


def convert_directory(
    label_dir: str,
    image_dir: str,
    output_dir: Optional[str] = None
):
    """
    批量转换目录下所有DOTA标注文件

    Args:
        label_dir: DOTA标注文件目录
        image_dir: 对应图像目录
        output_dir: 输出目录
    """
    label_dir = Path(label_dir)
    txt_files = sorted(label_dir.glob('*.txt'))

    print(f"标注目录：{label_dir}")
    print(f"图像目录：{image_dir}")
    print(f"找到 {len(txt_files)} 个标注文件")
    print(f"使用类别映射：{LABEL2ID}")

    converted = 0
    failed = 0

    for txt_file in txt_files:
        # 查找对应图像
        image_path = find_image(str(txt_file), image_dir)
        if image_path is None:
            print(f"跳过：找不到 {txt_file.stem} 对应的图像文件")
            failed += 1
            continue

        result = convert_dota_to_yolo(str(txt_file), image_path, output_dir)
        if result:
            converted += 1
        else:
            failed += 1

    print(f"\n转换完成：成功 {converted}，失败 {failed}，总计 {len(txt_files)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DOTA格式转YOLO-OBB格式')
    parser.add_argument('--input', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\dota\labels\val",
                        help='DOTA标注文件或目录')
    parser.add_argument('--images', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\dota\images\val",
                        help='对应的图像目录')
    parser.add_argument('--output', '-o', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\yolo\labels\val",
                        help='输出目录，默认与输入标注同目录')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        # 单文件模式：--images 可以是图像文件或目录
        images_path = Path(args.images)
        if images_path.is_file():
            image_path = str(images_path)
        else:
            image_path = find_image(str(input_path), args.images)
            if image_path is None:
                print(f"错误：找不到 {input_path.stem} 对应的图像文件")
                exit(1)

        convert_dota_to_yolo(str(input_path), image_path, args.output)

    elif input_path.is_dir():
        convert_directory(str(input_path), args.images, args.output)
    else:
        print(f"错误：{args.input} 不存在")
