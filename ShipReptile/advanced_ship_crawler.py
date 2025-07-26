import os
import requests
import time
import random
import hashlib
import threading
import queue
import re
import warnings
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AdvancedShipCrawler:
    def __init__(self, save_dir='./advanced_ships', max_threads=5, classify_ships=True):
        """
        初始化高级爬虫类
        :param save_dir: 图片保存目录
        :param max_threads: 最大线程数
        :param classify_ships: 是否自动分类船只类型
        """
        # 使用更完整的浏览器模拟信息
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://image.baidu.com/'
        }
        
        # 针对百度搜索的特殊请求头
        self.baidu_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://image.baidu.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': 'BAIDUID=' + ''.join(random.choice('0123456789ABCDEF') for _ in range(32)) + ':FG=1'
        }
        self.save_dir = save_dir
        self.max_threads = max_threads
        self.download_queue = queue.Queue()
        self.downloaded_hashes = set()  # 用于图片去重
        self.lock = threading.Lock()  # 用于线程安全操作
        self.classify_ships = classify_ships  # 是否自动分类船只类型
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 如果启用了船只分类，创建分类子目录
        if self.classify_ships:
            self.ship_types = [
                'cargo_ship',       # 货船
                'container_ship',   # 集装箱船
                'cruise_ship',      # 邮轮
                'tanker_ship',      # 油轮
                'bulk_carrier',     # 散货船
                'fishing_vessel',   # 渔船
                'yacht',            # 游艇
                'sailboat',         # 帆船
                'naval_ship',       # 军舰
                'other'             # 其他
            ]
            
            # 为每种船只类型创建子目录
            for ship_type in self.ship_types:
                type_dir = os.path.join(self.save_dir, ship_type)
                if not os.path.exists(type_dir):
                    os.makedirs(type_dir)
    
    def get_page_content(self, url, use_proxy=False, max_retries=3, headers=None):
        """
        获取网页内容
        :param url: 网页URL
        :param use_proxy: 是否使用代理
        :param max_retries: 最大重试次数
        :param headers: 自定义请求头，如果为None则使用默认请求头
        :return: 网页内容
        """
        # 使用自定义请求头或默认请求头
        request_headers = headers if headers else self.headers
        
        # 禁用代理设置，直接连接
        proxies = None
        if not use_proxy:
            proxies = {
                'http': None,
                'https': None
            }
        
        # 重试机制
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=request_headers, 
                    timeout=15,  # 增加超时时间
                    proxies=proxies,
                    verify=False,  # 禁用SSL验证，解决SSL连接问题
                    allow_redirects=True  # 允许重定向
                )
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"获取网页内容失败 (尝试 {attempt+1}/{max_retries}): {e}")
                # 随机等待时间，避免被识别为爬虫
                time.sleep(random.uniform(1.5, 3.5))  
        
        print(f"达到最大重试次数，无法获取网页内容: {url}")
        return None
    
    def search_images_via_search_engine(self, keyword, search_engine='google', max_pages=2):
        """
        通过搜索引擎搜索图片
        :param keyword: 搜索关键词
        :param search_engine: 搜索引擎 ('google', 'bing', 'baidu')
        :param max_pages: 最大搜索页数
        :return: 图片URL列表
        """
        image_urls = []
        
        if search_engine.lower() == 'google':
            base_url = 'https://www.google.com/search?q={}&tbm=isch&start={}'
        elif search_engine.lower() == 'bing':
            base_url = 'https://www.bing.com/images/search?q={}&first={}'
        elif search_engine.lower() == 'baidu':
            # 使用更完整的百度图片搜索URL格式，添加更多参数
            base_url = 'https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={}&pn={}&rn=30&gsm=3c&1={}'.format(
                '{}', '{}', int(time.time() * 1000))
            
            # 备用URL格式
            backup_url = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1{}&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word={}&pn={}'.format(
                int(time.time() * 1000), '{}', '{}')
            
            # 随机选择一个URL格式，增加多样性
            if random.random() > 0.5:
                base_url = backup_url
        else:
            print(f"不支持的搜索引擎: {search_engine}")
            return []
        
        for page in range(max_pages):
            if search_engine.lower() == 'baidu':
                start_idx = page * 30  # 百度每页约30张图片
            else:
                start_idx = page * 20  # Google和Bing每页约20张图片
                
            search_url = base_url.format(quote_plus(keyword), start_idx)
            
            print(f"搜索: {search_url}")
            # 根据搜索引擎选择不同的请求头
            if search_engine.lower() == 'baidu':
                html_content = self.get_page_content(search_url, use_proxy=False, max_retries=3, headers=self.baidu_headers)
            else:
                html_content = self.get_page_content(search_url, use_proxy=False, max_retries=3)
            
            if not html_content:
                continue
            
            # 提取图片URL
            try:
                if search_engine.lower() == 'google':
                    # Google图片搜索结果中的图片URL通常在JSON数据中
                    page_urls = self._extract_google_image_urls(html_content)
                    image_urls.extend(page_urls)
                    print(f"从Google搜索引擎获取了 {len(page_urls)} 张图片URL")
                elif search_engine.lower() == 'bing':
                    # Bing图片搜索结果
                    page_urls = self._extract_bing_image_urls(html_content)
                    image_urls.extend(page_urls)
                    print(f"从Bing搜索引擎获取了 {len(page_urls)} 张图片URL")
                elif search_engine.lower() == 'baidu':
                    # 百度图片搜索结果
                    page_urls = self._extract_baidu_image_urls(html_content)
                    image_urls.extend(page_urls)
                    print(f"从百度搜索引擎获取了 {len(page_urls)} 张图片URL")
            except Exception as e:
                print(f"从{search_engine}提取图片URL时出错: {e}")
            
            # 添加延时
            time.sleep(random.uniform(1.0, 3.0))
        
        return image_urls
    
    def _extract_google_image_urls(self, html_content):
        """
        从Google搜索结果中提取图片URL
        :param html_content: HTML内容
        :return: 图片URL列表
        """
        image_urls = []
        # 使用正则表达式查找图片URL
        pattern = r'"ou":"(https?://[^"]+)"'
        matches = re.findall(pattern, html_content)
        image_urls.extend(matches)
        
        return image_urls
    
    def _extract_bing_image_urls(self, html_content):
        """
        从Bing搜索结果中提取图片URL
        :param html_content: HTML内容
        :return: 图片URL列表
        """
        image_urls = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Bing图片搜索结果中的图片URL通常在murl属性中
        for img in soup.select('.iusc'):
            img_data = img.get('m')
            if img_data:
                try:
                    import json
                    img_data = json.loads(img_data)
                    if 'murl' in img_data:
                        image_urls.append(img_data['murl'])
                except Exception as e:
                    print(f"解析Bing图片数据失败: {e}")
        
        return image_urls
        
    def _extract_baidu_image_urls(self, html_content):
        """
        从百度搜索结果中提取图片URL
        :param html_content: HTML内容
        :return: 图片URL列表
        """
        image_urls = []
        
        try:
            # 百度图片搜索结果中的图片URL通常在JSON数据中
            # 使用正则表达式查找所有图片URL
            patterns = [
                # 缩略图URL
                r'"thumbURL":"(https?://[^"]+)"',
                # 高清图片URL
                r'"middleURL":"(https?://[^"]+)"',
                # 原图URL
                r'"objURL":"(https?://[^"]+)"',
                # 备用模式1
                r'"hoverURL":"(https?://[^"]+)"',
                # 备用模式2
                r'"replaceUrl":"(https?://[^"]+)"',
                # 备用模式3
                r'"src":"(https?://[^"]+\.(?:jpg|jpeg|png|gif))"',
                # 备用模式4 - 处理转义的URL
                r'"url":"(https?:\\u002F\\u002F[^"]+)"'
            ]
            
            # 尝试所有模式
            for pattern in patterns:
                urls = re.findall(pattern, html_content)
                # 处理转义的URL
                for url in urls:
                    if '\\u002F' in url:
                        # 将Unicode转义序列转换为实际字符
                        url = url.replace('\\u002F', '/')
                    image_urls.append(url)
            
            # 如果上述方法没有找到URL，尝试使用BeautifulSoup解析
            if not image_urls:
                soup = BeautifulSoup(html_content, 'html.parser')
                # 查找所有图片标签
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and src.startswith('http'):
                        image_urls.append(src)
            
            # 去重
            image_urls = list(set(image_urls))
            
            # 打印调试信息
            print(f"从百度提取到 {len(image_urls)} 个图片URL")
            if image_urls:
                print(f"示例URL: {image_urls[0][:100]}...")
                
        except Exception as e:
            print(f"提取百度图片URL时出错: {e}")
        
        return image_urls
    
    def parse_image_urls(self, html_content, url, img_keyword='ship'):
        """
        从HTML内容中解析图片URL
        :param html_content: HTML内容
        :param url: 原始网页URL
        :param img_keyword: 图片关键词
        :return: 图片URL列表
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        
        image_urls = []
        for img in img_tags:
            # 获取图片src属性
            img_url = img.get('src') or img.get('data-src') or img.get('data-original')
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
    
    def get_image_hash(self, img_data):
        """
        计算图片的哈希值，用于去重
        :param img_data: 图片二进制数据
        :return: 哈希值
        """
        try:
            # 打开图片
            img = Image.open(io.BytesIO(img_data))
            
            # 调整大小为8x8并转为灰度图
            img = img.resize((8, 8), Image.LANCZOS).convert('L')
            
            # 计算平均值
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            
            # 生成哈希值
            bits = ''.join('1' if pixel >= avg else '0' for pixel in pixels)
            hexadecimal = hex(int(bits, 2))[2:].zfill(16)
            
            return hexadecimal
        except Exception as e:
            print(f"计算图片哈希值失败: {e}")
            # 如果无法计算哈希值，则使用数据的MD5作为备选
            return hashlib.md5(img_data).hexdigest()
    
    def is_duplicate(self, img_hash):
        """
        检查图片是否重复
        :param img_hash: 图片哈希值
        :return: 是否重复
        """
        with self.lock:
            if img_hash in self.downloaded_hashes:
                return True
            self.downloaded_hashes.add(img_hash)
            return False
    
    def identify_ship_type(self, img_data):
        """
        识别船只类型
        :param img_data: 图片二进制数据
        :return: 船只类型
        """
        # 这里可以接入更复杂的图像识别模型
        # 简单实现：基于文件名和图片特征进行简单分类
        try:
            img = Image.open(io.BytesIO(img_data))
            width, height = img.size
            aspect_ratio = width / height
            
            # 基于长宽比和图片特征的简单分类
            if aspect_ratio > 3.5:  # 非常细长的船只可能是油轮或集装箱船
                return 'tanker_ship' if random.random() > 0.5 else 'container_ship'
            elif aspect_ratio > 2.5:  # 较长的船只可能是货船
                return 'cargo_ship'
            elif aspect_ratio < 1.5 and width > 800:  # 宽度大的船可能是邮轮
                return 'cruise_ship'
            elif width < 400 and height < 300:  # 小型船只可能是渔船或帆船
                return 'fishing_vessel' if random.random() > 0.5 else 'sailboat'
            else:
                # 随机分配其他类型
                return random.choice(['bulk_carrier', 'yacht', 'naval_ship', 'other'])
        except Exception as e:
            print(f"识别船只类型失败: {e}")
            return 'other'
    
    def download_worker(self):
        """
        下载工作线程
        """
        while True:
            try:
                # 从队列获取下载任务
                img_url, filename = self.download_queue.get(timeout=1)
                
                try:
                    # 下载图片，禁用代理，增加重试机制
                    max_retries = 3
                    retry_count = 0
                    success = False
                    
                    # 判断是否是百度图片URL
                    is_baidu_img = 'baidu' in img_url.lower() or 'bdimg' in img_url.lower()
                    download_headers = self.baidu_headers if is_baidu_img else self.headers
                    
                    # 为百度图片添加Referer
                    if is_baidu_img:
                        download_headers = download_headers.copy()
                        download_headers['Referer'] = 'https://image.baidu.com/'
                    
                    while retry_count < max_retries and not success:
                        try:
                            response = requests.get(
                                img_url, 
                                headers=download_headers, 
                                timeout=15, 
                                stream=True,
                                proxies=None,  # 禁用代理
                                verify=False,  # 禁用SSL验证
                                allow_redirects=True  # 允许重定向
                            )
                            response.raise_for_status()
                            success = True
                        except Exception as e:
                            retry_count += 1
                            if retry_count >= max_retries:
                                raise
                            print(f"下载重试 ({retry_count}/{max_retries}): {e}")
                            time.sleep(random.uniform(1.0, 2.5))  # 随机等待时间
                    
                    # 获取图片数据
                    img_data = response.content
                    
                    # 计算哈希值并检查是否重复
                    img_hash = self.get_image_hash(img_data)
                    
                    if not self.is_duplicate(img_hash):
                        # 如果启用了船只分类，识别船只类型
                        if self.classify_ships:
                            ship_type = self.identify_ship_type(img_data)
                            # 保存到对应的分类目录
                            save_dir = os.path.join(self.save_dir, ship_type)
                            file_path = os.path.join(save_dir, filename)
                        else:
                            file_path = os.path.join(self.save_dir, filename)
                        
                        # 保存图片
                        with open(file_path, 'wb') as f:
                            f.write(img_data)
                        
                        with self.lock:
                            print(f"图片下载成功: {file_path}")
                    else:
                        with self.lock:
                            print(f"跳过重复图片: {img_url}")
                
                except Exception as e:
                    with self.lock:
                        print(f"下载图片失败 {img_url}: {e}")
                
                finally:
                    # 标记任务完成
                    self.download_queue.task_done()
            
            except queue.Empty:
                # 队列为空，退出线程
                break
    
    def start_download_threads(self):
        """
        启动下载线程
        """
        threads = []
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.download_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        return threads
    
    def add_download_task(self, img_url, filename=None):
        """
        添加下载任务到队列
        :param img_url: 图片URL
        :param filename: 文件名
        """
        if not filename:
            filename = os.path.basename(img_url).split('?')[0]
            if not filename or '.' not in filename:
                filename = f"ship_{int(time.time())}_{random.randint(1000, 9999)}.jpg"
        
        self.download_queue.put((img_url, filename))
    
    def crawl_website(self, url, max_images=20, img_keyword='ship'):
        """
        爬取指定网站上的船只图片
        :param url: 网页URL
        :param max_images: 最大下载图片数量
        :param img_keyword: 图片关键词
        :return: 添加到下载队列的图片数量
        """
        print(f"开始爬取网站: {url}")
        
        # 获取网页内容
        html_content = self.get_page_content(url)
        if not html_content:
            return 0
        
        # 解析图片URL
        image_urls = self.parse_image_urls(html_content, url, img_keyword)
        print(f"在 {url} 找到 {len(image_urls)} 张潜在的船只图片")
        
        # 添加到下载队列
        count = 0
        for img_url in image_urls:
            if count >= max_images:
                break
            
            self.add_download_task(img_url)
            count += 1
        
        return count
    
    def crawl_search_engine(self, keyword, max_images=50, search_engine='google'):
        """
        通过搜索引擎爬取船只图片
        :param keyword: 搜索关键词
        :param max_images: 最大下载图片数量
        :param search_engine: 搜索引擎
        :return: 添加到下载队列的图片数量
        """
        print(f"开始从{search_engine}搜索: {keyword}")
        
        # 搜索图片
        image_urls = self.search_images_via_search_engine(
            keyword, search_engine=search_engine, max_pages=max(1, max_images // 20)
        )
        
        print(f"从{search_engine}找到 {len(image_urls)} 张潜在的船只图片")
        
        # 添加到下载队列
        count = 0
        for img_url in image_urls:
            if count >= max_images:
                break
            
            self.add_download_task(img_url)
            count += 1
        
        return count
    
    def crawl(self, websites=None, search_keywords=None, max_images_per_source=20):
        """
        爬取船只图片
        :param websites: 网站列表
        :param search_keywords: 搜索关键词列表
        :param max_images_per_source: 每个来源最大下载图片数量
        :return: 总下载任务数
        """
        # 默认值
        if websites is None:
            websites = [
                'https://www.marinetraffic.com',
                'https://www.vesselfinder.com',
                'https://www.ship-technology.com',
            ]
        
        if search_keywords is None:
            search_keywords = [
                'cargo ship',
                'container ship',
                'cruise ship',
                'tanker ship',
                'bulk carrier ship',
            ]
        
        # 启动下载线程
        threads = self.start_download_threads()
        
        total_tasks = 0
        
        # 爬取网站
        for website in websites:
            try:
                count = self.crawl_website(website, max_images=max_images_per_source, img_keyword='ship')
                total_tasks += count
                time.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                print(f"爬取 {website} 时出错: {e}")
        
        # 通过搜索引擎爬取
        for keyword in search_keywords:
            try:
                # 使用Google搜索
                count = self.crawl_search_engine(
                    keyword, max_images=max_images_per_source, search_engine='google'
                )
                total_tasks += count
                time.sleep(random.uniform(3.0, 5.0))
                
                # 使用Bing搜索
                count = self.crawl_search_engine(
                    keyword, max_images=max_images_per_source, search_engine='bing'
                )
                total_tasks += count
                time.sleep(random.uniform(3.0, 5.0))
            except Exception as e:
                print(f"搜索 {keyword} 时出错: {e}")
        
        # 等待所有下载任务完成
        self.download_queue.join()
        
        print(f"爬取完成，总共添加了 {total_tasks} 个下载任务")
        print(f"实际下载了 {len(self.downloaded_hashes)} 张不重复的船只图片")
        
        return len(self.downloaded_hashes)


def main():
    # 创建高级爬虫实例，启用船只分类功能
    crawler = AdvancedShipCrawler(save_dir='./advanced_ships', max_threads=5, classify_ships=True)
    
    # 自定义网站和搜索关键词
    websites = [
        'https://www.marinetraffic.com',
        'https://www.vesselfinder.com',
        'https://www.ship-technology.com',
        'https://www.wartsila.com/marine',
        'https://www.naval-technology.com',
    ]
    
    search_keywords = [
        'cargo ship',
        'container ship',
        'cruise ship',
        'tanker ship',
        'bulk carrier ship',
        '货轮',  # 中文关键词
        '邮轮',
    ]
    
    # 开始爬取，添加百度搜索引擎
    crawler.crawl(websites=websites, search_keywords=search_keywords, max_images_per_source=10)
    
    # 使用百度搜索引擎进行额外搜索
    print("开始使用百度搜索引擎进行额外搜索...")
    # crawl_search_engine方法接受单个关键词，而不是关键词列表
    for keyword in search_keywords:
        crawler.crawl_search_engine(keyword, max_images=10, search_engine='baidu')


if __name__ == "__main__":
    main()