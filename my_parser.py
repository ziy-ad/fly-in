import re
from my_graph import Zone
import webcolors
from typing import List, Tuple, Set
from graph_data import COLORS

class My_Parssing:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.existed_coordinates: Tuple[int, int] = set()
        self.existed_names: Set[str] = set()
        self.nb_drones: int = None
        self.zones: List[Zone] = []
        self.named_zones: dict[str, Zone] = {}
        self.start_hub = None
        self.end_hub = None

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
                            My_Parssing.log_and_exit(i, e)
                    elif not line.lower().startswith("nb_drones") and self.nb_drones == None:
                        raise ValueError("first line must be: nb_drones: n")
                    else:
                        if line.startswith("connection:"):
                            ltype, line = My_Parssing.strip_line(i, line)
                            connection_pattern = r"(\w+)-(\w+)(\s+\[.*\])?\s*$"
                            extract_line = re.fullmatch(connection_pattern, line)
                            if not extract_line:
                                My_Parssing.log_and_exit(i, f"invalid syntax for: {org_line}")
                            self.validate_connection(i, extract_line.groups(), org_line)
                        else:
                            ltype, line = My_Parssing.strip_line(i, line)
                            hub_pattern = r"(\w+)\s+(-?\d+)\s+(-?\d+)(\s+\[.*\])?\s*$"
                            extract_line = re.fullmatch(hub_pattern, line)
                            if not extract_line:
                                My_Parssing.log_and_exit(i, f"invalid syntax for: {org_line}")
                            temp_zone = self.validate_zone(i, extract_line.groups(), org_line)
                            if ltype == "start_hub" and self.start_hub:
                                My_Parssing.log_and_exit(i, f"duplicated 'start_hub': {org_line}")
                            elif ltype == "start_hub" and self.start_hub is None:
                                self.start_hub = temp_zone
                            
                            if ltype == "start_hub" or ltype == "end_hub":
                                if temp_zone.meta_data['zone'] == "blocked":
                                    My_Parssing.log_and_exit(i, f"{ltype} can't be blocked zone")

                            if ltype == "end_hub" and self.end_hub:
                                My_Parssing.log_and_exit(i, f"duplicated 'end_hub': {org_line}")
                            elif ltype == "end_hub" and self.end_hub is None:
                                self.end_hub = temp_zone
                if self.start_hub is None:
                    My_Parssing.log_and_exit(0, f"missing start_hub")
                elif self.end_hub is None:
                    My_Parssing.log_and_exit(0, f"missing end_hub")
        except Exception as e:
            My_Parssing.log_and_exit(0, e)

    @staticmethod
    def log_and_exit(i: int, msg: str) -> None:
        if i == 0:
            print(msg)
        else:
            print(f"Error at line ({i}): {msg}")
        exit(0)

    @staticmethod
    def strip_line(i: int, line: str):
        if line.startswith("start_hub:"):
            return ('start_hub', line.removeprefix('start_hub:').strip())
        elif line.startswith("hub:"):
            return ('hub', line.removeprefix('hub:').strip())
        elif line.startswith("end_hub:"):
            return ('end_hub', line.removeprefix('end_hub:').strip())
        elif line.startswith("connection:"):
            return ('connection', line.removeprefix('connection:').strip())
        else:
            My_Parssing.log_and_exit(i, f"invalid syntax\n {line}")


    def validate_zone(self, i: int, data: tuple, line: str) -> Zone:
        name = data[0]
        try:
            x = int(data[1])
            y  = int(data[2])
        except Exception as e:
            My_Parssing.log_and_exit(i, e)
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
                My_Parssing.log_and_exit(i, f"invalid metadata syntax: {line}")
            metadata = dict(re.findall(r'([A-Za-z_]+)\s*=\s*([A-Za-z0-9_]+)', metadata))
        if name in self.existed_names:
            My_Parssing.log_and_exit(i, f"redfining of existed hub name {line}")
        self.existed_names.add(name)
        if (x, y) in self.existed_coordinates:
            My_Parssing.log_and_exit(i, f"Zone with the same coordinates already exists\n{line}")
        self.existed_coordinates.add((x, y))
        metadata = self.validate_zone_metadata(i, metadata, line)
        zone = Zone(name, (x, y), metadata)
        self.named_zones[name] = zone
        self.zones.append(zone)
        return zone


    def validate_zone_metadata(self, i: int, metadata: dict[str, str | int], line: str) -> dict[str, str | int]:
        possible_keys = {'zone', 'color', 'max_drones'}
        possible_types = {'normal', 'blocked', 'restricted', 'priority'}

        if not metadata:
            return {"zone": "normal", "color": None, "max_drones": 1}

        for key, value in metadata.items():
            key = key.lower()
            if key not in possible_keys:
                My_Parssing.log_and_exit(i, f"{line}\ninvalid metadata possible keys: {possible_keys}")
            elif key == "zone" and value.lower() not in possible_types:
                My_Parssing.log_and_exit(i, f"{line}\ninvalid zone_type possible keys: {possible_types}")
            elif key == "color":
                try:
                    metadata['color'] = tuple(webcolors.name_to_rgb(value))
                except Exception:
                    try:
                        metadata['color'] = COLORS[value.lower()]
                    except KeyError:
                        My_Parssing.log_and_exit(i, f"invalid color in metadata {line}")
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except Exception as e:
                    My_Parssing.log_and_exit(i, f"{line}\n{e}")
                metadata['max_drones'] = max_drones
        if "zone" not in metadata.keys():
            metadata['zone'] = 'normal'
        if "color" not in metadata.keys():
            metadata['color'] = (255, 255, 255)
        if "max_drones" not in metadata.keys():
            metadata['max_drones'] = 1
        return metadata


    def validate_connection(self, i: int, data: tuple, line: str):
        zone1 = data[0]
        zone2 = data[1]
        max_link = 1

        if zone1 not in self.existed_names or zone2 not in self.existed_names:
            My_Parssing.log_and_exit(i, f"missing zone for connection:\n{line}")

        zone1_instance = self.named_zones[zone1]
        zone2_instance = self.named_zones[zone2]

        if My_Parssing.zone_name_exist(zone1, zone2_instance) or My_Parssing.zone_name_exist(zone2, zone1_instance):
            My_Parssing.log_and_exit(i, f"duplicated connection: {line}")

        if data[2]:
            metadata = data[2]
            pattern = r'^\s*(max_link_capacity)\s*=\s*(\d+)\s*$'
            metadata = data[2].strip('[] ')
            metadata = re.fullmatch(pattern, metadata)
            if not metadata:
                My_Parssing.log_and_exit(i, f"{line}\ninvalid metadata syntax, usage: [max_link_capacity = n]")
            metadata = metadata.groups()
            if int(metadata[1]) > self.nb_drones:
                My_Parssing.log_and_exit(i, f"max_link_capacity should be less or equal to nb_drones:{self.nb_drones}")
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
