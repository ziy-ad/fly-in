import pygame
import sys

pygame.init()

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Graph Animation")

clock = pygame.time.Clock()

# Colors
BG = (30, 30, 30)
NODE_COLOR = (100, 200, 255)
EDGE_COLOR = (180, 180, 180)
POINT_COLOR = (255, 100, 100)

font = pygame.font.SysFont(None, 24)

# Node class
class Node:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.x = x
        self.y = y

# Nodes
nodes = [
    Node(0, 100, 100),
    Node(1, 500, 300),
]

# Edge
edge = (0, 1)

# Animation progress
t = 0.0
speed = 0.005

running = True

while running:

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # BACKGROUND
    screen.fill(BG)

    # GET NODES
    start_node = nodes[edge[0]]
    end_node = nodes[edge[1]]

    # DRAW EDGE
    pygame.draw.line(
        screen,
        EDGE_COLOR,
        (start_node.x, start_node.y),
        (end_node.x, end_node.y),
        3
    )

    # DRAW NODES
    for node in nodes:

        pygame.draw.circle(
            screen,
            NODE_COLOR,
            (node.x, node.y),
            20
        )

        # label = font.render(str(node.id), True, (255,255,255))
        # rect = label.get_rect(center=(node.x, node.y))
        # screen.blit(label, rect)

    # ---- ANIMATION ----

    # Linear interpolation
    x = start_node.x + (end_node.x - start_node.x) * t
    y = start_node.y + (end_node.y - start_node.y) * t

    # Draw moving point
    pygame.draw.circle(
        screen,
        POINT_COLOR,
        (int(x), int(y)),
        10
    )

    # Update progress
    t += speed

    # Restart animation
    if t > 1:
        t = 0

    # UPDATE SCREEN
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
