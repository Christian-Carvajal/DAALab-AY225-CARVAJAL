# Prelim Lab Work 1: Decreasing Bubble Sort

## 📋 Overview
This module implements the **Bubble Sort** algorithm designed to sort a dataset of integers in **descending order**. Unlike standard library sorts, this implementation helps visualizes the internal mechanics of the sorting process, including swap operations and pass-throughs, while measuring execution time for performance analysis.

## ⚙️ Algorithms Analysis
*   **Algorithm**: Bubble Sort
*   **Order**: Descending (Highest to Lowest)
*   **Time Complexity**: $O(n^2)$ (Average/Worst Case)
*   **Space Complexity**: $O(1)$ (In-place sorting)

## 📂 File Structure
*   `bubblesort.py`: The main Python script. It utilizes the `time` module to benchmark the sorting process.
*   `dataset.txt`: Input file containing unsorted integers (one per line).

## 🚀 How to Run
1.  Open a terminal in this directory.
2.  Ensure `dataset.txt` exists and contains data.
3.  Execute the script:
    ```bash
    python bubblesort.py
    ```

## 📊 Sample Output
The program will display the sorted array and the precise time taken to sort it.

```text
Loaded 10000 numbers from dataset.txt

Starting Bubble Sort (Descending Order)...

============================================================
RESULTS
============================================================
Total elements sorted: 10000

All sorted data (descending order):
[9999, 9998, ..., 1, 0]
Time spent: 3.425120 seconds
============================================================
```
