# Python Type Hints and Static Analysis

Python's type hint system (PEP 484, PEP 526, and subsequent PEPs) enables static type checking in a dynamically typed language. Type hints improve code documentation, enable IDE autocompletion, and allow tools like mypy, pyright, and ruff to catch bugs before runtime.

## Basic Type Annotations

```python
# Variable annotations
name: str = "Alice"
age: int = 30
pi: float = 3.14159
active: bool = True

# Function signatures
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times
```

## Container Types

Python 3.9+ allows built-in generics directly:

```python
# Lists, dicts, sets, tuples
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Nested containers
Matrix = list[list[float]]
Config = dict[str, dict[str, str]]

# Tuples (fixed-length)
Point = tuple[float, float]
RGB = tuple[int, int, int]
```

## Optional and Union Types

```python
from typing import Optional, Union

# Pre-3.10 style
def find_user(user_id: int) -> Optional[str]:  # str | None
    return db.get(user_id)

# Python 3.10+ union syntax
def parse(value: str | int | None) -> float:
    ...
```

## Type Aliases

```python
from typing import TypeAlias

# Simple alias
Vector: TypeAlias = list[float]
Embedding: TypeAlias = list[float]
MemoryId: TypeAlias = str

# Generic alias
from typing import TypeVar
T = TypeVar('T')
```

## Callable Types

```python
from typing import Callable

# Function that takes (int, str) and returns bool
Predicate = Callable[[int, str], bool]

def filter_items(items: list[str], predicate: Callable[[str], bool]) -> list[str]:
    return [item for item in items if predicate(item)]
```

## Protocol: Structural Subtyping

`Protocol` enables duck typing with type checking:

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
    def get_bounds(self) -> tuple[int, int, int, int]: ...

def render(obj: Drawable) -> None:
    bounds = obj.get_bounds()
    obj.draw()

# Any class implementing draw() and get_bounds() satisfies Drawable
# without inheriting from it
```

## TypedDict for Structured Dicts

```python
from typing import TypedDict, NotRequired

class UserRecord(TypedDict):
    id: int
    name: str
    email: str
    avatar_url: NotRequired[str]  # Optional field

def create_user(data: UserRecord) -> None:
    ...
```

## Generics

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

s: Stack[int] = Stack()
s.push(42)  # Type-checked: must be int
```

## Literal Types

```python
from typing import Literal

Mode = Literal["read", "write", "append"]

def open_file(path: str, mode: Mode) -> None:
    ...

open_file("data.txt", "read")    # OK
open_file("data.txt", "delete")  # Type error: not in Literal
```

## Running mypy

```bash
pip install mypy
mypy src/ --strict --ignore-missing-imports
```

Common mypy settings in `pyproject.toml`:
```toml
[tool.mypy]
strict = true
python_version = "3.11"
warn_return_any = true
disallow_untyped_defs = true
```
