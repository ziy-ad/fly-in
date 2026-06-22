import sys
from my_graph import Graph, Display
from my_parser import My_Parssing
import pygame


def main() -> None:
    """Main entry point for the drone graph simulation.

    Initializes the parser and display from a given file, validates
    the parsed graph, and runs the main pygame rendering loop to
    simulate drone movements between hubs.
    """
    try:
        file_path = sys.argv[1]
    except Exception:
        print(
            "file not provided\n"
            "Usage: python3 main.py map_name"
        )
        exit(1)
    display = Display(file_path)
    parse = My_Parssing(file_path)
    parse.parser()

    try:
        if parse.nb_drones is None:
            raise AssertionError()
        if parse.start_hub is None:
            raise AssertionError()
        if parse.end_hub is None:
            raise AssertionError()
    except AssertionError as e:
        parse.log_and_exit(0, e)

    graph = Graph(
        parse.nb_drones, parse.start_hub, parse.end_hub
    )
    if not graph.path_exist(parse):
        parse.log_and_exit(0, "invalid path to end_hub !")

    screen = pygame.display.set_mode((1600, 800))
    graph.rank_hubs(parse)

    while display.rendring:
        display.dragging()
        screen.fill((25, 10, 40))
        for node in parse.zones:
            node.draw_edges(
                screen,
                parse.named_zones,
                display.camera_x,
                display.camera_y,
            )
        for node in parse.zones:
            node.draw_node(
                screen, display.camera_x, display.camera_y
            )

        graph.draw_drones(
            screen, display.camera_x, display.camera_y
        )
        graph.find_next_hubs(parse, screen, display)

        display.write_text(f"turns: {parse.turns}")
        pygame.display.flip()
        if parse.end_hub.drones_in == parse.nb_drones:
            parse.i += 1
            if parse.i >= 60:
                return
        graph.clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        exit(0)
