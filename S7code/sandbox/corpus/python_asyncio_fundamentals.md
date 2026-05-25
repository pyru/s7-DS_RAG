# Python asyncio: Fundamentals and Architecture

Python's `asyncio` library provides infrastructure for writing concurrent code using the async/await syntax. Introduced in Python 3.4 and matured significantly in Python 3.11+, asyncio enables efficient I/O-bound concurrency without threads.

## The Event Loop

The **event loop** is asyncio's core scheduler. It maintains a queue of callbacks and coroutines, executing them cooperatively. Only one coroutine runs at a time (asyncio is single-threaded), but when a coroutine suspends at an `await` point, the loop picks up another ready coroutine.

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

asyncio.run(main())  # Creates and runs the event loop
```

`asyncio.run()` is the standard entry point in Python 3.7+. It creates a new event loop, runs the coroutine to completion, and closes the loop.

## Coroutines and Awaitables

A **coroutine** is a function defined with `async def`. Calling it returns a coroutine object (not a result). To execute it, you must `await` it inside another coroutine or schedule it on the event loop.

**Awaitables** include:
- Coroutines (defined with `async def`)
- Tasks (wrapping coroutines for concurrent execution)
- Futures (low-level handles for pending results)

## Concurrent Execution with Tasks

`asyncio.create_task()` schedules a coroutine to run concurrently:

```python
async def fetch_data(url):
    await asyncio.sleep(0.5)  # Simulates network I/O
    return f"data from {url}"

async def main():
    task1 = asyncio.create_task(fetch_data("url1"))
    task2 = asyncio.create_task(fetch_data("url2"))
    r1, r2 = await asyncio.gather(task1, task2)
    print(r1, r2)  # Both run concurrently, total ~0.5s not 1.0s
```

## asyncio.gather()

`asyncio.gather(*coros)` runs multiple coroutines concurrently and collects their results. It returns a list of results in the same order as the input coroutines.

## asyncio.wait() and Task Groups

`asyncio.wait()` provides more control: you can process tasks as they complete. Python 3.11 introduced `asyncio.TaskGroup` for structured concurrency:

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch("url1"))
        task2 = tg.create_task(fetch("url2"))
    # Both tasks complete before reaching here
```

TaskGroup cancels all remaining tasks if any task raises an exception — eliminating common resource-leak patterns.

## Semaphores and Rate Limiting

`asyncio.Semaphore` limits concurrent access:

```python
sem = asyncio.Semaphore(10)  # Max 10 concurrent operations

async def limited_fetch(url):
    async with sem:
        return await fetch(url)
```

## Streams: Async I/O

`asyncio.open_connection()` provides async TCP streams:

```python
async def tcp_client():
    reader, writer = await asyncio.open_connection('localhost', 8080)
    writer.write(b'hello')
    data = await reader.read(100)
    writer.close()
```

## Performance Characteristics

asyncio excels at **I/O-bound** workloads (network requests, database queries, file operations). It offers much lower overhead than threads for high-concurrency scenarios (1000+ simultaneous connections). For **CPU-bound** work, use `asyncio.run_in_executor()` with a `ProcessPoolExecutor`.

## Common Pitfalls

1. **Blocking calls** inside async functions (e.g., `time.sleep()` instead of `await asyncio.sleep()`) block the event loop entirely
2. **Forgetting await** converts a call to a coroutine object, not executing it
3. **Sharing mutable state** across tasks without synchronization (asyncio.Lock)
