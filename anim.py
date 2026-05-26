import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Start and target positions
x, y = 100, 100
target_x, target_y = 600, 400

speed = 5  # pixels per frame

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Compute direction vector
    dx = target_x - x
    dy = target_y - y

    distance = math.hypot(dx, dy)

    # Move toward target
    if distance > speed:
        dx /= distance
        dy /= distance

        x += dx * speed
        y += dy * speed
    else:
        # Snap to target when close enough
        x = target_x
        y = target_y

    # Draw
    screen.fill((30, 30, 30))
    pygame.draw.circle(screen, (255, 100, 100), (int(x), int(y)), 20)

    pygame.display.flip()

pygame.quit()
