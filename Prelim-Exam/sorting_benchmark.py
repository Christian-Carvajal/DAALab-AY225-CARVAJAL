"""
Sorting Algorithm Stress Test - Comprehensive Benchmarking Tool
================================================================
A lightweight GUI application to benchmark sorting algorithms on large datasets.

Implements from scratch:
- Bubble Sort: O(n²)
- Insertion Sort: O(n²)  
- Merge Sort: O(n log n)

Author: Sorting Benchmark Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import time
import os
import threading
from typing import List, Tuple, Any, Callable

# ============================================================================
# SORTING ALGORITHMS (Implemented from scratch - no built-in sort functions)
# ============================================================================

def bubble_sort(arr: List[Tuple[int, Any]], key_index: int, is_numeric: bool, 
                progress_callback: Callable = None, cancel_flag: list = None) -> List[Tuple[int, Any]]:
    """
    Bubble Sort Implementation
    Time Complexity: O(n²)
    Space Complexity: O(1)
    
    Repeatedly steps through the list, compares adjacent elements,
    and swaps them if they are in the wrong order.
    """
    n = len(arr)
    result = arr.copy()
    total_comparisons = n * (n - 1) // 2
    comparison_count = 0
    last_progress = 0
    
    for i in range(n):
        # Check for cancellation at each outer loop iteration
        if cancel_flag and cancel_flag[0]:
            return result  # Return partial result
        
        swapped = False
        for j in range(0, n - i - 1):
            # Check for cancellation periodically in inner loop
            if cancel_flag and cancel_flag[0] and j % 1000 == 0:
                return result
            
            comparison_count += 1
            
            # Get values to compare
            val1 = result[j][key_index]
            val2 = result[j + 1][key_index]
            
            # Compare based on type
            if is_numeric:
                should_swap = val1 > val2
            else:
                should_swap = str(val1).lower() > str(val2).lower()
            
            if should_swap:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        
        # Progress callback (update every 1%)
        if progress_callback and total_comparisons > 0:
            progress = int((comparison_count / total_comparisons) * 100)
            if progress > last_progress:
                last_progress = progress
                progress_callback(progress, f"Bubble Sort: {progress}% complete")
        
        # Optimization: if no swaps occurred, array is sorted
        if not swapped:
            break
    
    return result


def insertion_sort(arr: List[Tuple[int, Any]], key_index: int, is_numeric: bool,
                   progress_callback: Callable = None, cancel_flag: list = None) -> List[Tuple[int, Any]]:
    """
    Insertion Sort Implementation
    Time Complexity: O(n²)
    Space Complexity: O(1)
    
    Builds the sorted array one item at a time by repeatedly
    inserting a new element into the sorted portion.
    """
    n = len(arr)
    result = arr.copy()
    last_progress = -1
    
    for i in range(1, n):
        # Check for cancellation at each iteration
        if cancel_flag and cancel_flag[0]:
            return result  # Return partial result
        
        key_item = result[i]
        key_val = key_item[key_index]
        j = i - 1
        
        while j >= 0:
            compare_val = result[j][key_index]
            
            if is_numeric:
                should_shift = compare_val > key_val
            else:
                should_shift = str(compare_val).lower() > str(key_val).lower()
            
            if should_shift:
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        
        result[j + 1] = key_item
        
        # Progress callback (throttled to avoid UI lag)
        if progress_callback:
            progress = int((i / n) * 100)
            if progress > last_progress:
                last_progress = progress
                progress_callback(progress, f"Insertion Sort: {progress}% complete")
    
    return result


def merge_sort(arr: List[Tuple[int, Any]], key_index: int, is_numeric: bool,
               progress_callback: Callable = None, cancel_flag: list = None) -> List[Tuple[int, Any]]:
    """
    Merge Sort Implementation
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    
    Divides the array into halves, recursively sorts them,
    then merges the sorted halves.
    """
    total_elements = len(arr)
    sorted_count = [0]  # Use list to allow modification in nested function
    last_progress = [-1]
    
    def merge(left: List, right: List) -> List:
        """Merge two sorted arrays into one sorted array"""
        # Check for cancellation
        if cancel_flag and cancel_flag[0]:
            return left + right
        
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            left_val = left[i][key_index]
            right_val = right[j][key_index]
            
            if is_numeric:
                should_take_left = left_val <= right_val
            else:
                should_take_left = str(left_val).lower() <= str(right_val).lower()
            
            if should_take_left:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        # Append remaining elements
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    def merge_sort_recursive(data: List) -> List:
        """Recursive merge sort implementation"""
        # Check for cancellation
        if cancel_flag and cancel_flag[0]:
            return data
        
        if len(data) <= 1:
            if len(data) == 1:
                sorted_count[0] += 1
                if progress_callback and total_elements > 0:
                    progress = int((sorted_count[0] / total_elements) * 100)
                    if progress > last_progress[0]:
                        last_progress[0] = progress
                        progress_callback(progress, f"Merge Sort: {progress}% complete")
            return data
        
        mid = len(data) // 2
        left_half = merge_sort_recursive(data[:mid])
        right_half = merge_sort_recursive(data[mid:])
        
        return merge(left_half, right_half)
    
    return merge_sort_recursive(arr.copy())


# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_csv_data(filepath: str, num_rows: int = None) -> Tuple[List[Tuple], float, List[str]]:
    """
    Load data from CSV file.
    
    Returns:
        - List of tuples (ID, FirstName, LastName)
        - Load time in seconds
        - Column headers
    """
    start_time = time.perf_counter()
    data = []
    headers = []
    
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row
        
        for i, row in enumerate(reader):
            if num_rows and i >= num_rows:
                break
            if len(row) >= 3:
                try:
                    # Convert ID to integer, keep names as strings
                    data.append((int(row[0]), row[1], row[2]))
                except ValueError:
                    continue
    
    load_time = time.perf_counter() - start_time
    return data, load_time, headers


# ============================================================================
# GUI APPLICATION
# ============================================================================

class SortingBenchmarkApp:
    """
    Lightweight GUI for Sorting Algorithm Benchmarking
    Uses tkinter for minimal resource usage on low-end devices
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sorting Algorithm Stress Test - Benchmarking Tool")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Data storage
        self.data = []
        self.headers = []
        self.is_sorting = False
        self.cancel_flag = [False]  # Mutable list so sorting threads can see changes
        # Use absolute path relative to this script's location for portability
        self.csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_data.csv")
        
        # Algorithm mapping
        self.algorithms = {
            "Bubble Sort": bubble_sort,
            "Insertion Sort": insertion_sort,
            "Merge Sort": merge_sort
        }
        
        # Column mapping
        self.column_map = {
            "ID": (0, True),           # (index, is_numeric)
            "FirstName": (1, False),
            "LastName": (2, False)
        }
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # ===== Title Section =====
        title_label = ttk.Label(
            main_frame, 
            text="🔬 Sorting Algorithm Stress Test",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # ===== Configuration Frame =====
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Row 1: Number of rows and Column selection
        ttk.Label(config_frame, text="Number of Rows (N):").grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        # Frame for preset buttons and custom input
        rows_frame = ttk.Frame(config_frame)
        rows_frame.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        self.rows_var = tk.StringVar(value="1000")
        
        # Preset buttons
        ttk.Button(rows_frame, text="1,000", width=7,
                   command=lambda: self.rows_var.set("1000")).pack(side="left", padx=(0, 3))
        ttk.Button(rows_frame, text="10,000", width=7,
                   command=lambda: self.rows_var.set("10000")).pack(side="left", padx=(0, 3))
        ttk.Button(rows_frame, text="100,000", width=7,
                   command=lambda: self.rows_var.set("100000")).pack(side="left", padx=(0, 8))
        
        # Custom input entry
        ttk.Label(rows_frame, text="Custom:").pack(side="left", padx=(0, 3))
        rows_entry = ttk.Entry(rows_frame, textvariable=self.rows_var, width=10)
        rows_entry.pack(side="left")
        
        ttk.Label(config_frame, text="Sort by Column:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.column_var = tk.StringVar(value="ID")
        column_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.column_var,
            values=["ID", "FirstName", "LastName"],
            state="readonly",
            width=15
        )
        column_combo.grid(row=0, column=3, sticky="w")
        
        # Row 2: Algorithm selection
        ttk.Label(config_frame, text="Algorithm:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        self.algo_var = tk.StringVar(value="Merge Sort")
        algo_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.algo_var,
            values=["Bubble Sort", "Insertion Sort", "Merge Sort"],
            state="readonly",
            width=15
        )
        algo_combo.grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        # Complexity label
        self.complexity_label = ttk.Label(config_frame, text="Complexity: O(n log n) ✓", foreground="green")
        self.complexity_label.grid(row=1, column=2, columnspan=2, sticky="w", padx=(20, 0), pady=(10, 0))
        algo_combo.bind('<<ComboboxSelected>>', self._update_complexity_label)
        
        # ===== Control Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.start_btn = ttk.Button(
            button_frame, 
            text="▶ Start Benchmark",
            command=self._start_benchmark
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(
            button_frame, 
            text="⏹ Stop",
            command=self._stop_benchmark,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="🗑 Clear Results",
            command=self._clear_results
        ).pack(side="left")
        
        # ===== Progress Section =====
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.status_var = tk.StringVar(value="Ready. Configure parameters and click Start.")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky="w")
        
        # ===== Results Section =====
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=4, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure text tags for formatting
        self.results_text.tag_configure("header", font=('Consolas', 10, 'bold'), foreground="blue")
        self.results_text.tag_configure("success", foreground="green")
        self.results_text.tag_configure("warning", foreground="orange")
        self.results_text.tag_configure("error", foreground="red")
        self.results_text.tag_configure("time", foreground="purple", font=('Consolas', 10, 'bold'))
        
        # ===== Footer with theoretical context =====
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        
        theory_text = "📊 Theory: Merge Sort O(n log n) vs Bubble/Insertion O(n²) | 100K rows: Merge ~seconds, Bubble ~hours"
        ttk.Label(footer_frame, text=theory_text, font=('Segoe UI', 9), foreground="gray").pack(side="left")
        
    def _update_complexity_label(self, event=None):
        """Update the complexity label based on selected algorithm"""
        algo = self.algo_var.get()
        if algo == "Merge Sort":
            self.complexity_label.config(text="Complexity: O(n log n) ✓", foreground="green")
        else:
            self.complexity_label.config(text="Complexity: O(n²) ⚠ (Slow for large N)", foreground="orange")
    
    def _log(self, message: str, tag: str = None):
        """Log a message to the results text area"""
        self.results_text.config(state="normal")
        if tag:
            self.results_text.insert(tk.END, message + "\n", tag)
        else:
            self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state="disabled")
    
    def _clear_results(self):
        """Clear the results text area"""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Results cleared. Ready for new benchmark.")
    
    def _update_progress(self, progress: int, status: str):
        """Thread-safe progress update"""
        self.root.after(0, lambda: self._do_update_progress(progress, status))
    
    def _do_update_progress(self, progress: int, status: str):
        """Actually update the progress (must run on main thread)"""
        self.progress_var.set(progress)
        self.status_var.set(status)
    
    def _start_benchmark(self):
        """Start the benchmarking process"""
        if self.is_sorting:
            return
        
        # Validate input
        try:
            num_rows = int(self.rows_var.get())
            if num_rows <= 0:
                raise ValueError("Number of rows must be positive")
            if num_rows > 100000:
                num_rows = 100000
                self.rows_var.set("100000")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter a valid number of rows.\n{e}")
            return
        
        algo_name = self.algo_var.get()
        column_name = self.column_var.get()
        
        # Warning for O(n²) algorithms with large datasets
        if algo_name in ["Bubble Sort", "Insertion Sort"] and num_rows >= 10000:
            estimated_time = self._estimate_time(algo_name, num_rows)
            result = messagebox.askquestion(
                "Performance Warning",
                f"⚠ Warning: {algo_name} has O(n²) complexity.\n\n"
                f"Sorting {num_rows:,} rows may take approximately {estimated_time}.\n\n"
                f"For large datasets, Merge Sort O(n log n) is recommended.\n\n"
                f"Do you want to continue?",
                icon='warning'
            )
            if result != 'yes':
                return
        
        # Start sorting in a separate thread
        self.is_sorting = True
        self.cancel_flag[0] = False  # Reset cancel flag
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        thread = threading.Thread(
            target=self._run_benchmark,
            args=(num_rows, algo_name, column_name),
            daemon=True
        )
        thread.start()
    
    def _estimate_time(self, algo_name: str, n: int) -> str:
        """Estimate sorting time for user warning"""
        import math
        # Empirical estimates based on typical Python performance
        if algo_name == "Bubble Sort":
            # Bubble sort is very slow - ~1.5e-7 seconds per comparison
            seconds = (n * n) * 1.5e-7
        elif algo_name == "Insertion Sort":
            # Insertion sort is faster than bubble - ~8e-8 seconds per comparison
            seconds = (n * n) * 8e-8
        else:
            # Merge sort - ~5e-7 seconds per n*log(n) operation
            seconds = (n * math.log2(max(n, 2))) * 5e-7
        
        if seconds < 1:
            return f"{seconds*1000:.0f} milliseconds"
        elif seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"
    
    def _get_lag_warning(self, algo_name: str, n: int) -> str:
        """Get warning message about potential lag"""
        import math
        if algo_name == "Bubble Sort" and n >= 5000:
            return f"\n\n⚠️ WARNING: This may cause UI lag. Estimated time: {self._estimate_time(algo_name, n)}\nYou can click STOP to cancel at any time."
        elif algo_name == "Insertion Sort" and n >= 10000:
            return f"\n\n⚠️ WARNING: This may cause slight UI lag. Estimated time: {self._estimate_time(algo_name, n)}\nYou can click STOP to cancel at any time."
        return ""
    
    def _run_benchmark(self, num_rows: int, algo_name: str, column_name: str):
        """Run the benchmark (executed in separate thread)"""
        try:
            # Clear previous results
            self.root.after(0, self._clear_results)
            
            self._log("=" * 60, "header")
            self._log(f"  SORTING ALGORITHM BENCHMARK", "header")
            self._log("=" * 60, "header")
            self._log("")
            self._log(f"Configuration:")
            self._log(f"  • Algorithm: {algo_name}")
            self._log(f"  • Rows to sort: {num_rows:,}")
            self._log(f"  • Sort column: {column_name}")
            self._log("")
            
            # Load data
            self._update_progress(0, "Loading CSV data...")
            self._log("─" * 40)
            self._log("PHASE 1: DATA LOADING", "header")
            self._log("─" * 40)
            
            load_start = time.perf_counter()
            self.data, load_time, self.headers = load_csv_data(self.csv_path, num_rows)
            actual_rows = len(self.data)
            
            self._log(f"  ✓ Loaded {actual_rows:,} rows in {load_time:.4f} seconds", "success")
            self._log(f"  ✓ Load speed: {actual_rows/load_time:,.0f} rows/second", "success")
            self._log("")
            
            # Check if cancelled during loading
            if self.cancel_flag[0]:
                self._log("⏹ Benchmark stopped by user.", "warning")
                return
            
            # Get column info
            col_index, is_numeric = self.column_map[column_name]
            
            # Sorting phase
            self._log("─" * 40)
            self._log("PHASE 2: SORTING", "header")
            self._log("─" * 40)
            self._log(f"  Starting {algo_name}...")
            self._log(f"  Data type: {'Numeric (Integer)' if is_numeric else 'String (Lexicographic)'}")
            self._log(f"  Estimated time: {self._estimate_time(algo_name, actual_rows)}")
            self._log("  (Click STOP button to cancel at any time)")
            self._log("")
            
            sort_func = self.algorithms[algo_name]
            
            sort_start = time.perf_counter()
            sorted_data = sort_func(
                self.data, 
                col_index, 
                is_numeric,
                progress_callback=self._update_progress,
                cancel_flag=self.cancel_flag
            )
            sort_time = time.perf_counter() - sort_start
            
            # Check if cancelled during sorting
            if self.cancel_flag[0]:
                self._log(f"⏹ Sorting stopped by user after {sort_time:.2f} seconds.", "warning")
                self._log("  Ready to start a new benchmark.", "warning")
                return
            
            self._update_progress(100, "Sorting complete!")
            
            self._log(f"  ✓ Sorting completed in {sort_time:.4f} seconds", "success")
            if sort_time > 0:
                self._log(f"  ✓ Sort speed: {actual_rows/sort_time:,.0f} rows/second", "success")
            self._log("")
            
            # Display results
            self._log("─" * 40)
            self._log("PHASE 3: RESULTS VERIFICATION", "header")
            self._log("─" * 40)
            self._log(f"First 10 sorted records (sorted by {column_name}):")
            self._log("")
            
            # Table header
            self._log(f"  {'#':<4} {'ID':<12} {'FirstName':<15} {'LastName':<15}")
            self._log(f"  {'-'*4} {'-'*12} {'-'*15} {'-'*15}")
            
            # Display first 10 records
            for i, record in enumerate(sorted_data[:10], 1):
                self._log(f"  {i:<4} {record[0]:<12} {record[1]:<15} {record[2]:<15}")
            
            self._log("")
            
            # Performance summary
            total_time = load_time + sort_time
            self._log("=" * 60, "header")
            self._log("  PERFORMANCE SUMMARY", "header")
            self._log("=" * 60, "header")
            self._log("")
            self._log(f"  📁 File Load Time:    {load_time:.4f} seconds", "time")
            self._log(f"  ⚙️  Sort Time:         {sort_time:.4f} seconds", "time")
            self._log(f"  ⏱️  Total Time:        {total_time:.4f} seconds", "time")
            self._log("")
            
            # Theoretical analysis
            import math
            self._log("─" * 40)
            self._log("THEORETICAL ANALYSIS", "header")
            self._log("─" * 40)
            
            n = actual_rows
            n_squared = n * n
            n_log_n = n * math.log2(n) if n > 0 else 0
            
            self._log(f"  Dataset size (n):     {n:,}")
            self._log(f"  O(n²) operations:     {n_squared:,}")
            self._log(f"  O(n log n) operations: {n_log_n:,.0f}")
            self._log(f"  Efficiency ratio:     {n_squared/n_log_n:.1f}x more ops for O(n²)" if n_log_n > 0 else "")
            self._log("")
            
            if algo_name == "Merge Sort":
                self._log("  ✓ Merge Sort is optimal for large datasets!", "success")
            else:
                self._log(f"  ⚠ For comparison: Merge Sort would be ~{n_squared/n_log_n:.0f}x faster", "warning")
            
            self._log("")
            self._log("=" * 60)
            self._log("  Benchmark completed successfully! ✓", "success")
            self._log("=" * 60)
            
        except FileNotFoundError:
            self._log(f"Error: Could not find file '{self.csv_path}'", "error")
            self._log("Please ensure 'generated_data.csv' is in the same directory.", "error")
        except Exception as e:
            self._log(f"Error: {str(e)}", "error")
        finally:
            self.root.after(0, self._finish_benchmark)
    
    def _stop_benchmark(self):
        """Stop the current benchmark immediately"""
        self.cancel_flag[0] = True  # Signal sorting algorithms to stop
        self.is_sorting = False
        self.status_var.set("⏹ Stopping... Please wait.")
    
    def _finish_benchmark(self):
        """Clean up after benchmark completes"""
        self.is_sorting = False
        self.cancel_flag[0] = False  # Reset for next run
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        if self.progress_var.get() >= 100:
            self.status_var.set("✓ Benchmark complete! See results below.")
        elif self.progress_var.get() > 0:
            self.status_var.set("⏹ Stopped. Ready to start a new benchmark.")
        else:
            self.status_var.set("Ready. Configure parameters and click Start.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    
    # Set application icon and style
    try:
        root.iconbitmap(default='')  # Use default icon
    except:
        pass
    
    # Configure ttk style for a clean look
    style = ttk.Style()
    try:
        style.theme_use('vista')  # Use modern theme on Windows
    except:
        try:
            style.theme_use('clam')  # Fallback theme
        except:
            pass
    
    # Create and run the application
    app = SortingBenchmarkApp(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
