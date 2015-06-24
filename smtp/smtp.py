import argparse
import smtplib
from base64 import b64encode
import logging as log
import os
import ssl

def get_args():
    parser = argparse.ArgumentParser(description="DNS server")
    parser.add_argument(
        "--server",
        default="smtp.rambler.ru",
        help="smtp server")
    parser.add_argument(
        "--port",
        help="Port",
        default=25, type=int)
    parser.add_argument(
        "--username",
        help="Username for EHLO",
        default='evil-hacker')
    parser.add_argument(
        "login",
        help="Sender email addres (login)"
    )
    parser.add_argument(
        "password",
        help="Password"
    )
    parser.add_argument(
        "receiver",
        help="Receiver email addres"
    )
    parser.add_argument(
        "--subject",
        "-s",
        help="Message subject"
    )
    parser.add_argument(
        "--text",
        "-t",
        help="Message text"
    )
    parser.add_argument(
        "--path",
        "-p",
        help="Path for attachment"
    )
    args = parser.parse_args()
    return args

def get_binary_from(path):
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'rb') as file:
            content = b''
            for lines in file:
                content += lines
            yield (filename, b64encode(content).decode('utf-8'))

def create_message(sender, receiver, subject, text, path):
    mail_subject = '=?UTF-8?B?' + b64encode(subject.encode('utf-8')).decode('utf-8') + '?='
    mail_text = b64encode(text.encode('utf-8')).decode('utf-8')

    body = "Mime-Version: 1.0\n"
    body += "Content-Type: multipart/mixed; boundary=\"my_bound\"\n\n"
    body += '--my_bound\nContent-Type: text/plain;\n\tcharset=\"UTF-8\"\nContent-Transfer-Encoding: base64\n\n' + mail_text + '\n'

    for _, binary in enumerate(get_binary_from(path)):
        body += '--my_bound\nContent-Type: application/octet-stream; name=' + binary[0] + '\n'
        body += "Content-Transfer-Encoding: base64\n"
        body += 'Content-Disposition: inline; filename=' + binary[0] + '\n\n'
        body += binary[1] + '\n'
    body += "\n--my_bound--\n"

    msg = '''From:{}
To:{}
Subject:{}
{}
.
'''.format(sender, receiver, mail_subject, body)
    return msg

def main(args):
    try:
        client = smtplib.dial_sec(args.server, args.port, args.username)
        smtplib.auth(client, args.login, args.password)
        msg = create_message(args.login, args.receiver, args.subject, args.text, args.path)
        smtplib.send_mail(client, args.login, args.receiver, msg)
        smtplib.quit(client)
    except smtplib.SMTPError as e:
        log.error(e)

if __name__ == "__main__":
    args = get_args()
    main(args)
