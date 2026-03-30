import os
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
    root.withdraw()
    messagebox.showerror(
        "Missing Requirements",
        f"A required library is missing: {e}\n\nPlease run:\npip install pandas networkx matplotlib"
    )
    sys.exit(1)

class DijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Routing Optimizer (Dijkstra Shortest Path Tree)")
        self.root.geometry("1000x800")
        
        self.graph_D = nx.DiGraph()
        self.graph_T = nx.DiGraph()
        self.graph_F = nx.DiGraph()
        self.nodes = []
        self.best_trees = {}
        
        try:
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {e}")
            self.root.destroy()
            return
            
        self.solve_dijkstra()
        self.create_widgets()
        self.draw_graph('D')
        
    def load_data(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        dataset_path = os.path.join(base_dir, 'dataset.csv')
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"dataset.csv not found at {dataset_path}")
            
        df = pd.read_csv(dataset_path)
        for _, row in df.iterrows():
            u, v = int(row['Node From']), int(row['Node To'])
            self.graph_D.add_edge(u, v, weight=float(row['D']))
            self.graph_T.add_edge(u, v, weight=float(row['T']))
            self.graph_F.add_edge(u, v, weight=float(row['F']))
            if u not in self.nodes: self.nodes.append(u)
            if v not in self.nodes: self.nodes.append(v)

    def solve_dijkstra(self):
        # Instead of a continuous TSP loop, we find the best "Origin Hub" 
        # by summing the shortest paths from the origin to ALL other nodes.
        self.best_trees = {}
        
        for metric, graph in [('D', self.graph_D), ('T', self.graph_T), ('F', self.graph_F)]:
            best_origin = None
            min_total_cost = float('inf')
            best_tree_edges = []
            
            for origin in self.nodes:
                try:
                    # length dict: {target_node: total_cost}
                    # paths dict: {target_node: [list_of_nodes_in_path]}
                    lengths, paths = nx.single_source_dijkstra(graph, origin)
                    
                    # Ensure the origin can actually reach EVERY other node
                    if len(lengths) == len(self.nodes):
                        total_sum = sum(lengths.values())
                        
                        if total_sum < min_total_cost:
                            min_total_cost = total_sum
                            best_origin = origin
                            best_lengths = lengths
                            best_paths = paths
                            
                            # Extract all the unique edges used in these shortest paths
                            edges = set()
                            for target, path in paths.items():
                                for i in range(len(path)-1):
                                    edges.add((path[i], path[i+1]))
                            best_tree_edges = list(edges)
                except nx.NetworkXNoPath:
                    continue
                    
            self.best_trees[metric] = {
                'origin': best_origin,
                'edges': best_tree_edges,
                'cost': min_total_cost,
                'lengths': best_lengths if best_origin else {},
                'paths': best_paths if best_origin else {}
            }

    def create_widgets(self):
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="Optimize Routing For:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.metric_var = tk.StringVar(value='D')
        ttk.Radiobutton(control_frame, text="Distance (D)", variable=self.metric_var, value='D', command=self.update_view).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(control_frame, text="Time (T)", variable=self.metric_var, value='T', command=self.update_view).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(control_frame, text="Fuel (F)", variable=self.metric_var, value='F', command=self.update_view).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="Technical Details", command=self.show_tech_defense).pack(side=tk.RIGHT, padx=10)

        # PanedWindow for side-by-side plot and routes
        self.main_content = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot frame
        self.plot_frame = ttk.Frame(self.main_content)
        self.main_content.add(self.plot_frame, weight=3)
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Routes frame (table)
        self.routes_frame = ttk.Frame(self.main_content, padding="5")
        self.main_content.add(self.routes_frame, weight=1)
        
        ttk.Label(self.routes_frame, text="Shortest Paths from Hub", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        self.tree = ttk.Treeview(self.routes_frame, columns=('Dest', 'Cost', 'Path'), show='headings', height=15)
        self.tree.heading('Dest', text='Dest Node')
        self.tree.heading('Cost', text='Cost')
        self.tree.heading('Path', text='Path Traversed')
        
        self.tree.column('Dest', width=80, anchor='center')
        self.tree.column('Cost', width=80, anchor='center')
        self.tree.column('Path', width=180, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True)

        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_label = ttk.Label(results_frame, text="", font=("Arial", 14, "bold"), foreground="blue", justify="center")
        self.result_label.pack(side=tk.TOP, pady=10)

    def update_view(self):
        self.draw_graph(self.metric_var.get())

    def draw_graph(self, metric):
        self.ax.clear()
        
        graphs = {'D': self.graph_D, 'T': self.graph_T, 'F': self.graph_F}
        labels = {'D': 'Distance (km)', 'T': 'Time (mins)', 'F': 'Fuel (Liters)'}
        G = graphs[metric]
        
        tree_data = self.best_trees.get(metric)
        
        pos = nx.spring_layout(G, seed=42)
        
        # Draw background edges
        nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=G.edges(), edge_color='lightgray', 
                               alpha=0.4, arrows=True, connectionstyle='arc3, rad=0.15')
        
        if tree_data and tree_data['origin'] is not None:
            best_origin = tree_data['origin']
            best_edges = tree_data['edges']
            cost = tree_data['cost']
            
            # Color the Origin Hub differently
            node_colors = ['#FFD700' if n == best_origin else '#CCE5FF' for n in G.nodes()]
            
            nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=node_colors, node_size=1000, edgecolors='black')
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=14, font_weight="bold")
            
            # Draw the thick Hub-and-Spoke tree branches
            nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=best_edges, edge_color='red', 
                                   width=3.5, arrows=True, arrowsize=30, connectionstyle='arc3, rad=0.15')
            
            # Show edge weights on the highlighted branches
            sp_edge_labels = {(u, v): f"{G[u][v]['weight']:g}" for u, v in best_edges}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=sp_edge_labels, ax=self.ax, 
                                         font_color='blue', font_weight='bold', font_size=10, 
                                         label_pos=0.35, 
                                         bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

            self.result_label.config(text=f"Optimal Hub: Node {best_origin}\nSum of all shortest paths: {cost:.2f} {labels[metric]}")
            
            # Update Table (Treeview)
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            lengths = tree_data.get('lengths', {})
            paths = tree_data.get('paths', {})
            
            unit = labels[metric].split()[0]
            
            for dest in sorted(self.nodes):
                if dest == best_origin:
                    continue
                path_str = " > ".join(map(str, paths.get(dest, [])))
                cost_val = lengths.get(dest, 0)
                self.tree.insert('', 'end', values=(dest, f"{cost_val:.2f} {unit}", path_str))
                
            # Insert a separator and total
            self.tree.insert('', 'end', values=('', '', ''))
            self.tree.insert('', 'end', values=('TOTAL', f"{cost:.2f} {unit}", ''))
            
        else:
            nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color='#CCE5FF', node_size=1000, edgecolors='black')
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=14, font_weight="bold")
            self.result_label.config(text="No valid hub found that reaches all nodes.")
            for item in self.tree.get_children():
                self.tree.delete(item)
            
        self.ax.set_title(f"Shortest Path Tree (Dijkstra) - Optimizing {labels[metric]}", fontsize=16, fontweight="bold")
        self.ax.axis('off')
        self.canvas.draw()

    def show_tech_defense(self):
        defense_win = tk.Toplevel(self.root)
        defense_win.title("Labwork 1 Technical Details")
        defense_win.geometry("900x600")

        canvas = tk.Canvas(defense_win, bg="#1E1E2F")
        scrollbar = ttk.Scrollbar(defense_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1E1E2F")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        questions = [
            ("1. What algorithm is used in this program?", 
             "This program uses Dijkstra's Algorithm (Single-Source Shortest Path). Instead of finding a continuous delivery loop (TSP), it finds the best 'Origin Hub' and calculates the absolute shortest path branches radiating out to every other individual node on the network.\n# [See Code: Lines 78-83]"),
            
            ("2. Why is Node 6 the optimal hub for Distance (62km)?", 
             "When the algorithm calculates the shortest possible path from Node 6 to every other node and adds them all together, it results in the lowest possible mathematical sum: 62 kilometers. Other nodes would require longer connecting branches.\n# [See Code: Lines 78-86]"),
            
            ("3. Why does the optimal hub change to Node 2 for Time (130 mins)?", 
             "Because Distance and Time are weighted differently in the dataset! When optimizing for Time, routing traffic through Node 2 results in faster branches. Summing the shortest time-paths from Node 2 to all other nodes perfectly equals 130 minutes.\n# [See Code: Lines 69-70 & 82]"),
            
            ("4. Why is Node 6 the optimal hub again for Fuel (7.90 Liters)?", 
             "When the graph evaluates the Fuel weights, Node 6 once again becomes the most efficient central hub. The algorithm maps out the most fuel-efficient individual routes to Nodes 1, 2, 3, 4, and 5. The total sum of gas burned across all those separate branches equals 7.90 Liters.\n# [See Code: Lines 69 & 82]"),
            
            ("5. How does the program calculate these totals?", 
             "It uses the `networkx.single_source_dijkstra` function. It iterates through every possible starting node, calculates the shortest path dictionary to all targets, and uses a `sum()` function to total the costs. It keeps the node with the lowest total sum.\n# [See Code: Lines 78-82]"),
             
            ("6. How is the data loaded and structured?", 
             "It uses `pandas.read_csv` to parse `dataset.csv`. For each row, it populates three separate `networkx.DiGraph()` instances (for D, T, and F), assigning the proper weights to the directional edges.\n# [See Code: Lines 45-60]"),
             
            ("7. How are the routes and values displayed visually for data science?", 
             "We collect the individual path dictionaries and cost values returned directly by Dijkstra's algorithm. These exact routes are traced into a Treeview table for clear mathematical breakdowns, while their specific traversal weights are overlaid directly onto the NetworkX plot edges, making it easy to digest visually.\n# [See Code: Lines 141-149 & 190-212]"),
        ]

        tk.Label(scrollable_frame, text="Technical Details", font=("Consolas", 18, "bold"), fg="#00E5FF", bg="#1E1E2F", pady=10).pack(fill=tk.X)

        for q, a in questions:
            frame = tk.Frame(scrollable_frame, bg="#2A2A3C", bd=2, relief="groove")
            frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(frame, text=q, font=("Consolas", 12, "bold"), fg="#00E5FF", bg="#2A2A3C", anchor="w").pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=a, font=("Consolas", 11), fg="#F8F8F2", bg="#2A2A3C", anchor="w", justify=tk.LEFT, wraplength=840).pack(fill=tk.X, padx=10, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()