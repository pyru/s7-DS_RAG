# Python Generators and Iterators

Generators and iterators are Python's mechanism for lazy evaluation — producing values on demand rather than computing everything upfront. They enable processing of datasets too large to fit in memory.

## Iterators

An iterator is any object implementing `__iter__()` and `__next__()`:

```python
class CountUp:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for n in CountUp(0, 5):
    print(n)  # 0, 1, 2, 3, 4
```

Calling `iter()` on an iterable returns an iterator; `next()` advances it.

## Generator Functions

Generator functions use `yield` instead of `return`, automatically implementing the iterator protocol:

```python
def count_up(start, stop):
    current = start
    while current < stop:
        yield current
        current += 1

# Equivalent to CountUp class above
gen = count_up(0, 5)
print(next(gen))  # 0
print(next(gen))  # 1
```

Generator functions are **lazy**: no computation happens until `next()` is called. The function body resumes from where it last yielded.

## Generator Expressions

Like list comprehensions but lazy:

```python
# List comprehension: computes all values immediately, stores in memory
squares_list = [x**2 for x in range(1_000_000)]  # ~8MB

# Generator expression: computes on demand
squares_gen = (x**2 for x in range(1_000_000))  # ~200 bytes

# Both can be iterated the same way
total = sum(squares_gen)
```

## Infinite Sequences

Generators enable infinite sequences:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Take first 10 Fibonacci numbers
from itertools import islice
first_10 = list(islice(fibonacci(), 10))

def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1
```

## Pipeline Composition

Generators compose naturally into processing pipelines:

```python
import gzip
import csv

def read_lines(filename):
    with gzip.open(filename, 'rt') as f:
        yield from f  # yield from delegates to sub-iterator

def parse_csv(lines):
    reader = csv.DictReader(lines)
    yield from reader

def filter_active(records):
    for r in records:
        if r['status'] == 'active':
            yield r

def process_name(records):
    for r in records:
        r['name'] = r['name'].strip().title()
        yield r

# Memory-efficient pipeline — only one record in memory at a time
pipeline = process_name(filter_active(parse_csv(read_lines('large_file.csv.gz'))))
for record in pipeline:
    save_to_db(record)
```

## send() and Two-Way Communication

Generators can receive values via `send()`:

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

gen = accumulator()
next(gen)           # Prime the generator (advance to first yield)
gen.send(10)        # Returns 10
gen.send(20)        # Returns 30
gen.send(5)         # Returns 35
```

## yield from: Delegation

`yield from` delegates iteration to a sub-generator and handles `send()` / `throw()` / `close()`:

```python
def chain(*iterables):
    for it in iterables:
        yield from it

def flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))  # [1, 2, 3, 4, 5]
```

## Memory and Performance

Generators shine for:
- Large file processing (line-by-line)
- Database cursors (fetch rows in batches)
- Network streams (process chunks as they arrive)
- Infinite sequences (Fibonacci, primes, random data)

```python
# Memory-efficient processing of 10GB file
def process_large_file(path):
    with open(path) as f:
        for line in f:            # File object is itself an iterator
            yield parse(line)

# Only one line in memory at a time regardless of file size
for record in process_large_file("massive.log"):
    analyze(record)
```
