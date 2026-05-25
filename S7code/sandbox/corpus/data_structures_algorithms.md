# Core Data Structures and Algorithms

Mastery of fundamental data structures and algorithms enables writing efficient, scalable software. This guide covers the essential structures every software engineer should know.

## Complexity Analysis

Big O notation describes algorithmic complexity as input size n grows:

| Complexity | Name | Example |
|-----------|------|---------|
| O(1) | Constant | Hash table lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Array scan |
| O(n log n) | Linearithmic | Merge sort |
| O(n²) | Quadratic | Bubble sort |
| O(2ⁿ) | Exponential | Recursive subsets |

Space complexity follows the same notation for memory usage.

## Arrays and Strings

**Dynamic arrays** (Python list, C++ vector): Amortized O(1) append via doubling strategy. O(n) insert/delete at arbitrary position.

**Sliding window**: O(n) technique for subarray problems
```python
def max_sum_subarray(arr, k):
    window = sum(arr[:k])
    max_sum = window
    for i in range(k, len(arr)):
        window += arr[i] - arr[i-k]
        max_sum = max(max_sum, window)
    return max_sum
```

**Two pointers**: O(n) for sorted array problems (finding pairs, removing duplicates).

## Linked Lists

**Singly linked**: O(1) prepend/insert-after; O(n) search/delete. No random access.

**Doubly linked**: O(1) insert/delete given pointer. Used in LRU cache (dict + deque).

**Fast-slow pointer** (Floyd's): Detect cycles, find midpoint in O(n) time O(1) space.

## Hash Tables

Python dict and set use hash tables: O(1) average for insert/lookup/delete.

**Collisions** handled by chaining (Python) or open addressing. Worst case O(n) with adversarial hash collisions (mitigated with random hash seeds).

## Trees

**Binary Search Tree (BST)**: O(log n) operations when balanced; O(n) worst case (degenerate).

**AVL trees / Red-Black trees**: Self-balancing; guarantee O(log n). Red-Black trees used in Java TreeMap, C++ std::map.

**B-trees**: Optimized for disk I/O; used in database indices (PostgreSQL, MySQL InnoDB).

**Tries**: Prefix trees for string operations; O(m) operations where m is string length. Used in autocomplete, spell-check.

**Heaps (Priority Queue)**:
```python
import heapq
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
min_val = heapq.heappop(heap)  # Returns 1
```
O(log n) push/pop; O(1) peek. Python's `heapq` is a min-heap.

## Graphs

**Representations**:
- Adjacency matrix: O(V²) space; O(1) edge lookup
- Adjacency list: O(V+E) space; O(degree) neighbor iteration

**BFS**: Shortest path in unweighted graphs; level-order traversal
**DFS**: Topological sort, cycle detection, connected components

**Dijkstra**: Shortest path in weighted graphs with non-negative edges; O((V+E) log V)
**Bellman-Ford**: Handles negative edges; O(VE)
**Floyd-Warshall**: All-pairs shortest paths; O(V³)

## Sorting

**Merge sort**: O(n log n) stable; O(n) extra space
**Quick sort**: O(n log n) average, O(n²) worst; O(log n) space; cache-friendly
**Heap sort**: O(n log n) worst case; O(1) space; not stable
**Timsort**: Python's default; adaptive merge sort, O(n) best case (nearly sorted)

## Dynamic Programming

Break overlapping subproblems into smaller problems, store results:

```python
# Fibonacci with memoization
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# Bottom-up tabulation
def fib_dp(n):
    dp = [0, 1]
    for i in range(2, n+1):
        dp.append(dp[-1] + dp[-2])
    return dp[n]
```

Classic DP problems: Longest Common Subsequence, 0/1 Knapsack, Coin Change, Edit Distance.
