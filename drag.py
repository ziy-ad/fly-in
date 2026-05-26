import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))

clock = pygame.time.Clock()

camera_x = 0
camera_y = 0

dragging = False

last_mouse_x = 0
last_mouse_y = 0

nodes = [
    (-200, 0),
    (0, 100),
    (300, -150)
]

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # START DRAG
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse_x, last_mouse_y = event.pos

        # STOP DRAG
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        # DRAGGING
        if event.type == pygame.MOUSEMOTION:
            if dragging:

                mouse_x, mouse_y = event.pos

                dx = mouse_x - last_mouse_x
                dy = mouse_y - last_mouse_y

                camera_x += dx
                camera_y += dy

                last_mouse_x = mouse_x
                last_mouse_y = mouse_y

    screen.fill((30,30,30))

    for node_x, node_y in nodes:

        screen_x = node_x + camera_x
        screen_y = node_y + camera_y

        pygame.draw.circle(
            screen,
            (0,200,255),
            (screen_x, screen_y),
            20
        )

    pygame.display.update()

    clock.tick(10)

pygame.quit()
