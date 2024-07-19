# spear.py

import math
import time
import pygame
import moderngl
import numpy as np
from settings import *

class Spear:
    def __init__(self, ctx, character):
        self.ctx = ctx
        self.x = character.x + 30
        self.y = character.y - 30
        cursor_x, cursor_y = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))
        self.speed = 10
        self.vx = 0
        self.vy = 0
        self.thrown = False
        self.charge_start_time = None
        self.length = SPEAR_HEIGHT
        self.charge_value = 0
        self.destroyed = False
        self.destroy_time = None
        
        self.coords = self.calculate_position()
        self.buffer = None
        self.update_buffer()
        
        self.spear_shader = ctx.program(
            vertex_shader='''
            #version 330 core
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330 core
            out vec4 out_color;
            void main() {
                out_color = vec4(
                    1.0 * 0.99, // R
                    1.0 * 0.1, // G
                    1.0 * 0.1, // B
                    1.0);
            }
            '''
        )
        
        self.render_spear = ctx.vertex_array(self.spear_shader, [(self.buffer, '2f', 'in_vert')])

    def update_buffer(self):
        ndc_coords = []
        for i in range(0, len(self.coords), 2):
            x, y = self.coords[i:i+2]
            ndc_x = 2.0 * x / SCREEN_WIDTH - 1.0
            ndc_y = 2.0 * y / SCREEN_HEIGHT - 1.0 
            ndc_coords.extend([ndc_x, -ndc_y])
        self.buffer = self.ctx.buffer(np.array(ndc_coords, dtype=np.float32))

    def calculate_position(self):
        # I swear, i dont know whats with half_height and half_width, whats with corners, but this works how it should be. 
        # Im sure i fucked up something, not a pro in maths, all math is made through ChatGPT, so there is an error for sure
        half_height = SPEAR_WIDTH / 2.0
        half_width = self.length / 2.0
        angle_rad = -math.radians(self.angle)   # Positive number -> cursor clockwise, spear rotates counterclockwise. So angle should be negative.
        
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        offset1_x = half_width * cos_angle - half_height * sin_angle
        offset1_y = half_width * sin_angle + half_height * cos_angle
        
        offset2_x = -half_width * cos_angle - half_height * sin_angle
        offset2_y = -half_width * sin_angle + half_height * cos_angle
        
        offset3_x = -half_width * cos_angle + half_height * sin_angle
        offset3_y = -half_width * sin_angle - half_height * cos_angle
        
        offset4_x = half_width * cos_angle + half_height * sin_angle
        offset4_y = half_width * sin_angle - half_height * cos_angle
        
        corner1_x = self.x + offset1_x
        corner1_y = self.y + offset1_y
        
        corner2_x = self.x + offset2_x
        corner2_y = self.y + offset2_y
        
        corner3_x = self.x + offset3_x
        corner3_y = self.y + offset3_y
        
        corner4_x = self.x + offset4_x
        corner4_y = self.y + offset4_y
        
        return [
            corner1_x, corner1_y, 
            corner2_x, corner2_y, 
            corner4_x, corner4_y,
            corner3_x, corner3_y, 
        ]

    def start_charging(self):
        self.charge_start_time = time.time()

    def charge(self):
        if self.charge_start_time:
            elapsed_time = time.time() - self.charge_start_time
            self.speed = min(SPEAR_MAX_SPEED, max(1, (SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            self.charge_value = min(CHARGE_VALUE_MAX, int(100 * (elapsed_time / CHARGE_TIME)))  # Max charge value of 100
            if elapsed_time >= CHARGE_TIME:
                self.throw()
            self.coords = self.calculate_position()
            self.update_buffer()
            self.render_spear = self.ctx.vertex_array(self.spear_shader, [(self.buffer, '2f', 'in_vert')])

    def follow_cursor(self):
        cursor_x, cursor_y = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))

    def throw(self):
        initial_speed = self.speed * SPEAR_IMPULSE
        self.vx = math.cos(math.radians(self.angle)) * initial_speed
        self.vy = -math.sin(math.radians(self.angle)) * initial_speed
        self.thrown = True

    def update(self):
        if self.thrown and not self.destroyed:
            if abs(self.vx) > self.speed or abs(self.vy) > self.speed:
                deceleration = 0.1
                self.vx *= (1 - deceleration)
                self.vy *= (1 - deceleration)
            else:
                self.vx =  math.cos(math.radians(self.angle)) * self.speed
                self.vy = -math.sin(math.radians(self.angle)) * self.speed

            self.x += self.vx
            self.y += self.vy
            self.coords = self.calculate_position()
            self.update_buffer()
            self.render_spear = self.ctx.vertex_array(self.spear_shader, [(self.buffer, '2f', 'in_vert')])

    def draw(self):
        if self.destroyed and time.time() - self.destroy_time <= 1:
            pass # create new object of hit_aftermath or amth like this
            # pygame.draw.circle(screen, GREY, (int(self.x), int(self.y)), 10)
        elif not self.destroyed:
            self.render_spear.render(mode=moderngl.TRIANGLE_STRIP)

    def destroy(self):
        self.destroyed = True
        self.destroy_time = time.time()
