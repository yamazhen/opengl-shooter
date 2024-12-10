from OpenGL.GLU import *
from math import cos, sin, radians
import pygame


class Camera:
    def __init__(
        self,
        ground_min_x=-49.0,
        ground_max_x=49.0,
        ground_min_z=-49.0,
        ground_max_z=49.0,
    ):
        self.eye = pygame.math.Vector3(0, 1.0, 5)
        self.up = pygame.math.Vector3(0, 1, 0)
        self.right = pygame.math.Vector3(1, 0, 0)
        self.forward = pygame.math.Vector3(0, 0, -1)
        self.look = self.eye + self.forward
        self.yaw = 0  # Facing towards negative Z
        self.pitch = 0
        self.mouse_sensitivityX = 0.1
        self.mouse_sensitivityY = 0.1
        self.key_sensitivity = 5.0

        # Boundary limits
        self.ground_min_x = ground_min_x
        self.ground_max_x = ground_max_x
        self.ground_min_z = ground_min_z
        self.ground_max_z = ground_max_z

    def rotate(self, yaw, pitch):
        self.yaw -= yaw
        self.pitch += pitch

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Corrected forward vector calculation
        self.forward.x = cos(radians(self.pitch)) * sin(radians(self.yaw))
        self.forward.y = sin(radians(self.pitch))
        self.forward.z = -cos(radians(self.pitch)) * cos(radians(self.yaw))
        self.forward = self.forward.normalize()
        self.right = self.forward.cross(pygame.math.Vector3(0, 1, 0)).normalize()
        self.up = self.right.cross(self.forward).normalize()

    def move(self, direction, delta_time, current_sensitivity):
        movement = direction * current_sensitivity * delta_time
        proposed_position = self.eye + movement

        # Enforce boundary constraints directly
        self.eye.x = max(self.ground_min_x, min(self.ground_max_x, proposed_position.x))
        self.eye.z = max(self.ground_min_z, min(self.ground_max_z, proposed_position.z))

    def update(self, w, h, delta_time):
        if pygame.mouse.get_visible():
            return

        mouse_pos = pygame.mouse.get_pos()
        center_pos = (w / 2, h / 2)
        mouse_change = pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(center_pos)
        pygame.mouse.set_pos(center_pos)

        # Adjusted mouse movement handling
        self.rotate(
            -mouse_change.x * self.mouse_sensitivityX,
            -mouse_change.y * self.mouse_sensitivityY,
        )

        keys = pygame.key.get_pressed()
        sprint_multiplier = 2 if keys[pygame.K_LSHIFT] else 1
        current_sensitivity = self.key_sensitivity * sprint_multiplier
        move_direction = pygame.math.Vector3(0, 0, 0)

        if keys[pygame.K_w]:
            move_direction += self.forward
        if keys[pygame.K_s]:
            move_direction -= self.forward
        if keys[pygame.K_d]:
            move_direction += self.right
        if keys[pygame.K_a]:
            move_direction -= self.right

        move_direction.y = 0  # Prevent moving vertically
        if move_direction.length() > 0:
            move_direction = move_direction.normalize()
            self.move(
                move_direction, delta_time, current_sensitivity
            )  # Pass current_sensitivity

        self.look = self.eye + self.forward

    def apply(self):
        gluLookAt(
            self.eye.x,
            self.eye.y,
            self.eye.z,
            self.look.x,
            self.look.y,
            self.look.z,
            self.up.x,
            self.up.y,
            self.up.z,
        )
