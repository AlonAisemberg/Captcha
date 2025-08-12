import base64
import hashlib

from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher:
    def __init__(self, key):
        '''
        initialize the AES cipher
        :param key: secret key
        '''
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        '''
        encrypts an unencrypted msg
        :param raw: unencrypted msg
        :return: encrypted msg
        '''
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        '''
        decrypts an encrypted msg
        :param enc: encrypted msg
        :return: unencrypted msg
        '''
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        '''
        applies PKCS#7 padding to the input string to match block size
        :param s: the input string to pad
        :return: the padded string
        '''
        padding_length = self.bs - len(s) % self.bs
        return s + (padding_length * chr(padding_length))

    @staticmethod
    def _unpad(s):
        '''
        removes PKCS#7 padding from a decrypted byte string
        :param s: the padded byte string
        :return: the unpadded byte string
        '''
        return s[:-ord(s[len(s) - 1:])]