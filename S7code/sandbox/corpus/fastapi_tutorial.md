# FastAPI: Building Async Web APIs

FastAPI is a modern Python web framework for building APIs with Python type hints. It automatically generates OpenAPI documentation, validates requests using Pydantic, and achieves performance comparable to Node.js and Go through async support.

## Quick Start

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items/", status_code=201)
async def create_item(item: Item) -> Item:
    # Pydantic validates request body automatically
    # OpenAPI docs generated from type hints
    return item

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    if item_id > 1000:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "query": q}
```

## Path Parameters and Query Parameters

```python
from enum import Enum

class ModelName(str, Enum):
    gpt4 = "gpt-4"
    claude = "claude-3"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model": model_name, "capabilities": get_caps(model_name)}

# Query parameters with validation
from fastapi import Query

@app.get("/search/")
async def search(
    q: str = Query(min_length=3, max_length=100, description="Search query"),
    page: int = Query(ge=1, default=1),
    per_page: int = Query(ge=1, le=100, default=20),
):
    return {"query": q, "page": page, "per_page": per_page}
```

## Dependencies

FastAPI's dependency injection enables clean separation of concerns:

```python
from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    user = await verify_token(token.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/profile/")
async def get_profile(
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    return db.query(User).filter(User.id == current_user.id).first()
```

## Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Slow operation, run after response sent
    smtp.sendmail(email, message)

@app.post("/register/")
async def register(email: str, background_tasks: BackgroundTasks):
    user = create_user(email)
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"status": "created"}
```

## Middleware and CORS

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)

@app.middleware("http")
async def add_timing_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

## WebSockets

```python
from fastapi import WebSocket

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

## Testing FastAPI

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_item():
    response = client.post("/items/", json={"name": "Pen", "price": 1.99})
    assert response.status_code == 201
    assert response.json()["name"] == "Pen"
```
