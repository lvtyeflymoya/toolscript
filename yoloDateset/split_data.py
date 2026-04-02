import os, shutil, random
random.seed(0)
import numpy as np
# from sklearn.model_selection import train_test_split

# 数据集划分比例
val_size = 0.2
test_size = 0.1

# 输入路径
postfix = 'png'
imgpath = r'E:\work\drawing_analysis\dataset\obb_all_graphes\annotation'
txtpath = r'E:\work\drawing_analysis\dataset\obb_all_graphes\annotation\ab_af_c_c_d_a_labels'

# 输出路径
output_dir = r'E:\work\drawing_analysis\dataset\obb_all_graphes\ab_af_c_c_d_a_anno'

# 创建输出目录
os.makedirs(f'{output_dir}/images/train', exist_ok=True)
os.makedirs(f'{output_dir}/images/val', exist_ok=True)
os.makedirs(f'{output_dir}/images/test', exist_ok=True)
os.makedirs(f'{output_dir}/labels/train', exist_ok=True)
os.makedirs(f'{output_dir}/labels/val', exist_ok=True)
os.makedirs(f'{output_dir}/labels/test', exist_ok=True)

listdir = np.array([i for i in os.listdir(txtpath) if 'txt' in i])
random.shuffle(listdir)
train, val, test = listdir[:int(len(listdir) * (1 - val_size - test_size))], listdir[int(len(listdir) * (1 - val_size - test_size)):int(len(listdir) * (1 - test_size))], listdir[int(len(listdir) * (1 - test_size)):]
print(f'train set size:{len(train)} val set size:{len(val)} test set size:{len(test)}')

for i in train:
    shutil.copy('{}/{}.{}'.format(imgpath, i[:-4], postfix), f'{output_dir}/images/train/{i[:-4]}.{postfix}')
    shutil.copy('{}/{}'.format(txtpath, i), f'{output_dir}/labels/train/{i}')

for i in val:
    shutil.copy('{}/{}.{}'.format(imgpath, i[:-4], postfix), f'{output_dir}/images/val/{i[:-4]}.{postfix}')
    shutil.copy('{}/{}'.format(txtpath, i), f'{output_dir}/labels/val/{i}')

for i in test:
    shutil.copy('{}/{}.{}'.format(imgpath, i[:-4], postfix), f'{output_dir}/images/test/{i[:-4]}.{postfix}')
    shutil.copy('{}/{}'.format(txtpath, i), f'{output_dir}/labels/test/{i}')