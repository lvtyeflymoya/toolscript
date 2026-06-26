"""
图片旋转脚本：按指定角度旋转图像，自动扩展边界保持完整显示
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
from typing import Optional


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    旋转图像（顺时针），自动扩展边界保持完整显示

    Args:
        image: 输入图像（BGR 格式）
        angle: 旋转角度（度，正数为顺时针）

    Returns:
        旋转后的图像
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # 获取旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算新边界
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # 调整旋转矩阵的平移部分，使图像居中
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # 执行旋转，使用白色填充边界
    rotated = cv2.warpAffine(image, M, (new_w, new_h),
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(255, 255, 255))
    return rotated


def rotate_single_image(
    input_path: str,
    angle: float,
    output_path: Optional[str] = None
) -> bool:
    """
    旋转单张图片

    Args:
        input_path: 输入图片路径
        angle: 旋转角度（度，正数为顺时针）
        output_path: 输出路径，默认在输入路径同目录添加后缀 _rotated

    Returns:
        成功返回 True，失败返回 False
    """
    input_path = Path(input_path)

    # 默认输出路径
    if output_path is None:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_rotated{suffix}"
    else:
        output_path = Path(output_path)

    # 中文路径兼容读取
    img = cv2.imread(str(input_path))
    if img is None:
        img = cv2.imdecode(np.fromfile(str(input_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"错误：无法读取图像 {input_path}")
        return False

    # 旋转
    rotated = rotate_image(img, angle)

    # 中文路径兼容写入
    ok, buf = cv2.imencode(input_path.suffix, rotated)
    if ok:
        buf.tofile(str(output_path))
        print(f"已旋转 {angle} 度: {input_path.name} -> {output_path}")
        return True
    else:
        print(f"错误：无法写入 {output_path}")
        return False


def rotate_directory(
    input_dir: str,
    angle: float,
    output_dir: Optional[str] = None
) -> None:
    """
    批量旋转目录下所有图片

    Args:
        input_dir: 输入目录
        angle: 旋转角度（度）
        output_dir: 输出目录，默认在输入目录下创建 rotated 子目录
    """
    input_dir = Path(input_dir)

    # 支持的图像格式
    image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}

    # 收集所有图像文件
    image_files = [f for f in input_dir.glob('*') if f.suffix.lower() in image_exts]
    image_files = sorted(image_files)

    # 确定输出目录
    if output_dir is None:
        output_dir = input_dir / "rotated"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"输入目录：{input_dir}")
    print(f"输出目录：{output_dir}")
    print(f"旋转角度：{angle} 度（顺时针）")
    print(f"找到 {len(image_files)} 个图像文件")

    success = 0
    failed = 0

    for img_file in image_files:
        output_path = output_dir / img_file.name
        if rotate_single_image(str(img_file), angle, str(output_path)):
            success += 1
        else:
            failed += 1

    print(f"\n完成：成功 {success}，失败 {failed}，总计 {len(image_files)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='图片旋转工具：按指定角度旋转图像，自动扩展边界保持完整显示'
    )
    parser.add_argument('--input', '-i', type=str,
                        help='输入图片文件或目录')
    parser.add_argument('--angle', '-a', type=float, required=True,
                        help='旋转角度（度，正数为顺时针）')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出文件或目录，默认在输入路径添加 _rotated 后缀或创建 rotated 子目录')

    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        parser.error("必须指定 --input 参数")

    input_path = Path(args.input)

    if input_path.is_file():
        rotate_single_image(str(input_path), args.angle, args.output)
    elif input_path.is_dir():
        rotate_directory(str(input_path), args.angle, args.output)
    else:
        print(f"错误：{args.input} 不存在")