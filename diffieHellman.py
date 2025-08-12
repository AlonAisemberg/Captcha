import secrets

# publicly known values for generating the key
p = 883
g = 7

class DiffieHellman:
    def __init__(self):
        '''
        initialize Diffie Hellman key exchange
        '''
        # generate a private key
        self.private_key = secrets.randbelow(10 ** 2)
        # calculate the public key
        self.public_key = (g ** self.private_key) % p


    def get_public_key(self):
        '''
        :return: public key
        '''
        return self.public_key


    def generate_shared_key(self, other_public_key):
        '''
        generate the shared secret key using the other party's public key
        :return: shared secret key
        '''
        return other_public_key ** self.private_key % p