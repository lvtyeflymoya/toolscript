import numpy as np
from PIL import Image, ImageDraw
import random

def draw_c_pair(draw, x, y, width, height, line_width=2):
    """
    在指定位置绘制一对相背的C型轮廓
    
    参数:
        draw: ImageDraw对象
        x, y: 轮廓左上角坐标
        width: 整个轮廓对的宽度
        height: 整个轮廓对的高度
        line_width: 线条宽度
    """
    # 计算C型的弯曲程度
    curve_depth = min(width, height) // 4
    
    # 左侧C型轮廓 (向右开口)
    # 上竖线
    draw.line([(x, y), (x, y + height // 2 - curve_depth)], 
              width=line_width, fill="red")
    # 曲线部分
    for i in range(curve_depth + 1):
        dx = int(curve_depth * (1 - np.cos(i * np.pi / (2 * curve_depth))))
        dy = height // 2 - curve_depth + int(curve_depth * np.sin(i * np.pi / (2 * curve_depth)))
        draw.line([(x + dx - 1, y + dy - 1), (x + dx, y + dy)], 
                  width=line_width, fill="red")
    # 下竖线
    draw.line([(x, y + height // 2 + curve_depth), (x, y + height)], 
              width=line_width, fill="red")
    
    # 右侧C型轮廓 (向左开口)
    right_x = x + width
    # 上竖线
    draw.line([(right_x, y), (right_x, y + height // 2 - curve_depth)], 
              width=line_width, fill="red")
    # 曲线部分
    for i in range(curve_depth + 1):
        dx = int(curve_depth * (1 - np.cos(i * np.pi / (2 * curve_depth))))
        dy = height // 2 - curve_depth + int(curve_depth * np.sin(i * np.pi / (2 * curve_depth)))
        draw.line([(right_x - dx + 1, y + dy - 1), (right_x - dx, y + dy)], 
                  width=line_width, fill="red")
    # 下竖线
    draw.line([(right_x, y + height // 2 + curve_depth), (right_x, y + height)], 
              width=line_width, fill="red")

def generate_c_pairs_image(width=800, height=800, num_pairs=10, min_size=30, max_size=100):
    """
    生成包含多个随机位置相背C型轮廓的图像
    
    参数:
        width, height: 图像尺寸
        num_pairs: 要生成的轮廓对数量
        min_size, max_size: 轮廓对的最小和最大尺寸
    """
    # 创建空白图像
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    for _ in range(num_pairs):
        # 随机生成轮廓尺寸
        pair_width = random.randint(min_size, max_size)
        pair_height = random.randint(min_size, max_size)
        
        # 确保轮廓能完全放在图像内
        x = random.randint(0, width - pair_width)
        y = random.randint(0, height - pair_height)
        
        # 绘制一对相背的C型轮廓
        draw_c_pair(draw, x, y, pair_width, pair_height)
    
    return image

if __name__ == "__main__":
    # 生成图像
    result_image = generate_c_pairs_image(800, 800, 15)
    # 显示图像
    result_image.show()
    # 保存图像
    result_image.save("c_pairs.png")