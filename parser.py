import re
from main import Zone
import webcolors
from typing import List

class Parssing:
    def __init__(self, file_path):
        self.file_path: str = file_path
        self.existed_coordinates: tuple(int, int) = None
        self.existed_names: set(str) = set()
        self.nb_drones: int = None
        self.zones: List[Zone] = []
        self.zones_names: dict[str, Zone] = {}

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
                            #print(extract_line.groups())
                        else:
                            line = Parssing.strip_line(i, line)
                            hub_pattern = r"(\w+)\s+(-?\d+)\s+(-?\d+)(\s+\[.*\])?\s*$"
                            extract_line = re.fullmatch(hub_pattern, line)
                            if not extract_line:
                                Parssing.log_and_exit(i, f"invalid syntax for: {org_line}")
                            self.validate_zone(i, extract_line.groups(), org_line)
                            #print(extract_line.groups())
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
        print(data)
        name = data[0]
        print(name)
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
        elif metadata is None:
            exit()
        if name in self.existed_names:
            Parssing.log_and_exit(i, f"redfining of existed hub name {line}")
        self.existed_names.add(name)
        if (x, y) in self.existed_coordinates:
            Parssing.log_and_exit(i, f"Zone with the same coordinates already exists\n{line}")
        self.existed_coordinates.add((x, y))
        #self.validate_zone_metadata(i, metadata, line)
        #self.zones_names[metadata]
        #self.zones.append(Zone(name, (x, y), metadata))


    def validate_zone_metadata(self, i: int, metadata: dict[str, str | int], line: str) -> None:
        possible_keys = {'zone', 'color', 'max_drones'}
        possible_types = {'normal', 'blocked', 'restricted', 'priority'}
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
        print(metadata)


import sys

c = Parssing(sys.argv[1])
c.parser()

#for zone in c.zones:
#    print(zone.name)
#    print(zone.coordinates)
#    print(zone.metadata)
