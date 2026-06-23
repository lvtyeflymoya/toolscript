"""
图像按比例批量裁剪脚本

输入：图像文件或目录
输出：按指定归一化区域裁剪后的 PNG 图片（前 4 个 BOM 区域和最后 1 个轴测图区域可分别指定输出目录）

使用方法：
    python crop_image_regions.py --input path/to/image.png --bom-dir path/to/bom --drawing-dir path/to/drawing
    python crop_image_regions.py -i path/to/image_dir --bom-dir path/to/bom --drawing-dir path/to/drawing
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


# 裁剪区域列表，格式：(cx, cy, half_w, half_h)，所有值归一化到 [0, 1]
# 来源：AngleSteelRebuild/config/default.json 的 image_load 段
# 前 4 个为 BOM 表区域，最后 1 个为轴测图区域
CROP_REGIONS = [
    (0.1757, 0.2101, 0.1757, 0.2093),  # BOM 1
    (0.1757, 0.5183, 0.1757, 0.0997),  # BOM 2
    (0.1757, 0.7087, 0.1757, 0.0907),  # BOM 3
    (0.1757, 0.8997, 0.1757, 0.0997),  # BOM 4
    (0.6738, 0.4983, 0.3261, 0.4983),  # 轴测图
]

# 支持的图像后缀
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}


def crop_image_to_regions(
    image_path: str,
    bom_dir: Optional[str] = None,
    drawing_dir: Optional[str] = None,
    regions: Tuple[Tuple[float, ...], ...] = CROP_REGIONS
) -> int:
    """
    按归一化区域批量裁剪单张图像

    Args:
        image_path: 输入图像路径
        bom_dir: 前 4 个 BOM 区域的输出目录，默认在图像同目录创建 <stem>_crops/
        drawing_dir: 第 5 个轴测图区域的输出目录，默认使用 bom_dir
        regions: 裁剪区域列表，每个元素是 (cx, cy, half_w, half_h) 归一化值

    Returns:
        成功裁剪的区域数，失败返回 0
    """
    image_path = Path(image_path)
    stem = image_path.stem

    # 确定 BOM 区域输出目录
    if bom_dir:
        bom_out_dir = Path(bom_dir)
    else:
        bom_out_dir = image_path.parent / f"{stem}_crops"
    bom_out_dir.mkdir(parents=True, exist_ok=True)

    # 确定轴测图区域输出目录
    if drawing_dir:
        drawing_out_dir = Path(drawing_dir)
    else:
        drawing_out_dir = bom_out_dir
    drawing_out_dir.mkdir(parents=True, exist_ok=True)

    # 中文路径读取
    image = cv2.imread(str(image_path))
    if image is None:
        image = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        print(f"错误：无法读取图像 {image_path}")
        return 0

    h, w = image.shape[:2]
    print(f"图像尺寸：{w}x{h}")

    exported = 0
    for i, (cx, cy, hw, hh) in enumerate(regions, start=1):
        # 计算裁剪区域（加边界 clamp 保护）
        x1 = max(0, int((cx - hw) * w))
        y1 = max(0, int((cy - hh) * h))
        x2 = min(w, int((cx + hw) * w))
        y2 = min(h, int((cy + hh) * h))

        # 裁剪
        roi = image[y1:y2, x1:x2]

        # 根据区域索引选择输出目录
        # 前 4 个区域（BOM）使用 bom_out_dir，第 5 个区域（轴测图）使用 drawing_out_dir
        if i < len(regions):
            out_dir = bom_out_dir
            region_type = "BOM"
        else:
            out_dir = drawing_out_dir
            region_type = "轴测图"

        # 输出文件名
        out_file = out_dir / f"{stem}_roi{i:01d}.png"

        # 中文路径写入
        ok, buf = cv2.imencode('.png', roi)
        if ok:
            buf.tofile(str(out_file))
            print(f"已裁剪：{image_path.name} 区域 {i}/{len(regions)} ({region_type}) -> {out_file} ({x2-x1}x{y2-y1})")
            exported += 1
        else:
            print(f"错误：无法编码 {out_file}")

    if exported > 0:
        print(f"完成：{image_path.name} 裁剪 {exported}/{len(regions)} 个区域 -> BOM: {bom_out_dir}, 轴测图: {drawing_out_dir}")
    else:
        print(f"失败：{image_path.name} 未裁剪任何区域")

    return exported


def crop_directory(
    input_dir: str,
    bom_dir: Optional[str] = None,
    drawing_dir: Optional[str] = None,
    regions: Tuple[Tuple[float, ...], ...] = CROP_REGIONS
):
    """
    批量裁剪目录下所有图像

    Args:
        input_dir: 输入目录
        bom_dir: BOM 区域输出目录
        drawing_dir: 轴测图区域输出目录
        regions: 裁剪区域列表
    """
    input_dir = Path(input_dir)

    # 收集所有图像文件
    image_files = [f for f in input_dir.glob('*') if f.suffix.lower() in IMAGE_EXTS]
    image_files = sorted(image_files)

    print(f"输入目录：{input_dir}")
    print(f"BOM 输出目录：{bom_dir if bom_dir else '（各图像同目录下的 <stem>_crops/）'}")
    print(f"轴测图输出目录：{drawing_dir if drawing_dir else '（同 BOM 输出目录）'}")
    print(f"找到 {len(image_files)} 个图像文件")

    converted = 0
    failed = 0

    for image_file in image_files:
        result = crop_image_to_regions(str(image_file), bom_dir, drawing_dir, regions)
        if result:
            converted += 1
        else:
            failed += 1

    print(f"\n裁剪完成：成功 {converted}，失败 {failed}，总计 {len(image_files)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='按归一化区域批量裁剪图像（前 4 个 BOM 区域和第 5 个轴测图区域可分别指定输出目录）')
    parser.add_argument('--input', '-i', type=str,
                        default=r"C:\Users\Zhang\Desktop\0615\E10MU402TM",
                        help='输入图像文件或目录')
    parser.add_argument('--bom-dir', '-b', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\graphes\tables",
                        help='前 4 个 BOM 区域的输出目录，默认在图像同目录创建 <stem>_crops/')
    parser.add_argument('--drawing-dir', '-d', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\graphes\axonometric_drawings",
                        help='第 5 个轴测图区域的输出目录，默认使用 --bom-dir')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        crop_image_to_regions(str(input_path), args.bom_dir, args.drawing_dir)
    elif input_path.is_dir():
        crop_directory(str(input_path), args.bom_dir, args.drawing_dir)
    else:
        print(f"错误：{args.input} 不存在")
