from random import randint

import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT


############################################################

def process_input(prev_direction, prev_paused):
    game_status, direction, pause = 1, prev_direction, prev_paused
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 0 # 0 for game over, 1 for play
        if event.type == KEYDOWN:
            key = event.key
            if key == K_ESCAPE:
                game_status = 0
            elif key == pygame. K_SPACE:
                if (pause == true):
                    pause = False
                else:
                    pause = True
            elif key == pygame.K_w:
                direction = (0, -2)
            elif key == pygame.K_s:
                direction = (0, 2)
            elif key == pygame.K_a:
                direction = (-2, 0)
            elif key == pygame.K_d:
                direction = (2, 0)
    return game_status, direction, pause

############################################################

def draw_everything(screen, mybox, pellets, borders):
    screen.fill((0, 250, 100)) # dark blue
    [pygame.draw.rect(screen, (0, 0, 0), b) for b in borders] # # Deep Sky Blue
    [pygame.draw.rect(screen, (100, 100, 100), p) for p in pellets] # pink
    pygame.draw.rect(screen, (20, 90, 254), mybox) # Deep Sky Blue
    pygame.display.update()

############################################################

def create_box(dims):
    w, h = dims
    box = pygame.Rect(w / 2, h / 2, 10, 10) # start in middle of the screen
    direction = 0, 1 # start direction: down
    return box, direction

############################################################

def collide(box, boxes):
    # return True if box collides with any entity in boxes
    return box.collidelist(boxes) != -1
    
############################################################

def move(box, direction):
    return box.move(direction[0], direction[1])

############################################################

def create_borders(dims, thickness=2):
    w, h = dims
    return [pygame.Rect(0, 0, thickness, h),
            pygame.Rect(0, 0, w, thickness),
            pygame.Rect(w - thickness, 0, thickness, h),
            pygame.Rect(0, h - thickness, w, thickness),
            pygame.Rect(w-200, h-20, thickness, 50),
            pygame.Rect(w - 50, h -100, thickness, 30)]
    
############################################################

def create_pellet(dims, offset):
    w, h = dims
    return pygame.Rect(randint(offset, w - offset),
                       randint(offset, h - offset), 5, 5)

def create_pellets(dims, qty, offset=10):
    # this is the only subroutine independent of Pygame
    return [create_pellet(dims, offset) for _ in range(qty)]
    
def eat_and_replace_colliding_pellet(box, pellets, dims, offset=10):
    p_index = box.collidelist(pellets)
    if p_index != -1: # ate a pellet: grow, and replace a pellet
        pellets[p_index] = create_pellet(dims, offset)
        box.size = box.width * 1.2, box.height * 1.2
    return box, pellets
    
############################################################

pygame.init()
clock = pygame.time.Clock()

# display
dims = 400, 300
screen = pygame.display.set_mode(dims)

# game objects
borders = create_borders(dims)
pellets = create_pellets(dims, 4)
mybox, direction = create_box(dims)
pause = False

# game loop
game_status = 1 # 0 for game over, 1 for play
while game_status:

    game_status, direction, pause = process_input(direction, pause)

    if not pause:
        mybox = move(mybox, direction)
    if collide(mybox, borders):
        mybox, direction = create_box(dims)
    mybox, pellets = eat_and_replace_colliding_pellet(mybox, pellets, dims)
    
    draw_everything(screen, mybox, pellets, borders)
    
    clock.tick(50) # or sleep(.02) to have the loop Pygame-independent