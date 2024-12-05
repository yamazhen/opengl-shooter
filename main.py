import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Camera import *
import numpy as np
import time
import random

pygame.init()

# Project settings
screen_width = 800
screen_height = 600
background_color = (0, 0, 0, 1)
drawing_color = (1, 1, 1, 1)
terrain_texture_id = None

screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption('Simple 3D Shooter')
camera = Camera()

def draw_crosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screen_width, 0, screen_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor(1, 1, 1)  # White color for the crosshair
    glLineWidth(2)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(screen_width / 2 - 10, screen_height / 2)
    glVertex2f(screen_width / 2 + 10, screen_height / 2)
    # Vertical line
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

def draw_targets(targets):
    for target in targets:
        if not target['hit']:
            glPushMatrix()
            glColor(1, 0, 0)  # Red for active targets
            glTranslatef(target['position'].x, target['position'].y, target['position'].z)
            draw_cube(target['size'])
            glPopMatrix()

def draw_cube(size):
    half_size = size / 2.0
    vertices = [
        [-half_size, -half_size, -half_size],
        [half_size, -half_size, -half_size],
        [half_size, half_size, -half_size],
        [-half_size, half_size, -half_size],
        [-half_size, -half_size, half_size],
        [half_size, -half_size, half_size],
        [half_size, half_size, half_size],
        [-half_size, half_size, half_size]
    ]

    surfaces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (1, 2, 6, 5),
        (4, 7, 3, 0)
    ]

    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

def load_texture(path):
    texture_surface = pygame.image.load(path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width = texture_surface.get_width()
    height = texture_surface.get_height()
    texture_id = glGenTextures(1)
    
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return texture_id

def Light():
    ambientLight = [0.2, 0.2, 0.2, 1.0]
    diffuseLight = [0.7, 0.7, 0.7, 1.0]
    specularLight = [1.0, 1.0, 1.0, 1.0]
    lightPos = [0.0, 10.0, 0.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

def initialise():
    global terrain_texture_id
    glClearColor(*background_color)
    glColor(*drawing_color)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, (screen_width / screen_height), 0.1, 500.0)

    Light()

    terrain_texture_id = load_texture("terrain_texture.jpeg")

def init_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glViewport(0, 0, screen.get_width(), screen.get_height())

def draw_world_axes():
    glLineWidth(2)
    glBegin(GL_LINES)

    glColor(1, 0, 0)
    glVertex3d(-1000, 0, 0)
    glVertex3d(1000, 0, 0)

    glColor(0, 1, 0)
    glVertex3d(0, -1000, 0)
    glVertex3d(0, 1000, 0)

    glColor(0, 0, 1)
    glVertex3d(0, 0, -1000)
    glVertex3d(0, 0, 1000)
    glEnd()
    glLineWidth(1.0)
    glColor(1, 1, 1)

def create_targets():
    targets = []
    num_targets = 10  # You can change this to how many targets you want
    field_min = -45   # Set slightly inside the field boundaries to avoid edge cases
    field_max = 45

    for _ in range(num_targets):
        x = random.uniform(field_min, field_max)
        y = -0.5  # Assuming targets are placed on the ground level
        z = random.uniform(field_min, field_max)
        target = {
            'position': pygame.math.Vector3(x, y, z),
            'hit': False,
            'size': 1.0
        }
        targets.append(target)
    return targets

def draw_ground():
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

class Bullet:
    def __init__(self, start_pos, direction):
        self.position = pygame.math.Vector3(start_pos)
        self.previous_position = pygame.math.Vector3(start_pos)  # Store the previous position
        self.direction = direction.normalize()
        self.speed = 150.0
        self.lifetime = 10.0
        self.start_time = time.time()
        self.size = 0.05

    def is_alive(self):
        return (time.time() - self.start_time) < self.lifetime

    def update(self, delta_time):
        self.previous_position = pygame.math.Vector3(self.position)  # Update previous position
        self.position += self.direction * self.speed * delta_time

    def draw(self, camera):
        # Calculate the end position of the tracer
        tracer_length = 1.0  # Length of the tracer
        line_end = self.position + self.direction * tracer_length
    
        # Disable lighting for consistent tracer appearance
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)  # Set tracer color to yellow
    
        # Draw a 3D line cylinder (main body of the tracer)
        glPushMatrix()
        # Move to the bullet's starting position
        glTranslatef(*self.position)
    
        # Calculate rotation to align the tracer with the direction
        default_direction = pygame.math.Vector3(0, 0, -1)  # Default OpenGL forward
        rotation_axis = default_direction.cross(self.direction).normalize()
        rotation_angle = np.degrees(np.arccos(default_direction.dot(self.direction)))
    
        if rotation_axis.length() > 0:
            glRotatef(rotation_angle, rotation_axis.x, rotation_axis.y, rotation_axis.z)
    
        # Draw the cylinder
        quadric = gluNewQuadric()
        gluCylinder(quadric, self.size / 4, self.size / 4, tracer_length, 16, 16)
    
        # Add hemispherical caps
        glPushMatrix()
        gluSphere(quadric, self.size / 4, 16, 16)
        glPopMatrix()
    
        glPushMatrix()
        glTranslatef(0, 0, tracer_length)  # Move to the end of the cylinder
        gluSphere(quadric, self.size / 4, 16, 16)
        glPopMatrix()
    
        glPopMatrix()
    
        glEnable(GL_LIGHTING)

def line_aabb_intersection(p1, p2, box_min, box_max):
    direction = p2 - p1
    t_min = 0.0
    t_max = 1.0

    for i in range(3):
        if abs(direction[i]) < 1e-8:
            if p1[i] < box_min[i] or p1[i] > box_max[i]:
                return False
        else:
            ood = 1.0 / direction[i]
            t1 = (box_min[i] - p1[i]) * ood
            t2 = (box_max[i] - p1[i]) * ood

            t_enter = min(t1, t2)
            t_exit = max(t1, t2)

            t_min = max(t_min, t_enter)
            t_max = min(t_max, t_exit)

            if t_min > t_max:
                return False

    return True

def check_hits_continuous(targets, bullet):
    for target in targets:
        if target['hit']:
            continue

        # Define the bounding box for the cube
        half_size = target['size'] / 2
        box_min = target['position'] - pygame.math.Vector3(half_size, half_size, half_size)
        box_max = target['position'] + pygame.math.Vector3(half_size, half_size, half_size)

        # Check if the bullet's path intersects the target's bounding box
        if line_aabb_intersection(bullet.previous_position, bullet.position, box_min, box_max):
            target['hit'] = True
            print(f"Target at {target['position']} hit!")
            return True  # Bullet hit a target

    return False  # No collision detected

def shoot_bullet(camera, bullets):
    forward_offset = 0.2
    downward_offset = -0.2
    bullet_start_pos = (pygame.math.Vector3(camera.eye) +
                        camera.forward * forward_offset +
                        camera.up * downward_offset)
    bullet_direction = pygame.math.Vector3(camera.forward).normalize()
    bullet = Bullet(bullet_start_pos, bullet_direction)
    bullets.append(bullet)

def display(targets, bullets):
    glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))
    init_camera()
    camera.apply()
    draw_world_axes()
    draw_ground()
    draw_targets(targets)

    for bullet in bullets:
        bullet.draw(camera)

    draw_crosshair()

def main():
    clock = pygame.time.Clock()
    done = False
    initialise()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    targets = create_targets()
    bullets = []

    while not done:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                if event.key == K_SPACE:
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    shoot_bullet(camera, bullets)

        camera.update(screen.get_width(), screen.get_height(), delta_time)

        # Update bullets and check collisions
        bullets_to_remove = []
        for bullet in bullets:
            bullet.update(delta_time)
            if check_hits_continuous(targets, bullet):
                bullets_to_remove.append(bullet)  # Mark for removal
            elif not bullet.is_alive():
                bullets_to_remove.append(bullet)  # Mark expired bullet for removal

        # Draw everything
        display(targets, bullets)

        # Remove bullets after drawing
        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        pygame.display.flip()

        if all(target['hit'] for target in targets):
            print("All targets eliminated! You win!")
            pygame.quit()
            exit()

    pygame.quit()

if __name__ == "__main__":
    main()
