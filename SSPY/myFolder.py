"""此文件用于解析遍历文件夹"""
import copy
import os


def get_filename_with_extension(file_path):
    """
    从文件路径中获取带扩展名的文件名

    参数:
        file_path: 文件的完整路径字符串

    返回:
        带扩展名的文件名（如 'report.txt'）
    """
    return os.path.basename(file_path)


def split_filename_and_extension(file_path):
    """
    从文件路径中获取不带扩展名的文件名

    参数:
        file_path: 文件的完整路径字符串

    返回:
        不带扩展名的文件名（如 'report'）
    """
    # 先获取带扩展名的文件名，再分割扩展名
    full_filename = os.path.basename(file_path)
    name_part, ext_part = os.path.splitext(full_filename)

    return (name_part, ext_part)


class DefFolder:
    def __init__(self, root_dir: str):
        self.__root_dir = root_dir
        self.__paths = self.collect_file_paths(self.__root_dir)

    @staticmethod
    def collect_file_paths(root_dir: str):
        """
        递归遍历文件夹及其子目录，收集所有文件的绝对路径
        排除预加载文件如~$xxx和__MACOSX文件夹
        Parameters:
            root_dir: 要遍历的根文件夹路径
        Returns:
            包含所有符合条件的文件绝对路径的列表
        """
        file_paths = []

        # 定义需要排除的文件名模式
        def is_excluded_file(filename: str) -> bool:
            # 排除以 ~$ 开头的文件（如Office预加载文件）
            if filename.startswith("~$"):
                return True
            # 排除以 __M 开头的文件
            if filename.startswith("__M"):
                return True
            # 排除编辑器临时文件（#开头/结尾、.swp、.swo等）
            if filename.startswith("#") or filename.endswith("#") or filename.endswith((".swp", ".swo")):
                return True
            # 排除临时备份文件
            if filename.endswith(".bak") or (filename.startswith("~") and not filename.startswith("~$")):
                return True
            return False

        # 遍历目录时排除__MACOSX文件夹
        for root, dirs, files in os.walk(root_dir):
            # 检查并移除__MACOSX文件夹（修改dirs列表会影响后续遍历）
            if "__MACOSX" in dirs:
                dirs.remove("__MACOSX")  # 从遍历列表中移除，后续不会递归进入

            # 过滤并收集文件
            for file in files:
                if is_excluded_file(file):
                    continue  # 跳过不符合条件的文件
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

        return file_paths

    @property
    def paths(self):
        return copy.deepcopy(self.__paths)

    @property
    def root_dir(self):
        return self.__root_dir

    @property
    def filenames(self):
        filenames = []
        for file in self.paths:
            filenames.append(get_filename_with_extension(file))
        return filenames

    @property
    def filenames_without_extension(self):
        filenames = []
        for file in self.paths:
            filenames.append(split_filename_and_extension(file)[0])
        return filenames

    def get_paths_by(self, extensions: list):
        files = []
        for file in self.paths:
            for ext in extensions:
                if file.endswith(ext):
                    files.append(file)
                    break
        return files

    def get_filenames_by(self, extensions: list):
        filenames = []
        ps = self.get_paths_by(extensions)
        for file in ps:
            filenames.append(get_filename_with_extension(file))
        return filenames

    def get_filenames_without_extension_by(self, extensions: list):
        pure_filenames = []
        ps = self.get_paths_by(extensions)
        for file in ps:
            pure_filenames.append(split_filename_and_extension(file)[0])
        return pure_filenames
