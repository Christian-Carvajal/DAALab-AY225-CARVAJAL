import time
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

def bubble_sort_descending(arr):
    """
    Sorts an array using the bubble sort algorithm in DESCENDING order.
    Optimized for performance with early exit.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Tuple of (sorted list, time taken in seconds)
    """
    start_time = time.time()
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        # Flag to optimize by detecting if array is already sorted
        swapped = False
        
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Swap if the element found is LESS than the next element (descending order)
            if arr[j] < arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no swaps occurred, array is sorted
        if not swapped:
            break
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    return arr, time_taken


def quick_sort_descending(arr):
    """
    Sorts an array using iterative quick sort (faster alternative) in DESCENDING order.
    Uses iteration instead of recursion to avoid recursion depth issues.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Tuple of (sorted list, time taken in seconds)
    """
    start_time = time.time()
    
    if len(arr) <= 1:
        return arr, time.time() - start_time
    
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] > pivot:  # For descending order
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    # Iterative quick sort using stack
    stack = [(0, len(arr) - 1)]
    
    while stack:
        low, high = stack.pop()
        if low < high:
            pi = partition(arr, low, high)
            # Push left and right partitions to stack
            stack.append((low, pi - 1))
            stack.append((pi + 1, high))
    
    end_time = time.time()
    time_taken = end_time - start_time

    return arr, time_taken


def insertion_sort_descending(arr):
    """
    Sorts an array using the insertion sort algorithm in DESCENDING order.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Tuple of (sorted list, time taken in seconds)
    """
    start_time = time.time()
    n = len(arr)
    
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        
        # Move elements that are smaller than key to one position ahead
        while j >= 0 and arr[j] < key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    return arr, time_taken


def merge_sort_descending(arr):
    """
    Sorts an array using the merge sort algorithm in DESCENDING order.
    Uses iterative approach to avoid recursion depth issues.
    
    Args:
        arr: List of comparable elements to sort
        
    Returns:
        Tuple of (sorted list, time taken in seconds)
    """
    start_time = time.time()
    n = len(arr)
    
    if n <= 1:
        return arr, time.time() - start_time
    
    # Iterative merge sort (bottom-up)
    curr_size = 1
    
    while curr_size < n:
        left = 0
        while left < n:
            mid = min(left + curr_size - 1, n - 1)
            right = min(left + 2 * curr_size - 1, n - 1)
            
            if mid < right:
                # Merge arr[left...mid] and arr[mid+1...right] in descending order
                left_arr = arr[left:mid + 1]
                right_arr = arr[mid + 1:right + 1]
                
                i = j = 0
                k = left
                
                while i < len(left_arr) and j < len(right_arr):
                    if left_arr[i] >= right_arr[j]:  # >= for descending order
                        arr[k] = left_arr[i]
                        i += 1
                    else:
                        arr[k] = right_arr[j]
                        j += 1
                    k += 1
                
                while i < len(left_arr):
                    arr[k] = left_arr[i]
                    i += 1
                    k += 1
                
                while j < len(right_arr):
                    arr[k] = right_arr[j]
                    j += 1
                    k += 1
            
            left += 2 * curr_size
        
        curr_size *= 2
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    return arr, time_taken


def load_data_from_file(filename):
    """
    Load integers from a file (one per line).
    
    Args:
        filename: Path to the file containing integers
        
    Returns:
        List of integers
    """
    try:
        with open(filename, 'r') as f:
            data = []
            for line in f:
                line = line.strip()
                if line:  # Only add non-empty lines
                    try:
                        data.append(int(line))
                    except ValueError:
                        # Skip lines that can't be converted to int
                        pass
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None


class BubbleSortGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔢 Sorting Algorithm Visualizer - Descending Order")
        self.root.geometry("1400x900")  # Larger window
        self.root.resizable(True, True)
        
        # Selected sorting algorithm
        self.selected_algorithm = tk.StringVar(value="Bubble Sort")
        
        # Color Scheme
        self.primary_color = "#1e3a8a"      # Dark Blue
        self.secondary_color = "#3b82f6"    # Bright Blue
        self.accent_color = "#10b981"       # Green
        self.danger_color = "#ef4444"       # Red
        self.success_color = "#059669"      # Dark Green
        self.bg_color = "#0f172a"           # Very Dark Blue
        self.card_bg = "#1e293b"            # Dark Slate
        self.text_color = "#f1f5f9"         # Light Text
        self.highlight_color = "#fbbf24"    # Amber
        
        self.root.configure(bg=self.bg_color)
        
        # Main Container
        main_container = tk.Frame(root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # ========== HEADER SECTION ==========
        self.create_header(main_container)
        
        # ========== MAIN CONTENT FRAME (Controls on top, Results below) ==========
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # TOP SECTION - Controls and Stats (Horizontal)
        top_section = tk.Frame(content_frame, bg=self.bg_color)
        top_section.pack(fill=tk.X, pady=(0, 15))
        
        # LEFT - Control Buttons
        buttons_frame = tk.Frame(top_section, bg=self.bg_color)
        buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        self.create_control_buttons(buttons_frame)
        
        # RIGHT - Statistics Cards
        stats_frame = tk.Frame(top_section, bg=self.bg_color)
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_stats_frame(stats_frame)
        
        # BOTTOM SECTION - Output Results (Full Width, Takes Most Space)
        output_container = tk.Frame(content_frame, bg=self.card_bg, relief=tk.FLAT)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        output_label = tk.Label(output_container, text="📊 Sorted Results", 
                               font=("Segoe UI", 14, "bold"), bg=self.card_bg, 
                               fg=self.highlight_color)
        output_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        self.output_text = scrolledtext.ScrolledText(output_container, 
                                                     font=("Courier New", 10),
                                                     bg="#0f172a", fg="#60a5fa",
                                                     insertbackground="#60a5fa",
                                                     selectbackground="#3b82f6",
                                                     selectforeground="#f1f5f9")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # ========== PROGRESS SECTION ==========
        progress_frame = tk.Frame(main_container, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.status_label = tk.Label(progress_frame, text="Ready to sort", 
                                     font=("Segoe UI", 10), bg=self.bg_color, 
                                     fg=self.accent_color)
        self.status_label.pack(anchor=tk.W, pady=(0, 6))
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 8))
        
        # ========== FOOTER SECTION ==========
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Create header with title and description"""
        header = tk.Frame(parent, bg=self.primary_color, height=100)
        header.pack(fill=tk.X, pady=(0, 0))
        
        title = tk.Label(header, text="🔢 Sorting Algorithm Visualizer", 
                        font=("Segoe UI", 22, "bold"), bg=self.primary_color, 
                        fg=self.highlight_color)
        title.pack(pady=(15, 5))
        
        subtitle = tk.Label(header, text="Choose an algorithm and sort data in descending order", 
                           font=("Segoe UI", 10), bg=self.primary_color, 
                           fg="#93c5fd")
        subtitle.pack(pady=(0, 15))
    
    def create_control_buttons(self, parent):
        """Create control buttons with modern styling"""
        button_style = {
            "font": ("Segoe UI", 13, "bold"),
            "padx": 30,
            "pady": 15,
            "border": 0,
            "relief": tk.FLAT,
            "cursor": "hand2",
            "highlightthickness": 0,
            "activeforeground": "black"
        }
        
        # Algorithm Selector
        algo_frame = tk.Frame(parent, bg=self.card_bg, relief=tk.FLAT, bd=2)
        algo_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        algo_label = tk.Label(algo_frame, text="📋 Algorithm:", 
                             font=("Segoe UI", 10, "bold"), bg=self.card_bg, 
                             fg=self.text_color)
        algo_label.pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        # Style for combobox
        style = ttk.Style()
        style.configure("TCombobox", font=("Segoe UI", 11))
        
        self.algo_combo = ttk.Combobox(algo_frame, 
                                       textvariable=self.selected_algorithm,
                                       values=["Bubble Sort", "Insertion Sort", "Merge Sort"],
                                       state="readonly",
                                       width=15,
                                       font=("Segoe UI", 11))
        self.algo_combo.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        self.algo_combo.current(0)
        
        # Start Button with background container
        start_bg_frame = tk.Frame(parent, bg="#047857", relief=tk.RAISED, bd=2)
        start_bg_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        self.sort_button = tk.Button(start_bg_frame, text="▶  START SORTING", 
                                    command=self.start_sort,
                                    bg="#047857", fg="black",
                                    activebackground="#065f46",
                                    **button_style)
        self.sort_button.pack(padx=2, pady=2)
        
        # Clear Button with background container
        clear_bg_frame = tk.Frame(parent, bg="#b91c1c", relief=tk.RAISED, bd=2)
        clear_bg_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        self.clear_button = tk.Button(clear_bg_frame, text="🗑  CLEAR", 
                                     command=self.clear_output,
                                     bg="#b91c1c", fg="black",
                                     activebackground="#7f1d1d",
                                     **button_style)
        self.clear_button.pack(padx=2, pady=2)
    
    def create_stats_frame(self, parent):
        """Create statistics display cards (horizontal layout)"""
        stats_container = tk.Frame(parent, bg=self.bg_color)
        stats_container.pack(fill=tk.BOTH, expand=True)
        
        # Title for stats
        stats_title = tk.Label(stats_container, text="📈 Statistics", 
                              font=("Segoe UI", 12, "bold"), bg=self.bg_color, 
                              fg=self.highlight_color)
        stats_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Create horizontal cards container
        cards_frame = tk.Frame(stats_container, bg=self.bg_color)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Total Numbers Card
        card1 = tk.Frame(cards_frame, bg=self.card_bg, relief=tk.FLAT, bd=1)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(card1, text="Total Numbers", font=("Segoe UI", 9), 
                bg=self.card_bg, fg="#94a3b8").pack(pady=(8, 2), padx=10, anchor=tk.W)
        self.total_label = tk.Label(card1, text="0", font=("Segoe UI", 16, "bold"), 
                                   bg=self.card_bg, fg=self.secondary_color)
        self.total_label.pack(pady=(0, 8), padx=10, anchor=tk.W)
        
        # Time Taken Card
        card2 = tk.Frame(cards_frame, bg=self.card_bg, relief=tk.FLAT, bd=1)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(card2, text="Time (seconds)", font=("Segoe UI", 9), 
                bg=self.card_bg, fg="#94a3b8").pack(pady=(8, 2), padx=10, anchor=tk.W)
        self.time_sec_label = tk.Label(card2, text="0.000", font=("Segoe UI", 16, "bold"), 
                                      bg=self.card_bg, fg=self.highlight_color)
        self.time_sec_label.pack(pady=(0, 8), padx=10, anchor=tk.W)
        
        # Time in MS Card
        card3 = tk.Frame(cards_frame, bg=self.card_bg, relief=tk.FLAT, bd=1)
        card3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(card3, text="Time (ms)", font=("Segoe UI", 9), 
                bg=self.card_bg, fg="#94a3b8").pack(pady=(8, 2), padx=10, anchor=tk.W)
        self.time_ms_label = tk.Label(card3, text="0.00", font=("Segoe UI", 16, "bold"), 
                                     bg=self.card_bg, fg="#ef4444")
        self.time_ms_label.pack(pady=(0, 8), padx=10, anchor=tk.W)
    
    def create_footer(self, parent):
        """Create footer with status information"""
        footer = tk.Frame(parent, bg=self.card_bg)
        footer.pack(fill=tk.X, padx=15, pady=15)
        
        self.footer_status = tk.Label(footer, text="✓ Ready to sort", 
                                     font=("Segoe UI", 10), bg=self.card_bg, 
                                     fg=self.accent_color)
        self.footer_status.pack(anchor=tk.W, pady=5)
        
        info_text = tk.Label(footer, text="Algorithms: Bubble Sort | Insertion Sort | Merge Sort | Order: Descending | Data Source: dataset.txt", 
                            font=("Segoe UI", 9), bg=self.card_bg, fg="#64748b")
        info_text.pack(anchor=tk.W)
    
    def start_sort(self):
        """Start sorting in a separate thread"""
        self.sort_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.algo_combo.config(state=tk.DISABLED)
        self.output_text.delete(1.0, tk.END)
        
        selected_algo = self.selected_algorithm.get()
        self.status_label.config(text=f"⏳ Loading data for {selected_algo}...", fg="#3b82f6")
        self.progress.start()
        
        # Run sorting in background thread
        thread = threading.Thread(target=self.perform_sort)
        thread.daemon = True
        thread.start()
    
    def perform_sort(self):
        """Perform the sorting operation with the selected algorithm"""
        try:
            # Load data - use script directory to find dataset.txt
            script_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_file = os.path.join(script_dir, "dataset.txt")
            data = load_data_from_file(dataset_file)
            
            if data is None:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                                f"Could not load {dataset_file}"))
                self.root.after(0, self.reset_ui)
                return
            
            count = len(data)
            selected_algo = self.selected_algorithm.get()
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text=f"🔄 Running {selected_algo} on {count} numbers...", fg="#60a5fa"))
            
            # Perform sorting based on selected algorithm
            if selected_algo == "Bubble Sort":
                sorted_data, time_taken = bubble_sort_descending(data.copy())
            elif selected_algo == "Insertion Sort":
                sorted_data, time_taken = insertion_sort_descending(data.copy())
            elif selected_algo == "Merge Sort":
                sorted_data, time_taken = merge_sort_descending(data.copy())
            else:
                sorted_data, time_taken = bubble_sort_descending(data.copy())
            
            # Display results
            self.root.after(0, lambda: self.display_results(sorted_data, time_taken, count, selected_algo))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def display_results(self, sorted_data, time_taken, count, algorithm):
        """Display sorting results in the GUI with improved formatting"""
        self.output_text.delete(1.0, tk.END)
        
        # Format results in a grid (20 numbers per row)
        result_lines = []
        numbers_per_row = 20
        
        # Add header
        result_lines.append("╔" + "═" * 103 + "╗")
        result_lines.append("║  SORTED RESULTS (Descending Order) " + " " * 67 + "║")
        result_lines.append("╠" + "═" * 103 + "╣")
        
        # Format data in rows
        for i in range(0, len(sorted_data), numbers_per_row):
            row_data = sorted_data[i:i + numbers_per_row]
            # Format each number as 5 characters wide, right-aligned
            formatted_row = "║  " + "  ".join(f"{num:5d}" for num in row_data) + "  ║"
            result_lines.append(formatted_row)
        
        result_lines.append("╠" + "═" * 103 + "╣")
        
        # Add summary section
        largest_10 = sorted_data[:10]
        smallest_10 = sorted_data[-10:]
        
        # Largest numbers
        result_lines.append("║  📊 LARGEST 10 NUMBERS:                                                                              ║")
        largest_formatted = "║  " + "  ".join(f"{num:5d}" for num in largest_10) + "  ║"
        result_lines.append(largest_formatted)
        
        result_lines.append("║  ─" * 52 + "│")
        
        # Smallest numbers
        result_lines.append("║  📊 SMALLEST 10 NUMBERS:                                                                             ║")
        smallest_formatted = "║  " + "  ".join(f"{num:5d}" for num in smallest_10) + "  ║"
        result_lines.append(smallest_formatted)
        
        result_lines.append("╠" + "═" * 103 + "╣")
        
        # Algorithm Info Section
        result_lines.append(f"║  ⏱️  ALGORITHM USED: {algorithm:<20}                                                              ║")
        result_lines.append("║  ─" * 52 + "│")
        
        time_ms = time_taken * 1000
        line = f"║  ✅ {algorithm:<15} : {time_taken:.6f}s ({time_ms:>8.2f}ms)"
        line = line + " " * (104 - len(line)) + "║"
        result_lines.append(line)
        
        result_lines.append("╠" + "═" * 103 + "╣")
        
        # Statistics
        result_lines.append(f"║  Total Numbers: {count:<6d}  |  Algorithm: {algorithm}  |  Max: {max(sorted_data):<6d}  |  Min: {min(sorted_data):<6d}  ║")
        
        result_lines.append("╚" + "═" * 103 + "╝")
        
        # Insert all formatted text
        full_text = "\n".join(result_lines)
        self.output_text.insert(tk.END, full_text)
        
        # Update stats cards
        self.total_label.config(text=str(count))
        self.time_sec_label.config(text=f"{time_taken:.6f}")
        self.time_ms_label.config(text=f"{time_taken * 1000:.2f}")
        
        # Update status
        self.status_label.config(text=f"✅ {algorithm} completed successfully!", fg=self.accent_color)
        self.footer_status.config(text=f"✓ Sort completed using {algorithm} - All data sorted in descending order", 
                                 fg=self.accent_color)
        
        self.progress.stop()
        self.reset_ui()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        self.total_label.config(text="0")
        self.time_sec_label.config(text="0.000")
        self.time_ms_label.config(text="0.00")
        self.status_label.config(text="Ready to sort", fg=self.accent_color)
        self.footer_status.config(text="✓ Ready to sort", fg=self.accent_color)
    
    def reset_ui(self):
        """Re-enable buttons after sorting"""
        self.sort_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.algo_combo.config(state="readonly")
        self.progress.stop()
        self.progress.stop()


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    gui = BubbleSortGUI(root)
    root.mainloop()