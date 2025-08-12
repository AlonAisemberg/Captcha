import threading
from io import BytesIO

import ClientComm
import clientProtocol
import queue
import pygame
import sys
from shared import *
import ipaddress

import base64
import tempfile
import os

SERVER_IP = "127.0.0.1"

try:
    ipaddress.ip_address(SERVER_IP)
except Exception:
    sys.exit("Invalid IP entered.")

pygame.init()

# set display and program caption
SCREEN_DIMENSIONS = (1280, 720)
screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
pygame.display.set_caption("Captcha")

# load pygame clock
clock = pygame.time.Clock()

# load images
BACKGROUND_IMG = pygame.image.load("graphics/background.png")
IMG_SLOTS = pygame.image.load("graphics/imgslots.png")
IMG_SLOTS_POSITION = (384, 74)

# load font
FONT_RUBIK_48 = pygame.font.Font("Rubik-Medium.ttf", 48)

# guess text
GUESS_TEXT = "Click on the rotten fruit."
GUESS_TEXT_POS = (365, 620)

# fruit images
received_images = []

# size of fruit images
FRUIT_IMG_SIZE = (160, 160)

# image positions
img_positions = [
    (392, 82),
    (560, 82),
    (728, 82),
    (392, 250),
    (560, 250),
    (728, 250),
    (392, 418),
    (560, 418),
    (728, 418),
]

# color constants
WHITE = (255, 255, 255)

# current state of the program (waiting, guessing, done)
state = ['waiting']

def get_img(comm, data):
    '''

    :param comm:
    :param data:
    :return:
    '''
    if not data:
        print("No image data received")
        return

    b64_img_str = data[0]
    try:
        img_bytes = base64.b64decode(b64_img_str)
    except Exception as e:
        print(f"Error decoding base64 image data: {e}")
        return

    img_file = BytesIO(img_bytes)
    try:
        image_surface = pygame.image.load(img_file).convert_alpha()
    except Exception as e:
        print(f"Error loading image into pygame surface: {e}")
        return

    # store the images
    received_images.append(image_surface)


def get_end_status(comm, data):
    '''

    :param comm:
    :param data:
    :return:
    '''
    end_status = data[0]

    


# dictionary of command code : command function
commands = {
    '01': get_img,
    '02': get_end_status
}


def close():
    '''
    handle closing the program
    '''
    pygame.quit()
    myComm.close_client()
    sys.exit("-exit-")


def handle_msgs(comm, recvQ):
    '''
    handle incoming messages from the server
    :param comm: communications client
    :param recvQ: queue of received messages
    '''
    while True:
        msg = recvQ.get()
        opcode, data = clientProtocol.unpack(msg)
        if opcode in commands.keys():
            commands[opcode](comm, data)


def display_text(text, font, color, position):
    '''
    display text on the screen
    :param text: string of text
    :param font: text font
    :param color: text color
    :param position: position on screen
    '''
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def check_button(button_top_left, button_bottom_right, mouse_pos):
    '''
    check if the mouse position is on a button
    :param button_top_left: top left position of button
    :param button_bottom_right: bottom right position of button
    :param mouse_pos: position of mouse
    :return: true if the mouse position is on the button, false otherwise
    '''
    # split positions into x's and y's
    left_x, top_y = button_top_left
    right_x, bottom_y = button_bottom_right
    x, y = mouse_pos

    # check if the mouse position is on the button
    return left_x < x < right_x and top_y < y < bottom_y


if __name__ == '__main__':
    msgsQ = queue.Queue()
    myComm = ClientComm.ClientComm(SERVER_IP, PORT, msgsQ)
    threading.Thread(target=handle_msgs, args=(myComm, msgsQ), daemon=True).start()



    # wait for encryption key to be set
    while not myComm.cipher:
        pass

    # main code loop
    running = True
    while running:
        if state[0] == 'waiting':
            # display background
            screen.blit(BACKGROUND_IMG, (0, 0))

            # update display
            pygame.display.update()

            # wait for images
            while len(received_images) < 9:
                pass

            # display images
            screen.blit(IMG_SLOTS, IMG_SLOTS_POSITION)

            for i, img in enumerate(received_images):
                screen.blit(img, img_positions[i])

            # clear fruit images list
            received_images.clear()

            # display guess text
            display_text(GUESS_TEXT, FONT_RUBIK_48, WHITE, GUESS_TEXT_POS)

            # update display
            pygame.display.update()

            # get input
            state[0] = 'guessing'
            while state[0] == 'guessing':
                for event in pygame.event.get():
                    # check for quit
                    if event.type == pygame.QUIT:
                        close()

                    # check for mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # check if a fruit was clicked
                        hovered_img_index = None
                        for i, pos in enumerate(img_positions):
                            bottom_right = tuple(a + b - 1 for a, b in zip(pos, FRUIT_IMG_SIZE))
                            if check_button(pos, bottom_right, event.pos):
                                # send guess
                                myComm.send_msg(clientProtocol.send_guess(i))

                                # exit both loops
                                state[0] = 'waiting'
                                break


    # handle exit and disconnect
    close()