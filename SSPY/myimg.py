"""此文件用于解析签到照片"""
import copy
import os

from bs4 import BeautifulSoup
from paddleocr import TableRecognitionPipelineV2
import PIL.Image
from .PersonneInformation import DefPerson
from .globalconstants import GlobalConstants as gc


def html_to_list(html_str: str) -> list[list[str]]:
    """
    将任意复杂 HTML 表格（含 rowspan / colspan / thead / tbody / tfoot / 嵌套表）解析为
    二维字符串列表：List[List[str]]。

    优化要点
    1. 自动扩展行数，防止 rowspan 越界；
    2. 支持 thead/tbody/tfoot 等多层 <tr>；
    3. 移除嵌套表格，避免文本污染；
    4. 单元格文本保留空格分隔，防止单词粘连；
    5. 全程只读不抛异常，非法 HTML 返回空表。
    """
    if not html_str or not isinstance(html_str, str):
        return []

    # ------------------------------------------------------------------ 解析 HTML
    try:
        soup = BeautifulSoup(html_str, "html.parser")
    except Exception as e:
        print(f"[html_to_list] HTML 解析失败: {e}")
        return []

    table = soup.find("table")
    if not table:
        print("[html_to_list] 未找到 <table> 标签")
        return []

    # ------------------------------------------------------------------ 收集所有行与单元格
    rows = []  # 每个元素对应一行，存放单元格 dict 列表
    for tr in table.select("tr"):  # select 会跨 thead/tbody/tfoot 找全部 tr
        row_cells = []
        for td in tr.find_all(["td", "th"]):
            # 丢弃嵌套表格，防止文本重复
            for nested in td.find_all("table"):
                nested.decompose()

            text = td.get_text(strip = True, separator = "") or ""  # 防止 None
            rowspan = max(1, int(td.get("rowspan", 1)))
            colspan = max(1, int(td.get("colspan", 1)))
            row_cells.append({"text": text, "rowspan": rowspan, "colspan": colspan})
        if row_cells:  # 跳过空行
            rows.append(row_cells)

    if not rows:
        return []

    # ------------------------------------------------------------------ 计算真实列数
    max_cols = max(sum(cell["colspan"] for cell in r) for r in rows)

    # ------------------------------------------------------------------ 计算真实行数（考虑 rowspan 溢出）
    max_rows = len(rows)
    for r_idx, row in enumerate(rows):
        for cell in row:
            max_rows = max(max_rows, r_idx + cell["rowspan"])

    # ------------------------------------------------------------------ 初始化二维表与占用标记
    table_list = [["" for _ in range(max_cols)] for _ in range(max_rows)]
    filled = [[False for _ in range(max_cols)] for _ in range(max_rows)]

    # ------------------------------------------------------------------ 填充单元格
    for r_idx, row in enumerate(rows):
        c_idx = 0
        for cell in row:
            # 找到第一个未被占用的列
            while c_idx < max_cols and filled[r_idx][c_idx]:
                c_idx += 1
            if c_idx >= max_cols:
                break

            # 跨行跨列填充
            for dr in range(cell["rowspan"]):
                for dc in range(cell["colspan"]):
                    nr, nc = r_idx + dr, c_idx + dc
                    if nr < max_rows and nc < max_cols:
                        table_list[nr][nc] = cell["text"]
                        filled[nr][nc] = True
            c_idx += cell["colspan"]
    from .myxlsx import clear_empty_lines
    return clear_empty_lines(table_list)


class PPOCRImgByModel:
    """进行ppocr img，所有解析方式全部采用模型"""

    def __init__(self):
        """加载模型"""
        print('加载ppocr的模型')
        self.__pipeline = TableRecognitionPipelineV2(
            use_doc_orientation_classify = True,
        )
        self.__output = None
        self.__sheet: list[list[str]] = []
        self.__isOK = False
        print('ppocr模型加载完毕!!!')

    def predict(self, path, clear: bool = False):
        self.__isOK = False
        if clear: self.__sheet = []
        import numpy
        if not os.path.exists(path):
            print('\"' + path + '\" 不存在')
            return False
        pil_img = PIL.Image.open(path).convert('RGB')
        img_np = numpy.array(pil_img)
        self.__output = self.__pipeline.predict(img_np)
        if self.__output is None:
            return False
        self.__isOK = True
        self.__sheet.extend(html_to_list(self.html_this))
        return True

    @property
    def result_this(self):
        """只能获取到本次的内容"""
        if self.__isOK:
            return copy.deepcopy(self.__output)
        else:
            return None

    @property
    def html_this(self):
        """只能获取到本次的内容"""
        if self.__isOK:
            return self.__output[0]['table_res_list'][0]['pred_html']
        else:
            return None

    @property
    def sheet_all(self) -> list[list[str]] | None:
        """可以获取到多次内容"""
        if self.__isOK:
            return copy.deepcopy(self.__sheet)
        else:
            return None

    def get_personList(self, classname: str, if_fuzzy = False) -> list[DefPerson]:
        """
        输出为人员列表
        Parameters:
            if_fuzzy (bool):是否启用键的部分检索
            classname (str):班级
        Return:
            返回人员列表
        """
        pers: list[DefPerson] = []
        if not self.__isOK: return pers
        from .myxlsx import get_header_from_xlsx, trans_list_to_person
        header, sheet = get_header_from_xlsx(self.sheet_all)

        for row in sheet:
            pers.append(
                trans_list_to_person(
                    header = header,
                    in_info = row,
                    if_fuzzy = if_fuzzy,
                    classname = classname))
        self.__sheet = []
        return pers
