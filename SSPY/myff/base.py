"""标准文件控制库"""
import os.path
import shutil
import time
from pathlib import Path

from SSPY.myff import BASE_DIR

import hashlib


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


def create_nested_folders(
    folder_path: str,
    exist_ok: bool = True,
    if_print: bool = True) -> None:
    """
    创建嵌套的文件夹（支持多层目录结构）

    Parameters:
        folder_path: 要创建的嵌套文件夹路径（如 "a/b/c/d"）
        exist_ok: 如果为 True，当文件夹已存在时不抛出错误；默认为 True
    """
    try:
        # 递归创建目录，exist_ok=True 避免目录已存在时的错误
        os.makedirs(folder_path, exist_ok = exist_ok)
        if if_print:
            print(f"成功创建嵌套文件夹：{folder_path}")
    except OSError as e:
        raise print(f"创建文件夹失败：{e}")


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
            print(f"文件复制成功：{source_path} ---> {target_full_path}")
        return True

    except Exception as e:
        print(f"文件复制失败：{str(e)}")
        return False


def is_same_path(a: str | Path, b: str | Path) -> bool:
    """判断是否是同一个路径"""
    p1 = os.path.abspath(str(a))
    p2 = os.path.abspath(str(b))
    return p1 == p2


def parent_dir(a: str | Path) -> tuple[str, str]:
    """获取母目录，并返回初始目录"""
    p = Path(a) if isinstance(a, str) else a
    return str(p.parent), str(a)


def get_top_parent_dir_by(header: str | Path, start: str | Path):
    """
    获取顶部路径
    """
    higher = start
    while True:
        higher, this = parent_dir(higher)
        if is_same_path(header, higher):
            return str(this)


def deduplication_paths(paths: list[str] | list[Path]) -> list[str | Path]:
    """对路径去重"""
    dedup = []
    exclude = []
    if len(paths) <= 1: return paths
    for i in range(len(paths)):
        if i in exclude: continue
        dedup.append(paths[i])
        for j in range(i + 1, len(paths)):
            if is_same_path(paths[i], paths[j]):
                exclude.append(j)
    return dedup


def safe_copytree(src, dst, max_retries = 3, delay = 0.2):
    for i in range(max_retries):
        try:
            shutil.copytree(src, dst, dirs_exist_ok = True)
            return True
        except PermissionError as e:
            if i < max_retries - 1:
                time.sleep(delay)  # 重试前延迟
                continue
            print(f'多次尝试复制"{src}"到"{dst}"失败：{e}')
            return False
        except Exception as e:
            print(f'复制 "{src}" 失败：{e}')
            return False


def calculate_file_hash(file_path, algorithm = 'md5'):
    """
    计算文件的哈希值
    Args:
        file_path: 文件的路径（绝对路径或相对路径）
        algorithm: 哈希算法，支持'md5'、'sha1'、'sha256'、'sha512'等
    Returns:
        哈希值的十六进制字符串
    """
    # 验证算法是否支持
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"不支持的哈希算法: {algorithm}")

    # 创建哈希对象
    hash_obj = hashlib.new(algorithm)

    # 分块读取文件并更新哈希
    block_size = 65536  # 64KB块大小，可根据需求调整
    try:
        with open(file_path, 'rb') as f:  # 二进制模式读取，避免编码问题
            while chunk := f.read(block_size):  # 循环读取块
                hash_obj.update(chunk)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {file_path}")

    # 返回十六进制哈希值
    return hash_obj.hexdigest()


class BaseFile:
    """一个文件对象"""

    def __init__(self, path: str | Path, base_dir: str = BASE_DIR, chash = True):
        """
        输入一个文件路径
        Args:
            path:目标文件
            base_dir:程序运行的默认路径（绝对）
            chash:是否计算哈希值
        """
        self.relative_path = None
        """相对路径"""
        self.absolute_path = None
        """绝对路径"""
        self.__hash = None
        """文件的哈希值"""
        self.__purename = None
        """纯文件名字，无后缀"""
        self.__filename = None
        """文件名字"""
        self.__extension = None
        """文件后缀"""
        if not os.path.exists(path):
            raise Exception(f'“{path}”不存在')
            # return
        if not os.path.isfile(path):
            raise Exception(f'“{path}”不是文件')
            # return
        self.absolute_path = os.path.abspath(str(path))
        self.relative_path = os.path.relpath(self.absolute_path, base_dir)
        self.__filename = os.path.basename(self.absolute_path)
        self.__purename, self.__extension = os.path.splitext(self.__filename)
        if chash:
            self.__hash = self._hash()

    def _hash(self) -> str:
        """计算哈希值"""
        hash_obj = hashlib.new('md5')
        # 分块读取文件并更新哈希
        block_size = 65536  # 64KB块大小，可根据需求调整
        try:
            with open(self.absolute_path, 'rb') as f:  # 二进制模式读取，避免编码问题
                while chunk := f.read(block_size):  # 循环读取块
                    hash_obj.update(chunk)
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {self.absolute_path}")
        except PermissionError:
            raise PermissionError(f"没有权限读取文件: {self.absolute_path}")
        except Exception as e:
            raise Exception(f"{e}")

        # 返回十六进制哈希值
        return hash_obj.hexdigest()

    def is_same(self, other: 'BaseFile') -> bool:
        """是否相同"""
        if self.is_same_path(other): return True
        if self.__hash is None or other.__hash is None: return False
        return self.__hash == other.__hash

    def is_same_path(self, other: 'BaseFile') -> bool:
        """是否是相同的路径"""
        if self.absolute_path is None or other.absolute_path is None: return False
        return other.absolute_path == self.absolute_path

    @property
    def filename(self) -> str:
        """
        从文件路径中获取带扩展名的文件名
        文件名称（文件名.后缀）
        """
        return self.__filename

    @property
    def purename(self) -> str:
        """
        纯名字
        """
        return self.__purename

    @property
    def extension(self) -> str:
        """文件后缀"""
        return self.__extension

    @property
    def purename_extension(self):
        return self.__purename, self.__extension

    def copy_to(self, dist: str | Path, if_print = False):
        """
        复制文件到dist
        Args:
            dist:输入的路径
            if_print:是否打印
        """
        try:
            # 复制文件（保留元数据）
            shutil.copy2(self.absolute_path, dist)

            # 输出成功信息
            if os.path.isdir(dist):
                # 目标是目录时，拼接完整目标路径
                target_full_path = os.path.join(dist, self.__filename)
            else:
                target_full_path = dist
            if if_print:
                print(f"文件复制成功：{self.relative_path} ---> {target_full_path}")
            return True

        except Exception as e:
            print(f"文件复制失败：{str(e)}")
            return False

    @property
    def parent_dir(self) -> str:
        """获取文件的上级路径"""
        try:
            return parent_dir(self.absolute_path)[0]
        except Exception as e:
            raise e

    def top_parent_dir(self, top_dir: str | Path) -> str:
        """
        获取顶级的文件路径
        Args:
            top_dir:顶级文件夹
        """
        return get_top_parent_dir_by(top_dir, self.absolute_path)
