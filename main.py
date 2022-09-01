#Computer science coursework prototype "Alpha". Programmed from scratch in 14 hours. The built in level currently playable is a test that everything works as it should.
from cmath import pi, rect, sin, sqrt
from distutils.spawn import spawn
from math import cos
from random import Random, getrandbits, random
import pygame
from pygame.locals import *
import time
import random as rand

#The level handler is an object of this class. 
class PhaseController():
    #Prepares to begin the game by initialising some things.
    def __init__(self, spawn_dictionary):
        self.current_phase = -1
        self.spawn_dictionary = spawn_dictionary
        self.ended = False

    #This is called every time the previous phase is registered as having ended.
    #Variables are extracted from the spawn dictionary, and used to allocate properties to each segment of the phase, and also determine the success condition.
    def initialise_phase(self):
        self.phase_complete = False
        if self.current_phase < maximum_phase:
            self.current_phase += 1
            self.main_delay = self.spawn_dictionary[self.current_phase][0][0]
            self.goal_type = self.spawn_dictionary[self.current_phase][0][1]
            self.goal = self.spawn_dictionary[self.current_phase][0][2]
            self.goal_locations = self.spawn_dictionary[self.current_phase][0][3]
            self.goal_complete = False
            self.current_segment = 1
            self.current_segment_iteration = 0
            self.current_delay = 0
            self.segments = []
            for i in range(len(self.spawn_dictionary[self.current_phase])-1):
                self.segments.append(self.spawn_dictionary[self.current_phase][i])
            if self.goal_type == "collect":
                for i in range(self.goal):
                    living_sprites.add(Objective(self.goal_locations[i][0], self.goal_locations[i][1]))
                    self.counting_down = False
            if self.goal_type == "survive":
                self.counting_down = True
        else:
            self.ended = True

    #Every frame, the timers of the current segment tick down and all neccesary sprites are created. The segments are cycled through indefinitely until the phase is over.
    #If the phase end conditions are met, it registers this and disables the main script until the next phase is set up.
    def update(self):
        if self.counting_down == True and self.goal >= 0:
            self.goal -= Delta
            if self.goal <= 0:
                self.goal_complete = True
            self.phase_complete = True
            if self.spawn_dictionary[self.current_phase] == []:
                self.ended = True
        if self.goal <= 0:
            self.goal_complete = True
            self.phase_complete = True
            if self.spawn_dictionary[self.current_phase] == []:
                self.ended = True
        if not self.ended:
            if self.main_delay > 0 or self.current_delay > 0:
                self.main_delay -= Delta
                self.current_delay -= Delta
            else:
                if self.current_segment_iteration < self.spawn_dictionary[self.current_phase][self.current_segment][1]:
                    self.current_segment_iteration += 1
                    self.entity = self.spawn_dictionary[self.current_phase][self.current_segment][2]
                    self.spawning_x = self.spawn_dictionary[self.current_phase][self.current_segment][4][0]
                    self.spawning_y = self.spawn_dictionary[self.current_phase][self.current_segment][4][1]
                    self.spawn_acc_x = self.spawn_dictionary[self.current_phase][self.current_segment][5][0]
                    self.spawn_acc_y = self.spawn_dictionary[self.current_phase][self.current_segment][5][1]
                    self.spawn_direction = self.spawn_dictionary[self.current_phase][self.current_segment][6]
                    self.spawn_speed = self.spawn_dictionary[self.current_phase][self.current_segment][7]
                    self.increment_x = self.spawn_dictionary[self.current_phase][self.current_segment][8]
                    self.increment_y = self.spawn_dictionary[self.current_phase][self.current_segment][9]
                    for i in range(self.spawn_dictionary[self.current_phase][self.current_segment][3]-1):
                        living_sprites.add(self.entity(self.spawning_x, self.spawning_y, self.spawn_acc_x, self.spawn_acc_y, self.spawn_direction, self.spawn_speed))
                        self.spawning_x += self.increment_x
                        self.spawning_y += self.increment_y
                    self.current_delay = self.spawn_dictionary[self.current_phase][self.current_segment][0]
                else:
                    self.current_segment += 1
                    self.current_segment_iteration = 0
                    if self.current_segment > len(self.segments):
                       self.current_segment = 1
#The entity you control.
class Player(pygame.sprite.Sprite):
    #The player's properties are initialised
    def __init__(self, colour, width, height, x_position, y_position):
        pygame.sprite.Sprite.__init__(self)
        self.life = 3
        self.regen_timer = 5
        self.x_position = x_position
        self.y_position = y_position
        self.sprite = pygame.image.load("player_sprite.png")
        self.rect = self.sprite.get_rect(center = (self.x_position, self.y_position))
        self.mask = pygame.mask.from_threshold(self.sprite, [255, 255, 255, 255], [255, 255, 255, 0])
        self.location = self.sprite.get_rect()
        self.location.center = x_position, y_position

    #The player is moved, and collision checks for collidable objects are made.
    def move(self, x_factor, y_factor):
        self.old_x = self.x_position
        self.old_y = self.y_position
        speed = 300*Delta
        if x_factor != 0 and y_factor != 0:
            self.x_position += x_factor.real*(1/sqrt(2))*speed
            self.y_position += y_factor.real*(1/sqrt(2))*speed
        else:
            self.x_position += x_factor.real*speed
            self.y_position += y_factor.real*speed
        self.x_position = self.x_position.real
        for object in collidable_objects:
            if self.mask.overlap_area(object.mask, ((self.x_position - object.x_position.real-41), (self.y_position.real - object.y_position.real-41))) != 0:
                self.x_position = self.old_x
        self.y_position = self.y_position.real
        for object in collidable_objects:
            if self.mask.overlap_area(object.mask, ((self.x_position - object.x_position.real-41), (self.y_position.real - object.y_position.real-41))) != 0:
                self.y_position = self.old_y
        self.location = self.x_position, self.y_position
    #The update loop handles health regeneration currently.
    def update(self):
        if self.life < 3:
            self.regen_timer -= Delta
            if self.regen_timer <= 0:
                self.life += 1
                self.regen_timer = 5
    def clean(self):
        pass

    #This method is called by a hostile sprite when it "hurts" the player. it handles damage and death of the player.
    def hit(self):
        hit_particles()
        self.life -= 1
        if self.life <= 0:
            self.kill()
            hit_particles()
            hit_particles()
            self.x_position = 5000
            self.y_position = 5000

    #This method is used by collidable objects to push the player out of the way if they run into them.
    def shove(self, x_shove, y_shove):
        self.x_position += x_shove
        self.y_position += y_shove
        self.location = self.x_position, self.y_position

class Bullet(pygame.sprite.Sprite):
    
    #This class is a parent for bullet sprites. It merely initialises some variables.
    def __init__(self, x_position, y_position, x_acceleration, y_acceleration, direction, speed):
        pygame.sprite.Sprite.__init__(self)
        self.sprite = pygame.image.load("bullet_1.png")
        self.x_position = x_position
        self.y_position = y_position
        self.direction = direction
        self.x_velocity = speed*sin(self.direction)
        self.y_velocity = speed*cos(self.direction)
        self.x_acceleration = x_acceleration
        self.y_acceleration = y_acceleration
        self.location = self.sprite.get_rect()
        self.location.center = x_position, y_position
        self.mask = pygame.mask.from_surface(self.sprite)

class BasicBullet(Bullet):
    def __init__(self, x_position, y_position, x_acceleration, y_acceleration, direction, speed):
        super().__init__(x_position, y_position, x_acceleration, y_acceleration, direction, speed)
        self.speed = speed
        self.sprite = pygame.image.load("bullet_1.png")
        self.mask = pygame.mask.from_surface(self.sprite)

    #The update method moves the bullet, and checks if it has hit the player. It also kills the bullet if the phase ends.
    def update(self):
        self.x_velocity += self.x_acceleration*Delta
        self.y_velocity += self.y_acceleration*Delta
        self.x_position += self.x_velocity*Delta
        self.y_position -= self.y_velocity*Delta
        self.location = self.x_position.real, self.y_position.real
        if self.mask.overlap_area(player.mask, ((self.x_position.real - player.x_position), (self.y_position.real - player.y_position))) != 0:
            player.hit()
            self.kill()
        if level_handler.phase_complete == True:
            bullet_particles(self.x_position.real, self.y_position.real, 1)
            self.kill()

    #This kills the bullet if it exits the screen.
    def clean(self):
        if self.x_position.real > DISPLAY_WIDTH + 12:
            self.kill()
        elif self.x_position.real < -12:
            self.kill()
        elif self.y_position.real > DISPLAY_HEIGHT + 12:
            self.kill()
        elif self.y_position.real < -12:
            self.kill()

class BigBullet(Bullet):
    def __init__(self, x_position, y_position, x_acceleration, y_acceleration, direction, speed):
        super().__init__(x_position, y_position, x_acceleration, y_acceleration, direction, speed)
        self.hasupdate = True
        self.hit_delay = 0
        self.speed = speed
        self.sprite = pygame.image.load("bullet_big.png")
        self.mask = pygame.mask.from_surface(self.sprite)
    def update(self):
        self.x_velocity += self.x_acceleration*Delta
        self.y_velocity += self.y_acceleration*Deltaddddd
        self.x_position += self.x_velocity*Delta
        self.y_position -= self.y_velocity*Delta
        if self.mask.overlap_area(player.mask, ((self.x_position.real - player.x_position), (self.y_position.real - player.y_position))) != 0:
            self.hit_delay -= Delta
            if self.hit_delay <= 0:
                player.hit()
                self.hit_delay = 0.1
        self.location = self.x_position.real, self.y_position.real
    def clean(self):
        if self.x_position.real > DISPLAY_WIDTH + 40:
            self.kill()
        elif self.x_position.real < -40:
            self.kill()
        elif self.y_position.real > DISPLAY_HEIGHT + 40:
            self.kill()
        elif self.y_position.real < -40:
            self.kill()
        
class Particle(pygame.sprite.Sprite):
    #This class handles all particle effects in the game.
    def __init__(self, sprite_name, x_position, y_position, x_velocity, y_velocity, x_acceleration, y_acceleration, rotation, rotation_change, scale, scale_change, lifetime):
        pygame.sprite.Sprite.__init__(self)
        self.rawsprite = pygame.image.load(str(sprite_name))
        self.size = self.rawsprite.get_size()
        self.scale_change = scale_change
        self.rotation_change = rotation_change
        self.rotation = rotation
        self.rawsprite = pygame.transform.rotate(self.rawsprite, self.rotation)
        self.x_position = x_position
        self.x_velocity = x_velocity
        self.x_acceleration = x_acceleration
        self.y_position = y_position
        self.y_velocity = y_velocity
        self.y_acceleration = y_acceleration
        self.scale = scale
        self.scale_change = scale_change
        self.lifetime = lifetime
        self.sprite = pygame.transform.scale(self.rawsprite, (self.size[0]*self.scale, self.size[1]*self.scale))
        self.location = self.x_position, self.y_position
    #The update function moves and transforms the particles appropriately.
    def update(self):
        self.x_velocity += self.x_acceleration*Delta
        self.x_position += self.x_velocity*Delta
        self.y_velocity += self.y_acceleration*Delta
        self.y_position += self.y_velocity*Delta
        self.sprite = pygame.transform.rotate(self.rawsprite, self.rotation_change)
        self.sprite = pygame.transform.scale(self.sprite, (self.size[0]*self.scale, self.size[1]*self.scale))
        self.scale += self.scale_change*Delta
        self.location = self.x_position, self.y_position
    #This kills the particles once they have lived their life.
    def clean(self):
        self.lifetime -= Delta
        if self.lifetime <= 0:
            self.kill()

class CollideBox(pygame.sprite.Sprite):
    #Initialises it as a collidable object.
    def __init__(self, x_position, y_position, x_acceleration, y_acceleration, direction, speed):
        pygame.sprite.Sprite.__init__(self)
        self.sprite = pygame.image.load(str("collide_box_1.png"))
        self.mask = pygame.mask.from_surface(self.sprite)
        self.rect = self.mask.get_rect(center = (x_position, y_position))
        self.x_position = x_position
        self.y_position = y_position
        self.speed = speed
        self.x_velocity = self.speed*sin(direction)
        self.y_velocity = self.speed*cos(direction)
        self.x_acceleration = x_acceleration
        self.y_acceleration = y_acceleration
        self.location = self.x_position, self.y_position
        collidable_objects.add(self)

    #Move the box, push the player out of the way if it hits.
    def update(self):
        self.x_velocity += self.x_acceleration*Delta
        self.x_position += self.x_velocity*Delta
        if self.mask.overlap_area(player.mask, ((self.x_position+41 - player.x_position), (self.y_position+41 - player.y_position))) != 0:
            player.shove(self.x_velocity*Delta, 0)
        self.y_velocity += self.y_acceleration*Delta
        self.y_position += self.y_velocity*Delta
        if self.mask.overlap_area(player.mask, ((self.x_position+41 - player.x_position), (self.y_position+41 - player.y_position))) != 0:
            player.shove(0, self.y_velocity*Delta)
        self.location = self.x_position, self.y_position

    #Kill the box if it leaves the screen.
    def clean(self):
        if self.x_position.real > DISPLAY_WIDTH + 50:
            self.kill()
        elif self.x_position.real < -50:
            self.kill()
        elif self.y_position.real > DISPLAY_HEIGHT + 50:
            self.kill()
        elif self.y_position.real < -50:
            self.kill()

    #If I ever want to make a collidebox movable by another sprite, this should do it.
    def shove(self, x_shove, y_shove):
        self.x_position += x_shove
        self.y_position += y_shove
        self.location = self.x_position, self.y_position

class Objective(pygame.sprite.Sprite):
    #This is something the player must "collect" to complete the phase.
    def __init__(self, x_position, y_position):
        pygame.sprite.Sprite.__init__(self)
        self.x_position = x_position
        self.y_position = y_position
        self.raw_sprite = pygame.image.load("goal.png")
        self.sprite = self.raw_sprite
        self.mask = pygame.mask.from_surface(self.sprite)
        self.location = x_position, y_position
        self.current_rotation = 0
        self.rotate_speed = (rand.random()-0.5)*2*pi

    #Just handles the visual side.
    def update(self):
        self.sprite = pygame.transform.rotate(self.raw_sprite, self.current_rotation)
        self.rotate_speed += (rand.random()-0.5)*pi
        self.rotate_speed = self.rotate_speed*0.98
        self.current_rotation += self.rotate_speed

    #If the player touches it, the level handler is informed and this sprite explodes.
    def clean(self):
        if self.mask.overlap_area(player.mask, ((self.x_position - player.x_position), (self.y_position - player.y_position))) != 0:
            goal_particles(self.x_position, self.y_position)
            level_handler.goal -= 1
            self.kill()

def spawn_bullet():
    living_sprites.add(BasicBullet(500, RED, 9, 9, DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, rand.randint(-2, 2), rand.randint(-2, 2), rand.randint(0, 360)))

def spawn_big_bullet():
    living_sprites.add(BigBullet(300, RED, 45, 45, DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, rand.randint(-2, 2), rand.randint(-2, 2), rand.randint(0, 360)))

def hit_particles():
    names = ["player_damage.png", "player_damage_red.png", "player_damage_white.png"]
    for i in range(15):
        living_sprites.add(Particle(names[rand.randint(0, 2)], player.x_position, player.y_position, rand.randint(-100, 100), rand.randint(-100, 100), 0, 20, 2*pi*rand.random(), rand.randint(-100, 100), 2, -0.3, 3))

def goal_particles(x_pos, y_pos):
    for i in range(15):
        living_sprites.add(Particle("goal_particle.png", x_pos, y_pos, rand.randint(-75, 75), rand.randint(-75, 75), 0, 20, 2*pi*rand.random(), rand.randint(-100, 100), 2, -0.6, 3))

def bullet_particles(x_pos, y_pos, scale):
    for i in range(8):
        living_sprites.add(Particle("bullet_particle.png", x_pos, y_pos, rand.randint(-35, 35), rand.randint(-35, 35), 0, 20, 2*pi*rand.random(), rand.randint(-100, 100), scale, -0.2, 2.5))

def draw_scene():
    #Every registered living object will be drawn.
    DISPLAY.fill((0, 0, 0))
    for entity in range(len(alive_objects)):
        DISPLAY.blit((alive_objects[entity]).sprite, (alive_objects[entity]).location)

def get_things_moving():
    #The update() and clean() methods of every living object will be run.
    for entity in range(len(alive_objects)):
        alive_objects[entity].update()
        alive_objects[entity].clean()

def get_spawn_dictionary():
    #Just a method to store the thing. I could store it externally but it's easier to interact with here.
    #delay, win type, win condition, locations
    #segment delay, iterations, entity spawned, number, location, acceleration, direction, speed, increment x, increment y
    spawn_dictionary = [
        [[2, "collect", 4, [(400,300), (1520, 300), (400,780), (1520,780)]], [0.5, 2, BasicBullet, 25, (1920,0), (0,0), 3*pi/2, 500, 0, 54], [0.5, 2, BasicBullet, 25, (0,27), (0,0), pi/2, 500, 0, 54]],
        [],
        []
    ]
    maximum_phase = 0
    return spawn_dictionary

                                       #definitions
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
                                       #main program

pygame.init()              # #   Some initialisation things I may or may not need
WHITE = (255, 255, 255)      #
RED = (255, 0, 0)            #
running = True               #
R = 1                        #
Delta = 1/120              # #

DISPLAY_WIDTH = 1920/R                                           # #   set up the screen
DISPLAY_HEIGHT = 1080/R                                            #
DISPLAY = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT)) #
pygame.display.set_caption("Alpha")                                #
DISPLAY.fill((0, 0, 0))                                            #
pygame.display.update()                                          # #

maximum_phase = 0
# All of this is initialising objects for the game, starting with the player
player_x = DISPLAY_WIDTH/2
player_y = DISPLAY_HEIGHT/2 + 500
player = Player(WHITE, 12/R, 12/R, player_x, player_y)

#set up the game clock, and object groups for sprite control.
clock = pygame.time.Clock()
objects = []
entities = []
living_sprites = pygame.sprite.Group()
collidable_objects = pygame.sprite.Group()
living_sprites.add(player)

#Here is where all the game's stages can be programmed in
spawn_dictionary = get_spawn_dictionary()

#The level handler is an object that controls all timing and spawning
level_handler = PhaseController(spawn_dictionary)
level_handler.initialise_phase()

#This is the main loop, runs every frame. Moves the player with keyboard inputs, updates the level handler, and triggers rendering and update methods of all living objects.
#It also measures how long it took to do this, and caps the frame rate to 120fps.
while running:
    player_x_move = 0
    player_y_move = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
    movement_response = {pygame.K_w: (0, -1), pygame.K_s: (0, 1), pygame.K_a: (-1, 0), pygame.K_d: (1, 0)}
    pressed = pygame.key.get_pressed()
    move = [movement_response[key] for key in movement_response if pressed[key]]
    if len(move) > 0:
        for i in range(len(move)):
            player_x_move += move[i][0]
            player_y_move += move[i][1]
    player.move(player_x_move, player_y_move)

    level_handler.update()
    if level_handler.phase_complete == True and not level_handler.ended:
        level_handler.initialise_phase()
    
    alive_objects = living_sprites.sprites()
    draw_scene()
    get_things_moving()
    pygame.display.update()

    clock.tick(120)
    Delta = clock.get_time()/1000
pygame.quit()