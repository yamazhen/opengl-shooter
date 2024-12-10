import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Camera import *
from Target import draw_targets, update_targets, create_targets
from Crosshair import draw_crosshair
from LoadTexture import load_texture
from World import draw_ground
from Bullet import check_hits_continuous, shoot_bullet

pygame.init()

# Project settings
screen_width = 800
screen_height = 600
background_color = (0.53, 0.81, 0.92, 1.0)
drawing_color = (1, 1, 1, 1)
terrain_texture_id = None

# Define boundary limits
GROUND_MIN_X = -49.0
GROUND_MAX_X = 49.0
GROUND_MIN_Z = -49.0
GROUND_MAX_Z = 49.0

screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Simple 3D Shooter")
camera = Camera(
    ground_min_x=GROUND_MIN_X,
    ground_max_x=GROUND_MAX_X,
    ground_min_z=GROUND_MIN_Z,
    ground_max_z=GROUND_MAX_Z,
)


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


def display(targets, bullets):
    glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))
    init_camera()
    camera.apply()
    draw_ground(terrain_texture_id)
    draw_targets(targets)

    for bullet in bullets:
        bullet.draw()

    draw_crosshair(screen.get_width(), screen.get_height())


def main():
    clock = pygame.time.Clock()
    done = False
    initialise()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    targets = create_targets()
    bullets = []

    while not done:
        delta_time = clock.tick(60) / 1000.0  # Time in seconds since last frame
        delta_time = min(delta_time, 0.05)  # Clamp to avoid large delta_time spikes

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

        # Update camera orientation and position
        camera.update(screen.get_width(), screen.get_height(), delta_time)

        # Update target positions with delta_time
        update_targets(targets, delta_time)

        # Update bullets and check collisions
        bullets_to_remove = []
        for bullet in bullets:
            bullet.update(delta_time)
            if check_hits_continuous(targets, bullet):
                bullets_to_remove.append(bullet)
            elif not bullet.is_alive():
                bullets_to_remove.append(bullet)

        # Draw everything
        display(targets, bullets)

        # Remove bullets after drawing
        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        pygame.display.flip()

        if all(target["hit"] for target in targets):
            print("All targets eliminated! You win!")
            pygame.quit()
            exit()

    pygame.quit()


if __name__ == "__main__":
    main()
