import pygame
import time
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class BulletTracer:
    def __init__(self, start_pos, direction):
        self.position = pygame.math.Vector3(start_pos)
        self.previous_position = pygame.math.Vector3(start_pos)
        self.direction = direction.normalize()
        self.speed = 150.0
        self.lifetime = 10.0
        self.start_time = time.time()
        self.size = 0.05

    def is_alive(self):
        return (time.time() - self.start_time) < self.lifetime

    def update(self, delta_time):
        self.previous_position = pygame.math.Vector3(self.position)
        self.position += self.direction * self.speed * delta_time

    def draw(self):
        tracer_length = 1.0

        # set yellow and disable lighting
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)

        glPushMatrix()
        # move to bullet start position
        glTranslatef(*self.position)

        # calculate rotation to align the tracer with the direction
        default_direction = pygame.math.Vector3(0, 0, -1)
        rotation_axis = default_direction.cross(self.direction).normalize()
        rotation_angle = np.degrees(np.arccos(default_direction.dot(self.direction)))

        if rotation_axis.length() > 0:
            glRotatef(rotation_angle, rotation_axis.x, rotation_axis.y, rotation_axis.z)

        # draw the cylinder
        quadric = gluNewQuadric()
        gluCylinder(quadric, self.size / 4, self.size / 4, tracer_length, 16, 16)

        # add caps to make it look like a bullet
        glPushMatrix()
        gluSphere(quadric, self.size / 4, 16, 16)
        glPopMatrix()

        glPushMatrix()

        # move to the end of the bullet and add another cap
        glTranslatef(0, 0, tracer_length)
        gluSphere(quadric, self.size / 4, 16, 16)
        glPopMatrix()

        glPopMatrix()

        glEnable(GL_LIGHTING)


def line_aabb_intersection(p1, p2, box_min, box_max):
    # calculate direction vector of the line
    direction = p2 - p1

    # initialize t_min (entry) and t_max (exit) for the line
    t_min = 0.0
    t_max = 1.0

    # check intersection along each axis (x,y,z)
    for i in range(3):
        # check if line is parallel to the plane
        if abs(direction[i]) < 1e-8:
            if p1[i] < box_min[i] or p1[i] > box_max[i]:
                return False
        else:
            # calculate intersect points with the hitbox
            ood = 1.0 / direction[i]
            t1 = (box_min[i] - p1[i]) * ood  # entry
            t2 = (box_max[i] - p1[i]) * ood  # exit

            # make sure t1 is the entry point
            t_enter = min(t1, t2)
            t_exit = max(t1, t2)

            # update t_min and t_max
            t_min = max(t_min, t_enter)
            t_max = min(t_max, t_exit)

            # if entry is after exit then no intersection
            if t_min > t_max:
                return False

    # otherwise intersection occurred
    return True


def check_hits_continuous(targets, bullet, hitbox_scale):
    for target in targets:
        if target["hit"]:
            continue

        # define hitbox by creating a box around the target's hitbox position
        half_size = (target["size"] / 2) * hitbox_scale
        y_half_size = target["size"] / 2
        box_min = target["hitbox_position"] - pygame.math.Vector3(
            half_size, y_half_size, half_size
        )
        box_max = target["hitbox_position"] + pygame.math.Vector3(
            half_size, y_half_size, half_size
        )

        # check if the bullet's path intersects the target's bounding box
        if line_aabb_intersection(
            bullet.previous_position, bullet.position, box_min, box_max
        ):
            target["hit"] = True
            print(f"Target at {target['position']} hit!")
            return True

    return False


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
