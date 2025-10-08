"""
搜索类的基础工具
"""


class SearchingTool:
    """搜索工具"""

    def __init__(self):
        from SSPY.myfolder import DefFolder
        self.__paths: list[str] = DefFolder(root_dir = '', ).paths
