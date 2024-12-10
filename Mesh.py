from OpenGL.GL import *


class Mesh:
    def __init__(self):
        self.vertices = [
            (0.5, -0.5, 0.5),
            (-0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5),
            (-0.5, 0.5, 0.5),
            (0.5, 0.5, -0.5),
            (-0.5, 0.5, -0.5),
        ]
        self.triangles = [0, 2, 3, 0, 3, 1]
        self.draw_type = GL_TRIANGLES

    def draw(self):
        glBegin(self.draw_type)
        for t in range(0, len(self.triangles), 3):  # t=0,3
            glBegin(self.draw_type)
            glVertex3fv(self.vertices[self.triangles[t]])
            glVertex3fv(self.vertices[self.triangles[t + 1]])
            glVertex3fv(self.vertices[self.triangles[t + 2]])
            glEnd()
