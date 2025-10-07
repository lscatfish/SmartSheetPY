"""
产生一个密钥
"""
from encryption.base import YamlEncryptor

if __name__ == "__main__":
    # 1. 初始化加密器（指定密钥文件路径）
    encryptor = YamlEncryptor(key_path = "my_secret.key", load = False)

    # 2. 生成密钥（仅首次使用时执行，之后注释掉）
    encryptor.generate_key()
