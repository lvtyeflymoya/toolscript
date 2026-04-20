"""
DOTA数据集划分脚本

将DOTA格式的标注数据集划分为训练集、验证集、测试集

使用方法：
    python DOTA_dataset/split_dota_dataset.py --images path/to/images --labels path/to/labels --output path/to/output --train 0.7 --val 0.2 --test 0.1
"""

import os
import shutil
import random
import argparse
from pathlib import Path


def split_dataset(
    image_dir: str,
    label_dir: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    image_ext: str = 'png',
    seed: int = 0
):
    """
    划分DOTA数据集

    Args:
        image_dir: 图片目录
        label_dir: 标签目录（DOTA格式txt文件）
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        image_ext: 图片扩展名
        seed: 随机种子
    """
    # 检查比例之和
    total_ratio = train_ratio + val_ratio + test_ratio
    if abs(total_ratio - 1.0) > 0.001:
        print(f"错误：比例之和应为1.0，当前为 {total_ratio}")
        return

    random.seed(seed)

    image_dir = Path(image_dir)
    label_dir = Path(label_dir)
    output_dir = Path(output_dir)

    # 创建输出目录结构
    for split in ['train', 'val', 'test']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # 获取所有标签文件
    label_files = list(label_dir.glob('*.txt'))
    random.shuffle(label_files)

    total = len(label_files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train_files = label_files[:train_end]
    val_files = label_files[train_end:val_end]
    test_files = label_files[val_end:]

    print(f"数据集总数: {total}")
    print(f"训练集: {len(train_files)} ({len(train_files)/total*100:.1f}%)")
    print(f"验证集: {len(val_files)} ({len(val_files)/total*100:.1f}%)")
    print(f"测试集: {len(test_files)} ({len(test_files)/total*100:.1f}%)")

    def copy_files(file_list, split_name):
        """复制图片和标签文件"""
        for label_file in file_list:
            # 复制标签
            shutil.copy(label_file, output_dir / 'labels' / split_name / label_file.name)

            # 复制对应的图片
            img_name = label_file.stem + f'.{image_ext}'
            img_file = image_dir / img_name

            if img_file.exists():
                shutil.copy(img_file, output_dir / 'images' / split_name / img_name)
            else:
                print(f"警告: 找不到图片 {img_file}")

    print("\n正在复制训练集...")
    copy_files(train_files, 'train')

    print("正在复制验证集...")
    copy_files(val_files, 'val')

    print("正在复制测试集...")
    copy_files(test_files, 'test')

    print(f"\n数据集划分完成！输出目录: {output_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DOTA数据集划分')
    parser.add_argument('--images', '-i', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\all_graphes",
                        help='图片目录')
    parser.add_argument('--labels', '-l', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\dota_txt",
                        help='标签目录（DOTA格式txt文件）')
    parser.add_argument('--output', '-o', type=str, default=r"DOTA_dataset\output\dota",
                        help='输出目录')
    parser.add_argument('--train', type=float, default=0.7,
                        help='训练集比例 (默认: 0.7)')
    parser.add_argument('--val', type=float, default=0.3,
                        help='验证集比例 (默认: 0.2)')
    parser.add_argument('--test', type=float, default=0,
                        help='测试集比例 (默认: 0.1)')
    parser.add_argument('--ext', type=str, default='png',
                        help='图片扩展名 (默认: png)')
    parser.add_argument('--seed', type=int, default=0,
                        help='随机种子 (默认: 0)')

    args = parser.parse_args()

    split_dataset(
        args.images,
        args.labels,
        args.output,
        args.train,
        args.val,
        args.test,
        args.ext,
        args.seed
    )
