# Authentication & Authorization Deep Research

Date: 2026-04-22
Agent: api-expert / ap-b2

## 1. JWT (JSON Web Tokens)

### Structure
A JWT has three parts separated by dots (.):
- **Header**: Algorithm and token type (typically HS256 or RS256)
- **Payload**: Claims (registered, public, private)
- **Signature**: Verification signature using header-specified algorithm

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Algorithms
- **HS256**: Symmetric — same key for signing and verification. Fast, good for internal services.
- **RS256**: Asymmetric (RSA) — private key signs, public key verifies. Good for distributed systems, SSO.
- **ES256**: Elliptic curve — similar security to RS256 with smaller key sizes.
- **none**: DANGER — algorithm "none" should be rejected by all implementations.

### JWT Security Concerns
- **Don't store sensitive data in payload**: JWT is base64-encoded, not encrypted. Anyone can read it.
- **Short-lived tokens**: Access tokens should be short (minutes to 1 hour). Use refresh tokens for longer sessions.
- **Store securely**: HttpOnly cookies for browser storage. Not localStorage (XSS vulnerable).
- **Validate all claims**: issuer, audience, expiration, notBefore, algorithm
- **Refresh token rotation**: Each use of refresh token issues a new refresh token (prevents replay attacks)

### Refresh Token Strategy
```
Access Token: 15-60 min lifetime, stored in memory
Refresh Token: 24 hours to 2 weeks, stored in HttpOnly cookie/secure storage
Rotation: Every refresh generates new refresh token, old one invalidated
```
- Reduces exposure window: if access token stolen, limited lifetime
- Rotation means stolen refresh tokens can be detected (old one no longer valid)

### JWT Best Practices
1. Always verify signature with expected algorithm (don't trust JWT header alg field)
2. Validate expiration (exp), issued at (iat), not before (nbf)
3. Validate audience (aud) if your API is multi-tenant
4. Validate issuer (iss) if you support multiple issuers
5. Use RS256 for cross-service/federated auth, HS256 for internal services
6. Set appropriate claim types (jti for token ID, useful for revocation)
7. Include enough claims but avoid bloat (token size affects every request)
8. Don't store tokens in localStorage or sessionStorage

## 2. OAuth 2.0 Deep Dive

### Grant Types

#### Authorization Code (Best for Server-Side Apps)
- User authenticates with authorization server
- Auth server redirects to client with authorization code
- Client exchanges code for tokens (server-side, secrets never exposed to browser)
- PKCE (Proof Key for Code Exchange) adds security for public clients

#### Authorization Code + PKCE (All Clients)
PKCE adds two parameters:
- **code_verifier**: random cryptographically secure string (43-128 chars)
- **code_challenge**: BASE64URL(SHA256(code_verifier))
- Auth request includes code_challenge and code_challenge_method
- Token exchange includes code_verifier, server recalculates and matches

#### Implicit Flow (DEPRECATED)
- Tokens returned directly in redirect URL fragment
- Security issues: tokens in browser history, no client secret verification
- Replaced by Authorization Code + PKCE

#### Client Credentials (Service-to-Service)
- No user involvement
- Client authenticates with client_id + client_secret
- Gets access token for API access
- Use for: backend jobs, cron tasks, BFF services

#### Device Authorization Grant (Smart TVs, CLIs)
- User visits URL on phone/computer with code
- Device polls authorization server for completion
- Good for: CLI tools, smart TV apps, limited-input devices

#### Resource Owner Password Credentials (DEPRECATED)
- User gives credentials directly to app
- App exchanges for access token
- Bad: credentials stored or transmitted, no MFA, no consent

### OAuth 2.0 Security Best Practices
1. Use PKCE for all public clients (SPA, mobile)
2. Validate redirect_uri exactly — don't allow open redirectors
3. Use state parameter to prevent CSRF on authorization callback
4. Keep client_secret server-side only (not in browser code)
5. Use short-lived tokens, rotate refresh tokens
6. Scope restrict tokens: only the permissions the client actually needs
7. Validate tokens on every API request, not just at gateway
8. Implement token revocation endpoint

### Scope Design
```
openid profile email          # Standard OIDC scopes
read:orders write:orders      # Resource-action format
urn:myapp:read:data           # URN format for custom scopes
```

### Token Introspection (RFC 7662)
For opaque tokens, resource servers can introspect:
```
POST /oauth/introspect
token=abc123
```
Returns: active, scope, client_id, exp, iat

## 3. OpenID Connect (OIDC)

### OIDC is OAuth 2.0 + Identity
OAuth 2.0 provides authorization. OIDC adds authentication and identity layer.

### ID Token
OIDC introduces the ID token — a JWT containing:
- Standard JWT claims (sub, iss, aud, exp, iat)
- OIDC-specific: nonce, auth_time, acr, amr
- User profile claims: name, email, picture, preferred_username

### Discovery Document
```json
GET /.well-known/openid-configuration
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "...",
  "token_endpoint": "...",
  "userinfo_endpoint": "...",
  "jwks_uri": "...",
  "scopes_supported": ["openid", "profile", "email"],
  "response_types_supported": ["code", "code id_token"],
  "id_token_signing_alg_values_supported": ["RS256"]
}
```

### JWKS (JSON Web Key Set)
Authorization server publishes public keys for JWT verification:
```json
GET /jwks
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "key-id-123",
      "use": "sig",
      "alg": "RS256",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

### Hybrid Flow
Combines authorization code with ID token in the response:
- **code id_token**: authorization code + ID token (for quick UI rendering)
- **code token**: authorization code + access token
- **code id_token token**: all three

### Authentication Context Class Reference (ACR)
- Defines the authentication method used (password, MFA, hardware key)
- Values: ial1 (identity proofing), ial2 (evidence verification), ial3 (biometric/physical)
- eKYC/identity verification providers map to IAL levels

### Authentication Methods Reference (AMR)
- How the user authenticated (pwd, mfa, swk, hwk, otp, swl)
- Stored in ID token, useful for risk assessment

## 4. WebAuthn / FIDO2 / Passkeys

### What is WebAuthn?
W3C standard for passwordless authentication using public-key cryptography. Replaces passwords with:
- Platform authenticators (Touch ID, Face ID, Windows Hello, Android biometric)
- Security keys (YubiKey, Google Titan, Feitian)

### How It Works

#### Registration
1. User initiates registration
2. Server sends challenge + relying party info (RP ID, name, origins)
3. Browser creates credential (public/private key pair) on authenticator
4. Private key stored on authenticator, public key sent to server
5. Server stores public key + credential ID linked to user account

#### Authentication
1. User initiates login, server sends challenge
2. Browser asks authenticator to sign challenge
3. Authenticator uses stored private key (user verifies with biometric/PIN first)
4. Signed assertion sent to server, verified with stored public key

### Passkeys
Passkeys are WebAuthn credentials managed by platform ecosystems:
- **Apple Passkeys**: iCloud Keychain, synced across devices
- **Google Password Manager**: synced via Google account
- **1Password / Bitwarden**: third-party credential managers
- FIDO1 migration: Some passkeys stored by password managers

### WebAuthn Levels
- **Level 1**: Core functionality (username-less, discoverable credentials)
- **Level 2**: Additional features (authenticator attestation, credential properties)
- **Level 3**: Enhanced features (enterprise attestation, alternative sources)

### Assertion Response Structure
```json
{
  "credentialId": "base64-encoded-id",
  "authenticatorData": "RP ID hash, counter, flags...",
  "clientDataJSON": "challenge, origin, type...",
  "signature": "sign(authenticatorData + SHA256(clientDataJSON))"
}
```

### Security Benefits
- Phishing-resistant: credentials bound to RP ID (exact domain)
- No shared secrets: server stores only public key, not password hashes
- No replay: authenticator counters detect cloned credentials
- Breach-resistant: even if all public keys stolen, accounts can't be accessed without physical authenticator

### UX Considerations
- Auto-fill: browsers can auto-fill passkeys after password field (WebAuthn conditional UI)
- Cross-device flow: phone as authenticator for desktop logins (QR code or Bluetooth)
- Backup/sync: critical for consumer apps, less critical for enterprise

## 5. API Key Management

### Types of API Keys
- **User-level keys**: Associated with a specific user, inherits their permissions
- **Service-level keys**: Associated with a service/client application, not a user
- **Team/project keys**: Scoped to a team or project for billing/tracking

### Key Generation
- Use cryptographically secure random (256-bit minimum)
- Store hash, not plaintext (like passwords)
- Format: key prefix + random body (e.g., `sk_live_` + 32 bytes base62)
- Prefix allows identification without exposing key value

### Key Rotation
- Support multiple active keys per user (for rotation without downtime)
- Key metadata: created date, last used, scopes, environments
- Automatic rotation for high-security contexts

### API Key Security
- Transmit over TLS only
- Store in hashed form (like bcrypt or Argon2)
- Log key usage for audit trail
- Rate limit per key to prevent abuse
- Revocation: immediate or with grace period

### Scoping and Permissions
```
read:data                   # Read-only access
write:data                  # Read-write access
admin:users                 # User management
billing:read                # Billing data access
webhooks:manage             # Webhook configuration
```

### Key-Based Authentication in APIs
- Header: Authorization: Bearer sk_live_xxx
- Query param (NOT recommended, leaks in logs): ?api_key=xxx
- Custom header: X-API-Key: xxx

## 6. Multi-Factor Authentication (MFA)

### Factors
- **Something you know**: Password, PIN, security questions
- **Something you have**: Phone, security key, hardware token
- **Something you are**: Fingerprint, face, iris

### TOTP (Time-based One-Time Password)
- Algorithm: TOTP = HMAC-SHA1(secret, floor(time / 30))
- 6-digit code, changes every 30 seconds
- RFC 6238
- Secret stored: QR code, manual entry, password manager
- Compromised if: device stolen, secret intercepted, phishing via real-time relay

### HMAC-based OTP (HOTP)
- Counter-based, not time-based
- Server increments counter on successful auth
- Less common than TOTP now

### Push Notifications
- Push-based MFA (Duo, Okta, Google Authenticator push)
- User approves on registered device
- Safer than TOTP code entry (no interception possible)
- Online required

### Hardware Security Keys (FIDO2)
- YubiKey, Google Titan, etc.
- Highest security MFA option
- Phishing and interception resistant
- Best for: privileged users, admin accounts, sensitive operations

### SMS MFA — AVOID
- SIM swap attacks: attacker transfers phone number
- SS7 vulnerabilities: intercept SMS
- Phishing: real-time relay of SMS codes
- NIST SP 800-63B recommends: OUT OF BAND (OOB) or cryptographic authenticators

## 7. Session Management

### Cookie-Based Sessions
```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=86400
```
- **HttpOnly**: Not accessible to JavaScript (prevents XSS theft)
- **Secure**: HTTPS only
- **SameSite**: CSRF protection (Lax, Strict, or None for cross-site)
- **Max-Age/Expires**: Session duration

### Token-Based Sessions (SPA)
- Access token in memory (not localStorage)
- Refresh token in HttpOnly cookie
- Silent refresh via iframe (avoid redirect loops)
- Clear on logout (revoke refresh token + clear memory)

### Session Security
- Rotate session ID on login (prevent session fixation)
- Invalidate on password change, MFA change
- Monitor for anomalies (new IP, new device)
- Server-side session store: Redis, PostgreSQL, Memcached
- Session fingerprinting: user agent, accept header, IP (subtle anomalies)

### Distributed Session Management
- Redis with TTL for stateless horizontal scaling
- Sticky sessions (not recommended — creates coupling)
- Database-backed sessions (heavier but simpler)

## 8. Authorization Models

### RBAC (Role-Based Access Control)
- Roles: Admin, Editor, Viewer
- Permissions: create, read, update, delete on resources
- Simple, efficient, widely supported
- Limitation: doesn't handle fine-grained permissions or context

### ABAC (Attribute-Based Access Control)
- Subject attributes: user role, department, clearance
- Resource attributes: owner, classification, sensitivity
- Environment attributes: time, location, device type
- Policy language: ALFA, XACML
- Flexible but complex to audit and debug

### Attribute-Based: JWT Claims
```json
{
  "sub": "user-123",
  "role": "editor",
  "tenant": "acme-corp",
  "permissions": ["read:posts", "write:posts", "read:users"],
  "org_units": ["marketing", "sales"]
}
```
- Permissions encoded in token (offline validation)
- Trade-off: token size vs round-trip validation

### Resource-Based Authorization
```json
{
  "permissions": [
    { "action": "write", "resource": "posts/*" },
    { "action": "write", "resource": "posts/authored-by-me" }
  ]
}
```
- Pattern match on resource identifiers
- Supports ownership checks (posts owned by current user)

### Policy-Based (Open Policy Agent / Casbin)
- Decouple authorization from application code
- OPA: Rego policy language, sidecar or library
- Casbin: multi-language, supports ACL, RBAC, ABAC models
- Good for: complex rules, audit requirements, centralized policy

## 9. Threat Modeling for APIs

### OWASP API Security Top 10 (2023)
1. **Broken Object Level Authorization (BOLA)**: Exposing endpoints that don't validate user ownership of referenced objects
2. **Broken Authentication**: Weak or misconfigured auth mechanisms
3. **Broken Object Property Level Authorization**: Users can access fields they shouldn't
4. **Unrestricted Resource Consumption**: APIs don't limit client resource usage
5. **Broken Function Level Authorization**: Privilege escalation via unauthorized endpoint access
6. **Unrestricted Access to Sensitive Business Flows**: No rate limits on critical operations
7. **Server-Side Request Forgery (SSRF)**: API fetches user-supplied URLs
8. **Security Misconfiguration**: Unnecessary features, verbose errors, missing security headers
9. **Improper Inventory Management**: Outdated endpoints, unpatched test environments
10. **Unsafe Consumption of Third-Party Services**: Insufficient validation of integration data

### Security Headers
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### Input Validation
- Validate all input at API boundary (never trust client)
- Schema validation (JSON Schema, Protobuf)
- Sanitize HTML output to prevent XSS
- Parameterize queries to prevent SQL injection
- Validate file uploads: type, size, name sanitization

## 10. Zero Trust Architecture

### Core Principles
- Never trust, always verify — every request must be authenticated and authorized
- Least privilege access — minimum permissions required
- Assume breach — design for detection and response
- Verify explicitly — use all available data points (identity, location, device health)

### Zero Trust for API Security
- Every API call must present valid credentials (API key, JWT, mTLS)
- Service-to-service: mTLS with workload identity (SPIFFE/SPIRE)
- API gateway: verify token, validate scopes, check rate limits
- Circuit breakers, request tracing, anomaly detection

### SPIFFE / SPIRE
- **SPIFFE**: Secure Production Identity Framework for Everyone
- Standard for workload identity in production environments
- Workloads get SVIDs (SPIFFE Verifiable Identity Documents) — X.509 certificates
- **SPIRE**: Reference implementation of SPIFFE
- Can integrate with Kubernetes, AWS, Azure, GCP, VM environments

### mTLS with Workload Identity
```yaml
# SPIRE registration entry
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: web-service
spec:
  spiffeIDTemplate: "ns/{{.MetaData.short_namespace}}/sa/{{.PodMeta.ServiceAccountName}}"
  podSelector:
    matchLabels:
      app: web
```
- Each pod gets a certificate with its SPIFFE ID
- Other services can verify: "is this caller from namespace X and service account Y?"

## 11. Identity Providers

| Provider | Type | Key Features |
|----------|------|-------------|
| Auth0 | SaaS | Universal Login, Rules, Extensions, MFA, SSO |
| Okta | SaaS + On-prem | Lifecycle management, API Access Management |
| Keycloak | Open source | Self-hosted, Federation, Social login, TOTP |
| Dex | Open source | OpenID provider, connects to existing IdPs |
| Clerk | SaaS | React-first, Embeddable UIs, User management |
| WorkOS | SaaS | Enterprise SSO, SCIM, Audit logs |
| AWS Cognito | AWS-native | User pools, Federated identities, Lambda triggers |
| Azure AD B2C | Azure-native | Custom policies, Social login, Enterprise federation |

---
Sources: Web research — RFC 7519 (JWT), RFC 6749 (OAuth2), RFC 7636 (PKCE), W3C WebAuthn spec, FIDO Alliance, OWASP API Security Top 10, SPIFFE/SPIRE docs, NIST SP 800-63B, Auth0 docs, Okta docs, Keycloak docs.
