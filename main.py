import sys
from my_graph import Zone, Graph
from my_parser import My_Parssing
import pygame
import time
from graph_data import SPEED


class Display:
    def __init__(self, file_path):
        self.parse = My_Parssing(file_path)
        self.screen = pygame.display.set_mode((1600, 800))
        self.clock = pygame.time.Clock()
        self.rendring = True
        self.draging = False
        self.camera_x, self.camera_y = (0, 0)
        self.last_x = 0
        self.last_y = 0


    def dragging(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rendring = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.draging = True
                    self.last_x, self.last_y = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.draging = False

            if event.type == pygame.MOUSEMOTION:
                if self.draging:
                    dx = event.pos[0] - self.last_x
                    dy = event.pos[1] - self.last_y

                    self.camera_x += dx
                    self.camera_y += dy
                    self.last_x, self.last_y = event.pos

    def write_text(self, txt: str) -> None:
        """Render a single status line on the top left window."""
        pygame.init()
        font = pygame.font.SysFont("", 32)
        text_surface = font.render(txt, True, (255, 255, 255))
        self.screen.blit(text_surface, (50, 100))

def main():
    try:
        file_path = sys.argv[1]
    except Exception as e:
        print("file not provided\nUsage: python3 main.py map_name")
        exit(1)
    display = Display(file_path)
    parse = My_Parssing(file_path)
    parse.parser()

    graph = Graph(parse.nb_drones, parse.start_hub, parse.end_hub)
    if not graph.path_exist(parse):
        parse.log_and_exit("invalid path to end_hub !")
        exit(1)
    # print(len(graph. extract_all_paths(parse)))

    screen = pygame.display.set_mode((1600, 800))
    graph.rank_hubs(parse)

    while display.rendring:
        display.dragging()
        screen.fill((25, 10, 40))
        for node in parse.zones:
            node.draw_edges(screen, parse.named_zones, display.camera_x, display.camera_y)
        for node in parse.zones:
            node.draw_node(screen, display.camera_x, display.camera_y)

        graph.draw_drones(screen, display.camera_x, display.camera_y)
        graph.find_next_hubs(parse, screen, display)

        display.write_text(f"turns: {parse.turns}")
        pygame.display.flip()
        graph.clock.tick(60)

if __name__ == "__main__":
    main()
