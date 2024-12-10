from OpenGL.GL import *


def draw_ground(terrain_texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, terrain_texture_id)

    repeat_factor = 50

    glPushMatrix()
    glColor(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-50, -1, -50)
    glTexCoord2f(repeat_factor, 0)
    glVertex3f(50, -1, -50)
    glTexCoord2f(repeat_factor, repeat_factor)
    glVertex3f(50, -1, 50)
    glTexCoord2f(0, repeat_factor)
    glVertex3f(-50, -1, 50)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
