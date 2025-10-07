"""
邮件下载器的main文件
你需要一个密钥以解密yaml文件
"""
from downloader.email.core import download_attachments

download_attachments('./input/email_yaml.yaml', 'my_secret.key')
