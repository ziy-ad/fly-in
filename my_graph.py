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
        self.rank = float('inf')
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
        self.visited = set()
        self.index = i
        self.t = 0
        self.moving = 0
        self.target = None
        self.target_coordinates = self.zone['coordinates']
        self.previous = None
        self.drone_start_x = 0
        self.drone_start_y = 0
        self.logs = []
    

    def draw_drone(self, screen, camera_x, camera_y):
        x, y = self.zone['coordinates']
        screen_x, screen_y = to_screen(x, y, camera_x, camera_y)
        image_rect = self.img.get_rect(center=(screen_x, screen_y))
        screen.blit(self.img, image_rect)
    
    def move_drone(self, graph, parse, screen, display) -> bool:
        if self.zone['coordinates'] == self.target_coordinates:
            return True

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
        graph.clock.tick(60)
        return False


    @staticmethod
    def load_image() -> pygame.surface.Surface:
        image = pygame.image.load(random.choice(graph_data.drones))
        image = pygame.transform.scale(image, (60, 60))
        return image


    def find_next_move(self, parse, graph) -> None:
        if self.zone['name'] == parse.end_hub.name:
            # if parse.end_hub.meta_data['zone'] == 'restricted':
            #     self.logs.append(f"D{self.index}-{.name}-{min_rank['name']}")
            # self.logs.append(f"D{self.index}-{min_rank['name']}")
            return

        if self.target is not None:
            return
        
        connections = parse.named_zones[self.zone['name']].connections
        min_hub = min(connections, key=lambda x: parse.named_zones[x['name']].rank)
        min_rank = {'name': None, 'rank': float('inf')}


        if not min_hub or parse.named_zones[min_hub['name']].rank == float('inf'):
            return

        min_rank['name'] = min_hub['name']
        min_rank['rank'] = parse.named_zones[min_hub['name']].rank

        current = parse.named_zones[min_hub['name']]

        if current.drones_in < current.meta_data['max_drones']:
            parse.named_zones[min_rank['name']].drones_in += 1
        
            if parse.named_zones[min_rank['name']].meta_data['zone'] == 'restricted':
                self.logs.append(f"D{self.index}-{current.name}-{min_rank['name']}")
            self.logs.append(f"D{self.index}-{min_rank['name']}")
            self.target = min_rank['name']
        else:
            filtred_connections = []
            for connection in connections:
                current = parse.named_zones[connection['name']]
                if current.rank == min_rank['rank'] or current.rank == min_rank['rank'] + 1:
                    if current.name != min_rank['name']:
                        filtred_connections.append(connection)
            if filtred_connections:
                print(filtred_connections)




    # def find_next_move(self, parse, graph) -> None:
    #     if self.zone['name'] == parse.end_hub.name:
    #         # if parse.end_hub.meta_data['zone'] == 'restricted':
    #         #     self.logs.append(f"D{self.index}-{.name}-{min_rank['name']}")
    #         # self.logs.append(f"D{self.index}-{min_rank['name']}")
    #         return

    #     if self.target is not None:
    #         return

    #     connections = parse.named_zones[self.zone['name']].connections
        
    #     # sorted_connections = sorted(connections, key=lambda x: parse.named_zones[x['name']].rank)
    #     # min_name = sorted_connections[0]['name']
    #     min_rank = {'name': None, 'rank': float('inf')}

    #     for connection in connections:
    #         current = parse.named_zones[connection['name']]
    #         if current.rank < min_rank['rank']:
    #             min_rank['rank'] = current.rank
    #             min_rank['name'] = current.name
        
    #     current = parse.named_zones[min_rank['name']]
    #     if current.drones_in < current.meta_data['max_drones'] and min_rank['name'] != self.previous:
    #         parse.named_zones[min_rank['name']].drones_in += 1
        
    #         if parse.named_zones[min_rank['name']].meta_data['zone'] == 'restricted':
    #             self.logs.append(f"D{self.index}-{current.name}-{min_rank['name']}")
    #         self.logs.append(f"D{self.index}-{min_rank['name']}")
    #         self.target = min_rank['name']
    #         return

    #     for connection in connections:
    #         current = parse.named_zones[connection['name']]
    #         if current.rank == min_rank['rank'] or current.rank == min_rank['rank'] + 1:
    #             if current.drones_in < current.meta_data['max_drones'] and current.name != self.previous:
    #                 min_rank['rank'] = current.rank
    #                 min_rank['name'] = current.name
                


    #     # filtred_connections = []
    #     # for connection in connections:
    #     #     current = parse.named_zones[connection['name']]
    #     #     if current.drones_in < current.meta_data['max_drones'] and current.rank != float('inf'):
    #     #         if current.name != self.previous:
    #     #             filtred_connections.append(connection)

        
    #     # if filtred_connections:
    #     #     filtred_connections = sorted(filtred_connections,  key=lambda x: parse.named_zones[x['name']].rank)
    #     #     min_rank['name'] = filtred_connections[0]['name']
    #     #     min_rank['rank'] = parse.named_zones[connection['name']].rank

    #     if not min_rank['name']:
    #         self.target = None
    #         return
        
    #     parse.named_zones[min_rank['name']].drones_in += 1
        
    #     if parse.named_zones[min_rank['name']].meta_data['zone'] == 'restricted':
    #         self.logs.append(f"D{self.index}-{current.name}-{min_rank['name']}")
    #     self.logs.append(f"D{self.index}-{min_rank['name']}")
    #     self.target = min_rank['name']
        

class Graph:
    def __init__(self, nb_drones, start_hub, end_hub):
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.drones: List[Drone] = self.add_drones(nb_drones)
        self.visited = set()
        self.next_moves = []
        self.moving_drones = []  # Drones currently animating
        self.links_in_use = {}  # Track drones using each link: {(from, to): count}
        self.clock = pygame.time.Clock()

    def add_drones(self, n):
        result = []
        for i in range(n):
            result.append(Drone(self.start_hub, self.end_hub, i+1))
        return result
    
    def get_link_key(self, from_hub, to_hub):
        """Create a consistent key for bidirectional links"""
        return (from_hub, to_hub)
    
    def get_link_capacity(self, parse, from_hub_name, to_hub_name):
        """Get the max capacity of a link between two hubs"""
        from_hub = parse.named_zones[from_hub_name]
        for connection in from_hub.connections:
            if connection['name'] == to_hub_name:
                return connection.get('max_link_capacity', 1)
        return 1  # Default capacity if not found
    
    def get_link_usage(self, from_hub_name, to_hub_name):
        """Get current usage count of a link"""
        link_key = self.get_link_key(from_hub_name, to_hub_name)
        return self.links_in_use.get(link_key, 0)
    
    def increment_link_usage(self, from_hub_name, to_hub_name):
        """Increment link usage when drone starts moving"""
        link_key = self.get_link_key(from_hub_name, to_hub_name)
        self.links_in_use[link_key] = self.links_in_use.get(link_key, 0) + 1
    
    def decrement_link_usage(self, from_hub_name, to_hub_name):
        """Decrement link usage when drone finishes moving"""
        link_key = self.get_link_key(from_hub_name, to_hub_name)
        if link_key in self.links_in_use:
            self.links_in_use[link_key] = max(0, self.links_in_use[link_key] - 1)

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
        """
        Process one animation frame at a time, enabling smooth drone movement.
        This is called once per frame from the main loop.
        """
        
        # Step 1: Update drones that are currently animating
        drones_still_moving = []
        for drone in self.moving_drones:
            # Update animation progress
            progress = min(drone.t, 1)
            target_x = drone.drone_start_x + (drone.target_coordinates[0] - drone.drone_start_x) * progress
            target_y = drone.drone_start_y + (drone.target_coordinates[1] - drone.drone_start_y) * progress
            
            drone.zone['coordinates'] = (target_x, target_y)
            drone.t += graph_data.SPEED
            
            # Check if drone reached target
            if drone.t >= 1:
                drone.zone['coordinates'] = drone.target_coordinates
                # Finalize arrival
                if drone.target != parse.end_hub.name:
                    parse.named_zones[drone.target].drones_in -= 1
                else:
                    drone.visited.add(drone.target)
                
                # NEW: Decrement link usage when drone arrives
                self.decrement_link_usage(drone.zone['name'], drone.target)
                
                drone.previous = drone.zone['name']
                drone.zone['name'] = drone.target
                drone.target = None
            else:
                # Still animating
                drones_still_moving.append(drone)
        
        self.moving_drones = drones_still_moving
        
        # Step 2: Find new targets for drones that aren't moving
        for drone in self.drones:
            if drone not in self.moving_drones and drone.zone['name'] != parse.end_hub.name:
                drone.find_next_move(parse, self)
                if drone.target:
                    # Prepare to animate this drone
                    drone.drone_start_x, drone.drone_start_y = drone.zone['coordinates']
                    drone.target_coordinates = parse.named_zones[drone.target].coordinates
                    drone.t = 0
                    self.moving_drones.append(drone)
        
        # Step 3: Print logs (once per move initiation)
        logs_exist = False
        for drone in self.drones:
            if drone.logs:
                logs_exist = True 
                print(drone.logs.pop(0), end=" ", flush=True)
        if logs_exist:
            parse.turns += 1
            print()

    # def extract_all_paths(self, parse):
    #     """Extract all possible paths from start_hub to end_hub"""
    #     all_paths = []
        
    #     def dfs(current_zone, target_zone, path, visited):
    #         # Base case: reached the target (use object comparison, not name)
    #         if current_zone is target_zone:
    #             all_paths.append(path[:])
    #             return
            
    #         # Prevent cycles: add to visited before exploring
    #         visited.add(current_zone.name)
            
    #         # Explore all neighbors sorted by rank (greedy preference)
    #         neighbors = sorted(
    #             current_zone.connections, 
    #             key=lambda x: parse.named_zones[x['name']].rank
    #         )
            
    #         for connection in neighbors:
    #             neighbor_name = connection['name']
    #             # Skip if already visited or if it's a blocked zone
    #             if neighbor_name in visited:
    #                 continue
                
    #             neighbor_zone = parse.named_zones[neighbor_name]
                
    #             # Skip blocked zones unless it's the target
    #             if (neighbor_zone.meta_data.get('zone') == 'blocked' and 
    #                 neighbor_zone is not target_zone):
    #                 continue
                
    #             path.append(neighbor_zone.name)
    #             dfs(neighbor_zone, target_zone, path, visited)
    #             path.pop()
            
    #         # Backtrack: remove from visited to allow other paths
    #         visited.remove(current_zone.name)
        
    #     # Start DFS from start_hub with its name in the path
    #     dfs(self.start_hub, self.end_hub, [self.start_hub.name], set())
    #     return all_paths

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