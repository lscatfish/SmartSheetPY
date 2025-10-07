import logging

import yaml


def load_config(config_file = 'config.yaml'):
    """从YAML文件加载配置"""
    try:
        with open(config_file, 'r', encoding = 'utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        raise
