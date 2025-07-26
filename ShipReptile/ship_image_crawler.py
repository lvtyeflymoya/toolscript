import os
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

# 导入本地测试模块
try:
    from local_test_crawler import LocalShipImageGenerator
    LOCAL_TEST_AVAILABLE = True
except ImportError:
    LOCAL_TEST_AVAILABLE = False


class ShipImageCrawler:
    def __init__(self, save_dir='./images', local_test_mode=False):
        """
        初始化爬虫类
        :param save_dir: 图片保存目录
        :param local_test_mode: 是否使用本地测试模式（不进行网络请求，生成本地测试图片）
        """
        self.save_dir = save_dir
        self.local_test_mode = local_test_mode
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        if self.local_test_mode:
            if not LOCAL_TEST_AVAILABLE:
                raise ImportError("本地测试模式需要local_test_crawler.py模块，但无法导入该模块")
            
            # 初始化本地测试图片生成器
            self.local_generator = LocalShipImageGenerator(save_dir=save_dir)
            print(f"爬虫初始化完成（本地测试模式），图片将保存到: {os.path.abspath(save_dir)}")
        else:
            # 使用更现代的User-Agent
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
            }
            
            print(f"图片将保存到: {os.path.abspath(save_dir)}")
            print("初始化爬虫完成（网络模式），准备开始爬取...")
            
            # 设置会话，保持cookie
            self.session = requests.Session()
    
    def get_page_content(self, url):
        """
        获取网页内容
        :param url: 网页URL
        :return: 网页内容
        """
        max_retries = 5  # 增加最大重试次数
        retry_count = 0
        
        # 根据不同网站调整headers
        headers = self.headers.copy()
        
        # 针对视觉中国网站的特殊处理
        if 'vcg.com' in url:
            headers['Referer'] = 'https://www.vcg.com/'
            headers['Host'] = 'www.vcg.com'
            print("正在访问视觉中国网站，已调整请求头...")
        
        # 针对抖音网站的特殊处理
        elif 'douyin.com' in url:
            headers['Referer'] = 'https://www.douyin.com/'
            headers['Host'] = 'www.douyin.com'
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
            headers['sec-ch-ua'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = '"Windows"'
            headers['sec-fetch-dest'] = 'document'
            headers['sec-fetch-mode'] = 'navigate'
            headers['sec-fetch-site'] = 'none'
            headers['sec-fetch-user'] = '?1'
            headers['upgrade-insecure-requests'] = '1'
            print("正在访问抖音网站，已调整请求头...")
        
        while retry_count < max_retries:
            try:
                print(f"正在获取网页: {url}")
                # 使用session发送请求
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=30,  # 进一步增加超时时间
                    allow_redirects=True
                )
                response.raise_for_status()  # 如果请求不成功则抛出异常
                
                # 检查是否是有效的HTML内容
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                    print(f"警告: 响应不是HTML内容，而是 {content_type}")
                
                # 打印响应状态和大小
                print(f"获取成功: 状态码 {response.status_code}, 内容大小: {len(response.text)} 字节")
                
                # 如果是抖音网站，可能需要处理JavaScript渲染的内容
                if 'douyin.com' in url and len(response.text) < 5000:
                    print("警告: 抖音网站返回内容较少，可能需要浏览器渲染支持")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        wait_time = retry_count * 4  # 增加等待时间
                        print(f"等待 {wait_time} 秒后使用不同参数重试...")
                        time.sleep(wait_time)
                        continue
                
                return response.text
            
            except requests.exceptions.RequestException as e:
                retry_count += 1
                wait_time = retry_count * 4  # 递增等待时间，进一步增加等待时间
                print(f"获取网页失败 (尝试 {retry_count}/{max_retries}): {e}")
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            except Exception as e:
                # 捕获所有其他异常
                retry_count += 1
                wait_time = retry_count * 4
                print(f"获取网页时发生未知错误 (尝试 {retry_count}/{max_retries}): {e}")
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print(f"获取网页内容失败，已达到最大重试次数: {max_retries}")
        return None
    
    def parse_image_urls(self, html_content, url, img_keyword='ship'):
        """
        从HTML内容中解析图片URL
        :param html_content: HTML内容
        :param url: 原始网页URL，用于将相对路径转为绝对路径
        :param img_keyword: 图片关键词，用于筛选相关图片
        :return: 图片URL列表
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 针对抖音网站的特殊处理
        if 'douyin.com' in url or '抖音' in url:
            return self.parse_douyin_images(soup, url, img_keyword)
        # 通用处理方式
        else:
            img_tags = soup.find_all('img')
            
            image_urls = []
            for img in img_tags:
                # 获取图片src属性
                img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                if not img_url:
                    continue
                
                # 将相对路径转为绝对路径
                img_url = urljoin(url, img_url)
                
                # 过滤小图标和广告图片
                if 'svg' in img_url or 'icon' in img_url or 'logo' in img_url or 'ad' in img_url:
                    continue
                
                # 检查图片URL是否包含关键词或者alt/title属性包含关键词
                alt_text = img.get('alt', '').lower()
                title_text = img.get('title', '').lower()
                
                # 检查是否包含船只相关关键词
                keywords = ['ship', 'boat', 'vessel', '船', '舰', '艇', '游艇', '帆船', '轮船']
                if any(kw in alt_text or kw in title_text or kw in img_url.lower() for kw in keywords) or \
                   img_keyword.lower() in alt_text or img_keyword.lower() in title_text or img_keyword.lower() in img_url.lower():
                    image_urls.append(img_url)
            
            print(f"找到 {len(image_urls)} 张潜在的船只图片")
            return image_urls
        
    def parse_douyin_images(self, soup, url, img_keyword):
        """
        解析抖音网站的图片
        :param soup: BeautifulSoup对象
        :param url: 网页URL
        :param img_keyword: 图片关键词
        :return: 图片URL列表
        """
        print(f"正在解析抖音网站图片: {url}")
        image_urls = []
        
        # 定义船只相关关键词
        ship_keywords = ['ship', 'boat', 'vessel', 'yacht', 'sailing', 'cruise', 
                        '船', '舰', '艇', '游艇', '帆船', '轮船', '渔船', '货船', '邮轮']
        
        # 方法1: 查找所有图片和视频标签
        img_tags = soup.find_all(['img', 'video'])
        for tag in img_tags:
            # 对于视频标签，尝试获取封面图
            if tag.name == 'video':
                img_url = tag.get('poster')
                if img_url:
                    img_url = urljoin(url, img_url)
                    # 过滤小图标和广告图片
                    if any(x in img_url.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                        continue
                    
                    # 检查图片大小信息（如果URL中包含尺寸信息）
                    if any(x in img_url.lower() for x in ['16x16', '32x32', '64x64', 'small', 'thumb', 'tiny']):
                        continue
                    
                    # 添加到结果列表
                    image_urls.append(img_url)
            # 对于图片标签
            else:
                img_url = tag.get('src') or tag.get('data-src') or tag.get('data-original')
                if img_url:
                    img_url = urljoin(url, img_url)
                    # 过滤小图标和广告图片
                    if any(x in img_url.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                        continue
                    
                    # 检查图片大小信息（如果URL中包含尺寸信息）
                    if any(x in img_url.lower() for x in ['16x16', '32x32', '64x64', 'small', 'thumb', 'tiny']):
                        continue
                    
                    # 检查alt和title属性是否包含船只关键词
                    alt_text = tag.get('alt', '').lower()
                    title_text = tag.get('title', '').lower()
                    
                    # 如果alt或title包含船只关键词，优先添加
                    if any(kw in alt_text or kw in title_text for kw in ship_keywords):
                        image_urls.append(img_url)
                        continue
                    
                    # 如果URL包含船只关键词或搜索关键词，也添加
                    if any(kw in img_url.lower() for kw in ship_keywords) or img_keyword.lower() in img_url.lower():
                        image_urls.append(img_url)
                    # 如果没有明确的关键词匹配，但图片看起来是内容图片而非界面元素，也添加
                    elif 'jpg' in img_url.lower() or 'jpeg' in img_url.lower() or 'png' in img_url.lower():
                        image_urls.append(img_url)
        
        # 方法2: 查找所有可能包含图片URL的属性
        for tag in soup.find_all():
            for attr in ['data-src', 'data-original', 'data-origin', 'data-img-url', 'data-image', 'data-cover']:
                img_url = tag.get(attr)
                if img_url and isinstance(img_url, str) and img_url.startswith(('http://', 'https://')):
                    # 过滤小图标和广告图片
                    if any(x in img_url.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                        continue
                    
                    # 检查图片大小信息（如果URL中包含尺寸信息）
                    if any(x in img_url.lower() for x in ['16x16', '32x32', '64x64', 'small', 'thumb', 'tiny']):
                        continue
                    
                    # 如果URL包含船只关键词或搜索关键词，添加
                    if any(kw in img_url.lower() for kw in ship_keywords) or img_keyword.lower() in img_url.lower():
                        image_urls.append(img_url)
                    # 如果没有明确的关键词匹配，但图片看起来是内容图片而非界面元素，也添加
                    elif 'jpg' in img_url.lower() or 'jpeg' in img_url.lower() or 'png' in img_url.lower():
                        image_urls.append(img_url)
        
        # 方法3: 查找所有背景图片样式
        import re
        for tag in soup.find_all(style=True):
            style = tag['style']
            url_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            if url_match:
                img_url = url_match.group(1)
                img_url = urljoin(url, img_url)
                
                # 过滤小图标和广告图片
                if any(x in img_url.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                    continue
                
                # 检查图片大小信息（如果URL中包含尺寸信息）
                if any(x in img_url.lower() for x in ['16x16', '32x32', '64x64', 'small', 'thumb', 'tiny']):
                    continue
                
                # 如果URL包含船只关键词或搜索关键词，添加
                if any(kw in img_url.lower() for kw in ship_keywords) or img_keyword.lower() in img_url.lower():
                    image_urls.append(img_url)
                # 如果没有明确的关键词匹配，但图片看起来是内容图片而非界面元素，也添加
                elif 'jpg' in img_url.lower() or 'jpeg' in img_url.lower() or 'png' in img_url.lower():
                    image_urls.append(img_url)
        
        # 方法4: 查找所有script标签中的JSON数据
        import json
        for script in soup.find_all('script', type='application/json'):
            try:
                if script.string:
                    data = json.loads(script.string)
                    self._extract_image_urls_from_json(data, image_urls, ship_keywords, img_keyword)
            except (json.JSONDecodeError, Exception) as e:
                continue
        
        # 方法5: 查找所有script标签中的URL模式
        for script in soup.find_all('script'):
            if script.string:
                # 查找所有可能的图片URL
                url_patterns = re.findall(r'https?://[^\s\'\"]+\.(jpg|jpeg|png|gif|webp)', script.string, re.IGNORECASE)
                for match in url_patterns:
                    img_url = match[0]
                    # 过滤小图标和广告图片
                    if any(x in img_url.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                        continue
                    
                    # 如果URL包含船只关键词或搜索关键词，添加
                    if any(kw in img_url.lower() for kw in ship_keywords) or img_keyword.lower() in img_url.lower():
                        image_urls.append(img_url)
                    # 如果没有明确的关键词匹配，但图片看起来是内容图片而非界面元素，也添加
                    elif 'jpg' in img_url.lower() or 'jpeg' in img_url.lower() or 'png' in img_url.lower():
                        image_urls.append(img_url)
        
        # 去重
        image_urls = list(set(image_urls))
        print(f"在抖音网站找到 {len(image_urls)} 张潜在的船只图片")
        return image_urls
        
    def _extract_image_urls_from_json(self, data, image_urls, ship_keywords, img_keyword):
        """
        从JSON数据中递归提取图片URL
        :param data: JSON数据
        :param image_urls: 图片URL列表，用于存储结果
        :param ship_keywords: 船只相关关键词列表
        :param img_keyword: 搜索关键词
        """
        if isinstance(data, dict):
            for key, value in data.items():
                # 检查常见的图片URL字段名
                if isinstance(value, str) and key.lower() in ['cover', 'image', 'img', 'url', 'src', 'poster', 'thumbnail', 'origin_cover']:
                    if value.startswith(('http://', 'https://')) and any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        # 过滤小图标和广告图片
                        if any(x in value.lower() for x in ['svg', 'icon', 'logo', 'ad', 'avatar', 'emoji']):
                            continue
                        
                        # 检查图片大小信息（如果URL中包含尺寸信息）
                        if any(x in value.lower() for x in ['16x16', '32x32', '64x64', 'small', 'thumb', 'tiny']):
                            continue
                        
                        # 如果URL包含船只关键词或搜索关键词，添加
                        if any(kw in value.lower() for kw in ship_keywords) or img_keyword.lower() in value.lower():
                            image_urls.append(value)
                        # 如果没有明确的关键词匹配，但图片看起来是内容图片而非界面元素，也添加
                        else:
                            image_urls.append(value)
                else:
                    self._extract_image_urls_from_json(value, image_urls, ship_keywords, img_keyword)
        elif isinstance(data, list):
            for item in data:
                self._extract_image_urls_from_json(item, image_urls, ship_keywords, img_keyword)
        
        else:
            # 通用处理方式
            img_tags = soup.find_all('img')
            
            image_urls = []
            for img in img_tags:
                # 获取图片src属性
                img_url = img.get('src')
                if not img_url:
                    continue
                
                # 将相对路径转为绝对路径
                img_url = urljoin(url, img_url)
                
                # 检查图片URL是否包含关键词
                if img_keyword.lower() in img_url.lower() or \
                   img_keyword.lower() in (img.get('alt', '').lower()) or \
                   img_keyword.lower() in (img.get('title', '').lower()):
                    image_urls.append(img_url)
            
            return image_urls
    
    def download_image(self, img_url, filename=None):
        """
        下载图片
        :param img_url: 图片URL
        :param filename: 保存的文件名，如果为None则使用URL中的文件名
        :return: 是否下载成功
        """
        max_retries = 3  # 最大重试次数
        retry_count = 0
        
        # 针对不同网站调整headers
        headers = self.headers.copy()
        
        # 针对抖音网站的特殊处理
        if 'douyin.com' in img_url:
            headers['Referer'] = 'https://www.douyin.com/'
            headers['Host'] = 'www.douyin.com'
            print("正在下载抖音图片，已调整请求头...")
        
        while retry_count < max_retries:
            try:
                print(f"正在下载图片: {img_url}")
                
                # 使用session下载图片
                response = self.session.get(
                    img_url, 
                    headers=headers, 
                    timeout=20,  # 增加超时时间 
                    stream=True,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # 检查是否是图片内容
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print(f"警告: 响应不是图片内容，而是 {content_type}")
                    if retry_count == max_retries - 1:  # 最后一次尝试时仍然继续
                        print("尝试继续下载，即使内容类型不是图片...")
                    else:
                        retry_count += 1
                        wait_time = retry_count * 3  # 增加等待时间
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                
                # 如果没有指定文件名，则从URL中提取
                if not filename:
                    filename = os.path.basename(img_url).split('?')[0]  # 移除URL参数
                    if not filename or '.' not in filename:  # 确保文件名有扩展名
                        # 根据内容类型确定扩展名
                        ext = '.jpg'  # 默认扩展名
                        if 'image/png' in content_type:
                            ext = '.png'
                        elif 'image/gif' in content_type:
                            ext = '.gif'
                        elif 'image/webp' in content_type:
                            ext = '.webp'
                        
                        filename = f"ship_{int(time.time())}_{random.randint(1000, 9999)}{ext}"
                
                # 确保文件名是安全的（不包含非法字符）
                filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
                
                # 保存图片
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 验证文件大小
                file_size = os.path.getsize(file_path)
                if file_size < 1000:  # 小于1KB的文件可能是错误的
                    print(f"警告: 下载的文件太小 ({file_size} 字节)，可能不是有效图片")
                    # 但仍然保留文件
                
                print(f"图片下载成功: {file_path} ({file_size} 字节)")
                return True
            
            except Exception as e:
                retry_count += 1
                wait_time = retry_count * 2  # 递增等待时间
                print(f"下载图片失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"下载图片失败，已达到最大重试次数: {max_retries}")
                    return False
        
        return False
    
    def crawl(self, url, max_images=20, img_keyword='ship'):
        """
        爬取指定网页上的船只图片
        :param url: 网页URL
        :param max_images: 最大下载图片数量
        :param img_keyword: 图片关键词
        :return: 下载的图片数量
        """
        print(f"\n{'='*50}")
        print(f"开始爬取: {url}")
        print(f"{'='*50}")
        
        # 如果是本地测试模式，使用本地图片生成器
        if self.local_test_mode:
            print("使用本地测试模式，生成测试图片...")
            download_count = 0
            
            # 生成一半普通图片，一半船只轮廓图片
            normal_count = max_images // 2
            outline_count = max_images - normal_count
            
            # 生成普通图片
            for i in range(normal_count):
                # 显示进度
                progress = f"[{i+1}/{max_images}]"
                print(f"\n{progress} 正在生成普通测试图片...")
                
                # 随机大小
                width = random.randint(600, 1200)
                height = random.randint(400, 800)
                
                # 生成图片
                self.local_generator.generate_test_image(width=width, height=height)
                download_count += 1
                
                # 添加随机延时，模拟真实爬取
                if i < normal_count - 1:
                    delay = random.uniform(0.5, 1.5)
                    print(f"等待 {delay:.2f} 秒...")
                    time.sleep(delay)
            
            # 生成船只轮廓图片
            for i in range(outline_count):
                # 显示进度
                progress = f"[{normal_count+i+1}/{max_images}]"
                print(f"\n{progress} 正在生成船只轮廓图片...")
                
                # 随机大小
                width = random.randint(600, 1200)
                height = random.randint(400, 800)
                
                # 生成图片
                self.local_generator.generate_ship_outline(width=width, height=height)
                download_count += 1
                
                # 添加随机延时，模拟真实爬取
                if i < outline_count - 1:
                    delay = random.uniform(0.5, 1.5)
                    print(f"等待 {delay:.2f} 秒...")
                    time.sleep(delay)
            
            print(f"\n{'='*50}")
            print(f"本地测试完成，共生成 {download_count} 张测试图片")
            print(f"{'='*50}")
            return download_count
        
        try:
            # 获取网页内容
            html_content = self.get_page_content(url)
            if not html_content:
                print(f"无法获取网页内容，跳过: {url}")
                return 0
            
            # 解析图片URL
            image_urls = self.parse_image_urls(html_content, url, img_keyword)
            
            if not image_urls:
                print(f"未找到任何船只图片，请检查网页结构或关键词: {url}")
                return 0
            
            print(f"找到 {len(image_urls)} 张潜在的船只图片")
            
            # 下载图片
            download_count = 0
            for i, img_url in enumerate(image_urls):
                if download_count >= max_images:
                    print(f"已达到最大下载数量限制: {max_images}")
                    break
                
                print(f"\n正在处理第 {i+1}/{len(image_urls)} 张图片")
                print(f"进度: {download_count}/{max_images} ({int(download_count/max_images*100 if max_images > 0 else 0)}%)")
                
                success = self.download_image(img_url)
                if success:
                    download_count += 1
                
                # 添加随机延时，避免请求过于频繁
                delay = random.uniform(1.0, 3.0)
                print(f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)
            
            print(f"\n{'='*50}")
            print(f"下载完成，网站 {url} 共下载 {download_count} 张图片")
            print(f"{'='*50}")
            return download_count
            
        except Exception as e:
            print(f"爬取过程中发生错误: {e}")
            return 0


def main():
    try:
        print("\n船只图片爬虫启动...\n")
        
        # 解析命令行参数
        import argparse
        parser = argparse.ArgumentParser(description='船只图片爬虫')
        parser.add_argument('--local', action='store_true', help='使用本地测试模式（不进行网络请求）')
        parser.add_argument('--max-images', type=int, default=5, help='每个网站最大下载图片数量')
        parser.add_argument('--save-dir', type=str, default='./downloaded_ships', help='图片保存目录')
        args = parser.parse_args()
        
        # 创建保存目录
        save_dir = args.save_dir
        abs_save_dir = os.path.abspath(save_dir)
        print(f"图片将保存到: {abs_save_dir}")
        
        # 设置每个网站的最大下载图片数量和关键词
        max_images_per_site = args.max_images
        keywords = ['ship', 'boat', 'vessel', 'sailing', '船', '舰', '艇', '游艇', '帆船']  # 可以使用多个关键词，包括中文关键词
        
        # 检查是否使用本地测试模式
        local_test_mode = args.local
        if local_test_mode:
            print("\n使用本地测试模式，将生成本地测试图片而不进行网络请求")
            if not LOCAL_TEST_AVAILABLE:
                print("错误: 本地测试模式需要local_test_crawler.py模块，但无法导入该模块")
                print("请确保local_test_crawler.py文件存在于当前目录")
                return
        else:
            print("\n使用网络模式，将从网站下载船只图片")
        
        # 创建爬虫实例
        crawler = ShipImageCrawler(save_dir=save_dir, local_test_mode=local_test_mode)
        
        # 爬取多个网站的船只图片
        websites = [
            # 抖音上的船只相关页面
            'https://www.douyin.com/search/船?source=normal_search&aid=3a3cec5d-f9a6-4749-9e9c-becbd6a0b787',
            'https://www.douyin.com/search/游艇?source=normal_search&aid=3a3cec5d-f9a6-4749-9e9c-becbd6a0b787',
            'https://www.douyin.com/search/帆船?source=normal_search&aid=3a3cec5d-f9a6-4749-9e9c-becbd6a0b787',
            'https://www.douyin.com/search/轮船?source=normal_search&aid=3a3cec5d-f9a6-4749-9e9c-becbd6a0b787',
            # 可以添加更多网站
        ]
        
        print(f"\n将爬取 {len(websites)} 个网站，每个网站最多下载 {max_images_per_site} 张图片")
        print(f"使用的关键词: {', '.join(keywords)}\n")
        
        # 开始计时
        start_time = time.time()
        
        total_images = 0
        successful_sites = 0
        
        for i, website in enumerate(websites):
            print(f"\n处理网站 {i+1}/{len(websites)}: {website}")
            
            try:
                # 随机选择一个关键词
                keyword = random.choice(keywords)
                print(f"使用关键词: {keyword}")
                
                # 爬取网站
                count = crawler.crawl(website, max_images=max_images_per_site, img_keyword=keyword)
                total_images += count
                
                if count > 0:
                    successful_sites += 1
                
                # 在不同网站之间添加更长的延时
                if i < len(websites) - 1:  # 如果不是最后一个网站
                    delay = random.uniform(2.0, 5.0) if local_test_mode else random.uniform(5.0, 10.0)
                    print(f"\n等待 {delay:.2f} 秒后继续下一个网站...")
                    time.sleep(delay)
            
            except Exception as e:
                print(f"爬取 {website} 时出错: {e}")
        
        # 计算总耗时
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        
        print(f"\n{'='*60}")
        print(f"爬取完成!")
        print(f"模式: {'本地测试' if local_test_mode else '网络爬取'}")
        print(f"总共爬取了 {len(websites)} 个网站，成功 {successful_sites} 个")
        print(f"总共{'生成' if local_test_mode else '下载'}了 {total_images} 张船只图片")
        print(f"总耗时: {int(minutes)}分{int(seconds)}秒")
        print(f"图片保存在: {abs_save_dir}")
        print(f"{'='*60}")
    
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n爬虫程序结束")
        
        # 如果下载了图片，提示用户查看
        if os.path.exists(save_dir) and len(os.listdir(save_dir)) > 0:
            print(f"您可以在 {abs_save_dir} 目录中查看下载的图片")
            
            # 在Windows系统下，可以尝试打开资源管理器显示图片
            try:
                if os.name == 'nt':  # Windows系统
                    os.startfile(abs_save_dir)
                    print("已为您打开图片文件夹")
            except:
                pass  # 忽略打开文件夹的错误


if __name__ == "__main__":
    main()