import csv
import heapq
import math
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────

def load_graph(filepath):
    graph = {}   # adjacency list: node -> list of (neighbor, attrs)
    nodes = set()

    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frm  = row['From Node'].strip()
            to   = row['To Node'].strip()
            dist = float(row['Distance (km)'])
            time = float(row['Time (mins)'])
            fuel = float(row['Fuel (Liters)'])

            nodes.add(frm)
            nodes.add(to)

            graph.setdefault(frm, []).append((to,   {'distance': dist, 'time': time, 'fuel': fuel}))
            graph.setdefault(to,  []).append((frm,  {'distance': dist, 'time': time, 'fuel': fuel}))

    return graph, sorted(nodes)


# ─────────────────────────────────────────
#  DIJKSTRA
# ─────────────────────────────────────────

def dijkstra(graph, start, end, weight_key):
    """
    Returns (cost, path, totals_dict) where totals_dict has distance/time/fuel
    for the found path regardless of which weight was optimised.
    """
    # priority queue: (cost, node, path_so_far)
    pq = [(0, start, [start])]
    visited = {}

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited[node] = (cost, path)

        if node == end:
            # compute full totals along the path
            totals = {'distance': 0, 'time': 0, 'fuel': 0}
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                for (nb, attrs) in graph.get(a, []):
                    if nb == b:
                        totals['distance'] += attrs['distance']
                        totals['time']     += attrs['time']
                        totals['fuel']     += attrs['fuel']
                        break
            return cost, path, totals

        for (nb, attrs) in graph.get(node, []):
            if nb not in visited:
                new_cost = cost + attrs[weight_key]
                heapq.heappush(pq, (new_cost, nb, path + [nb]))

    return None, [], {}   # no path found


# ─────────────────────────────────────────
#  NODE MAP (Canvas-based)
# ─────────────────────────────────────────

NODE_POSITIONS = {
    'NOVELETA': (0.15, 0.25),
    'KAWIT':    (0.48, 0.08),
    'BACOOR':   (0.80, 0.18),
    'IMUS':     (0.85, 0.40),
    'GENTRI':   (0.20, 0.55),
    'DASMA':    (0.65, 0.65),
    'INDANG':   (0.25, 0.85),
    'SILANG':   (0.75, 0.88),
}

# ── Color Palette ──
BG_MAIN        = '#1E1E2F'
BG_SIDEBAR     = '#252538'
BG_CARD        = '#2D2D44'
FG_PRIMARY     = '#FFFFFF'
FG_SECONDARY   = '#A2A2B5'
ACCENT_PRIMARY = '#00E5FF' # Cyan
ACCENT_HOVER   = '#00B3CC'
BTN_RESET_BG   = '#3E3E5C'
BTN_RESET_HOV  = '#505073'
EDGE_COLOR     = '#424263'
EDGE_TEXT      = '#8B8BA7'
NODE_FILL      = '#252538'
NODE_OUTLINE   = '#424263'
HL_EDGE        = '#00E5FF'
HL_NODE        = '#00E5FF'

CANVAS_W       = 800
CANVAS_H       = 650
RADIUS         = 24


def draw_map(canvas, graph, nodes, highlight_path=None, active_metric='distance'):
    canvas.delete('all')
    W, H = CANVAS_W, CANVAS_H

    # Subtle dotted background grid
    for x in range(0, W, 50):
        canvas.create_line(x, 0, x, H, fill='#232336', width=1, dash=(2, 4))
    for y in range(0, H, 50):
        canvas.create_line(0, y, W, y, fill='#232336', width=1, dash=(2, 4))

    def pos(name):
        px, py = NODE_POSITIONS.get(name, (0.5, 0.5))
        return int(px * W), int(py * H)

    drawn_edges = set()

    # Collect highlighted edges
    hl_edges = set()
    if highlight_path and len(highlight_path) > 1:
        for i in range(len(highlight_path) - 1):
            a, b = highlight_path[i], highlight_path[i + 1]
            hl_edges.add((min(a, b), max(a, b)))

    # Pass 1: Draw ALL Lines first (so they sit below text/nodes)
    drawn_edges = set()
    for node in graph:
        for (nb, attrs) in graph[node]:
            key = (min(node, nb), max(node, nb))
            if key in drawn_edges:
                continue
            drawn_edges.add(key)

            x1, y1 = pos(node)
            x2, y2 = pos(nb)
            is_hl  = key in hl_edges
            color  = HL_EDGE if is_hl else EDGE_COLOR
            width  = 3 if is_hl else 1.5

            if is_hl:
                canvas.create_line(x1, y1, x2, y2, fill='#005B66', width=6, smooth=True, capstyle=tk.ROUND)
            canvas.create_line(x1, y1, x2, y2, fill=color, width=width, smooth=True, capstyle=tk.ROUND)

    # Pass 2: Draw Edge Labels (so they sit ON TOP of lines)
    drawn_labels = set()
    for node in graph:
        for (nb, attrs) in graph[node]:
            key = (min(node, nb), max(node, nb))
            if key in drawn_labels:
                continue
            drawn_labels.add(key)
            
            x1, y1 = pos(node)
            x2, y2 = pos(nb)
            is_hl  = key in hl_edges
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            
            metric_val = attrs[active_metric]
            val_str = f"{metric_val:.1f}km"
            if active_metric == 'time': val_str = f"{metric_val:.0f}m"
            if active_metric == 'fuel': val_str = f"{metric_val:.1f}L"
            
            bg_width = 38
            bg_height = 16
            canvas.create_rectangle(mx - bg_width//2, my - bg_height//2, 
                                    mx + bg_width//2, my + bg_height//2, 
                                    fill=BG_MAIN, outline=EDGE_COLOR, width=1)
            
            fg_label = ACCENT_PRIMARY if is_hl else EDGE_TEXT
            canvas.create_text(mx, my, text=val_str, fill=fg_label, font=('Segoe UI', 8, 'bold'))

    # Pass 3: Draw Nodes (on top of everything)
    for name in nodes:
        x, y   = pos(name)
        is_hl  = highlight_path and name in highlight_path
        fill   = BG_MAIN
        outline = HL_NODE if is_hl else NODE_OUTLINE
        lw     = 3 if is_hl else 2

        if is_hl:
            canvas.create_oval(x - RADIUS - 4, y - RADIUS - 4, x + RADIUS + 4, y + RADIUS + 4,
                               fill='', outline='#005B66', width=2)
            fill = HL_NODE
            outline = '#FFFFFF'

        canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                           fill=fill, outline=outline, width=lw)
                           
        # Node text (City initials inside, full name below)
        text_color = '#1E1E2F' if is_hl else FG_PRIMARY
        canvas.create_text(x, y, text=name[:3], fill=text_color, font=('Segoe UI', 9, 'bold'))
                           
        name_color = '#FFFFFF'
        font_weight = 'bold' if is_hl else 'normal'
        canvas.create_text(x, y + RADIUS + 14, text=name, fill=name_color, font=('Segoe UI', 9, font_weight))


# ─────────────────────────────────────────
#  GUI / LAYOUT
# ─────────────────────────────────────────

class AppUI:
    def __init__(self, root, graph, nodes):
        self.root = root
        self.graph = graph
        self.nodes = nodes
        
        # Configure fonts
        self.font_h1 = ('Segoe UI', 18, 'bold')
        self.font_h2 = ('Segoe UI', 12, 'bold')
        self.font_p = ('Segoe UI', 10)
        self.font_small = ('Segoe UI', 9)
        self.font_value = ('Segoe UI', 14, 'bold')

        self.setup_ui()

    def create_card(self, parent, title, row, col):
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=8, bd=0)
        card.grid(row=row, column=col, sticky='nsew', padx=4, pady=4)
        
        tk.Label(card, text=title, bg=BG_CARD, fg=FG_SECONDARY, font=self.font_small).pack(anchor='w')
        val_lbl = tk.Label(card, text="-", bg=BG_CARD, fg=ACCENT_PRIMARY, font=self.font_value)
        val_lbl.pack(anchor='w', pady=(2,0))
        return val_lbl

    def setup_ui(self):
        # ── Main Layout (Sidebar + Canvas) ──
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=320)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(self.root, bg=BG_MAIN)
        self.main_area.pack(side='right', fill='both', expand=True)

        # ── Canvas ──
        self.canvas = tk.Canvas(self.main_area, width=CANVAS_W, height=CANVAS_H,
                                bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=20, pady=20)
        draw_map(self.canvas, self.graph, self.nodes)

        # ── Sidebar Content ──
        # Header
        header_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=20, padx=25)
        header_frm.pack(fill='x')
        tk.Label(header_frm, text="ROUTE ENGINE", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_h1, anchor='w').pack(fill='x')
        tk.Label(header_frm, text="Network Path Optimizer", bg=BG_SIDEBAR, fg=ACCENT_PRIMARY, font=self.font_p, anchor='w').pack(fill='x')

        separator = tk.Frame(self.sidebar, bg=BG_CARD, height=2)
        separator.pack(fill='x', padx=25, pady=(0, 20))

        # Controls Form
        form_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=25)
        form_frm.pack(fill='x')

        # Dropdowns Style (using ttk)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=BG_CARD, background=BG_SIDEBAR, foreground='white', borderwidth=0, arrowcolor=ACCENT_PRIMARY)
        style.map('TCombobox', 
                  fieldbackground=[('readonly', BG_CARD)], 
                  selectbackground=[('readonly', BG_CARD)], 
                  selectforeground=[('readonly', 'white')], 
                  foreground=[('readonly', 'white')])
        self.root.option_add('*TCombobox*Listbox.background', BG_CARD)
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', ACCENT_HOVER)
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')

        # Origin
        tk.Label(form_frm, text="Origin Node", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        self.frm_var = tk.StringVar()
        cb_origin = ttk.Combobox(form_frm, textvariable=self.frm_var, values=self.nodes, state='readonly', font=self.font_p)
        cb_origin.set("Select Origin...")
        cb_origin.pack(fill='x', pady=(4, 15), ipady=4)
        cb_origin.bind("<<ComboboxSelected>>", lambda e: self.on_dropdown_change())

        # Destination
        tk.Label(form_frm, text="Destination Node", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        self.to_var = tk.StringVar()
        cb_dest = ttk.Combobox(form_frm, textvariable=self.to_var, values=self.nodes, state='readonly', font=self.font_p)
        cb_dest.set("Select Destination...")
        cb_dest.pack(fill='x', pady=(4, 15), ipady=4)
        cb_dest.bind("<<ComboboxSelected>>", lambda e: self.on_dropdown_change())

        # Optimization Criteria (Radio Buttons for better UCD)
        tk.Label(form_frm, text="Optimization Criteria", bg=BG_SIDEBAR, fg=FG_SECONDARY, font=self.font_small).pack(anchor='w', pady=(5, 5))
        self.opt_var = tk.StringVar(value='distance')
        
        radio_frm = tk.Frame(form_frm, bg=BG_SIDEBAR)
        radio_frm.pack(fill='x', pady=(0, 20))
        
        for text, val in [("Distance", "distance"), ("Time", "time"), ("Fuel", "fuel")]:
            rb = tk.Radiobutton(radio_frm, text=text, variable=self.opt_var, value=val,
                                bg=BG_SIDEBAR, fg=FG_PRIMARY, selectcolor=BG_CARD,
                                activebackground=BG_SIDEBAR, activeforeground=ACCENT_PRIMARY,
                                font=self.font_p, cursor='hand2', bd=0, highlightthickness=0,
                                command=self.on_metric_change)
            rb.pack(side='left', padx=(0, 10))

        # Actions
        def on_enter(e, btn, color): btn['background'] = color
        def on_leave(e, btn, color): btn['background'] = color

        btn_frm = tk.Frame(form_frm, bg=BG_SIDEBAR)
        btn_frm.pack(fill='x', pady=10)

        reset_btn = tk.Button(btn_frm, text="Reset Map", command=self.reset_map,
                              bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p,
                              relief='flat', pady=6, cursor='hand2', activebackground=BTN_RESET_HOV)
        reset_btn.pack(fill='x')
        reset_btn.bind("<Enter>", lambda e: on_enter(e, reset_btn, BTN_RESET_HOV))
        reset_btn.bind("<Leave>", lambda e: on_leave(e, reset_btn, BTN_RESET_BG))


        # ── Results Dashboard ──
        self.res_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=20, pady=20)
        self.res_frm.pack(fill='both', expand=True)

        tk.Label(self.res_frm, text="ROUTE METRICS", bg=BG_SIDEBAR, fg=FG_SECONDARY, font=self.font_h2, anchor='w').pack(fill='x', padx=5, pady=(0, 10))
        
        metrics_grid = tk.Frame(self.res_frm, bg=BG_SIDEBAR)
        metrics_grid.pack(fill='x')
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

        self.lbl_dist = self.create_card(metrics_grid, "Total Distance", 0, 0)
        self.lbl_time = self.create_card(metrics_grid, "Est. Time", 0, 1)
        self.lbl_fuel = self.create_card(metrics_grid, "Fuel Usage", 1, 0)
        
        self.path_card = tk.Frame(metrics_grid, bg=BG_CARD, padx=12, pady=8, bd=0)
        self.path_card.grid(row=1, column=1, sticky='nsew', padx=4, pady=4)
        tk.Label(self.path_card, text="Path Summary", bg=BG_CARD, fg=FG_SECONDARY, font=self.font_small).pack(anchor='w')
        self.lbl_path = tk.Label(self.path_card, text="-", bg=BG_CARD, fg=FG_PRIMARY, font=('Segoe UI', 9), wraplength=100, justify='left')
        self.lbl_path.pack(anchor='w', pady=(2,0))

    def on_dropdown_change(self):
        # Automatically recalculate path when a new city is selected from the dropdown
        if self.frm_var.get() in self.nodes and self.to_var.get() in self.nodes:
            if self.frm_var.get() == self.to_var.get():
                messagebox.showwarning("Same Node", "Origin and Destination cannot be the same. Please select different nodes.", parent=self.root)
                self.reset_map()
            else:
                self.find_path()

    def on_metric_change(self):
        # Automatically recalculate path when metric is clicked, if valid nodes are selected
        if self.frm_var.get() in self.nodes and self.to_var.get() in self.nodes:
            if self.frm_var.get() != self.to_var.get():
                self.find_path()
            else:
                draw_map(self.canvas, self.graph, self.nodes, active_metric=self.opt_var.get())
        else:
            # Just visually update the graph lines even if no route is planned
            draw_map(self.canvas, self.graph, self.nodes, active_metric=self.opt_var.get())

    def reset_map(self):
        draw_map(self.canvas, self.graph, self.nodes, active_metric=self.opt_var.get())
        self.lbl_dist.config(text="-")
        self.lbl_time.config(text="-")
        self.lbl_fuel.config(text="-")
        self.lbl_path.config(text="-")
        self.frm_var.set("Select Origin...")
        self.to_var.set("Select Destination...")

    def find_path(self):
        start = self.frm_var.get()
        end   = self.to_var.get()
        key   = self.opt_var.get()

        if start not in self.nodes or end not in self.nodes:
            return

        if start == end:
            return

        cost, path, totals = dijkstra(self.graph, start, end, key)

        if not path:
            messagebox.showinfo("No Route", f"No accessible path found from {start} to {end}.", parent=self.root)
            self.reset_map()
            return

        draw_map(self.canvas, self.graph, self.nodes, highlight_path=path, active_metric=key)
        
        # Update metrics
        self.lbl_dist.config(text=f"{totals['distance']:.1f} km")
        self.lbl_time.config(text=f"{totals['time']:.0f} min")
        self.lbl_fuel.config(text=f"{totals['fuel']:.1f} L")
        
        # Format path
        path_str = " → ".join(path)
        self.lbl_path.config(text=path_str)


def build_gui(graph, nodes):
    root = tk.Tk()
    root.title("Optinet Network Optimizer")
    root.geometry("1100x700")
    root.configure(bg=BG_MAIN)
    root.minsize(900, 600)
    
    # Force window to the front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    app = AppUI(root, graph, nodes)
    root.mainloop()


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

import os

if __name__ == '__main__':
    # Ensure we look for the dataset in the same directory as this script regardless of working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    CSV_FILE = os.path.join(script_dir, 'dataset.csv')
    
    try:
        graph, nodes = load_graph(CSV_FILE)
    except FileNotFoundError:
        print(f"ERROR: '{CSV_FILE}' not found. Please ensure 'dataset.csv' exists in the same folder.")
        raise

    print(f"Loaded {len(nodes)} nodes and {sum(len(v) for v in graph.values()) // 2} edges.")
    build_gui(graph, nodes)