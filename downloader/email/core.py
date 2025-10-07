import imaplib
import os
import re
from datetime import datetime, timedelta
import logging
import traceback

from ..config.core import load_config

# 配置日志
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler("email_download.log", encoding = 'utf-8'),
        logging.StreamHandler()
    ]
)


def decode_mime_header(header):
    """解码邮件头信息"""
    try:
        from email.header import decode_header
        decoded = decode_header(header)
        result = []
        for part, encoding in decoded:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or 'utf-8'))
                except:
                    result.append(part.decode('utf-8', errors = 'replace'))
            else:
                result.append(part)
        return ''.join(result)
    except Exception as e:
        logging.error(f"解码头信息失败: {str(e)}")
        return str(header)


def extract_sender_email(from_header):
    """从发件人信息中提取纯邮箱地址"""
    if not from_header:
        return "unknown_sender"

    try:
        # 尝试匹配格式: 姓名 <email@example.com>
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1).strip()

        # 尝试匹配纯邮箱地址
        match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', from_header)
        if match:
            return match.group(1).strip()

        # 如果都无法匹配，返回原始信息（清理无效字符）
        cleaned = re.sub(r'[<>"]', '', from_header)
        return cleaned.strip()[:50]  # 限制长度
    except Exception as e:
        logging.error(f"提取发件人邮箱失败: {str(e)}")
        return "unknown_sender"


def setup_imap_id(conn, email_user):
    """设置IMAP ID信息，特别是对于网易邮箱需要此步骤"""
    try:
        # 添加ID命令到IMAP协议支持列表
        imaplib.Commands['ID'] = ('AUTH',)

        # 准备客户端身份信息
        id_args = '("name" "Python-Email-Downloader" "contact" "%s" "version" "1.0.0" "vendor" "Python-Script")' % email_user

        # 发送ID命令
        typ, dat = conn._simple_command('ID', id_args)
        logging.info(f"IMAP ID设置响应: {typ}")
        return True
    except Exception as e:
        logging.warning(f"设置IMAP ID失败: {str(e)}")
        return False


def validate_and_format_imap_date(date_str):
    """验证和格式化IMAP日期格式"""
    try:
        # 解析日期
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        # 转换为IMAP要求的格式: DD-Mmm-YYYY HH:MM:SS
        # 注意：月份必须是英文缩写且大写
        imap_date = date_obj.strftime('%d-%b-%Y %H:%M:%S').upper()
        logging.info(f"转换后的IMAP日期格式: {imap_date}")
        return imap_date
    except ValueError as e:
        logging.error(f"日期格式错误: {str(e)}")
        raise ValueError(f"日期格式应为 'YYYY-MM-DD HH:MM:SS': {date_str}")


def download_attachments(p):
    """主函数：下载邮件附件"""
    mail = None
    failed_downloads = []

    try:
        # 加载配置
        config = load_config(p)

        email_user = config['email']['address']
        email_pass = config['email']['authorization_code']
        imap_server = config['email']['imap_server']
        start_date = config['download']['start_date']
        end_date = config['download']['end_date']

        # 创建基础保存目录
        base_dir = config['download'].get('save_dir', './attachments')
        os.makedirs(base_dir, exist_ok = True)

        logging.info(f"开始连接IMAP服务器: {imap_server}")

        # 连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        logging.info("登录成功")

        # 设置IMAP ID (特别是网易邮箱需要)
        if '163.com' in imap_server or '126.com' in imap_server:
            logging.info("检测到网易邮箱，设置IMAP ID信息")
            setup_imap_id(mail, email_user)

        # 关键步骤：先选择邮箱文件夹
        mailbox = config['download'].get('mailbox', 'INBOX')
        status, data = mail.select(mailbox)
        if status != 'OK':
            logging.error(f"选择邮箱 '{mailbox}' 失败: {data}")
            raise Exception(f"无法选择邮箱: {mailbox}")

        logging.info(f"已选择邮箱: {mailbox}, 共有 {data[0].decode()} 封邮件")

        # 验证和格式化日期
        imap_start = validate_and_format_imap_date(start_date)
        imap_end = validate_and_format_imap_date(end_date)

        # 构建搜索条件 - 使用正确的引号格式
        search_criteria = f'(SINCE "{imap_start}" BEFORE "{imap_end}")'
        logging.info(f"搜索条件: {search_criteria}")

        # 执行搜索
        status, messages = mail.search(None, search_criteria)

        if status != 'OK':
            logging.error(f"邮件搜索失败: {messages}")
            return

        email_ids = messages[0].split()
        logging.info(f"找到 {len(email_ids)} 封符合条件的邮件")

        # 后续处理逻辑保持不变...
        # [这里是你原来的邮件处理和附件下载代码]

    except Exception as e:
        error_msg = f"程序执行失败: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        failed_downloads.append({
            'sender'   : '系统错误',
            'filename' : 'N/A',
            'error'    : str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    finally:
        # 关闭连接
        if mail:
            try:
                mail.close()
                mail.logout()
                logging.info("IMAP连接已关闭")
            except Exception as e:
                logging.error(f"关闭连接时出错: {str(e)}")

        # 记录下载失败的情况
        if failed_downloads:
            failed_file = os.path.join(base_dir, 'failed_downloads.txt')
            with open(failed_file, 'w', encoding = 'utf-8') as f:
                f.write("下载失败的附件列表:\n")
                f.write("=" * 50 + "\n")
                for item in failed_downloads:
                    f.write(f"时间: {item['timestamp']}\n")
                    f.write(f"发件人: {item['sender']}\n")
                    f.write(f"附件: {item['filename']}\n")
                    f.write(f"错误: {item['error']}\n")
                    f.write("-" * 30 + "\n")

            logging.warning(f"有 {len(failed_downloads)} 个附件下载失败，详情见 {failed_file}")
        else:
            logging.info("所有附件下载成功，无失败记录")

        logging.info("附件下载任务完成")
