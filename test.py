import os.path
from pathlib import Path

from SSPY.myff import BASE_DIR
from SSPY.myff.base import calculate_file_hash,BaseFolder

f=BaseFolder('D:/code/SmartSheetPY/SSPY')
print(f.all_filepaths)
print(f.children_paths)