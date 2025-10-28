"""标准文件控制库"""
import copy
import os.path
import shutil
import time
import hashlib
from enum import Enum, unique
from os import PathLike

from pathlib import Path
from SSPY.myff import BASE_DIR


def get_filename(file_path):
    """
    从文件路径中获取带扩展名的文件名

    Parameters:
        file_path: 文件的完整路径字符串

    Returns:
        带扩展名的文件名（如 'report.txt'）
    """
    return os.path.basename(file_path)


def get_purename_extension(file_path):
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

    return name_part, ext_part


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


def is_same_path(a: str | Path, b: str | Path) -> bool:
    """判断是否是同一个路径"""
    p1 = os.path.abspath(a)
    p2 = os.path.abspath(b)
    return p1 == p2


def parent_dir(a: str | Path) -> tuple[str, str]:
    """获取母目录，并返回初始目录"""
    p = Path(a) if isinstance(a, str) else a
    return str(p.parent), str(a)


def get_top_parent_dir(header: str | Path, start: str | Path):
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


def calculate_str_hash(s: str) -> str:
    """按照md5方法计算哈希值"""
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def safe_copy_any(src: str | PathLike | Path,
                  dst: str | Path | PathLike,
                  rename: str = None,
                  if_print = True,
                  max_retries = 3,
                  delay = 0.1):
    """
    安全复制函数，针对文件和文件夹
    复制src文件夹下的所有的内容
    Args:
        src:初始文件(夹)
        dst:目标路径（只能是路径）
        rename:是否重命名（不含后缀）
        if_print:打印提示
        max_retries:重复尝试次数
        delay:尝试延时
    """
    from SSPY.communitor import mprint
    if os.path.isfile(src):
        """如果是文件"""
        create_nested_folders(dst, if_print = False)
        target_full_path = os.path.join(dst, (os.path.basename(src)) if rename is None
        else f"{rename}{get_purename_extension(src)[1]}")
        shutil.copy2(src, target_full_path)
        if if_print:
            mprint(f'复制文件成功：{src} ---> {target_full_path}')
    elif os.path.isdir(src):
        target_full_path = os.path.join(dst, (os.path.basename(src)) if rename is None else rename)
        for i in range(max_retries):
            try:
                shutil.copytree(src, target_full_path, dirs_exist_ok = True)
                if if_print:
                    mprint(f'复制文件夹成功：{src} ---> {target_full_path}')
                return
            except PermissionError as e:
                if i < max_retries - 1:
                    time.sleep(delay)
                    continue
                mprint(f'多次尝试复制"{src}"到"{target_full_path}"失败：{e}', 'red')
                return
            except Exception as e:
                print(f"文件复制失败：{str(e)}")
                return


class BaseFile:
    """一个文件对象"""

    @unique
    class Type(Enum):
        unknown = 0
        docx = 1
        pdf = 2
        xlsx = 3

    def __init__(self, path: str | Path, base_dir: str | Path = BASE_DIR, auto_hash = True):
        """
        输入一个文件路径
        Args:
            path:目标文件
            base_dir:程序运行的默认路径（绝对）
            auto_hash:自动打开（只有在使用哈希的时候才会自动打开）
        """
        self._relative_path = None
        """相对路径"""
        self._absolute_path = None
        """绝对路径"""
        self.__hash = None
        """文件的哈希值"""
        self.__purename = None
        """纯文件名字，无后缀"""
        self.__filename = None
        """文件名字"""
        self.__extension = None
        """文件后缀"""
        self.__type = self.Type.unknown
        """文件类型"""
        if not os.path.exists(path):
            raise Exception(f'“{path}”不存在')
            # return
        if not os.path.isfile(path):
            raise Exception(f'“{path}”不是文件')
            # return
        self._absolute_path = os.path.abspath(path)
        self._relative_path = os.path.relpath(self._absolute_path, str(base_dir))
        self.__filename = os.path.basename(self._absolute_path)
        self.__purename, self.__extension = os.path.splitext(self.__filename)
        if not auto_hash:
            self.__hash = self.chash()

    def chash(self) -> str:
        """计算哈希值"""
        hash_obj = hashlib.new('md5')
        # 分块读取文件并更新哈希
        block_size = 65536  # 64KB块大小，可根据需求调整
        try:
            with open(self._absolute_path, 'rb') as f:  # 二进制模式读取，避免编码问题
                while chunk := f.read(block_size):  # 循环读取块
                    hash_obj.update(chunk)
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {self._absolute_path}")
        except PermissionError:
            raise PermissionError(f"没有权限读取文件: {self._absolute_path}")
        except Exception as e:
            raise Exception(f"{e}")
        # 返回十六进制哈希值
        return hash_obj.hexdigest()

    def is_same_content(self, other: 'BaseFile') -> bool:
        """文件的内容是否相同"""
        if self.is_same_path(other): return True
        return self.hash_all == other.hash_all

    def is_same_path(self, other: 'BaseFile') -> bool:
        """文件的路径是否是相同"""
        if self._absolute_path is None or other._absolute_path is None: return False
        return other._absolute_path == self._absolute_path

    @property
    def filename(self) -> str:
        """
        从文件路径中获取带扩展名的文件名
        文件名称（文件名.后缀）
        """
        return self.__filename

    @property
    def purename(self) -> str:
        """  纯名字    """
        return self.__purename

    @property
    def extension(self) -> str:
        """文件后缀"""
        return self.__extension

    @property
    def purename_extension(self):
        """纯文件名 + 后缀"""
        return self.__purename, self.__extension

    @property
    def absolute_path(self) -> str:
        """绝对路径"""
        return self._absolute_path

    @property
    def relative_path(self, base_dir: str | Path = None) -> str:
        """
        相对路径，相对于base_dir
        Args:
            base_dir:基础路径
        """
        if base_dir is None:
            return self._relative_path
        else:
            return os.path.relpath(self._absolute_path, str(base_dir))

    @property
    def hash_all(self):
        """总哈希值"""
        if self.__hash is None:
            self.__hash = self.chash()
        return self.__hash

    @property
    def ftype(self):
        return self.__type

    @ftype.setter
    def ftype(self, t):
        if isinstance(t, self.Type):
            self.__type = t

    def copy_to(self, dist: str | Path, rename: str = None, if_print = False):
        """
        复制文件到dist
        Args:
            dist:输入的路径
            rename:重命名文件，只有当dist为path时才有效
            if_print:是否打印
        """
        try:
            # 输出成功信息
            if os.path.isdir(dist):

                # 目标是目录时，拼接完整目标路径
                target_full_path = os.path.join(str(dist), self.__filename if rename is None else rename)
            else:
                target_full_path = str(dist)
            # 复制文件（保留元数据）
            shutil.copy2(self._absolute_path, target_full_path)
            if if_print:
                print(f"文件复制成功：{self._relative_path} ---> {target_full_path}")
            return True

        except Exception as e:
            print(f"文件复制失败：{str(e)}")
            return False

    @property
    def parent_dir(self) -> str:
        """获取文件的上级路径"""
        try:
            return parent_dir(self._absolute_path)[0]
        except Exception as e:
            raise e

    def top_parent_dir(self, top_dir: str | Path) -> str:
        """
        获取顶级的文件路径
        Args:
            top_dir:顶级文件夹
        """
        return get_top_parent_dir(top_dir, self._absolute_path)


class BaseFolder:
    """基础的文件夹"""

    def __init__(
        self,
        root_dir: str | Path,
        extensions: list[str] | tuple[str] | None = None):
        """
        Args:
            root_dir:根目录
            extensions:限制后缀名称
            # base_dir:基于基础目录
        """
        self._root_dir = os.path.abspath(root_dir)
        """根地址"""
        self.__all_filepaths: list[str] = []
        """_root_dir同源下的文件"""
        self.__isfile = False
        """是否为文件"""
        self.__children: list['BaseFolder'] | None = self._get_children(extensions)
        """子文件夹/子文件"""

    def _get_children(self, extensions: list[str] | tuple[str] | None) -> list['BaseFolder'] | None:
        """
        获取子文件/路径
        This fucking function is so stupid!
        But it works well!
        """
        ch: list['BaseFolder'] = []
        self.__all_filepaths.clear()
        if os.path.isfile(self._root_dir):
            self.__isfile = True
            self.__all_filepaths.append(self._root_dir)
            return None
        str_ch = os.listdir(self._root_dir)
        if len(str_ch) == 0: return None
        for pn in str_ch:
            if pn.startswith(("~$", "__M", "._")) or (pn.startswith("#") and pn.endswith("#")):
                continue
            if (extensions is not None) and (not get_purename_extension(pn)[1] in extensions):
                continue
            bf = BaseFolder(f"{self._root_dir}/{pn}")
            self.__all_filepaths.extend(bf.__all_filepaths)
            ch.append(bf)
        return ch

    @property
    def children(self) -> list['BaseFolder']:
        """获取子BaseFolder"""
        return self.__children

    @property
    def children_paths(self):
        """获取子路径"""
        if self.__children is None:
            return None
        ps = []
        for child in self.__children:
            ps.append(child._root_dir)
        return ps

    @property
    def all_filepaths(self, extensions: list[str] | tuple[str] | None = None) -> list[str]:
        """
        输出此文件夹下的所有的文件，包含嵌套
        Args:
            extensions:文件的后缀限制
        """
        outlist = []
        if extensions is None:
            return copy.deepcopy(self.__all_filepaths)
        for fp in self.__all_filepaths:
            if get_purename_extension(fp)[1] in extensions:
                outlist.append(fp)
        return outlist

    @property
    def root_dir(self) -> str:
        return self._root_dir

    @property
    def isfile(self) -> bool:
        return self.__isfile

    @property
    def isdir(self) -> bool:
        return not self.__isfile

    def has_path(self, path: str) -> bool:
        """
        判断一个路径是否在这个文件夹中
        Args:
            path:输入的要比较的路径
        """
        abp = os.path.abspath(path)
        return abp in self.all_filepaths

    def copy_to(self, dist: str | PathLike, if_print: bool = True):
        """使用请求函数进行复制，复制到文件夹dist"""
        safe_copy_any(self._root_dir, dist, if_print = if_print)
