from OpenGL.GL import *
from Mesh import *


class LoadMesh(Mesh):
    def __init__(self, filename, draw_type):
        self.vertices = []
        self.triangles = []
        self.filename = filename
        self.draw_type = draw_type
        self.load_drawing()

    def load_drawing(self):
        with open(self.filename) as fp:
            line = fp.readline()
            while line:
                if line.startswith("v "):  # Vertex data
                    vx, vy, vz = [float(value) for value in line[2:].split()]
                    self.vertices.append((vx, vy, vz))
                elif line.startswith("f "):  # Face data
                    face = line[2:].split()
                    # Parse only the vertex indices from the face data
                    face_indices = [int(value.split("/")[0]) - 1 for value in face]
                    # Convert n-gon to triangles (fan triangulation)
                    for i in range(1, len(face_indices) - 1):
                        self.triangles.extend(
                            [face_indices[0], face_indices[i], face_indices[i + 1]]
                        )
                line = fp.readline()

    def draw(self):
        for t in range(0, len(self.triangles), 3):  # Draw triangles
            glBegin(self.draw_type)
            glVertex3fv(self.vertices[self.triangles[t]])
            glVertex3fv(self.vertices[self.triangles[t + 1]])
            glVertex3fv(self.vertices[self.triangles[t + 2]])
            glEnd()
