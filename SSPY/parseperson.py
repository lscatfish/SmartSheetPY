# -*- coding: utf-8 -*-
import copy

from .PersonneInformation import DefPerson


def trans_sheet_to_person(
    in_sheet: list[list[str]],
    classname: str = None,
    inkey_as_sub = False,
    stdkey_as_sub = False) -> DefPerson:
    per = DefPerson()
    sheet = copy.deepcopy(in_sheet)
    if classname is not None:
        per.classname = classname

    for row in sheet:
        i = 0
        while i < len(row):
            stdkey = DefPerson.get_stdkey(
                row[i], inkey_as_sub = inkey_as_sub, stdkey_as_sub = stdkey_as_sub)
            if stdkey is not None:
                # 将索引拉取到下一个非None
                i += 1
                while i < len(row):
                    if str(row[i]) != 'None':
                        re = str(row[i]).strip()
                        per.set_information(stdkey, re)
                        i += 1
                        break
                    else:
                        i += 1
            else:
                i += 1
    per.optimize()
    return per


def renormalization(in_sheet: list[list[str]], path: str, cmtt):
    """
    重整化
    Args:
        in_sheet:输入的list[list[str]]
        path:文件路径
        cmtt:是否为班委报名表
    """
    if in_sheet is None or len(in_sheet) == 0: return None
    per = trans_sheet_to_person(in_sheet, inkey_as_sub = True)
    """从表格获取人员信息"""
    per.filepath = path
    if '推荐' in path:
        per.set_information('报名方式', '组织推荐')
    elif '自' in path:
        per.set_information('报名方式', '自主报名')
    elif '组织' in path or '社团' in path or '学院' in path:
        per.set_information('报名方式', '组织推荐')
    elif '重庆大学团校' in path or '团校报名' in path or '团校学员报名' in path:
        per.set_information('报名方式', '自主报名')
    else:
        # 不以最坏情况思考
        per.set_information('报名方式', '组织推荐')
    per.ifsign = cmtt
    return per
