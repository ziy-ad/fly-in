import sys
from my_graph import Zone, Graph
from my_parser import My_Parssing
import pygame
import time
from graph_data import SPEED

def main():
    try:
        file_path = sys.argv[1]
    except Exception as e:
        print("file not provided\nUsage: python3 main.py map_name")
        exit(1)
    parse = My_Parssing(file_path)
    parse.parser()
    pygame.init()


    print(parse.named_zones[parse.start_hub.connections[0]['name']])
    screen = pygame.display.set_mode((1600, 800))
    clock = pygame.time.Clock()
    
    print()

    graph = Graph(parse.nb_drones, parse.start_hub, parse.end_hub)
    graph.rank_hubs(parse)

        
    drone_start_x, drone_start_y = graph.drones[0].zone['coordinates']

    rendring = True
    draging = False
    cammera_x, cammera_y = (0, 0)


    t = 0
    i = 0
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
        
        if i >= 0:
            if graph.drones[i].move_drone(screen, cammera_x, cammera_y):
                if i == len(graph.drones) - 1:
                    i = -1
                else:
                    i += 1


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
