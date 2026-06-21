from typing import Any, List, Tuple
import pygame
import random
import graph_data


class Display:
    def __init__(self, file_path: str) -> None:
        self.screen: pygame.Surface = pygame.display.set_mode(
            (1600, 800)
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.rendring: bool = True
        self.draging: bool = False
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.last_x: int = 0
        self.last_y: int = 0

    @staticmethod
    def to_screen(
        x: int,
        y: int,
        camera_x: int,
        camera_y: int,
    ) -> Tuple[int, int]:
        screen_x: int = x * graph_data.SCALE + 50 + camera_x
        screen_y: int = 400 - y * graph_data.SCALE + camera_y

        return (screen_x, screen_y)

    def dragging(self) -> None:
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
        """Render a single status line on the top left."""
        pygame.init()
        font: pygame.font.Font = pygame.font.SysFont(
            "", 32
        )
        text_surface: pygame.Surface = font.render(
            txt, True, (255, 255, 255)
        )
        self.screen.blit(text_surface, (50, 100))


class Zone:
    def __init__(
        self,
        name: str,
        coordinates: Tuple[int, int],
        meta_data: dict[str, str | int] | None = None,
    ) -> None:
        self.name: str = name
        self.coordinates: Tuple[int, int] = coordinates
        self.meta_data: dict[str, str | int] = (
            meta_data if meta_data is not None else {}
        )
        self.connections: List[dict[str, Any]] = []
        self.rank: float = float("inf")
        self.drones_in: int = 0

    def draw_node(
        self,
        window: pygame.Surface,
        dx: int,
        dy: int,
    ) -> None:
        x, y = self.coordinates
        pygame.draw.circle(
            window,
            (220, 180, 255),
            Display.to_screen(x, y, dx, dy),
            20,
        )
        pygame.draw.circle(
            window,
            self.meta_data["color"],
            Display.to_screen(x, y, dx, dy),
            15,
        )

    def draw_edges(
        self,
        window: pygame.Surface,
        named_zones: dict[str, "Zone"],
        dx: int,
        dy: int,
    ) -> None:
        start_pos = Display.to_screen(
            self.coordinates[0], self.coordinates[1], dx, dy
        )

        for connection in self.connections:
            zone_type = self.meta_data["zone"]
            try:
                assert isinstance(zone_type, str)
            except AssertionError as e:
                print(e)
                exit(0)
            color = graph_data.edge_colors[zone_type]
            end_pos = named_zones[
                connection["name"]
            ].coordinates
            end_pos = Display.to_screen(
                end_pos[0], end_pos[1], dx, dy
            )
            pygame.draw.line(
                window, color, start_pos, end_pos, 2
            )


class Drone:
    def __init__(
        self,
        current_hub: "Zone",
        end_hub: "Zone",
        i: int,
    ) -> None:
        self.img: pygame.Surface = Drone.load_image()
        self.zone: dict[str, Any] = {
            "name": current_hub.name,
            "coordinates": current_hub.coordinates,
        }
        self.visited: set[Any] = set()
        self.index: int = i
        self.t: float = 0
        self.target: str | None = None
        self.target_coordinates: Tuple[
            int, int
        ] = self.zone["coordinates"]
        self.previous: str | None = None
        self.drone_start_x: int = 0
        self.drone_start_y: int = 0
        self.logs: List[str] = []
        self.in_restricted: int = 0

    def draw_drone(
        self,
        screen: pygame.Surface,
        camera_x: int,
        camera_y: int,
    ) -> None:
        x, y = self.zone["coordinates"]
        screen_x, screen_y = Display.to_screen(
            x, y, camera_x, camera_y
        )
        image_rect = self.img.get_rect(
            center=(screen_x, screen_y)
        )
        screen.blit(self.img, image_rect)

    def move_drone(
        self,
        graph: "Graph",
        parse: Any,
        screen: pygame.Surface,
        display: Display,
    ) -> bool:
        if (
            self.zone["coordinates"]
            == self.target_coordinates
        ):
            return True

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

        progress = min(self.t, 1)
        target_x = (
            self.drone_start_x
            + (
                self.target_coordinates[0]
                - self.drone_start_x
            )
            * progress
        )
        target_y = (
            self.drone_start_y
            + (
                self.target_coordinates[1]
                - self.drone_start_y
            )
            * progress
        )

        self.draw_drone(
            screen, display.camera_x, display.camera_y
        )
        self.t += graph_data.SPEED

        self.zone["coordinates"] = (target_x, target_y)
        if self.t >= 1:
            self.zone[
                "coordinates"
            ] = self.target_coordinates
        pygame.display.flip()
        graph.clock.tick(60)
        return False

    @staticmethod
    def load_image() -> pygame.Surface:
        image: pygame.Surface = pygame.image.load(
            random.choice(graph_data.drones)
        )
        image = pygame.transform.scale(image, (60, 60))
        return image

    def find_next_move(
        self, parse: Any, graph: "Graph"
    ) -> None:
        if self.zone["name"] == parse.end_hub.name:
            return

        if self.target is not None:
            return

        connections = parse.named_zones[
            self.zone["name"]
        ].connections
        if not connections:
            return

        # Sort connections by rank to evaluate best first
        sorted_connections = sorted(
            connections,
            key=lambda x: parse.named_zones[
                x["name"]
            ].rank,
        )

        min_rank: dict[str, Any] = {
            "name": None,
            "rank": float("inf"),
        }
        if sorted_connections:
            min_rank["name"] = sorted_connections[0][
                "name"
            ]
            min_rank["rank"] = parse.named_zones[
                min_rank["name"]
            ].rank

        if (
            not min_rank["name"]
            or min_rank["rank"] == float("inf")
        ):
            return

        # 1. Try the best minimum rank connection
        best_node = parse.named_zones[min_rank["name"]]
        link_cap = graph.get_link_capacity(
            parse, self.zone["name"], best_node.name
        )
        link_use = graph.get_link_usage(
            self.zone["name"], best_node.name
        )

        if (
            best_node.drones_in
            < best_node.meta_data["max_drones"]
            and link_use < link_cap
        ):
            parse.named_zones[
                self.zone["name"]
            ].drones_in -= 1
            best_node.drones_in += 1

            self.target = best_node.name
            if best_node.meta_data["zone"] == "restricted":
                self.logs.append(
                    f"D{self.index}-"
                    f"{self.zone['name']}-"
                    f"{best_node.name}"
                )
                self.in_restricted = 1
            else:
                self.logs.append(
                    f"D{self.index}-{best_node.name}"
                )
            return

        # 2. Look for alternatives of equal/higher rank
        for connection in sorted_connections:
            current = parse.named_zones[
                connection["name"]
            ]
            if (
                current.rank == min_rank["rank"]
                or current.rank == min_rank["rank"] + 1
            ):
                if current.name == min_rank["name"]:
                    continue

                link_cap = graph.get_link_capacity(
                    parse,
                    self.zone["name"],
                    current.name,
                )
                link_use = graph.get_link_usage(
                    self.zone["name"], current.name
                )

                if (
                    current.drones_in
                    < current.meta_data["max_drones"]
                    and link_use < link_cap
                ):
                    parse.named_zones[
                        self.zone["name"]
                    ].drones_in -= 1
                    current.drones_in += 1

                    self.target = current.name
                    if (
                        current.meta_data["zone"]
                        == "restricted"
                    ):
                        self.logs.append(
                            f"D{self.index}-"
                            f"{self.zone['name']}-"
                            f"{current.name}"
                        )
                        self.in_restricted = 1
                    else:
                        self.logs.append(
                            f"D{self.index}-{current.name}"
                        )
                    return


class Graph:
    def __init__(
        self,
        nb_drones: int,
        start_hub: "Zone",
        end_hub: "Zone",
    ) -> None:
        self.start_hub: "Zone" = start_hub
        self.end_hub: "Zone" = end_hub
        self.drones: List["Drone"] = self.add_drones(
            nb_drones
        )
        self.visited: set[Any] = set()
        self.next_moves: List[Any] = []
        self.moving_drones: List["Drone"] = []
        self.links_in_use: dict[
            Tuple[str, str], int
        ] = {}
        self.clock: pygame.time.Clock = (
            pygame.time.Clock()
        )

    def add_drones(self, n: int) -> List["Drone"]:
        result: List["Drone"] = []
        for i in range(n):
            result.append(
                Drone(self.start_hub, self.end_hub, i + 1)
            )
        return result

    @staticmethod
    def get_link_key(
        from_hub: str, to_hub: str
    ) -> Tuple[str, str]:
        """Create a consistent key for bidir links"""
        return (from_hub, to_hub)

    def get_link_capacity(
        self,
        parse: Any,
        from_hub_name: str,
        to_hub_name: str,
    ) -> int:
        """Get the max capacity of a link"""
        from_hub = parse.named_zones[from_hub_name]
        for connection in from_hub.connections:
            if connection["name"] == to_hub_name:
                cap = connection.get("max_link_capacity", 1)
                try:                
                    assert isinstance(cap, int)
                except AssertionError as e:
                    print(e)
                    exit(0)
                return cap
        return 1

    def get_link_usage(
        self, from_hub_name: str, to_hub_name: str
    ) -> int:
        """Get current usage count of a link"""
        link_key = self.get_link_key(
            from_hub_name, to_hub_name
        )
        return self.links_in_use.get(link_key, 0)

    def increment_link_usage(
        self, from_hub_name: str, to_hub_name: str
    ) -> None:
        """Increment link usage when drone moves"""
        link_key = self.get_link_key(
            from_hub_name, to_hub_name
        )
        self.links_in_use[link_key] = (
            self.links_in_use.get(link_key, 0) + 1
        )

    def decrement_link_usage(
        self, from_hub_name: str, to_hub_name: str
    ) -> None:
        """Decrement link usage when drone arrives"""
        link_key = self.get_link_key(
            from_hub_name, to_hub_name
        )
        if link_key in self.links_in_use:
            self.links_in_use[link_key] = max(
                0, self.links_in_use[link_key] - 1
            )

    def draw_drones(
        self,
        screen: pygame.Surface,
        camera_x: int,
        camera_y: int,
    ) -> None:
        for drone in self.drones:
            drone.draw_drone(
                screen, camera_x, camera_y
            )

    def move_drones(
        self,
        graph: "Graph",
        parse: Any,
        screen: pygame.Surface,
        display: Display,
    ) -> None:
        for drone in self.drones:
            drone.move_drone(
                graph, parse, screen, display
            )

    def path_exist(self, parse: Any) -> bool:
        visited: set[Any] = set()
        queue: List["Zone"] = [self.start_hub]

        while queue:
            current = queue.pop(0)
            visited.add(current)
            if current.meta_data["zone"] == "blocked":
                continue
            if current == self.end_hub:
                return True
            for neighbor in current.connections:
                if (
                    parse.named_zones[neighbor["name"]]
                    not in visited
                ):
                    queue.append(
                        parse.named_zones[
                            neighbor["name"]
                        ]
                    )
        return False

    def rank_hubs(self, parse: Any) -> None:
        heap: List["Zone"] = [parse.end_hub]
        visited: set[Any] = set()
        parse.end_hub.rank = 0

        while heap:
            current = heap.pop(0)
            visited.add(current)
            for neighbor in current.connections:
                neighbor = parse.named_zones[
                    neighbor["name"]
                ]
                if neighbor not in visited:
                    heap.append(neighbor)
                    neighbor.rank = (
                        current.rank
                        + graph_data.COST[
                            neighbor.meta_data["zone"]
                        ]
                    )

    def find_next_hubs(
        self,
        parse: Any,
        screen: pygame.Surface,
        display: Display,
    ) -> None:
        """
        Process one animation frame at a time, enabling
        smooth drone movement.
        """

        # Step 1: Update drones currently animating
        drones_still_moving: List["Drone"] = []
        for drone in self.moving_drones:
            # Update animation progress
            progress = min(drone.t, 1)
            target_x = (
                drone.drone_start_x
                + (
                    drone.target_coordinates[0]
                    - drone.drone_start_x
                )
                * progress
            )
            target_y = (
                drone.drone_start_y
                + (
                    drone.target_coordinates[1]
                    - drone.drone_start_y
                )
                * progress
            )

            drone.zone["coordinates"] = (
                target_x,
                target_y,
            )
            drone.t += graph_data.SPEED

            # Check if drone reached target
            if drone.t >= 1:
                drone.zone[
                    "coordinates"
                ] = drone.target_coordinates

                if drone.in_restricted == 1:
                    # Drone just arrived on connection.
                    # Must wait for next turn to enter.
                    pass
                else:
                    # Drone arrived at final destination
                    if (
                        drone.target
                        == parse.end_hub.name
                    ):
                        drone.visited.add(drone.target)

                    # Decrement link usage on arrival
                    if drone.target is not None:
                        self.decrement_link_usage(
                            drone.zone["name"],
                            drone.target,
                        )

                    drone.previous = drone.zone["name"]
                    drone.zone["name"] = drone.target
                    drone.target = None
            else:
                # Still animating
                drones_still_moving.append(drone)

        self.moving_drones = drones_still_moving

        # Step 2: Find targets for idle drones
        for drone in self.drones:
            if (
                drone not in self.moving_drones
                and drone.zone["name"]
                != parse.end_hub.name
            ):
                started_new_move = False

                # If target is None, find a new move
                if drone.target is None:
                    drone.find_next_move(parse, self)
                    if drone.target:
                        started_new_move = True

                # If target is set, execute move/wait
                if drone.target:
                    drone.drone_start_x = drone.zone[
                        "coordinates"
                    ][0]
                    drone.drone_start_y = drone.zone[
                        "coordinates"
                    ][1]

                    if drone.in_restricted == 1:
                        target_zone_coords = (
                            parse.named_zones[
                                drone.target
                            ].coordinates
                        )
                        if started_new_move:
                            # Turn 1: Move to midpoint
                            drone.target_coordinates = (
                                (
                                    drone.drone_start_x
                                    + target_zone_coords[0]
                                )
                                / 2,
                                (
                                    drone.drone_start_y
                                    + target_zone_coords[1]
                                )
                                / 2,
                            )
                        else:
                            # Turn 2: Move into restricted
                            drone.target_coordinates = (
                                target_zone_coords
                            )
                            drone.logs.append(
                                f"D{drone.index}-"
                                f"{drone.target}"
                            )
                            drone.in_restricted = 0
                    else:
                        # Normal 1-turn movement
                        drone.target_coordinates = (
                            parse.named_zones[
                                drone.target
                            ].coordinates
                        )

                    drone.t = 0
                    self.moving_drones.append(drone)

                    # Increment link usage on new move
                    if started_new_move:
                        self.increment_link_usage(
                            drone.zone["name"],
                            drone.target,
                        )

        # Step 3: Print logs once per move init
        logs_exist = False
        for drone in self.drones:
            if drone.logs:
                logs_exist = True
                print(
                    drone.logs.pop(0),
                    end=" ",
                    flush=True,
                )
        if logs_exist:
            parse.turns += 1
            print()
