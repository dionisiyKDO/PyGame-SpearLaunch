import sys
from array import array

import pygame
import moderngl

pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((800, 600))
ctx = moderngl.create_context()

clock = pygame.time.Clock()


img = pygame.image.load("image.png")
img.convert_alpha()
img = pygame.transform.scale(img, (400, 400))

quad_buffer = ctx.buffer(array('f', [
    # position (x, y), uv coords (x, y)
    -1.0,  1.0, 0.0, 0.0, 
     1.0,  1.0, 1.0, 0.0, 
    -1.0, -1.0, 0.0, 1.0, 
     1.0, -1.0, 1.0, 1.0, 
]))

program = ctx.program(
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
    uniform float time;
    
    in vec2 uv;
    out vec4 out_color;
    
    void main() {
        out_color = vec4(
            texture(tex, uv).r, 
            texture(tex, uv).g, 
            texture(tex, uv).b, 
            1.0);
    }
    '''
)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'in_vert', 'in_uv')])
def surf_to_texture(surface):
    texture = ctx.texture(surface.get_size(), components=4)
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    texture.swizzle = 'BGRA'
    texture.write(surface.get_view('1'))
    return texture


program['in_vert'] = quad_buffer

time = 0

while True:
    display.fill((0, 0, 0))
    display.blit(img, pygame.mouse.get_pos())
    
    time += 1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    frame_tex = surf_to_texture(display)
    frame_tex.use(0)
    program['tex'] = 0
    render_object.render(mode=moderngl.TRIANGLE_STRIP)

    pygame.display.flip()
    frame_tex.release()
    clock.tick(60)