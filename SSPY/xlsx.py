"""
这是用于解析xlsx文件的py文件
"""
from openpyxl import load_workbook, Workbook


# # 加载工作簿（read_only=True 适合大文件，提升性能）
# wb = load_workbook(r"D:\code\SmartSheetPY\青峰班.xlsx", True, True)
# # data_only=True 表示读取单元格计算后的值，而非公式
#
# # 获取所有工作表名称
# print(wb.sheetnames)  # 输出: ['Sheet1', 'Sheet2']
# sns = wb.sheetnames
#
# # 选择工作表
# sheet = wb[sns[0]]  # 通过名称选择
#
# # 获取工作表维度（数据范围）
# # print(sheet.dimensions)  # 输出: A1:C5
# # 读取单元格
# cell = sheet['A1']
# print(f"单元格值: {cell.value}")
# print(f"单元格坐标: {cell.coordinate}")
# print(f"行号: {cell.row}, 列号: {cell.column}")
# # 按行读取数据
# for row in sheet.iter_rows( values_only = True):
#     for cell in row:
#         if cell is not None:print(cell)
#         else:print("i")
# # 关闭工作簿
# wb.close()

class XlsxLoad:
    """读取xlsx文件的类"""

    def __init__(self, _path):
        self.__path = _path
        self.__sheet = []
        self.__load()

    def __load(self):
        """读取文件"""
        print('xlsx文件读取\"'+self.__path+'\"',end = '')
        wb = load_workbook(self.__path)
        wb = load_workbook(self.path, data_only = True, read_only = True)
        ws = wb.worksheets[0]
        for row in ws.iter_rows(values_only = True):  # 遍历全部
            self.__sheet.append(row)
        ws.close()
        wb.close()
        print(' - Done!')

    @property
    def path(self):
        """返回文件路径"""
        return self.__path

    @property
    def sheet(self):
        """返回解析到的sheet"""
        return self.__sheet
