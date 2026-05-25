# Network Security Fundamentals

Network security encompasses the practices, technologies, and protocols that protect data in transit and network infrastructure from unauthorized access, attacks, and failures.

## TLS/SSL: Securing Transport

TLS (Transport Layer Security) encrypts communication between client and server via a handshake that establishes:
1. **Authentication**: Server presents a certificate signed by a trusted Certificate Authority
2. **Key exchange**: Agree on session keys without exposing them (Diffie-Hellman or ECDH)
3. **Encryption**: Symmetric encryption (AES-GCM) using derived session keys
4. **Integrity**: Message authentication codes (HMAC-SHA256) detect tampering

**TLS 1.3 improvements** (RFC 8446, 2018):
- 0-RTT (Zero Round Trip Time) resumption for returning clients
- Removed weak cipher suites (RC4, SHA-1, DES)
- Encrypted server certificate — prevents passive observer from seeing target hostname
- Perfect forward secrecy is mandatory (ephemeral DH keys)

## PKI: Certificate Infrastructure

X.509 certificates bind a public key to an identity, signed by a Certificate Authority (CA).

**Certificate chain**:
Root CA → Intermediate CA → Server Certificate

Browsers trust ~150 root CAs. A compromised root CA can sign any domain — this is why certificate transparency logs are critical.

**Let's Encrypt**: Free, automated CA. Issued 3+ billion certificates. ACME protocol enables automatic renewal via `certbot`.

## Common Attacks

### TLS Stripping / HSTS

An attacker downgrades HTTPS to HTTP, enabling eavesdropping. **HSTS** (HTTP Strict Transport Security) prevents this by instructing browsers to always use HTTPS:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### Man-in-the-Middle (MITM)

Attacker intercepts and relays communication between client and server. Prevented by:
- Certificate validation (reject invalid certs)
- Certificate pinning (embed expected cert hash in app)
- mTLS (mutual TLS — both client and server authenticate)

### SQL Injection

Unsanitized user input modifies database queries:
```sql
-- Vulnerable:
query = "SELECT * FROM users WHERE name = '" + name + "'"
# name = "'; DROP TABLE users; --" → deletes table

-- Safe (parameterized):
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```

### Cross-Site Scripting (XSS)

Injecting malicious scripts into web pages seen by other users. Prevented by:
- HTML entity encoding of user-controlled output
- Content Security Policy (CSP) headers
- HttpOnly cookies (prevent JavaScript cookie access)

### CSRF (Cross-Site Request Forgery)

Tricks authenticated users into making unintended requests. Prevented by:
- CSRF tokens in forms
- SameSite cookie attribute
- Checking Origin/Referer headers

## Authentication Best Practices

**Password storage**: Never store plaintext. Use bcrypt, scrypt, or Argon2 (memory-hard hashing algorithms that resist GPU brute force).

**Multi-factor authentication (MFA)**: Combine knowledge (password) + possession (TOTP app) + biometric.

**JWT (JSON Web Tokens)**: Stateless authentication tokens. Sign with RS256 (asymmetric) for distributed systems. Never store sensitive data in JWT payload — it's only base64-encoded, not encrypted.

## Rate Limiting and DDoS

```python
# FastAPI rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str):
    return await perform_search(q)
```

DDoS mitigation: CDN with scrubbing (Cloudflare, AWS Shield), BGP black-holing, anycast routing.

## Security Headers

Essential response headers:
```
Content-Security-Policy: default-src 'self'; script-src 'self' cdn.example.com
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```
