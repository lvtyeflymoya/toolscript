"""
按类别从 xAnyLabeling OBB 标注中裁剪区域

裁剪方式：取 OBB 四点的轴对齐外接矩形，在裁剪图中 OBB 多边形外的像素填白。

用法示例：
python crop_obb_by_class.py \
    --json_dir "E:/work/drawing_analysis/dataset/obb_all_graphes/annotation/ab_af_c_lc_tc_d_an_cn_em_labels/x_json" \
    --image_dir "E:/work/drawing_analysis/dataset/obb_all_graphes/annotation/all_graphes" \
    --output_dir "./output" \
    --classes dimension clampNumber
"""

import json
import os
import argparse
from pathlib import Path

import cv2
import numpy as np


def crop_obb_regions(json_dir, image_dir, output_dir, target_classes):
    json_dir = Path(json_dir)
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    target_set = set(target_classes)
    json_files = list(json_dir.glob("*.json"))
    print(f"找到 {len(json_files)} 个 JSON 文件，目标类别: {target_set}")

    total_cropped = 0

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = image_dir / data["imagePath"]
        if not image_path.exists():
            print(f"图片不存在: {image_path}")
            continue

        img = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            print(f"图片读取失败: {image_path}")
            continue

        stem = json_file.stem
        class_counter = {}

        for shape in data.get("shapes", []):
            if shape.get("shape_type") != "rotation":
                continue

            label = shape.get("label")
            if label not in target_set:
                continue

            points = shape.get("points", [])
            if len(points) != 4:
                continue

            pts = np.array(points, dtype=np.float32)

            # 轴对齐外接矩形
            x, y, w, h = cv2.boundingRect(pts)

            # 边界检查
            img_h, img_w = img.shape[:2]
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(img_w, x + w)
            y2 = min(img_h, y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            # 截取外接矩形区域
            crop = img[y1:y2, x1:x2].copy()

            # 创建多边形掩码（坐标偏移到裁剪区域局部坐标）
            local_pts = pts - np.array([x1, y1])
            local_pts = local_pts.astype(np.int32)

            mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
            cv2.fillPoly(mask, [local_pts], 255)

            # 掩码外像素填白
            crop[mask == 0] = 255

            # 保存
            class_counter[label] = class_counter.get(label, 0) + 1
            idx = class_counter[label]
            save_name = f"{stem}_{label}_{idx}.png"
            save_path = output_dir / save_name
            cv2.imencode(".png", crop)[1].tofile(str(save_path))
            total_cropped += 1

        print(f"已处理: {json_file.name}")

    print(f"完成！共裁剪 {total_cropped} 个区域，保存至 {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="按类别从 xAnyLabeling OBB 标注中裁剪区域")
    parser.add_argument("--json_dir", type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_lc_tc_d_an_cn_em_labels\x_json", 
                        help="JSON 标注文件目录")
    parser.add_argument("--image_dir", type=str, default=r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\all_graphes",
                        help="对应图片目录")
    parser.add_argument("--output_dir", type=str, default=r"E:\work\drawing_analysis\dataset\ocr\an_cn_em_cropped_images\angleSteel_number",
                        help="裁剪结果输出目录")
    parser.add_argument("--classes", nargs="+", default=["dimension"], 
                        help="要裁剪的类别列表")

    args = parser.parse_args()
    crop_obb_regions(args.json_dir, args.image_dir, args.output_dir, args.classes)
