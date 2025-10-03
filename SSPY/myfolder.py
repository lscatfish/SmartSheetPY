"""此文件用于解析遍历文件夹以及拷贝文件"""
import copy
import os
import shutil


def get_filename_with_extension(file_path):
    """
    从文件路径中获取带扩展名的文件名

    Parameters:
        file_path: 文件的完整路径字符串

    Returns:
        带扩展名的文件名（如 'report.txt'）
    """
    return os.path.basename(file_path)


def split_filename_and_extension(file_path):
    """
    从文件路径中获取不带扩展名的文件名
    Parameters:
        file_path: 文件的完整路径字符串

    Returns:
        不带扩展名的文件名（如 'report'）
    """
    # 先获取带扩展名的文件名，再分割扩展名
    full_filename = os.path.basename(file_path)
    name_part, ext_part = os.path.splitext(full_filename)

    return (name_part, ext_part)


def create_nested_folders(folder_path: str, exist_ok: bool = True) -> None:
    """
    创建嵌套的文件夹（支持多层目录结构）

    Parameters:
        folder_path: 要创建的嵌套文件夹路径（如 "a/b/c/d"）
        exist_ok: 如果为 True，当文件夹已存在时不抛出错误；默认为 True
    """
    try:
        # 递归创建目录，exist_ok=True 避免目录已存在时的错误
        os.makedirs(folder_path, exist_ok = exist_ok)
        print(f"成功创建嵌套文件夹：{folder_path}")
    except OSError as e:
        print(f"创建文件夹失败：{e}")


def copy_file(source_path: str, target_path: str, if_print: bool = False) -> bool:
    """
    将源文件复制到目标地址

    Parameters:
        if_print:    是否启用打印
        source_path: 源文件的完整路径（如 "data/file.txt"）
        target_path: 目标地址，可以是目录或完整文件路径
                     (若为目录：文件会复制到该目录下，文件名与源文件相同)
                     (若为文件路径：文件会复制到指定位置并使用新文件名

    Returns:
        复制成功返回 True，失败返回 False
    """
    try:
        # 检查源文件是否存在
        if not os.path.isfile(source_path):
            print(f"错误：源文件不存在 - {source_path}")
            return False

        # 复制文件（保留元数据）
        shutil.copy2(source_path, target_path)

        # 输出成功信息
        if os.path.isdir(target_path):
            # 目标是目录时，拼接完整目标路径
            target_full_path = os.path.join(target_path, os.path.basename(source_path))
        else:
            target_full_path = target_path
        if if_print:
            print(f"文件复制成功：{source_path} ----> {target_full_path}")
        return True

    except Exception as e:
        print(f"文件复制失败：{str(e)}")
        return False


class DefFolder:
    def __init__(self, root_dir: str, if_print: bool = False, extensions: str | list = None):
        """
        Args:
            root_dir:目标文件夹路径
            if_print:是否打印提示
            extensions:按照给定后缀提取文件
        """
        self.__root_dir = root_dir
        self.__if_print = if_print
        if self.__if_print: print('加载文件夹 \"' + self.__root_dir + '\"')
        self.__paths = self.collect_file_paths(self.__root_dir, if_print = self.__if_print)
        if extensions is not None:
            self.__paths = self.get_paths_by(extensions)
        if self.__if_print: print('Done!')

    @staticmethod
    def collect_file_paths(root_dir: str, if_print: bool = False) -> list[str]:
        """
        递归遍历文件夹及其子目录，收集所有文件的绝对路径
        排除预加载文件如~$xxx和__MACOSX文件夹
        Parameters:
            if_print: 是否打印检测到的文件
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
                if if_print:
                    print(file_path)
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
    def pure_filenames(self):
        filenames: list[str] = []
        for file in self.paths:
            filenames.append(split_filename_and_extension(file)[0])
        return filenames

    def get_paths_by(self, extensions: list | str) -> list[str]:
        files = []
        extn = extensions if isinstance(extensions, list) else [extensions, ]
        for file in self.paths:
            for ext in extn:
                if file.endswith(ext):
                    files.append(file)
                    break
        return files

    def get_filenames_by(self, extensions: list | str) -> list[str]:
        filenames = []
        ps = self.get_paths_by(extensions)
        for file in ps:
            filenames.append(get_filename_with_extension(file))
        return filenames

    def get_pure_filenames_by(self, extensions: list | str) -> list[str]:
        pure_filenames = []
        ps = self.get_paths_by(extensions)
        for file in ps:
            pure_filenames.append(split_filename_and_extension(file)[0])
        return pure_filenames
