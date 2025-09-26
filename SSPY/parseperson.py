from .PersonneInformation import DefPerson


def trans_person_to_sheet(per: DefPerson, std: list) -> list | None:
    """
    Parameters
    -------
    per : DefPerson
        人员
    std : list
        提取标准
    """
    outList = []
    for s in std:
        outList.append(per.get_information(s))
    return outList

def trans_sheet_to_person( sheet: list) -> DefPerson:

    pass
def trans_lists_to_person(lists: list) -> DefPerson:
    pass