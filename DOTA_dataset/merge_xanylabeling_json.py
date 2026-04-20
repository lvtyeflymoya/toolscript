"""
合并 xAnyLabeling JSON 标注文件的脚本

功能：
- 将两个 xAnyLabeling JSON 标注文件（或文件夹）中指定类别的标注合并
- 支持两种模式：单文件合并、文件夹批量合并

使用方法：
    # 合并两个文件
    python DOTA_dataset/merge_xanylabeling_json.py --mode file \
        --file_a a.json --file_b b.json --output merged.json \
        --classes_a cls1 cls2 --classes_b cls3 cls4

    # 合并两个文件夹
    python DOTA_dataset/merge_xanylabeling_json.py --mode folder \
        --folder_a dir_a --folder_b dir_b --output_dir output \
        --classes_a cls1 cls2 --classes_b cls3 cls4
"""

import os
import json
import argparse
from pathlib import Path
from typing import List


# ==================== 配置区域 ====================
# 文件A中要提取的类别（空列表表示提取全部）
CLASSES_A = ["angelSteelBack", "angelSteelFront", "clamp", "LConnection", "TConnection", "dimension"]

# 文件B中要提取的类别（空列表表示提取全部）
CLASSES_B = ["angelSteelNumber", "clampNumber", "endMark"]
# ==================== 配置区域结束 ====================


def load_json(path: str) -> dict:
    """加载 JSON 标注文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    """保存 JSON 标注文件"""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def filter_shapes(shapes: list, classes: List[str]) -> list:
    """按类别过滤 shapes，classes 为空则保留全部"""
    if not classes:
        return shapes
    class_set = set(classes)
    return [s for s in shapes if s.get('label') in class_set]


def count_by_class(shapes: list) -> dict:
    """统计每个类别的标注数量"""
    counts = {}
    for s in shapes:
        label = s.get('label', 'unknown')
        counts[label] = counts.get(label, 0) + 1
    return counts


def merge_two_json(data_a: dict, data_b: dict, classes_a: List[str], classes_b: List[str]) -> dict:
    """
    合并两个 xAnyLabeling JSON 数据

    以 data_a 的元数据（imagePath, imageHeight 等）为基础，
    将两个 JSON 中指定类别的 shapes 合并
    """
    shapes_a = filter_shapes(data_a.get('shapes', []), classes_a)
    shapes_b = filter_shapes(data_b.get('shapes', []), classes_b)

    merged = data_a.copy()
    merged['shapes'] = shapes_a + shapes_b
    return merged


def merge_files(file_a: str, file_b: str, output: str, classes_a: List[str], classes_b: List[str]):
    """合并两个 JSON 标注文件"""
    data_a = load_json(file_a)
    data_b = load_json(file_b)

    merged = merge_two_json(data_a, data_b, classes_a, classes_b)
    save_json(merged, output)

    # 统计信息
    shapes_a = filter_shapes(data_a.get('shapes', []), classes_a)
    shapes_b = filter_shapes(data_b.get('shapes', []), classes_b)

    print(f"文件 A 筛选出 {len(shapes_a)} 个标注: {count_by_class(shapes_a)}")
    print(f"文件 B 筛选出 {len(shapes_b)} 个标注: {count_by_class(shapes_b)}")
    print(f"合并后共 {len(merged['shapes'])} 个标注")
    print(f"输出文件: {output}")


def merge_folders(folder_a: str, folder_b: str, output_dir: str, classes_a: List[str], classes_b: List[str]):
    """批量合并两个文件夹中的 JSON 标注文件"""
    os.makedirs(output_dir, exist_ok=True)

    # 获取两个文件夹的 JSON 文件映射
    files_a = {f for f in os.listdir(folder_a) if f.endswith('.json')}
    files_b = {f for f in os.listdir(folder_b) if f.endswith('.json')}

    all_files = files_a | files_b
    merged_count = 0
    only_a_count = 0
    only_b_count = 0

    for filename in sorted(all_files):
        output_path = os.path.join(output_dir, filename)

        if filename in files_a and filename in files_b:
            # 两个文件夹都有，合并
            data_a = load_json(os.path.join(folder_a, filename))
            data_b = load_json(os.path.join(folder_b, filename))
            merged = merge_two_json(data_a, data_b, classes_a, classes_b)
            save_json(merged, output_path)
            merged_count += 1

            count_a = count_by_class(filter_shapes(data_a.get('shapes', []), classes_a))
            count_b = count_by_class(filter_shapes(data_b.get('shapes', []), classes_b))
            print(f"  [合并] {filename}: A={count_a}, B={count_b}")

        elif filename in files_a:
            # 仅在 A 中
            data_a = load_json(os.path.join(folder_a, filename))
            data_a['shapes'] = filter_shapes(data_a.get('shapes', []), classes_a)
            save_json(data_a, output_path)
            only_a_count += 1
            print(f"  [仅A]  {filename}: {count_by_class(data_a['shapes'])}")

        else:
            # 仅在 B 中
            data_b = load_json(os.path.join(folder_b, filename))
            data_b['shapes'] = filter_shapes(data_b.get('shapes', []), classes_b)
            save_json(data_b, output_path)
            only_b_count += 1
            print(f"  [仅B]  {filename}: {count_by_class(data_b['shapes'])}")

    print("-" * 50)
    print(f"处理完成！输出文件总数：{len(all_files)}")
    print(f"  - 两文件夹合并：{merged_count} 个")
    print(f"  - 仅来自文件夹 A：{only_a_count} 个")
    print(f"  - 仅来自文件夹 B：{only_b_count} 个")
    print(f"  - 输出路径：{output_dir}")


def main():
    parser = argparse.ArgumentParser(description='合并 xAnyLabeling JSON 标注文件')
    parser.add_argument('--input_a', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_c_d_labels\x_json",
                        help='输入A：JSON 文件或文件夹路径')
    parser.add_argument('--input_b', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\an_cn_em_labels\x_json",
                        help='输入B：JSON 文件或文件夹路径')
    parser.add_argument('--output', '-o', type=str,
                        default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\x_json",
                        help='输出路径（文件或文件夹）')
    parser.add_argument('--classes_a', nargs='*', default=CLASSES_A,
                        help='从A中提取的类别（留空=全部）')
    parser.add_argument('--classes_b', nargs='*', default=CLASSES_B,
                        help='从B中提取的类别（留空=全部）')

    args = parser.parse_args()

    path_a = Path(args.input_a)
    path_b = Path(args.input_b)

    print("=" * 50)
    print("xAnyLabeling JSON 标注合并工具")
    print("=" * 50)
    print(f"A提取类别：{args.classes_a if args.classes_a else '全部'}")
    print(f"B提取类别：{args.classes_b if args.classes_b else '全部'}")
    print("-" * 50)

    if path_a.is_file() and path_b.is_file():
        # 两个文件：合并为单个文件
        merge_files(str(path_a), str(path_b), args.output, args.classes_a, args.classes_b)
    elif path_a.is_dir() and path_b.is_dir():
        # 两个文件夹：批量合并
        merge_folders(str(path_a), str(path_b), args.output, args.classes_a, args.classes_b)
    else:
        if not path_a.exists():
            print(f"错误：路径A不存在：{args.input_a}")
        elif not path_b.exists():
            print(f"错误：路径B不存在：{args.input_b}")
        else:
            print(f"错误：input_a 和 input_b 必须同为文件或同为文件夹")
            print(f"  input_a: {'文件' if path_a.is_file() else '文件夹' if path_a.is_dir() else '未知'}")
            print(f"  input_b: {'文件' if path_b.is_file() else '文件夹' if path_b.is_dir() else '未知'}")


if __name__ == "__main__":
    main()
