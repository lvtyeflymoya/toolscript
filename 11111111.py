import shutil

src_path = r"D:\Anaconda\envs\anomalib_env\Lib\site-packages\torch"
tar_path = r"D:\Anaconda\envs\tsai\Lib\site-packages\torch"

shutil.copytree(src_path, tar_path)