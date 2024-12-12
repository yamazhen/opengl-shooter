from OpenGL.GLU import *
from OpenGL.GL import *
from math import cos, sin, radians
import pygame


class Camera:
    def __init__(
        self,
        ground_min_x,
        ground_max_x,
        ground_min_z,
        ground_max_z,
    ):
        self.gun_mesh = None
        self.eye = pygame.math.Vector3(0, 1.0, 5)
        self.up = pygame.math.Vector3(0, 1, 0)
        self.right = pygame.math.Vector3(1, 0, 0)
        self.forward = pygame.math.Vector3(0, 0, -1)
        self.look = self.eye + self.forward
        self.yaw = 0
        self.pitch = 0
        self.mouse_sensitivityX = 0.1
        self.mouse_sensitivityY = 0.1
        self.key_sensitivity = 5.0

        # recoil attributes
        self.gun_recoil = 0.0
        self.max_recoil = 5.0
        self.recoil_recovery_speed = 20.0

        # boundary limits
        self.ground_min_x = ground_min_x
        self.ground_max_x = ground_max_x
        self.ground_min_z = ground_min_z
        self.ground_max_z = ground_max_z

    # applies the gun recoil
    def apply_recoil(self, recoil_amount):
        self.gun_recoil += recoil_amount
        if self.gun_recoil > self.max_recoil:
            self.gun_recoil = self.max_recoil

    # slowly recovers the gun recoil
    def update_recoil(self, delta_time):
        if self.gun_recoil > 0:
            self.gun_recoil -= self.recoil_recovery_speed * delta_time
            if self.gun_recoil < 0:
                self.gun_recoil = 0

    def attach_gun(self, gun_mesh):
        self.gun_mesh = gun_mesh

    def draw_gun(self):
        if self.gun_mesh:
            glPushMatrix()
            # position the gun model to match the camera's position
            glTranslatef(self.eye.x, self.eye.y, self.eye.z)

            # rotate the gun model to match the camera's orientation
            glRotatef(-self.yaw, 0, 1, 0)
            glRotatef(self.pitch, 1, 0, 0)

            # rotate the gun model
            glRotatef(-90, 0, 1, 0)

            # apply gun recoil
            glRotatef(self.gun_recoil, 0, 0, -1)

            # offset the gun to appear like the player is holding it
            glTranslatef(-0.6, -0.2, -0.3)

            self.gun_mesh.draw()
            glPopMatrix()

    def rotate(self, yaw, pitch):
        self.yaw -= yaw
        self.pitch += pitch

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        self.forward.x = cos(radians(self.pitch)) * sin(radians(self.yaw))
        self.forward.y = sin(radians(self.pitch))
        self.forward.z = -cos(radians(self.pitch)) * cos(radians(self.yaw))
        self.forward = self.forward.normalize()
        self.right = self.forward.cross(pygame.math.Vector3(0, 1, 0)).normalize()
        self.up = self.right.cross(self.forward).normalize()

    def move(self, direction, delta_time, current_sensitivity):
        movement = direction * current_sensitivity * delta_time
        proposed_position = self.eye + movement

        # enforce boundary constraints
        self.eye.x = max(self.ground_min_x, min(self.ground_max_x, proposed_position.x))
        self.eye.z = max(self.ground_min_z, min(self.ground_max_z, proposed_position.z))

    def update(self, w, h, delta_time):
        if pygame.mouse.get_visible():
            return

        mouse_pos = pygame.mouse.get_pos()
        center_pos = (w / 2, h / 2)
        mouse_change = pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(center_pos)
        pygame.mouse.set_pos(center_pos)

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

        # prevent y axis movement
        move_direction.y = 0
        if move_direction.length() > 0:
            move_direction = move_direction.normalize()
            self.move(move_direction, delta_time, current_sensitivity)

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
