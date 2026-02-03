# 🔬 Sorting Algorithm Stress Test - Benchmarking Tool

A comprehensive GUI-based benchmarking tool that demonstrates the performance differences between O(n²) and O(n log n) sorting algorithms.

---

## 📋 Laboratory Objectives Compliance

This tool fulfills all requirements specified in the laboratory objectives:

### ✅ Core Sorting Requirements

| Algorithm | Implementation | Complexity | Status |
|-----------|---------------|------------|--------|
| **Bubble Sort** | From scratch (no built-in sort) | O(n²) | ✅ Implemented |
| **Insertion Sort** | From scratch (no built-in sort) | O(n²) | ✅ Implemented |
| **Merge Sort** | From scratch (no built-in sort) | O(n log n) | ✅ Implemented |

> ⚠️ **Important**: No built-in library sorting functions like `.sort()` or `sorted()` are used.

### ✅ Advanced Functional Requirements

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| **Data Parsing** | Reads `generated_data.csv` file | ✅ |
| **Column Selection** | User can choose: ID, FirstName, or LastName | ✅ |
| **ID Comparison** | Integer comparison | ✅ |
| **FirstName/LastName Comparison** | String comparison (case-insensitive) | ✅ |
| **Scalability Test** | Preset buttons: 1,000 / 10,000 / 100,000 rows | ✅ |
| **Custom N Value** | User can input any custom number | ✅ |
| **Load Time Measurement** | Displays time to load CSV file | ✅ |
| **Sort Time Measurement** | Displays time to sort data | ✅ |
| **Progress Bar** | Real-time progress updates during sorting | ✅ |
| **Warning for O(n²)** | Warning dialog for large datasets with slow algorithms | ✅ |
| **First 10 Records** | Displays first 10 sorted records for verification | ✅ |
| **Total Execution Time** | Shows load time + sort time + total time | ✅ |

---

## 🚀 How to Run

### Prerequisites
- Python 3.x installed
- `generated_data.csv` file in the same directory (100,000 rows)

### Running the Application
```bash
python sorting_benchmark.py
```

---

## 🖥️ User Interface Guide

### Configuration Panel
1. **Number of Rows (N)**: 
   - Click preset buttons: `1,000` | `10,000` | `100,000`
   - Or type a custom value in the input field

2. **Sort by Column**:
   - `ID` - Integer comparison (numeric sorting)
   - `FirstName` - String comparison (alphabetical)
   - `LastName` - String comparison (alphabetical)

3. **Algorithm**:
   - `Bubble Sort` - O(n²) complexity
   - `Insertion Sort` - O(n²) complexity
   - `Merge Sort` - O(n log n) complexity

### Control Buttons
- **▶ Start Benchmark** - Begin the sorting benchmark
- **⏹ Stop** - Cancel the current operation (works immediately)
- **🗑 Clear Results** - Clear the output display

---

## 📊 Output Information

The tool displays:

### Phase 1: Data Loading
- Number of rows loaded
- Load time in seconds
- Load speed (rows/second)

### Phase 2: Sorting
- Algorithm being used
- Data type (Numeric/String)
- Estimated completion time
- Real-time progress bar

### Phase 3: Results Verification
- First 10 sorted records displayed in a table format
- Verifies sorting correctness

### Performance Summary
- 📁 File Load Time
- ⚙️ Sort Time
- ⏱️ Total Time

### Theoretical Analysis
- Dataset size (n)
- O(n²) operations count
- O(n log n) operations count
- Efficiency ratio comparison

---

## 📐 Theoretical Context

This tool demonstrates why **O(n log n)** is the standard for modern computing:

| Dataset Size | O(n²) Operations | O(n log n) Operations | Ratio |
|--------------|------------------|----------------------|-------|
| 1,000 | 1,000,000 | ~10,000 | 100x |
| 10,000 | 100,000,000 | ~133,000 | 750x |
| 100,000 | 10,000,000,000 | ~1,660,000 | 6,000x |

### 📈 Actual Benchmark Results

The following results were obtained by running this tool on the `generated_data.csv` dataset using my own computer:

#### Merge Sort - O(n log n)

| Dataset Size | File Load Time | Sort Time | Total Time |
|--------------|----------------|-----------|------------|
| **1,000** | 0.0013 sec | 0.0887 sec | 0.0900 sec |
| **10,000** | 0.0114 sec | 0.1387 sec | 0.1501 sec |
| **100,000** | 0.1097 sec | 0.7311 sec | 0.8407 sec |

#### Insertion Sort - O(n²)

| Dataset Size | File Load Time | Sort Time | Total Time |
|--------------|----------------|-----------|------------|
| **1,000** | 0.0012 sec | 0.1437 sec | 0.1449 sec |
| **10,000** | 0.0099 sec | 7.1894 sec | 7.1993 sec |
| **100,000** | 0.1070 sec | **1730.25 sec (~28.8 min)** | 1730.36 sec |

#### Bubble Sort - O(n²)

| Dataset Size | File Load Time | Sort Time | Total Time |
|--------------|----------------|-----------|------------|
| **1,000** | 0.0014 sec | 0.2424 sec | 0.2438 sec |
| **10,000** | 0.0102 sec | 18.1831 sec | 18.1932 sec |
| **100,000** | 0.1053 sec | **3935.13 sec (~65.6 min)** | 3935.24 sec |

#### Performance Comparison Summary

| Algorithm | 1,000 rows | 10,000 rows | 100,000 rows |
|-----------|------------|-------------|--------------|
| **Merge Sort** | 0.09 sec | 0.15 sec | **0.84 sec** |
| **Insertion Sort** | 0.14 sec | 7.20 sec | **~29 minutes** |
| **Bubble Sort** | 0.24 sec | 18.19 sec | **~66 minutes** |

> 💡 **Key Insight**: At 100,000 rows, Merge Sort completes in under **1 second**, while Bubble Sort takes over **1 hour**. This demonstrates why O(n log n) algorithms are essential for large-scale data processing.

---

## 🛠️ Technical Implementation

### Sorting Algorithms

**Bubble Sort** (`bubble_sort` function)
- Compares adjacent elements and swaps if in wrong order
- Optimized: stops early if no swaps occur (already sorted)
- Best case: O(n), Worst case: O(n²)

**Insertion Sort** (`insertion_sort` function)
- Builds sorted array one element at a time
- Efficient for small or nearly-sorted datasets
- Best case: O(n), Worst case: O(n²)

**Merge Sort** (`merge_sort` function)
- Divide-and-conquer approach
- Recursively splits, sorts, and merges
- Consistent O(n log n) performance

### Features
- **Lightweight GUI**: Uses tkinter (built-in, no external dependencies)
- **Threaded Execution**: Sorting runs in background thread
- **Cancel Support**: Stop button immediately halts sorting
- **Progress Tracking**: Real-time progress bar updates

---

## 📁 File Structure

```
sirval exam/
├── sorting_benchmark.py    # Main application
├── generated_data.csv      # Dataset (100,000 rows)
└── README.md               # This documentation
```

---

## 📝 CSV File Format

The `generated_data.csv` file contains:

| Column | Type | Description |
|--------|------|-------------|
| ID | Integer | Unique identifier (random 7-digit number) |
| FirstName | String | Person's first name |
| LastName | String | Person's last name |

Example:
```csv
ID,FirstName,LastName
5930868,Bruce,Shiro
5402847,John,Reeves
6697032,Austin,Dickerson
```

---

## ⚠️ Performance Warnings

The application will warn you when:
- Using **Bubble Sort** or **Insertion Sort** with **10,000+ rows**
- Estimated completion time exceeds reasonable limits

You can always click **STOP** to cancel a long-running sort operation.

---

## 🎓 Learning Outcomes

After using this tool, you will understand:

1. **Why O(n log n) matters** - The dramatic performance difference at scale
2. **Algorithm trade-offs** - When simpler algorithms are acceptable
3. **Benchmarking methodology** - Separating load time from sort time
4. **Practical complexity** - How theoretical complexity translates to real-world performance

---

## 👨‍💻 Author

Sorting Algorithm Stress Test - Benchmarking Tool  
Laboratory Exercise for Algorithm Analysis

---

## 📜 License

Educational use - Laboratory assignment submission
