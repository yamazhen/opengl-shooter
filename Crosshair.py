from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D


def draw_crosshair(screen_width, screen_height):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screen_width, 0, screen_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    # white color crosshair
    glColor(1, 1, 1)
    glLineWidth(2)
    glBegin(GL_LINES)
    # horizontal line
    glVertex2f(screen_width / 2 - 10, screen_height / 2)
    glVertex2f(screen_width / 2 + 10, screen_height / 2)
    # vertical line
    glVertex2f(screen_width / 2, screen_height / 2 - 10)
    glVertex2f(screen_width / 2, screen_height / 2 + 10)
    glEnd()
    glLineWidth(1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
