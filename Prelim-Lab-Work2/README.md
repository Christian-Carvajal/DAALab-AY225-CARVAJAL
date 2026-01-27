# Prelim Lab Work 2: Sorting Algorithms Visualizer

## 🖥️ Overview
A sophisticated, interactive **Graphical User Interface (GUI)** application built with Python's `tkinter`. This tool allows users to visualize and compare the performance of different sorting algorithms in real-time. It features a "Premium Industry" dark-themed design with live graphical rendering of the sorting process.

## ✨ Features
*   **Multi-Algorithm Support**:
    *   **Bubble Sort**: The classic brute-force approach.
    *   **Insertion Sort**: Builds the final sorted array one item at a time.
    *   **Merge Sort**: A highly efficient, divide-and-conquer algorithm.
*   **Interactive Visualization**: Watch the bars move and rearrange in real-time as the data is sorted.
*   **Dual Views**:
    *   **Graphical View**: Visual bar chart representation.
    *   **Data Grid**: Raw numerical data view.
*   **Performance Metrics**: Live timer measuring execution speed.
*   **Robustness**: Handles large recursion depths and provides user-friendly error messages (e.g., missing dataset files).

## 🛠️ Design & Technologies
*   **Language**: Python 3.x
*   **Library**: `tkinter` (Standard GUI), `threading` (Non-blocking UI), `ttk` (Themed widgets).
*   **Theme**: Custom "Dark Matter" industry palette (Black/Gold/White).

## 📂 Directory Structure
```
Prelim-Lab-Work2/
└── Sorting/
    ├── sorting_gui.py   # Main application entry point
    └── dataset.txt      # Data source for visualization
```

## 🚀 How to Run
To launch the visualizer, run the script from the terminal.

**Option 1: From the root directory**
```bash
python Sorting/sorting_gui.py
```

**Option 2: From the Sorting directory**
```bash
cd Sorting
python sorting_gui.py
```

## ⚠️ Notes
*   **dataset.txt**: Ensure this file is present in the `Sorting` folder. The application uses a relative path resolver to locate it automatically.
*   **Recursion Limit**: The script automatically adjusts the system recursion limit to handle deep recursion stacks required by Merge Sort on large datasets.
