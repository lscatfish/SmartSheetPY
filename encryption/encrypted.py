# -*- coding: utf-8 -*-
from encryption.base import YamlEncryptor


def encrypt_code(
    yaml_path: str,
    sensitive_fields: list[str],
    key_path: str = 'my_secret.key'):
    encryptor = YamlEncryptor(key_path = key_path)
    encryptor.encrypt_fields(
        yaml_path = yaml_path,
        sensitive_fields = sensitive_fields
    )


def encrypt_email_authorization_code(
    yaml_path: str,
    key_path: str = 'my_secret.key'):
    encrypt_code(
        yaml_path = yaml_path,
        sensitive_fields = ['email.authorization_code'],
        key_path = key_path
    )
