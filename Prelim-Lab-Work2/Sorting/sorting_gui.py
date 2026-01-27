import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import threading
import sys
import os

# Increase recursion depth just in case, though for 10k-20k items log(n) is small.
sys.setrecursionlimit(20000)

class SortingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Algorithms Analyzer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # --- Premium Industry Palette (Black, Gold, White) ---
        self.colors = {
            "bg": "#121212",           # Deep Matte Black
            "panel": "#1E1E1E",        # Elevated Black Surface
            "text": "#FFFFFF",         # High Contrast White
            "subtext": "#AAAAAA",      # Silver/Grey
            "accent": "#D4AF37",       # Metallic Gold
            "accent_hover": "#FFD700", # Bright Gold
            "success": "#D4AF37",      # Gold for success
            "warning": "#FF9800",      # Orange for running
            "button_fg": "#000000",    # Black Text on Gold Buttons
            "border": "#333333"
        }
        
        self.root.configure(bg=self.colors["bg"])

        # Use absolute path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(script_dir, "dataset.txt")
        self.original_data = []
        self.is_sorting = False
        self.stop_requested = False
        self.resize_timer = None

        self.setup_styles()
        self.create_layout()
        self.load_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # 'clam' allows flexible styling
        
        # Configure Frames
        style.configure("Main.TFrame", background=self.colors["bg"])
        style.configure("Panel.TFrame", background=self.colors["panel"], relief="flat")
        
        # Configure Labels
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=self.colors["text"]) # White Title
        style.configure("SubHeader.TLabel", font=("Segoe UI", 11), foreground=self.colors["subtext"])
        
        # Timer Label Style
        style.configure("Timer.TLabel", font=("Consolas", 28), foreground=self.colors["accent"], background=self.colors["panel"])
        
        # Standard Buttons (Gold)
        style.configure("TButton", 
            font=("Segoe UI", 10, "bold"),
            background=self.colors["accent"],
            foreground=self.colors["button_fg"],
            borderwidth=0,
            padding=10
        )
        style.map("TButton",
            background=[('active', self.colors["accent_hover"]), ('disabled', '#333333')],
            foreground=[('disabled', '#888888')]
        )
        
        # Reset Button Style (White with Black Text)
        style.configure("Reset.TButton", background="#FFFFFF", foreground="#000000") 
        style.map("Reset.TButton", background=[('active', '#e0e0e0'), ('disabled', '#333333')])

    def create_layout(self):
        # 1. Main Conteiner
        container = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # 2. Header Section
        header_frame = ttk.Frame(container, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Sorting Algorithm Analyzer", style="Header.TLabel")
        title.pack(side=tk.LEFT)
        
        # 3. Content Area (Left: Controls, Right: Data)
        content_frame = ttk.Frame(container, style="Main.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Left Panel: Controls & Metrics ---
        left_panel = ttk.Frame(content_frame, style="Panel.TFrame", padding=20)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Status
        ttk.Label(left_panel, text="STATUS", style="SubHeader.TLabel", background=self.colors["panel"]).pack(anchor=tk.W)
        self.info_label = ttk.Label(left_panel, text="Initializing...", style="Panel.TLabel", font=("Segoe UI", 11))
        self.info_label.pack(anchor=tk.W, pady=(5, 20))
        
        # Timer
        ttk.Label(left_panel, text="PERFORMANCE", style="SubHeader.TLabel", background=self.colors["panel"]).pack(anchor=tk.W)
        self.time_display = ttk.Label(left_panel, text="0.0000s", style="Timer.TLabel")
        self.time_display.pack(anchor=tk.W, pady=(5, 30))
        
        # Menu Options
        ttk.Label(left_panel, text="ALGORITHMS", style="SubHeader.TLabel", background=self.colors["panel"]).pack(anchor=tk.W, pady=(0, 10))
        
        self.btn_bubble = ttk.Button(left_panel, text="Bubble Sort", command=lambda: self.start_sort("Bubble"))
        self.btn_bubble.pack(fill=tk.X, pady=5)
        
        self.btn_insertion = ttk.Button(left_panel, text="Insertion Sort", command=lambda: self.start_sort("Insertion"))
        self.btn_insertion.pack(fill=tk.X, pady=5)
        
        self.btn_merge = ttk.Button(left_panel, text="Merge Sort", command=lambda: self.start_sort("Merge"))
        self.btn_merge.pack(fill=tk.X, pady=5)
        
        self.btn_stop = ttk.Button(left_panel, text="Stop Sorting", command=self.stop_sort, state=tk.DISABLED)
        self.btn_stop.pack(fill=tk.X, pady=5)

        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=20)
        
        self.btn_reset = ttk.Button(left_panel, text="Reset & Reload", style="Reset.TButton", command=self.reset_data)
        self.btn_reset.pack(fill=tk.X, side=tk.BOTTOM)

        # --- Right Panel: Data Visualization ---
        right_panel = ttk.Frame(content_frame, style="Main.TFrame")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tabbed Interface for "Industry Standard" Multi-view
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=(0, 20), pady=(0, 20))

        # Tab 1: Graphical Visualization
        self.viz_frame = ttk.Frame(self.notebook, style="Main.TFrame", padding=10)
        self.notebook.add(self.viz_frame, text="   Graphical View   ")
        
        self.canvas = tk.Canvas(self.viz_frame, bg=self.colors["panel"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.refresh_canvas) # Redraw on resize

        # Tab 2: Raw Data Grid
        self.grid_frame = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.grid_frame, text="   Data Grid   ")
        
        # Text Area with Custom colors
        self.text_area = scrolledtext.ScrolledText(self.grid_frame, 
                                                   font=("Consolas", 10),
                                                   bg=self.colors["panel"], 
                                                   fg=self.colors["text"],
                                                   insertbackground="white",
                                                   relief="flat",
                                                   padx=10,
                                                   pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Debounce resize to prevent lag during window dragging
        self.text_area.bind("<Configure>", self.on_text_resize)

        # Progress Bar (Indeterminate)
        self.progress = ttk.Progressbar(container, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(20, 0))

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                self.original_data = [int(line.strip()) for line in f if line.strip().lstrip('-').isdigit()]
            self.info_label.config(text=f"Loaded {len(self.original_data)} items")
            self.display_data(self.original_data)
        except FileNotFoundError:
             self.info_label.config(text="File not found")
             messagebox.showerror("Error", f"Dataset file not found at:\n{self.filename}\n\nPlease ensure 'dataset.txt' is in the same directory as the script.")
             self.original_data = []
        except Exception as e:
            self.info_label.config(text="Error loading file")
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
            self.original_data = []

    def refresh_canvas(self, event=None):
        # Triggered when window resizes
        if hasattr(self, 'current_data_view'):
            self.draw_graph(self.current_data_view)

    def on_text_resize(self, event=None):
        # Debounce re-rendering of text grid to avoid freeze on drag
        if self.resize_timer is not None:
            self.root.after_cancel(self.resize_timer)
        # 300ms delay
        self.resize_timer = self.root.after(300, self.trigger_responsive_grid)

    def trigger_responsive_grid(self):
        # Only refresh if not actively sorting (prevent fighting live updates)
        if hasattr(self, 'current_data_view') and hasattr(self, 'is_sorting'):
            if not self.is_sorting and self.current_data_view:
                self.display_data(self.current_data_view)

    def draw_graph(self, data, live=False):
        # Optimized graph drawing
        self.canvas.delete("all")
        if not data:
            return
            
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        n = len(data)
        if n == 0 or w <= 1: return

        bar_color = self.colors["accent"]

        # Optimization: During live sorting, draw fewer lines to reduce lag
        resolution = 2 if live else 1 
        
        max_val = max(self.original_data) if self.original_data else 1
        
        # We can only draw ~w pixels.
        step = max(1, n / (w / resolution))
        
        # Vectorized-like drawing logic
        display_data_indices = [int(i * step) for i in range(int(min(w, n) / resolution))]
        
        for i, idx in enumerate(display_data_indices):
            if idx >= n: break
            val = data[idx] 
            
            x1 = i * resolution
            
            # y position
            bar_h = (val / max_val) * (h - 20)
            y0 = h - bar_h
            
            self.canvas.create_line(x1, h, x1, y0, fill=bar_color, width=resolution)


    def display_data(self, data):
        self.current_data_view = data 
        
        # 1. Text Update
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        if not data:
            self.text_area.insert(tk.END, "No data available.")
        else:
            formatted_lines = []
            
            # Dynamic responsiveness:
            # Calculate how many columns fit in the current window width.
            # Numbers are formatted as "{num:>8}", so 8 chars wide.
            # Consolas font average char width is roughly 8-9 pixels (depending on OS/Scaling).
            # We estimate ~75 pixels per column to be safe.
            w_pixels = self.text_area.winfo_width()
            if w_pixels > 100:
                chunk_size = max(5, int(w_pixels / 75))
            else:
                chunk_size = 12 # Default fallback if window not ready

            # Display all data as requested, regardless of size
            # note: For millions of items, this will take time to render.
            display_subset = data
            
            for i in range(0, len(display_subset), chunk_size):
                chunk = display_subset[i:i + chunk_size]
                line = "".join(f"{num:>8}" for num in chunk)
                formatted_lines.append(line)
            
            self.text_area.insert(tk.END, "\n".join(formatted_lines))
            
        self.text_area.config(state=tk.DISABLED)
        
        # 2. Graphical Update
        self.root.update_idletasks()
        self.draw_graph(data)


    def reset_data(self):
        if self.is_sorting:
            messagebox.showwarning("Busy", "Task in progress...")
            return
        
        self.load_data()
        self.time_display.config(text="0.0000s")
        self.toggle_buttons(True)
        self.progress.stop()

    def update_live_timer(self):
        if self.is_sorting:
            elapsed = time.time() - self.start_timestamp
            self.time_display.config(text=f"{elapsed:.4f}s")
            # Schedule next update in 50ms (20 FPS)
            self.root.after(50, self.update_live_timer)

    def stop_sort(self):
        if self.is_sorting:
            self.stop_requested = True
            self.info_label.config(text="Stopping...", foreground=self.colors["warning"])

    def sort_stopped(self):
        self.is_sorting = False
        self.progress.stop()
        self.info_label.config(text="Stopped", foreground=self.colors["warning"])
        self.toggle_buttons(True)
        messagebox.showinfo("Stopped", "Sorting process was stopped by user.")

    def start_sort(self, algorithm_name):
        if self.is_sorting or not self.original_data:
            return

        self.stop_requested = False
        self.is_sorting = True
        self.toggle_buttons(False)
        self.progress.start(10) # Start animation
        self.info_label.config(text=f"Running {algorithm_name}...", foreground=self.colors["warning"])
        
        # Start Live Timer
        self.start_timestamp = time.time()
        self.update_live_timer()
        
        # Start Animation Loop (60 FPS / ~16ms for smoothness, or 30ms)
        self.root.after(30, self.update_visuals_loop)
        
        data_to_sort = self.original_data.copy()
        # Reference for the visualizer
        self.current_sort_data = data_to_sort
        
        threading.Thread(target=self.run_sort_thread, args=(algorithm_name, data_to_sort), daemon=True).start()

    def update_visuals_loop(self):
        if not self.is_sorting:
            return
            
        # Determine which tab is active to optimize rendering
        current_tab = self.notebook.index("current")
        
        if current_tab == 0: # Graphical View
            # Using current_sort_data which is being modified by the thread
            self.draw_graph(self.current_sort_data, live=True)
            
        elif current_tab == 1: # Data Grid
            # Updating 20,000 text items is heavy.
            # We will throttle this or do partial updates. 
            # For "Real Time" feel, simpler is to just update it.
            # Be aware this might lag bubble sort slightly due to GIL contention,
            # but it fulfills the requirement.
            # To prevent freezing, maybe skip some updates?
            # Let's try direct update.
            pass 
            # Actually, doing full text replace every 30ms is impossible for 20k items.
            # It will freeze the app.
            # We will update text less frequently, e.g. every 500ms?
            
            # Helper to rate limit text updates
            current_time = time.time()
            if not hasattr(self, 'last_text_update'):
                self.last_text_update = 0
            
            if current_time - self.last_text_update > 0.5: # 2 FPS for text
                self.update_text_grid_live(self.current_sort_data)
                self.last_text_update = current_time

        # Schedule next update
        self.root.after(30, self.update_visuals_loop)

    def update_text_grid_live(self, data):
        # Specialized fast text update
        # Inserting 20,000 items is extremely slow in Tkinter.
        # We will only display the FIRST 200 items during live sort to prevent lag.
        # The user can see the full sorted list when finished.
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        formatted_lines = []
        chunk_size = 12 
        
        # Optimization: Only show a preview during live sort
        limit = 300 # Show first 300 items only for performance
        
        subset = data[:limit]
        
        for i in range(0, len(subset), chunk_size):
            chunk = subset[i:i + chunk_size]
            line = "".join(f"{num:>8}" for num in chunk)
            formatted_lines.append(line)
            
        self.text_area.insert(tk.END, "\n".join(formatted_lines))
        self.text_area.insert(tk.END, "\n\n... (View paused for performance, full data available after sort) ...")
        self.text_area.config(state=tk.DISABLED)

    def run_sort_thread(self, algorithm_name, data):
        start_time = time.time()
        
        if algorithm_name == "Bubble":
            self.bubble_sort(data)
        elif algorithm_name == "Insertion":
            self.insertion_sort(data)
        elif algorithm_name == "Merge":
            self.merge_sort(data)
            
        elapsed = time.time() - start_time
        
        if self.stop_requested:
            self.root.after(0, self.sort_stopped)
        else:
            self.root.after(0, lambda: self.sort_completed(algorithm_name, elapsed, data))

    def sort_completed(self, algorithm_name, elapsed, sorted_data):
        self.is_sorting = False
        self.progress.stop()
        
        self.time_display.config(text=f"{elapsed:.4f}s")
        self.info_label.config(text=f"Completed: {algorithm_name}", foreground=self.colors["success"])
        self.display_data(sorted_data)
        
        messagebox.showinfo("Success", f"{algorithm_name} completed in {elapsed:.4f} seconds.\nPlease Reset & Reload to continue.")

    def toggle_buttons(self, state):
        s = tk.NORMAL if state else tk.DISABLED
        self.btn_bubble.config(state=s)
        self.btn_insertion.config(state=s)
        self.btn_merge.config(state=s)
        self.btn_reset.config(state=tk.NORMAL) # Reset always active if desired, but here we keep logic simple
        
        # Enable Stop button ONLY when sorting (state=False)
        self.btn_stop.config(state=tk.DISABLED if state else tk.NORMAL)

    # --- Algorithms ---
    def bubble_sort(self, arr):
        n = len(arr)
        for i in range(n):
            if self.stop_requested: return
            swapped = False
            for j in range(0, n - i - 1):
                if arr[j] < arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            
            # Yield to GUI thread every outer loop iteration
            time.sleep(0.0001)
            
            if not swapped:
                break

    def insertion_sort(self, arr):
        for i in range(1, len(arr)):
            if self.stop_requested: return
            key = arr[i]
            j = i - 1
            while j >= 0 and key > arr[j]:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
            
            # Yield to GUI thread every few iterations
            if i % 5 == 0:
                time.sleep(0.0001)

    def merge_sort(self, arr):
        # In-place visualization-friendly Merge Sort
        self._merge_sort_rec(arr, 0, len(arr)-1)

    def _merge_sort_rec(self, arr, l, r):
        if self.stop_requested: return
        if l < r:
            # Yield to GUI thread slightly less often to keep recursion fast
            if (r - l) > 500: # Only yield on large chunks
                 time.sleep(0.0001)
                 
            m = (l + r) // 2
            self._merge_sort_rec(arr, l, m)
            self._merge_sort_rec(arr, m+1, r)
            self._merge(arr, l, m, r)

    def _merge(self, arr, l, m, r):
        # Merge logic that updates arr in-place
        n1 = m - l + 1
        n2 = r - m
        
        # Create temp arrays
        L = arr[l : m + 1]
        R = arr[m + 1 : r + 1]
        
        i = 0
        j = 0
        k = l
        
        while i < n1 and j < n2:
            # Change to >= for Descending Order
            if L[i] >= R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
            
        while i < n1:
            arr[k] = L[i]
            i += 1
            k += 1
            
        while j < n2:
            arr[k] = R[j]
            j += 1
            k += 1

if __name__ == "__main__":
    root = tk.Tk()
    # Try to set icon or theme if available, otherwise default
    try:
        root.tk.call("source", "azure.tcl") # Example if theme existed

        root.tk.call("set_theme", "light")
    except:
        pass
        
    app = SortingApp(root)
    root.mainloop()
