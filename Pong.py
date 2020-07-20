#!/usr/bin/env python
#import RPi.GPIO as gpio
import os
import pygame, pygame.math
import random
import numpy
from button import Button


# --- Returns a small rectangle on the left or right face of passed rectangle
def return_face(rect, face):
    if face == "right":
        return pygame.Rect(rect.left + rect.width - 1, rect.top, 1, rect.height)
    elif face == "left":
        return pygame.Rect(rect.left, rect.top,  1, rect.height)
    else:
        return 0


# --- Paddle objects, two modes, AI or User
class Paddle:
    def __init__(self, rect, speed, io_up = 0, io_down = 0):
        self.rect = rect
        self.io_up = io_up
        self.io_down = io_down
        self.speed = speed
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.velocity = pygame.math.Vector2(0, 0)

    def move_up(self):
        self.velocity.y = -self.speed
    def move_down(self):
        self.velocity.y = self.speed
    def reset_speed(self):
        self.velocity.y = 0
    def update(self, *args):
        if len(args) == 1:
            ball_rect = args[0]

            if ball_rect.centery > self.rect.centery:
                self.velocity.y = self.speed
            elif ball_rect.centery < self.rect.centery:
                self.velocity.y = -self.speed
            else:
                self.velocity.y = 0

        self.position.y = numpy.clip(self.position.y + self.velocity.y, 0, HEIGHT - self.rect.height)
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def draw(self, disp):
        pygame.draw.rect(disp, fg_color, self.rect)


# --- Ball object
class Ball:

    def __init__(self, rect, speed):
        self.rect = rect
        self.score = [0, 0]
        self.speed = speed
        self.velocity = 0
        self.position = 0
        self.milliseconds_to_wait = 30
        self.milliseconds_passed = 0
        self.initPos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.ball_setup()

    def ball_setup(self, *args):
        if len(args) == 1:
            if args[0] < 0:
                self.score[1] += 1
            elif args[0] > WIDTH:
                self.score[0] += 1
        #    print 'score is ' + str(self.score)
        self.milliseconds_passed = 0
        temp_vel_y = random.uniform(0.1, self.speed)
        temp_vel_x = random.choice([-self.speed, self.speed])
        self.velocity = pygame.math.Vector2(temp_vel_x, temp_vel_y)
        self.position = pygame.math.Vector2(self.initPos.x - 5, self.initPos.y - 5)
       # print 'Reset, Position:' + str(self.position) + 'init pos: ' + str(self.initPos)

    def set_y_velocity(self, num):
        self.velocity.y += numpy.clip(num, -self.speed, self.speed)

    def update(self):

        self.milliseconds_passed += 1
        # print 'Time since last frame:' + str(clock.get_time())
        if self.milliseconds_passed > self.milliseconds_to_wait:
            self.position += self.velocity
            self.rect.x = self.position.x
            self.rect.y = self.position.y

            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.velocity.y = - self.velocity.y
                # print 'change y'
            elif self.rect.right <= 0 or self.rect.left >= WIDTH:
                self.ball_setup(self.rect.centerx)

    def draw(self, disp):
        pygame.draw.rect(disp, fg_color, self.rect)

pygame.init()
pygame.display.init()
screen = pygame.display.set_mode([480, 320])
#pygame.mouse.set_visible(False)

# --- Constants
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
SPEED = 120
SCREENRECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
# --- Colors
bg_Color = (0, 0, 0)
fg_color = (255, 255, 255)

# --- Objects
pad1 = Paddle(pygame.Rect(20,60,10,50), 2, 17, 22)
pad2 = Paddle(pygame.Rect(WIDTH - 40, 60, 10, 50), 1.1)
ball = Ball(pygame.Rect((WIDTH/2) - 5, (HEIGHT/2) - 5, 10, 10), 1.33)
buttons = [Button(screen, (84, 84, 84), (124, 124, 124), pygame.Rect(WIDTH / 2 - 82, HEIGHT - 80, 80, 80),
                  10, 0, [0], pad1.move_up),
           Button(screen, (84, 84, 84), (124, 124, 124), pygame.Rect(WIDTH / 2 - 2, HEIGHT - 80, 80, 80),
                  10, 1, [0], pad1.move_down)]

# --- Misc
clock = pygame.time.Clock()
score_font = pygame.font.Font('Pixeled.ttf', 32)
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
               pad1.move_up()
            elif event.key == pygame.K_DOWN:
                pad1.move_down()
        elif event.type == pygame.KEYUP:
            pad1.reset_speed()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for b in buttons:
                    b.start_click_event(0, *pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for b in buttons:
                    pad1.reset_speed()
                    b.end_click_event(0, *pygame.mouse.get_pos())


    # --- Game Logic
    # --- --- Collision Logic
    if ball.rect.colliderect(return_face(pad1.rect, "right")):
        ball.rect.left = pad1.rect.right
        # print 'collide pad1'
        ball.velocity.x = - ball.velocity.x
        ball.set_y_velocity(-(pad1.rect.centery - ball.rect.centery) / 100)
    elif return_face(pad2.rect, "left").colliderect(ball.rect):
        ball.rect.right = pad2.rect.left - 5
        # print 'collide pad2'
        ball.velocity.x = - ball.velocity.x
        ball.set_y_velocity(-(pad2.rect.centery - ball.rect.centery) / 100)
    # --- --- End Collision Logic

    # --- --- Object Updates
    pad1.update()
    pad2.update(ball.rect)
    ball.update()
    # --- --- End Object Updates
    # --- End Game Logic

    # --- Draw Logic
    screen.fill(bg_Color)
    # --- --- Object Draws
    for b in buttons:
        b.draw(2, 0)
    for y in range(0, HEIGHT, 10):
        if y % 2 == 0:
            pygame.draw.line(screen, fg_color, [(WIDTH / 2) - 2, y], [(WIDTH / 2) - 2, y + 5], 4)
    text = score_font.render(str(ball.score[0]),True,fg_color)
    screen.blit(text, [(WIDTH * 0.25) - (text.get_width() / 2), 20])
    text = score_font.render(str(ball.score[1]), True, fg_color)
    screen.blit(text, [(WIDTH * 0.75) - (text.get_width() / 2), 20])
    # pygame.draw.line(screen,(0,255,0),[WIDTH/2 - 1, HEIGHT /2 - 1],[WIDTH/2 + 1, HEIGHT /2 + 1])
    pad1.draw(screen)
    pad2.draw(screen)
    ball.draw(screen)
    # --- --- End Object Draws

    pygame.display.flip()
    # --- End Draw Logic
    # FPS Set
    clock.tick(SPEED)

pygame.quit()
