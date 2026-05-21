import re
from main import Zone
import webcolors
from typing import List

class Parssing:
    def __init__(self, file_path):
        self.file_path: str = file_path
        self.existed_coordinates: tuple(int, int) = set()
        self.existed_names: set(str) = set()
        self.nb_drones: int = None
        self.zones: List[Zone] = []
        self.named_zones: dict[str, Zone] = {}

    def parser(self):
        zones_metadata = {"zone", "color", "max_drones"}
        try:
            with open(self.file_path) as file:
                i = 0
                for line in file:
                    i += 1
                    org_line = line
                    line = line.strip()
                    if line == "" or line.startswith("#"):
                        continue
                    line = line.split('#', 1)[0].strip()
                    if line.lower().startswith("nb_drones") and self.nb_drones == None:
                        n_line = re.findall(r'\w+:\s+?-?\d+\s?', line.lower())
                        if not n_line or n_line[0] != line:
                            raise ValueError(f"invalid format: {org_line}")
                        try:
                            self.nb_drones = int(n_line[0].split(':')[1])
                            if self.nb_drones <= 0:
                                raise ValueError("number should be positive")
                        except Exception as e:
                            Parssing.log_and_exit(i, e)
                    elif not line.lower().startswith("nb_drones") and self.nb_drones == None:
                        raise ValueError("first line must be: nb_drones: n")
                    else:
                        if line.startswith("connection:"):
                            line = Parssing.strip_line(i, line)
                            connection_pattern = r"(\w+)-(\w+)(\s+\[.*\])?\s*$"
                            extract_line = re.fullmatch(connection_pattern, line)
                            if not extract_line:
                                Parssing.log_and_exit(i, f"invalid syntax for: {org_line}")
                            self.validate_connection(i, extract_line.groups(), org_line)
                        else:
                            line = Parssing.strip_line(i, line)
                            hub_pattern = r"(\w+)\s+(-?\d+)\s+(-?\d+)(\s+\[.*\])?\s*$"
                            extract_line = re.fullmatch(hub_pattern, line)
                            if not extract_line:
                                Parssing.log_and_exit(i, f"invalid syntax for: {org_line}")
                            self.validate_zone(i, extract_line.groups(), org_line)
        except Exception as e:
            Parssing.log_and_exit(0, e)

    @staticmethod
    def log_and_exit(i: int, msg: str) -> None:
        if i == 0:
            print(msg)
        else:
            print(f"Error at line ({i}): {msg}")
        exit(0)

    @staticmethod
    def strip_line(i: int, line: str) -> str:
        if line.startswith("start_hub:"):
            return line.removeprefix('start_hub:').strip()
        elif line.startswith("hub:"):
            return line.removeprefix('hub:').strip()
        elif line.startswith("end_hub:"):
            return line.removeprefix('end_hub:').strip()
        elif line.startswith("connection:"):
            return line.removeprefix('connection:').strip()
        else:
            Parssing.log_and_exit(i, f"invalid syntax\n {line}")


    def validate_zone(self, i: int, data: tuple, line: str) -> Zone:
        name = data[0]
        try:
            x = int(data[1])
            y  = int(data[2])
        except Exception as e:
            Parssing.log_and_exit(i, e)
        metadata = data[3]
        if metadata:
            pattern = r'''
                    ^\s*
                    [A-Za-z_]+\s*=\s*[A-Za-z0-9_]+
                    (?:\s+[A-Za-z_]+\s*=\s*[A-Za-z0-9_]+)*
                    \s*$
                    '''
            metadata = metadata.strip('[] ')
            if not re.fullmatch(pattern, metadata, re.VERBOSE):
                Parssing.log_and_exit(i, f"invalid metadata syntax: {line}")
            metadata = dict(re.findall(r'([A-Za-z_]+)\s*=\s*([A-Za-z0-9_]+)', metadata))
        if name in self.existed_names:
            Parssing.log_and_exit(i, f"redfining of existed hub name {line}")
        self.existed_names.add(name)
        if (x, y) in self.existed_coordinates:
            Parssing.log_and_exit(i, f"Zone with the same coordinates already exists\n{line}")
        self.existed_coordinates.add((x, y))
        metadata = self.validate_zone_metadata(i, metadata, line)
        zone = Zone(name, (x, y), metadata)
        self.named_zones[name] = zone
        self.zones.append(zone)


    def validate_zone_metadata(self, i: int, metadata: dict[str, str | int], line: str) -> dict[str, str | int]:
        possible_keys = {'zone', 'color', 'max_drones'}
        possible_types = {'normal', 'blocked', 'restricted', 'priority'}

        if not metadata:
            return {"zone": "normal", "color": None, "max_drones": 1}

        for key, value in metadata.items():
            key = key.lower()
            if key not in possible_keys:
                log_and_exit(i, f"{line}\ninvalid metadata possible keys: {possible_keys}")
            elif key == "zone" and value.lower() not in possible_keys:
                log_and_exit(i, f"{line}\ninvalid zone_type possible keys: {possible_types}")
            elif key == "color":
                try:
                    metadata['color'] = tuple(webcolors.name_to_rgb(value))
                except Exception:
                    Parssing.log_and_exit(i, f"invalid color in metadata {line}")
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except Exception as e:
                    Parssing.log_and_exit(i, f"{line}\n{e}")
                if max_drones > self.nb_drones:
                    Parssing.log_and_exit(1, f"max_drones should be under {self.nb_drones}")
                else:
                    metadata['max_drones'] = max_drones
        if "zone" not in metadata.keys():
            metadata['zone'] = 'normal'
        if "color" not in metadata.keys():
            metadata['color'] = None
        if "max_drones" not in metadata.keys():
            metadata['max_drones'] = 1
        return metadata


    def validate_connection(self, i: int, data: tuple, line: str):
        zone1 = data[0]
        zone2 = data[1]
        max_link = 1

        if zone1 not in self.existed_names or zone2 not in self.existed_names:
            Parssing.log_and_exit(i, f"missing zone for connection:\n{line}")

        zone1_instance = self.named_zones[zone1]
        zone2_instance = self.named_zones[zone2]

        if Parssing.zone_name_exist(zone1, zone2_instance) or Parssing.zone_name_exist(zone2, zone1_instance):
            Parssing.log_and_exit(i, f"duplicated connection: {line}")

        if data[2]:
            metadata = data[2]
            pattern = r'^\s*(max_link_capacity)\s*=\s*(\d+)\s*$'
            metadata = data[2].strip('[] ')
            metadata = re.fullmatch(pattern, metadata)
            if not metadata:
                Parssing.log_and_exit(i, f"{line}\ninvalid metadata syntax, usage: [max_link_capacity = n]")
            metadata = metadata.groups()
            if int(metadata[1]) > self.nb_drones:
                Parssing.log_and_exit(i, f"max_link_capacity should be less or equal to nb_drones:{self.nb_drones}")
            max_link = int(metadata[1])

        zone1_instance.connections.append({'name': zone2, 'max_link_capacity': max_link})
        zone2_instance.connections.append({'name': zone1, 'max_link_capacity': max_link})

    @staticmethod
    def zone_name_exist(name: str, zone: Zone) -> bool:
        if not zone.connections:
            return False
        name_connections = {connection['name'] for connection in zone.connections}
        if name in name_connections:
            return True
        return False


import sys

c = Parssing(sys.argv[1])
c.parser()

for zone in c.zones:
    print(zone.name)
    print(zone.coordinates)
    print(zone.meta_data)
    print(zone.connections)
