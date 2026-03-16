# Midterm Lab 2: Travelling Salesman / Shortest Path Visualizer

**Created by:** Christian Ezekiel L. Carvajal  
**Submitted for:** Midterm Lab 2 Exam

## Overview
This project is an enterprise-grade desktop application that visualizes a network of cities based on a dataset and mathematically calculates the absolute shortest path between any two locations. It evaluates routes in real-time while taking into account **Distance (km)**, **Time (mins)**, and **Fuel (Liters)** consumption.

Designed with a professional User-Centered Design (UCD) approach, the app features a sleek dark-themed dashboard built purely in Python's native 	kinter library.

## Key Features
- **Dynamic Dijkstra Algorithm Integration**: Guarantees the optimal path based on any of the three chosen metrics (Distance, Time, Fuel) utilizing Priority Queues (heapq).
- **Real-Time Reactive UI**: Gone are the days of manual "Calculate" buttons. Changing the *Origin*, *Destination*, or *Weight Target* via radio buttons immediately recalculates and visually updates the node map in real time.
- **Geographically Calibrated Node Map**: The nodes (cities arrayed around Cavite mapping) are uniquely aligned via custom x/y coordinates to mirror relative geographical reality, rather than a randomized graph.
- **Dynamic Contextual Labels**: Visual edges update seamlessly to display their respective units�showing km for distance, mins for time, and L for fuel consumption.
- **Fail-Safe Data Ingestion**: Correctly processes .csv data dynamically using absolute os.path resolutions, ensuring zero execution failures across different Windows CLI boundaries.

## Brief Report: Approach and Algorithm

### Approach & Data Structures
The application takes a User-Centered Design (UCD) approach to solving minimum-cost graph traversal problems, simulating a real-world local geography (cities in Cavite) mapping network edges based on practical travel metrics. We implemented this using pure Python standard libraries to avoid heavy dependencies:
- **Adjacency List (Dictionaries & Lists)**: The dataset is parsed using the `csv` module into a graph represented as an adjacency list (`graph[node] = [(neighbor, {distance, time, fuel}), ...]`). This allows efficient $O(1)$ neighbor lookups and is optimally space-efficient for geographic graphs.
- **Priority Queue (`heapq`)**: Essential for priority-based traversal, guaranteeing that the next node evaluated is always the one with the currently lowest cumulative cost.
- **Reactive UI (`tkinter`)**: An event-driven GUI that instantly recalculates paths and redraws Canvas objects whenever a dropdown or radio button value changes.

### Algorithm Used: Dijkstra's Algorithm
Finding the most efficient traversal across a weighted graph relies on a customized implementation of **Dijkstra's Algorithm**. 
- **Time Complexity:** Operates at **$O((V + E) \log V)$** (where $V$ is vertices and $E$ is edges) due to the use of Python's binary heap (`heapq`). This ensures lightning-fast execution capable of matching the user's real-time interface clicks.
- **State Tracking**: The priority queue stores states efficiently as `(cost, current_node, path_so_far)`. This organically traces and builds the route history without requiring a massive parent-pointer array.
- **Execution Flow**: The algorithm incrementally explores outward from the origin node. It pops the lowest-cost node, checks if it has been marked `visited`, and iterates through its neighbors. It adds the specific edge's weight (dynamically switching between Distance, Time, or Fuel based on the UI `weight_key`) to the cumulative cost and pushes it back into the heap.
- **Bonus Extrapolation Tracking**: Once the algorithm successfully locks onto the destination node, it traverses the finalized path one last time to independently tabulate and report the parallel metrics (e.g. calculating total *Time* and *Fuel* even if prioritized blindly for *Distance*).

## Code Architecture (MidtermLab2-Carvajal.py)
1. **load_graph()**: Parses dataset.csv into a bidirectional adjacency list natively, converting edge capacities to precision floats.
2. **dijkstra()**: Employs structural graph theory tracking current cost, history, and previously visited vertices.
3. **AppUI Class**: The heart of the visual dashboard. Implements event-driven programming combining 	tk.Combobox <<ComboboxSelected>> behaviors alongside Canvas geometric drawing properties.

## Installation & Setup
1. Ensure you have **Python 3.8+** installed on your system.
2. Ensure you have the provided dataset.csv in the same root directory as the script.
3. Run the application via terminal or IDE:
   `ash
   python MidtermLab2-[Lastname].py
   `

## Usage Instructions
1. **Launch the Dashboard**: The main Application Window will appear in a modern dark-themed scheme.
2. **Select Origin and Target**: Use the dropdown menus on the sidebar to choose the starting node and the destination node.
3. **Select Optimization Metric**: Click the radio buttons under "Select Optimization Metric". Choose from:
   - **Distance** (Minimizes Total Kilometers)
   - **Time** (Minimizes Minutes Traveled)
   - **Fuel** (Minimizes Liter Consumption)
4. **View Results Dashboard**: The Route Highlights immediately trace over the geometric coordinate canvas map, and the total tallies instantly calculate in the lower-left metrics box.

## Mathematical Accuracy & Data Proportions Note
If selecting *Distance*, *Time*, or *Fuel* occasionally produces visually identical routes, this is working exactly as intended. The provided dataset.csv contains naturally linear, highly proportional values. When Distance perfectly scales with Fuel and Time, finding the shortest mathematical path for one invariably discovers the shortest mathematical path for all three. The backend terminal validations confirm absolute \%$ accuracy down to the decimal.
