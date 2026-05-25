# Advanced asyncio Patterns in Python

This document covers production-grade patterns for building robust asynchronous applications beyond basic coroutine usage.

## Structured Concurrency with TaskGroup

Python 3.11 introduced `asyncio.TaskGroup` as the preferred pattern for managing multiple concurrent tasks. Unlike `gather()`, TaskGroup provides automatic cancellation on failure:

```python
async def process_batch(items: list[str]) -> list[Result]:
    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_item(item)) for item in items]
    return [t.result() for t in tasks]
```

If any task raises an exception, all remaining tasks are cancelled and an `ExceptionGroup` is raised. Handle it with `except*`:

```python
try:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(risky_operation())
except* ValueError as eg:
    for exc in eg.exceptions:
        print(f"ValueError: {exc}")
```

## Producer-Consumer with asyncio.Queue

`asyncio.Queue` enables decoupled producer-consumer pipelines:

```python
async def producer(queue: asyncio.Queue, items):
    for item in items:
        await queue.put(item)
    await queue.put(None)  # sentinel

async def consumer(queue: asyncio.Queue, results):
    while True:
        item = await queue.get()
        if item is None:
            break
        results.append(await process(item))
        queue.task_done()

async def pipeline(items):
    queue = asyncio.Queue(maxsize=100)
    results = []
    await asyncio.gather(
        producer(queue, items),
        consumer(queue, results),
        consumer(queue, results),  # Multiple consumers
    )
    return results
```

## Timeout and Cancellation

`asyncio.timeout()` (Python 3.11+) provides context-manager-style timeouts:

```python
async def fetch_with_timeout(url: str) -> str:
    try:
        async with asyncio.timeout(5.0):
            return await fetch(url)
    except asyncio.TimeoutError:
        return ""
```

For older Python, use `asyncio.wait_for(coro, timeout=5.0)`.

## Async Context Managers

Implement `__aenter__` and `__aexit__` for resources that require async setup/teardown:

```python
class AsyncDatabaseConnection:
    async def __aenter__(self):
        self.conn = await create_connection()
        return self.conn
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.conn.close()

async def query():
    async with AsyncDatabaseConnection() as conn:
        return await conn.execute("SELECT * FROM users")
```

## Async Generators and Streams

```python
async def read_lines(file_path: str):
    async with aiofiles.open(file_path) as f:
        async for line in f:
            yield line.strip()

async def process_file():
    async for line in read_lines("data.txt"):
        await process_line(line)
```

## Synchronization Primitives

asyncio provides thread-equivalent synchronization:

- `asyncio.Lock()` — mutual exclusion
- `asyncio.Event()` — signal between coroutines
- `asyncio.Semaphore(n)` — limit concurrent access
- `asyncio.Condition()` — wait-notify pattern

```python
lock = asyncio.Lock()

async def safe_increment():
    async with lock:
        # Critical section
        counter += 1
```

## Running Blocking Code

CPU-bound or legacy synchronous code must be offloaded:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

async def run_sync_io(path: str) -> bytes:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, open(path, "rb").read)

async def run_cpu_work(data: bytes) -> dict:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(pool, heavy_computation, data)
```

## Performance Tuning

- Use `uvloop` (Unix) for 2-4× throughput improvement: it replaces asyncio's event loop with a libuv-based implementation
- Keep coroutines short and avoid holding locks across I/O boundaries
- Profile with `asyncio.get_event_loop().set_debug(True)` to catch slow callbacks
- Use `aiohttp.ClientSession()` pooling rather than creating new sessions per request
