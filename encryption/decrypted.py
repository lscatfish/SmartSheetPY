# -*- coding: utf-8 -*-
from encryption.base import YamlEncryptor


def decrypt_code(
    yaml_path: str,
    sensitive_fields: list[str],
    key_path: str = 'my_secret.key'):
    encryptor = YamlEncryptor(key_path = key_path)
    decrypted_config = encryptor.decrypt_fields(
        yaml_path,
        sensitive_fields = sensitive_fields
    )
    return decrypted_config


def decrypt_email_authorization_code(
    yaml_path: str,
    key_path: str = 'my_secret.key'):
    de_co = decrypt_code(
        yaml_path,
        sensitive_fields = ['email.authorization_code',],
        key_path = key_path
    )
    return de_co['email']['authorization_code']
