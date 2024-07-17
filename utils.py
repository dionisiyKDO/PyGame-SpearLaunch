import moderngl
import numpy as np

def surf_to_texture(ctx, surface):
    texture = ctx.texture(surface.get_size(), components=4)
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    texture.swizzle = 'BGRA'
    texture.write(surface.get_view('1'))
    return texture