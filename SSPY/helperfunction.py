def clean_enter(in_list: list | tuple) -> list:
    """清除in_sheet中的\\n，返回一个list[list]"""
    out_list = []
    for row in in_list:
        if isinstance(row, list | tuple):
            out_list.append(clean_enter(row))
        else:
            c = str(row)
            nc = c.replace('\n', '').replace('\r', '')
            out_list.append(nc)
    return out_list

def check_value(in_list: list | tuple, target_value = None, part: bool = False) -> bool:
    if target_value is None: return True
    if target_value not in in_list:
        for cell in in_list:
            if isinstance(cell, list | tuple):
                if check_value(cell, target_value,part): return True
            else:
                if part and target_value in cell:
                    return True
                continue
    else:
        return True
    return False
