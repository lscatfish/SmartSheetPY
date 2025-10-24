"""标准文件控制库"""
import os.path
from pathlib import Path

from SSPY.myfile import BASE_DIR

import hashlib


def calculate_file_hash(file_path, algorithm = 'md5'):
    """
    计算文件的哈希值

    参数:
        file_path: 文件的路径（绝对路径或相对路径）
        algorithm: 哈希算法，支持'md5'、'sha1'、'sha256'、'sha512'等

    返回:
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


class AFile:
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
        if not os.path.exists(path):
            return
        self.absolute_path = os.path.abspath(str(path))
        self.relative_path = os.path.relpath(self.absolute_path, base_dir)
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

        # 返回十六进制哈希值
        return hash_obj.hexdigest()

    def is_same(self, other: 'AFile') -> bool:
        """是否相同"""
        if self.is_same_path(other):  return True
        if self.__hash is None or other.__hash is None: return False
        return self.__hash == other.__hash

    def is_same_path(self, other: 'AFile') -> bool:
        """是否是相同的路径"""
        if self.absolute_path is None or other.absolute_path is None: return False
        return other.absolute_path == self.absolute_path
