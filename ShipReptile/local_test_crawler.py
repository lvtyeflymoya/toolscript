import os
import time
import random
from PIL import Image
import io


class LocalShipImageGenerator:
    def __init__(self, save_dir='./local_test_images'):
        """
        初始化本地测试图片生成器
        :param save_dir: 图片保存目录
        """
        self.save_dir = save_dir
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def generate_test_image(self, width=800, height=600, color=None, filename=None):
        """
        生成测试图片
        :param width: 图片宽度
        :param height: 图片高度
        :param color: 图片颜色，如果为None则随机生成
        :param filename: 文件名，如果为None则自动生成
        :return: 保存的文件路径
        """
        # 如果没有指定颜色，则随机生成
        if color is None:
            # 随机生成RGB颜色
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = (r, g, b)
        
        # 创建图片
        img = Image.new('RGB', (width, height), color=color)
        
        # 如果没有指定文件名，则自动生成
        if not filename:
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            filename = f"ship_{timestamp}_{random_num}.png"
        
        # 保存图片
        file_path = os.path.join(self.save_dir, filename)
        img.save(file_path)
        
        print(f"生成测试图片: {os.path.abspath(file_path)}")
        return file_path
    
    def generate_ship_outline(self, width=800, height=600, filename=None):
        """
        生成带有简单船只轮廓的图片
        :param width: 图片宽度
        :param height: 图片高度
        :param filename: 文件名，如果为None则自动生成
        :return: 保存的文件路径
        """
        # 创建背景图片（蓝色代表海洋）
        img = Image.new('RGB', (width, height), color=(66, 135, 245))
        
        # 创建绘图对象
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的船只轮廓
        # 船体
        ship_color = (120, 120, 120)  # 灰色
        ship_width = width // 2
        ship_height = height // 4
        ship_x = (width - ship_width) // 2
        ship_y = height // 2
        
        # 绘制船体
        draw.rectangle(
            [(ship_x, ship_y), (ship_x + ship_width, ship_y + ship_height)],
            fill=ship_color,
            outline=(0, 0, 0)
        )
        
        # 绘制船舱
        cabin_width = ship_width // 3
        cabin_height = ship_height // 2
        cabin_x = ship_x + (ship_width - cabin_width) // 2
        cabin_y = ship_y - cabin_height // 2
        
        draw.rectangle(
            [(cabin_x, cabin_y), (cabin_x + cabin_width, cabin_y + cabin_height)],
            fill=(200, 200, 200),
            outline=(0, 0, 0)
        )
        
        # 如果没有指定文件名，则自动生成
        if not filename:
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            filename = f"ship_outline_{timestamp}_{random_num}.png"
        
        # 保存图片
        file_path = os.path.join(self.save_dir, filename)
        img.save(file_path)
        
        print(f"生成船只轮廓图片: {os.path.abspath(file_path)}")
        return file_path
    
    def generate_multiple_images(self, count=5):
        """
        生成多张测试图片
        :param count: 图片数量
        :return: 生成的图片路径列表
        """
        image_paths = []
        
        print(f"开始生成 {count} 张测试图片...")
        
        # 生成纯色背景图片
        for i in range(count // 2):
            # 随机大小
            width = random.randint(600, 1200)
            height = random.randint(400, 800)
            
            # 生成图片
            path = self.generate_test_image(width=width, height=height)
            image_paths.append(path)
            
            # 添加延时，模拟真实爬取
            time.sleep(random.uniform(0.2, 0.5))
        
        # 生成船只轮廓图片
        for i in range(count - count // 2):
            # 随机大小
            width = random.randint(600, 1200)
            height = random.randint(400, 800)
            
            # 生成图片
            path = self.generate_ship_outline(width=width, height=height)
            image_paths.append(path)
            
            # 添加延时，模拟真实爬取
            time.sleep(random.uniform(0.2, 0.5))
        
        print(f"生成完成，共生成 {len(image_paths)} 张测试图片")
        return image_paths


def main():
    # 创建本地测试图片生成器
    generator = LocalShipImageGenerator(save_dir='./local_test_images')
    
    # 生成多张测试图片
    generator.generate_multiple_images(count=10)
    
    print("\n本地测试完成！")
    print("注意: 这个脚本只是生成了本地测试图片，没有进行实际的网络爬取。")
    print("      实际爬取失败可能是由于网络连接问题或代理设置导致的。")


if __name__ == "__main__":
    main()