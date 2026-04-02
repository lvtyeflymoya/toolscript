"""
合并两个 YOLO-OBB 标注文件夹的脚本

功能：
- 将两个文件夹中的 YOLO-OBB label 文件合并到一个输出文件夹
- 自动合并标签列表，并重新映射第二个文件夹的类别 ID
- 支持文件名相同的 label 文件内容合并

YOLO-OBB 格式：
class_id x1 y1 x2 y2 x3 y3 x4 y4

标签列表配置：
在脚本底部的 if __name__ == "__main__" 块中修改
"""

import os
from typing import Dict, List


# ==================== 配置区域 ====================
# 文件夹 A 的标签列表
CLASSES_A = ["angelSteelBack", "angelSteelFront", "clamp", "LConnection", "TConnection", "tiltedConnection", "dimension"]

# 文件夹 B 的标签列表
CLASSES_B = ["arrowhead"]

# 合并后的标签列表（必须等于 CLASSES_A + CLASSES_B）
MERGED_CLASSES = ["angelSteelBack", "angelSteelFront", "clamp", "LConnection", "TConnection", 
                  "tiltedConnection", "dimension", "arrowhead"]

# 文件夹 A 路径（包含第一批 label 文件）
FOLDER_A = r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_c_d_labels\txt"

# 文件夹 B 路径（包含第二批 label 文件）
FOLDER_B = r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\arrowhead_labels\yolo_txt"

# 输出文件夹路径（合并后的 label 文件）
OUTPUT_DIR = r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_c_d_a_labels"
# ==================== 配置区域结束 ====================


def parse_label_file(label_path: str) -> List[str]:
    """读取 label 文件，返回所有非空行"""
    if not os.path.exists(label_path):
        return []

    with open(label_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines


def write_label_file(label_path: str, lines: List[str]):
    """将标注行写入 label 文件"""
    os.makedirs(os.path.dirname(label_path), exist_ok=True)
    with open(label_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def remap_class_id(line: str, offset: int) -> str:
    """将 label 行的类别 ID 重新映射（加上偏移量）"""
    parts = line.split()
    if len(parts) < 9:
        return line

    class_id = int(parts[0])
    new_class_id = class_id + offset
    parts[0] = str(new_class_id)
    return ' '.join(parts)


def get_label_files(label_dir: str) -> Dict[str, str]:
    """获取目录下所有 label 文件，返回 {文件名：完整路径} 的映射"""
    label_files = {}
    if not os.path.exists(label_dir):
        return label_files

    for filename in os.listdir(label_dir):
        if filename.endswith('.txt'):
            label_files[filename] = os.path.join(label_dir, filename)

    return label_files


def merge_labels(
    folder_a: str,
    folder_b: str,
    output_dir: str,
    classes_a: List[str],
    classes_b: List[str],
    merged_classes: List[str]
) -> None:
    """
    合并两个文件夹的 YOLO-OBB label 文件

    Args:
        folder_a: 第一个 label 文件夹路径
        folder_b: 第二个 label 文件夹路径
        output_dir: 输出文件夹路径
        classes_a: 第一个文件夹的类别列表
        classes_b: 第二个文件夹的类别列表
        merged_classes: 合并后的类别列表
    """
    # 计算类别 ID 偏移量（folder_b 的类别 ID 需要加上这个值）
    class_offset = len(classes_a)

    # 验证合并后的类别列表是否正确
    expected_merged = classes_a + classes_b
    if merged_classes != expected_merged:
        print(f"警告：MERGED_CLASSES 与 CLASSES_A + CLASSES_B 不一致！")
        print(f"  期望：{expected_merged}")
        print(f"  实际：{merged_classes}")
        print(f"将使用 CLASSES_A + CLASSES_B 的结果：{expected_merged}")
        merged_classes = expected_merged

    print(f"类别列表 A: {classes_a} (共 {len(classes_a)} 类)")
    print(f"类别列表 B: {classes_b} (共 {len(classes_b)} 类)")
    print(f"合并后类别列表：{merged_classes} (共 {len(merged_classes)} 类)")
    print(f"类别 ID 偏移量：{class_offset}")
    print("-" * 50)

    # 获取两个文件夹的 label 文件
    files_a = get_label_files(folder_a)
    files_b = get_label_files(folder_b)

    print(f"文件夹 A 中有 {len(files_a)} 个 label 文件")
    print(f"文件夹 B 中有 {len(files_b)} 个 label 文件")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 用于统计
    merged_count = 0  # 合并的文件数
    only_a_count = 0  # 只在 A 中的文件数
    only_b_count = 0  # 只在 B 中的文件数

    all_filenames = set(files_a.keys()) | set(files_b.keys())

    for filename in all_filenames:
        output_path = os.path.join(output_dir, filename)

        # 读取两个文件夹的内容
        lines_a = parse_label_file(files_a.get(filename, ''))
        lines_b = parse_label_file(files_b.get(filename, ''))

        # 对 folder_b 的内容进行类别 ID 重新映射
        lines_b_remap = [remap_class_id(line, class_offset) for line in lines_b]

        # 合并内容（保留所有标注，包括可能的重复）
        merged_lines = lines_a + lines_b_remap

        # 写入输出文件
        write_label_file(output_path, merged_lines)

        # 统计
        if lines_a and lines_b:
            merged_count += 1
        elif lines_a:
            only_a_count += 1
        elif lines_b:
            only_b_count += 1

    print("-" * 50)
    print(f"输出文件总数：{len(all_filenames)}")
    print(f"  - 合并两个文件夹内容：{merged_count} 个文件")
    print(f"  - 仅来自文件夹 A: {only_a_count} 个文件")
    print(f"  - 仅来自文件夹 B: {only_b_count} 个文件")
    print(f"合并后的 label 文件已保存至：{output_dir}")


def main():
    print("=" * 50)
    print("YOLO-OBB 标签文件合并工具")
    print("=" * 50)

    # 验证输入文件夹是否存在
    if not os.path.isdir(FOLDER_A):
        print(f"错误：文件夹 A 不存在：{FOLDER_A}")
        return
    if not os.path.isdir(FOLDER_B):
        print(f"错误：文件夹 B 不存在：{FOLDER_B}")
        return

    # 执行合并
    merge_labels(
        FOLDER_A,
        FOLDER_B,
        OUTPUT_DIR,
        CLASSES_A,
        CLASSES_B,
        MERGED_CLASSES
    )

    # 输出合并后的类别列表，方便用户复制到配置文件
    print("\n" + "=" * 50)
    print("合并后的类别列表（可用于 dataset.yaml 配置）：")
    print("names:")
    for i, cls in enumerate(MERGED_CLASSES):
        print(f"  {i}: {cls}")


if __name__ == "__main__":
    main()
