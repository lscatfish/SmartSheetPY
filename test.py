import os.path
from pathlib import Path
import hashlib

from SSPY.myff import BASE_DIR
from SSPY.myff.base import calculate_file_hash,BaseFolder
from SSPY.mydocx import DocxLoad
from SSPY.mypdf import PdfLoad
from SSPY.helperfunction import all_str

f=BaseFolder('D:/code/SmartSheetPY/SSPY')
print(f.all_filepaths)
print(f.children_paths)
print(hashlib.md5(''.encode('utf-8')).hexdigest())
d=DocxLoad(
    r'D:\code\SmartSheetPY\input\sign_for_QingziClass\自主报名-丁晔\自主报名—丁晔—青书班.docx',
    if_print = True,parse_paragraphs = True)
print(d.sheets)
print(d.paragraphs)
# p=PdfLoad(r"D:\code\SmartSheetPY\input\sign_for_QingziClass\校团委组织部-青峰、组、书班班委+联络人推荐\校团委组织部-青书班班委推荐\组织推荐班委-刘禹初.pdf",
# False,True)
# print(all_str(p.sheets))
# print(all_str(p.pages))
a={1:2,3:4,5:6}
b={2:3,5:0}
a.update(b)
print(a)
from SSPY.myff.document.word import DirectDocxParser
ddd=DirectDocxParser(r'D:\code\SmartSheetPY\input\sign_for_QingziClass\自主报名-丁晔\自主报名—丁晔—青书班.docx')
print(ddd.sheets())
print(ddd.paragraphs())