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
        self.target = None
        self.visited = set()
        self.target_coordinates = self.zone['coordinates']
        self.drone_start_x = 0
        self.drone_start_y = 0
    

    def draw_drone(self, screen, camera_x, camera_y):
        x, y = self.zone['coordinates']
        screen_x, screen_y = to_screen(x, y, camera_x, camera_y)
        image_rect = self.img.get_rect(center=(screen_x, screen_y))
        screen.blit(self.img, image_rect)
    
    def move_drone(self, graph, parse, screen, display) -> bool:
        # Check if we've reached the target (with small tolerance for floating point)
        if self.t >= 1:
            self.zone['coordinates'] = self.target_coordinates
            return True

        display.dragging()
        screen.fill((25, 10, 40))

        for node in parse.zones:
            node.draw_edges(screen, parse.named_zones, display.camera_x, display.camera_y)
        for node in parse.zones:
            node.draw_node(screen, display.camera_x, display.camera_y)

        graph.draw_drones(screen, display.camera_x, display.camera_y)

        # Interpolate position smoothly
        progress = min(self.t, 1)
        target_x = self.drone_start_x + (self.target_coordinates[0] - self.drone_start_x) * progress
        target_y = self.drone_start_y + (self.target_coordinates[1] - self.drone_start_y) * progress

        # Update zone coordinates for this frame
        self.zone['coordinates'] = (target_x, target_y)
        
        self.draw_drone(screen, display.camera_x, display.camera_y)
        pygame.display.flip()
        
        # Increment progress after drawing
        self.t += graph_data.SPEED
        
        graph.clock.tick(60)
        return False
    
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
                if current.rank <= min_rank['rank']:
                    if current.drones_in < current.meta_data['max_drones']:
                        min_rank['name'] = connection['name']
                        min_rank['rank'] = parse.named_zones[connection['name']].rank
                        current.drones_in += 1
                        # continue

        if not min_rank['name']:
            return

        self.drone_start_x, self.drone_start_y = self.zone['coordinates']
        self.target_coordinates = parse.named_zones[min_rank['name']].coordinates
        self.t = 0

        i = 0
        while not self.move_drone(graph, parse, screen, display):
            # print(i)
            i += 1
        parse.named_zones[self.zone['name']].drones_in -= 1
        self.zone['name'] = min_rank['name']


    @staticmethod
    def load_image() -> pygame.surface.Surface:
        image = pygame.image.load(random.choice(graph_data.drones))
        image = pygame.transform.scale(image, (60, 60))
        return image
    
    def find_next_move(self, parse, graph) -> list:
        if self.zone['name'] == parse.end_hub.name:
            return

        if self.target is not None:
            return

        connections = parse.named_zones[self.zone['name']].connections
        min_rank = {'name': None, 'rank': float('inf')}
        
        sorted_connections = sorted(connections, key=lambda x: parse.named_zones[x['name']].rank)

        for connection in sorted_connections:
            current = parse.named_zones[connection['name']]
            if current.rank == float('inf'):
                break
            if current.rank <= min_rank['rank']:
                    if current.drones_in < current.meta_data['max_drones']:
                        min_rank['name'] = connection['name']
                        min_rank['rank'] = parse.named_zones[connection['name']].rank

        if not min_rank['name']:
            return
        
        parse.named_zones[min_rank['name']].drones_in += 1
        self.target = min_rank['name']
        
        

class Graph:
    def __init__(self, nb_drones, start_hub, end_hub):
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.drones: List[Drone] = self.add_drones(nb_drones)
        self.visited = set()
        self.next_moves = []
        self.clock = pygame.time.Clock()

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
        parse.end_hub.rank = 0

        while heap:
            current = heap.pop(0)
            visited.add(current)
            for neighbor in current.connections:
                neighbor = parse.named_zones[neighbor['name']]
                if neighbor not in visited:
                    heap.append(neighbor)
                    neighbor.rank = current.rank + graph_data.COST[neighbor.meta_data['zone']]

    
    def find_next_hubs(self, parse, screen, display):
        for drone in self.drones:
            drone.find_next_move(parse, self)
            if drone.target:
                self.next_moves.append(drone)

        # for next_move in self.next_moves:
        #     print('--------------')
        #     print(f"D{next_move.index} {next_move.target}")
        
        while self.next_moves:
            current = self.next_moves.pop(0)
            current.drone_start_x, current.drone_start_y = current.zone['coordinates']
            current.target_coordinates = parse.named_zones[current.target].coordinates
            if not current.move_drone(self, parse, screen, display):
                self.next_moves.append(current)
            else:
                # Drone arrived at target; decrement the target's occupancy
                if current.target != parse.end_hub.name:
                    parse.named_zones[current.target].drones_in -= 1
                current.zone['name'] = current.target
                current.target = None


    # def print_zones(self, parse):
    #     visited = set()
    #     queue = [self.start_hub]

    #     while queue:
    #         current = queue.pop(0)
    #         visited.add(current)
    #         print(current.name, current.drones_in, end=" ")
    #         for neighbor in current.connections:
    #             if parse.named_zones[neighbor['name']] not in visited:
    #                 queue.append(parse.named_zones[neighbor['name']])
    #     print()