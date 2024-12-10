import math
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import GLU_SMOOTH, gluNewQuadric, gluCylinder, gluQuadricNormals


def draw_hemisphere(radius, slices, stacks):
    """Draws a hemisphere aligned along the positive y-axis."""
    for i in range(stacks):
        lat0 = (math.pi / 2) * (i / stacks)  # Start latitude
        lat1 = (math.pi / 2) * ((i + 1) / stacks)  # End latitude

        z0 = math.sin(lat0)
        zr0 = math.cos(lat0)

        z1 = math.sin(lat1)
        zr1 = math.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)
            x = math.cos(lng)
            y = math.sin(lng)

            # First vertex (lower latitude)
            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)

            # Second vertex (upper latitude)
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
        glEnd()


def draw_capsule(size, slices=16, stacks=16):
    """
    Draws a capsule aligned along the y-axis.

    Parameters:
    - size: Total height of the capsule.
    - slices: Number of subdivisions around the z-axis.
    - stacks: Number of subdivisions along the y-axis.
    """
    radius = size / 4.0  # Adjust radius as needed
    cylinder_height = size - 2 * radius

    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)

    # Draw the cylinder aligned along y-axis
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Rotate to align with y-axis
    gluCylinder(quadric, radius, radius, cylinder_height, slices, stacks)
    glPopMatrix()

    # Draw the top hemisphere at the end of the cylinder
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Rotate to align with y-axis
    glTranslatef(0.0, 0.0, cylinder_height)  # Move along the new z-axis
    draw_hemisphere(radius, slices, stacks)
    glPopMatrix()

    # Draw the bottom hemisphere at the base of the cylinder
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Rotate to align with y-axis
    glRotatef(180, 1, 0, 0)  # Flip hemisphere downward
    # No translation needed; the base is already at z=0 after rotation
    draw_hemisphere(radius, slices, stacks)
    glPopMatrix()


def draw_targets(targets):
    for target in targets:
        if not target["hit"]:
            glPushMatrix()
            glColor(1, 0, 0)  # Red for active targets
            glTranslatef(
                target["position"].x, target["position"].y, target["position"].z
            )
            draw_capsule(target["size"])
            glPopMatrix()


def update_targets(targets, delta_time):
    for target in targets:
        if target["hit"]:
            continue

        # Update elapsed time
        target["elapsed_time"] += delta_time

        # Calculate new positions based on elapsed time
        new_x = target["initial_x"] + target["amplitude_x"] * math.sin(
            target["frequency_x"] * target["elapsed_time"] + target["phase_x"]
        )
        new_z = target["initial_z"] + target["amplitude_z"] * math.cos(
            target["frequency_z"] * target["elapsed_time"] + target["phase_z"]
        )

        target["position"].x = new_x
        target["position"].z = new_z


def create_targets():
    targets = []
    num_targets = 10
    field_min = -45
    field_max = 45

    for _ in range(num_targets):
        initial_x = random.uniform(field_min, field_max)
        initial_z = random.uniform(field_min, field_max)
        y = -0.5

        # Randomize movement parameters for each axis
        amplitude_x = random.uniform(3.0, 10.0)
        amplitude_z = random.uniform(3.0, 10.0)
        frequency_x = random.uniform(0.5, 2.0)  # Oscillations per second
        frequency_z = random.uniform(0.5, 2.0)
        phase_x = random.uniform(0, 2 * math.pi)
        phase_z = random.uniform(0, 2 * math.pi)

        target = {
            "position": pygame.math.Vector3(initial_x, y, initial_z),
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
            "elapsed_time": 0.0,  # Initialize elapsed time
        }
        targets.append(target)
    return targets
