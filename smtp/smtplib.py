from base64 import b64encode
import socket
import ssl
import re
import logging as log

log.basicConfig(level=log.INFO)

BUFFER_SIZE = 4096
CODE_REGEXP = re.compile('(\d{3})')

class SMTPError(Exception):
    pass

def _get_code(answer):
    matcher = CODE_REGEXP.search(answer.decode('utf-8'))
    if matcher.group():
        return int(matcher.group())
    else:
        return -1

def dial(addr, port, user):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((addr, port))
    log.info(sock.recv(BUFFER_SIZE))
    log.debug('SENT TO SERVER "EHLO {}"'.format(user))
    sock.send(bytes('EHLO {}\n'.format(user), 'utf-8'))

    message = sock.recv(BUFFER_SIZE)

    if _get_code(message) != 250:
        raise SMTPError('Hello error: {}'.format(message))
    else:
        log.info('Server accept EHLO')

    return sock

def dial_sec(addr, port, user):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = ssl.wrap_socket(sock)
    sock.settimeout(1)
    sock.connect((addr, port))
    log.info(sock.recv(BUFFER_SIZE))
    log.debug('SENT TO SERVER "EHLO {}"'.format(user))
    sock.send(bytes('EHLO {}\n'.format(user), 'UTF-8'))

    message = sock.recv(BUFFER_SIZE)

    if _get_code(message) != 250:
        raise SMTPError('Hello error: {}'.format(message))
    else:
        log.info('Server accept EHLO')

    return sock

def auth(sock, username, pswd):
    log.debug('SENT TO SERVER: "AUTH LOGIN"')
    sock.send(b'AUTH LOGIN\n')
    message = sock.recv(BUFFER_SIZE)

    if _get_code(message) != 334:
        raise SMTPError('Auth error: {}'.format(message))
    else:
        log.info('Server waits username')

    sock.send(b64encode(username.encode('utf-8')) + b'\n')
    log.debug('SENT TO SERVER: {}'.format(username))
    message = sock.recv(BUFFER_SIZE)

    if _get_code(message) != 334:
        raise SMTPError('Auth error: {}'.format(message))
    else:
        log.info('Username was accepted')
        log.info('Server waits password')

    sock.send(b64encode(pswd.encode('utf-8')) + b'\n')
    log.debug('SENT TO SERVER: {}'.format(pswd))
    message = sock.recv(BUFFER_SIZE)

    if _get_code(message) != 235:
        raise SMTPError('Auth error: {}'.format(message))
    else:
        log.info('235 Authentication succeeded')

def send_mail(sock, sender, receiver, msg):
    sock.send(b'mail from: ' + sender.encode('utf-8') + b'\n')
    log.debug('SENT TO SERVER: "mail from: {}"'.format(sender))
    message = sock.recv(BUFFER_SIZE)
    if _get_code(message) != 250:
        raise SMTPError('Error in the sender\'s mailbox: {}'.format(message))

    sock.send(b'rcpt to: '+ receiver.encode('utf-8') + b'\n')
    log.debug('SENT TO SERVER: "rcpt to: {}"'.format(receiver))
    message = sock.recv(BUFFER_SIZE)
    if _get_code(message) != 250:
        raise SMTPError('Error in the recipient\'s mailbox: {}'.format(message))

    sock.send(b'data\n')
    log.debug('SENT TO SERVER: data')
    message = sock.recv(BUFFER_SIZE)
    if _get_code(message) != 354:
        raise SMTPError(message)

    sock.send(msg.encode('utf-8') + b'\n')
    sock.send(b'.\n')
    log.info('SEND MAIL OK')

def quit(sock):
    sock.send(b'QUIT\n')
    sock.close()
