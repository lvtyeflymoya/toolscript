# 从一个文件夹中读取视频然后抽帧为图片
import cv2
import os
import time

def extract_frames(input_dir, output_dir, interval_sec=0.3):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历输入目录中的所有视频文件
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            video_path = os.path.join(input_dir, filename)
            cap = cv2.VideoCapture(video_path)
            
            # 获取视频帧率和总帧数
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * interval_sec)
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 按时间间隔抽取帧
                if frame_count % frame_interval == 0:
                    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                    output_name = f"{os.path.splitext(filename)[0]}_{timestamp}.jpg"
                    cv2.imwrite(os.path.join(output_dir, output_name), frame)
                    print(f"已抽取第 {frame_count} 帧，时间戳：{timestamp}ms")
                
                frame_count += 1
            
            cap.release()

if __name__ == "__main__":
    input_folder = "E:/Dataset/vedio0804"    # 视频源目录
    output_folder = "E:/Dataset/vedioImage0804-2s"  # 输出图片目录
    
    start_time = time.time()
    extract_frames(input_folder, output_folder, interval_sec=2)
    print(f"处理完成，耗时：{time.time()-start_time:.2f}秒")
