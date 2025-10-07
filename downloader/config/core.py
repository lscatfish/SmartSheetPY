import yaml


def load_config(config_file = 'config.yaml'):
    """从YAML文件加载配置"""
    import logging
    try:
        with open(config_file, 'r', encoding = 'utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        raise


def load_config_for_email(config_file = 'config.yaml'):
    """从YAML文件加载配置"""
    import logging
    try:
        with open(config_file, 'r', encoding = 'utf-8') as file:
            config = yaml.safe_load(file)
        # 检查必要配置
        required_keys = ['email', 'download']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"配置文件中缺少必要的 '{key}' 部分")
        if 'address' not in config['email'] or 'authorization_code' not in config['email'] or 'imap_server' not in \
                config['email']:
            raise ValueError("'email' 部分必须包含 'address', 'authorization_code' 和 'imap_server'")
        if 'start_date' not in config['download'] or 'end_date' not in config['download']:
            raise ValueError("'download' 部分必须包含 'start_date' 和 'end_date'")
        return config
    except FileNotFoundError:
        logging.error(f"配置文件 '{config_file}' 未找到")
        raise
    except yaml.YAMLError as e:
        logging.error(f"解析YAML配置文件失败: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        raise
