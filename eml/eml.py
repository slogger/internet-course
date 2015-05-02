import argparse
import mimetypes
import base64
import os


def get_args():
    parser = argparse.ArgumentParser(description="EML packer")
    parser.add_argument(
        "path",
        help="Filename")
    parser.add_argument(
        "--debug", "-d",
        action='store_false')
    args = parser.parse_args()
    return args


def generate_eml(args):
    kwargs = dict(args._get_kwargs())
    eml = '''
From: {sender} <{sender_email}>
To: {target} <{target_email}>
Subject: =?windows-1251?B?x+Dn8+v/IM3g8uDr/P8gwujy4Ov85eLt4A==?=
    '''.format(**kwargs)
    if args.is_text:
        attach = ""
    else:
        attach = '''
Content-Type: multipart/mixed;boundary=attach
--attach
Content-Type: {mime[0]};
Content-Disposition:attachment;FileName="{filename}";
Content-Transfer-Encoding: base64

{encoded_content}
--attach--
'''.format(**kwargs)
    return(eml+attach)

def pack_text(args):
    raise Exception('Not support file')
    import magic
    blob = open(args.path).read()
    m = magic.open(magic.MAGIC_MIME_ENCODING)
    m.load()
    args.encoding = m.buffer(blob)
    print(args)

def pack_binary(args):
    with open(args.path, 'rb') as file:
        args.encoded_content = str(base64.b64encode(file.read()), 'utf-8')

    eml = generate_eml(args)
    with open('out.eml', 'w') as file:
        file.write(eml)

def main(args):
    # HACK: Что-бы при ошибке с доступом к файлу нам сообщали о ней
    with open(args.path, 'r') as file:
        pass
    args.mime = mimetypes.guess_type(args.path)
    args.filename = os.path.basename(args.path)
    args.sender = 'Senderbot'
    args.sender_email = 'sender@uprt.ru'
    args.target = 'Target'
    args.target_email = 'target@ya.ru'
    mime_check = args.mime[0][:4]
    if mime_check == 'text':
        args.is_text = True
        pack_text(args)
    else:
        args.is_text = False
        pack_binary(args)


if __name__ == '__main__':
    args = get_args()
    try:
        main(args)
    except Exception as e:
        if args.debug:
            exit(e)
        else:
            raisex
