"""此文件用于解析遍历文件夹"""
import os


def collect_file_paths(root_dir):
    """
    递归遍历文件夹及其子目录，收集所有文件的绝对路径

    Parameters:
        root_dir: 要遍历的根文件夹路径

    Returns:
        包含所有文件绝对路径的列表
    """
    file_paths = []

    # 遍历根目录下的所有文件和子目录
    # root: 当前目录路径
    # dirs: 当前目录下的子目录列表
    # files: 当前目录下的文件列表
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # 拼接文件的绝对路径
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths


# 使用示例
if __name__ == "__main__":
    # 替换为你要遍历的文件夹路径
    target_dir = "../test_sourc"

    # 收集所有文件路径
    all_files = collect_file_paths(target_dir)

    # 打印结果
    print(f"共找到 {len(all_files)} 个文件:")
    for path in all_files:
        print(path)

class DefFolder:
    def __init__(self, root_dir):
        pass