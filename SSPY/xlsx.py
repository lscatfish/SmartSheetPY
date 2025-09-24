"""
这是用于解析xlsx文件的py文件
"""
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Side, Border, Alignment
from globalconstants import GlobalConstants as gc


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

    def __init__(self, _path: str):
        self.__path = _path
        self.__sheet = []
        self.__load()

    def __load(self):
        """读取文件"""
        print('xlsx文件读取\"' + self.__path + '\"', end = '')
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


class XlsxWrite:
    """xlsx写文件"""

    def __init__(
        self,
        path: str = None,
        sheet: list = None,
        title: str = '',
        widths: list = None,
        heights: int = None,
        font_regular: Font = gc.fontRegularGBK,
        font_title: Font = gc.fontTitleGBK,
        font_header: Font = gc.fontHeaderGBK,
        border: Border = gc.borderThinBlack,
        has_border: bool = False,
        has_title: bool = False,
        has_header: bool = False,
        alignment: Alignment = gc.alignmentStd,
    ):
        """
        Parameters
        --------
        path : str
            路径
        sheet : list
            表格
        title : str
            标题的名称
        widths : list
            列宽的组合
        heights : int
            行高
        font_regular: Font
            正文字体
        font_title: Font
            标题字体
        font_header: Font
            表头字体
        border: Border
            单元格边框
        has_border: bool
            是否加边框
        has_title: bool
            是否有标题
        has_header: bool
            是否有表头
        alignment: Alignment
            对齐方式
        """
        self.__path = path
        self.__sheet = sheet
        self.__title = title
        self.__fontRegular = font_regular
        self.__fontTitle = font_title
        self.__border = border
        self.__hasBorder = has_border
        self.__hasTitle = has_title
        self.__alignment = alignment
        self.__hasTitle = has_title
        self.__hasHeader = has_header
        self.__fontHeader = font_header
        self.__widths = widths
        self.__heights = heights

    def can_write(self) -> bool:
        """检查能否开始写入表格"""
        if self.__path is None: return False
        if self.__sheet is None: return False
        if self.__title == '' and self.__hasTitle: return False
        return True

    def write(self) -> bool:
        """写入文件"""
        if not self.can_write(): return False
        # 创建wb
        wb = Workbook()
        ws = wb.active
        if self.__hasTitle: ws.title = self.__title
        for row in self.__sheet:
            ws.append(row)

        wb.save(self.__path)
        ws.close()
        wb.close()
        return True
