from SSPY.myfolder import DefFolder
from SSPY.mypdf import PdfLoad
from SSPY import parseperson
from SSPY.globalconstants import GlobalConstants as gc

# a = PdfLoad('./组织推荐班委-李炘宇.pdf', table_only = True)
# s = a.sheets
# print(s)
# input()

f=DefFolder(gc.dir_INPUT_)
print(f.get_filenames_by(['.pdf','docx']))