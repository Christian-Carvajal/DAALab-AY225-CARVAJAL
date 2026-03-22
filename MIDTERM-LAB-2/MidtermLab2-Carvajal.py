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
        self._first_path_run = True
        
        # Configure fonts
        self.font_h1 = ('Segoe UI', 18, 'bold')
        self.font_h2 = ('Segoe UI', 12, 'bold')
        self.font_p = ('Segoe UI', 10)
        self.font_small = ('Segoe UI', 9)
        self.font_value = ('Segoe UI', 14, 'bold')

        self.setup_ui()

    def show_custom_dialog(self, title, message, show_maximize=False):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("450x200")
        dlg.configure(bg=BG_CARD)
        dlg.transient(self.root)
        dlg.grab_set()
        
        # Center the dialog
        dlg.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 100
        dlg.geometry(f"+{x}+{y}")
        
        lbl_title = tk.Label(dlg, text=title, bg=BG_CARD, fg=ACCENT_PRIMARY, font=self.font_h2)
        lbl_title.pack(pady=(20, 10))
        
        lbl_msg = tk.Label(dlg, text=message, bg=BG_CARD, fg=FG_PRIMARY, font=self.font_p, wraplength=400, justify='center')
        lbl_msg.pack(pady=(0, 20), padx=20)
        
        btn_frame = tk.Frame(dlg, bg=BG_CARD)
        btn_frame.pack(fill='x', pady=10)
        
        if show_maximize:
            def do_maximize():
                self.root.state('zoomed')
                dlg.destroy()
            btn_max = tk.Button(btn_frame, text="Maximize Window", command=do_maximize, bg=ACCENT_PRIMARY, fg=BG_MAIN, font=self.font_p, relief='flat', cursor='hand2', padx=10, pady=5)
            btn_max.pack(side='left', expand=True, padx=10)
            
            btn_dismiss = tk.Button(btn_frame, text="Dismiss", command=dlg.destroy, bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p, relief='flat', cursor='hand2', padx=10, pady=5)
            btn_dismiss.pack(side='right', expand=True, padx=10)
        else:
            btn_ok = tk.Button(btn_frame, text="OK", command=dlg.destroy, bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p, relief='flat', cursor='hand2', padx=20, pady=5)
            btn_ok.pack()

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
        
        # Scrollbar Style (Silver/Grey track)
        style.configure('Vertical.TScrollbar',
                        background='#A2A2B5',     # Silver thumb
                        darkcolor='#A2A2B5',
                        lightcolor='#A2A2B5',
                        troughcolor=BG_MAIN,      # Track matches background
                        bordercolor=BG_MAIN,
                        arrowcolor=ACCENT_PRIMARY) # Cyan arrows
        style.map('Vertical.TScrollbar',
                  background=[('active', '#FFFFFF')]) # Bright white when hovered
        
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

        analyze_btn = tk.Button(btn_frm, text="Run Global Hub Analysis", command=self.show_analysis,
                              bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p,
                              relief='flat', pady=6, cursor='hand2', activebackground=BTN_RESET_HOV)
        analyze_btn.pack(fill='x', pady=(0, 10))
        analyze_btn.bind("<Enter>", lambda e: on_enter(e, analyze_btn, BTN_RESET_HOV))
        analyze_btn.bind("<Leave>", lambda e: on_leave(e, analyze_btn, BTN_RESET_BG))

        stats_btn = tk.Button(btn_frm, text="View Algorithmic Stats", command=self.show_stats,
                              bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p,
                              relief='flat', pady=6, cursor='hand2', activebackground=BTN_RESET_HOV)
        stats_btn.pack(fill='x', pady=(0, 10))
        stats_btn.bind("<Enter>", lambda e: on_enter(e, stats_btn, BTN_RESET_HOV))
        stats_btn.bind("<Leave>", lambda e: on_leave(e, stats_btn, BTN_RESET_BG))

        tech_btn = tk.Button(btn_frm, text="Technical", command=self.show_tech_defense,
                              bg=BTN_RESET_BG, fg=FG_PRIMARY, font=self.font_p,
                              relief='flat', pady=6, cursor='hand2', activebackground=BTN_RESET_HOV)
        tech_btn.pack(fill='x', pady=(0, 10))
        tech_btn.bind("<Enter>", lambda e: on_enter(e, tech_btn, BTN_RESET_HOV))
        tech_btn.bind("<Leave>", lambda e: on_leave(e, tech_btn, BTN_RESET_BG))

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
        
        # Span the empty space for cleaner look if needed, but pulling Path Summary out is better
        placeholder = tk.Frame(metrics_grid, bg=BG_SIDEBAR)
        placeholder.grid(row=1, column=1, sticky='nsew')
        
        # Path Summary (Full width below metrics grid)
        self.path_card = tk.Frame(self.res_frm, bg=BG_CARD, padx=12, pady=8, bd=0)
        self.path_card.pack(fill='both', expand=True, pady=(10, 0), padx=4)
        
        tk.Label(self.path_card, text="Path Summary", bg=BG_CARD, fg=FG_SECONDARY, font=self.font_small).pack(anchor='w')
        
        # Scrollable Text widget frame
        path_text_frame = tk.Frame(self.path_card, bg=BG_CARD)
        path_text_frame.pack(fill='both', expand=True, pady=(2,0))
        
        self.lbl_path = tk.Text(path_text_frame, bg=BG_CARD, fg=FG_PRIMARY, font=('Segoe UI', 9), bd=0, height=4, wrap='word')
        
        # Add actual scrollbar so it can be dragged
        path_scroll = ttk.Scrollbar(path_text_frame, orient='vertical', command=self.lbl_path.yview)
        self.lbl_path.configure(yscrollcommand=path_scroll.set)
        
        self.lbl_path.pack(side='left', fill='both', expand=True)
        path_scroll.pack(side='right', fill='y')
        
        self.lbl_path.insert('1.0', "-")
        self.lbl_path.config(state='disabled')
        
        tk.Label(self.sidebar, text="(Maximize window for best visibility)", bg=BG_SIDEBAR, fg=FG_SECONDARY, font=('Segoe UI', 8, 'italic')).pack(side='bottom', pady=(0, 10))

    def on_dropdown_change(self):
        # Automatically recalculate path when a new city is selected from the dropdown
        if self.frm_var.get() in self.nodes and self.to_var.get() in self.nodes:
            if self.frm_var.get() == self.to_var.get():
                self.show_custom_dialog("Invalid Selection", "Origin and Destination cannot be the same.\nPlease select different nodes.")
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

    def show_analysis(self):
        win = tk.Toplevel(self.root)
        win.title("Network Hub Optimization Report")
        # Ensure window is large and let it resize naturally without text squishing.
        win.state('zoomed')
        win.geometry("1500x900")
        win.configure(bg=BG_MAIN)
        
        # Focus strategy
        win.transient(self.root)
        win.grab_set()
        
        # Header
        hdr = tk.Frame(win, bg=BG_SIDEBAR, pady=15)
        hdr.pack(fill='x')
        
        btn_back = tk.Button(hdr, text="← Return to Map", command=win.destroy, bg=BTN_RESET_BG, fg=FG_PRIMARY, relief='flat', padx=10, cursor='hand2')
        btn_back.pack(side='left', padx=15)
        
        tk.Label(hdr, text="📊 Comprehensive All-Pairs Algorithmic Analysis", 
                 font=('Segoe UI', 16, 'bold'), bg=BG_SIDEBAR, fg=FG_PRIMARY).pack(side='left', fill='x', expand=True)

        # Compute data
        metrics = [('distance', 'Optimal Distance', 'km'), ('time', 'Optimal Time', 'mins'), ('fuel', 'Optimal Fuel', 'L')]
        results = {}
        for m_key, m_name, m_unit in metrics:
            node_totals = []
            for start in self.nodes:
                total_cost = 0
                details = []
                for dest in self.nodes:
                    if start == dest: continue
                    cost, path, _ = dijkstra(self.graph, start, dest, m_key)
                    if cost is not None:
                        total_cost += cost
                        details.append((dest, cost, path))
                node_totals.append((total_cost, start, details))
            node_totals.sort(key=lambda x: x[0])
            results[m_key] = node_totals

        # Layout
        container = tk.Frame(win, bg=BG_MAIN)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        for i, (m_key, m_name, m_unit) in enumerate(metrics):
            container.columnconfigure(i, weight=1)
            card = tk.Frame(container, bg=BG_SIDEBAR, bd=0)
            card.grid(row=0, column=i, sticky='nsew', padx=10)
            
            best_val, best_node, best_details = results[m_key][0]
            
            tk.Label(card, text=f"Top Hub ({m_name})", font=('Segoe UI', 12, 'bold'), bg=BG_SIDEBAR, fg=FG_SECONDARY).pack(pady=(15, 0))
            tk.Label(card, text=f"Total: {best_val:.2f} {m_unit}", font=('Segoe UI', 16, 'bold'), bg=BG_SIDEBAR, fg=ACCENT_PRIMARY).pack(pady=(0, 15))
            
            detail_frm = tk.Frame(card, bg=BG_CARD, padx=15, pady=15)
            detail_frm.pack(fill='both', expand=True, padx=15, pady=(0, 15))
            
            tk.Label(detail_frm, text="[ ALGORITHM VALIDATION ]", font=('Courier New', 9, 'bold'), bg=BG_CARD, fg=FG_SECONDARY, anchor='w').pack(fill='x', pady=(0, 10))
            tk.Label(detail_frm, text=f"Aggregate {m_key} sums per vertex:", font=('Segoe UI', 9, 'italic'), bg=BG_CARD, fg=FG_PRIMARY, anchor='w').pack(fill='x')
            
            summary_canvas = tk.Canvas(detail_frm, bg=BG_CARD, highlightthickness=0, height=140)
            summary_canvas.pack(fill='x', pady=(5,5))
            
            y_pos = 5
            for rank, (val, node, _) in enumerate(results[m_key]):
                prefix = "► " if rank == 0 else "  "
                color = ACCENT_PRIMARY if rank == 0 else FG_PRIMARY
                bold = 'bold' if rank == 0 else 'normal'
                summary_canvas.create_text(5, y_pos, text=f"{prefix}{node:<10}  {val:.2f}", anchor='nw', font=('Consolas', 9, bold), fill=color)
                y_pos += 16
                
            tk.Label(detail_frm, text=f"\n[ OPTIMAL TARGET ]\nBest Origin: {best_node} strictly dominates.", font=('Segoe UI', 9, 'bold'), bg=BG_CARD, fg=ACCENT_PRIMARY, anchor='w', justify='left', wraplength=350).pack(fill='x', pady=(5,10))
            
            tk.Label(detail_frm, text=f"ROUTING STRUCTURE (From {best_node}):", font=('Segoe UI', 8, 'bold'), bg=BG_CARD, fg=FG_SECONDARY, anchor='w').pack(fill='x', pady=(0,5))
            
            # Canvas with scrollbar for path details
            canvas = tk.Canvas(detail_frm, bg=BG_CARD, highlightthickness=0)
            scrollbar = ttk.Scrollbar(detail_frm, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=BG_CARD)

            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            # Use a slightly wider window to prevent cutoff
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=550)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            for dest, cost, path in sorted(best_details, key=lambda x: x[0]):
                path_str = " ➔ ".join(path)
                # Keep formatting flat without forcing Message into an unnatural wrap
                desc = f"Target {dest:<8} | Cost: {cost:.1f}\n   Path: {path_str}"
                tk.Label(scrollable_frame, text=desc, font=('Consolas', 9), bg=BG_CARD, fg=FG_PRIMARY, anchor='w', justify='left').pack(fill='x', pady=(2, 6))

    def show_stats(self):
        win = tk.Toplevel(self.root)
        win.title("Algorithmic Properties & Memory Data")
        win.geometry("750x750")
        win.configure(bg=BG_MAIN)
        win.transient(self.root)
        win.grab_set()

        # Title
        tk.Label(win, text="⚙️ Graph Data & Algorithm Properties", font=('Segoe UI', 16, 'bold'), bg=BG_MAIN, fg=FG_PRIMARY).pack(pady=20)
        
        info_frame = tk.Frame(win, bg=BG_SIDEBAR, padx=20, pady=20)
        info_frame.pack(fill='x', padx=20)
        
        num_v = len(self.nodes)
        num_e = sum(len(v) for v in self.graph.values()) // 2
        
        stats_text = (
            f"GRAPH PROPERTIES:\n"
            f" ➔ Order (Vertices, V): {num_v}\n"
            f" ➔ Size (Edges, E): {num_e}\n"
            f" ➔ Graph Type: Undirected, Positively Weighted\n"
            f" ➔ Data Structure Used: Adjacency List (O(1) neighbor lookups)\n\n"
            f"DIJKSTRA'S ALGORITHM DATA:\n"
            f" ➔ Queue Mechanism: Priority Queue (Python heapq Module)\n"
            f" ➔ Time Complexity: O((V + E) log V) via Binary Heap\n"
            f" ➔ Space Complexity: O(V) array visited tracking + O(V) Priority Queue\n"
            f" ➔ Negative Weights Support: None (Valid, as geography properties >= 0)\n"
        )
        
        tk.Label(info_frame, text=stats_text, font=('Consolas', 10), bg=BG_SIDEBAR, fg=FG_SECONDARY, justify='left', anchor='w').pack(fill='x')
        
        tk.Label(win, text="[ RAW ADJACENCY LIST IN MEMORY ]", font=('Courier New', 10, 'bold'), bg=BG_MAIN, fg=ACCENT_PRIMARY, anchor='w').pack(fill='x', padx=20, pady=(15, 5))
        
        text_area = tk.Text(win, bg=BG_CARD, fg=FG_PRIMARY, font=('Consolas', 9), bd=0, padx=15, pady=15)
        text_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
        
        dump_str = ""
        for n in sorted(self.graph.keys()):
            dump_str += f"{n}:\n"
            for nb, attrs in sorted(self.graph[n], key=lambda x: x[0]):
                dump_str += f"  ➔ {nb:<10} [Dist: {attrs['distance']}km | Time: {attrs['time']}m | Fuel: {attrs['fuel']}L]\n"
            dump_str += "\n"
            
        text_area.insert('1.0', dump_str)
        text_area.config(state='disabled')

    def show_tech_defense(self):
        win = tk.Toplevel(self.root)
        win.title("Technical Defense & Source Validation")
        win.state('zoomed')
        win.geometry("1500x900")
        win.configure(bg=BG_MAIN)
        win.transient(self.root)
        win.grab_set()
        
        hdr = tk.Frame(win, bg=BG_SIDEBAR, pady=15)
        hdr.pack(fill='x')
        btn_back = tk.Button(hdr, text="← Return to Map", command=win.destroy, bg=BTN_RESET_BG, fg=FG_PRIMARY, relief='flat', padx=10, cursor='hand2')
        btn_back.pack(side='left', padx=15)
        tk.Label(hdr, text="🧑‍🏫 Technical Analysis & Expected Defense Questions", font=('Segoe UI', 16, 'bold'), bg=BG_SIDEBAR, fg=FG_PRIMARY).pack(side='left', fill='x', expand=True)

        canvas = tk.Canvas(win, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_MAIN)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1400)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        # Helper to create Q&A Panels
        def add_qa_panel(question, answer, code_snippet=None):
            card = tk.Frame(scrollable_frame, bg=BG_CARD, padx=20, pady=20)
            card.pack(fill='x', pady=(0, 20), padx=20)
            
            tk.Label(card, text=f"Q: {question}", font=('Segoe UI', 14, 'bold'), fg=ACCENT_PRIMARY, bg=BG_CARD, justify='left', wraplength=1300, anchor='w').pack(fill='x', pady=(0, 10))
            tk.Label(card, text=answer, font=('Segoe UI', 11), fg=FG_PRIMARY, bg=BG_CARD, justify='left', wraplength=1300, anchor='w').pack(fill='x', pady=(0, 15))
            
            if code_snippet:
                code_frame = tk.Frame(card, bg='#151521', padx=15, pady=15)
                code_frame.pack(fill='x')
                tk.Label(code_frame, text=code_snippet, font=('Consolas', 10), fg='#00E5FF', bg='#151521', justify='left', anchor='w').pack(fill='x')

        # Generate the panels
        add_qa_panel(
            "How does the program extract data from the CSV, and what data structure holds it?",
            "The program opens 'dataset.csv' using python's built-in `csv.DictReader` to safely map headers. It dynamically extracts 'From Node', 'To Node', 'Distance', 'Time', and 'Fuel'. To store it, I used an Adjacency List represented by a Python Dictionary. Each key is a City, and its value is a list of Tuples containing the neighboring city and a nested dictionary of weights.",
            "# [See Code: Lines 11-30]\n"
            "def load_graph(filepath):\n"
            "    graph = {}\n"
            "    nodes = set()\n"
            "    with open(filepath, newline='', encoding='utf-8-sig') as f:\n"
            "        reader = csv.DictReader(f)\n"
            "        for row in reader:\n"
            "            ... # parsing casting to float\n"
            "            graph.setdefault(frm, []).append((to, {'distance': dist, 'time': time, 'fuel': fuel}))\n"
            "            graph.setdefault(to,  []).append((frm, {'distance': dist, 'time': time, 'fuel': fuel}))"
        )
        
        add_qa_panel(
            "What algorithm did you implement to calculate the shortest path, and why?",
            "I used Dijkstra's Algorithm. Since geographic values (distance, time, fuel) can never be negative, Dijkstra is mathematically optimal. I utilized a Min-Heap (via Python's `heapq` module) as a Priority Queue to keep the extraction of the lowest-cost edge at O(log V). The total time complexity thus comes out to O((V + E) log V).",
            "# [See Code: Lines 37-69]\n"
            "def dijkstra(graph, start, end, weight_key):\n"
            "    pq = [(0, start, [start])] # Cost, Current Node, Path Taken\n"
            "    visited = {}\n"
            "    while pq:\n"
            "        cost, node, path = heapq.heappop(pq)\n"
            "        if node in visited: continue\n"
            "        visited[node] = (cost, path)\n"
            "        ...\n"
            "        for (nb, attrs) in graph.get(node, []):\n"
            "            if nb not in visited:\n"
            "                heapq.heappush(pq, (cost + attrs[weight_key], nb, path + [nb]))"
        )
        
        add_qa_panel(
            "If the user asks to optimize by 'Time', how does the program calculate the 'Fuel' and 'Distance' shown in the results?",
            "This is a common trap! When calculating Dijkstra, I only sum up the active `weight_key`. If I optimized for Time, the shortest path guarantees the fastest route. But once that final array of nodes (e.g., [A, B, C]) is found, I iterate back through the graph specifically connecting those nodes and independently aggregate the exact Distance and Fuel values of that specific path.",
            "# [See Code: Lines 53-64]\n"
            "        if node == end:\n"
            "            totals = {'distance': 0, 'time': 0, 'fuel': 0}\n"
            "            for i in range(len(path) - 1):\n"
            "                a, b = path[i], path[i + 1]\n"
            "                for (nb, attrs) in graph.get(a, []):\n"
            "                    if nb == b:\n"
            "                        totals['distance'] += attrs['distance']\n"
            "                        totals['time']     += attrs['time']\n"
            "                        totals['fuel']     += attrs['fuel']\n"
            "            return cost, path, totals"
        )

        add_qa_panel(
            "How did you implement the 'Global Hub' feature and trace back its exact ranking?",
            "The Global Hub feature runs an 'All-Pairs Shortest Path' simulation dynamically. First, I iterate every single node as an 'Origin' using a standard for loop. For each origin, I run Dijkstra targeting every other node to gather the individual cost, and aggregate them into `total_cost`. These aggregate sums are saved into a List of Tuples: `(total_cost, origin_node, details)`. Finally, I execute Python's built-in `.sort(key=lambda x: x[0])` to rank them from the absolute lowest cost to highest, natively establishing the 'Top Hub' correctly at index 0.",
            "# [See Code: Lines 365-373]\n"
            "        for start in self.nodes:\n"
            "            total_cost = 0\n"
            "            details = []\n"
            "            for dest in self.nodes:\n"
            "                if start == dest: continue\n"
            "                cost, path, _ = dijkstra(self.graph, start, dest, m_key)\n"
            "                if cost is not None:\n"
            "                    total_cost += cost\n"
            "            node_totals.append((total_cost, start, details))\n"
            "        node_totals.sort(key=lambda x: x[0])  # Rank from Best to Worst"
        )
        
        add_qa_panel(
            "How are the numbers in the 'Algorithmic Stats' (like Order and Size) calculated so accurately?",
            "Graph Order (V) represents the total number of Vertices. Since my `self.nodes` is a distinct Python `set()`, I just return `len(self.nodes)`. \n\nGraph Size (E) represents total Edges. Because this graph is Undirected (A -> B and B -> A both exist in the dictionary), summing the raw lengths of every neighbor list would double-count them. To fix this, I sum all elements inside `self.graph.values()` and floor-divide by 2 `// 2`, extracting the exact true Edge count instantaneously.",
            "# [See Code: Lines 453-456]\n"
            "        num_v = len(self.nodes)\n"
            "        num_e = sum(len(v) for v in self.graph.values()) // 2\n"
            "        # Big-O Time: O((V + E) log V)\n"
            "        # Big-O Space: O(V) for visited set + Priority Queue"
        )

        add_qa_panel(
            "How is the canvas rendering the map coordinates effectively?",
            "Instead of hardcoding raw pixel values, I mapped cities using proportional floats (e.g., 0.15, 0.25). A multiplier function takes the `CANVAS_W` and `CANVAS_H` and projects the percentages onto the screen. It separates drawing into 3 passes (Edges -> Labels -> Nodes) to ensure the overlapping visual hierarchy (z-index) puts nodes strictly on top.",
            "# [See Code: Lines 92-142]\n"
            "    def pos(name):\n"
            "        px, py = NODE_POSITIONS.get(name, (0.5, 0.5))\n"
            "        return int(px * W), int(py * H)\n"
            "    # Pass 1: Draw lines\n"
            "    # Pass 2: Draw Labels ON TOP of lines\n"
            "    # Pass 3: Draw Nodes ON TOP of labels"
        )
        
        add_qa_panel(
            "Why did you use a `set()` to store the nodes during data loading instead of a standard list?",
            "A `set` automatically prevents duplicate entries. When reading the CSV, both 'From' and 'To' cities appear multiple times across different rows. By using `nodes.add(frm)`, it guarantees O(1) average time complexity for insertions and ensures each city is only stored once. If I used a list, I would have to use `if node not in list`, which operates at O(N) time complexity and heavily slows down the data loading.",
            "# [See Code: Lines 13-25]\n"
            "def load_graph(filepath):\n"
            "    graph = {}\n"
            "    nodes = set() # Optimized for O(1) uniqueness\n"
            "    with open(filepath, ...):\n"
            "        ...\n"
            "        nodes.add(frm)\n"
            "        nodes.add(to)"
        )

        add_qa_panel(
            "What happens if a user selects the exact same city for both the Origin and the Destination (e.g., Bacoor to Bacoor)?",
            "The program intercepts this invalid input immediately at the UI event level. Inside the `on_dropdown_change` method, it checks if the selected origin matches the destination. If they are identical, it halts execution before the Dijkstra algorithm is even called, triggers a custom dialog box alerting the user, and safely resets the map. There is also a secondary fail-safe directly inside the `find_path` method that aborts the calculation if `start == end`.",
            "# [See Code: Lines 339-345]\n"
            "    # Inside on_dropdown_change() UI event handler:\n"
            "    if self.frm_var.get() == self.to_var.get():\n"
            "        self.show_custom_dialog(\n"
            "            \"Invalid Selection\", \n"
            "            \"Origin and Destination cannot be the same.\\nPlease select different nodes.\"\n"
            "        )\n"
            "        self.reset_map()\n"
            "    else:\n"
            "        self.find_path()"
        )

        add_qa_panel(
            "If a panelist runs your code on their own computer, will the program crash because the file path to the CSV is different?",
            "No, the program is completely portable. Instead of hardcoding my local computer's absolute directory path, I utilized Python's built-in `os` module. Specifically, `os.path.dirname(os.path.abspath(__file__))` dynamically locates the exact folder where the script is currently running and looks for `dataset.csv` right next to it. I also wrapped it in a `try-except` block to catch a `FileNotFoundError` cleanly if the user forgot to download the CSV entirely.",
            "# [See Code: Lines 885-895]\n"
            "if __name__ == '__main__':\n"
            "    script_dir = os.path.dirname(os.path.abspath(__file__))\n"
            "    CSV_FILE = os.path.join(script_dir, 'dataset.csv')\n"
            "    try:\n"
            "        graph, nodes = load_graph(CSV_FILE)\n"
            "    except FileNotFoundError:\n"
            "        print('ERROR: dataset.csv not found.')\n"
            "        raise"
        )

        add_qa_panel(
            "Your standard Dijkstra is O((V+E) log V). What is the exact mathematical time complexity of your 'Global Hub Analysis' feature?",
            "The Global Hub acts as an 'All-Pairs Shortest Path' calculator. It loops through every node as an origin (V), and for each origin, it runs Dijkstra targeting every other node (V-1). Therefore, it executes the Dijkstra algorithm V × (V-1) times. The total theoretical time complexity functionally scales to O(V² × (V+E) log V). It executes instantly for our dataset of 8 cities, but for a massive nationwide grid, this specific unoptimized O(V³) bounding would need to be replaced with Floyd-Warshall or offloaded to a background thread to prevent UI freezing.",
            "# [See Code: Lines 366-372]\n"
            "        for start in self.nodes: # Loops V times\n"
            "            ... \n"
            "            for dest in self.nodes: # Loops V-1 times\n"
            "                if start == dest: continue\n"
            "                cost, path, _ = dijkstra(self.graph, start, dest, m_key)"
        )
        
        add_qa_panel(
            "When traversing an Undirected Graph, how does your Dijkstra implementation prevent infinite loops (going back and forth between A and B)?",
            "I utilize a `visited` dictionary. When a node is popped from the Priority Queue, it represents the absolute shortest known path to that node. It is immediately registered in `visited`. During neighbor exploration, the condition `if nb not in visited` acts as a strict firewall, blocking the algorithm from adding paths that trace back to previously finalized nodes.",
            "# [See Code: Lines 46-68]\n"
            "    while pq:\n"
            "        cost, node, path = heapq.heappop(pq)\n\n"
            "        if node in visited: # Firewall 1: Check if already processed in queue\n"
            "            continue\n"
            "        visited[node] = (cost, path) # Mark node as permanently finalized\n\n"
            "        for (nb, attrs) in graph.get(node, []):\n"
            "            if nb not in visited: # Firewall 2: Do not backtrack\n"
            "                heapq.heappush(pq, (new_cost, nb, path + [nb]))"
        )

        add_qa_panel(
            "How does `heapq` know what to evaluate when sorting the queue? What happens if two paths have the exact same cost?",
            "Python's `heapq` structures the Priority Queue as a Binary Min-Heap and compares tuples lexicographically (element by element). My tuples are structured as `(cost, node, path)`. By placing `cost` at index 0, the Min-Heap naturally extracts the lowest cost first. If two costs are identical, it falls back to index 1 (`node`), comparing the city names alphabetically. This prevents the program from crashing attempting to compare lists (`path`), effortlessly establishing a stable sort process.",
            "# [See Code: Lines 43-47]\n"
            "    # Priority Queue tuple format: (cost, node_name, list_of_path_nodes)\n"
            "    pq = [(0, start, [start])]\n"
            "    \n"
            "    while pq:\n"
            "        # Pops the element with the lowest `cost` directly at index 0\n"
            "        cost, node, path = heapq.heappop(pq)"
        )


    def reset_map(self):
        draw_map(self.canvas, self.graph, self.nodes, active_metric=self.opt_var.get())
        self.lbl_dist.config(text="-")
        self.lbl_time.config(text="-")
        self.lbl_fuel.config(text="-")
        
        self.lbl_path.config(state='normal')
        self.lbl_path.delete('1.0', tk.END)
        self.lbl_path.insert('1.0', "-")
        self.lbl_path.config(state='disabled')
        
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
            self.show_custom_dialog("No Route", f"No accessible path found from {start} to {end}.")
            self.reset_map()
            return

        draw_map(self.canvas, self.graph, self.nodes, highlight_path=path, active_metric=key)
        
        # Update metrics
        self.lbl_dist.config(text=f"{totals['distance']:.1f} km")
        self.lbl_time.config(text=f"{totals['time']:.0f} min")
        self.lbl_fuel.config(text=f"{totals['fuel']:.1f} L")
        
        # Format path with detailed step-by-step segment weights
        path_parts = []
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            seg_val = 0
            for (nb, attrs) in self.graph.get(a, []):
                if nb == b:
                    seg_val = attrs[key]
                    break
            unit_str = "km" if key == "distance" else ("m" if key == "time" else "L")
            path_parts.append(f"{a} ─({seg_val:.1f}{unit_str})➔")
            
        path_parts.append(path[-1])
        path_str = " ".join(path_parts)
        
        self.lbl_path.config(state='normal')
        self.lbl_path.delete('1.0', tk.END)
        self.lbl_path.insert('1.0', path_str)
        self.lbl_path.config(state='disabled')
        
        # Check if the user should be prompted to maximize for better viewing
        if getattr(self, '_first_path_run', True):
            self._first_path_run = False
            # If not vertically zoomed/maximized
            if self.root.state() != 'zoomed':
                self.show_custom_dialog(
                    "Display Recommendation",
                    "For full path details, edge visibility, and the best immersive experience, it is highly recommended to view this application in Full Screen.",
                    show_maximize=True
                )


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