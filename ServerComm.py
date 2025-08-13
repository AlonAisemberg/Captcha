import socket
import threading
import select
import aesCipher
import diffieHellman

class ServerComm:
    def __init__(self, port, recvQ):
        '''
        initialize comms server
        :param port: port
        :param recvQ: received messages queue
        '''
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = port
        self.recvQ = recvQ
        self.open_clients = {}

        threading.Thread(target=self._mainLoop).start()

    def _mainLoop(self):
        '''
        main loop of communications server
        '''
        # open server
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(3)

        print("Server running.")

        # main loop
        while True:
            # get input
            rlist, wlist, xlist = select.select([self.server_socket] + list(self.open_clients.keys()), list(self.open_clients.keys()), [], 0.1)

            for current_socket in rlist:
                if current_socket is self.server_socket:
                    # handle connect
                    client, addr = self.server_socket.accept()

                    # check if the ip is already connected
                    current_ip = addr[0]
                    if any(ip == current_ip for ip, _ in self.open_clients.values()):
                        # close the client
                        client.close()
                        print(f"{current_ip} attempted to connect from another instance.")
                    else:
                        print(f"{current_ip} - connected")
                        # exchange key with new client
                        threading.Thread(target=self._change_key, args=(client, addr[0],)).start()
                else:
                    # handle receiving a message
                    try:
                        msg_len = int(current_socket.recv(3).decode())
                        msg = current_socket.recv(msg_len)
                    except Exception as e:
                        print(f"error in server comm recv - {e}")
                        msg = b""

                    if not msg:
                        self.close_client(self.open_clients[current_socket][0])
                    else:
                        # handle decrypting and putting the received message into recv queue
                        ip, key = self.open_clients[current_socket]
                        try:
                            decrypted_message = key.decrypt(msg)
                            self.recvQ.put((ip, decrypted_message))
                        except Exception as e:
                            print(f"Error decrypting message: {e}")
                            self.close_client(self.open_clients[current_socket][0])

    def _change_key(self, client_soc, client_ip):
        '''
        exchange key with a client
        :param client_soc: client soc
        :param client_ip: client ip
        '''
        diffie = diffieHellman.DiffieHellman()
        public_key = diffie.get_public_key()

        p_len = len(str(diffieHellman.p))
        other_public_key = ""
        try:
            client_soc.send(str(public_key).zfill(p_len).encode())
            other_public_key = int(client_soc.recv(p_len).decode())
        except Exception as e:
            print(f"error in key exchange - {e}")
            self.close_client(client_ip)

        key = diffie.generate_shared_key(other_public_key)

        # set key
        self.open_clients[client_soc] = [client_ip, aesCipher.AESCipher(str(key))]
        print(f"{client_ip} - changed key ({key})")

        # call client connected function in main server code
        self.recvQ.put((client_ip, "98"))



    def _find_socket_by_ip(self, client_ip):
        '''
        get the socket of a client by the client's ip
        :param client_ip: client ip
        :return: socket of client
        '''
        return next((socket for socket in self.open_clients.keys() if self.open_clients[socket][0] == client_ip), None)


    def _close_client(self, client_soc):
        '''
        close a client
        :param client_soc: client soc
        '''
        if client_soc in self.open_clients.keys():
            print(f'({self.open_clients[client_soc][0]}) - disconnected')
            del self.open_clients[client_soc]
            client_soc.close()


    def close_client(self, client_ip):
        '''
        close a client
        :param client_ip: client ip
        '''
        # send close client message to main server code
        self.recvQ.put((client_ip, "99"))

        client_soc = self._find_socket_by_ip(client_ip)
        self._close_client(client_soc)
        

    def send_msg(self, client_ip, msg):
        '''
        encrypt and send a message to a client
        :param client_ip: client ip
        :param msg: msg to send
        '''
        current_soc = self._find_socket_by_ip(client_ip)
        if current_soc:
            # encrypt and build full message
            encrypted_msg = self.open_clients[current_soc][1].encrypt(msg)
            full_msg = str(len(encrypted_msg)).zfill(6).encode() + encrypted_msg

            # send message
            try:
                current_soc.send(full_msg)
            except Exception as e:
                print(f"error in sending message - {e}")
                self.close_client(client_ip)
