# Python Concurrency: Threads, Processes, and Beyond

Python offers multiple concurrency models, each suited to different workloads. Understanding the GIL (Global Interpreter Lock) is essential for choosing the right approach.

## The Global Interpreter Lock (GIL)

CPython's GIL prevents multiple threads from executing Python bytecode simultaneously. This means:
- **Python threads do NOT parallelize CPU-bound work** (only one thread runs at a time)
- **Python threads DO parallelize I/O-bound work** (GIL is released during I/O operations)

Python 3.13 introduced experimental no-GIL builds (PEP 703), which may enable true thread parallelism in future versions.

## Threading: For I/O-Bound Concurrency

```python
import threading
from concurrent.futures import ThreadPoolExecutor

# Low-level threading
def download(url):
    # GIL released during network I/O
    return requests.get(url).content

threads = [threading.Thread(target=download, args=(url,)) for url in urls]
for t in threads:
    t.start()
for t in threads:
    t.join()

# High-level ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download, url) for url in urls]
    results = [f.result() for f in futures]
```

Thread safety requires synchronization:
```python
lock = threading.Lock()
event = threading.Event()
semaphore = threading.Semaphore(5)  # Max 5 concurrent accesses
```

## Multiprocessing: For CPU-Bound Parallelism

`multiprocessing` bypasses the GIL by using separate Python processes:

```python
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool

# ProcessPoolExecutor (recommended high-level API)
def heavy_computation(data):
    return sum(x**2 for x in data)

with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(heavy_computation, chunks))

# Pool.map with chunksize for large iterables
with Pool(processes=8) as pool:
    results = pool.map(heavy_computation, chunks, chunksize=1000)
```

**Caution**: Inter-process communication has overhead — pickled data transferred via pipes. Keep inter-process data small; prefer shared memory (mp.shared_memory) for large arrays.

## When to Use What

| Workload | Best Choice |
|----------|-------------|
| Network I/O (many requests) | asyncio or ThreadPoolExecutor |
| File I/O | ThreadPoolExecutor (or asyncio with aiofiles) |
| CPU-bound computation | ProcessPoolExecutor |
| CPU-bound NumPy/SciPy | Threading (NumPy releases GIL) |
| Mixed I/O + CPU | asyncio + ProcessPoolExecutor |

## Shared Memory (Python 3.8+)

```python
from multiprocessing import shared_memory
import numpy as np

# Create shared memory block
shm = shared_memory.SharedMemory(create=True, size=1000000)
array = np.ndarray((100000,), dtype=np.float32, buffer=shm.buf)
array[:] = np.random.random(100000)

# Access from other processes using shm.name
# ...
shm.close()
shm.unlink()
```

## Subprocess: Running External Programs

```python
import subprocess

# Run and capture output
result = subprocess.run(
    ["ffmpeg", "-i", "input.mp4", "output.mp3"],
    capture_output=True, text=True, timeout=60, check=True
)

# Async subprocess
import asyncio
proc = await asyncio.create_subprocess_exec(
    "python", "worker.py",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
stdout, stderr = await proc.communicate()
```

## Parallelism vs Concurrency

**Concurrency**: Multiple tasks make progress by interleaving execution (asyncio, threading)
**Parallelism**: Multiple tasks execute simultaneously on multiple CPUs (multiprocessing)

High-performance systems combine both: asyncio handles thousands of concurrent I/O operations while a ProcessPoolExecutor handles CPU-intensive work in parallel workers.
