from SmartSocket import connections
import threading

import pygame
from pygame.locals import *
pygame.init()

Event = connections.BasicEvent

CLIENT = connections.SCS_CLIENT()

ip = input("Enter IP >>> ") or connections.getLocalIP()
port = int( input("Enter Port >>> ") or 7871 )

print(f"Connecting to {ip}:{port}")
CLIENT.connect( (ip, port), )
print("Connected")

class Gamestate():
    running = False

    board = [
        [0,0,0],
        [0,0,0],
        [0,0,0]
    ]

    queue = []






icon_o = pygame.image.load('./resources/o.png')
icon_x = pygame.image.load('./resources/x.png')

display = pygame.display.set_mode([300,300])
pygame.display.set_caption("Tic Tac Toe")

running = True

CLIENT.hsend_e(Event('ready'))

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: #LMB
                bx = int(mouse_pos[0]/100)
                by = int(mouse_pos[1]/100)
                click = Event('click_tile', coord=(bx,by))
                Gamestate.queue.append(click)
    
    display.fill((240,240,240))

    # draw board
    for y in range(3):
        for x in range(3):
            rx,ry = x*100,y*100
            pygame.draw.rect(display, (255,255,255),
            (rx+2,ry+2,96,96))
            board_value = Gamestate.board[y][x]
            if board_value == 1: display.blit(icon_o, (rx+2,ry+2))
            if board_value == 2: display.blit(icon_x, (rx+2,ry+2))

    pygame.display.flip()



    for event in Gamestate.queue:
        CLIENT.hsend_e(event)
    
    Gamestate.queue = []
    
    messages, connected = CLIENT.get_new_messages(True,True)

    if not connected:
        print("Connection closed by server!")
        break
    
    for message in messages:
        if message.is_dict:
            event = Event(message)
            print(event)

            if event.is_i("update_board"):
                coord = event.get('coord')
                value = event.get('value')
                if coord is not None and value is not None:
                    Gamestate.board[coord[1]][coord[0]] = value


Gamestate.running = False
pygame.quit()
