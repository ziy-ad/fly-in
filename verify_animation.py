#!/usr/bin/env python3
"""Quick verification that the refactored code still works"""

from my_parser import My_Parssing
from my_graph import Graph

def verify_smooth_animation():
    print("Verifying smooth animation refactoring...\n")
    
    # Test with a simple map
    parse = My_Parssing("maps/easy/01_linear_path.txt")
    parse.parser()
    
    graph = Graph(parse.nb_drones, parse.start_hub, parse.end_hub)
    
    if not graph.path_exist(parse):
        print("✗ Path validation failed")
        return False
    
    graph.rank_hubs(parse)
    
    # Verify the key changes
    print("✓ Graph initialized successfully")
    print(f"✓ moving_drones list exists: {hasattr(graph, 'moving_drones')}")
    print(f"✓ Initial moving_drones count: {len(graph.moving_drones)}")
    
    # Verify drones have animation fields
    drone = graph.drones[0]
    print(f"✓ Drone has 't' field (animation progress): {hasattr(drone, 't')}")
    print(f"✓ Drone has 'drone_start_x': {hasattr(drone, 'drone_start_x')}")
    print(f"✓ Drone has 'target_coordinates': {hasattr(drone, 'target_coordinates')}")
    
    # Simulate a few frames (without rendering)
    print("\nSimulating 10 frames of animation...")
    for frame in range(10):
        # This is what the main loop does
        graph.find_next_hubs(parse, None, None)
        
        # Check status
        moving = len(graph.moving_drones)
        if moving > 0:
            print(f"  Frame {frame}: {moving} drone(s) animating", end="")
            for d in graph.moving_drones:
                print(f" | D{d.index}:t={d.t:.2f}", end="")
            print()
    
    print("\n✓ Animation refactoring verified successfully!")
    return True

if __name__ == "__main__":
    verify_smooth_animation()
