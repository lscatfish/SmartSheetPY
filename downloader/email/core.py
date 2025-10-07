import imaplib
import email
import os
from datetime import datetime, timedelta
from email.header import decode_header
import logging
import traceback

from ..config.core import load_config

# 配置日志记录
logging.basicConfig(
    filename = 'email_download.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)


def decode_mime_header(header):
    """解码邮件头信息"""
    try:
        decoded = decode_header(header)
        return ''.join(
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded
        )
    except:
        return str(header)


def download_attachments():
    """主函数：下载邮件附件"""
    # 加载配置
    config = load_config()

    email_user = config['email']['address']
    email_pass = config['email']['authorization_code']
    imap_server = config['email']['imap_server']
    start_date = config['download']['start_date']
    end_date = config['download']['end_date']

    # 创建基础保存目录
    base_dir = config['download'].get('save_dir', './attachments')
    os.makedirs(base_dir, exist_ok = True)

    # 失败记录列表
    failed_downloads = []

    try:
        # 连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select('inbox')

        # 转换日期格式为IMAP搜索格式
        imap_start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        imap_end = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days = 1)).strftime('%d-%b-%Y')

        # 搜索特定时间范围内的邮件
        search_criteria = f'(SINCE "{imap_start}" BEFORE "{imap_end}")'
        status, messages = mail.search(None, search_criteria)

        if status != 'OK':
            logging.error("邮件搜索失败")
            return

        email_ids = messages[0].split()
        logging.info(f"找到 {len(email_ids)} 封符合条件的邮件")

        # 遍历邮件
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                # 获取发件人信息
                from_header = msg.get('From', '')
                sender_email = extract_sender_email(from_header)
                sender_folder = os.path.join(base_dir, sender_email)
                os.makedirs(sender_folder, exist_ok = True)

                # 检查并下载附件
                attachments = []
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        filename = decode_mime_header(filename)
                        attachments.append((filename, part))

                if not attachments:
                    logging.info(f"邮件 {email_id.decode()} 无附件，跳过")
                    continue

                # 下载附件
                for filename, part in attachments:
                    try:
                        file_data = part.get_payload(decode = True)
                        if file_data:
                            filepath = os.path.join(sender_folder, filename)
                            with open(filepath, 'wb') as f:
                                f.write(file_data)
                            logging.info(f"成功下载: {filename} from {sender_email}")
                    except Exception as e:
                        error_msg = f"下载失败: {filename} from {sender_email}, 错误: {str(e)}"
                        logging.error(error_msg)
                        failed_downloads.append({
                            'sender'  : sender_email,
                            'filename': filename,
                            'error'   : str(e)
                        })

            except Exception as e:
                error_msg = f"处理邮件 {email_id.decode()} 时出错: {str(e)}"
                logging.error(error_msg)
                failed_downloads.append({
                    'sender'  : '未知',
                    'filename': f"邮件ID: {email_id.decode()}",
                    'error'   : str(e)
                })

    except Exception as e:
        logging.error(f"程序执行失败: {str(e)}")
        logging.error(traceback.format_exc())

    finally:
        # 关闭连接
        try:
            mail.close()
            mail.logout()
        except:
            pass

    # 记录下载失败的情况
    if failed_downloads:
        with open('failed_downloads.txt', 'w', encoding = 'utf-8') as f:
            for item in failed_downloads:
                f.write(f"发件人: {item['sender']}, 附件: {item['filename']}, 错误: {item['error']}\n")

    logging.info("附件下载完成")


def extract_sender_email(from_header):
    """从发件人头信息中提取邮箱地址"""
    try:
        # 尝试解析格式如 "姓名 <email@example.com>" 的发件人信息
        if '<' in from_header and '>' in from_header:
            start = from_header.rfind('<') + 1
            end = from_header.rfind('>')
            return from_header[start:end].strip()
        return from_header.strip()
    except:
        return "unknown_sender"


if __name__ == '__main__':
    download_attachments()
