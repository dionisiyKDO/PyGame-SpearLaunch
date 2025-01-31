import pygame
import numpy as np
import moderngl
from app.settings import CHARACTER_COLOR, CHARACTER_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT

class Character:
    def __init__(self, ctx, x, y):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.enemies_killed = 0
        
        # Create vertices for a square that will be our character
        vertices = np.array([
            # x    y     u   v
            -1.0, -1.0,  0.0, 0.0,  # Bottom left
             1.0, -1.0,  1.0, 0.0,  # Bottom right
            -1.0,  1.0,  0.0, 1.0,  # Top left
             1.0,  1.0,  1.0, 1.0   # Top right
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices.tobytes())
        
        # Shader for drawing the character
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                
                in vec2 in_position;
                in vec2 in_uv;
                
                uniform vec2 scale;
                uniform vec2 translation;
                uniform vec2 screen_size;
                
                out vec2 uv;
                
                void main() {
                    // Scale by radius and translate to position
                    vec2 scaled_pos = in_position * scale;
                    vec2 translated_pos = scaled_pos + translation;
                    
                    // Convert to NDC coordinates (-1 to 1)
                    vec2 ndc = translated_pos / screen_size * 2.0 - 1.0;
                    // Flip Y coordinate for OpenGL
                    ndc.y = -ndc.y;
                    
                    gl_Position = vec4(ndc, 0.0, 1.0);
                    uv = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330
                
                in vec2 uv;
                out vec4 fragColor;
                
                void main() {
                    // Calculate distance from center
                    vec2 center = vec2(0.5, 0.5);
                    float dist = length(uv - center) * 2.0;
                    
                    // Create a circle
                    if (dist > 1.0) {
                        discard;
                    }
                    
                    // Use CHARACTER_COLOR (red in this case)
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
                }
            '''
        )
        
        # Set up vertex array
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '2f 2f', 'in_position', 'in_uv'),
            ]
        )
        
        # Set uniforms
        self.prog['scale'].value = (CHARACTER_RADIUS, CHARACTER_RADIUS)
        self.prog['screen_size'].value = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.update_position()

    def update_position(self):
        self.prog['translation'].value = (self.x, self.y)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.update_position()

    def draw(self, display):
        # Enable blending for transparency
        self.ctx.enable(moderngl.BLEND)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        self.ctx.disable(moderngl.BLEND)