import sys
import math
import time
import random
from array import array

from settings import *

import pygame
import moderngl
import numpy as np

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
ctx = moderngl.create_context()

pygame.display.set_caption("Flying Spear")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


quad_buffer = ctx.buffer(array('f', [
    # position (x, y), uv coords (x, y)
    -1.0,  1.0, 0.0, 0.0, 
     1.0,  1.0, 1.0, 0.0, 
    -1.0, -1.0, 0.0, 1.0, 
     1.0, -1.0, 1.0, 1.0, 
]))
shader        = ctx.program(
    vertex_shader = '''
    #version 330 core
    in vec2 in_vert;
    in vec2 in_uv;
    out vec2 uv;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        uv = in_uv;
    }

    ''',
    
    fragment_shader = '''
    #version 330 core

    uniform sampler2D tex;

    in vec2 uv;
    out vec4 out_color;

    void main() {
        out_color = texture(tex, uv);
    }

    '''
)
render_object = ctx.vertex_array(shader, [(quad_buffer, '2f 2f', 'in_vert', 'in_uv')])
shader['in_vert'] = quad_buffer

def surf_to_texture(surface):
    texture         = ctx.texture(surface.get_size(), components=4)
    texture.filter  = (moderngl.NEAREST, moderngl.NEAREST)
    texture.swizzle = 'BGRA'
    texture.write(surface.get_view('1'))
    return texture




class Character:
    def __init__(self, x=CHARACTER_POS[0], y=CHARACTER_POS[1]):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        pygame.draw.circle(screen, CHARACTER_COLOR, (int(self.x), int(self.y)), CHARACTER_RADIUS)

class Dummy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = DUMMY_RADIUS
        self.color = DUMMY_COLOR
        self.hit = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, spear):
        if not self.hit and spear.thrown and not spear.destroyed:
            distance = math.sqrt((self.x - spear.x) ** 2 + (self.y - spear.y) ** 2)
            max_distance = spear.speed + self.radius
            if distance <= max_distance:
                self.hit = True
                self.color = HIT_COLOR
                print("Dummy hit!")
                spear.destroy()
                return True
        return False

class Spear:
    def __init__(self, character):
        self.x = character.x + 30
        self.y = character.y - 30
        self.angle = 0
        self.speed = 0
        self.vx = 0
        self.vy = 0
        self.thrown = False
        self.charge_start_time = None
        self.length = SPEAR_HEIGHT
        self.charge_value = 0
        self.destroyed = False
        self.destroy_time = None
        
        
        self.spear_shader  = ctx.program(
            vertex_shader = '''
            #version 330 core
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }

            ''',
            fragment_shader = '''
            #version 330 core

            uniform sampler2D tex;

            in vec2 uv;
            out vec4 out_color;

            void main() {
                out_color = vec4(
                    texture(tex, uv).r, 
                    texture(tex, uv).g * 0.0, 
                    texture(tex, uv).b * 0.0, 
                    1.0);
            }
            '''
        )
        
        hw, hh = SPEAR_WIDTH / 2.0, SPEAR_HEIGHT / 2.0
        angle_rad = math.radians(self.angle)
        dx = hw * math.cos(angle_rad)
        dy = hw * math.sin(angle_rad)
        
        vertex_data = [
            float(self.x - dx), float(self.y - dy),
            float(self.x + dy), float(self.y - dx),
            float(self.x + dx), float(self.y + dy),
            float(self.x - dy), float(self.y + dx)
        ]
        
        vertex_data = array('f', vertex_data)
        self.render_spear  = ctx.vertex_array(self.spear_shader, [(vertex_data, '2f 2f', 'in_vert', 'in_uv')])
        self.spear_shader['in_vert'] = vertex_data


    def start_charging(self):
        self.charge_start_time = time.time()

    def charge(self):
        if self.charge_start_time:
            elapsed_time = time.time() - self.charge_start_time
            self.speed = min(SPEAR_MAX_SPEED, SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            self.charge_value = min(CHARGE_VALUE_MAX, int(100 * (elapsed_time / CHARGE_TIME)))  # Max charge value of 100
            if elapsed_time >= CHARGE_TIME:
                self.throw()

    def follow_cursor(self, cursor_x, cursor_y):
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))

    def throw(self):
        initial_speed = self.speed * 4.0  # Example: starting with double the speed
        self.vx = math.cos(math.radians(self.angle)) * initial_speed
        self.vy = -math.sin(math.radians(self.angle)) * initial_speed
        self.thrown = True

    def update(self):
        if self.thrown and not self.destroyed:
            if abs(self.vx) > self.speed or abs(self.vy) > self.speed:
                # Apply deceleration to simulate slowing down after initial impulse
                deceleration = 0.1  # Adjust as needed
                self.vx *= (1 - deceleration)
                self.vy *= (1 - deceleration)
            else:
                # Once velocity reaches or falls below self.speed, maintain steady speed
                self.vx = math.cos(math.radians(self.angle)) * self.speed
                self.vy = -math.sin(math.radians(self.angle)) * self.speed

            self.x += self.vx
            self.y += self.vy

    def draw(self, screen):
        if self.destroyed and time.time() - self.destroy_time <= 1:
            pygame.draw.circle(screen, GREY, (int(self.x), int(self.y)), 10)
        elif not self.destroyed:
            spear_surface = pygame.Surface((self.length, SPEAR_WIDTH), pygame.SRCALPHA)
            spear_tex = surf_to_texture(spear_surface)
            spear_tex.use(1)
            self.spear_shader['tex'] = 1
            self.render_spear.render(mode=moderngl.TRIANGLE_STRIP)
            spear_tex.release()
        
    def destroy(self):
        self.destroyed = True
        self.destroy_time = time.time()



def draw_charge_indicator(screen, charge_value):
    charge_indicator_width = int((charge_value / 100) * SCREEN_WIDTH)
    pygame.draw.rect(screen, RED, (0, SCREEN_HEIGHT - 20, charge_indicator_width, 20))
    charge_text = font.render(f"Charge: {charge_value}", True, BLACK)
    screen.blit(charge_text, (10, SCREEN_HEIGHT - 60))

def handle_events(character, spear=None):
    global zoom_level

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and spear is None:
            spear = Spear(character)
            spear.start_charging()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and spear and not spear.thrown:
            spear.throw()
            zoom_level = 1.0

    delta_time = clock.get_time() / 10.0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        character.move(-CHARACTER_SPEED * delta_time, 0)
    if keys[pygame.K_d]:
        character.move(CHARACTER_SPEED * delta_time, 0)
    if keys[pygame.K_w]:
        character.move(0, -CHARACTER_SPEED * delta_time)
    if keys[pygame.K_s]:
        character.move(0, CHARACTER_SPEED * delta_time)

    return spear, True


def main():
    global zoom_level

    character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    dummies   = [Dummy(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)) for _ in range(NUM_DUMMIES)]
    spear     = None
    
    running = True
    while running:
        spear, running = handle_events(character, spear)

        display.fill(WHITE)
        character.draw(display)
        
        # Draw dummies + check collisions
        # region
        if all(dummy.hit == True for dummy in dummies):
            # All dummies have been hit, reset them
            dummies = [Dummy(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)) for _ in range(NUM_DUMMIES)]
        for dummy in dummies:
            # draw dummy
            dummy.draw(display)
            if spear and spear.thrown:
                # check if dummy has been hit
                if dummy.check_collision(spear):
                    spear = None
        # endregion

        # Draw spear charge indicator + check if thrown out of bounds
        # region
        if spear:
            if not spear.thrown:
                # If spear is created but not thrown, follow cursor
                cursor_x, cursor_y = pygame.mouse.get_pos()
                spear.follow_cursor(cursor_x, cursor_y)
                spear.charge()
                # draw charge indicator
                draw_charge_indicator(display, spear.charge_value)
            # draw spear
            spear.update()
            spear.draw(display)
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH or spear.y < 0 or spear.x < 0):
                # if spear is thrown and out of bounds, destroy
                spear = None
        # endregion



        # Render objects using ModernGL
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        shader['tex'] = 0
        render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pygame.display.flip()
        frame_tex.release()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()