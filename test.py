import os.path

from SSPY.myfile import BASE_DIR
from SSPY.myfile.file import calculate_file_hash
print(BASE_DIR)
print(os.path.relpath(r'D:\code\SmartSheetPY\SSPY\hijack\\', BASE_DIR))
print(calculate_file_hash(r"D:\code\SmartSheetPY\output\sign_for_QingziClass_out\committee\青社班\组织推荐-安丁树-20250075\安丁树-20250075(4).docx",'md5'))
print(calculate_file_hash(r"D:\code\SmartSheetPY\output\sign_for_QingziClass_out\committee\青社班\组织推荐-安丁树-20250075\安丁树-20250075(3).docx",'md5'))