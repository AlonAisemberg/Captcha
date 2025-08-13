import math
import threading
from io import BytesIO
import ClientComm
import clientProtocol
import queue
import pygame
import sys
import ipaddress
import base64
import tempfile
import os

# ip of server
SERVER_IP = "127.0.0.1"

# port
PORT = 900

# check validity of server ip
try:
    ipaddress.ip_address(SERVER_IP)
except Exception:
    sys.exit("Invalid IP entered.")

# initialize pygame
pygame.init()

# set display and program caption
SCREEN_DIMENSIONS = (1280, 720)
screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
pygame.display.set_caption("Captcha")

# load pygame clock
clock = pygame.time.Clock()

# load images
background_img = pygame.image.load("graphics/background.png")
img_slots = pygame.image.load("graphics/imgslots.png")
IMG_SLOTS_POSITION = (384, 74)
pass_img = pygame.image.load("graphics/pass.png")
fail_img = pygame.image.load("graphics/fail.png")
END_IMG = fail_img
END_IMG_POSITION = (509, 229)

# load font
font_rubik_48 = pygame.font.Font("Rubik-Medium.ttf", 48)

# guess text
GUESS_TEXT = "Click on the rotten fruit"
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

# button overlays
hover_overlay = pygame.Surface((160, 160), pygame.SRCALPHA)
hover_overlay.fill((150, 150, 150, 60))
click_overlay = pygame.Surface((160, 160), pygame.SRCALPHA)
click_overlay.fill((50, 50, 50, 100))

# loading bar stuff
loading_background_bar = pygame.Rect(538, 349, 205, 22)
LOADING_BACKGROUND_BAR_COLOR = (74, 98, 116)
loading_fill = pygame.Rect(538, 349, 0, 22)
LOADING_FILL_COLOR = (198, 230, 255)
loading_bar_outline = pygame.image.load("graphics/loading_outline.png")
LOADING_OUTLINE_POSITION = (535, 346)
INCREMENT_PER_IMAGE = 23

# current state of the program (waiting, guessing, done)
state = ['waiting']

# pass or fail status
end_status = ['']

# index of current clicked button
clicked_index = -1

# index of current hovered over button
hovering_index = -1

def get_img(comm, data):
    '''
    handle receiving an image from the server
    :param comm: communications client
    :param data: image date
    '''
    # check that image data was received
    if not data:
        print("No image data received")
    else:
        # extract the base64 image string
        b64_img_str = data[0]

        # decode the base64 string into raw bytes
        try:
            img_bytes = base64.b64decode(b64_img_str)
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
        else:
            # load the image from bytes into a pygame surface
            img_file = BytesIO(img_bytes)
            try:
                image_surface = pygame.image.load(img_file).convert_alpha()
            except Exception as e:
                print(f"Error loading image into pygame surface: {e}")
            else:
                # store the successfully loaded image
                received_images.append(image_surface)

                # increase the loading bar length
                loading_fill.width += INCREMENT_PER_IMAGE


def get_end_status(comm, data):
    '''
    get end status from server and set the state of the client to done
    :param comm: communications client
    :param data: end status (pass/fail)
    '''
    state[0] = 'done'
    end_status[0] = data[0]


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
            # wait for images
            while len(received_images) < 9 and state[0] == 'waiting':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        close()

                # display background
                screen.blit(background_img, (0, 0))

                # display loading bar
                pygame.draw.rect(screen, LOADING_BACKGROUND_BAR_COLOR, loading_background_bar)
                pygame.draw.rect(screen, LOADING_FILL_COLOR, loading_fill)
                screen.blit(loading_bar_outline, LOADING_OUTLINE_POSITION)

                # update display
                pygame.display.update()

            # check if actually waiting and not done
            if state[0] == 'waiting':
                # get input
                state[0] = 'guessing'
                while state[0] == 'guessing':
                    # display background
                    screen.blit(background_img, (0, 0))

                    # display fruit images
                    screen.blit(img_slots, IMG_SLOTS_POSITION)
                    for i, img in enumerate(received_images):
                        screen.blit(img, img_positions[i])

                    # display guess text
                    display_text(GUESS_TEXT, font_rubik_48, WHITE, GUESS_TEXT_POS)

                    # check if the mouse cursor is on a fruit img
                    hovering_index = -1
                    for i, pos in enumerate(img_positions):
                        bottom_right = tuple(a + b - 1 for a, b in zip(pos, FRUIT_IMG_SIZE))
                        if check_button(pos, bottom_right, pygame.mouse.get_pos()):
                            hovering_index = i
                            break


                    # check inputs
                    for event in pygame.event.get():
                        # check for quit
                        if event.type == pygame.QUIT:
                            close()
                        # check if fruit img clicked
                        elif hovering_index != -1 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            clicked_index = hovering_index
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            # check if the mouse is released on the fruit img that was clicked
                            if hovering_index != -1 and clicked_index == hovering_index:
                                # clear fruit images list
                                received_images.clear()

                                # reset loading bar
                                loading_fill.width = 0

                                # send guess
                                myComm.send_msg(clientProtocol.send_guess(clicked_index))

                                # exit both loops
                                state[0] = 'waiting'
                            # reset clicked index
                            clicked_index = -1

                    # check if a fruit is being hovered over but not clicked, and apply overlay
                    if clicked_index == -1 and hovering_index != -1:
                        pos = img_positions[hovering_index]
                        screen.blit(hover_overlay, pos)
                    # check if a fruit is being clicked, and apply overlay
                    elif clicked_index != -1:
                        pos = img_positions[clicked_index]
                        screen.blit(click_overlay, pos)

                    # update display
                    pygame.display.update()

        elif state[0] == 'done':
            # set pass/fail image
            if end_status[0] == 'pass':
                END_IMG = pass_img
            else:
                END_IMG = fail_img

            # display background
            screen.blit(background_img, (0, 0))

            # display pass graphics
            screen.blit(END_IMG, END_IMG_POSITION)

            # update display
            pygame.display.update()

            for event in pygame.event.get():
                # check for quit
                if event.type == pygame.QUIT:
                    close()




    # handle exit and disconnect
    close()