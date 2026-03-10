import os
import itertools

try:
    import pandas as pd
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    import sys
    
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showerror(
        "Missing Requirements",
        f"A required library is missing: {e}\n\n"
        "Please run the following command in your terminal:\n"
        "pip install pandas networkx matplotlib"
    )
    sys.exit(1)

class TSPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TSP Resource Optimizer (Distance, Time, Fuel)")
        self.root.geometry("1000x800")
        
        # Data storage
        self.graph_D = nx.DiGraph()
        self.graph_T = nx.DiGraph()
        self.graph_F = nx.DiGraph()
        self.nodes = []
        self.best_paths = {}
        
        try:
            self.load_data()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error Reading Dataset", f"An error occurred: {e}")
            self.root.destroy()
            return
            
        self.solve_tsp()
        self.create_widgets()
        self.draw_graph('D') # Default view
        
    def load_data(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        dataset_path = os.path.join(base_dir, 'dataset.csv')
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at: {dataset_path}")
            
        df = pd.read_csv(dataset_path)
        
        for _, row in df.iterrows():
            u = int(row['Node From'])
            v = int(row['Node To'])
            d = float(row['D'])
            t = float(row['T'])
            f = float(row['F'])
            
            self.graph_D.add_edge(u, v, weight=d)
            self.graph_T.add_edge(u, v, weight=t)
            self.graph_F.add_edge(u, v, weight=f)
            
            if u not in self.nodes: self.nodes.append(u)
            if v not in self.nodes: self.nodes.append(v)
            
    def calculate_path_cost(self, path, graph):
        cost = 0
        for i in range(len(path) - 1):
            if graph.has_edge(path[i], path[i+1]):
                cost += graph[path[i]][path[i+1]]['weight']
            else:
                return float('inf') # Invalid path
        return cost

    def solve_tsp(self):
        # We assume TSP requires returning to the start node.
        # So Hamilton cycle: Start -> ... -> Start
        # If not fully connected, some permutations will result in infinity.
        
        min_costs = {'D': float('inf'), 'T': float('inf'), 'F': float('inf')}
        best_routes = {'D': [], 'T': [], 'F': []}
        
        start_node = self.nodes[0]
        nodes_to_visit = self.nodes[1:]
        
        # Testing all permutations (brute force, acceptable for small node count)
        for perm in itertools.permutations(nodes_to_visit):
            route = [start_node] + list(perm) + [start_node]
            
            for metric, graph in [('D', self.graph_D), ('T', self.graph_T), ('F', self.graph_F)]:
                cost = self.calculate_path_cost(route, graph)
                if cost < min_costs[metric] - 1e-9:
                    min_costs[metric] = cost
                    best_routes[metric] = [route]
                elif abs(cost - min_costs[metric]) < 1e-9:
                    if route not in best_routes[metric]:
                        best_routes[metric].append(route)
                        
        # Filter combinations to remove purely reversed paths (e.g. 1-2-3-1 vs 1-3-2-1)
        # So Distance & Fuel have 1 answer, Time has exactly 2 distinct answers
        for metric in ['D', 'T', 'F']:
            unique_paths = []
            seen_internals = set()
            for p in best_routes[metric]:
                internal = tuple(p[1:-1])
                internal_rev = tuple(reversed(internal))
                if internal not in seen_internals and internal_rev not in seen_internals:
                    unique_paths.append(p)
                    seen_internals.add(internal)
                    seen_internals.add(internal_rev)
            best_routes[metric] = unique_paths
                
        self.best_paths = {
            'D': (best_routes['D'], min_costs['D']),
            'T': (best_routes['T'], min_costs['T']),
            'F': (best_routes['F'], min_costs['F'])
        }
        self.current_route_idx = {'D': 0, 'T': 0, 'F': 0}

    def create_widgets(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="Optimize by:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.metric_var = tk.StringVar(value='D')
        
        btn_d = ttk.Radiobutton(control_frame, text="Distance (D)", variable=self.metric_var, value='D', command=lambda: self.update_view('D'))
        btn_d.pack(side=tk.LEFT, padx=10)
        
        btn_t = ttk.Radiobutton(control_frame, text="Time (T)", variable=self.metric_var, value='T', command=lambda: self.update_view('T'))
        btn_t.pack(side=tk.LEFT, padx=10)
        
        btn_f = ttk.Radiobutton(control_frame, text="Fuel (F)", variable=self.metric_var, value='F', command=lambda: self.update_view('F'))
        btn_f.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(control_frame, text="Next Route", command=self.next_route)
        self.next_btn.pack(side=tk.LEFT, padx=20)

        # Plot Frame
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Results Panel at the bottom
        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_label = ttk.Label(results_frame, text="", font=("Arial", 14, "bold"), foreground="blue", justify="center")
        self.result_label.pack(side=tk.TOP, pady=10)

    def update_view(self, metric=None):
        if metric is None:
            metric = self.metric_var.get()
            
        routes, cost = self.best_paths[metric]
        n_routes = len(routes)
        idx = self.current_route_idx[metric]
        
        if n_routes > 1:
            self.next_btn.config(state=tk.NORMAL, text=f"Next Optimal Route ({idx+1}/{n_routes})")
        else:
            self.next_btn.config(state=tk.DISABLED, text=f"Route (1/1)")
            
        self.draw_graph(metric)

    def next_route(self):
        metric = self.metric_var.get()
        routes, _ = self.best_paths[metric]
        if len(routes) > 1:
            self.current_route_idx[metric] = (self.current_route_idx[metric] + 1) % len(routes)
            self.update_view(metric)

    def draw_graph(self, metric):
        self.ax.clear()
        
        graphs = {'D': self.graph_D, 'T': self.graph_T, 'F': self.graph_F}
        labels = {'D': 'Distance', 'T': 'Time', 'F': 'Fuel units'}
        G = graphs[metric]
        best_routes, cost = self.best_paths[metric]
        
        if best_routes:
            best_route = best_routes[self.current_route_idx[metric]]
        else:
            best_route = None

        # Positions for all nodes
        pos = nx.spring_layout(G, seed=42)
        
        # Draw all nodes
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color='#CCE5FF', node_size=1000, 
                               edgecolors='black', linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=14, font_weight="bold")
        
        # Draw background edges with fading format and curvature to avoid overlapping
        all_edges = G.edges()
        nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=all_edges, edge_color='lightgray', 
                               alpha=0.4, arrows=True, connectionstyle='arc3, rad=0.15', 
                               arrowsize=12, width=1.0)
        
        # Highlight best path
        if best_route:
            # Create pairs of connecting nodes for the optimal path
            path_edges = [(best_route[i], best_route[i+1]) for i in range(len(best_route)-1)]
            
            # Draw prominent glowing arrows for the optimized path
            nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=path_edges, edge_color='red', 
                                   width=3.5, arrows=True, arrowsize=30, 
                                   connectionstyle='arc3, rad=0.15', min_target_margin=15)
            
            idx = self.current_route_idx[metric]
            total_r = len(best_routes)
            if total_r > 1:
                route_str = f"{total_r} Optimal Routes Found!\nShowing Option {idx+1}/{total_r}:  {' ➔ '.join(map(str, best_route))}\nTotal {labels[metric]}: {cost:.2f}"
                self.result_label.config(text=route_str)
            else:
                self.result_label.config(text=f"Optimal Route:\n{' ➔ '.join(map(str, best_route))}\nTotal {labels[metric]}: {cost:.2f}")
        else:
            self.result_label.config(text=f"No complete cycle found for {labels[metric]}.")
            
        self.ax.set_title(f"TSP Visualization - Optimizing {labels[metric]}", fontsize=16, fontweight="bold")
        self.ax.axis('off')
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = TSPApp(root)
    root.mainloop()
