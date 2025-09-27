import copy

from .PersonneInformation import DefPerson


def trans_sheet_to_person(in_sheet: list, classname: str = None) -> DefPerson:
    per = DefPerson()
    sheet = copy.deepcopy(in_sheet)
    if classname is not None:
        per.classname = classname

    for row in sheet:
        i = 0
        while i < len(row):
            stdkey = DefPerson.get_stdkey(row[i])
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





