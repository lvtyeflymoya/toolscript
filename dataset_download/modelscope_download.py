 #数据集下载
from modelscope.msdatasets import MsDataset
download_path = "E:/Dataset/OCR"
ds =  MsDataset.load('yuwenbonnie/ParaCAD-Dataset',
                    subset_name='default', 
                    split='validation',
                    cache_dir=download_path)
#您可按需配置 subset_name、split，参照“快速使用”示例代码