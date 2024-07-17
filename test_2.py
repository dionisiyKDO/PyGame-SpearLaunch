import sys
import math
import time
import random

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

# Background shader
# region
def create_background_shader(ctx):
    quad_buffer = ctx.buffer(np.array([
        # position (x, y), uv coords (x, y)
        -1.0,  1.0, 0.0, 0.0, 
         1.0,  1.0, 1.0, 0.0, 
        -1.0, -1.0, 0.0, 1.0, 
         1.0, -1.0, 1.0, 1.0, 
    ], dtype=np.float32))
    
    scene_shader = ctx.program(
        vertex_shader='''
        #version 330 core
        in vec2 in_vert;
        in vec2 in_uv;
        out vec2 uv;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            uv = in_uv;
        }
        ''',
        fragment_shader='''
        #version 330 core
        uniform sampler2D tex;
        in vec2 uv;
        out vec4 out_color;
        void main() {
            out_color = vec4(
                texture(tex, uv).r * 0.9, 
                texture(tex, uv).g * 0.9, 
                texture(tex, uv).b * 0.9, 
                1.0);
        }
        '''
    )
    render_object = ctx.vertex_array(scene_shader, [(quad_buffer, '2f 2f', 'in_vert', 'in_uv')])
    return render_object

render_object = create_background_shader(ctx)
# endregion

def surf_to_texture(surface):
    texture = ctx.texture(surface.get_size(), components=4)
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
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

    def draw(self, display):
        pygame.draw.circle(display, CHARACTER_COLOR, (int(self.x), int(self.y)), CHARACTER_RADIUS)

class Spear:
    def __init__(self, character):
        self.x = character.x + 30
        self.y = character.y - 30
        cursor_x, cursor_y = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(self.y - cursor_y, cursor_x - self.x))
        self.speed = 0
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
        self.buffer = ctx.buffer(np.array(ndc_coords, dtype=np.float32))

    def calculate_position(self):
        half_height = SPEAR_WIDTH / 2.0
        half_width = self.length / 2.0
        angle_rad = -math.radians(self.angle)  # Positive number -> cursor clockwise, spear rotates counterclockwise. So angle should be negative.
        
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Calculate corner offsets
        offset1_x = half_width * cos_angle - half_height * sin_angle
        offset1_y = half_width * sin_angle + half_height * cos_angle
        
        offset2_x = -half_width * cos_angle - half_height * sin_angle
        offset2_y = -half_width * sin_angle + half_height * cos_angle
        
        offset3_x = -half_width * cos_angle + half_height * sin_angle
        offset3_y = -half_width * sin_angle - half_height * cos_angle
        
        offset4_x = half_width * cos_angle + half_height * sin_angle
        offset4_y = half_width * sin_angle - half_height * cos_angle
        
        # Calculate actual corner positions
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
            self.speed = min(SPEAR_MAX_SPEED, SPEAR_MAX_SPEED * (elapsed_time / CHARGE_TIME))
            self.length = SPEAR_HEIGHT + (SPEAR_HEIGHT * 3 * (elapsed_time / CHARGE_TIME))  # Stretching effect
            self.charge_value = min(CHARGE_VALUE_MAX, int(100 * (elapsed_time / CHARGE_TIME)))  # Max charge value of 100
            if elapsed_time >= CHARGE_TIME:
                self.throw()
            self.coords = self.calculate_position()
            self.update_buffer()
            self.render_spear = ctx.vertex_array(self.spear_shader, [(self.buffer, '2f', 'in_vert')])

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
                # Apply deceleration to simulate slowing down after initial impulse
                deceleration = 0.1
                self.vx *= (1 - deceleration)
                self.vy *= (1 - deceleration)
            else:
                # Once velocity reaches or falls below self.speed, maintain steady speed
                self.vx =  math.cos(math.radians(self.angle)) * self.speed
                self.vy = -math.sin(math.radians(self.angle)) * self.speed

            self.x += self.vx
            self.y += self.vy
            self.coords = self.calculate_position()
            self.update_buffer()
            self.render_spear = ctx.vertex_array(self.spear_shader, [(self.buffer, '2f', 'in_vert')])

    def draw(self, screen):
        if self.destroyed and time.time() - self.destroy_time <= 1:
            pygame.draw.circle(screen, GREY, (int(self.x), int(self.y)), 10)
        elif not self.destroyed:
            self.render_spear.render(mode=moderngl.TRIANGLE_STRIP)

    def destroy(self):
        self.destroyed = True
        self.destroy_time = time.time()

class Dummy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = DUMMY_RADIUS
        self.color = DUMMY_COLOR
        self.is_destroyed = False

    def draw(self, display):
        pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, spear):
        if self.is_destroyed:
            return False

        distance = math.sqrt((self.x - spear.x) ** 2 + (self.y - spear.y) ** 2)
        max_distance = spear.speed + self.radius
        if distance <= max_distance:
            self.hit = True
            self.color = HIT_COLOR
            # print("Dummy hit!")
            spear.destroy()
            return True
        return False
class DummyManager:
    def __init__(self):
        self.dummies = []
        self.spawn_time = 0

    def spawn_dummy(self):
        x = random.randint(DUMMY_RADIUS, SCREEN_WIDTH - DUMMY_RADIUS)
        y = random.randint(DUMMY_RADIUS, SCREEN_HEIGHT - DUMMY_RADIUS)
        self.dummies.append(Dummy(x, y))

    def update(self, spears):
        current_time = time.time()
        if current_time - self.spawn_time > DUMMY_SPAWN_INTERVAL:
            self.spawn_time = current_time
            self.spawn_dummy()

        for dummy in self.dummies:
            if dummy.is_destroyed:
                continue
            for spear in spears:
                if spear.thrown and dummy.check_collision(spear):
                    dummy.is_destroyed = True
                    spear.destroy()
                    break

    def draw(self, display):
        for dummy in self.dummies:
            if not dummy.is_destroyed:
                dummy.draw(display)

def main():
    character = Character()
    spears = []
    dummy_manager = DummyManager()

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        display.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                spear = Spear(character)
                spear.start_charging()
                spears.append(spear)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for spear in spears:
                    if not spear.thrown:
                        spear.throw()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            character.move(0, -CHARACTER_SPEED)
        if keys[pygame.K_s]:
            character.move(0, CHARACTER_SPEED)
        if keys[pygame.K_a]:
            character.move(-CHARACTER_SPEED, 0)
        if keys[pygame.K_d]:
            character.move(CHARACTER_SPEED, 0)

        dummy_manager.update(spears)

        character.draw(display)
        dummy_manager.draw(display)
        frame_tex = surf_to_texture(display)
        frame_tex.use()
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
        for spear in spears:
            if not spear.thrown:
                spear.follow_cursor()
                spear.charge()
            spear.update()
            spear.draw(screen)
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH or spear.y < 0 or spear.x < 0):
                spear = None


        pygame.display.flip()
        frame_tex.release()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
