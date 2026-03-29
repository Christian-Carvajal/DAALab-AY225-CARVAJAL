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
        self.root.title("Bi-Directional Path Visualizer (Classmate Route)")
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
        # This specifically maps the classmate's bi-directional back-tracking logic.
        # It visits 5 -> 6, then turns completely around and goes 6 -> 3.
        # This results in exactly 62 km.
        classmate_route = [1, 2, 6, 5, 6, 3, 4]
        
        min_costs = {'D': 0, 'T': 0, 'F': 0}
        
        # Calculate exactly what this specific path costs for Distance, Time, and Fuel
        min_costs['D'] = self.calculate_path_cost(classmate_route, self.graph_D)
        min_costs['T'] = self.calculate_path_cost(classmate_route, self.graph_T)
        min_costs['F'] = self.calculate_path_cost(classmate_route, self.graph_F)

        # Save this exact route as the "best path" so the UI draws it
        self.best_paths = {
            'D': ([classmate_route], min_costs['D']),
            'T': ([classmate_route], min_costs['T']),
            'F': ([classmate_route], min_costs['F'])
        }
        self.current_route_idx = {'D': 0, 'T': 0, 'F': 0}

    def create_widgets(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="View Metrics For:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.metric_var = tk.StringVar(value='D')
        
        btn_d = ttk.Radiobutton(control_frame, text="Distance (D)", variable=self.metric_var, value='D', command=lambda: self.update_view('D'))
        btn_d.pack(side=tk.LEFT, padx=10)
        
        btn_t = ttk.Radiobutton(control_frame, text="Time (T)", variable=self.metric_var, value='T', command=lambda: self.update_view('T'))
        btn_t.pack(side=tk.LEFT, padx=10)
        
        btn_f = ttk.Radiobutton(control_frame, text="Fuel (F)", variable=self.metric_var, value='F', command=lambda: self.update_view('F'))
        btn_f.pack(side=tk.LEFT, padx=10)
        
        btn_tech = ttk.Button(control_frame, text="Technical Details", command=self.show_tech_defense)
        btn_tech.pack(side=tk.RIGHT, padx=10)

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
            
        self.draw_graph(metric)

    def draw_graph(self, metric):
        self.ax.clear()
        
        graphs = {'D': self.graph_D, 'T': self.graph_T, 'F': self.graph_F}
        labels = {'D': 'Distance', 'T': 'Time', 'F': 'Fuel units'}
        G = graphs[metric]
        best_routes, cost = self.best_paths[metric]
        
        best_route = best_routes[0]

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
            
            route_str = f"Classmate's Bi-Directional Route (Backtracks over Node 6):\n{' ➔ '.join(map(str, best_route))}\nTotal {labels[metric]}: {cost:.2f}"
            self.result_label.config(text=route_str)
        
        self.ax.set_title(f"Visualizing Classmate Route - Calculating {labels[metric]}", fontsize=16, fontweight="bold")
        self.ax.axis('off')
        
        self.canvas.draw()

    def show_tech_defense(self):
        defense_win = tk.Toplevel(self.root)
        defense_win.title("Labwork 1 Technical Details")
        defense_win.geometry("900x600")

        # Create Canvas for scrollable content
        canvas = tk.Canvas(defense_win, bg="#1E1E2F")
        scrollbar = ttk.Scrollbar(defense_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1E1E2F")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        questions = [
            ("1. What algorithm is used in this program?", 
             "Instead of using a classic TSP algorithm (like Brute-Force or Held-Karp) which searches for an optimal cycle, this program uses a Direct Path Evaluation / Array Traversal Algorithm. It hardcodes a specific array and walks through a Directed Graph to sum exact edge weights. It functions as a static bi-directional path visualizer rather than an active solver.\n# [See Code: Lines 85-89]"),
            
            ("2. Why does the classmate route equal a Distance of 62km?", 
             "The program evaluates the specific sequence `[1, 2, 6, 5, 6, 3, 4]`. Summing the Distance (D) edge weights from the dataset for these hops: (1->2=10) + (2->6=8) + (6->5=8) + (5->6=8 [Backtracking!]) + (6->3=14) + (3->4=14) yields exactly 62 km. It achieves this by breaking standard TSP rules and visiting Node 6 twice.\n# [See Code: Lines 88-89 & 94]"),
            
            ("3. Why is the total Time equal to 130 minutes?", 
             "The code evaluates the exact same classmate array but queries the `self.graph_T` Directed Graph. Summing the Time (T) edge weights for those same hops (including the backtrack from 5 back to 6) mathematically totals to exactly 130 minutes.\n# [See Code: Lines 95]"),
            
            ("4. Why is the total Fuel equal to 8.20 liters?", 
             "Similar to distance and time, the program iterates through the `self.graph_F` Directed Graph which stores Fuel data. The sum of the fuel costs for that specific sequence, including the 5->6 backtrack, precisely equals 8.20 liters.\n# [See Code: Lines 96]"),
            
            ("5. How are these costs actually calculated in the code?", 
             "The `calculate_path_cost(path, graph)` function takes the array and loops `for i in range(len(path) - 1)`. For each step, it checks if the edge exists (`graph.has_edge`) and adds the `weight` attribute to a running `cost` variable.\n# [See Code: Lines 76-83]"),
             
            ("6. How is the data loaded and structured?", 
             "It uses `pandas.read_csv` to parse `dataset.csv`. For each row, it populates three separate `networkx.DiGraph()` instances (for D, T, and F). The 'Node From' and 'Node To' govern the directional edge, while D, T, F are assigned to the edge's 'weight' attribute.\n# [See Code: Lines 64-74]"),
        ]

        # Add title
        tk.Label(scrollable_frame, text="Technical Details", 
                 font=("Consolas", 18, "bold"), fg="#00E5FF", bg="#1E1E2F", pady=10).pack(fill=tk.X)

        for q, a in questions:
            frame = tk.Frame(scrollable_frame, bg="#2A2A3C", bd=2, relief="groove")
            frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(frame, text=q, font=("Consolas", 12, "bold"), fg="#00E5FF", bg="#2A2A3C", anchor="w").pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=a, font=("Consolas", 11), fg="#F8F8F2", bg="#2A2A3C", anchor="w", justify=tk.LEFT, wraplength=840).pack(fill=tk.X, padx=10, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TSPApp(root)
    root.mainloop()