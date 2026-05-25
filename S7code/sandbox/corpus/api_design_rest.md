# REST API Design Principles

REST (Representational State Transfer) is an architectural style for distributed hypermedia systems, defined by Roy Fielding in his 2000 dissertation. RESTful APIs use HTTP methods and URIs to create, read, update, and delete resources.

## Core Constraints

REST is defined by six architectural constraints:

1. **Client-Server**: UI and data storage are separated, enabling independent evolution
2. **Stateless**: Each request contains all information needed to process it; no session state on server
3. **Cacheable**: Responses must define cacheability; eliminates redundant requests
4. **Uniform Interface**: Resources identified by URIs; representations manipulate resources; self-descriptive messages; HATEOAS
5. **Layered System**: Client cannot tell whether it is connected directly to the end server
6. **Code on Demand** (optional): Servers can extend client functionality by transferring executable code

## Resource Design

Design around resources (nouns), not actions (verbs):

```
GOOD:
GET    /users           → list users
POST   /users           → create user
GET    /users/{id}      → get user
PUT    /users/{id}      → replace user
PATCH  /users/{id}      → partially update user
DELETE /users/{id}      → delete user

AVOID:
POST   /getUser         → use GET /users/{id}
POST   /createUser      → use POST /users
POST   /deleteUser      → use DELETE /users/{id}
```

## HTTP Methods

| Method | Idempotent | Safe | Body | Use |
|--------|-----------|------|------|-----|
| GET | Yes | Yes | No | Retrieve resource |
| POST | No | No | Yes | Create resource |
| PUT | Yes | No | Yes | Replace resource |
| PATCH | No | No | Yes | Partial update |
| DELETE | Yes | No | No | Delete resource |

## Status Codes

Use meaningful HTTP status codes:

```
2xx Success:
  200 OK              → GET, PUT, PATCH success
  201 Created         → POST success (include Location header)
  204 No Content      → DELETE success

4xx Client Errors:
  400 Bad Request     → Malformed request body/params
  401 Unauthorized    → Missing/invalid authentication
  403 Forbidden       → Authenticated but not authorized
  404 Not Found       → Resource does not exist
  409 Conflict        → State conflict (duplicate, version mismatch)
  422 Unprocessable   → Valid syntax, invalid semantics
  429 Too Many        → Rate limit exceeded

5xx Server Errors:
  500 Internal Error  → Unexpected server failure
  503 Service Unavail → Temporary outage (include Retry-After)
```

## Versioning Strategies

**URL versioning** (most common):
```
/v1/users
/v2/users
```

**Header versioning**:
```
Accept: application/vnd.myapi.v2+json
```

**Query parameter**:
```
/users?version=2
```

URL versioning is most discoverable and easiest to test.

## Pagination

```json
GET /articles?page=2&per_page=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 247,
    "total_pages": 13
  },
  "_links": {
    "self": "/articles?page=2&per_page=20",
    "next": "/articles?page=3&per_page=20",
    "prev": "/articles?page=1&per_page=20"
  }
}
```

Cursor-based pagination scales better for real-time data:
```
GET /articles?cursor=eyJpZCI6MTIzfQ==&limit=20
```

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "message": "Must be a valid email address"},
      {"field": "age", "message": "Must be at least 18"}
    ],
    "request_id": "req_7f3a9b2c"
  }
}
```

## Security Essentials

- **HTTPS only**: Never transmit API tokens over HTTP
- **Authentication**: JWT (stateless) or opaque tokens (revocable)
- **Rate limiting**: Protect with per-IP and per-token limits (headers: X-RateLimit-*)
- **CORS**: Specify allowed origins explicitly
- **Input validation**: Validate all inputs at the boundary; reject early
