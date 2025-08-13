import socket
import sys
import threading

import aesCipher
import diffieHellman


class ClientComm:
    def __init__(self, server_ip, port, recvQ):
        """
        initialize comms client
        :param server_ip: server ip
        :param port: port
        :param recvQ: received message queue
        """
        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.port = port
        self.recvQ = recvQ
        self.cipher = None

        # connect to the server
        try:
            self.my_socket.connect((self.server_ip, self.port))
        except Exception as e:
            print("error in connect ", e)
            sys.exit("server down - try later")

        # exchange key with server
        self._change_key()

        threading.Thread(target=self._mainLoop,).start()


    def recv_all(self, length):
        """
        receive data from the server, this function can also be used to receive a very large amount of data that
        exceeds 1024 bytes
        :param length: length of the data
        :return: fully received data
        """
        data = b''
        while len(data) < length:
            packet = self.my_socket.recv(min(length - len(data), 1024))
            if not packet:
                raise ConnectionError("Socket closed during recv")
            data += packet
        return data



    def _mainLoop(self):
        """
        main loop of communications client
        """
        # main loop
        while True:
            # handle receiving a message
            data = b""
            try:
                length_bytes = self.recv_all(6)
                data_len = int(length_bytes.decode())
                data = self.recv_all(data_len)
            except Exception as e:
                print(f"Error in mainLoop: {e}")
                self.close_client()

            if not data:
                self.close_client()

            try:
                # handle decrypting and putting the received message into recv queue
                msg = self.cipher.decrypt(data)
                self.recvQ.put(msg)
            except Exception as e:
                print(f"Error decrypting message: {e}")
                self.close_client()


    def _change_key(self):
        """
        exchange key with the server
        """
        diffie = diffieHellman.DiffieHellman()
        public_key = diffie.get_public_key()

        p_len = len(str(diffieHellman.p))
        other_public_key = ""
        try:
            self.my_socket.send(str(public_key).zfill(p_len).encode())
            other_public_key = int(self.my_socket.recv(p_len).decode())
        except Exception as e:
            print(f"error in key exchange - {e}")
            self.close_client()

        # set key
        key = diffie.generate_shared_key(other_public_key)
        self.cipher = aesCipher.AESCipher(str(key))


    def close_client(self):
        """
        close the socket
        """
        self.my_socket.close()
        sys.exit("bye :)")


    def send_msg(self, msg):
        """
        encrypt and send a message to the server
        :param msg: msg to send
        """
        # encrypt and build full message
        encrypted_msg = self.cipher.encrypt(msg)
        full_msg = str(len(encrypted_msg)).zfill(3).encode() + encrypted_msg

        # send message
        try:
            self.my_socket.send(full_msg)
        except Exception as e:
            print(f"error in sending message - {e}")
            self.close_client()