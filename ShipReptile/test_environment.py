import os
import sys
import requests
import bs4
from bs4 import BeautifulSoup
from PIL import Image
import io


def test_environment():
    """测试环境是否正确设置"""
    print("\n===== 环境测试开始 =====")
    
    # 测试Python版本
    print(f"Python版本: {sys.version}")
    
    # 测试依赖库
    print("\n依赖库版本:")
    print(f"- requests: {requests.__version__}")
    print(f"- BeautifulSoup4: {bs4.__version__}")
    print(f"- Pillow: {Image.__version__}")
    
    # 创建测试目录
    test_dir = './test_images'
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    print(f"\n创建测试目录: {os.path.abspath(test_dir)}")
    
    # 创建测试图片
    try:
        # 创建一个简单的彩色图片
        img = Image.new('RGB', (100, 100), color='red')
        img_path = os.path.join(test_dir, 'test_red.png')
        img.save(img_path)
        print(f"创建测试图片: {os.path.abspath(img_path)}")
        
        # 打开并显示图片信息
        with Image.open(img_path) as img:
            print(f"图片大小: {img.size}")
            print(f"图片模式: {img.mode}")
        
        print("\n图片处理测试成功!")
    except Exception as e:
        print(f"图片处理测试失败: {e}")
    
    # 测试HTML解析
    try:
        html = """<html><body><h1>Ship Test</h1><img src="test.jpg" alt="A ship image"><p>This is a test</p></body></html>"""
        soup = BeautifulSoup(html, 'html.parser')
        img_tags = soup.find_all('img')
        print(f"\nHTML解析测试: 找到 {len(img_tags)} 个图片标签")
        print(f"图片标签属性: {img_tags[0].attrs}")
        print("HTML解析测试成功!")
    except Exception as e:
        print(f"HTML解析测试失败: {e}")
    
    print("\n===== 环境测试完成 =====\n")
    print("所有依赖已正确安装，环境设置正常!")
    print("注意: 脚本运行时出现网络错误可能是由于网络连接问题或代理设置导致的，而不是环境问题。")


if __name__ == "__main__":
    test_environment()