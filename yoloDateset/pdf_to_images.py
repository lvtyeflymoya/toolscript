"""
PDF 转 PNG 图片脚本（每页一张）

输入：PDF 文件或目录
输出：PNG 图片（每页一张）

使用方法：
    python pdf_to_images.py --input path/to/file.pdf --output path/to/output --dpi 300
    python pdf_to_images.py -i path/to/pdf_dir -o path/to/output --dpi 600
"""

import argparse
import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


def convert_pdf_to_images(
    pdf_path: str,
    output_dir: Optional[str] = None,
    dpi: int = 300
) -> int:
    """
    将单个 PDF 的每一页渲染为 PNG

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录，默认在 PDF 同目录创建 <stem>_images/
        dpi: 渲染 DPI

    Returns:
        成功导出的页数，失败返回 0
    """
    pdf_path = Path(pdf_path)
    stem = pdf_path.stem

    # 确定输出目录
    if output_dir:
        out_root = Path(output_dir)
    else:
        out_root = pdf_path.parent / f"{stem}"

    # 为该 PDF 创建独立子目录
    out_dir = out_root
    out_dir.mkdir(parents=True, exist_ok=True)

    # 打开 PDF
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"错误：无法打开 PDF {pdf_path} - {e}")
        return 0

    page_count = doc.page_count
    print(f"PDF 页数：{page_count}")

    # 渲染每一页
    exported = 0
    for i in range(page_count):
        page = doc[i]

        # 设置 DPI 矩阵（PDF 默认 72 DPI）
        matrix = fitz.Matrix(dpi / 72, dpi / 72)

        # 渲染页面（alpha=False 避免透明通道）
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        # 输出文件名（4 位前导零）
        out_file = out_dir / f"{stem}_{i + 1:04d}.png"

        # 兼容中文路径写入
        try:
            png_bytes = pix.tobytes("png")
            with open(out_file, 'wb') as f:
                f.write(png_bytes)
            print(f"已导出：{pdf_path.name} 第 {i + 1}/{page_count} 页 -> {out_file}")
            exported += 1
        except Exception as e:
            print(f"错误：无法写入 {out_file} - {e}")

    doc.close()

    if exported > 0:
        print(f"完成：{pdf_path.name} 导出 {exported}/{page_count} 页 -> {out_dir}")
    else:
        print(f"失败：{pdf_path.name} 未导出任何页面")

    return exported


def convert_directory(
    input_dir: str,
    output_dir: Optional[str] = None,
    dpi: int = 300
):
    """
    批量转换目录下所有 PDF

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        dpi: 渲染 DPI
    """
    input_dir = Path(input_dir)
    pdf_files = sorted(input_dir.glob('*.pdf'))

    print(f"输入目录：{input_dir}")
    print(f"输出目录：{output_dir if output_dir else '（各 PDF 同目录）'}")
    print(f"找到 {len(pdf_files)} 个 PDF 文件")

    converted = 0
    failed = 0

    for pdf_file in pdf_files:
        result = convert_pdf_to_images(str(pdf_file), output_dir, dpi)
        if result:
            converted += 1
        else:
            failed += 1

    print(f"\n转换完成：成功 {converted}，失败 {failed}，总计 {len(pdf_files)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDF 转 PNG 图片（每页一张）')
    parser.add_argument('--input', '-i', type=str,
                        default=r"C:\Users\Zhang\Desktop\0616",
                        help='输入 PDF 文件或目录')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出目录，默认在 PDF 同目录创建 <stem>_images/')
    parser.add_argument('--dpi', type=int, default=96,
                        help='渲染 DPI')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        convert_pdf_to_images(str(input_path), args.output, args.dpi)
    elif input_path.is_dir():
        convert_directory(str(input_path), args.output, args.dpi)
    else:
        print(f"错误：{args.input} 不存在")
