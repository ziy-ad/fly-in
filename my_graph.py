from abc import ABC, abstractmethod
from typing import Any, List, Tuple
import pygame
import random
import graph_data
import webcolors


ZONE_RADIUS = 100
SCALE = 60

import time
def to_screen(x, y, camera_x, camera_y):
    screen_x = x  * SCALE + 50 + camera_x
    screen_y = 400 - y * SCALE + camera_y

    return (screen_x, screen_y)

class Zone:
    def __init__(self, name: str, coordinates: tuple, meta_data: dict = {}) -> None:
        self.name: str = name
        self.coordinates: Tuple[int, int] = coordinates
        self.meta_data : dict[str, str | int] = meta_data
        self.connections: List[dict] = []
        self.rank = 0


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
    def __init__(self, current_hub, end_hub):
        self.img: pygame.surface.Surface = Drone.load_image()
        self.zone: dict[str, Any] = {"name": current_hub.name, "coordinates": current_hub.coordinates}
        self.t = 0
        self.moving = 0
        self.target = end_hub
        self.drone_start_x = 0
        self.drone_start_y = 0
    

    def draw_drone(self, screen, camera_x, camera_y):
        x, y = self.zone['coordinates']
        screen_x, screen_y = to_screen(x, y, camera_x, camera_y)
        image_rect = self.img.get_rect(center=(screen_x, screen_y))
        screen.blit(self.img, image_rect)
    
    def move_drone(self, screen, camera_x, camera_y) -> bool:
        progress = min(self.t, 1)
        target_x = self.drone_start_x + (self.target.coordinates[0] - self.drone_start_x) * progress
        target_y = self.drone_start_y + (self.target.coordinates[1] - self.drone_start_y) * progress

        self.draw_drone(screen, camera_x, camera_y)
        self.t += graph_data.SPEED

        self.zone['coordinates'] = (target_x, target_y)
        if self.t >= 1:
            self.zone['coordinates'] = self.target.coordinates
            return True
        elif self.zone['coordinates'] == self.target.coordinates:
            return True
        return False



    @staticmethod
    def load_image() -> pygame.surface.Surface:
        image = pygame.image.load(random.choice(graph_data.drones))
        image = pygame.transform.scale(image, (60, 60))
        return image


class Graph:
    def __init__(self, nb_drones, current_hub, end_hub):
        self.current_hub = current_hub
        self.end_hub = end_hub
        self.drones: List[Drone] = self.add_drones(nb_drones)

    def add_drones(self, n):
        result = []
        for i in range(n):
            result.append(Drone(self.current_hub, self.end_hub))
        return result

    def draw_drones(self,screen, camera_x, camera_y):
        for drone in self.drones:
            drone.draw_drone(screen, camera_x, camera_y)
    
    def move_drones(self, screen, camera_x, camera_y):
        self.drones[0].move_drone(screen, camera_x, camera_y)



    def rank_hubs(self, parse):
        heap = [parse.end_hub]
        visited = set()

        def rank_hub(current, previous_hub):
            current.rank = previous_hub.rank + 1

        while heap:
            current = heap.pop(0)
            visited.add(current)
            if parse.start_hub == current:
                print("start_hub: ", current.meta_data['color'], current.rank)
            elif parse.end_hub == current:
                print("end_hub: ", current.meta_data['color'], current.rank)
            else:
                print(webcolors.rgb_to_name(current.meta_data['color']), current.rank)
            for neighbor in current.connections:
                neighbor = parse.named_zones[neighbor['name']]
                if neighbor not in visited:
                    heap.append(neighbor)
                neighbor.rank = current.rank + 1
