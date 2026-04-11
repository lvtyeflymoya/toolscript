import cv2
import numpy as np
import os

def draw_yolo_obb(image_path, label_path, class_names=None):
    """
    读取图片和 YOLO-OBB 格式的标签文件，绘制旋转框并显示
    """
    if not os.path.exists(image_path):
        print(f"找不到图片文件: {image_path}")
        return
    if not os.path.exists(label_path):
        print(f"找不到标签文件: {label_path}")
        return
        
    # 1. 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("图片读取失败，请检查路径中是否有中文字符或文件是否损坏。")
        # 可以尝试使用 imdecode 解决中文路径读取问题：
        # img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return
        
    h, w, _ = img.shape
    
    # 预设几个常用的颜色 (BGR格式)
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255)]
    
    # 2. 读取标签文件
    with open(label_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        class_id = int(parts[0])
        color = colors[class_id % len(colors)]
        
        # 提取归一化的 8 个坐标点：x1 y1 x2 y2 x3 y3 x4 y4
        coords = [float(x) for x in parts[1:9]]
        
        # 3. 将归一化坐标还原到原图的像素坐标
        points = []
        for i in range(0, 8, 2):
            px = int(coords[i] * w)
            py = int(coords[i+1] * h)
            points.append([px, py])
            
        # 转换为 numpy 数组，并调整形状以适应 cv2.polylines
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # 4. 绘制多边形 (闭合的旋转矩形框)
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
        
        # 5. 在第一个点的位置绘制类别名称文本
        label_text = str(class_id)
        if class_names and class_id < len(class_names):
            label_text = class_names[class_id]
            
        # 给文本加个背景以便看得更清楚（可选）
        (text_w, text_h), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        x_min, y_min = points[0][0], points[0][1]
        cv2.rectangle(img, (x_min, y_min - text_h - baseline), (x_min + text_w, y_min), color, -1)
        # 绘制文本
        cv2.putText(img, label_text, (x_min, y_min - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
    # 6. 显示结果
    window_name = "YOLO-OBB Verify"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # 限制窗口显示大小，防止大分辨率图片超出屏幕
    display_w = min(w, 1200)
    display_h = int(display_w * (h / w))
    cv2.resizeWindow(window_name, display_w, display_h)
    
    cv2.imshow(window_name, img)
    print("绘制完成！请在弹出的图片窗口中查看，按任意键关闭窗口。")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 也可将结果保存下来核对
    # save_path = "verify_result.jpg"
    # cv2.imwrite(save_path, img)
    # print(f"结果已保存至 {save_path}")

if __name__ == "__main__":
    # 请根据您本地的实际路径替换以下内
    image_file = r"E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\253_286_roi5.png"
    label_file = r"E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_anno\yolo\labels\test\253_286_roi5.txt"
    
    # 转换时约定的类别名字典（顺序必须和转换时生成的数字ID对应，0对应第一个，1对应第二个）
    class_list = ["angelSteelBack", "angelSteelFront", "clamp", "LConnection", "TConnection", 
                  "tiltedConnection", "dimension", "arrowhead"]
    
    draw_yolo_obb(image_file, label_file, class_list)
