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
