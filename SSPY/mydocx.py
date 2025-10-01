import copy
from docx.oxml.ns import qn


class DocxLoad:
    """解析docx文件"""

    def __init__(self, _path: str = None):
        """
        Args:
            _path: 文件路径
        """
        self.__path = _path
        self.__sheets = []
        if self.__path is not None:
            self.__sheets = self.parse_docx_tables(self.__path)

    @staticmethod
    def get_merge_info(cell):
        """判断合并的cell"""
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()

        # 水平合并信息（跨列数）
        gridSpan = tcPr.find(qn('w:gridSpan'))
        horizontal_span = int(gridSpan.get(qn('w:val'))) if gridSpan is not None else 1

        # 垂直合并信息（是否为合并起始点）
        vMerge = tcPr.find(qn('w:vMerge'))
        is_vertical_start = False
        if vMerge is not None:
            v_merge_val = vMerge.get(qn('w:vMerge'))  # 注意这里修正了原代码的属性名错误
            is_vertical_start = (v_merge_val == 'restart')

        return (horizontal_span > 1, horizontal_span, is_vertical_start)

    @staticmethod
    def parse_docx_tables(file_path: str):
        """解析Word表格，处理合并单元格，返回[[行1内容], [行2内容], ...]"""
        from docx import Document
        doc = Document(file_path)
        all_tables = []

        for table in doc.tables:
            table_data = []
            # 记录已处理的单元格位置，避免重复添加
            processed = set()

            for row_idx, row in enumerate(table.rows):
                row_data = []
                for col_idx, cell in enumerate(row.cells):
                    # 如果该单元格已被合并处理过，跳过
                    if (row_idx, col_idx) in processed:
                        continue

                    content = cell.text.strip()
                    row_data.append(content)

                    # 获取合并信息
                    is_horizontal, span, is_vertical = DocxLoad.get_merge_info(cell)

                    # 标记水平合并的单元格为已处理
                    if is_horizontal:
                        for i in range(1, span):
                            processed.add((row_idx, col_idx + i))

                    # 垂直合并暂不处理（如需完整处理需更复杂逻辑，此处只保证水平去重）

                table_data.append(row_data)

            all_tables.append(table_data)
        return all_tables

    @property
    def sheets(self) -> list[list[list]]:
        return copy.deepcopy(self.__sheets)

    @property
    def sheets_without_enter(self) -> list[list[list]]:
        from .helperfunction import clean_enter
        outs = clean_enter(self.__sheets)
        return outs

    @property
    def path(self):
        return self.__path

    def get_sheet(self, index = None):
        """从文件中按照index内容读取一个表格"""
        from .helperfunction import check_value
        if isinstance(index, int):
            if len(self.__sheets) > index:
                return copy.deepcopy(self.__sheets[index])
        if isinstance(index, str):  # 按照关键值查找sheet
            for sheet in self.__sheets:
                if check_value(in_list = sheet, target_value = index, part = False): return copy.deepcopy(sheet)
        if isinstance(index, list):
            ind = copy.deepcopy(index)
            for sheet in self.__sheets:
                if check_value(in_list = sheet, target_value = ind, part = True): return copy.deepcopy(sheet)
        return None

    def get_sheet_without_enter(self, index = None) -> list[list] | None:
        """从文件中按照index内容读取一个表格"""
        from .helperfunction import clean_enter
        outs = clean_enter(self.get_sheet(index = index))
        if isinstance(outs, list):
            return outs
        else:
            return None
