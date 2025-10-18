import copy
import threading
import SSPY.fuzzy.search as fuzzy_search

from SSPY.mypdf import PdfLoad
from SSPY.mydocx import DocxLoad
from SSPY.PersonneInformation import DefPerson
from SSPY.globalconstants import GlobalConstants as gc
from SSPY.myfolder import DefFolder, copy_file
from SSPY.myxlsx import XlsxLoad, XlsxWrite
from SSPY.helperfunction import _exit
from SSPY.tracker.core import VariableType, monitor_variables, get_current_monitor
from SSPY.communitor.connect import (
    connect_progress_default,
    disconnect_progress_default,
    post_progress_default)


class DoQingziClass:
    """青字班程序控制库"""

    def __init__(self):
        self.__persons_all: list[DefPerson] = []  # """所有人员的名单"""
        self.__classname_all: list[str] = []  # 所有的班级名
        self.__unknownPersons: list[tuple[DefPerson, list[DefPerson]]] = []  # 未知的人员列表
        self.__stopFlag: threading.Event | None = None  # 停止标志


    def __self_check(self):
        """自检方法"""
        pass

    def reset(self):
        """重置状态"""
        self.__persons_all.clear()
        self.__classname_all.clear()
        self.__unknownPersons.clear()
        if self.__stopFlag and isinstance(self.__stopFlag, threading.Event):
            self.__stopFlag.clear()
        self.__stopFlag = None

    def start(self, callback_cfunction, stop_flag: threading.Event = None):
        """
        Args:
            callback_cfunction:选择回调，或者是int类型
            stop_flag:线程退出标志
        """
        self.reset()  # 确保不会出错
        self.__stopFlag = stop_flag
        match callback_cfunction:
            case 1:
                if not _exit(self.__stopFlag):
                    self.__load_person_all()
                if not _exit(self.__stopFlag):
                    self.appSheet()
            case 2:
                if not _exit(self.__stopFlag):
                    self.__load_person_all()
                if not _exit(self.__stopFlag):
                    self.attSheet()
            case 3:
                if not _exit(self.__stopFlag):
                    self.signforqcSheet()


    def choose(self) -> int:
        """选择器"""
        while True:
            print('请选择功能：')
            print('1.生成签到表')
            print('2.生成汇总表')
            print('3.统计青字班报名情况')
            c = input('请选择：')
            if len(c) == 0:
                print(end = '\n')
                print('你的选择错误')

            elif int(c) == 1:
                break
            elif int(c) == 2:
                break
            elif int(c) == 3:
                break
            else:
                print(end = '\n')
                print('你的选择错误')

        return int(c)

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def __load_person_all(self):
        """加载所有的学员信息"""
        try:
            print('加载所有的学员信息')
            folder = DefFolder(gc.dir_INPUT_ALL_, extensions = gc.extensions_XLSX, if_print = True)
            self.__classname_all = folder.pure_filenames
            paths = folder.paths
            len_paths = len(paths)
            connect_progress_default(paths)
            i = 0
            for p in paths:
                i += 1
                if _exit(self.__stopFlag): return
                post_progress_default(i, len_paths, '加载文件 ' + p)
                xlsx_sheet = XlsxLoad(_path = p, classname = gc.get_classname_from_path(path = p))  # 自动识别班级
                self.__persons_all.extend(xlsx_sheet.get_personList())
        finally:
            disconnect_progress_default()

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def appSheet(self):
        """签到表"""
        current_monitor = get_current_monitor()

        @current_monitor.add_nested_function(return_value = ([], []))
        def __load_person_app():
            """解析报集会名表中的人员"""
            print('加载报名学员名单中...')
            folder = DefFolder(gc.dir_INPUT_APP_, extensions = ['.xlsx', '.XLSX'], if_print = True)
            paths = folder.paths
            classnames = folder.pure_filenames
            persons_app: list[DefPerson] = []
            for i in range(len(paths)):
                if _exit(self.__stopFlag): return None
                xlsx_sheet = XlsxLoad(paths[i], classname = gc.get_classname_from_path(path = paths[i]))  # 自动识别班级
                persons_app.extend(xlsx_sheet.get_personList(stdkey_as_sub = True))
            return persons_app, classnames

        @current_monitor.add_nested_function()
        def __person_sign(persons_app: list[DefPerson]):
            """标记人员"""
            if persons_app is None or len(persons_app) == 0: return
            for per_app in persons_app:
                per_all = self.search(per_app, push_unknown = True)
                if per_all is not None:
                    per_all.ifsign = True

        @current_monitor.add_nested_function()
        def __make_sheet(classname: str) -> list[list[str]] | None:
            """制表"""
            if classname is None: return None
            header = ['姓名', '学号']
            outSheet: list[list[str]] = [['序号', '姓名', '学号', '签到'], ]
            i = 1
            for per in self.__persons_all:
                if per.ifsign and per.classname == classname:
                    l: list[str] = [str(i)]
                    l.extend(per.to_list(header))
                    l.append('')
                    outSheet.append(l)
                    i += 1
            return outSheet

        @current_monitor.add_nested_function()
        def __save(sheet: list[list[str]], classname: str):
            if sheet is None or classname is None: return
            if _exit(self.__stopFlag): return

            from SSPY.helperfunction import sort_table
            sort_table(sheet,
                lambda a, b: True
                if len(a[2]) > len(b[2])
                else True if len(a[2]) == len(b[2]) and a[2] > b[2]
                else False,
                [0, ], [0, ])

            path = gc.dir_OUTPUT_APP_ + classname + '.xlsx'
            writer = XlsxWrite(
                path = path,
                sheet = sheet,
                title = classname + '签到表',
                widths = [7, 24],
                height = 24,
                height_title = 40
            )
            writer.fontRegular = gc.fontRegularSong
            writer.fontTitle = gc.fontTitleGBK
            writer.border = gc.borderThinBlack
            if writer.can_write:
                writer.write()
            print('签到表已储存：\"' + path + '\"')

        @current_monitor.add_nested_function()
        def __storage():
            """储存报名信息"""
            sheet: list[list[str]] = []
            header = [gc.chstrQClassname, gc.chstrName, gc.chstrStudentID]
            sheet.append(header)
            for per in self.__persons_all:
                if _exit(self.__stopFlag): return
                if per.ifsign:
                    sheet.append(per.to_list(header))
            path = gc.dir_STORAGE_ + 'storage.xlsx'
            XlsxWrite(
                path = path,
                sheet = sheet,
                font_regular = gc.fontRegularSongSmall
            ).write()
            print('报名信息已储存：\"' + path + '\"')

        pers_app, cns = __load_person_app()
        try:
            connect_progress_default(cns)
            __person_sign(pers_app)
            len_cns = len(cns)
            """班级名字list的长度"""
            for i in range(len_cns):
                post_progress_default(i, len_cns, f'处理班级{cns[i]}中...')
                sh = __make_sheet(cns[i])
                __save(sh, cns[i])
        finally:
            disconnect_progress_default()

        __storage()
        self.__unknownSheet()

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def attSheet(self):
        """签到汇总"""
        current_monitor = get_current_monitor()

        @current_monitor.add_nested_function()
        def __organize_imgs() -> dict[str, list[str]] | None:
            """整理照片以及其地址"""
            classname_imgpath: dict[str, list[str]] = {}
            folder = DefFolder(gc.dir_INPUT_ATTIMGS_, extensions = gc.extensions_IMG, if_print = True)
            for p in folder.paths:
                if _exit(self.__stopFlag): return None
                for cn in gc.cns:
                    if cn[0] in p:
                        if classname_imgpath.get(cn[1], '') == '':
                            classname_imgpath[cn[1]] = [p, ]
                        else:
                            classname_imgpath[cn[1]].append(p)
            # print(classname_imgpath)
            return classname_imgpath

        @current_monitor.add_nested_function(return_value = [])
        def __parse_imgs(cn_ip: dict[str, list[str]]) -> list[DefPerson] | None:
            if cn_ip is None: return None
            persons_att: list[DefPerson] = []
            # 启用ocr
            from SSPY.myimg import PPOCRImgByModel
            ocr = PPOCRImgByModel(stop_flag = self.__stopFlag)
            if _exit(self.__stopFlag):
                return []
            try:
                len_sum = 0
                for cn in cn_ip:
                    len_sum += len(cn_ip[cn])
                connect_progress_default(len_sum)
                i = 0
                for cn in cn_ip.keys():
                    for ip in cn_ip[cn]:
                        if _exit(self.__stopFlag): return []
                        i += 1
                        post_progress_default(i, len_sum, f'OCR正在识别文件 {ip}')
                        ocr.predict(ip)
                    persons_att.extend(ocr.get_personList(cn, ifp = True))
            finally:
                disconnect_progress_default()
            return persons_att

        @current_monitor.add_nested_function()
        def __person_checkin(persons_att: list[DefPerson]):
            """检查是否签到"""
            if persons_att is None: return
            for per_att in persons_att:
                per_all = self.search(per_att, push_unknown = True)
                if per_all is not None:
                    qd = per_att.get_information('签到')
                    if qd != '' and qd != 'None':
                        per_all.ifcheck = True

        @current_monitor.add_nested_function()
        def __make_sheet(classname: str) -> list[list[str]] | None:
            """制表"""
            if classname is None: return None
            in_header = [gc.chstrName, gc.chstrStudentID, gc.chstrAcademy, '联系方式']
            out: list[list[str]] = [
                [gc.chstrName, gc.chstrStudentID, gc.chstrAcademy, '联系方式', gc.chstrCheckIn, '备注'], ]
            for per in self.__persons_all:
                if per.classname == classname:
                    l = per.to_list(in_header)
                    if per.ifcheck:
                        l.append('已签到')
                    elif per.ifsign:
                        l.append('缺席')
                    else:
                        l.append('')
                    if per.ifsign:
                        l.append('')
                    else:
                        l.append('未报名')
                    out.append(l)
            return out

        @current_monitor.add_nested_function()
        def __save(sheet: list[list[str]], classname: str):
            """保存签到表"""
            if _exit(self.__stopFlag): return
            if sheet is None or classname is None: return

            from openpyxl.styles import Font
            from SSPY.helperfunction import sort_table
            sort_table(sheet,
                lambda a, b: True
                if len(a[4]) < len(b[4])
                else True
                if len(a[4]) == len(b[4]) and a[2] > b[2]
                else False,
                [0, ])

            path = gc.dir_OUTPUT_ATT_ + classname + '线下签到汇总表.xlsx'
            writer = XlsxWrite(
                path = path,
                sheet = sheet,
                widths = [40, 40],
                height = 25,
                font_regular = Font(name = '宋体', size = 16)
            )
            writer.heightTitle = 45
            writer.title = classname + '线下签到汇总表'
            writer.fontTitle = Font(name = '方正小标宋简体', size = 26)
            writer.border = gc.borderThinBlack
            writer.write()
            print('线下签到汇总表已储存：\"' + path + '\"')

        self.__load_storage()
        pers_att = __parse_imgs(__organize_imgs())

        __person_checkin(pers_att)
        for cn in self.__classname_all:
            __save(__make_sheet(cn), cn)
        self.__unknownSheet()

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def signforqcSheet(self):
        """青字班报名统计,per.ifsign表示是否报名班委"""
        unknown_paths: list[str] = []
        """未知（无法解析）的文件的路径"""
        cmtts_paths: list[str] = []
        """班委报名表的路径"""
        current_monitor = get_current_monitor()

        @current_monitor.add_nested_function(return_value = ([], []))
        def __organize_files():
            """收集报名的各种文件"""
            if _exit(self.__stopFlag):  return [], []
            folder = DefFolder(gc.dir_INPUT_SIGNFORQC_)
            pdf_paths = folder.get_paths_by(gc.extensions_PDF)
            docx_paths = folder.get_paths_by(gc.extensions_DOCX)
            return pdf_paths, docx_paths

        @current_monitor.add_nested_function(return_value = [])
        def __parse_docxs(paths: list[str]) -> list[DefPerson]:
            """解析docx文件"""
            if paths is None or (isinstance(paths, list) and len(paths)) == 0: return []
            nonlocal unknown_paths
            from SSPY.parseperson import trans_sheet_to_person
            pers: list[DefPerson] = []

            try:
                len_paths = len(paths)
                connect_progress_default(len_paths)
                i = 0
                for p in paths:
                    if _exit(self.__stopFlag):  return []
                    i += 1
                    post_progress_default(i, len_paths,
                        f'解析DOCX文件 {p}')
                    word = DocxLoad(p)
                    sh_per = word.get_sheet_without_enter('姓名')
                    if sh_per is not None:
                        per = trans_sheet_to_person(sh_per, inkey_as_sub = True)  # 启用模糊处理
                        per.set_information('地址', value = p)
                        if '自' in p:
                            per.set_information('报名方式', '自主报名')
                        elif '组织' in p:
                            per.set_information('报名方式', '组织推荐')
                        elif '重庆大学团校' in p:
                            per.set_information('报名方式', '自主报名')
                        else:
                            # 不以最坏情况思考
                            per.set_information('报名方式', '组织推荐')
                        pers.append(per)
                    else:
                        unknown_paths.append(p)
            finally:
                disconnect_progress_default()

            return pers

        @current_monitor.add_nested_function(return_value = [])
        def __parse_pdfs(paths: list[str]) -> list[DefPerson]:
            """解析pdf文件"""
            if paths is None or len(paths) == 0: return []
            nonlocal unknown_paths
            nonlocal cmtts_paths
            from SSPY.parseperson import trans_sheet_to_person
            pers: list[DefPerson] = []

            try:
                len_paths = len(paths)
                connect_progress_default(len_paths)
                i = 0

                for p in paths:
                    if _exit(self.__stopFlag):  return []
                    i += 1
                    post_progress_default(i, len_paths,
                        f'解析PDF文件 {p}')
                    pdf = PdfLoad(p)
                    sh1 = pdf.get_sheet('应聘岗位', True)
                    sh2 = pdf.get_sheet('所任职务', True)
                    if sh1 is not None:
                        cmtts_paths.append(p)
                        per = trans_sheet_to_person(sh1, inkey_as_sub = True)
                        per.ifsign = True  # 报名班委
                        per.set_information('地址', value = p)
                        if '自' in p:
                            per.set_information('报名方式', '自主报名')
                        else:
                            per.set_information('报名方式', '组织推荐')
                        pers.append(per)
                        continue
                    elif sh2 is not None:
                        per = trans_sheet_to_person(sh2, inkey_as_sub = True)
                        per.set_information('地址', value = p)
                        if '自' in p:
                            per.set_information('报名方式', '自主报名')
                        elif '组织' in p or '社团' in p or '学院' in p:
                            per.set_information('报名方式', '组织推荐')
                        elif '重庆大学团校' in p:
                            per.set_information('报名方式', '自主报名')
                        else:
                            # 不以最坏情况思考
                            per.set_information('报名方式', '组织推荐')
                        pers.append(per)
                        continue
                    else:
                        unknown_paths.append(p)
            finally:
                disconnect_progress_default()

            return pers

        @current_monitor.add_nested_function()
        def __merge(pers_pdf: list[DefPerson]):
            """合并解析出的人员信息"""
            if pers_pdf is None or len(pers_pdf) == 0: return
            temps: list[DefPerson] = []
            for p in pers_pdf:
                p_all = self.search(p)  # 不启用push
                if p_all is not None:
                    p_all.merge(p)
                else:
                    temps.append(p)
            self.__persons_all.extend(temps)

        @current_monitor.add_nested_function()
        def __make_sheet():
            """制表"""
            """预制表过程"""
            header: list[str] = [
                gc.chstrName,
                gc.chstrGender,
                gc.chstrEthnicity,
                gc.chstrGrade,
                gc.chstrStudentID,
                gc.chstrPoliticalOutlook,
                gc.chstrAcademy,
                gc.chstrMajors,
                gc.chstrPosition,
                gc.chstrClub,
                gc.chstrPhone,
                gc.chstrQQ,
                gc.chstrEmail,
                gc.chstrQClassname,
                gc.chstrSignPosition,
                gc.chstrRegistrationMethod,
                gc.chstrNote,
                # gc.chstrPersonalProfile,
                # gc.chstrPersonalStrengths,
                # gc.chstrWorkExperience,
                # gc.chstrAwardsAndHonors,
                '文件地址']
            sheet: list[list[str]] = [copy.deepcopy(header)]
            sheet[0].append('是否报名班委')
            for per in self.__persons_all:
                row = per.to_list(header)
                row.append('是' if per.ifsign else '否')
                sheet.append(row)
            # 生成序号
            sheet[0].insert(0, '序号')
            for i in range(1, len(sheet)):
                sheet[i].insert(0, str(i))
            return sheet


        @current_monitor.add_nested_function()
        def __save(sheet: list[list[str]]):
            from openpyxl.styles import Alignment
            from SSPY.helperfunction import sort_table
            if sheet is None or len(sheet) == 0: return
            sort_table(sheet, lambda a, b: a[0] < b[0], [0, ], [0, ])
            writer = XlsxWrite(
                sheet = sheet,
                path = gc.dir_OUTPUT_SIGNFORQC_ + '报名.xlsx',
                font_regular = gc.fontRegularSongSmall,
                alignment = Alignment(vertical = 'center')
            )
            writer.write()

        pdf_paths, docx_paths = __organize_files()
        pers_doc = __parse_docxs(docx_paths)
        if pers_doc is None or len(pers_doc) == 0:
            return
        else:
            self.__persons_all.extend(pers_doc)
        __merge(__parse_pdfs(pdf_paths))
        __save(__make_sheet())

        """处理错误"""
        for p in unknown_paths:
            copy_file(p, gc.dir_OUTPUT_SIGNFORQC_unknown, if_print = True)

        for p in cmtts_paths:
            copy_file(p, gc.dir_OUTPUT_SIGNFORQC_committee, if_print = True)

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def __load_storage(self):
        """加载临时文件，自动报名"""
        pers_app = XlsxLoad(
            _path = gc.dir_STORAGE_ + 'storage.xlsx',
            const_classname = False,
            ifp = True
        ).get_personList()
        for p_app in pers_app:
            for per in self.__persons_all:
                if per.classname == p_app.classname and self.is_same_studentID(per.studentID, p_app.studentID):
                    per.ifsign = True

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def __unknownSheet(self):
        sheet: list[list[str]] = [['类型', gc.chstrQClassname, gc.chstrName, gc.chstrStudentID], ]
        header = [gc.chstrQClassname, gc.chstrName, gc.chstrStudentID]
        if len(self.__unknownPersons) > 0:
            for per in self.__unknownPersons:
                if _exit(self.__stopFlag): return
                # print(per[0])
                l: list[str] = ['*UNKNOWN', ]
                l.extend(per[0].to_list(header))
                sheet.append(l)
                for lp in per[1]:
                    l2: list[str] = ['-LIKELY', ]
                    l2.extend(lp.to_list(header))
                    sheet.append(l2)
            for r in sheet:
                if _exit(self.__stopFlag): return
                print(r)
        else:
            print('没有未知人员')
        path = gc.dir_OUTPUT_ + 'unknown.xlsx'
        XlsxWrite(
            path = path,
            sheet = sheet,
            font_regular = gc.fontRegularSongSmall,
            widths = [24, ]
        ).write()
        print('未知人员表已储存：\"' + path + '\"')

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = _exit,
        return_value = None)
    def search(self, target: DefPerson, push_unknown = False) -> DefPerson | None:
        """从全部的库中搜索目标人员，返回总表人员的指针"""
        same_name = 0
        maybe_per = None
        for per_a in self.__persons_all:
            if per_a.classname == target.classname:
                if self.is_same_studentID(target.studentID, per_a.studentID):
                    return per_a
                elif target.name == per_a.name:
                    maybe_per = per_a
                    same_name += 1
        if same_name == 1:
            return maybe_per
        if push_unknown:
            likely: list[DefPerson] = []
            for per_a in self.__persons_all:
                if per_a.classname == target.classname:
                    if self.is_fuzzy_studentID(target.studentID, per_a.studentID):
                        likely.append(copy.deepcopy(per_a))
                    elif fuzzy_search.match_by(per_a.name, target.name, fuzzy_search.LEVEL.High):
                        likely.append(copy.deepcopy(per_a))
            self.__unknownPersons.append((copy.deepcopy(target), likely))

        return None


    @staticmethod
    def is_same_studentID(a: str, b: str) -> bool:
        if len(a) != len(b):  return False
        if len(a) < 4 or len(b) < 4: return False
        if a.endswith(('t', 'T')) and b.endswith(('t', 'T')):
            a_number_part = a[:-1]
            b_number_part = b[:-1]
            return a_number_part == b_number_part
        else:
            return a == b


    @staticmethod
    def is_fuzzy_studentID(a: str, b: str) -> bool:
        if len(a) < 4 or len(b) < 4: return False
        if a.endswith(('t', 'T')) and b.endswith(('t', 'T')):
            a_number_part = a[:-1]
            b_number_part = b[:-1]
            return fuzzy_search.match_by(a_number_part, b_number_part, fuzzy_search.LEVEL.High)
        else:
            return fuzzy_search.match_by(a, b, fuzzy_search.LEVEL.High)
