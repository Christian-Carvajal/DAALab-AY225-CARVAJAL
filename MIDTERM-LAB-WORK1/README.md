# Midterm Lab Work 1 - TSP Resource Optimizer

## Group Members
- **CARVAJAL, Christian Ezekiel L.**
- **CHAVEZ, Floyd**
- **SARSALIJO, John Miko**

## Description
This program is a Python-based graphical application that solves the Traveling Salesperson Problem (TSP). It calculates the optimal (shortest) continuous path to visit all given nodes and return to the starting point, optimizing for three distinct metrics based on the provided `dataset.csv`:
- **Distance (D)**
- **Time (T)**
- **Fuel (F)**

## Prerequisites & Installation
Because this program features a professional interactive Graphical User Interface (GUI) and network graphing, it relies on a few industry-standard external Python libraries. 

**You must install these packages before running the program.** Open your terminal or command prompt and run the following command to install them:

```bash
pip install pandas networkx matplotlib
```

- **`pandas`**: Essential for securely parsing and reading the data directly from `dataset.csv`.
- **`networkx`**: Powers the internal node-path routing math and handles the graph logic.
- **`matplotlib`**: Used to physically plot and render the visual node map inside the application.

## How to Run
Navigate to this directory in your terminal and execute the Python script:
```bash
python TSP.py
```
*(Alternatively, you can just click the "Run" / "Play" button if you are inside an IDE like VS Code).*

## Expected Results
Upon execution, a clean, interactive GUI window will pop up featuring:
1. **Interactive Controls**: Radio buttons at the top let you dynamically switch between optimizing for Distance (D), Time (T), or Fuel (F).
2. **Visual Network Graph**: An automated node map showing all possible routes. The chosen optimal path will be visibly highlighted with thick **red curved arrows** indicating the exact direction of travel, while non-optimal connections fade cleanly into a gray background.
3. **Explicit Text Readout**: Positioned at the bottom of the window, clearly printing out the precise consecutive optimal sequence (e.g., `1 ➔ 2 ➔ 5 ➔ 4 ➔ 3 ➔ 6 ➔ 1`) along with the exact final calculated minimum cost.
4. **Multiple Valid Routes Support**: If multiple distinct routes yield the exact same minimum cost, the program will detect this. For example, while Distance and Fuel both evaluate to 1 unique answer, **Time (T)** uncovers exactly **2 distinct optimal routes** that tie for the lowest cost (130.00). You can click the `Next Route` button at the top to toggle and visualize both correct answers immediately!


