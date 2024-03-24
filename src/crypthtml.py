from hashlib import pbkdf2_hmac
from base64 import b64encode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util import Padding

from jinja2 import Template


DESIRED_ITERATIONS = int(1024*8)
PBKDF2_KEYLEN = 32


def encrypt(plain_text: str, pass_phrase: str) -> tuple:
    iv = get_random_bytes(16)
    salt = get_random_bytes(16)
    encrypted_text = None

    aes_key = pbkdf2_hmac(
            'sha256', str(pass_phrase).encode('utf-8'), salt, DESIRED_ITERATIONS, PBKDF2_KEYLEN
        )
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    pad_text = Padding.pad(
        str(plain_text).encode('utf-8'), AES.block_size, 'pkcs7'
    )
    encrypted_text = aes_cipher.encrypt(pad_text)

    return (
        b64encode(iv).decode('utf-8'), b64encode(salt).decode('utf-8'), b64encode(encrypted_text).decode('utf-8')
    )


def main(in_html_path, pass_phrese):
    with open('./html/index.html.jinja2') as jinja2_file:
        template = Template(jinja2_file.read())
    with open(in_html_path) as in_html_file:
        plain_text = in_html_file.read()
    encrypted = encrypt(plain_text, pass_phrese)
    rendered = template.render(
        iv = encrypted[0],
        salt = encrypted[1],
        encrypted_text = encrypted[2]
    )
    with open('./out.html', mode="w") as html_file:
        html_file.write(rendered)


if __name__ == '__main__':
    import argparse
    from getpass import getpass
    parser = argparse.ArgumentParser(description='Generate Encrypted HTML.')
    parser.add_argument(
        'in_html_path', metavar='IN_HTML_PATH', type=str,
        help='HTTP URL of m3u8 file'
    )
    args = parser.parse_args()
    pass_phrese = getpass('Enter Passphrase: ')
    main(args.in_html_path, pass_phrese)
