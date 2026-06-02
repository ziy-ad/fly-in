import sys
from my_graph import Zone, Graph
from my_parser import My_Parssing
import pygame
import time

def main():
    try:
        file_path = sys.argv[1]
    except Exception as e:
        print("file not provided\nUsage: python3 main.py map_name")
        exit(1)
    parse = My_Parssing(file_path)
    parse.parser()
    pygame.init()

    screen = pygame.display.set_mode((1600, 800))
    clock = pygame.time.Clock()

    start_hub = min(parse.zones, key=lambda x: x.coordinates[0])
    end_hub = max(parse.zones, key=lambda x: x.coordinates[0])
    graph = Graph(parse.nb_drones, start_hub)
    drone_start_x, drone_start_y = graph.drones[0].zone['coordinates']

    rendring = True
    draging = False
    cammera_x, cammera_y = (0, 0)


    t = 0
    speed = 0.01
    while rendring:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rendring = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    draging = True
                    last_x, last_y = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    draging = False

            if event.type == pygame.MOUSEMOTION:
                if draging:
                    dx = event.pos[0] - last_x
                    dy = event.pos[1] - last_y

                    cammera_x += dx
                    cammera_y += dy
                    last_x, last_y = event.pos


        screen.fill((25, 10, 40))
        for node in parse.zones:
            node.draw_edges(screen, parse.named_zones, cammera_x, cammera_y)
        for node in parse.zones:
            node.draw_node(screen, cammera_x, cammera_y)

        graph.draw_drones(screen, cammera_x, cammera_y)


        progress = min(t, 1)
        target_x = drone_start_x + (end_hub.coordinates[0] - drone_start_x) * progress
        target_y = drone_start_y + (end_hub.coordinates[1] - drone_start_y) * progress

        graph.drones[0].draw_drone(screen, cammera_x, cammera_y)
        t += speed

        graph.drones[0].zone['coordinates'] = (target_x, target_y)
        if t >= 1:
            graph.drones[0].zone['coordinates'] = end_hub.coordinates
        # print(self.zone['coordinates'])


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
