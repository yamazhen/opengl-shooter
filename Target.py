import math
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import GLU_SMOOTH, gluNewQuadric, gluCylinder, gluQuadricNormals


def draw_hemisphere(radius, slices, stacks):
    for i in range(stacks):
        # start and end latitude
        lat0 = (math.pi / 2) * (i / stacks)
        lat1 = (math.pi / 2) * ((i + 1) / stacks)

        z0 = math.sin(lat0)
        zr0 = math.cos(lat0)

        z1 = math.sin(lat1)
        zr1 = math.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)
            x = math.cos(lng)
            y = math.sin(lng)

            # first vertex (lower latitude)
            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)

            # second vertex (higher latitude)
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
        glEnd()


def draw_capsule(size, slices=16, stacks=16):
    radius = size / 4.0
    cylinder_height = size - 2 * radius

    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)

    # draw the cylinder standing
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quadric, radius, radius, cylinder_height, slices, stacks)
    glPopMatrix()

    # draw the top hemisphere
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0.0, 0.0, cylinder_height)
    draw_hemisphere(radius, slices, stacks)
    glPopMatrix()

    # draw the bottom hemisphere
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glRotatef(180, 1, 0, 0)
    draw_hemisphere(radius, slices, stacks)
    glPopMatrix()


def draw_targets(targets):
    for target in targets:
        if not target["hit"]:
            glPushMatrix()
            glColor(1, 0, 0)
            glTranslatef(
                target["position"].x, target["position"].y, target["position"].z
            )
            draw_capsule(target["size"])
            glPopMatrix()


def update_targets(targets, delta_time):
    for target in targets:
        if target["hit"]:
            continue

        # update elapsed time
        target["elapsed_time"] += delta_time

        # calculate new positions based on elapsed time
        new_x = target["initial_x"] + target["amplitude_x"] * math.sin(
            target["frequency_x"] * target["elapsed_time"] + target["phase_x"]
        )
        new_z = target["initial_z"] + target["amplitude_z"] * math.cos(
            target["frequency_z"] * target["elapsed_time"] + target["phase_z"]
        )

        # update target and hitbox position
        target["position"].x = new_x
        target["position"].z = new_z
        target["hitbox_position"].x = new_x
        target["hitbox_position"].z = new_z


def create_targets():
    targets = []
    num_targets = 10
    field_min = -45
    field_max = 45

    for _ in range(num_targets):
        initial_x = random.uniform(field_min, field_max)
        initial_z = random.uniform(field_min, field_max)
        y = -0.5  # capsule height is 1.0, so y = -0.5 centers it

        # random movement for each axis (except y)
        amplitude_x = random.uniform(3.0, 10.0)
        amplitude_z = random.uniform(3.0, 10.0)
        frequency_x = random.uniform(0.5, 2.0)
        frequency_z = random.uniform(0.5, 2.0)
        phase_x = random.uniform(0, 2 * math.pi)
        phase_z = random.uniform(0, 2 * math.pi)

        # target properties (dictionary)
        target = {
            "position": pygame.math.Vector3(initial_x, y, initial_z),
            "hitbox_position": pygame.math.Vector3(initial_x, 0, initial_z),
            "hit": False,
            "size": 2.0,
            "initial_x": initial_x,
            "initial_z": initial_z,
            "amplitude_x": amplitude_x,
            "amplitude_z": amplitude_z,
            "frequency_x": frequency_x,
            "frequency_z": frequency_z,
            "phase_x": phase_x,
            "phase_z": phase_z,
            "elapsed_time": 0.0,
        }
        targets.append(target)
    return targets
