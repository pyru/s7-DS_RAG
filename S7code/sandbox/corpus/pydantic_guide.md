# Pydantic: Data Validation and Settings Management

Pydantic is Python's most widely used data validation library. It uses type annotations to define data schemas and validates, coerces, and serializes data with minimal boilerplate. Pydantic v2 (2023) rewrote the core in Rust, delivering 5-50× performance improvement.

## Core Concepts

### BaseModel

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    bio: Optional[str] = None
    score: float = Field(ge=0, le=100, description="Quality score 0-100")

# Validation happens at instantiation
user = User(id=1, name="Alice", email="alice@example.com", score=95.5)

# Dict input is automatically coerced
user2 = User.model_validate({"id": "42", "name": "Bob", "email": "b@x.com", "score": 0})
# id="42" is coerced to int(42), score=0 is valid (ge=0)

print(user.model_dump())  # → {"id": 1, "name": "Alice", ...}
print(user.model_dump_json())  # → '{"id": 1, "name": "Alice", ...}'
```

### Validation Errors

```python
from pydantic import ValidationError

try:
    User(id="abc", name="Test", email="test@x.com", score=200)
except ValidationError as e:
    print(e.errors())
    # [{'type': 'int_parsing', 'loc': ('id',), 'msg': 'Input should be a valid integer', ...},
    #  {'type': 'less_than_equal', 'loc': ('score',), 'msg': 'Input should be <= 100', ...}]
```

## Field Validators

```python
from pydantic import field_validator, model_validator

class Article(BaseModel):
    title: str
    word_count: int
    tags: list[str] = []

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('tags', mode='before')
    @classmethod
    def split_tags(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(',')]
        return v
    
    @model_validator(mode='after')
    def check_consistency(self) -> 'Article':
        if self.word_count > 10000 and len(self.tags) == 0:
            raise ValueError("Long articles must have tags")
        return self
```

## Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str = "US"

class Company(BaseModel):
    name: str
    headquarters: Address
    offices: list[Address] = []

company = Company(
    name="Acme",
    headquarters={"street": "123 Main St", "city": "Springfield"},
    offices=[{"street": "456 Oak Ave", "city": "Shelbyville"}]
)
# Nested dicts are automatically coerced to Address models
```

## Settings Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    database_url: str
    debug: bool = False
    max_retries: int = 3
    
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

settings = Settings()  # Reads APP_API_KEY, APP_DATABASE_URL from env/.env
```

## JSON Schema Generation

```python
schema = User.model_json_schema()
# Generates full JSON Schema Draft 7 — useful for API documentation,
# OpenAI function calling schemas, structured output APIs
```

## Discriminated Unions

```python
from typing import Annotated, Literal
from pydantic import Discriminator, Tag

class TextMessage(BaseModel):
    type: Literal["text"] = "text"
    content: str

class ImageMessage(BaseModel):
    type: Literal["image"] = "image"
    url: str
    width: int
    height: int

Message = Annotated[TextMessage | ImageMessage, Field(discriminator="type")]

class ChatHistory(BaseModel):
    messages: list[Message]

chat = ChatHistory(messages=[
    {"type": "text", "content": "Hello"},
    {"type": "image", "url": "https://...", "width": 800, "height": 600}
])
```

## Performance Tips (v2)

- Use `model_construct()` to skip validation when data is already trusted
- Use `model_rebuild()` after forward references are resolved
- `TypeAdapter` for validating non-Model types without defining a class
