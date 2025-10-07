import yaml
import os
from cryptography.fernet import Fernet
from typing import Dict, List


class YamlEncryptor:
    def __init__(self, key_path: str = "secret.key", load: bool = True):
        """
        初始化YAML加密器
        :param key_path: 密钥文件路径（默认secret.key）
        """
        self.key_path = key_path
        self.fernet = None
        # 加载密钥（若不存在则提示生成）
        if load:
            self._load_key()

    def generate_key(self) -> None:
        """生成加密密钥（仅需执行一次）"""
        if os.path.exists(self.key_path):
            print(f"密钥文件 {self.key_path} 已存在，无需重复生成")
            return
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as f:
            f.write(key)
        # 限制密钥文件权限（仅当前用户可读）
        os.chmod(self.key_path, 0o600)
        print(f"密钥已生成：{self.key_path}（请妥善保管，勿提交到代码仓库）")

    def _load_key(self) -> None:
        """加载密钥（内部方法）"""
        if not os.path.exists(self.key_path):
            raise FileNotFoundError(
                f"未找到密钥文件 {self.key_path}，请先调用 generate_key() 生成"
            )
        with open(self.key_path, "rb") as f:
            key = f.read()
        self.fernet = Fernet(key)

    def _get_nested_value(self, data: Dict, key_path: str) -> tuple:
        """
        获取嵌套字典中指定路径的值（内部方法）
        :param data: YAML解析后的字典
        :param key_path: 字段路径（如 "db.password"）
        :return: (父字典, 最后一级字段名, 原始值)
        """
        parts = key_path.split(".")
        current = data
        for part in parts[:-1]:
            if part not in current:
                raise KeyError(f"YAML中未找到字段路径：{key_path}（缺失层级：{part}）")
            current = current[part]
        last_part = parts[-1]
        if last_part not in current:
            raise KeyError(f"YAML中未找到字段：{key_path}")
        return current, last_part, current[last_part]

    def encrypt_fields(self, yaml_path: str, sensitive_fields: List[str]) -> None:
        """
        加密YAML中的敏感字段
        :param yaml_path: YAML文件路径
        :param sensitive_fields: 需加密的字段路径列表（如 ["db.password", "api.key"]）
        """
        # 读取YAML
        with open(yaml_path, "r", encoding = "utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}

        # 加密指定字段
        for field in sensitive_fields:
            parent, last_part, original_value = self._get_nested_value(data, field)
            # 若已加密则跳过（避免重复加密）
            if isinstance(original_value, str) and original_value.startswith("ENC(") and original_value.endswith(")"):
                print(f"字段 {field} 已加密，跳过")
                continue
            # 加密并标记为密文（便于识别）
            encrypted = self.fernet.encrypt(str(original_value).encode("utf-8")).decode("utf-8")
            parent[last_part] = f"ENC({encrypted})"  # 增加标识，区分密文/明文

        # 保存加密后的YAML
        with open(yaml_path, "w", encoding = "utf-8") as f:
            yaml.dump(data, f, sort_keys = False, allow_unicode = True)  # 保留原顺序和中文
        print(f"已加密字段：{sensitive_fields}，结果保存至 {yaml_path}")

    def decrypt_fields(self, yaml_path: str, sensitive_fields: List[str]) -> Dict:
        """
        解密YAML中的敏感字段（返回解密后的字典，不修改原文件）
        :param yaml_path: YAML文件路径
        :param sensitive_fields: 需解密的字段路径列表
        :return: 解密后的配置字典
        """
        with open(yaml_path, "r", encoding = "utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}

        # 解密指定字段
        for field in sensitive_fields:
            parent, last_part, encrypted_value = self._get_nested_value(data, field)
            # 提取密文（去除ENC()标记）
            if not (
                    isinstance(encrypted_value, str) and encrypted_value.startswith("ENC(") and encrypted_value.endswith(")")):
                print(f"字段 {field} 未加密，跳过")
                continue
            ciphertext = encrypted_value[4:-1]  # 去掉"ENC("和")"
            decrypted = self.fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
            parent[last_part] = decrypted

        return data
