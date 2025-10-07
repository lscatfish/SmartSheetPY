import yaml


def load_config(config_file = 'config.yaml'):
    """从YAML文件加载配置"""
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config