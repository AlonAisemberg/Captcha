import os
import threading
import ServerComm
import serverProtocol
import queue
import time
import random
import sys
import pygame
from captchasession import CaptchaSession
from shared import *
import captchasession
import base64


# clock
clock = pygame.time.Clock()

# ip : captcha session
captcha_sessions = {}


def generate_captcha(comm, ip):
    '''
    choose random images and store the correct answer,
    send the random images to the client
    :param ip:
    :return:
    '''
    # choose random number as the index of the rotten fruit
    rotten = random.randint(0, 8)
    captcha_sessions[ip].current_correct_answer = rotten

    # get the paths of the fruit images into temporary lists
    clean_imgs = [f for f in os.listdir("clean") if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    rotten_imgs = [f for f in os.listdir("rotten") if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for i in range(9):
        # set folder_path and img_files
        if i == rotten:
            folder_path = "rotten"
            img_files = rotten_imgs
        else:
            folder_path = "clean"
            img_files = clean_imgs

        # get a random image path and remove it from the temporary list
        random_img = random.choice(img_files)
        img_files.remove(random_img)
        random_img_path = f"{folder_path}/{random_img}"

        # get image data
        data = None
        with open(random_img_path, "rb") as f:
            data = f.read()

        if not data:
            sys.exit("Error in read image")

        # base64 encode bytes to ASCII string
        b64_data = base64.b64encode(data).decode('ascii')

        # send image
        comm.send_msg(ip, serverProtocol.img_msg([b64_data]))


def handle_guess(comm, ip, data):
    '''

    :param comm:
    :param ip:
    :param data:
    :return:
    '''
    answer = int(data[0])

    # handle client's answer
    captcha_sessions[ip].handle_answer(answer)

    # get client's captcha session status
    session_status = captcha_sessions[ip].get_status()

    # handle session status
    if session_status == 'continue':
        generate_captcha(comm, ip)
    elif session_status == 'pass':
        comm.send_msg(ip, serverProtocol.end_msg([session_status]))
    elif session_status == 'fail':
        comm.send_msg(ip, serverProtocol.end_msg([session_status]))
        comm.close_client(ip)


def client_connected(comm, ip, data):
    '''
    handle client connecting
    :param comm: communications server
    :param ip: ip of player who connected
    :param data: none
    '''

    # add the player to the home players list
    captcha_sessions[ip] = CaptchaSession()

    # generate a captcha for the new client
    generate_captcha(comm, ip)



def remove_client(comm, ip, data):
    '''
    handle removing client
    :param comm: none
    :param ip: ip of client
    :param data: none
    '''
    del captcha_sessions[ip]


# dictionary of command code : command function
commands = {
    '01': handle_guess,
    '98': client_connected,
    '99': remove_client
}


def handle_msgs(comm, recvQ):
    '''
    handle incoming messages from the client
    :param comm: communications server
    :param recvQ: queue of received messages
    '''
    while True:
        ip, msg = recvQ.get()
        opcode, data = serverProtocol.unpack(msg)
        if opcode in commands.keys():
            commands[opcode](comm, ip, data)


if __name__ == '__main__':
    msgsQ = queue.Queue()
    myServer = ServerComm.ServerComm(PORT, msgsQ)
    threading.Thread(target=handle_msgs, args=(myServer, msgsQ)).start()

    # program loop
    running = True
    while running:
        pass

    sys.exit("-exit-")