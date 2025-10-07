import imaplib
import email
import os
import re
from datetime import datetime, timedelta

import traceback
from sys import stderr

from downloader.config.core import load_config_for_email


def decode_mime_header(header):
    """解码邮件头信息（如主题、文件名）"""
    import logging
    if header is None:
        return None
    try:
        from email.header import decode_header
        decoded = decode_header(header)
        result = []
        for part, encoding in decoded:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or 'utf-8'))
                except UnicodeDecodeError:
                    # 如果指定编码解码失败，尝试常用编码
                    try:
                        result.append(part.decode('gbk'))
                    except UnicodeDecodeError:
                        try:
                            result.append(part.decode('gb2312'))
                        except UnicodeDecodeError:
                            # 最后尝试utf-8，忽略错误
                            result.append(part.decode('utf-8', errors = 'replace'))
            else:
                result.append(part)
        return ''.join(result)
    except Exception as e:
        logging.error(f"解码头信息 '{header}' 失败: {str(e)}")
        return str(header) if header else "unknown"


def extract_sender_email(from_header):
    """从发件人信息中提取纯邮箱地址"""
    import logging
    if not from_header:
        return "unknown_sender"

    try:
        # 尝试匹配格式: "姓名 <email@example.com>"
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1).strip()

        # 尝试匹配纯邮箱地址
        match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', from_header)
        if match:
            return match.group(1).strip()

        # 如果都无法匹配，清理并返回原始信息的一部分（用作文件夹名需确保安全）
        cleaned = re.sub(r'[<>"|?*\\/:]', '', from_header)  # 移除Windows文件名非法字符
        cleaned = cleaned.strip()
        # 如果太长，取一部分
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
        return cleaned if cleaned else "unknown_sender"
    except Exception as e:
        logging.error(f"提取发件人邮箱失败: {str(e)}")
        return "unknown_sender"


def setup_imap_id(conn, email_user):
    """
    设置IMAP ID信息，特别是对于网易邮箱需要此步骤
    参考: https://blog.csdn.net/jony_online/article/details/108638571
    """
    import logging
    try:
        # 检查Commands字典中是否已有ID命令，若无则添加
        if 'ID' not in imaplib.Commands:
            imaplib.Commands['ID'] = ('AUTH', 'SELECTED')  # 确保ID命令在AUTH和SELECTED状态下可用

        # 准备客户端身份信息 (GUID 示例，可根据需要修改)
        # 网易邮箱似乎需要此ID信息才能正常使用某些功能
        id_args = (
            "name", "PyMailDownloader",
            "version", "1.0",
            "vendor", "PythonScript",
            "contact", email_user
        )
        # 构造ID命令的参数，格式为: (("name" "PyMailDownloader") ("version" "1.0") ...)
        typ, dat = conn._simple_command('ID', '("name" "PyMailDownloader" "version" "1.0" "vendor" "PythonScript" "contact" "{}")'.format(email_user))
        logging.info(f"IMAP ID设置响应: {typ}")
        if typ != 'OK':
            logging.warning(f"IMAP ID 命令返回非OK状态: {typ}")
        return True
    except AttributeError as e:
        # 如果imaplib.Commands不可写或_simple_command不支持ID
        logging.warning(f"无法设置IMAP ID (可能IMAP库版本或服务器不支持): {str(e)}")
        return False
    except Exception as e:
        logging.warning(f"设置IMAP ID时出错: {str(e)}")
        return False


def parse_email_date(date_str):
    """尝试解析邮件头中的Date字段，返回datetime对象。"""
    import logging
    if not date_str:
        return None

    # 移除可能存在的多余括号内容，如 "(CST)"
    import re
    date_str_clean = re.sub(r'\([^)]*\)', '', date_str).strip()

    # 常见日期格式列表
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # 例如: Tue, 07 Oct 2025 22:15:18 +0800
        '%d %b %Y %H:%M:%S %z',  # 例如: 07 Oct 2025 22:15:18 +0800
        '%a, %d %b %Y %H:%M:%S',  # 例如: Tue, 07 Oct 2025 22:15:18 (无时区)
        '%Y-%m-%d %H:%M:%S',  # 例如: 2025-10-07 22:15:18
    ]

    parsed_dt = None
    for fmt in date_formats:
        try:
            parsed_dt = datetime.strptime(date_str_clean, fmt)
            # 如果解析成功且没有时区信息，将其视为本地时区
            if parsed_dt.tzinfo is None:
                # 假设邮件服务器时间与本地时间一致，或者根据需要转换为UTC
                # parsed_dt = parsed_dt.replace(tzinfo=timezone.utc) # 或者转换为UTC
                # 这里我们假设它是本地时间，并赋予本地时区（更常见的做法）
                from datetime import timezone
                import time
                # 获取本地时区偏移（秒）
                local_offset_sec = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
                local_offset = timezone(timedelta(seconds = -local_offset_sec))
                parsed_dt = parsed_dt.replace(tzinfo = local_offset)
            break  # 成功解析一种格式就退出循环
        except ValueError:
            continue

    if parsed_dt is None:
        logging.warning(f"无法解析的日期格式: {date_str}")
    return parsed_dt


def download_attachments(
    config_path = './input/email_yaml.yaml',
    key_path = 'my_secret.key'):
    """
    主函数：下载指定时间范围内的邮件附件，并按发件人邮箱地址分类保存。
    读取config.yaml配置文件。
    """
    import logging
    mail = None
    failed_downloads = []  # 记录下载失败的附件信息
    downloaded_count = 0  # 成功下载的附件计数

    try:
        # 1. 加载配置
        config = load_config_for_email(config_path, key_path)  # 默认读取 config.yaml

        email_user = config['email']['address']
        email_pass = config['email']['authorization_code']
        imap_server = config['email']['imap_server']
        start_date_str = config['download']['start_date']  # 格式: "2025-10-07 22:10:00"
        end_date_str = config['download']['end_date']  # 格式: "2025-10-07 22:21:59"

        # 解析配置中的时间，并转换为datetime对象用于比较
        try:
            start_dt_cfg = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_dt_cfg = datetime.strptime(end_date_str, '%Y-%m-%d')
            # 假设配置中的时间是本地时间，并赋予本地时区
            from datetime import timezone
            import time
            local_offset_sec = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
            local_tz = timezone(timedelta(seconds = -local_offset_sec))
            start_dt_cfg = start_dt_cfg.replace(tzinfo = local_tz)
            end_dt_cfg = end_dt_cfg.replace(tzinfo = local_tz)
        except ValueError as e:
            stderr(f"配置文件中的时间格式错误，应为 'YYYY-MM-DD HH:MM:SS': {str(e)}")
            raise

        # 创建基础保存目录
        base_dir = config['download'].get('save_dir', './attachments')
        os.makedirs(base_dir, exist_ok = True)

        # 配置日志
        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(message)s',
            handlers = [
                logging.FileHandler("./attachments/email_download.txt", encoding = 'utf-8'),
                logging.StreamHandler()
            ]
        )

        logging.info(f"附件将保存至目录: {os.path.abspath(base_dir)}")

        mailbox_name = config['download'].get('mailbox', 'INBOX')

        # 2. 连接到IMAP服务器
        logging.info(f"开始连接IMAP服务器: {imap_server}")
        mail = imaplib.IMAP4_SSL(imap_server)
        logging.info("TCP连接建立成功")

        # 3. 登录
        mail.login(email_user, email_pass)
        logging.info("登录认证成功")

        # 4. 特别处理：为网易邮箱设置IMAP ID
        if '163.com' in imap_server or '126.com' in imap_server or 'yeah.net' in imap_server:
            logging.info("检测到网易邮箱，尝试设置IMAP ID信息...")
            setup_imap_id(mail, email_user)
        # 其他邮箱服务器也可根据需要添加特殊处理

        # 5. 选择邮箱文件夹（关键步骤，进入SELECTED状态才能搜索）
        logging.info(f"选择邮箱文件夹: {mailbox_name}")
        status, data = mail.select(mailbox_name)
        if status != 'OK':
            raise Exception(f"选择邮箱文件夹 '{mailbox_name}' 失败: {data[0].decode() if data else 'Unknown error'}")
        logging.info(f"已成功选择邮箱 '{mailbox_name}'，共有 {data[0].decode()} 封邮件")

        # 6. 构建IMAP搜索条件（基于日期，不含时间）
        # IMAP的SINCE/BEFORE通常对包含时间的日期格式支持不好，这里只使用日期部分
        imap_start_date = start_dt_cfg.strftime('%d-%b-%Y').upper()  # 例如: "07-OCT-2025"
        imap_end_date = end_dt_cfg.strftime('%d-%b-%Y').upper()
        # 注意：BEFORE是排除性的，所以要下载结束日期那天的邮件，需要+1天
        # 但由于我们后面还要精确时间筛选，这里保守一点，用结束日期，然后靠本地过滤
        search_criteria = f'(SINCE "{imap_start_date}" BEFORE "{imap_end_date}")'
        # 另一种策略：获取SINCE开始日期之后的所有邮件，然后在本地过滤结束时间
        # search_criteria = f'(SINCE "{imap_start_date}")'
        logging.info(f"IMAP搜索条件 (日期范围): {search_criteria}")

        # 7. 执行IMAP搜索
        status, messages = mail.search(None, search_criteria)
        if status != 'OK':
            raise Exception(f"邮件搜索失败: {messages[0].decode() if messages else 'Unknown error'}")

        email_ids = messages[0].split()
        logging.info(f"IMAP搜索找到 {len(email_ids)} 封在日期范围内的邮件")

        if not email_ids:
            logging.info("没有找到符合条件的邮件。")
            return

        # 8. 遍历邮件，解析并精确筛选（精确到秒）
        valid_email_count = 0
        for email_id in email_ids:
            email_id_str = email_id.decode()
            try:
                # 获取邮件内容
                status, msg_data = mail.fetch(email_id, '(RFC822)')  # 获取整个邮件
                if status != 'OK':
                    logging.error(f"获取邮件ID {email_id_str} 内容失败: {msg_data[0].decode() if msg_data else 'Unknown error'}")
                    failed_downloads.append({'sender'   : 'Unknown', 'filename': f"MailID: {email_id_str}",
                                             'error'    : 'FETCH failed',
                                             'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    continue

                msg = email.message_from_bytes(msg_data[0][1])

                # 解析邮件日期并进行精确时间筛选
                email_date_str = msg.get('Date')
                email_dt = parse_email_date(email_date_str)

                if email_dt is None:
                    logging.warning(f"邮件 {email_id_str} 无法解析日期 '{email_date_str}'，跳过此邮件")
                    continue

                # 精确时间比较（本地时区，注意时区问题！）
                # 这里假设邮件日期和配置日期都是本地时区，或已处理时区转换
                # 如果email_dt是aware对象（含时区），需要与同样时区的start_dt_cfg比较，或转换时区
                # 简单处理：如果email_dt是naive，认为它是本地时区
                # 更健壮的做法是配置文件中指定时区，或将所有时间转换为UTC比较
                if email_dt < start_dt_cfg or email_dt > end_dt_cfg:
                    logging.debug(f"邮件 {email_id_str} 时间 {email_dt} 不在精确时间范围内，跳过")
                    continue

                valid_email_count += 1
                logging.info(f"处理邮件 [{email_id_str}], 发送时间: {email_dt}")

                # 提取发件人邮箱
                from_header = msg.get('From', '')
                sender_email = extract_sender_email(from_header)
                logging.debug(f"发件人提取: '{from_header}' -> '{sender_email}'")

                # 创建发件人对应的文件夹
                sender_folder = os.path.join(base_dir, sender_email)
                os.makedirs(sender_folder, exist_ok = True)

                # 遍历邮件部分，寻找附件
                attachments_in_mail = 0
                for part in msg.walk():
                    # 跳过multipart容器本身
                    if part.get_content_maintype() == 'multipart':
                        continue
                    # 检查是否有Content-Disposition头，并且是attachment（或者即使没有明确disposition，但有文件名也认为是附件）
                    disposition = part.get('Content-Disposition')
                    filename = part.get_filename()

                    if disposition is not None and 'attachment' in disposition:
                        # 明确是附件
                        pass
                    elif filename:
                        # 有文件名，但可能没有Content-Disposition，也可能内联，这里根据需求决定是否下载
                        # 本例中，只要有文件名就尝试下载
                        pass
                    else:
                        # 既不是明确附件，也没有文件名，跳过
                        continue

                    if not filename:
                        # 有些附件可能没有文件名？生成一个默认名
                        content_type = part.get_content_type()
                        ext = '.bin'
                        if 'image' in content_type:
                            ext = '.img'
                        elif 'text' in content_type:
                            ext = '.txt'
                        # ... 其他类型映射
                        filename = f"attachment_{attachments_in_mail}{ext}"

                    # 解码文件名
                    filename_decoded = decode_mime_header(filename)
                    if not filename_decoded:
                        filename_decoded = f"unnamed_attachment_{attachments_in_mail}"

                    try:
                        # 获取附件数据
                        file_data = part.get_payload(decode = True)
                        if file_data is None:
                            logging.warning(f"附件 {filename_decoded} 解码后数据为空，跳过")
                            continue

                        # 构建完整保存路径，处理同名文件
                        filepath = os.path.join(sender_folder, filename_decoded)
                        counter = 1
                        name, ext = os.path.splitext(filename_decoded)
                        while os.path.exists(filepath):
                            filepath = os.path.join(sender_folder, f"{name}_{counter}{ext}")
                            counter += 1

                        # 保存文件
                        with open(filepath, 'wb') as f:
                            f.write(file_data)

                        attachments_in_mail += 1
                        downloaded_count += 1
                        logging.info(f"  成功下载: {filename_decoded} -> {filepath}")

                    except Exception as e:
                        error_msg = f"下载附件失败: {filename_decoded} from {sender_email}, 错误: {str(e)}"
                        logging.error(error_msg)
                        failed_downloads.append({
                            'sender'   : sender_email,
                            'filename' : filename_decoded,
                            'error'    : str(e),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'mail_id'  : email_id_str
                        })

                if attachments_in_mail == 0:
                    logging.info(f"邮件 {email_id_str} 中未找到附件")

            except Exception as e:
                error_msg = f"处理邮件 {email_id_str} 时发生未预期错误: {str(e)}"
                logging.error(error_msg)
                logging.error(traceback.format_exc())
                failed_downloads.append({
                    'sender'   : 'Unknown',
                    'filename' : f"MailID: {email_id_str}",
                    'error'    : str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        logging.info(f"处理完成。共处理 {valid_email_count} 封符合时间精确要求的邮件，成功下载 {downloaded_count} 个附件。")

    except Exception as e:
        error_msg = f"程序执行过程中发生严重错误: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        failed_downloads.append({
            'sender'   : 'SYSTEM_ERROR',
            'filename' : 'N/A',
            'error'    : str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    finally:
        # 确保关闭连接
        if mail:
            try:
                mail.close()
            except Exception as e:
                logging.error(f"关闭邮箱时出错: {str(e)}")
            try:
                mail.logout()
                logging.info("IMAP连接已注销")
            except Exception as e:
                logging.error(f"注销IMAP连接时出错: {str(e)}")

    # 9. 记录下载失败的情况
    if failed_downloads:
        failed_file = os.path.join(base_dir, 'failed_downloads.txt')
        try:
            with open(failed_file, 'w', encoding = 'utf-8') as f:
                f.write("下载失败的附件列表:\n")
                f.write("=" * 60 + "\n")
                for item in failed_downloads:
                    f.write(f"失败时间: {item['timestamp']}\n")
                    f.write(f"关联邮件ID: {item.get('mail_id', 'N/A')}\n")
                    f.write(f"发件人: {item['sender']}\n")
                    f.write(f"附件名: {item['filename']}\n")
                    f.write(f"错误信息: {item['error']}\n")
                    f.write("-" * 40 + "\n")
            logging.warning(f"有 {len(failed_downloads)} 个附件下载失败，详情见: {failed_file}")
        except Exception as e:
            logging.error(f"写入失败记录文件时出错: {str(e)}")
    else:
        logging.info("恭喜！所有附件均成功下载，无失败记录。")

    logging.info("邮件附件下载任务执行完毕。")


if __name__ == '__main__':
    download_attachments()
