from random import choice, randint
from time import sleep

from threading import Thread

#from common import Model

from pygame import QUIT, KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT
   
def poll(timeout=0):
    asyncore.loop(timeout=timeout, count=1)  # return right away


################### MODEL #############################

def collide_boxes(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return x1 < x2 + w2 and y1 < y2 + h2 and x2 < x1 + w1 and y2 < y1 + h1
    

class Model():
    
    cmd_directions = {'up': (0, -1),
                      'down': (0, 1),
                      'left': (-1, 0),
                      'right': (1, 0)}
    
    def __init__(self):
        self.borders = [[0, 0, 2, 300],
                        [0, 0, 400, 2],
                        [398, 0, 2, 300],
                        [0, 298, 400, 2]]
        self.pellets = [ [randint(10, 380), randint(10, 280), 5, 5] 
                        for _ in range(4) ]
        self.game_over = False
        self.mydir = self.cmd_directions['down']  # start direction: down
        self.mybox = [200, 150, 10, 10]  # start in middle of the screen
        self.pellet_count = len(self.pellets)
        
        self.check = False
        self.runs = 0
        
    def do_cmd(self, cmd, network_controller):
        if cmd == 'quit':
            self.game_over = True
        else:
            self.mydir = self.cmd_directions[cmd]
            network_controller.do_send({'input': cmd})
            
    def update(self, data):
        # move me
#         self.mybox[0] += self.mydir[0]
#         self.mybox[1] += self.mydir[1]
        self.runs += 1
        if self.runs > 1:
            old_size = self.mybox
            old_pellets = self.pellets
            self.check = True
        
        self.pellets = data['pellets']
        self.borders = data['borders']
        self.myname = data['myname']
        self.mybox = data['players'][self.myname]
        
        if (self.check == True and old_size[2] != self.mybox[2] and old_size[-1] != self.mybox[-1]):
            for i in range(0, len(old_pellets)):
                for i2 in range(0, len(old_pellets[0])):
                    if (old_pellets[i][i2] != self.pellets[i][i2]):
                        print('Pellet Eaten')
                        return
        

################### HANDLER ################################
import asynchat
import asyncore
import json
import os
import socket

# {'players': {'1': [60, 188, 10, 10]},
# 'borders': [[0, 0, 2, 300], [0, 0, 400, 2], [398, 0, 2, 300], [0, 298, 400, 2]],
# 'pellets': [[263, 65, 5, 5], [335, 188, 5, 5], [45, 211, 5, 5], [150, 157, 5, 5]],
# 'myname': '1'}



class NetworkController(asynchat.async_chat):
    
    def __init__(self, host, port, model, sock=None):
        if sock:  # passive side: Handler automatically created by a Listener
            asynchat.async_chat.__init__(self, sock)
        else:  # active side: Handler created manually
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
            asynchat.async_chat.__init__(self, sock)
            self.connect((host, port))  # asynchronous and non-blocking
        self.set_terminator('\0')
        self._buffer = []
        self.model = model
        
    def collect_incoming_data(self, data):
        self._buffer.append(data)

    def found_terminator(self):
        msg = json.loads(''.join(self._buffer))
        self._buffer = []
        self.on_msg(msg)
    
    def handle_close(self):
        self.close()
        self.on_close()

    def handle_connect(self):  # called on the active side
        self.on_open()
        
    # API you can use
    def do_send(self, msg):
        self.push(json.dumps(msg) + '\0')
        
    def do_close(self):
        self.handle_close()  # will call self.on_close
    
    # callbacks you should override
    def on_open(self):
        print('Connection Successful')
        
    def on_close(self):
        print('Connection Closed')
        self.model.game_over = True
        
    def on_msg(self, data):
        self.model.update(data)
#         print data


################### CONTROLLER #############################

class RandomBotController():
    def __init__(self, m):
        self.m = m
        self.cmds = ['up', 'down', 'left', 'right']
        
    def poll(self):
        self.m.do_cmd(choice(self.cmds))
        
################### CONTROLLER #############################

class SmartBotController():
    def __init__(self, m, network):
        self.m = m
        self.network = network
        
    def poll(self):
        p = self.m.pellets[0]  # always target the first pellet
        b = self.m.mybox
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] + p[2] < b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1]:
            cmd = 'down'
        else:
            cmd = 'up'
        self.m.do_cmd(cmd, self.network)

################### CONTROLLER ###############################
class NormalController():
    def __init__(self, m, network):
        self.m = m
        self.network = network
        
    def poll(self):
        cmd = None
        for event in pygame.event.get():  # inputs
            if event.type == QUIT:
                cmd = 'quit'
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    cmd = 'quit'
                elif key == K_UP:
                    cmd = 'up'
                elif key == K_DOWN:
                    cmd = 'down'
                elif key == K_LEFT:
                    cmd = 'left'
                elif key == K_RIGHT:
                    cmd = 'right'
        if cmd:
            self.m.do_cmd(cmd, self.network)


################### CONSOLE VIEW #############################

class ConsoleView():
    def __init__(self, m):
        self.m = m
        self.frame_freq = 20
        self.frame_count = 0
        
    def display(self):
        self.frame_count += 1
        if self.frame_count == self.frame_freq:
            self.frame_count = 0
            b = self.m.mybox
            print 'Position: %d, %d' % (b[0], b[1])


################### PYGAME VIEW #############################
# this view is only here in case you want to see how the bot behaves

import pygame

class PygameView():
    
    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        b = self.m.mybox
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64))  # dark blue
        pygame.draw.rect(screen, (0, 191, 255), myrect)  # Deep Sky Blue
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red
        pygame.display.update()
    
################### LOOP #############################
model = Model()

host, port = 'localhost', 8888

network = NetworkController(host, port, model)

# c = RandomBotController(model)
c2 = SmartBotController(model, network)
#v = ConsoleView(model)
v2 = PygameView(model)



def periodic_poll():
    while 1:
        poll(200)
        #sleep(0.2)
        
thread = Thread(target=periodic_poll)
thread.daemon = True
thread.start()


while not model.game_over:
    sleep(0.02)
    c2.poll()
    #v.display()
    v2.display()
#     network.do_send('meep')