from SSPY.myfolder import DefFolder
from SSPY.mypdf import PdfLoad
from SSPY import parseperson
from SSPY.globalconstants import GlobalConstants as gc
from SSPY.parseperson import get_header_from_sheet


# 使用示例
# if __name__ == "__main__":
#
#
#     test_sheet = [
#         ["无效行1", "内容"],
#         ["姓名", "年龄", "性别"],  # 这行会被识别为表头
#         ["张三", "20", "男"],
#         ["李四", "25", "女"]
#     ]
#
#     header, sheet_without_header = get_header_from_sheet(test_sheet)
#     print("表头:", header)  # 输出：('姓名', '年龄', '性别')
#     print("去除表头后的内容:", sheet_without_header)