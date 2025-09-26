from SSPY.mypdf import PdfLoad

a = PdfLoad('./组织推荐班委-李炘宇.pdf', table_only = True)
s = a.sheets
print(s)
input()
