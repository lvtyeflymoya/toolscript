"""
图片缩放脚本：将图片调整为指定尺寸
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


def resize_image(
    image: np.ndarray,
    new_size: Tuple[int, int],
    keep_aspect: bool = False
) -> np.ndarray:
    """
    调整图像尺寸

    Args:
        image: 输入图像（BGR 格式）
        new_size: 目标尺寸 (width, height)
        keep_aspect: 是否保持宽高比（使用 letterbox 填充）

    Returns:
        调整后的图像
    """
    if keep_aspect:
        # 保持宽高比，使用 letterbox 填充
        h, w = image.shape[:2]
        target_w, target_h = new_size

        # 计算缩放比例
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # 缩放
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # 创建目标尺寸画布，填充白色
        canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 255
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        return canvas
    else:
        # 直接缩放到目标尺寸
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def resize_single_image(
    input_path: str,
    new_size: Tuple[int, int],
    output_path: Optional[str] = None,
    keep_aspect: bool = False
) -> bool:
    """
    调整单张图片尺寸

    Args:
        input_path: 输入图片路径
        new_size: 目标尺寸 (width, height)
        output_path: 输出路径，默认在输入路径同目录添加 _resized 后缀
        keep_aspect: 是否保持宽高比

    Returns:
        成功返回 True，失败返回 False
    """
    input_path = Path(input_path)

    # 默认输出路径
    if output_path is None:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_resized_{new_size[0]}x{new_size[1]}{suffix}"
    else:
        output_path = Path(output_path)

    # 中文路径兼容读取
    img = cv2.imread(str(input_path))
    if img is None:
        img = cv2.imdecode(np.fromfile(str(input_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"错误：无法读取图像 {input_path}")
        return False

    # 缩放
    resized = resize_image(img, new_size, keep_aspect)

    # 中文路径兼容写入
    ok, buf = cv2.imencode(input_path.suffix, resized)
    if ok:
        buf.tofile(str(output_path))
        aspect_info = "（保持宽高比）" if keep_aspect else ""
        print(f"已缩放至 {new_size[0]}x{new_size[1]}{aspect_info}: {input_path.name} -> {output_path}")
        return True
    else:
        print(f"错误：无法写入 {output_path}")
        return False


def resize_directory(
    input_dir: str,
    new_size: Tuple[int, int],
    output_dir: Optional[str] = None,
    keep_aspect: bool = False
) -> None:
    """
    批量调整目录下所有图片尺寸

    Args:
        input_dir: 输入目录
        new_size: 目标尺寸 (width, height)
        output_dir: 输出目录，默认在输入目录下创建 resized 子目录
        keep_aspect: 是否保持宽高比
    """
    input_dir = Path(input_dir)

    # 支持的图像格式
    image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}

    # 收集所有图像文件
    image_files = [f for f in input_dir.glob('*') if f.suffix.lower() in image_exts]
    image_files = sorted(image_files)

    # 确定输出目录
    if output_dir is None:
        suffix = f"_resized_{new_size[0]}x{new_size[1]}"
        output_dir = input_dir.parent / (input_dir.name + suffix)
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"输入目录：{input_dir}")
    print(f"输出目录：{output_dir}")
    print(f"目标尺寸：{new_size[0]}x{new_size[1]}")
    if keep_aspect:
        print(f"保持宽高比：是（使用 letterbox 白色填充）")
    else:
        print(f"保持宽高比：否（直接拉伸）")
    print(f"找到 {len(image_files)} 个图像文件")

    success = 0
    failed = 0

    for img_file in image_files:
        output_path = output_dir / img_file.name
        if resize_single_image(str(img_file), new_size, str(output_path), keep_aspect):
            success += 1
        else:
            failed += 1

    print(f"\n完成：成功 {success}，失败 {failed}，总计 {len(image_files)}")


def parse_size(size_str: str) -> Tuple[int, int]:
    """解析尺寸字符串，支持 'WxH' 或 'W,H' 或 'W H' 格式"""
    size_str = size_str.replace(',', ' ').replace('x', ' ')
    parts = size_str.split()
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"尺寸格式错误，应为 'WxH' 或 'W,H'，如 '1920x1080'")
    w, h = map(int, parts)
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("宽度和高度必须为正整数")
    return (w, h)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='图片缩放工具：将图片调整为指定尺寸'
    )
    parser.add_argument('--input', '-i', type=str,
                        help='输入图片文件或目录')
    parser.add_argument('--size', '-s', type=parse_size, required=True,
                        help='目标尺寸，格式为 WxH 或 W,H，如 1920x1080 或 1920,1080')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出文件或目录，默认在输入路径添加 _resized 后缀')
    parser.add_argument('--keep-aspect', '-k', action='store_true',
                        help='保持宽高比（使用 letterbox 白色填充）')

    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        parser.error("必须指定 --input 参数")

    input_path = Path(args.input)

    if input_path.is_file():
        resize_single_image(str(input_path), args.size, args.output, args.keep_aspect)
    elif input_path.is_dir():
        resize_directory(str(input_path), args.size, args.output, args.keep_aspect)
    else:
        print(f"错误：{args.input} 不存在")
