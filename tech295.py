import networkx as nx
import asyncio
import random
import time
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import numpy as np

@dataclass
class NetworkNode:
    """Represents a node in the network with its properties."""
    name: str
    ip_address: str
    is_router: bool = False
    area_id: int = 0  # OSPF area ID

class NetworkSimulator:
    """Simulates a dynamic computer network with OSPF routing and visualization."""
    
    def __init__(self):
        """Initialize the network simulator with a structured topology."""
        self.graph = nx.Graph()
        self.nodes: Dict[str, NetworkNode] = {}
        self.latencies: Dict[Tuple[str, str], float] = {}
        self.ospf_costs: Dict[Tuple[str, str], float] = {}
        self._initialize_network()
        self._running = True
        
    def _initialize_network(self) -> None:
        """Create a structured network topology with 7 nodes (4 routers, 3 regular nodes)."""
        # Define node positions in a structured way
        node_positions = {
            'R1': (0, 2),  # Router 1
            'R2': (2, 2),  # Router 2
            'R3': (2, 0),  # Router 3
            'R4': (0, 0),  # Router 4
            'N1': (1, 3),  # Node 1
            'N2': (3, 1),  # Node 2
            'N3': (1, -1)  # Node 3
        }
        
        # Create nodes
        for node_name, (x, y) in node_positions.items():
            ip_address = f"192.168.1.{len(self.nodes)}"
            is_router = node_name.startswith('R')
            area_id = 0 if node_name in ['R1', 'N1'] else (1 if node_name in ['R2', 'N2'] else 2)
            node = NetworkNode(node_name, ip_address, is_router, area_id)
            self.nodes[node_name] = node
            self.graph.add_node(node_name, pos=(x, y))
        
        # Create connections (edges)
        connections = [
            ('R1', 'R2'), ('R2', 'R3'), ('R3', 'R4'), ('R4', 'R1'),  # Router backbone
            ('R1', 'N1'), ('R2', 'N2'), ('R3', 'N3')  # Router to node connections
        ]
        
        for u, v in connections:
            self.graph.add_edge(u, v)
            # Initialize latency between 10-50ms for better simulation
            latency = random.uniform(10, 50)
            self.latencies[(u, v)] = latency
            self.latencies[(v, u)] = latency
            # Calculate OSPF cost
            cost = int(100 / (latency / 10))
            self.ospf_costs[(u, v)] = cost
            self.ospf_costs[(v, u)] = cost
    
    async def update_latencies(self) -> None:
        """Periodically update link latencies to simulate dynamic network conditions."""
        while self._running:
            for edge in self.graph.edges():
                # Randomly adjust latency by ±10% (smaller variation for stability)
                current_latency = self.latencies[edge]
                new_latency = current_latency * random.uniform(0.9, 1.1)
                self.latencies[edge] = new_latency
                self.latencies[(edge[1], edge[0])] = new_latency
                # Update OSPF costs
                cost = int(100 / (new_latency / 10))
                self.ospf_costs[edge] = cost
                self.ospf_costs[(edge[1], edge[0])] = cost
            await asyncio.sleep(5)  # Update every 5 seconds
    
    def get_ospf_path(self, source: str, destination: str) -> List[str]:
        """Calculate the OSPF shortest path based on link costs."""
        try:
            # Create a weighted graph for OSPF path calculation
            ospf_graph = nx.Graph()
            for edge in self.graph.edges():
                ospf_graph.add_edge(edge[0], edge[1], weight=self.ospf_costs[edge])
            
            # Calculate shortest path using Dijkstra's algorithm (OSPF)
            path = nx.shortest_path(ospf_graph, source, destination, weight='weight')
            return path
        except nx.NetworkXNoPath:
            raise ValueError(f"No OSPF path found between {source} and {destination}")
    
    async def ping(self, source: str, destination: str, count: int = 4) -> Tuple[List[float], List[str]]:
        """Simulate ICMP ping between two nodes using OSPF path."""
        if source not in self.nodes or destination not in self.nodes:
            raise ValueError("Source or destination node not found")
        
        rtts = []
        path = self.get_ospf_path(source, destination)
        
        for _ in range(count):
            try:
                # Simulate packet loss (1% chance)
                if random.random() < 0.01:
                    raise TimeoutError("Request timed out")
                
                # Calculate total latency along OSPF path
                total_latency = sum(
                    self.latencies[(path[i], path[i+1])] 
                    for i in range(len(path)-1)
                )
                
                # Add some jitter (±2ms)
                rtt = total_latency + random.uniform(-2, 2)
                rtts.append(max(0, rtt))  # Ensure non-negative RTT
                
                # Simulate network processing time
                await asyncio.sleep(0.1)
                
            except TimeoutError:
                rtts.append(None)
                print(f"Request timed out")
            except Exception as e:
                print(f"Error during ping: {e}")
                rtts.append(None)
        
        return rtts, path
    
    async def traceroute(self, source: str, destination: str) -> Tuple[List[Tuple[str, float]], List[str]]:
        """Simulate traceroute between two nodes using OSPF path."""
        if source not in self.nodes or destination not in self.nodes:
            raise ValueError("Source or destination node not found")
        
        try:
            path = self.get_ospf_path(source, destination)
            hops = []
            
            for i in range(len(path)-1):
                current = path[i]
                next_hop = path[i+1]
                latency = self.latencies[(current, next_hop)]
                hops.append((current, latency))
                # Simulate network processing time
                await asyncio.sleep(0.1)
            
            # Add final hop
            hops.append((destination, 0))
            return hops, path
            
        except Exception as e:
            print(f"Error during traceroute: {e}")
            return [], []

    def visualize_network(self, highlight_path: List[str] = None) -> None:
        """Visualize the network topology with OSPF areas and current latencies."""
        plt.figure(figsize=(12, 8))
        
        # Get node positions from the graph
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Define colors for different OSPF areas
        area_colors = {
            0: 'lightblue',
            1: 'lightgreen',
            2: 'lightcoral'
        }
        
        # Draw nodes by OSPF area
        for area_id in area_colors:
            area_nodes = [node for node in self.nodes 
                         if self.nodes[node].area_id == area_id]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=area_nodes,
                                 node_color=area_colors[area_id],
                                 node_size=1000,
                                 label=f'Area {area_id}')
        
        # Draw routers with a different style
        router_nodes = [node for node in self.nodes if self.nodes[node].is_router]
        nx.draw_networkx_nodes(self.graph, pos, nodelist=router_nodes,
                             node_color='red', node_size=1200,
                             node_shape='s', label='Routers')
        
        # Draw edges with latency and OSPF cost labels
        edge_labels = {(u, v): f"{self.latencies[(u, v)]:.1f}ms\nCost: {self.ospf_costs[(u, v)]}" 
                      for u, v in self.graph.edges()}
        
        # Draw all edges
        nx.draw_networkx_edges(self.graph, pos, width=2)
        
        # If a path is provided, highlight it
        if highlight_path:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                         for i in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges,
                                 edge_color='red', width=4)
        
        # Add labels
        nx.draw_networkx_labels(self.graph, pos, font_size=12, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                   font_size=8)
        
        plt.title("Network Topology with OSPF Areas and Link Metrics", pad=20)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def stop(self) -> None:
        """Stop the network simulator."""
        self._running = False

async def main():
    """Main function to demonstrate network simulation with OSPF."""
    # Create network simulator
    network = NetworkSimulator()
    
    # Start latency updates in background
    asyncio.create_task(network.update_latencies())
    
    try:
        # Visualize initial network
        print("\nVisualizing initial network topology...")
        network.visualize_network()
        
        # Get user input for source and destination
        print("\nAvailable nodes:")
        print("Routers: R1, R2, R3, R4")
        print("Nodes: N1, N2, N3")
        print("\nAreas:")
        print("Area 0: R1, N1")
        print("Area 1: R2, N2")
        print("Area 2: R3, R4, N3")
        
        source = input("\nEnter source node (e.g., R1): ").upper()
        destination = input("Enter destination node (e.g., N3): ").upper()
        
        if source not in network.nodes or destination not in network.nodes:
            print("Invalid node names. Please try again.")
            return
        
        print(f"\nPinging {destination} from {source}...")
        rtts, path = await network.ping(source, destination)
        for i, rtt in enumerate(rtts, 1):
            if rtt is not None:
                print(f"Reply from {destination}: time={rtt:.2f}ms")
            else:
                print(f"Request timed out")
        
        print(f"\nTraceroute to {destination}...")
        hops, path = await network.traceroute(source, destination)
        print("\nHop\tNode\t\tLatency\t\tArea")
        print("-" * 50)
        for i, (hop, latency) in enumerate(hops, 1):
            area_id = network.nodes[hop].area_id
            print(f"{i}\t{hop}\t\t{latency:.2f}ms\t\tArea {area_id}")
        
        # Visualize network with highlighted OSPF path
        print("\nVisualizing network with highlighted OSPF path...")
        network.visualize_network(highlight_path=path)
            
    except KeyboardInterrupt:
        print("\nStopping network simulation...")
    finally:
        network.stop()

if __name__ == "__main__":
    asyncio.run(main())
