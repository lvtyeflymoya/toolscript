# 船只图片爬虫

这是一个用于爬取网络上船只图片的Python脚本。该脚本可以从指定的网站上搜索并下载与船只相关的图片。

## 本地测试

在开始使用前，您可以运行以下测试脚本来验证环境配置：

```bash
python test_environment.py  # 检查环境配置
python local_test_crawler.py  # 生成本地测试图片
```

这些测试脚本将检查所有依赖项是否正确安装，并生成一些本地测试图片，无需依赖网络连接。

## 功能特点

### 基础版本 (ship_image_crawler.py)

- 支持多个网站爬取
- 根据关键词筛选相关图片
- 自动将相对路径转为绝对路径
- 添加随机延时，避免请求过于频繁
- 错误处理和日志输出

### 高级版本 (advanced_ship_crawler.py)

- 支持搜索引擎爬取 (Google, Bing, 百度)
- 多线程并行下载
- 图片去重功能
- 支持中英文关键词搜索
- 更强大的图片URL提取能力
- 船只类型自动分类功能

### 本地测试版本 (local_test_crawler.py)

- 生成本地测试图片，无需网络连接
- 创建纯色背景图片和简单船只轮廓图片
- 模拟真实爬取过程，添加随机延时
- 用于验证环境配置和依赖安装

## 依赖安装

在使用该脚本前，请确保已安装所需的Python库：

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install requests beautifulsoup4 Pillow
```

## 使用方法

### 基础版本

1. 直接运行脚本：

```bash
python ship_image_crawler.py  # 网络模式，从网站下载图片
python ship_image_crawler.py --local  # 本地测试模式，生成本地测试图片
```

2. 命令行参数：

```bash
# 使用本地测试模式
python ship_image_crawler.py --local

# 指定每个网站最大下载图片数量
python ship_image_crawler.py --max-images 10

# 指定图片保存目录
python ship_image_crawler.py --save-dir ./my_ship_images

# 组合使用多个参数
python ship_image_crawler.py --local --max-images 15 --save-dir ./test_ships
```

3. 或者在你的Python代码中导入并使用：

```python
from ship_image_crawler import ShipImageCrawler

# 创建爬虫实例（网络模式）
crawler = ShipImageCrawler(save_dir='./my_ship_images')

# 创建爬虫实例（本地测试模式）
# crawler = ShipImageCrawler(save_dir='./my_ship_images', local_test_mode=True)

# 爬取指定网站的船只图片
crawler.crawl('https://www.example.com', max_images=20, img_keyword='ship')
```

### 高级版本

1. 直接运行脚本：

```bash
python advanced_ship_crawler.py
```

2. 或者在你的Python代码中导入并使用：

```python
from advanced_ship_crawler import AdvancedShipCrawler

# 创建高级爬虫实例，启用船只自动分类功能
crawler = AdvancedShipCrawler(save_dir='./my_advanced_ships', max_threads=5, classify_ships=True)

# 自定义爬取参数
websites = ['https://www.example1.com', 'https://www.example2.com']
search_keywords = ['cargo ship', 'cruise ship', '货轮']

# 开始爬取
crawler.crawl(websites=websites, search_keywords=search_keywords, max_images_per_source=10)

# 使用百度搜索引擎进行额外搜索
for keyword in search_keywords:
    crawler.crawl_search_engine(keyword, max_images=10, search_engine='baidu')
```

### 本地测试版本

如果您遇到网络连接问题，可以使用以下两种方式运行本地测试：

1. 使用专门的本地测试脚本：

```bash
python local_test_crawler.py
```

这将在 `local_test_images` 目录中生成10张测试图片，包括纯色背景图片和简单的船只轮廓图片。

2. 使用基础爬虫的本地测试模式：

```bash
python ship_image_crawler.py --local
```

这将使用与基础爬虫相同的流程，但不进行网络请求，而是生成本地测试图片。这种方式的优点是可以测试完整的爬虫流程，包括多网站处理、关键词筛选等功能，而不依赖网络连接。

本地测试模式生成的图片包括：
- 纯色背景的随机图片
- 带有简单船只轮廓的图片

## 自定义配置

### 基础版本

你可以通过修改脚本中的以下参数来自定义爬虫行为：

- `save_dir`：图片保存目录
- `max_images`：每个网站最大下载图片数量
- `img_keyword`：图片关键词，用于筛选相关图片
- `websites`：要爬取的网站列表

### 高级版本

高级版本提供了更多自定义选项：

- `save_dir`：图片保存目录
- `max_threads`：最大下载线程数
- `classify_ships`：是否启用船只类型自动分类功能
- `max_images_per_source`：每个来源最大下载图片数量
- `search_keywords`：搜索关键词列表，支持中英文
- `websites`：要爬取的网站列表
- `search_engines`：搜索引擎选择列表 ('google', 'bing', 'baidu')

## 注意事项

1. 请遵守网站的robots.txt规则和使用条款
2. 不要过于频繁地请求同一网站，以免被封IP
3. 下载的图片可能受版权保护，请确保你有权使用这些图片
4. 某些网站可能需要更复杂的爬取策略，如处理JavaScript渲染的内容、验证码等
5. 网络连接问题处理：
   - 如果遇到SSL连接错误或代理问题，可以使用 `--local` 参数运行本地测试模式
   - 对于实际网络爬取，可能需要配置代理服务器或解决SSL证书问题
   - 在某些网络环境下，可能需要使用VPN或代理服务
6. 如果您只想测试程序功能而不关心实际爬取结果，强烈建议使用本地测试模式

## 进阶功能

高级版本已实现以下功能：

- 多线程并行下载
- 图片去重（使用感知哈希算法）
- 搜索引擎爬取（Google、Bing、百度）
- 支持中英文关键词
- 船只类型自动分类（基于图片特征）

如需更强大的功能，可以考虑进一步扩展：

- 代理IP轮换
- 验证码识别
- 支持更多搜索引擎（如Yandex、DuckDuckGo等）
- 图片质量评估和筛选
- 改进船只类型分类（使用深度学习模型）
- 定时任务和增量爬取
- 船只特征提取和分析