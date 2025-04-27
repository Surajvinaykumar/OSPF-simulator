# Network Simulator with OSPF Routing

A Python-based simulation tool for modeling dynamic computer networks with OSPF routing protocol visualization.

## Overview

This simulation demonstrates how routers and nodes communicate across a network using the OSPF (Open Shortest Path First) protocol. It features real-time visualization of network topology, dynamic link conditions, and common network diagnostic tools.

## Features

- **Interactive Network Visualization**: Color-coded display of network topology with OSPF areas
- **Dynamic Link Conditions**: Realistic simulation of changing network latencies
- **OSPF Routing**: Path calculation based on dynamic cost metrics
- **Network Diagnostics**:
  - Ping with realistic RTT and occasional packet loss
  - Traceroute with hop-by-hop analysis
- **Multi-Area OSPF**: Simulation of different OSPF routing areas

## Requirements

- Python 3.7+
- Dependencies:
  - networkx
  - matplotlib
  - numpy
  - asyncio (standard library)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/network-simulator.git
cd network-simulator

# Install dependencies
pip install networkx matplotlib numpy
```

## Usage

Run the simulator:

```bash
python network_simulator.py
```

Follow the interactive prompts:
1. View the initial network topology visualization
2. Select source and destination nodes when prompted
3. Observe ping and traceroute results
4. View the updated network visualization with highlighted path

## Example Session

```
Visualizing initial network topology...

Available nodes:
Routers: R1, R2, R3, R4
Nodes: N1, N2, N3

Areas:
Area 0: R1, N1
Area 1: R2, N2
Area 2: R3, R4, N3

Enter source node (e.g., R1): R1
Enter destination node (e.g., N3): N3

Pinging N3 from R1...
Reply from N3: time=135.27ms
Reply from N3: time=138.45ms
Reply from N3: time=134.93ms
Reply from N3: time=136.54ms

Traceroute to N3...

Hop     Node            Latency         Area
--------------------------------------------------
1       R1              40.25ms         Area 0
2       R4              35.29ms         Area 2
3       R3              30.45ms         Area 2
4       N3              0.00ms          Area 2

Visualizing network with highlighted OSPF path...
```

## Network Structure

The default topology consists of:
- **Routers**: 4 interconnected routers (R1-R4)
- **Nodes**: 3 end nodes (N1-N3)
- **Areas**: 3 OSPF areas demonstrating area-based routing
- **Links**: Dynamically changing connection latencies
## graph visualisation
<img width="733" alt="Screenshot 2025-04-26 at 6 06 44 PM" src="https://github.com/user-attachments/assets/273df31f-949b-43e9-a660-c80551441478" />


## Extending the Project

Possible extensions:
- Add more complex network topologies
- Implement additional routing protocols (BGP, RIP)
- Add network congestion simulation
- Simulate device failures and recovery scenarios
- Implement packet-level simulation

## Troubleshooting

If you encounter visualization issues:
- Ensure matplotlib is correctly installed
- Try running in a different terminal/environment
- Check for Python version compatibility

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
