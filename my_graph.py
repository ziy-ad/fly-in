from abc import ABC, abstractmethod
from typing import Any, List, Tuple
import pygame
import random
import graph_data
import webcolors

import time
def to_screen(x, y, camera_x, camera_y):
    screen_x = x  * graph_data.SCALE + 50 + camera_x
    screen_y = 400 - y * graph_data.SCALE + camera_y

    return (screen_x, screen_y)

class Zone:
    def __init__(self, name: str, coordinates: tuple, meta_data: dict = {}) -> None:
        self.name: str = name
        self.coordinates: Tuple[int, int] = coordinates
        self.meta_data : dict[str, str | int] = meta_data
        self.connections: List[dict] = []
        self.rank = 0
        self.drones_in = 0


    def draw_node(self, window: pygame.Surface, dx, dy):
        x, y = self.coordinates
        pygame.draw.circle(window, (220, 180, 255), to_screen(x, y, dx, dy), 20)
        pygame.draw.circle(window, self.meta_data['color'], to_screen(x, y, dx, dy), 15)

    def draw_edges(self, window: pygame.Surface, named_zones, dx, dy):
        start_pos = to_screen(self.coordinates[0], self.coordinates[1],dx, dy)

        for connection in self.connections:
            color = graph_data.edge_colors[named_zones[connection['name']].meta_data['zone']]
            end_pos = named_zones[connection['name']].coordinates
            end_pos = to_screen(end_pos[0], end_pos[1],dx, dy)
            pygame.draw.line(
                window,
                color,
                start_pos,
                end_pos,
                2
            )


class Drone:
    def __init__(self, current_hub, end_hub, i):
        self.img: pygame.surface.Surface = Drone.load_image()
        self.zone: dict[str, Any] = {"name": current_hub.name, "coordinates": current_hub.coordinates}
        self.index = i
        self.t = 0
        self.moving = 0
        self.target = end_hub
        self.visited = set()
        self.target_coordinates = self.target.coordinates
        self.drone_start_x = 0
        self.drone_start_y = 0
    

    def draw_drone(self, screen, camera_x, camera_y):
        x, y = self.zone['coordinates']
        screen_x, screen_y = to_screen(x, y, camera_x, camera_y)
        image_rect = self.img.get_rect(center=(screen_x, screen_y))
        screen.blit(self.img, image_rect)
    
    def move_drone(self, graph, parse, screen, display):
        while self.zone['coordinates'] != self.target_coordinates:
            display.dragging()
            screen.fill((25, 10, 40))

            for node in parse.zones:
                node.draw_edges(screen, parse.named_zones, display.camera_x, display.camera_y)
            for node in parse.zones:
                node.draw_node(screen, display.camera_x, display.camera_y)

            graph.draw_drones(screen, display.camera_x, display.camera_y)

            progress = min(self.t, 1)
            target_x = self.drone_start_x + (self.target_coordinates[0] - self.drone_start_x) * progress
            target_y = self.drone_start_y + (self.target_coordinates[1] - self.drone_start_y) * progress

            self.draw_drone(screen, display.camera_x, display.camera_y)
            self.t += graph_data.SPEED

            self.zone['coordinates'] = (target_x, target_y)
            if self.t >= 1:
                self.zone['coordinates'] = self.target_coordinates
            pygame.display.flip()
    
    def find_path(self, graph, parse, screen, display):
        visited = set()

        if self.zone['name'] == self.target.name:
            return 

        # while self.zone['name'] != self.target.name:
        self.visited.add(self.zone['name'])
        connections = parse.named_zones[self.zone['name']].connections
        min_rank = {'name': None, 'rank': float('inf')}
        for connection in connections:
            if connection['name'] not in self.visited:
                current = parse.named_zones[connection['name']]
                if current.rank < min_rank['rank']:
                    if current.drones_in >= current.meta_data['max_drones']:
                        continue
                    min_rank['name'] = connection['name']
                    min_rank['rank'] = parse.named_zones[connection['name']].rank
                    current.drones_in += 1

        if not min_rank['name']:
            return

        self.drone_start_x, self.drone_start_y = self.zone['coordinates']
        self.target_coordinates = parse.named_zones[min_rank['name']].coordinates
        self.t = 0

        self.move_drone(graph, parse, screen, display)
        parse.named_zones[self.zone['name']].drones_in -= 1
        self.zone['name'] = min_rank['name']


    @staticmethod
    def load_image() -> pygame.surface.Surface:
        image = pygame.image.load(random.choice(graph_data.drones))
        image = pygame.transform.scale(image, (60, 60))
        return image


class Graph:
    def __init__(self, nb_drones, start_hub, end_hub):
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.drones: List[Drone] = self.add_drones(nb_drones)

    def add_drones(self, n):
        result = []
        for i in range(n):
            result.append(Drone(self.start_hub, self.end_hub, i))
        return result

    def draw_drones(self, screen, camera_x, camera_y):
        for drone in self.drones:
            drone.draw_drone(screen, camera_x, camera_y)
    
    def move_drones(self,graph, parse, screen, display):
        for drone in self.drones:
            drone.move_drone(graph, parse, screen, display)

    def path_exist(self, parse):
        visited = set()
        queue = [self.start_hub]


        while queue:
            current = queue.pop(0)
            visited.add(current)
            if current.meta_data['zone'] == "blocked":
                continue
            if current == self.end_hub:
                return True
            for neighbor in current.connections:
                if parse.named_zones[neighbor['name']] not in visited:
                    queue.append(parse.named_zones[neighbor['name']])
        return False


    def rank_hubs(self, parse):
        heap = [parse.end_hub]
        visited = set()

        while heap:
            current = heap.pop(0)
            visited.add(current)
            if current == parse.start_hub:
                current.rank = 0
                break
            for neighbor in current.connections:
                neighbor = parse.named_zones[neighbor['name']]
                if neighbor not in visited:
                    heap.append(neighbor)
                    neighbor.rank = current.rank + graph_data.COST[neighbor.meta_data['zone']]