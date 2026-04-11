"""
验证DOTA格式标注是否正确

读取图片和DOTA格式的标签文件，绘制旋转框并显示

DOTA格式每行：x1 y1 x2 y2 x3 y3 x4 y4 category_name difficult
头部可选：imagesource:xxx, gsd:xxx

使用方法：
    python DOTA_dataset/verify_dota_obb.py --image path/to/image.png --label path/to/label.txt
"""

import cv2
import numpy as np
import os
import argparse


def draw_dota_obb(image_path: str, label_path: str, output_path: str = None):
    """
    读取图片和DOTA格式的标签文件，绘制旋转框并显示

    Args:
        image_path: 图片文件路径
        label_path: DOTA格式标签文件路径
        output_path: 输出图片路径（可选）
    """
    if not os.path.exists(image_path):
        print(f"找不到图片文件: {image_path}")
        return
    if not os.path.exists(label_path):
        print(f"找不到标签文件: {label_path}")
        return

    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        # 尝试解决中文路径问题
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            print("图片读取失败")
            return

    h, w = img.shape[:2]

    # 预设颜色 (BGR格式)
    colors = [
        (0, 255, 0),    # 绿色
        (0, 0, 255),    # 红色
        (255, 0, 0),    # 蓝色
        (255, 255, 0),  # 青色
        (255, 0, 255),  # 紫色
        (0, 255, 255),  # 黄色
        (128, 0, 255),  # 橙色
        (255, 128, 0),  # 天蓝
    ]

    # 读取标签文件
    with open(label_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    color_map = {}
    color_idx = 0
    obj_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过头部信息
        if line.startswith('imagesource:') or line.startswith('gsd:'):
            continue

        parts = line.split()
        if len(parts) < 9:
            continue

        # DOTA格式：x1 y1 x2 y2 x3 y3 x4 y4 category difficult
        coords = [float(x) for x in parts[:8]]
        category = parts[8]
        difficult = int(parts[9]) if len(parts) > 9 else 0

        # 获取颜色（每个类别用不同颜色）
        if category not in color_map:
            color_map[category] = colors[color_idx % len(colors)]
            color_idx += 1
        color = color_map[category]

        # DOTA使用绝对坐标，直接转换为点
        points = []
        for i in range(0, 8, 2):
            px = int(coords[i])
            py = int(coords[i + 1])
            points.append([px, py])

        # 转换为numpy数组
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        # 绘制多边形
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)

        # 绘制类别名称
        label_text = category
        if difficult:
            label_text += " (difficult)"

        (text_w, text_h), baseline = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        x_min, y_min = points[0]
        cv2.rectangle(img, (x_min, y_min - text_h - 5),
                      (x_min + text_w, y_min), color, -1)
        cv2.putText(img, label_text, (x_min, y_min - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        obj_count += 1

    print(f"共绘制 {obj_count} 个标注框")
    print(f"类别颜色映射: {color_map}")

    # 显示结果
    window_name = f"DOTA Verify: {os.path.basename(image_path)}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # 调整窗口大小
    display_w = min(1200, w)
    display_h = int(display_w * (h / w))
    cv2.resizeWindow(window_name, display_w, display_h)

    cv2.imshow(window_name, img)
    print("按任意键关闭窗口...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 保存结果
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='验证DOTA格式标注')
    parser.add_argument('--image', '-i', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\all_graphes\253_16_roi5.png",
                        help='图片文件路径')
    parser.add_argument('--label', '-l', type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_lc_tc_d_anno\dota\labels\val\253_16_roi5.txt",
                        help='DOTA格式标签文件路径')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出图片路径（可选）')

    args = parser.parse_args()

    draw_dota_obb(args.image, args.label, args.output)
