import os.path
from pathlib import Path

from SSPY.myff import BASE_DIR
from SSPY.myff.base import calculate_file_hash
print(BASE_DIR)
print(os.path.relpath(r'D:\code\SmartSheetPY\SSPY\hijack\\', BASE_DIR))
print(os.listdir(r'D:\code\SmartSheetPY\SSPY\myff\crtl_path.py'))
print(os.path.abspath((Path(r'D:\code\SmartSheetPY\SSPY\myff\crtl_path.py'))))