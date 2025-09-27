import copy

from .PersonneInformation import DefPerson


def trans_person_to_sheet(per: DefPerson, in_std: list) -> list | None:
    """
    Parameters
    -------
    per : DefPerson
        人员
    in_std : list
        提取标准
    """
    outList = []
    std = copy.deepcopy(in_std)
    for s in std:
        outList.append(per.get_information(s))
    return outList


def trans_sheet_to_person(in_sheet: list, classname: str = None) -> DefPerson:
    per = DefPerson()
    sheet = copy.deepcopy(in_sheet)
    if classname is not None:
        per.classname = classname
    for row in sheet:
        for i in range(len(row)):
            stdkey = DefPerson.get_stdkey(row[i])
            if stdkey is not None:
                # 将索引拉取到下一个非None
                i += 1
                while i < len(row):
                    if str(row[i]) != 'None':
                        re = str(row[i]).strip()
                        per.set_information(stdkey, re)
                        break
                    else:
                        i += 1
            elif stdkey is None:
                continue
    per.optimize()
    return per


def trans_lists_to_person(in_header: list, in_info: list, classname: str = None) -> DefPerson:
    per = DefPerson()
    header = copy.deepcopy(in_header)
    info = copy.deepcopy(in_info)
    if classname is not None:
        per.classname = classname
    for i in range(len(header)):
        if i >= len(info): break
        per.set_information(header[i], str(info[i]).strip())
    per.optimize()
    return per
