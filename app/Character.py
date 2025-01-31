import pygame
import numpy as np
import moderngl

from app.settings import CHARACTER_COLOR, CHARACTER_RADIUS

class Character:
    def __init__(self, ctx, x, y):
        self.x = x
        self.y = y
        self.enemies_killed = 0
        
        self.buffer = ctx.buffer(np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0,
        ], dtype='f4').tobytes())
        
        self.char_shader = ctx.program(
            vertex_shader='''
            #version 330 core
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330 core
            in vec2 in_vert;
            
            uniform vec2 circle_center;
            uniform float circle_radius;
            
            out vec4 out_color;
            void main() {
                vec2 frag_coord = gl_FragCoord.xy;
                float distance = length(frag_coord - circle_center);
                
                if (distance < circle_radius) {
                    out_color = vec4(1.0, 0.0, 0.0, 1.0);
                } else {
                    discard;
                }
            }
            '''
        )
        self.circle_center = (self.x, self.y)
        self.circle_radius = CHARACTER_RADIUS
        self.char_shader['circle_center'].value = self.circle_center
        self.char_shader['circle_radius'].value = self.circle_radius
        self.render_char = ctx.vertex_array(self.char_shader, [(self.buffer, '2f', 'in_vert')])

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, display):
        self.render_char.render(mode=moderngl.TRIANGLE_STRIP)
        # pygame.draw.circle(display, CHARACTER_COLOR, (int(self.x), int(self.y)), CHARACTER_RADIUS)
