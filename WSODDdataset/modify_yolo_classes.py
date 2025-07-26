import os
import glob

def modify_yolo_classes(input_dir, output_dir, class_mapping):
    """
    批量修改YOLO标注文件中的类别编号
    :param input_dir: 输入标注文件目录
    :param output_dir: 输出标注文件目录
    :param class_mapping: 类别映射字典 {旧类别: 新类别}
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for txt_file in glob.glob(os.path.join(input_dir, "*.txt")):
        output_path = os.path.join(output_dir, os.path.basename(txt_file))
        
        with open(txt_file, 'r') as f_in, open(output_path, 'w') as f_out:
            for line in f_in:
                parts = line.strip().split()
                if len(parts) >= 5:
                    old_cls = parts[0]
                    # 应用类别映射
                    new_cls = class_mapping.get(old_cls, old_cls)  # 未指定的类别保持原样
                    # new_cls = '99'
                    new_line = f"{new_cls} {' '.join(parts[1:])}\n"
                    f_out.write(new_line)

if __name__ == "__main__":
    # 配置参数示例
    input_dir = "E:/dataset/漂浮物-0722/buoy.v1i.yolov/train/labels"
    output_dir = "E:/dataset/漂浮物-0722/buoy.v1i.yolov/train/labels-modify"
    
    # 定义需要修改的类别映射（旧类别: 新类别）
    class_mapping = {
        "0": "1",  # 将原类别0改为1
        "1": "1",
        "2": "1",
        "3": "1",
        "4": "2",
        "5": "2",
        "6": "1",
        "7": "1",
        "8": "1",
        "9": "1",
        "10": "1",
        "11": "1",
        "12": "1",
        "13": "1",
    }
    
    modify_yolo_classes(input_dir, output_dir, class_mapping)
    print(f"标注文件修改完成，已保存到 {output_dir}")
