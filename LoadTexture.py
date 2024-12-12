import pygame
from OpenGL.GL import *


def load_texture(path):
    # load image
    texture_surface = pygame.image.load(path)

    # convert image to pixel data in RGBA format and flip vertically for OpenGL
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)

    # get image dimensions
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    # generate texture id
    texture_id = glGenTextures(1)

    # upload texture data to OpenGL
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        texture_data,
    )

    # set texture wrap for S(horizontal) and T(vertical) axis
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # set texture filtering
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id
