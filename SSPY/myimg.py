"""此文件用于解析签到照片"""
import copy
import os
import threading

from bs4 import BeautifulSoup
from paddleocr import TableRecognitionPipelineV2
import PIL.Image

from .PersonneInformation import DefPerson
from .globalconstants import GlobalConstants as gc
from SSPY.helperfunction import _exit
from SSPY.tracker.core import VariableType, monitor_variables, get_current_monitor


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


def rotation_checklist_content(table: list[list[str]], header: list[str]) -> list[list[str]]:
    """
    检查表格中的内容，然后对齐表格的格式
    Parameters:
        header: 表头
        table:输入的表格
    Returns:返回修正的新表
    """
    """关键检查方式：序号只能是数字，学号检测"""
    from .PersonneInformation import is_studentID
    out_table = []

    for row in table:
        is_problem = False
        """此行是否有问题"""
        idx_stID_header = -1
        """表头的索引"""
        idx_stID_row = -1
        """row的索引"""
        for i in range(min(len(row), len(header))):
            if header[i] == gc.chstrStudentID:
                if not is_studentID(row[i]):  # 说明此行有问题
                    idx_stID_header = i
                    for j in range(len(row)):
                        if j == i: continue
                        if is_studentID(row[j]): idx_stID_row = j
                    is_problem = True
                    break
        if is_problem:
            if idx_stID_header >= 0 and idx_stID_row >= 0:
                start = idx_stID_row - len(row)
                end = idx_stID_row
                step = idx_stID_header - idx_stID_row
                new_row = copy.deepcopy(row)
                for i in range(start, end):
                    new_row[step + i] = row[i]
                out_table.append(new_row)
        else:
            out_table.append(row)
    return out_table


class PPOCRImgByModel:
    """进行ppocr img，所有解析方式全部采用模型"""
    config = 'table_recognition_v2'

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None
    )
    def __init__(self, paddlex_config: str = None, stop_flag: threading.Event = None):
        """加载模型
        Parameters:
            paddlex_config:自主配置的yaml文件路径
            stop_flag:终止标志
        """
        self.__stopFlag = stop_flag  # 一定要提前加载
        from .communitor.core import get_response
        print('加载ppocr的模型')
        # 这个模型就是一坨
        # 这里使用本地时会有bug：https://github.com/PaddlePaddle/PaddleOCR/issues/16606
        # doc_orientation_classify_model_name = 'PP-LCNet_x1_0_doc_ori'，这个模型会被加载两遍
        # 这里使用的是PPstructureV3的子产线TableRecognitionPipelineV2
        # 我们不推荐在class构造的时候导入地址，如需导入模型，请使用table_recognition_v2的yaml文件
        """
            # 你可以通过以下代码来输出默认的yaml配置文件
            from paddleocr import TableRecognitionPipelineV2
            pipeline = TableRecognitionPipelineV2()
            pipeline.export_paddlex_config_to_yaml("TableRecognitionPipelineV2.yaml")
        """
        if paddlex_config is not None:
            PPOCRImgByModel.config = paddlex_config

        unps = PPOCRImgByModel._models_unexist()
        if len(unps) > 0:
            reps = get_response(('ppocr_model_dir_unexist', unps))
            if reps == 'exit' or reps == 'exit-error' or ('exit' in reps):
                return
        if _exit(stop_flag): return

        self.__pipeline = TableRecognitionPipelineV2(
            paddlex_config = None if paddlex_config is None else paddlex_config,
        )

        # 预加载模型：用一张空图触发首次predict，强制加载所有模型
        self.__preload_model()

        self.__output = None
        self.__sheet: list[list[str]] = []
        self.__isOK = False
        print('ppocr模型加载完毕!!!\n')


    def __preload_model(self):
        """预加载模型，避免首次predict时加载"""
        try:
            # 创建一张1x1的空图（RGB模式）
            import numpy as np
            # 创建一张合理尺寸的空白图像（如 200x200 像素，RGB通道）
            empty_img = np.ones((200, 200, 3), dtype = np.uint8) * 255  # 白色图像
            self.__pipeline.predict(input = empty_img)
            print("模型预加载完成")
        except Exception as e:
            print(f"预加载模型失败：{e}")


    def predict(self, path, clear: bool = False):
        self.__isOK = False
        if clear: self.__sheet.clear()
        import numpy
        if not os.path.exists(path):
            print('\"' + path + '\" 不存在')
            return False
        pil_img = PIL.Image.open(path).convert('RGB')
        img_np = numpy.array(pil_img)
        self.__output = self.__pipeline.predict(input = img_np)
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

    def get_personList(self, classname: str, if_fuzzy = False, ifp = False) -> list[DefPerson]:
        """
        输出为人员列表
        Parameters:
            ifp: 是否打印解析出的sheet
            if_fuzzy (bool):是否启用键的部分检索
            classname (str):班级
        Return:
            返回人员列表
        """
        pers: list[DefPerson] = []
        if not self.__isOK: return pers
        from .myxlsx import get_header_from_xlsx, trans_list_to_person

        header, sheet = get_header_from_xlsx(self.sheet_all)
        ok_sheet = rotation_checklist_content(sheet, header)
        if ifp:
            print(classname + 'ocr结果')
            print(header)
            for row in ok_sheet:
                print(row)
            print('\n')

        for row in ok_sheet:
            pers.append(
                trans_list_to_person(
                    header = header,
                    in_info = row,
                    inkey_as_sub = True,
                    stdkey_as_sub = True,
                    classname = classname))
        self.__sheet.clear()
        return pers

    @staticmethod
    def _models_unexist():
        """返回不存在的模型地址"""
        from paddlex.inference import load_pipeline_config
        official_yamls = load_pipeline_config(PPOCRImgByModel.config)

        # print(official_yamls)
        # 这里默认导入的yaml文件是正确的(不正确的画官方函数load_pipeline_config会报错)
        def __parse_dict(_y: dict[str, dict] | dict[str, str] | dict[str, None]):
            """解析嵌套的dict"""
            name2dir: dict[str, str | None] = {}
            """一套字典只有能解析一套模型"""
            model_name = None
            model_dir = None
            for key in _y:
                if isinstance(_y[key], dict):
                    name2dir.update(__parse_dict(_y[key]))
                elif model_name is None and key == 'model_name':
                    model_name = _y[key]
                elif model_dir is None and key == 'model_dir':
                    model_dir = _y[key]
            if model_name is not None:
                name2dir[model_name] = model_dir
            return name2dir


        model_name2dir: dict[str, str | None] = __parse_dict(official_yamls)
        """模型名称与路径的字典序列"""

        def __set_dir():
            """设置模型路径"""
            nonlocal model_name2dir
            from paddlex.inference.utils.official_models import _ModelManager
            for key in model_name2dir:
                if model_name2dir[key] is None:
                    model_name2dir[key] = str(_ModelManager._save_dir) + '/' + key

        def __check_dir():
            """检查地址是否存在，返回不存在的地址"""
            from pathlib import Path
            nonlocal model_name2dir
            unknown_paths: list[str] = []
            for key in model_name2dir:
                if not Path(model_name2dir[key]).exists():
                    unknown_paths.append(key)
            return unknown_paths

        __set_dir()
        return __check_dir()


class PPOCRImgByAlgorithm:
    """通过算法来解析表格，仅使用部分模型"""

    def __init__(self):
        pass
