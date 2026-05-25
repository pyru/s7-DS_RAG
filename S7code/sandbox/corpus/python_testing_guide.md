# Python Testing with pytest

pytest is Python's most popular testing framework, known for its concise syntax, powerful fixtures, and rich plugin ecosystem. Writing good tests enables confident refactoring and catches regressions early.

## Basic Test Structure

```python
# test_calculator.py
def add(a, b):
    return a + b

def test_add_integers():
    assert add(2, 3) == 5

def test_add_floats():
    assert abs(add(1.1, 2.2) - 3.3) < 1e-10

def test_add_negative():
    assert add(-1, 1) == 0
```

Run: `pytest test_calculator.py -v`

pytest collects functions starting with `test_` in files starting with `test_` or ending with `_test.py`.

## Fixtures

Fixtures provide reusable test setup and teardown:

```python
import pytest

@pytest.fixture
def sample_user():
    """Create a user for testing."""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

@pytest.fixture
def db_connection():
    """Setup test database; teardown after test."""
    conn = create_test_db()
    yield conn          # Provide to test
    conn.close()        # Teardown after test completes
    drop_test_db()

def test_user_email(sample_user):
    assert "@" in sample_user["email"]

def test_user_creation(db_connection, sample_user):
    db_connection.insert_user(sample_user)
    retrieved = db_connection.get_user(sample_user["id"])
    assert retrieved["name"] == "Alice"
```

## Parametrize: Multiple Test Cases

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("123abc", "123ABC"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

# Generates 4 distinct test cases
```

## Testing Exceptions

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(1, 0)

def test_divide_returns_float():
    result = divide(10, 3)
    assert result == pytest.approx(3.333, rel=1e-3)
```

## Mocking with unittest.mock

```python
from unittest.mock import patch, MagicMock

def fetch_weather(city: str) -> dict:
    import httpx
    response = httpx.get(f"https://api.weather.com/{city}")
    return response.json()

def test_fetch_weather_mocked():
    mock_response = MagicMock()
    mock_response.json.return_value = {"city": "Tokyo", "temp": 24}
    
    with patch("httpx.get", return_value=mock_response) as mock_get:
        result = fetch_weather("Tokyo")
        mock_get.assert_called_once_with("https://api.weather.com/Tokyo")
    
    assert result["temp"] == 24
```

## Async Testing

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://example.com")
    assert result is not None

# Configure in pytest.ini or pyproject.toml:
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

## Coverage

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Target 80%+ coverage for production code; 100% for critical paths.

## Markers and Test Selection

```python
@pytest.mark.slow
def test_full_pipeline():
    ...

@pytest.mark.integration
def test_database_roundtrip():
    ...
```

```bash
pytest -m "not slow"        # Skip slow tests
pytest -m integration        # Run only integration tests
pytest -k "test_user"        # Run tests matching pattern
pytest --lf                  # Re-run last failed tests
```

## conftest.py: Shared Fixtures

Place shared fixtures in `conftest.py` at the test directory root — automatically discovered by pytest without imports.

## Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)
```

Hypothesis generates hundreds of test cases automatically, including edge cases.
