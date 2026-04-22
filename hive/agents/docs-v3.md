# API Documentation Mastery: Complete Technical Reference
> Compiled by API-Expert Agent — 2026-04-22  
> Topics: OpenAPI 3.1, Doc Best Practices, SDK Generation, Postman/Insomnia, Contract Testing, Mock Servers

---

## Table of Contents
1. [OpenAPI 3.1 Specification Deep Dive](#1-openapi-31-specification-deep-dive)
2. [API Documentation Best Practices](#2-api-documentation-best-practices)
3. [SDK Generation Tools & Workflows](#3-sdk-generation-tools--workflows)
4. [Postman & Insomnia Workflows](#4-postman--insomnia-workflows)
5. [Contract Testing](#5-contract-testing)
6. [Mock Servers & Testing Stubs](#6-mock-servers--testing-stubs)
7. [Developer Experience (DX) Principles](#7-developer-experience-dx-principles)
8. [Interactive Documentation](#8-interactive-documentation)
9. [API Changelog & Versioning Docs](#9-api-changelog--versioning-docs)
10. [AI-Assisted Documentation Tools](#10-ai-assisted-documentation-tools)

---

## 1. OpenAPI 3.1 Specification Deep Dive

### 1.1 What's New in OpenAPI 3.1

OpenAPI 3.1.0 (March 2021) brought several significant changes:

1. **JSON Schema is now fully compatible** — OpenAPI 3.1 uses JSON Schema Draft 2020-12, enabling use of `if`/`then`/`else`, `$dynamicRef`, and all JSON Schema keywords directly
2. **Free-form `additionalProperties`** — `additionalProperties: true` no longer implies `additionalProperties: {}`; schema can be truly free-form
3. **`$defs` for reusable schema definitions** — No more need for `components/schemas` for local references; use `$defs` within the document
4. **Removed `type` requirement** — Schema objects can omit `type`, making schemas truly open
5. **Webhooks** — First-class support for webhook definitions
6. **Server `description` supports markdown** — Full markdown in server descriptions

### 1.2 OpenAPI 3.1 Document Structure

```yaml
openapi: 3.1.0
info:
  title: Trading API
  version: 2.1.0
  description: |
    ## Overview
    The Trading API provides real-time market data and order execution.
    
    **Base URL:** `https://api.trading.example.com/v2`
  contact:
    name: API Support
    email: api-support@trading.example.com
    url: https://developers.trading.example.com
  license:
    name: Proprietary
    url: https://trading.example.com/terms
  x-logo:
    url: https://cdn.trading.example.com/logo.png
    altText: Trading API Logo

servers:
  - url: https://api.trading.example.com/v2
    description: Production
    variables:
      region:
        default: us-east-1
        enum: [us-east-1, eu-west-1, ap-south-1]
        description: Regional endpoint
  - url: https://sandbox.trading.example.com/v2
    description: Sandbox environment (no real money)

webhooks:
  orderUpdate:
    post:
      tags: [Webhooks]
      summary: Receive order status updates
      operationId: receiveOrderUpdate
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/$defs/OrderUpdate'
      responses:
        '200':
          description: OK

$defs:
  OrderUpdate:
    type: object
    required: [orderId, status, timestamp]
    properties:
      orderId:
        type: string
        pattern: '^ORD-[A-Z0-9]{12}$'
      status:
        type: string
        enum: [PENDING, FILLED, PARTIAL, CANCELLED, REJECTED]
      fillPrice:
        type: number
        format: double
        nullable: true
      fills:
        type: array
        items:
          $ref: '#/$defs/Fill'
      timestamp:
        type: string
        format: iso8601-datetime
  
  Fill:
    type: object
    required: [price, quantity, timestamp]
    properties:
      price:
        type: number
        format: double
        minimum: 0
      quantity:
        type: integer
        minimum: 1
      timestamp:
        type: string
        format: iso8601-datetime
  
  Error:
    type: object
    required: [code, message]
    properties:
      code:
        type: string
        enum: [INVALID_REQUEST, NOT_FOUND, UNAUTHORIZED, RATE_LIMITED, SERVER_ERROR]
      message:
        type: string
      details:
        type: array
        items:
          $ref: '#/$defs/ValidationError'
      requestId:
        type: string
        description: Use this for support requests

  ValidationError:
    type: object
    properties:
      field:
        type: string
        example: quantity
      issue:
        type: string
        example: must be greater than 0

paths:
  /orders:
    post:
      tags: [Orders]
      summary: Place a new order
      operationId: placeOrder
      description: |
        Places a limit or market order. Orders are validated against
        user limits and market conditions before acceptance.
      security:
        - BearerAuth: [api:write]
      parameters:
        - name: idempotencyKey
          in: header
          required: true
          description: Unique key to prevent duplicate orders
          schema:
            type: string
            pattern: '^[a-zA-Z0-9-]{16,64}$'
            example: ord-4f3a2b1c6d5e
          examples:
            uuid:
              value: 550e8400-e29b-41d4-a716-446655440000
            ksuids:
              value: 4TqLuPFRTBqi3oB9vCxJgP5cNd
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/$defs/PlaceOrderRequest'
            example:
              symbol: AAPL
              quantity: 100
              side: BUY
              orderType: LIMIT
              price: 185.50
      responses:
        '201':
          description: Order placed successfully
          headers:
            X-Order-Id:
              schema:
                type: string
              description: Server-assigned order ID
            Location:
              schema:
                type: string
                format: uri
              description: URL to order details
          content:
            application/json:
              schema:
                $ref: '#/$defs/Order'
              example:
                orderId: ORD-7K4M9N2P1ABC
                symbol: AAPL
                quantity: 100
                filledQuantity: 0
                status: PENDING
                side: BUY
                orderType: LIMIT
                price: 185.50
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/$defs/Error'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '409':
          description: Idempotency conflict — order may already exist
          content:
            application/json:
              schema:
                $ref: '#/$defs/Error'
        '422':
          description: Validation error
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/$defs/Error'
                  - type: object
                    properties:
                      code:
                        const: INVALID_REQUEST
                      details:
                        type: array
                        items:
                          $ref: '#/$defs/ValidationError'
        '429':
          $ref: '#/components/responses/RateLimited'
        '500':
          $ref: '#/components/responses/InternalError'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT issued by our auth server. Include as:
        `Authorization: Bearer <token>`
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  responses:
    Unauthorized:
      description: Invalid or missing authentication
      content:
        application/json:
          schema:
            $ref: '#/$defs/Error'
    RateLimited:
      description: Rate limit exceeded
      headers:
        X-RateLimit-Limit:
          schema:
            type: integer
        X-RateLimit-Remaining:
          schema:
            type: integer
        X-RateLimit-Reset:
          schema:
            type: integer
            format: unix-timestamp
        Retry-After:
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/$defs/Error'
    InternalError:
      description: Unexpected server error
      content:
        application/json:
          schema:
            $ref: '#/$defs/Error'

  parameters:
    orderId:
      name: orderId
      in: path
      required: true
      schema:
        type: string
        pattern: '^ORD-[A-Z0-9]{12}$'
      description: Order ID returned from placeOrder

  examples:
    NotFoundOrder:
      summary: Order not found
      value:
        code: NOT_FOUND
        message: Order not found
        requestId: abc123

tags:
  - name: Orders
    description: Order management endpoints
    externalDocs:
      url: https://developers.trading.example.com/docs/orders
  - name: Market Data
    description: Real-time and historical market data
  - name: Webhooks
    description: Configure webhook endpoints for real-time updates

externalDocs:
  url: https://developers.trading.example.com
  description: Full developer documentation
```

### 1.3 Advanced OpenAPI Patterns

**Polymorphic Schemas (oneOf):**

```yaml
OrderEvent:
  oneOf:
    - $ref: '#/$defs/OrderFillEvent'
    - $ref: '#/$defs/OrderCancelEvent'
    - $ref: '#/$defs/OrderRejectEvent'
  discriminator:
    propertyName: eventType
    mapping:
      FILL: '#/$defs/OrderFillEvent'
      CANCELLED: '#/$defs/OrderCancelEvent'
      REJECTED: '#/$defs/OrderRejectEvent'

OrderFillEvent:
  type: object
  required: [eventType, orderId, fill]
  properties:
    eventType:
      const: FILL
    orderId:
      type: string
    fill:
      $ref: '#/$defs/Fill'
```

**Link Objects (HATEOAS):**

```yaml
responses:
  '201':
    content:
      application/json:
        schema:
          type: object
          properties:
            orderId:
              type: string
            status:
              type: string
            _links:
              type: object
              properties:
                self:
                  $ref: '#/components/links/GetOrder'
                cancel:
                  $ref: '#/components/links/CancelOrder'

components:
  links:
    GetOrder:
      operationId: getOrder
      parameters:
        orderId: '$response.body#/orderId'
    CancelOrder:
      operationId: cancelOrder
      parameters:
        orderId: '$response.body#/orderId'
```

---

## 2. API Documentation Best Practices

### 2.1 The Anatomy of Great API Documentation

| Element | Purpose | Common Mistake |
|---------|---------|---------------|
| **Getting Started Guide** | First-time developer success in < 5 minutes | "Read the full spec first" |
| **Authentication Section** | How to get API keys, OAuth flows | Buried in footnotes |
| **Endpoint Reference** | Every endpoint documented with examples | One-liners: "Creates an order" |
| **Code Samples** | Working code in 5+ languages | Only cURL examples |
| **Error Reference** | Every error code documented with causes and fixes | Generic "an error occurred" |
| **SDK/SDKs** | Pre-built client libraries | No SDKs, only REST |
| **Changelog** | What changed and why in each version | No changelog |
| **Status Page** | Current API health and incidents | Nothing |

### 2.2 Writing Effective Descriptions

**Bad:** `POST /users - Creates a user.`

**Good:**
```markdown
## POST /users

Creates a new user account.

**Note:** Email addresses are case-insensitive but stored as-is. If 
`user@example.com` already exists, `User@Example.com` will conflict.

**Constraints:**
- Email must be unique across the platform
- Username must be 3-20 characters, alphanumeric + underscores
- Maximum 5 user accounts per organization (upgrade to add more)

**Webhooks triggered:** `user.created`, `user.activated`

### 2.3 Documentation Site Structure

```
docs.example.com/
├── quickstart/              # 5-minute getting started
│   ├── index.mdx           # One page, no prerequisites
│   ├── authentication.mdx
│   └── first-api-call.mdx
├── guides/
│   ├── webhooks.mdx
│   ├── rate-limiting.mdx
│   ├── pagination.mdx
│   └── error-handling.mdx
├── api-reference/
│   ├── openapi.json        # Machine-readable spec
│   └── [auto-generated from spec]
├── sdks/
│   ├── python.mdx
│   ├── typescript.mdx
│   └── go.mdx
├── changelog.mdx
├── status.mdx
└── support.mdx
```

### 2.4 Interactive Examples

```javascript
// Embed real, runnable examples in documentation
// Using RAPI (Run API in browser)

const apiExample = {
  title: "Place an order",
  request: {
    method: "POST",
    url: "https://api.trading.example.com/v2/orders",
    headers: {
      "Authorization": "Bearer {{token}}",
      "Content-Type": "application/json",
      "Idempotency-Key": "{{idempotencyKey}}"
    },
    body: {
      symbol: "AAPL",
      quantity: 10,
      side: "BUY",
      orderType: "MARKET"
    }
  },
  expectedResponse: {
    status: 201,
    body: {
      orderId: "ORD-7K4M9N2P1ABC",
      status: "PENDING",
      filledQuantity: 0
    }
  },
  tryIt: {
    enabled: true,
    authProvider: "oauth"
  }
};
```

---

## 3. SDK Generation Tools & Workflows

### 3.1 SDK Generation Landscape

| Tool | Language | Quality | Maintainability | Best For |
|------|----------|---------|-----------------|----------|
| **openapi-generator** | 50+ languages | Good | Medium | Broad language support |
| ** fern** | TypeScript, Python, Java, Go | Excellent | High (code-first) | Type-safe generation |
| ** Speakeasy** | Multiple | Excellent | High (direct generation) | Production SDKs |
| **SDKMAN** | Multiple | Good | Medium | Simple APIs |
| ** Curie** | TypeScript, Python | Good | Medium | GraphQL APIs |
| ** Bumpapi** | TypeScript | Good | Medium | TypeScript-first |

### 3.2 openapi-generator CLI

```bash
# Install
npm install -g @openapitools/openapi-generator-cli
# or
brew install openapi-generator

# Generate multiple SDKs
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-fetch \
  -o ./sdks/typescript \
  --additional-properties=nodePackageName=@mycompany/api-client,supportsES6=true,npmVersion=2.1.0

openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o ./sdks/python \
  --additional-properties=packageName=mycompany_api,packageVersion=2.1.0

openapi-generator-cli generate \
  -i openapi.json \
  -g go \
  -o ./sdks/go \
  --additional-properties=packageName=mycompany/api,structPrefix=false

# Generate server stubs (Node.js Express)
openapi-generator-cli generate \
  -i openapi.json \
  -g express-server \
  -o ./server \
  --additional-properties=framework=express
```

### 3.3 Fern (Code-First SDK)

Fern uses a `FernDefinition` to generate both OpenAPI and SDKs:

```yaml
# fern.config.yaml
x-fern-definition:
  api-name: trading-api
  version: 2.1.0

generators:
  typescript:
    output: ./sdks/typescript
    version: 3.x
  python:
    output: ./sdks/python
    version: 1.x
  openapi:
    output: ./openapi.json
```

```typescript
// src/api/resources/orders/service.ts
import { FernRegistry } from "@fern-fern/api";

export class OrdersService {
  constructor(private readonly _baseUrl: FernRegistry.BaseUrl, private readonly _options: FernRegistry.RequestOptions) {}

  async placeOrder(request: PlaceOrderRequest, options?: RequestOptions): Promise<PlaceOrderResponse> {
    return this._requester.request({
      method: "POST",
      url: `${this._baseUrl}/orders`,
      body: {
        symbol: request.symbol,
        quantity: request.quantity,
        side: request.side,
        orderType: request.orderType,
        price: request.price,
      },
      contentTypes: ["application/json"],
      accept: "application/json",
      ...options,
    });
  }
}
```

### 3.4 Speakeasy

```bash
# Install
brew install speakeasy

# Generate SDK with best practices
speakeasy sdk generate \
  --spec ./openapi.json \
  --lang typescript \
  --out ./sdks/typescript \
  --doc-version 2.1.0

# Generate with custom configuration
speakeasy sdk generate \
  --spec ./openapi.json \
  --lang python \
  --out ./sdks/python \
  --team my-team \
  --sdk-name trading-api \
  --version 2.1.0 \
  -- Serpent config for auth handling, retries, paginated list support

# Generate multi-language in CI/CD
speakeasy sdk generate \
  --spec ./openapi.json \
  --langs typescript,python,go \
  --out ./sdks \
  --mode provider  # generates all at once
```

---

## 4. Postman & Insomnia Workflows

### 4.1 Postman Collection Architecture

```json
{
  "info": {
    "name": "Trading API v2",
    "version": "2.1.0",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "{{baseUrl_sandbox}}"
    },
    {
      "key": "accessToken",
      "value": ""
    }
  ],
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{accessToken}}",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "Orders",
      "item": [
        {
          "name": "Place Order",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Order created', () => {",
                  "  pm.response.to.have.status(201);",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.orderId).to.match(/^ORD-[A-Z0-9]{12}$/);",
                  "  pm.collectionVariables.set('orderId', json.orderId);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Idempotency-Key",
                "value": "{{$guid}}",
                "type": "text"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/orders",
              "host": ["{{baseUrl}}"],
              "path": ["orders"]
            },
            "body": {
              "mode": "raw",
              "raw": "{{json.stringify({
                symbol: 'AAPL',
                quantity: 10,
                side: 'BUY',
                orderType: 'MARKET'
              })}}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            }
          }
        },
        {
          "name": "Get Order",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{baseUrl}}/orders/{{orderId}}",
              "host": ["{{baseUrl}}"],
              "path": ["orders", "{{orderId}}"]
            }
          }
        }
      ]
    }
  ],
  "auth": {
    "type": "oauth2",
    "oauth2": [
      {
        "key": "accessTokenUrl",
        "value": "https://auth.trading.example.com/oauth/token",
        "type": "string"
      },
      {
        "key": "authUrl",
        "value": "https://auth.trading.example.com/oauth/authorize",
        "type": "string"
      },
      {
        "key": "callbackUrl",
        "value": "https://app.getpostman.com/oauth2/callback",
        "type": "string"
      },
      {
        "key": "clientId",
        "value": "{{clientId}}",
        "type": "string"
      },
      {
        "key": "clientSecret",
        "value": "{{clientSecret}}",
        "type": "string"
      },
      {
        "key": "scope",
        "value": "api:read api:write",
        "type": "string"
      },
      {
        "key": "grantType",
        "value": "authorization_code",
        "type": "string"
      },
      {
        "key": "addTokenTo",
        "value": "header",
        "type": "string"
      }
    ]
  }
}
```

### 4.2 Insomnia Workspaces

Insomnia's git-sync and Organizations features are excellent for team collaboration:

```yaml
# .insomnia.yaml (GitOps for API specs)
version: 1.0.0
organization:
  id: trading-api-org
  name: Trading API Team
workspaces:
  - id: ws-trading-api
    name: Trading API
    description: Main API workspace
    git:
      url: git@github.com:trading/api-insomnia.git
      folder: .
      attributes:
        team: api-platform
    environments:
      - id: env-production
        name: Production
        variables:
          baseUrl: https://api.trading.example.com/v2
          apiKey: ""
      - id: env-sandbox
        name: Sandbox
        variables:
          baseUrl: https://sandbox.trading.example.com/v2
    collections:
      - name: Orders
        requests:
          - name: Place Order
            method: POST
            url: "{{ baseUrl }}/orders"
            headers:
              - name: Content-Type
                value: application/json
            body:
              type: json
              text: |
                {
                  "symbol": "AAPL",
                  "quantity": 10,
                  "side": "BUY",
                  "orderType": "MARKET"
                }
```

### 4.3 Postman to OpenAPI Sync

```bash
# Postman CLI (newman)
newman run trading-api.postman-collection.json \
  --environment production.env.json \
  --reporters cli,junit \
  --reporter-junit export results.xml

# Auto-generate OpenAPI from Postman collection
npx postman-to-openapi trading-api.postman-collection.json \
  --output openapi-generated.json \
  --name "Trading API" \
  --version "2.1.0"

# Import OpenAPI into Postman
postman import openapi.json
```

---

## 5. Contract Testing

### 5.1 What is Contract Testing?

Contract testing verifies that an API provider and API consumers agree on the contract — the request/response shapes. It's the key to safely evolving APIs without breaking consumers.

**Consumer-Driven Contracts (CDC):**
- Consumers define what they need from the API
- Provider verifies it satisfies all consumer contracts
- Independent deployment becomes safe

### 5.2 Pact (Consumer-Driven Contracts)

**Consumer Test (tests what the client needs):**

```python
# Python Pact consumer test
import pytest
from pact import Consumer, Provider, Term

@pytest.fixture
def pact_config():
    return {
        'consumer': {'name': 'trading-web-app'},
        'provider': {'name': 'trading-api'},
        'broker_url': 'https://pact-broker.trading.example.com'
    }

def test_place_order_creates_order(pact_config):
    pact = Consumer('trading-web-app').using_pact(pact_config)
    
    (pact
     .given('AAPL stock exists with price 185.50')
     .upon_receiving('a request to place a BUY order for 10 shares')
     .with_request(
         method='POST',
         path='/v2/orders',
         headers={'Authorization': 'Bearer token123', 'Content-Type': 'application/json'},
         body={
             'symbol': 'AAPL',
             'quantity': 10,
             'side': 'BUY',
             'orderType': 'MARKET'
         }
     )
     .will_respond_with(
         status=201,
         headers={'Content-Type': 'application/json', 'X-Order-Id': Term('\w{4}-\w{12}', 'ORD-7K4M9N2P1ABC')},
         body={
             'orderId': Term(r'ORD-[A-Z0-9]{12}', 'ORD-7K4M9N2P1ABC'),
             'status': 'PENDING',
             'filledQuantity': 0,
             'symbol': 'AAPL',
             'quantity': 10,
             'side': 'BUY'
         }
     )
     .then(test_function))
```

**Provider Verification:**

```python
# Pact provider verification
import subprocess

def verify_pact_with_broker():
    """Verify all consumer contracts against this provider"""
    result = subprocess.run([
        'pact-broker',
        'can-i-deploy',
        '--pacticipant', 'trading-api',
        '--version', os.environ['API_VERSION'],
        '--to-environment', 'production'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Contract verification failed:\n{result.stdout}")
    
    # Pull all consumer contracts and verify
    result = subprocess.run([
        'pact-provider-verifier',
        '--provider-base-url', 'http://localhost:3001',
        '--pact-broker-url', 'https://pact-broker.trading.example.com',
        '--provider-name', 'trading-api',
        '--broker-token', os.environ['PACT_BROKER_TOKEN']
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Pact verification failed:\n{result.stderr}")
```

### 5.3 Dredd (API Blueprint Testing)

```yaml
# dredd.yml
dry-run: false
hookfiles: ./test/hooks.py
language: nodejs
reporter: cli
custom:
  apiKey: testing-key
endpoints: >-
  https://api.trading.example.com/v2

# API Blueprint .apib file
FORMAT: 1A

# Trading API

## Orders [/v2/orders]

### Place Order [POST]

+ Request (application/json)
    + Headers
        Authorization: Bearer token123
        Idempotency-Key: ord-key-001
    + Body
        {
            "symbol": "AAPL",
            "quantity": 10,
            "side": "BUY",
            "orderType": "MARKET"
        }

+ Response 201 (application/json)
    + Headers
        X-Order-Id: ORD-7K4M9N2P1ABC
    + Body
        {
            "orderId": "ORD-7K4M9N2P1ABC",
            "status": "PENDING",
            "filledQuantity": 0
        }
```

### 5.4 WireMock for Stubbing

```json
// wiremock-stubs/order-stub.json
{
  "request": {
    "method": "POST",
    "urlPath": "/v2/orders",
    "headers": {
      "Authorization": {
        "matches": "Bearer .+"
      },
      "Content-Type": {
        "equalTo": "application/json"
      },
      "Idempotency-Key": {
        "matches": "[a-zA-Z0-9-]{16,64}"
      }
    },
    "bodyPatterns": [
      {
        "matchesJsonPath": "$.symbol",
        "matchesJsonPath": "$.quantity"
      }
    ]
  },
  "response": {
    "status": 201,
    "jsonBody": {
      "orderId": "ORD-7K4M9N2P1ABC",
      "symbol": "{{jsonPath request.body '$.symbol'}}",
      "quantity": "{{jsonPath request.body '$.quantity'}}",
      "status": "PENDING",
      "filledQuantity": 0,
      "createdAt": "{{now}}"
    },
    "headers": {
      "Content-Type": "application/json",
      "X-Order-Id": "ORD-7K4M9N2P1ABC"
    }
  },
  "scenarioName": "Order successfully placed",
  "requiredScenarioState": "Started"
}
```

---

## 6. Mock Servers & Testing Stubs

### 6.1 Prism (OpenAPI Mock Server)

```bash
# Install Prism CLI
npm install -g @stoplight/prism

# Run mock server from OpenAPI spec
prism mock openapi.json --port 4010

# With dynamic response generation (fixed fields from examples)
prism mock openapi.json \
  --port 4010 \
  --dynamic \
  --errors

# Validate requests against spec
prism mock openapi.json \
  --port 4010 \
  --request-name validation \
  --strict
```

```bash
# Docker deployment
docker run -d \
  --name prism-mock \
  -p 4010:4010 \
  -v $(pwd)/openapi.json:/openapi.json \
  stoplight/prism:latest \
  mock -h 0.0.0.0 /openapi.json --dynamic
```

### 6.2 Prism Config for Scenarios

```yaml
# prism.config.yaml
mock:
  dynamic: true
  collation: operation
  
  # Override responses based on scenarios
  scenarios:
    sandbox:
      when:
        header:
          X-Environment: sandbox
      then:
        delay: 100  # ms - simulate latency
        
    error-case:
      when:
        header:
          X-Test-Scenario: error
      then:
        response:
          status: 500
          body:
            code: SERVER_ERROR
            message: Internal server error
            requestId: test-error-001
```

### 6.3 MSW (Mock Service Worker)

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('https://api.trading.example.com/v2/orders', async ({ request }) => {
    const body = await request.json();
    
    // Simulate validation error
    if (body.quantity < 1) {
      return HttpResponse.json(
        {
          code: 'INVALID_REQUEST',
          message: 'Validation failed',
          details: [{ field: 'quantity', issue: 'must be greater than 0' }]
        },
        { status: 422 }
      );
    }
    
    // Simulate successful response
    return HttpResponse.json(
      {
        orderId: `ORD-${Date.now().toString(36).toUpperCase()}`,
        symbol: body.symbol,
        quantity: body.quantity,
        side: body.side,
        status: 'PENDING',
        filledQuantity: 0,
        createdAt: new Date().toISOString()
      },
      { status: 201, headers: { 'X-Order-Id': 'ORD-MOCK000001' } }
    );
  }),
  
  http.get('https://api.trading.example.com/v2/orders/:orderId', ({ params }) => {
    return HttpResponse.json({
      orderId: params.orderId,
      status: 'FILLED',
      filledQuantity: 100,
      fills: [
        { price: 185.50, quantity: 100, timestamp: new Date().toISOString() }
      ]
    });
  }),
];
```

```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);
```

### 6.4 Mock Server in CI/CD

```yaml
# .github/workflows/contract-test.yml
name: Contract Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Start Mock Server
        run: docker run -d --name prism -p 4010:4010 -v $(pwd):/openapi.json stoplight/prism:latest mock /openapi.json
      
      - name: Wait for Mock Server
        run: sleep 3 && curl -f http://localhost:4010/health || exit 1
      
      - name: Run Pact Consumer Tests
        run: |
          pip install pact-python
          pytest tests/consumer_pact_tests/ -v
      
      - name: Stop Mock Server
        run: docker stop prism
```

---

## 7. Developer Experience (DX) Principles

### 7.1 The "First Call in 5 Minutes" Rule

Every API should be usable within 5 minutes by a developer who has never seen it:

1. **No signup wall** — Allow API access with just an email or no auth for read-only endpoints
2. **Interactive console** — Try the API directly in the browser
3. **Pre-populated examples** — Show working code, not "replace with your data"
4. **Clear error messages** — "Invalid quantity: must be between 1 and 10000" beats "400 Bad Request"

### 7.2 SDK-First Design

When designing an API, design the SDK first:

```python
# BAD API design (low-level, verbose)
response = http_client.post(
    url='https://api.example.com/v2/orders',
    headers={'Authorization': 'Bearer ' + token, 'Idempotency-Key': key},
    json={'symbol': symbol, 'quantity': quantity, 'side': side, 'orderType': order_type}
)
order_id = response.headers['X-Order-Id']

# GOOD API design (clean, intuitive)
client = TradingClient(api_key='your-key')
order = client.orders.create(
    symbol='AAPL',
    quantity=10,
    side=OrderSide.BUY,
    order_type=OrderType.MARKET
)
print(order.id)  # ORD-7K4M9N2P1ABC
```

### 7.3 API Stability Guarantees

```markdown
## API Lifecycle Policy

### Versioning
- We use URL versioning: `/v1/`, `/v2/`
- We maintain N-2 versions (currently: v1 EOL, v2 active, v3 beta)
- We give 12 months notice before deprecating a version

### Breaking vs Non-Breaking Changes

**Non-breaking (no version bump needed):**
- Adding new optional request fields
- Adding new response fields
- Adding new endpoints
- Adding new enum values

**Breaking (requires version bump):**
- Removing or renaming fields
- Changing field types
- Changing error codes
- Removing endpoints
- Changing authentication requirements

### Deprecation Process
1. Announce in changelog + email to registered developers
2. Mark as deprecated in OpenAPI spec (`deprecated: true`)
3. Add `Deprecation` header to responses
4. Return sunset date in `Link` header
5. After sunset date, return 410 Gone
```

---

## 8. Interactive Documentation

### 8.1 Stoplight (Spectral + Elements)

```yaml
# . spectral.yml
extends: ['@stoplight/spectral:oas']
rules:
  oas2-api-host: error
  oas2-api-schemav: error
  info-description: warn
  operation-description: warn
  operation-tags: warn
  operation-tag-defined: warn
  operation-params: error
  operation-tag-description: warn
  path-params: error
  typed-enum: error
  valid-oas-3-1: error

functions:
  pathCaseConvention:
    targets:
      - target: $.paths
        function: pattern
        functionOptions:
          match: '^/\{[^}]+\}|[a-z0-9-]+$'

rules:
  path-case-convention:
    given: $.paths[*]
    then:
      function: pathCaseConvention
```

### 8.2 Redocly

```javascript
// redocly.config.js
export default {
 apis: './openapi.json',
  lint: {
    rules: {
      'no-unresolved-refs': 'error',
      'no-identical-paths': 'error',
    },
  },
  build: {
    apis: {
      'trading-api': {
        root: './openapi.json',
        output: './dist/docs',
      },
    },
  },
  customize: {
    theme: {
      spacing: { sectionHorizontal: '40px' },
      colors: {
        primary: { main: '#0066FF' },
      },
    },
  },
};
```

### 8.3 Swagger UI with Auth

```javascript
// Embed Swagger UI with OAuth 2.0
SwaggerUI({
  url: 'https://api.example.com/openapi.json',
  dom_id: '#swagger-ui',
  deepLink: true,
  displayRequestDuration: true,
  persistAuthorization: true,
  withCredentials: true,
  
  // OAuth 2.0 configuration
  oauth2RedirectUrl: `${window.location.origin}/oauth2-redirect.html`,
  authActions: {
    authorize: {
      apply: async (authParams) => {
        // Custom OAuth flow
        const token = await getOAuthToken(authParams);
        return { bearerAuth: [token] };
      }
    }
  },
  
  // Preload API key
  initOAuth: {
    clientId: 'trading-api-docs',
    scopes: ['api:read api:write'],
    usePkceWithAuthorizationCodeGrant: true,
    advancedOpts: true,
  },
  
  // Custom plugin for additional features
  plugins: [
    () => (system) => ({
      wrapComponents: {
        Info: wrapInfoWithLinks,
      },
    }),
  ],
  
  presets: [
    SwaggerUIBundle.presets.apis,
    SwaggerUIBundle.SwaggerUIStandalonePreset,
  ],
});
```

---

## 9. API Changelog & Versioning Docs

### 9.1 Changelog Format (Keep a Changelog)

```markdown
# Changelog

All notable changes to this API will be documented in this file.

## [2.2.0] - 2026-06-01

### Added
- **Webhooks v2** — Real-time order updates via WebSocket-backed webhooks
- **`GET /v2/market-data/historical`** — OHLCV candlestick data
- **`X-Request-Id` response header** — Use for support requests
- SDK support for Rust

### Changed
- **BREAKING** `quantity` field changed from `string` to `integer` (e.g., `"100"` → `100`)
- Rate limits increased from 100/min to 1000/min for `GET /v2/market-data`
- WebSocket `quote` event now includes `change24h` field

### Deprecated
- `GET /v1/orders` — Use `GET /v2/orders`; will be removed in v3.0.0

### Fixed
- `POST /v2/orders` with `orderType=STOP` now correctly validates stop price
- Fixed race condition in webhook delivery retry logic
- Rate limit headers now correctly reset after the window expires

### Security
- TLS 1.0 and 1.1 disabled; TLS 1.2 minimum required
- JWT tokens now use RS256 (asymmetric); HS256 is deprecated

## [2.1.0] - 2026-03-15

### Added
- GraphQL endpoint at `/graphql` for flexible querying
- Bulk order endpoint `POST /v2/orders/bulk`
- Pagination cursor for list endpoints
```

### 9.2 OpenAPI Versioning Strategy

```yaml
# openapi.v2.yaml - main spec for v2
openapi: 3.1.0
info:
  title: Trading API v2
  version: "2.2.0"
  description: |
    ## Migration from v1
    See [Migration Guide v1→v2](https://developers.example.com/migration/v1-v2)
    
    ## Changelog
    [View changelog](https://developers.example.com/changelog)

servers:
  - url: https://api.trading.example.com/v2

# All paths under v2

# Add deprecation markers to old endpoints
paths:
  /orders/v1:
    get:
      deprecated: true
      description: |
        **DEPRECATED** Use `GET /v2/orders` instead.
        
        Removal scheduled for 2027-01-01.
```

---

## 10. AI-Assisted Documentation Tools

### 10.1 Auto-Generated Descriptions with LLMs

```python
import anthropic

async def generate_endpoint_description(endpoint: dict) -> str:
    """Use LLM to generate a human-readable endpoint description"""
    client = anthropic.Anthropic()
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system="""You are an API documentation writer. Write clear, concise 
        descriptions for API endpoints. Follow these rules:
        - Start with a verb (Creates, Retrieves, Updates, Deletes)
        - Explain what the operation does in one sentence
        - List any important constraints or side effects
        - Mention related endpoints""",
        messages=[{
            "role": "user",
            "content": f"""Generate a description for this OpenAPI operation:
            
Endpoint: {endpoint.get('summary', '')}
Method: {endpoint.get('method', '')}
Path: {endpoint.get('path', '')}
Description: {endpoint.get('description', '')}
Parameters: {json.dumps(endpoint.get('parameters', []))}
Request body: {json.dumps(endpoint.get('requestBody', {}))}
Responses: {json.dumps(endpoint.get('responses', {}))}"""
        }]
    )
    
    return response.content[0].text

async def update_openapi_descriptions(openapi_spec: dict) -> dict:
    """Update all endpoint descriptions in an OpenAPI spec using AI"""
    for path, methods in openapi_spec.get('paths', {}).items():
        for method, operation in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                current_desc = operation.get('description', '')
                
                # Only generate if missing or placeholder
                if not current_desc or current_desc.startswith('[TODO]'):
                    operation['description'] = await generate_endpoint_description({
                        'summary': operation.get('summary', ''),
                        'method': method.upper(),
                        'path': path,
                        'parameters': operation.get('parameters', []),
                        'requestBody': operation.get('requestBody', {}),
                        'responses': operation.get('responses', {})
                    })
    
    return openapi_spec
```

### 10.2 Docusaurus with AI Chat

```typescript
// docs/sidebars.ts - AI chat integration
import { LLMSidebarChat } from '@theme/LLMSidebarChat';

const sidebars = {
  mainSidebar: [
    {
      type: 'doc',
      id: 'getting-started',
    },
    {
      type: 'category',
      label: 'API Reference',
      items: ['api-reference/overview'],
      link: {
        type: 'generated-index',
        title: 'API Reference',
        description: 'Complete API documentation',
      },
    },
    {
      type: 'html',
      value: '<div id="ai-chat" />',
      className: 'ai-chat-sidebar',
    },
  ],
};
```

### 10.3 Automated Changelog Generation

```bash
#!/bin/bash
# Generate changelog from git commits + PR titles

# Extract conventional commits
git log --pretty=format:"%s" --since="2026-04-01" | \
  grep -E "^(feat|fix|docs|style|refactor|perf|test|chore)" | \
  while read line; do
    type=$(echo "$line" | cut -d: -f1)
    desc=$(echo "$line" | cut -d: -f2 | xargs)
    echo "- **$type**: $desc"
  done > changelog-pending.md
```

---

*Last updated: 2026-04-22 | Version: 3.0*
