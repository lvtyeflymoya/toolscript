import os
import xml.etree.ElementTree as ET
import math
import glob

def parse_robndbox(cx, cy, w, h, angle):
    """
    根据 cx, cy, w, h, angle(弧度) 计算出带有旋转的四个角点。
    返回: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    """
    # math.cos/sin 的参数为弧度
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # 图像坐标系通常 y 轴向下。获取未旋转时的四个相对顶点的坐标：
    # top-left
    dx1, dy1 = -w / 2, -h / 2
    # top-right
    dx2, dy2 = w / 2, -h / 2
    # bottom-right
    dx3, dy3 = w / 2, h / 2
    # bottom-left
    dx4, dy4 = -w / 2, h / 2
    
    pts = [(dx1, dy1), (dx2, dy2), (dx3, dy3), (dx4, dy4)]
    
    corners = []
    for dx, dy in pts:
        # 基本旋转矩阵计算
        rx = cx + dx * cos_a - dy * sin_a
        ry = cy + dx * sin_a + dy * cos_a
        corners.append((rx, ry))
        
    return corners

def convert_xml_to_yolo_obb(xml_path, out_dir, class_mapping):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    size = root.find("size")
    if size is None:
        return
        
    img_w = float(size.find("width").text)
    img_h = float(size.find("height").text)
    
    if img_w <= 0 or img_h <= 0:
        return

    # 准备输出的 txt 文件
    out_file_name = os.path.splitext(os.path.basename(xml_path))[0] + ".txt"
    out_file_path = os.path.join(out_dir, out_file_name)
    
    # 提取所有 object
    objects = root.findall("object")
    if not objects:
        return
        
    with open(out_file_path, "w", encoding="utf-8") as f:
        for obj in objects:
            name = obj.find("name").text
            
            # 如果遇到字典中没有的类别，自动添加到字典中
            if name not in class_mapping:
                class_mapping[name] = len(class_mapping)
                
            class_id = class_mapping[name]
            
            # 判断是否为 robndbox (旋转框格式)
            robndbox = obj.find("robndbox")
            if robndbox is not None:
                cx = float(robndbox.find("cx").text)
                cy = float(robndbox.find("cy").text)
                w = float(robndbox.find("w").text)
                h = float(robndbox.find("h").text)
                angle = float(robndbox.find("angle").text)
                
                corners = parse_robndbox(cx, cy, w, h, angle)
            else:
                # 兼容水平框 bndbox (非旋转框)
                bndbox = obj.find("bndbox")
                if bndbox is not None:
                    xmin = float(bndbox.find("xmin").text)
                    ymin = float(bndbox.find("ymin").text)
                    xmax = float(bndbox.find("xmax").text)
                    ymax = float(bndbox.find("ymax").text)
                    corners = [
                        (xmin, ymin),
                        (xmax, ymin),
                        (xmax, ymax),
                        (xmin, ymax)
                    ]
                else:
                    continue
            
            # YOLO OBB 中要求坐标必须属于 [0, 1] 归一化区间
            norm_corners = []
            for x, y in corners:
                nx = max(0.0, min(1.0, x / img_w))
                ny = max(0.0, min(1.0, y / img_h))
                norm_corners.append(nx)
                norm_corners.append(ny)
            
            # 格式: class_index x1 y1 x2 y2 x3 y3 x4 y4
            f.write(f"{class_id} " + " ".join([f"{v:.6f}" for v in norm_corners]) + "\n")

if __name__ == "__main__":
    # 配置 XML 存放目录和想要保存 Labels 的同级目录
    # 注意修改为你的真实目录
    xml_dir = r"E:\work\drawing_analysis\dataset\obb_all_graphes\xml"
    out_dir = r"E:\work\drawing_analysis\dataset\obb_all_graphes\labels"
    
    os.makedirs(out_dir, exist_ok=True)
    
    # 初始化预置类别 (如果有新的会自动在上面代码中添加)
    class_mapping = {
        "angelSteel": 0,
        "clamp": 1
    }
    
    xml_files = glob.glob(os.path.join(xml_dir, "*.xml"))
    print(f"找到 {len(xml_files)} 个 XML 文件")
    
    for xml_path in xml_files:
        try:
            convert_xml_to_yolo_obb(xml_path, out_dir, class_mapping)
        except Exception as e:
            print(f"处理文件 {xml_path} 时出现错误: {e}")
            
    print("=" * 40)
    print("转换完成！类别映射如下 (在训练 YOLOv8-OBB 的 dataset.yaml 中需要同此顺序和内容保持一致):")
    for k, v in class_mapping.items():
        print(f"  {v}: {k}")
