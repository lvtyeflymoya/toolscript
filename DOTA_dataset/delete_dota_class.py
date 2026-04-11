"""
删除 DOTA 格式标注文件中指定类别的脚本

功能：
- 从标注文件夹中批量删除指定类别的标注行
- 保留头部信息（imagesource、gsd）
- 输出到新文件夹，不修改原始文件

DOTA格式每行：x1 y1 x2 y2 x3 y3 x4 y4 category_name difficult
头部可选：imagesource:xxx, gsd:xxx

使用方法：
    python DOTA_dataset/delete_dota_class.py --input path/to/labels --output path/to/output --classes cls1 cls2
"""

import os
import glob
import argparse


def delete_classes(input_dir, output_dir, delete_class_names):
    """
    从 DOTA 标注文件中删除指定类别

    Args:
        input_dir: 输入标注文件夹路径
        output_dir: 输出标注文件夹路径
        delete_class_names: 要删除的类别名称集合
    """
    os.makedirs(output_dir, exist_ok=True)

    total_files = 0
    total_deleted = 0
    total_kept = 0

    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        output_path = os.path.join(output_dir, filename)

        kept_lines = []
        deleted_count = 0

        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()

                # 保留空行
                if not stripped:
                    kept_lines.append('')
                    continue

                # 保留头部信息
                if stripped.startswith('imagesource:') or stripped.startswith('gsd:'):
                    kept_lines.append(stripped)
                    continue

                parts = stripped.split()
                if len(parts) < 9:
                    kept_lines.append(stripped)
                    continue

                # DOTA格式：x1 y1 x2 y2 x3 y3 x4 y4 category difficult
                category = parts[8]
                if category in delete_class_names:
                    deleted_count += 1
                else:
                    kept_lines.append(stripped)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(kept_lines))

        total_files += 1
        total_deleted += deleted_count
        total_kept += len(kept_lines)

        if deleted_count > 0:
            print(f"  {filename}: 删除 {deleted_count} 行，保留 {len(kept_lines)} 行")

    print("-" * 50)
    print(f"处理完成！")
    print(f"  处理文件数：{total_files}")
    print(f"  删除标注总数：{total_deleted}")
    print(f"  保留标注总数：{total_kept}")
    print(f"  输出路径：{output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='删除 DOTA 标注中指定类别')
    parser.add_argument('--input', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\dota\split_output\annfiles",
                        help='输入标注文件夹路径')
    parser.add_argument('--output', '-o', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_lc_tc_d_anno\dota\split_output\annfiles",
                        help='输出标注文件夹路径')
    parser.add_argument('--classes', nargs='+', default=["tiltedConnection"],
                        help='要删除的类别名称（可指定多个）')

    args = parser.parse_args()

    print("=" * 50)
    print("DOTA 标注删除指定类别工具")
    print("=" * 50)
    print(f"输入文件夹：{args.input}")
    print(f"输出文件夹：{args.output}")
    print(f"删除类别：{args.classes}")

    if not os.path.isdir(args.input):
        print(f"错误：输入文件夹不存在：{args.input}")
        exit(1)

    delete_classes(args.input, args.output, set(args.classes))
