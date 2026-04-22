# API Security Hardening: Complete Technical Reference
> Compiled by API-Expert Agent — 2026-04-22  
> Topics: OAuth 2.1, PKCE, mTLS, API Gateway Security, Rate Limiting, Abuse Prevention, Bot Detection

---

## Table of Contents
1. [OAuth 2.1 Deep Dive](#1-oauth-21-deep-dive)
2. [PKCE (Proof Key for Code Exchange)](#2-pkce-proof-key-for-code-exchange)
3. [Mutual TLS (mTLS) & Certificate-Based Auth](#3-mutual-tls-mtls--certificate-based-auth)
4. [API Gateway Security Patterns](#4-api-gateway-security-patterns)
5. [Rate Limiting Algorithms](#5-rate-limiting-algorithms)
6. [API Abuse Prevention Strategies](#6-api-abuse-prevention-strategies)
7. [Bot Detection & Mitigation](#7-bot-detection--mitigation)
8. [Zero Trust API Security](#8-zero-trust-api-security)
9. [Security Checklist & Audit Guide](#9-security-checklist--audit-guide)
10. [Emerging Threats & Countermeasures](#10-emerging-threats--countermeasures)

---

## 1. OAuth 2.1 Deep Dive

### 1.1 What is OAuth 2.1?

OAuth 2.1 (draft specification, IETF) is a consolidation and modernization of OAuth 2.0. It removes deprecated flows, strengthens security requirements, and simplifies the specification by removing dangerous legacy patterns.

### 1.2 Key Changes from OAuth 2.0

| Deprecated Feature | OAuth 2.1 Requirement | Rationale |
|-------------------|------------------------|------------|
| Implicit flow | Removed entirely | Tokens exposed in URL fragments; no refresh tokens |
| Resource Owner Password Credentials | Removed | High risk; gives app full credential access |
| `redirect_uri` wildcard | Disallowed | Must be exact match or prefix match |
| `response_type=code` without PKCE | Requires PKCE for public clients | Prevents authorization code interception |
| Fragment in redirect URIs | Prohibited | Information leakage risk |
| Bearer token in query strings | Strongly discouraged | Gets logged in server logs |
| Non-HTTPS redirect URIs | Must be HTTPS in production | Token interception on HTTP |

### 1.3 OAuth 2.1 Authorization Code Flow (with PKCE)

```
Client App                          Authorization Server              Resource Server
     |                                      |                               |
     |  1. Generate code_verifier (random)  |                               |
     |  2. Generate code_challenge (SHA256) |                               |
     |                                      |                               |
     |----------- Authorization Request ---------------->                  |
     |  ?response_type=code                                                   |
     |  &client_id=my-app                                                     |
     |  &redirect_uri=https://myapp.com/callback                              |
     |  &scope=openid profile email                                           |
     |  &state=random-state-value                                             |
     |  &code_challenge=E9Melhoa2OwvR2uz7E1fWVS25aB8JZh7iA7wmI8zA             |
     |  &code_challenge_method=S256                                           |
     |                                      |                               |
     |<---------- User Login UI ------------|                               |
     |                                      |  3. User authenticates        |
     |                                      |  4. User grants permissions   |
     |                                      |                               |
     |<---------- Redirect w/ code --------- |                               |
     |  https://myapp.com/callback          |                               |
     |  ?code=AUTH_CODE_123                 |                               |
     |  &state=random-state-value            |                               |
     |                                      |                               |
     |  5. Exchange code for tokens (POST)   |                               |
     |------------------ token endpoint ---> |                               |
     |  grant_type=authorization_code        |                               |
     |  &code=AUTH_CODE_123                  |                               |
     |  &redirect_uri=https://myapp.com/callback                            |
     |  &client_id=my-app                    |                               |
     |  &code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk         |
     |                                      |  6. Verify code_verifier      |
     |                                      |  7. Verify code_challenge     |
     |                                      |  8. Verify redirect_uri       |
     |                                      |  9. Verify client_id          |
     |                                      |                               |
     |<----------- Access Token ------------ |                               |
     |  { "access_token": "...",             |                               |
     |    "token_type": "Bearer",            |                               |
     |    "expires_in": 3600,                |                               |
     |    "refresh_token": "...",            |                               |
     |    "scope": "openid profile email" }  |                               |
     |                                      |                               |
     |  10. Call API with Bearer token ------ |------------------------------>|
     |  Authorization: Bearer <access_token> |                               |
     |                                      |  11. Validate token          |
     |                                      |  12. Check scopes            |
     |                                      |                               |
     |<----------- Protected Resource ------ |------------------------------>|
```

### 1.4 Authorization Server Implementation

```python
# Using Authlib with OAuth 2.1 compliance
from authlib.integrations.flask_oauth2 import AuthorizationServer, IntrospectionEndpoint
from authlib.oauth2.rfc7636 import PkceValidation
from authlib.oauth2.rfc6749 import Scope
from flask import Flask, request, jsonify

app = Flask(__name__)

# PKCE validation is now required by default
authorization_server = AuthorizationServer(
    app=app,
    query_client=query_client,
    save_token=save_token,
    scopes=Scope(['openid', 'profile', 'email', 'api:read', 'api:write']),
)

# Register custom validators
authorization_server.register_validator(PkceValidation())

@app.route('/.well-known/jwks.json')
def jwks():
    """Expose public keys for token verification"""
    return jsonify({
        'keys': [jwk.as_dict() for jwk in key_set.keys]
    })

# Device Authorization Flow (for CLI/smart TV apps)
@app.route('/device/code', methods=['POST'])
def device_code():
    user_code = generate_user_code()
    device_code = generate_device_code()
    
    # Store device code with 10-minute expiry
    redis.setex(
        f'device:{device_code}',
        600,  # 10 minutes
        json.dumps({
            'user_code': user_code,
            'status': 'pending',
            'client_id': request.json['client_id'],
            'scope': request.json.get('scope', 'openid')
        })
    )
    
    return jsonify({
        'device_code': device_code,
        'user_code': user_code,
        'verification_uri': 'https://auth.example.com/device',
        'verification_uri_complete': f'https://auth.example.com/device?code={user_code}',
        'interval': 5,
        'expires_in': 600
    })

@app.route('/device/token', methods=['POST'])
def device_token():
    grant_type = request.form.get('grant_type')
    if grant_type == 'urn:ietf:params:oauth:grant-type:device_code':
        device_code = request.form.get('device_code')
        device_entry = redis.get(f'device:{device_code}')
        
        if not device_entry:
            return jsonify({'error': 'expired_token'}), 400
        
        entry = json.loads(device_entry)
        if entry['status'] == 'pending':
            return jsonify({'error': 'authorization_pending'}), 400
        
        # Issue tokens
        return issue_tokens(entry['user_id'], entry['scope'])
```

### 1.5 Token Validation

```python
from jose import jwt, JWTError
from functools import wraps

ALGORITHMS = ['RS256']  # OAuth 2.1 mandates asymmetric algorithms only

def validate_token(token: str) -> dict:
    try:
        # Verify with public key from JWKS
        payload = jwt.decode(
            token,
            public_key,  # fetched from /jwks endpoint, cached
            algorithms=ALGORITHMS,
            audience='my-api',
            issuer='https://auth.example.com',
            options={
                'verify_aud': True,
                'verify_iss': True,
                'verify_exp': True,
                'verify_nbf': True,
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()

def require_scope(*required_scopes):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'missing_token'}), 401
            
            token = auth_header[7:]
            payload = validate_token(token)
            
            # Check scopes
            token_scopes = payload.get('scope', '').split()
            for scope in required_scopes:
                if scope not in token_scopes:
                    return jsonify({'error': 'insufficient_scope'}), 403
            
            request.token_payload = payload
            return f(*args, **kwargs)
        return decorated
    return decorator
```

---

## 2. PKCE (Proof Key for Code Exchange)

### 2.1 The Threat Model

PKCE (RFC 7636) protects against Authorization Code Interception Attacks:

**Attack Scenario (without PKCE):**
1. Attacker registers a malicious app with same `client_id` as victim app
2. Victim initiates OAuth flow — attacker intercepts the authorization code via:
   - HTTP referrer leakage
   - Server-side request forgery (SSRF)
   - Log files containing the redirect URL
3. Attacker exchanges the stolen code at token endpoint (no `code_verifier` needed)
4. Attacker receives tokens for victim

**Defense (with PKCE):**
- Client generates a random `code_verifier` (43-128 chars, unguessable)
- Server stores `code_challenge` = BASE64URL(SHA256(code_verifier))
- Attacker cannot exchange code without knowing `code_verifier`
- Even if attacker intercepts the code, they cannot generate the valid `code_verifier`

### 2.2 PKCE Implementation

```python
import hashlib, base64, secrets, re

def generate_code_verifier(length=64):
    """Generate a cryptographically random code_verifier (43-128 chars)"""
    if length < 43 or length > 128:
        raise ValueError("code_verifier length must be 43-128")
    # Use at least 256 bits of entropy for 43-char verifier
    minimum_entropy = 43 * 3 / 4  # ~32 bytes
    random_bytes = secrets.token_bytes(int(minimum_entropy))
    return base64url_encode(random_bytes)[:length]

def generate_code_challenge(code_verifier: str, method='S256'):
    """Generate code_challenge from code_verifier"""
    if method == 'S256':
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        return base64url_encode(digest)
    elif method == 'plain':
        return code_verifier
    else:
        raise ValueError(f"Unknown method: {method}")

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

# Client-side (mobile/web app)
code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier, 'S256')

# Store code_verifier securely (session storage, secure storage, etc.)
session['pkce_code_verifier'] = code_verifier

# Authorization request includes code_challenge
auth_url = (
    f"https://auth.example.com/authorize"
    f"?client_id={client_id}"
    f"&response_type=code"
    f"&redirect_uri={redirect_uri}"
    f"&scope={scope}"
    f"&state={state}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)
```

### 2.3 Server-Side PKCE Verification

```python
def verify_pkce(authorization_code, code_verifier, client_id):
    """
    Verify PKCE during token exchange.
    The code_verifier must match the stored code_challenge.
    """
    # Fetch stored auth code record
    code_record = db.get_auth_code(authorization_code)
    
    if not code_record:
        raise InvalidCodeError("Code not found")
    
    if code_record['client_id'] != client_id:
        raise InvalidClientError("Client mismatch")
    
    if code_record['redirect_uri'] != request.form.get('redirect_uri'):
        raise InvalidRedirectError("Redirect URI mismatch")
    
    if code_record['expires_at'] < time.time():
        raise ExpiredCodeError("Code expired")
    
    # CRITICAL: Verify code_verifier matches code_challenge
    stored_challenge = code_record['code_challenge']
    sent_challenge = generate_code_challenge(code_verifier, code_record['code_challenge_method'])
    
    if not secrets.compare_digest(stored_challenge, sent_challenge):
        raise PkceError("Invalid code_verifier")  # Generic error per RFC 7636
    
    # Invalidate code after use (one-time use)
    db.delete_auth_code(authorization_code)
    
    return code_record['user_id']
```

---

## 3. Mutual TLS (mTLS) & Certificate-Based Auth

### 3.1 How mTLS Works

In standard TLS, only the **client** verifies the **server's** certificate. In mTLS, both sides present certificates, and both sides verify each other.

```
Traditional TLS:
  Client ──── verifies ────► Server (has server cert)
  
mTLS:
  Client (has client cert) ──── verifies ────► Server (has server cert)
                    ◄───── verifies ─────────
```

### 3.2 mTLS Implementation

**Using nginx with client certificate verification:**

```nginx
# /etc/nginx/nginx.conf
server {
    listen 443 ssl;
    server_name api.example.com;

    # Server certificate
    ssl_certificate /etc/ssl/server.crt;
    ssl_certificate_key /etc/ssl/server.key;
    ssl_trusted_certificate /etc/ssl/ca.crt;

    # mTLS configuration
    ssl_client_certificate /etc/ssl/ca.crt;  # CA cert that signs client certs
    ssl_verify_client on;                     # Require client certificate
    ssl_verify_depth 2;                       # CA chain depth

    location / {
        # Verify that client cert's CN matches expected pattern
        if ($ssl_client_verify != "SUCCESS") {
            return 403;
        }
        
        # Extract client identity from certificate
        set $client_cn $ssl_client_s_dn_cn;
        set $client_serial $ssl_client_serial;
        
        # Pass to upstream
        proxy_set_header X-Client-CN $client_cn;
        proxy_set_header X-Client-Serial $client_serial;
        proxy_set_header X-Client-Verified $ssl_client_verify;
        
        proxy_pass http://backend;
    }
}
```

**Go mTLS server:**

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "net/http"
    "io/ioutil"
    "log"
)

func main() {
    // Load CA certificate to verify client certs
    caCert, err := ioutil.ReadFile("ca.crt")
    if err != nil {
        log.Fatal(err)
    }
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        ClientCAs: caCertPool,
        ClientAuth: tls.RequireAndVerifyClientCert,
        MinVersion: tls.VersionTLS 1.3,  // TLS 1.3 required for security
        CurvePreferences: []tls.CurveID{
            tls.X25519,
            tls.CurveP256,
        },
        CipherSuites: []uint16{
            tls.TLS_AES_256_GCM_SHA384,
            tls.TLS_CHACHA20_POLY1305_SHA256,
            tls.TLS_AES_128_GCM_SHA256,
        },
    }

    server := &http.Server{
        Addr:      ":8443",
        TLSConfig: tlsConfig,
        Handler:   apiHandler(),
    }
    log.Fatal(server.ListenAndServeTLS("server.crt", "server.key"))
}
```

### 3.3 Certificate-Based API Authentication

Beyond mTLS, client certificates can be used to authenticate API requests:

```python
from fastapi import Request, HTTPException
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import hashlib

@app.middleware
async def certificate_auth_middleware(request: Request, call_next):
    # Get client certificate from TLS termination
    client_cert = request.headers.get('X-Client-CN')
    cert_serial = request.headers.get('X-Client-Serial')
    
    if not client_cert:
        # Check for API key fallback
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            raise HTTPException(status_code=401, detail="No credentials provided")
        
        # Validate API key
        api_key_record = await validate_api_key(api_key)
        if not api_key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        request.state.client_id = api_key_record['client_id']
        request.state.auth_method = 'api_key'
    else:
        # mTLS authentication
        request.state.client_id = client_cert
        request.state.client_serial = cert_serial
        request.state.auth_method = 'mtls'
    
    return await call_next(request)

async def validate_api_key(api_key: str) -> dict:
    """API key stored as bcrypt hash of the key itself"""
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    return db.api_keys.find_one({'key_hash': hashed_key, 'active': True})
```

### 3.4 SPIFFE/SPIRE for Service-to-Service mTLS

SPIFFE (Secure Production Identity Framework For Everyone) provides workload identity:

```yaml
# SPIFFE Verifiable Identity Document (SVID)
issuer: spiffe://example.com/ns/workload-namespace/sa/my-service
# Automatically issued by SPIRE agent on each workload
```

```go
// golang SPIFFE mTLS
import (
    "github.com/spiffe/go-spiffe/v2/spiffeid"
    "github.com/spiffe/go-spiffe/v2/spiffetls/tlsconfig"
    "github.com/spiffe/go-spiffe/v2/workloadapi"
)

ctx := context.Background()
source, err := workloadapi.NewX509Source(ctx)
defer source.Close()

tlsConfig := tls.Config{
    MinVersion: tls.VersionTLS1.3,
    Roots: source.GetPool(),
    GetConfigForClient: tlsconfig.ConfigFromSourceMap(source, tlsconfig.Address(spiffeid.RequireIDFromString("spiffe://example.com/ns/workload-namespace/sa/my-service"))),
}
```

---

## 4. API Gateway Security Patterns

### 4.1 Gateway Architecture

```
Internet ──► WAF (Cloudflare/AWS WAF) ──► Load Balancer ──► API Gateway ──► Backend Services
                      │                                              │
                      │                                              ├── Rate Limit
                      ├── DDoS protection                            ├── Auth
                      ├── Bot management                            ├── Transform
                      └── Geo-blocking                               ├── Validate
                                                                    ├── Log
```

### 4.2 Kong API Gateway Security Config

```yaml
# Kong declarative config
_format_version: "3.0"
_services:
  - name: backend-api
    url: http://backend-cluster.internal
    routes:
      - name: api-route
        paths: ["/api/v1"]
        strip_path: false
    
    plugins:
      # Rate limiting
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
          policy: redis
          redis_host: redis.internal
          hide_client_headers: false
      
      # OAuth 2.0 / JWT validation
      - name: jwt
        config:
          uri_param_names: ["bearer"]
          header_names: ["Authorization"]
          claims_to_verify: ["exp", "iss"]
          maximum_expiration: 3600
          run_on_preflight: true
      
      # Request size limiting
      - name: request-size-limiting
        config:
          allowed_payload_size: 8  # megabytes
          size_unit: megabytes
      
      # IP restriction
      - name: ip-restriction
        config:
          allow:
            - 10.0.0.0/8
            - 172.16.0.0/12
            - 192.168.0.0/16
          deny: []
      
      # CORS
      - name: cors
        config:
          origins:
            - "https://app.example.com"
          methods:
            - GET
            - POST
            - PUT
            - DELETE
          headers:
            - Authorization
            - Content-Type
            - X-Request-ID
          exposed_headers:
            - X-RateLimit-Remaining
            - X-RateLimit-Reset
          credentials: true
          max_age: 3600
      
      # Bot detection
      - name: bot-detection
        config:
          allow: []
          deny:
            - "curl"
            - "wget"
            - "python-requests"
      
      # Response rate limiting (anti-scraping)
      - name: response-ratelimiting
        config:
          header_name: "X-RateLimit"
          limit: 1000
          window_size: 3600
```

### 4.3 AWS API Gateway Security

```python
# AWS API Gateway REST API - authorizer config
import boto3

apigateway = boto3.client('apigateway')

# Create Cognito authorizer
apigateway.create_authorizer(
    restApiId='api-id',
    name='cognito-authorizer',
    type='COGNITO_USER_POOLS',
    providerARNs=['arn:aws:cognito-idp:us-east-1:123456789:userpool/us-east-1_ABC123'],
    identitySource='method.request.header.Authorization',
    authorizerUri='arn:aws:apigateway:us-east-1:lambda:function:...',
    ttl=300
)

# Lambda authorizer for custom JWT validation
apigateway.create_authorizer(
    restApiId='api-id',
    name='jwt-lambda-authorizer',
    type='TOKEN',
    authorizerUri='arn:aws:apigateway:us-east-1:lambda:function:jwt-validator',
    identitySource='method.request.header.Authorization',
    resultTtlInSeconds=300
)
```

### 4.4 Request Validation

```python
from pydantic import BaseModel, validator, constr
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

class CreateOrderRequest(BaseModel):
    symbol: constr(min_length=1, max_length=10, regex='^[A-Z]+$')
    quantity: int = Field(gt=0, le=10000)
    side: Literal['BUY', 'SELL']
    order_type: Literal['MARKET', 'LIMIT', 'STOP']
    price: Optional[float] = Field(None, gt=0)
    
    @validator('price')
    def validate_price(cls, v, values):
        if values.get('order_type') == 'LIMIT' and v is None:
            raise ValueError('Limit orders require a price')
        return v

@app.post('/api/v1/orders')
async def create_order(req: CreateOrderRequest, authorize: Auth = Depends()):
    """Create a new order with full validation"""
    order = await order_service.create(
        user_id=authorize.user_id,
        symbol=req.symbol,
        quantity=req.quantity,
        side=req.side,
        order_type=req.order_type,
        price=req.price
    )
    return order

# Request validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            'error': 'validation_failed',
            'details': exc.errors(),
            'request_id': request.state.request_id
        }
    )
```

---

## 5. Rate Limiting Algorithms

### 5.1 Token Bucket

The most common algorithm. Tokens are added to a bucket at a fixed rate. Each request consumes a token.

**Properties:**
- Allows burst traffic up to bucket capacity
- Smooth average rate over time
- Memory-efficient (one counter per client + last_refill timestamp)

```python
from dataclasses import dataclass, field
from time import time
import redis

@dataclass
class TokenBucket:
    capacity: float        # Max tokens
    refill_rate: float     # Tokens per second
    tokens: float
    last_refill: float = field(default_factory=time)
    
    def consume(self, tokens: float = 1.0) -> bool:
        now = time()
        # Refill tokens based on elapsed time
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True  # Request allowed
        return False    # Request denied (retry after)
    
    def retry_after(self) -> float:
        if self.tokens >= 1.0:
            return 0
        tokens_needed = 1.0 - self.tokens
        return tokens_needed / self.refill_rate


class RedisTokenBucket:
    """Lua script for atomic token bucket on Redis"""
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])
    
    local data = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(data[1]) or capacity
    local last_refill = tonumber(data[2]) or now
    
    -- Refill tokens
    local elapsed = now - last_refill
    tokens = math.min(capacity, tokens + (elapsed * refill_rate))
    
    if tokens >= requested then
        tokens = tokens - requested
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        return {1, tokens, 0}  -- allowed
    else
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        local retry_after = (requested - tokens) / refill_rate
        return {0, tokens, retry_after}  -- denied
    end
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script = redis_client.register_script(self.LUA_SCRIPT)
    
    def consume(self, client_id: str, capacity: float, refill_rate: float) -> dict:
        result = self.script(
            keys=[f'token_bucket:{client_id}'],
            args=[capacity, refill_rate, time(), 1]
        )
        return {'allowed': bool(result[0]), 'remaining': result[1], 'retry_after': result[2]}
```

### 5.2 Leaky Bucket

Requests enter a queue and are processed at a fixed rate (the "leak rate"). If the queue is full, new requests are dropped.

**Properties:**
- Strict rate limiting — smooth output rate
- No burst capability
- Memory required for queue

```python
class LeakyBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # requests per second
        self.capacity = capacity
        self.queue = asyncio.Queue(maxsize=capacity)
        self.leaking = False
    
    async def leak(self):
        """Background task: process requests at fixed rate"""
        while True:
            if not self.queue.empty():
                request = await self.queue.get()
                await self.process_request(request)
            await asyncio.sleep(1.0 / self.rate)
    
    async def add(self, request: dict) -> bool:
        try:
            self.queue.put_nowait(request)
            return True
        except asyncio.QueueFull:
            return False
```

### 5.3 Sliding Window Log

More accurate than fixed windows — tracks exact timestamps of requests.

```python
from sortedcontainers import SortedList
import time

class SlidingWindowLog:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}  # client_id -> SortedList of timestamps
    
    def is_allowed(self, client_id: str) -> tuple[bool, float]:
        now = time.time()
        window_start = now - self.window_seconds
        
        if client_id not in self.clients:
            self.clients[client_id] = SortedList()
        
        timestamps = self.clients[client_id]
        
        # Remove expired timestamps
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)
        
        if len(timestamps) < self.max_requests:
            timestamps.add(now)
            return True, 0.0
        
        # Retry-after = time until oldest request expires
        retry_after = timestamps[0] - window_start
        return False, retry_after
```

### 5.4 Sliding Window Counter (Hybrid)

Combines token bucket accuracy with sliding window simplicity:

```python
class SlidingWindowCounter:
    """Two fixed windows for smoother approximation"""
    def __init__(self, redis_client, max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.window_size = window_seconds // 2  # Two half-windows
    
    def is_allowed(self, client_id: str) -> dict:
        now = time.time()
        half_window = self.window_size
        
        # Current window key (0 to half_window)
        window1_key = f'ratelimit:{client_id}:{int(now // half_window)}'
        # Previous window key
        window2_key = f'ratelimit:{client_id}:{int(now // half_window) - 1}'
        
        pipe = self.redis.pipeline()
        pipe.get(window1_key)
        pipe.get(window2_key)
        counts = pipe.execute()
        
        window1_count = int(counts[0] or 0)
        window2_count = int(counts[1] or 0)
        
        # Weighted sum based on how far into current window we are
        weight = (now % half_window) / half_window
        current_count = window1_count + window2_count * (1 - weight)
        
        if current_count < self.max_requests:
            pipe2 = self.redis.pipeline()
            pipe2.incr(window1_key)
            pipe2.expire(window1_key, self.window_seconds)
            pipe2.execute()
            return {'allowed': True, 'remaining': self.max_requests - int(current_count) - 1}
        
        return {'allowed': False, 'remaining': 0, 'retry_after': half_window - (now % half_window)}
```

---

## 6. API Abuse Prevention Strategies

### 6.1 Common Abuse Patterns

| Pattern | Indicator | Impact |
|---------|-----------|--------|
| Credential stuffing | Many logins with different creds from same IP | Account takeover |
| Scraping | Sequential access, same user-agent, high volume | Data exfiltration |
| DoS/DDoS | Traffic spike, no referral, no cookies | Service unavailability |
| API key fraud | Key reuse, key from multiple IPs | Resource theft |
| Subscription fraud | Free tier abuse, promo code abuse | Revenue loss |
| Inventory exhaustion | Rapid add-to-cart, checkout attempts | UX degradation |

### 6.2 Fraud Detection System

```python
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

class AbuseDetector:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.window = 3600  # 1 hour
    
    async def check_request(self, request: Request) -> AbuseCheckResult:
        client_ip = get_client_ip(request)
        client_id = await self.get_client_id(request)
        user_agent = request.headers.get('User-Agent', '')
        
        checks = [
            await self.check_velocity(client_ip, client_id),
            await self.check_user_agent(client_ip, user_agent),
            await self.check_geo_anomaly(client_ip, client_id),
            await self.check_api_key_reuse(client_id, client_ip),
            await self.check_pattern_anomaly(request),
        ]
        
        # Aggregate risk score
        total_score = sum(c.score for c in checks)
        max_score = sum(c.max_score for c in checks)
        normalized = total_score / max_score if max_score else 0
        
        return AbuseCheckResult(
            allowed=normalized < 0.7,
            score=normalized,
            reasons=[c.reason for c in checks if c.triggered],
            recommended_action='block' if normalized > 0.8 else 'challenge' if normalized > 0.5 else 'allow'
        )
    
    async def check_velocity(self, ip: str, client_id: str) -> CheckResult:
        key = f'velocity:{ip}:{datetime.now().hour}'
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)
        
        if count > 1000:  # 1000 req/hour/IP
            return CheckResult(triggered=True, score=0.4, max_score=0.4, reason='high_velocity_ip')
        return CheckResult(triggered=False, score=0, max_score=0.4, reason=None)
    
    async def check_user_agent(self, ip: str, ua: str) -> CheckResult:
        known_bots = ['curl', 'wget', 'python-requests', 'scrapy', 'bot', 'crawler']
        suspicious_patterns = ['sqlmap', 'nikto', 'nmap', 'masscan']
        
        ua_lower = ua.lower()
        
        for bot in known_bots:
            if bot in ua_lower:
                return CheckResult(triggered=True, score=0.3, max_score=0.3, reason=f'known_bot_ua:{bot}')
        
        for pattern in suspicious_patterns:
            if pattern in ua_lower:
                return CheckResult(triggered=True, score=0.5, max_score=0.5, reason=f'suspicious_ua:{pattern}')
        
        return CheckResult(triggered=False, score=0, max_score=0.3, reason=None)
```

### 6.3 API Key Rotation & Audit

```python
# API key rotation without downtime
class APIKeyManager:
    def __init__(self, db):
        self.db = db
    
    async def rotate_key(self, user_id: str) -> dict:
        """Create new key, old key remains valid for grace period"""
        old_key = await self.db.api_keys.find_one({'user_id': user_id, 'active': True})
        
        new_key = 'sk_' + secrets.token_urlsafe(32)
        new_key_hash = hashlib.sha256(new_key.encode()).hexdigest()
        
        await self.db.api_keys.insert_one({
            'user_id': user_id,
            'key_hash': new_key_hash,
            'active': True,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=365),
            'last_used': None,
            'previous_key_hash': old_key['key_hash'] if old_key else None,  # Grace period
            'previous_key_expires': datetime.utcnow() + timedelta(hours=24)
        })
        
        if old_key:
            # Schedule old key cleanup
            await self.schedule_key_cleanup(old_key['key_hash'])
        
        return {'key': new_key, 'grace_period_hours': 24}
    
    async def validate_key(self, api_key: str) -> Optional[dict]:
        hashed = hashlib.sha256(api_key.encode()).hexdigest()
        
        record = await self.db.api_keys.find_one({
            'key_hash': hashed,
            'active': True,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        if record:
            await self.db.api_keys.update_one(
                {'_id': record['_id']},
                {'$set': {'last_used': datetime.utcnow()}}
            )
            return record
        
        # Check grace period for rotated key
        old_record = await self.db.api_keys.find_one({
            'previous_key_hash': hashed,
            'previous_key_expires': {'$gt': datetime.utcnow()}
        })
        
        if old_record:
            return {'user_id': old_record['user_id'], 'grace_period': True}
        
        return None
```

---

## 7. Bot Detection & Mitigation

### 7.1 Detection Techniques

```python
# Multi-layer bot detection
class BotDetectionService:
    def __init__(self, config: BotDetectionConfig):
        self.config = config
    
    async def detect_bot(self, request: Request) -> BotDetectionResult:
        signals = await asyncio.gather(
            self.check_fingerprint(request),
            self.check_behavior(request),
            self.check_challenge_response(request),
            self.check_rate_pattern(request),
            return_exceptions=True
        )
        
        score = sum(s['score'] for s in signals if isinstance(s, dict) and 'score' in s)
        
        if score > 0.8:
            return BotDetectionResult(action='block', score=score)
        elif score > 0.5:
            return BotDetectionResult(action='challenge', score=score)
        else:
            return BotDetectionResult(action='allow', score=score)
    
    async def check_fingerprint(self, request: Request) -> dict:
        """Client fingerprint analysis"""
        # Canvas fingerprint
        canvas_hash = request.headers.get('X-Canvas-Fingerprint', '')
        # WebGL renderer
        webgl = request.headers.get('X-WebGL-Renderer', '')
        # Timezone
        tz = request.headers.get('X-Timezone', '')
        # Language
        lang = request.headers.get('Accept-Language', '')
        
        # Missing fingerprints are suspicious
        missing = sum(1 for x in [canvas_hash, webgl, tz, lang] if not x)
        
        if missing >= 3:
            return {'score': 0.6, 'signal': 'missing_fingerprint'}
        
        return {'score': 0, 'signal': 'normal'}
    
    async def check_behavior(self, request: Request) -> dict:
        """Behavioral analysis"""
        # Mouse movement pattern (if provided via JS SDK)
        mouse_events = request.headers.get('X-Mouse-Events', '0')
        # Scroll behavior
        scroll_depth = request.headers.get('X-Scroll-Depth', '0')
        
        if int(mouse_events) < 5 and float(scroll_depth) < 0.1:
            return {'score': 0.4, 'signal': 'no_human_behavior'}
        
        return {'score': 0, 'signal': 'normal'}
    
    async def check_rate_pattern(self, request: Request) -> dict:
        """Statistical anomaly detection"""
        client_ip = get_client_ip(request)
        path = request.url.path
        
        # Key: ip:path:minute
        key = f'bot_detect:{client_ip}:{path}:{datetime.now().minute}'
        count = self.redis.incr(key)
        self.redis.expire(key, 120)
        
        if count > 60:  # 60 req/min to same endpoint
            return {'score': 0.5, 'signal': 'rate_pattern_anomaly'}
        
        return {'score': 0, 'signal': 'normal'}
```

### 7.2 Challenge-Response (CAPTCHA Alternatives)

```python
# Proof-of-work challenge (CPU-intensive)
class ProofOfWorkChallenge:
    DIFFICULTY = 18  # Takes ~1 second on average CPU
    
    def generate_challenge(self) -> dict:
        server_seed = secrets.token_hex(16)
        difficulty = self.DIFFICULTY
        
        return {
            'challenge': server_seed,
            'difficulty': difficulty,
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
    
    def verify_solution(self, challenge: str, solution: str, difficulty: int) -> bool:
        # Check expiry
        # Verify: SHA256(challenge + solution) starts with difficulty zeros
        hash_input = hashlib.sha256(f'{challenge}{solution}'.encode()).hexdigest()
        return hash_input[:difficulty] == '0' * difficulty
```

---

## 8. Zero Trust API Security

### 8.1 Zero Trust Principles for APIs

1. **Never trust, always verify** — Every request is authenticated and authorized
2. **Least privilege access** — Minimum scopes needed for each operation
3. **Assume breach** — Log and monitor everything; limit blast radius
4. **Continuous verification** — Re-verify permissions on every call, not just at login

### 8.2 Implementation

```python
# Zero trust API middleware
class ZeroTrustMiddleware:
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
    
    async def __call__(self, request: Request, call_next):
        # 1. Identity extraction (not just authentication)
        identity = await self.extract_identity(request)
        if not identity:
            return JSONResponse(status_code=401, content={'error': 'unauthenticated'})
        
        # 2. Context gathering
        context = await self.gather_context(request, identity)
        
        # 3. Policy evaluation
        policy = await self.policy_engine.evaluate(
            subject=identity,
            action=f"{request.method}:{request.url.path}",
            resource=self.get_resource(request),
            context=context
        )
        
        if not policy.allowed:
            await self.log_denial(request, identity, context)
            return JSONResponse(status_code=403, content={'error': 'access_denied'})
        
        # 4. Continuous authorization
        if policy.requires_reauth:
            # Check if session is still valid
            await self.verify_session(identity)
        
        # 5. Add audit headers
        request.state.identity = identity
        request.state.policy = policy
        
        response = await call_next(request)
        
        # 6. Response headers for security
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'none'"
        response.headers['Permissions-Policy'] = 'accelerometer=(), camera=(), microphone=()'
        
        return response
```

---

## 9. Security Checklist & Audit Guide

### Pre-Deployment Checklist

- [ ] All endpoints require authentication (no anonymous access except health checks)
- [ ] OAuth 2.1 with PKCE for all client applications
- [ ] mTLS for all service-to-service communication
- [ ] JWT tokens use RS256 (asymmetric) — no HS256
- [ ] Token expiry: access token ≤ 1 hour, refresh token ≤ 30 days
- [ ] All secrets in vault (HashiCorp Vault, AWS Secrets Manager) — no hardcoded secrets
- [ ] Rate limiting on every endpoint (per-client and per-IP)
- [ ] Request validation on all inputs (schema + business rules)
- [ ] Response encoding: UTF-8, no JSONP, no XSS-susceptible output
- [ ] CORS configured with explicit origins only
- [ ] Security headers on all responses
- [ ] API keys hashed (bcrypt/SHA256)
- [ ] SQL injection prevention (parameterized queries)
- [ ] No sensitive data in logs (PII, tokens, passwords)
- [ ] Audit log for all auth/authz decisions

### Regular Security Audits

```bash
# OWASP ZAP API scan (CI/CD integration)
docker run -t owasp/zap2docker-stable zap-api-scan.py \
    -t https://api.example.com/openapi.json \
    -f openapi \
    -r report.html

# Secret scanning
git pre-commit hook: detect-secrets scan
gitleaks detect --source . --verbose

# Dependency vulnerability scan
npm audit --audit-level=high
pip-audit -r requirements.txt
trivy image your-api-image:latest
```

---

## 10. Emerging Threats & Countermeasures

### 10.1 API-Specific Threats (OWASP API Top 10 2023)

| Rank | Threat | Countermeasure |
|------|--------|----------------|
| API1 | Broken Object Level Authorization | Implement authorization checks on every object access |
| API2 | Broken Authentication | OAuth 2.1 + PKCE + mTLS; no API keys as sole auth |
| API3 | Broken Object Property Level Authorization | Validate which fields are returned (no data leakage) |
| API4 | Unrestricted Resource Consumption | Rate limiting + request size limits + cost controls |
| API5 | Broken Function Level Authorization | Route-level + method-level + field-level auth checks |
| API6 | Unrestricted Access to Sensitive Business Flows | Flow quotas, challenge on anomaly |
| API7 | Server-Side Request Forgery | Validate/sanitize all user-provided URLs |
| API8 | Security Misconfiguration | Hardened configs, regular config audits |
| API9 | Improper Inventory Management | API versioning, sunset policies, schema validation |
| API10 | Unsafe Consumption of APIs | Validate all third-party response data |

### 10.2 AI-Prompt Injection via API

```python
# Defend against prompt injection in AI-powered APIs
class PromptInjectionDetector:
    SUSPICIOUS_PATTERNS = [
        r'ignore (previous|all|above) (instructions?|context)',
        r'(forget|delete|overwrite) (system|your) (instructions?|prompt)',
        r'pretend you are',
        r'i am (now |just )?(a |an )?(developer|admin|system)',
        r'---\s*system\s*:',
    ]
    
    def detect(self, user_input: str) -> bool:
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        return False
```

---

*Last updated: 2026-04-22 | Version: 3.0*
