import sys
import math
import time
import random

from app.settings import *
from app.Character import Character
from app.Spear import Spear
from app.Enemie import Enemie
from app.utils import surf_to_texture

import pygame
import moderngl
import numpy as np

# TODO
# [1] Add support for multiple spears through LMB RMB, right works, but with bugs
# 
# Rewrite every render in moderngl
# 
# + Implement enemy HP
# - Implement difficulty system
# - Implement score system
# - Add upgrades
#    - Advanced upgrades  
#        - More then one spear at the same time could be launched
#        - Spawn two spears at the time
#    - Simple upgrades
#       - More damage
#       - More spear speed
#       - More range
#    - Cosmetics
#    - More spears variants
#       - diff elements + fluid switch between them
#           - Enemies with specific elements weakness
#           - Element reactions
# - Implement score system
#    - Points for hitting enemies
#    - High score tracking
# - Implement main menu and pause menu
#    - Start game, options, and exit
#    - Resume, restart, and quit options in the pause menu
# - Implement particle effects
#    - Spear trails
#    - Impact effects when spear hits an enemy or the ground
# - Milestone rewards (e.g., hitting 100 enemies)



class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Flying Spear')
        self.clock = pygame.time.Clock()
        self.font  = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.running = True
        
        # Set up OpenGL context
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.OPENGL | pygame.DOUBLEBUF)
        self.display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create ModernGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Create game objects
        self.enemies = self.create_enemies()
        self.character = Character(self.ctx, *CHARACTER_POS)
        self.spears = []
        
        self.init_shaders()
        
    def init_shaders(self):
        quad_buffer = self.ctx.buffer(np.array([
            # position (x, y), uv coords (x, y)
            -1.0,  1.0, 0.0, 0.0, 
             1.0,  1.0, 1.0, 0.0, 
            -1.0, -1.0, 0.0, 1.0, 
             1.0, -1.0, 1.0, 1.0, 
        ], dtype=np.float32))
        scene_shader = self.ctx.program(
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
                    texture(tex, uv).r * 0.9, 
                    texture(tex, uv).g * 0.9, 
                    texture(tex, uv).b * 0.9, 
                    1.0);
            }
            '''
        )
        self.render_object = self.ctx.vertex_array(scene_shader, [(quad_buffer, '2f 2f', 'in_vert', 'in_uv')])

    def create_enemies(self, NUM_ENEMIES=NUM_ENEMIES):
        return [Enemie(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50), random.randint(5, 150)) for _ in range(NUM_ENEMIES)]

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN: 
                # TODO: [1]
                spear = Spear(self.ctx, self.character)
                self.spears.append(spear)
                spear.start_charging()
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.spears:
                    self.spears[-1].throw()

    def update(self):
        delta_time = self.clock.get_time() / 10.0
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a]:
            dx = -CHARACTER_SPEED * delta_time
        if keys[pygame.K_d]:
            dx =  CHARACTER_SPEED * delta_time
        if keys[pygame.K_w]:
            dy = -CHARACTER_SPEED * delta_time
        if keys[pygame.K_s]:
            dy =  CHARACTER_SPEED * delta_time
        self.character.move(dx, dy)

        if all(enemy.killed == True for enemy in self.enemies): # All self.enemies have been hit -> reset them
            self.enemies = self.create_enemies()

        for spear in self.spears:
            if not spear.thrown:
                spear.follow_cursor()
                spear.charge()
            spear.update()
            for enemy in self.enemies:
                if enemy.check_collision(spear):
                    self.spears.remove(spear)
                    if enemy.killed == True:
                        self.character.enemies_killed += 1
                    break
            if spear.thrown and (spear.y > SCREEN_HEIGHT or spear.x > SCREEN_WIDTH or spear.y < 0 or spear.x < 0):
                self.spears.remove(spear)

    def draw_ui(self):
        # draw charge indicator
        if self.spears:
            charge_value = self.spears[-1].charge_value
            charge_indicator_width = int((charge_value / 100) * SCREEN_WIDTH)
            pygame.draw.rect(self.display, RED, (0, SCREEN_HEIGHT - 20, charge_indicator_width, 20))
            charge_text = self.font.render(f"Charge: {charge_value}", True, BLACK)
            self.display.blit(charge_text, (10, SCREEN_HEIGHT - 60))
        
        # draw score indicator
        score_text = self.font.render(f"Score: {self.character.enemies_killed}", True, BLACK)
        self.display.blit(score_text, (10, 10))

    def draw(self):
        # Clear screen
        self.ctx.clear(1.0, 1.0, 1.0)
        
        # Draw to pygame surface first
        self.display.fill(WHITE)
        
        # Draw enemies (still using Pygame for now)
        for enemy in self.enemies:
            enemy.draw(self.display)
        
        # Draw UI
        self.draw_ui()
        
        # Convert Pygame surface to texture and render it
        frame_tex = surf_to_texture(self.ctx, self.display)
        frame_tex.use(0)
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
        # Draw ModernGL objects
        self.character.draw(self.display)
        for spear in self.spears:
            spear.draw()
        
        pygame.display.flip()
        frame_tex.release()
        

if __name__ == "__main__":
    game = Game()
    game.run()
