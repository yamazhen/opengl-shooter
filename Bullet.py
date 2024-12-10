import pygame
import time
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class BulletTracer:
    def __init__(self, start_pos, direction):
        self.position = pygame.math.Vector3(start_pos)
        self.previous_position = pygame.math.Vector3(
            start_pos
        )  # Store the previous position
        self.direction = direction.normalize()
        self.speed = 150.0
        self.lifetime = 10.0
        self.start_time = time.time()
        self.size = 0.05

    def is_alive(self):
        return (time.time() - self.start_time) < self.lifetime

    def update(self, delta_time):
        self.previous_position = pygame.math.Vector3(
            self.position
        )  # Update previous position
        self.position += self.direction * self.speed * delta_time

    def draw(self):
        # Calculate the end position of the tracer
        tracer_length = 1.0  # Length of the tracer

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
        if target["hit"]:
            continue

        # Define the bounding box for the cube
        half_size = target["size"] / 2
        box_min = target["position"] - pygame.math.Vector3(
            half_size, half_size, half_size
        )
        box_max = target["position"] + pygame.math.Vector3(
            half_size, half_size, half_size
        )

        # Check if the bullet's path intersects the target's bounding box
        if line_aabb_intersection(
            bullet.previous_position, bullet.position, box_min, box_max
        ):
            target["hit"] = True
            print(f"Target at {target['position']} hit!")
            return True  # Bullet hit a target

    return False  # No collision detected


def shoot_bullet(camera, bullets):
    gun_world_pos = (
        pygame.math.Vector3(camera.eye)
        + (camera.right * 0.6)
        + (camera.up * -0.15)
        + (camera.forward * -0.3)
    )

    bullet_start_pos = gun_world_pos

    bullet_direction = pygame.math.Vector3(camera.forward).normalize()

    bullet = BulletTracer(bullet_start_pos, bullet_direction)
    bullets.append(bullet)

    camera.apply_recoil(5.0)
