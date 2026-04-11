"""
删除 YOLO-OBB 标注文件中指定类别的脚本

功能：
- 从标注文件夹中批量删除指定类别的标注行
- 自动重映射剩余类别的 ID，使其保持连续
- 输出到新文件夹，不修改原始文件

YOLO-OBB 格式：
class_id x1 y1 x2 y2 x3 y3 x4 y4

配置：
在脚本底部的 if __name__ == "__main__" 块中修改参数
"""

import os
import glob

from configs import CLASSES


def delete_classes(input_dir, output_dir, classes, delete_class_names):
    """
    从 YOLO-OBB 标注文件中删除指定类别并重映射剩余类别 ID

    Args:
        input_dir: 输入标注文件夹路径
        output_dir: 输出标注文件夹路径
        classes: 完整的类别名称列表（索引即为 class_id）
        delete_class_names: 要删除的类别名称列表
    """
    # 找出要删除的 class_id 集合
    delete_class_ids = set()
    for name in delete_class_names:
        if name in classes:
            delete_class_ids.add(classes.index(name))
        else:
            print(f"警告：类别 '{name}' 不在类别列表中，跳过")

    if not delete_class_ids:
        print("没有找到要删除的类别，退出")
        return

    # 构建 class_id 重映射表（删除后的 id 映射到新 id）
    # 例如：删除 class 1，则 {0:0, 2:1, 3:2}
    remap = {}
    new_id = 0
    new_classes = []
    for old_id, name in enumerate(classes):
        if old_id not in delete_class_ids:
            remap[old_id] = new_id
            new_classes.append(name)
            new_id += 1

    print(f"原始类别列表：{classes} (共 {len(classes)} 类)")
    print(f"要删除的类别：{[classes[i] for i in sorted(delete_class_ids)]}")
    print(f"删除后类别列表：{new_classes} (共 {len(new_classes)} 类)")
    print(f"类别 ID 重映射：{remap}")
    print("-" * 50)

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
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) < 9:
                    # 行格式不对，保留原样
                    kept_lines.append(line)
                    continue

                class_id = int(parts[0])
                if class_id in delete_class_ids:
                    deleted_count += 1
                else:
                    # 重映射 class_id
                    new_class_id = remap.get(class_id, class_id)
                    parts[0] = str(new_class_id)
                    kept_lines.append(' '.join(parts))

        with open(output_path, 'w', encoding='utf-8') as f:
            for line in kept_lines:
                f.write(line + '\n')

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

    # 输出新的类别列表，方便复制到配置文件
    print("\n删除后的类别列表（可用于 dataset.yaml）：")
    print("names:")
    for i, cls in enumerate(new_classes):
        print(f"  {i}: {cls}")


def main():
    print("=" * 50)
    print("YOLO-OBB 标注删除指定类别工具")
    print("=" * 50)

    if not os.path.isdir(INPUT_DIR):
        print(f"错误：输入文件夹不存在：{INPUT_DIR}")
        return

    delete_classes(INPUT_DIR, OUTPUT_DIR, CLASSES, DELETE_CLASSES)


# ==================== 配置区域 ====================
# CLASSES 已从 configs.py 导入

# 要删除的类别名称
DELETE_CLASSES = ["tiltedConnection"]

# 输入标注文件夹路径
INPUT_DIR = r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\yolo\labels\test"

# 输出标注文件夹路径
OUTPUT_DIR = r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_lc_tc_d_anno\yolo\test"
# ==================== 配置区域结束 ====================


if __name__ == "__main__":
    main()
