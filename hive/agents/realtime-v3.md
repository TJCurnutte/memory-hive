# Real-Time APIs: Complete Technical Reference
> Compiled by API-Expert Agent — 2026-04-22  
> Topics: WebSockets, SSE, GraphQL Subscriptions, Bidirectional Streaming, WebRTC, Real-Time Pipelines

---

## Table of Contents
1. [WebSocket Architecture & Protocol](#1-websocket-architecture--protocol)
2. [Server-Sent Events (SSE)](#2-server-sent-events-sse)
3. [GraphQL Subscriptions](#3-graphql-subscriptions)
4. [Bidirectional Streaming](#4-bidirectional-streaming)
5. [WebRTC for AI Agents](#5-webrtc-for-ai-agents)
6. [Real-Time Data Pipeline Patterns](#6-real-time-data-pipeline-patterns)
7. [Comparison Matrix](#7-comparison-matrix)
8. [Best Practices & Anti-Patterns](#8-best-practices--anti-patterns)
9. [Code Examples](#9-code-examples)
10. [Future Trends](#10-future-trends)

---

## 1. WebSocket Architecture & Protocol

### 1.1 Protocol Fundamentals

WebSockets, defined in RFC 6455, provide a persistent, full-duplex communication channel over a single TCP connection. Unlike HTTP, where every request opens a new connection, WebSockets establish a connection once and keep it alive for bidirectional message exchange.

**The Handshake:**
- Client sends an HTTP upgrade request with `Upgrade: websocket` and `Sec-WebSocket-Key`
- Server responds with `101 Switching Protocols` and a signed `Sec-WebSocket-Accept` key
- Connection upgrades from HTTP to WebSocket protocol

```
Client → Server:
GET /ws HTTP/1.1
Host: api.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

Server → Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 1.2 WebSocket Frame Structure

Each WebSocket message is split into frames:

| Field | Bits | Description |
|-------|------|-------------|
| FIN | 1 | Final fragment flag (1=yes complete) |
| RSV1-3 | 3 | Extension-reserved |
| Opcode | 4 | 0x0=continuation, 0x1=text, 0x2=binary, 0x8=close, 0x9=ping, 0xA=pong |
| MASK | 1 | Whether payload is masked (client→server always 1) |
| Payload len | 7/16/64 | 7 bits, or 16 bits with "127" marker, or 64 bits |
| Masking key | 0/32 | If MASK=1, 4 bytes |
| Payload | N | The actual data |

**Opcodes:**
- `0x1` — Text frame (UTF-8 encoded)
- `0x2` — Binary frame
- `0x8` — Close frame (can include status code + reason)
- `0x9` — Ping (client/server can send; recipient responds with Pong)
- `0xA` — Pong (response to Ping)

### 1.3 Server Implementations

**Node.js (ws library):**
```javascript
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws, req) => {
  const clientId = req.headers['x-client-id'];
  
  ws.on('message', (data, isBinary) => {
    const msg = isBinary ? data : data.toString('utf-8');
    // Broadcast to all clients
    wss.clients.forEach(client => {
      if (client.readyState === 1 /* OPEN */) {
        client.send(JSON.stringify({ from: clientId, msg }));
      }
    });
  });

  ws.on('close', (code, reason) => {
    console.log(`Client disconnected: ${code} - ${reason.toString()}`);
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });

  // Heartbeat to detect dead connections
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
});

// Heartbeat interval
setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);
```

**Python (FastAPI + WebSockets):**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Process and broadcast
            await manager.broadcast({
                "type": "message",
                "client_id": client_id,
                "data": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 1.4 Scaling WebSockets

**Horizontal Scaling Challenges:**
- Sticky sessions (load balancer routes same client to same server)
- Redis Pub/Sub for cross-server message distribution
- Connection limits per instance

**Redis Pub/Sub Architecture:**
```python
# Each server instance subscribes to a Redis channel
import redis

redis_client = redis.Redis(host='redis-host')
pubsub = redis_client.pubsub()

async def forward_to_redis(channel: str, message: dict):
    redis_client.publish(channel, json.dumps(message))

async def subscribe_from_redis(channel: str):
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message['type'] == 'message':
            await manager.broadcast(json.loads(message['data']))
```

**Alternative: Socket.IO with Redis Adapter:**
```javascript
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';

const io = new Server();
const pubClient = createClient({ host: 'redis-host', port: 6379 });
const subClient = pubClient.duplicate();

io.adapter(createAdapter({ pubClient, subClient }));
// Now all Socket.IO servers share message routing
```

### 1.5 Subprotocols

WebSocket subprotocols (`Sec-WebSocket-Protocol` header) allow clients and servers to negotiate application semantics:

| Protocol | Use Case |
|----------|----------|
| `mqtt` | MQTT over WebSocket |
| `graphql-ws` | GraphQL subscription protocol |
| `json-1.0` | Simple JSON message protocol |
| `wamp.2.json` | WAMP (Web Application Messaging Protocol) |

---

## 2. Server-Sent Events (SSE)

### 2.1 How SSE Works

Server-Sent Events (W3C spec, RFC 6202) are a one-way push mechanism from server to client over HTTP. Unlike WebSockets, SSE uses plain HTTP, making it firewall-friendly and simple to implement.

**Key advantages over WebSockets for one-way:**
- Works over HTTP/2 multiplexed connections
- Automatic reconnection with `Last-Event-ID`
- Simpler infrastructure (no special protocol upgrade)
- Works through proxies
- Lower overhead for server-to-client only scenarios

### 2.2 SSE Message Format

Each message is a UTF-8 text block terminated by double newlines (`\n\n`):

```
event: stock-update
id: 1703
data: {"symbol": "AAPL", "price": 185.42}
data: {"symbol": "MSFT", "price": 410.21}
retry: 5000

event: notification
id: 1704
data: New order received for 500 shares

: this is a comment
```

**Fields:**
- `id` — Event ID (client sends `Last-Event-ID` header on reconnection)
- `event` — Named event type
- `data` — Payload (multiple `data:` lines are concatenated with `\n`)
- `retry` — Reconnection time in ms
- `:` — Comment (ignored)

### 2.3 Server Implementation

**Node.js (Express + SSE):**
```javascript
import express from 'express';

const app = express();

const clients = new Set();

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no'); // Disable Nginx buffering

  res.flushHeaders();

  const clientId = Math.random().toString(36).slice(2);
  clients.add({ id: clientId, res });

  res.write(`: connected\n\n`);
  res.write(`event: connected\ndata: ${JSON.stringify({ clientId })}\n\n`);

  req.on('close', () => {
    clients.delete({ id: clientId, res });
  });
});

// Broadcast to all connected clients
function broadcast(eventName, data) {
  const payload = `event: ${eventName}\ndata: ${JSON.stringify(data)}\n\n`;
  clients.forEach(client => client.res.write(payload));
}

export { broadcast };
```

**Python (FastAPI):**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio, json

app = FastAPI()
clients = set()

@app.get("/events")
async def sse_endpoint(request: Request):
    async def event_stream():
        queue = asyncio.Queue()
        clients.add(queue)
        
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            clients.remove(queue)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

async def broadcast(event_data: dict):
    for queue in clients:
        await queue.put(event_data)
```

### 2.4 Client-Side Handling

```javascript
// Browser SSE client
const eventSource = new EventSource('/events', {
  withCredentials: true
});

eventSource.addEventListener('stock-update', (e) => {
  const data = JSON.parse(e.data);
  updateDashboard(data);
});

eventSource.addEventListener('notification', (e) => {
  showNotification(e.data);
});

// Reconnection with Last-Event-ID
eventSource.onerror = (e) => {
  if (eventSource.readyState === EventSource.CLOSED) {
    console.log('SSE closed, attempting reconnect...');
    eventSource = new EventSource('/events');
  }
};

// Manual reconnect
let lastEventId = null;
eventSource.addEventListener('message', (e) => {
  lastEventId = e.lastEventId;
  // process e.data
});
```

---

## 3. GraphQL Subscriptions

### 3.1 Subscription Protocol

GraphQL subscriptions extend the query language for real-time data. The standard approach uses WebSockets with the `graphql-transport-ws` subprotocol (replacing the older `graphql-ws` protocol).

**Message Types:**

| Type | Direction | Description |
|------|-----------|-------------|
| `connection_init` | Client→Server | Initial connection parameters |
| `connection_ack` | Server→Client | Connection accepted |
| `subscribe` | Client→Server | Subscribe to a field |
| `next` | Server→Client | Streaming a result item |
| `error` | Server→Client | Error in subscription |
| `complete` | Both | Unsubscribe / subscription ended |

### 3.2 Server Implementation (graphql-yoga + Mercury)

```javascript
import { createServer } from 'http';
import { createYoga, createSchema } from 'graphql-yoga';
import { useGraphQLTransportSSE } from '@graphql-tools/utils';

const schema = createSchema({
  typeDefs: /* GraphQL */ `
    type Query {
      _: String
    }
    
    type Subscription {
      priceUpdates(symbol: String!): PriceUpdate!
      newOrders: Order!
      notifications(userId: ID!): Notification!
    }
    
    type PriceUpdate {
      symbol: String!
      price: Float!
      change: Float!
      timestamp: String!
    }
    
    type Order {
      id: ID!
      symbol: String!
      quantity: Int!
      side: OrderSide!
      price: Float
      status: OrderStatus!
    }
    
    enum OrderSide { BUY SELL }
    enum OrderStatus { PENDING FILLED CANCELLED }
    
    type Notification {
      id: ID!
      message: String!
      type: NotificationType!
      timestamp: String!
    }
    
    enum NotificationType { INFO WARNING ALERT }
  `,
  resolvers: {
    Subscription: {
      priceUpdates: {
        subscribe: async function* (_, { symbol }) {
          // Simulate real-time price stream
          let price = getInitialPrice(symbol);
          while (true) {
            price += (Math.random() - 0.5) * 2;
            yield { priceUpdates: { symbol, price, change: Math.random() * 10, timestamp: new Date().toISOString() } };
            await sleep(1000);
          }
        }
      },
      newOrders: {
        subscribe: async function* (_, __, { pubsub }) {
          // Yield a reference, pubsub publishes to it
          yield { newOrders: null }; // placeholder
          for await (const order of orderIterator(pubsub)) {
            yield { newOrders: order };
          }
        }
      },
      notifications: {
        subscribe: (_, { userId }, { pubsub }) {
          return pubsub.asyncIterator(`notifications:${userId}`);
        }
      }
    }
  }
});

const yoga = createYoga({
  schema,
  plugins: [useGraphQLTransportSSE()],
  fetchAPI: { Response, ReadableStream }
});

const server = createServer(yoga);
server.listen(4000, () => console.log('GraphQL server running at http://localhost:4000/graphql'));
```

### 3.3 Client Subscription (urql / Apollo)

```javascript
import { createClient, cacheExchange, fetchExchange, subscriptionExchange } from 'urql';
import { createClient as createWSClient } from 'graphql-ws';

const wsClient = createWSClient({
  url: 'ws://localhost:4000/graphql',
  connectionParams: { authToken: getAuthToken() },
  retryAttempts: 5,
  on: {
    connected: () => console.log('WS connected'),
    error: (err) => console.error('WS error:', err),
  }
});

const client = createClient({
  url: 'http://localhost:4000/graphql',
  exchanges: [
    cacheExchange,
    fetchExchange,
    subscriptionExchange({
      forwardSubscription(request) {
        const input = { ...request, query: request.query };
        return {
          subscribe(sink) {
            return wsClient.subscribe(input, sink);
          },
        };
      },
    }),
  ],
});

// Subscribe
const [result] = client.subscription(`
  subscription WatchPrice($symbol: String!) {
    priceUpdates(symbol: $symbol) {
      symbol
      price
      change
      timestamp
    }
  }
`, { symbol: 'AAPL' }).subscribe(data => {
  console.log('Price update:', data);
});
```

---

## 4. Bidirectional Streaming

### 4.1 HTTP/2 Server Push & Streams

HTTP/2 (RFC 7540) introduced multiplexing — multiple streams over a single TCP connection. HTTP/3 (QUIC-based) builds on this with better congestion control.

**gRPC Streaming:**
gRPC uses HTTP/2's multiplexing for four types of streaming:
- **Server-side streaming** — One request, many responses
- **Client-side streaming** — Many requests, one response
- **Bidirectional streaming** — Many requests, many responses
- **Unary** — Traditional request-response

```protobuf
syntax = "proto3";
package marketdata;

service MarketData {
  // Unary
  rpc GetQuote(Symbol) returns (Quote) {}
  
  // Server-side streaming
  rpc StreamQuotes(Symbol) returns (stream Quote) {}
  
  // Bidirectional streaming
  rpc ExecuteTrades(stream TradeRequest) returns (stream TradeConfirmation) {}
}

message Symbol { string symbol = 1; }

message Quote {
  string symbol = 1;
  double price = 2;
  int64 timestamp = 3;
}

message TradeRequest {
  string symbol = 1;
  int32 quantity = 2;
  string side = 3;
  double price = 4;
}

message TradeConfirmation {
  string order_id = 1;
  string status = 2;
  double fill_price = 3;
  int32 filled_quantity = 4;
}
```

**Go gRPC Server (bidirectional):**
```go
func (s *server) ExecuteTrades(stream MarketData_ExecuteTradesServer) error {
    for {
        req, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }
        
        // Process the trade
        confirmation := &TradeConfirmation{
            OrderId: generateOrderId(),
            Status:  "FILLED",
            FillPrice: req.Price,
            FilledQuantity: req.Quantity,
        }
        
        if err := stream.Send(confirmation); err != nil {
            return err
        }
    }
}
```

### 4.2 WebSocket Streaming (Streaming JSON Lines)

A common lightweight streaming pattern over WebSocket is JSON Lines — newline-delimited JSON objects:

```javascript
// Client sends commands
ws.send(JSON.stringify({ type: 'subscribe', channels: ['AAPL', 'MSFT'] }));
ws.send(JSON.stringify({ type: 'unsubscribe', channels: ['AAPL'] }));
ws.send(JSON.stringify({ type: 'ping' }));

// Server streams responses
// {"type":"quote","symbol":"AAPL","price":185.42,"ts":"2026-04-22T18:00:00Z"}
// {"type":"quote","symbol":"MSFT","price":410.21,"ts":"2026-04-22T18:00:01Z"}
// {"type":"pong"}
```

### 4.3 chunked Transfer-Encoding (HTTP Streaming)

For one-way server push over plain HTTP:

```python
@app.route('/stream-logs')
def stream_logs():
    def generate():
        for line in tail_log_file('/var/log/app.log'):
            yield f"data: {line}\n\n"
            time.sleep(0.1)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'X-Accel-Buffering': 'no'}
    )
```

---

## 5. WebRTC for AI Agents

### 5.1 Why WebRTC for AI Agents?

WebRTC (Web Real-Time Communication) enables peer-to-peer media and data channel communication. For AI agents, it enables:
- **Ultra-low latency voice conversations** (sub-300ms round-trip)
- **Real-time screen sharing** between agents
- **Direct data channel** for binary data (sensor streams, etc.)
- **Bypassing server infrastructure** for direct agent-to-agent communication

### 5.2 WebRTC Architecture

```
Agent A                      Signaling Server              Agent B
  |                                |                          |
  |--- createOffer() -------------->|                          |
  |                                |<--------- createAnswer() --|
  |                                |                          |
  |<--- ICE Candidate Exchange --->|                          |
  |                                |                          |
  |====== Direct P2P Connection (ICE/DTLS) ======|
  |                                                        |
  |---- STUN/TURN servers needed for NAT traversal ---->    |
```

**Key Components:**
- **Signaling** — Exchange session description (SDP) and ICE candidates (typically via WebSocket)
- **ICE** — Interactive Connectivity Establishment; finds best path through NATs
- **STUN** — Session Traversal Utilities for NAT (public IP discovery)
- **TURN** — Traversal Using Relays around NAT (relay server when direct P2P fails)
- **DTLS** — Datagram Transport Layer Security (encrypted data channels)
- **SCTP** — Stream Control Transmission Protocol (reliable/unreliable data channels)

### 5.3 Data Channel Implementation

```javascript
// Setting up a WebRTC data channel
const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    // TURN for production
    {
      urls: 'turn:turn.example.com:3478',
      username: 'user',
      credential: 'pass'
    }
  ]
};

async function createDataChannel(pc, label) {
  const dataChannel = pc.createDataChannel(label, {
    ordered: false,        // Allow out-of-order delivery
    maxRetransmits: 0,     // No retransmits (UDP-like)
    protocol: 'binary'      // Binary protocol
  });

  dataChannel.onopen = () => console.log(`Data channel '${label}' opened`);
  dataChannel.onmessage = (e) => {
    if (e.data instanceof ArrayBuffer) {
      const decoder = new TextDecoder();
      const msg = JSON.parse(decoder.decode(e.data));
      handleAgentMessage(msg);
    }
  };

  return dataChannel;
}

// ICE connection state machine
pc.oniceconnectionstatechange = () => {
  console.log('ICE state:', pc.iceConnectionState);
  // States: new → checking → connected → completed → disconnected → failed
};
```

### 5.4 AI Voice Pipeline with WebRTC

```
[Microphone] → [WebRTC Audio Processing] → [opus-encoded RTP] → [P2P or TURN]
     ↓                                                              ↓
[Audio Output] ← [WebRTC Audio Processing] ← [opus-encoded RTP] ← [AI Voice Model]
```

**Using MediaRecorder + WebAudio for AI pipelines:**
```javascript
const audioContext = new AudioContext();
const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
const micSource = audioContext.createMediaStreamSource(micStream);

// Connect to analyser for visualization
const analyser = audioContext.createAnalyser();
micSource.connect(analyser);

// For AI transcription: send to speech-to-text API
const mediaRecorder = new MediaRecorder(micStream, {
  mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
    ? 'audio/webm;codecs=opus' 
    : 'audio/webm'
});

const chunks = [];
mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.onstop = async () => {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  const arrayBuffer = await blob.arrayBuffer();
  // Send to AI transcription service
  const transcript = await transcribeStream(new Uint8Array(arrayBuffer));
  processTranscript(transcript);
};

mediaRecorder.start(100); // Collect in 100ms chunks
```

---

## 6. Real-Time Data Pipeline Patterns

### 6.1 Message Queue Architectures

**Apache Kafka:**
- Distributed, durable, high-throughput event streaming platform
- Key concepts: Topics, Partitions, Consumer Groups, Offsets
- For WebSocket scale-out: each server instance is a consumer group member

```python
from confluent_kafka import Consumer, Producer

# Producer (published by backend services)
producer = Producer({
    'bootstrap.servers': 'kafka1:9092,kafka2:9092',
    'client.id': 'websocket-gateway'
})

def publish_quote(symbol, price):
    producer.produce(
        topic='market-quotes',
        key=symbol.encode(),
        value=json.dumps({
            'symbol': symbol,
            'price': price,
            'ts': time.time()
        }).encode()
    )
    producer.flush()

# Consumer (WebSocket broadcast)
consumer = Consumer({
    'bootstrap.servers': 'kafka1:9092,kafka2:9092',
    'group.id': 'ws-broadcast-group',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True
})
consumer.subscribe(['market-quotes'])

def consume_and_broadcast():
    while True:
        msg = consumer.poll(1.0)
        if msg:
            quote = json.loads(msg.value().decode())
            broadcast_to_websocket_clients(quote)
```

**Redis Streams:**
- Lightweight alternative to Kafka for lower-volume streams
- Built into Redis (no separate cluster)

```python
import redis

r = redis.Redis(host='redis-host', decode_responses=True)

# Add to stream
r.xadd('market-quotes', {
    'symbol': 'AAPL',
    'price': '185.42',
    'ts': str(time.time())
}, maxlen=10000)  # Cap at 10k entries

# Consumer group for distributed WebSocket servers
r.xgroup_create('market-quotes', 'ws-broadcast', id='0', mkstream=True)

while True:
    # Block for 5 seconds waiting for new messages
    messages = r.xreadgroup('ws-broadcast', 'server-1', {'market-quotes': '>'}, count=100, block=5000)
    for stream, entries in messages:
        for msg_id, data in entries:
            broadcast_to_clients(data)
            r.xack('market-quotes', 'ws-broadcast', msg_id)
```

### 6.2 Backpressure Handling

When the data source produces faster than clients can consume:

```python
import asyncio
from collections import deque

class BackpressureBuffer:
    def __init__(self, max_size=1000):
        self.buffer = deque(maxlen=max_size)
        self.waiters = asyncio.Queue()
    
    async def put(self, item):
        if len(self.buffer) >= self.buffer.maxlen:
            # Drop oldest if buffer full (configurable strategy)
            self.buffer.popleft()
        self.buffer.append(item)
        
        # Wake up a waiter if any
        if self.waiters.qsize():
            self.waiters.put_nowait(item)
    
    async def get(self, timeout=5.0):
        # Return buffered item if available
        if self.buffer:
            return self.buffer.popleft()
        
        # Wait for new item with timeout
        try:
            return await asyncio.wait_for(self.waiters.get(), timeout)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Backpressure buffer timeout - no data")
```

### 6.3 Message Batching for Efficiency

```javascript
// Batch messages for network efficiency
class MessageBatcher {
  constructor(batchSize = 10, maxDelayMs = 100) {
    this.batch = [];
    this.batchSize = batchSize;
    this.maxDelayMs = maxDelayMs;
    this.timer = null;
    this.onFlush = null;
  }

  add(message) {
    this.batch.push(message);
    if (!this.timer) {
      this.timer = setTimeout(() => this.flush(), this.maxDelayMs);
    }
    if (this.batch.length >= this.batchSize) {
      this.flush();
    }
  }

  flush() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.batch.length && this.onFlush) {
      this.onFlush([...this.batch]);
      this.batch = [];
    }
  }
}

// Usage
const batcher = new MessageBatcher(5, 50);
batcher.onFlush = (batch) => ws.send(JSON.stringify({ type: 'batch', messages: batch }));
```

---

## 7. Comparison Matrix

| Feature | WebSocket | SSE | GraphQL Subscriptions | gRPC Streaming | WebRTC Data Channel |
|---------|-----------|-----|----------------------|----------------|---------------------|
| Direction | Bidirectional | Server→Client | Bidirectional | Bidirectional | Bidirectional |
| Protocol | ws:// | HTTP | WebSocket | HTTP/2 | UDP/TCP |
| Firewall friendly | Moderate | Yes | Moderate | Moderate | No (needs STUN/TURN) |
| Automatic reconnect | Manual | Yes (built-in) | Via lib | Via lib | Via lib |
| Binary support | Yes | No (text only) | Yes | Yes (Protobuf) | Yes (SCTP) |
| Built-in encryption | WSS (TLS) | HTTPS | WSS (TLS) | TLS on HTTP/2 | DTLS |
| NAT traversal | Needs proxy | N/A | Needs proxy | Needs proxy | STUN/TURN |
| Browser native | Yes | Yes | Via lib | Via lib | Yes |
| Max connections/tab | ~200 per domain | Unlimited | Via lib | Via lib | ~300 per origin |
| Message ordering | Per channel | Yes | Yes | Yes | Configurable |
| Latency | ~1ms | ~5ms | ~1ms | ~0.5ms | ~0.5ms |
| Best for | Chat, collab, games | Notifications, feeds | Real-time queries | Microservice streams | Voice, P2P, media |

---

## 8. Best Practices & Anti-Patterns

### Best Practices

1. **Always use WSS (WebSocket Secure)** in production — encrypt the entire frame stream
2. **Implement heartbeat/ping-pong** to detect dead connections early (every 30s)
3. **Use message framing** with size prefix or delimiters to handle partial reads
4. **Handle reconnection** with exponential backoff + jitter (max 5 retries)
5. **Close connections gracefully** — send close frame, wait for response, then terminate
6. **Limit max message size** (e.g., 1MB) to prevent memory exhaustion
7. **Use Redis/SQLite for session affinity** when scaling WebSocket servers
8. **Separate concerns** — use a message bus for scaling, not in-process pub/sub
9. **Validate all incoming messages** against a schema before processing
10. **Monitor connection count, message rate, latency p99** per WebSocket server instance

### Anti-Patterns

1. **Don't hold large messages in memory** — stream large payloads
2. **Don't use WebSocket for request-response** — use HTTP/REST/gRPC; WebSocket overhead is ~7 bytes/frame header
3. **Don't trust client-sent data blindly** — validate opcode, payload size, UTF-8 validity for text frames
4. **Don't ignore `Sec-WebSocket-Version`** — reject connections from outdated libraries
5. **Don't store WebSocket objects in global state** without cleanup — causes memory leaks
6. **Don't send pings from the client too frequently** — server-side ping is standard
7. **Don't use subprotocols as security boundaries** — they're not authenticated

---

## 9. Code Examples

### 9.1 WebSocket Load Balancer Health Check

```javascript
// Kubernetes readiness probe for WebSocket server
app.get('/ready', async (req, res) => {
  const healthy = 
    wsServer.clients.size < MAX_CONNECTIONS &&
    memoryUsage.heapUsed < HEAP_LIMIT &&
    await checkDatabaseConnection() &&
    await checkRedisConnection();
  
  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    connections: wsServer.clients.size,
    maxConnections: MAX_CONNECTIONS,
    memoryMB: Math.round(memoryUsage.heapUsed / 1024 / 1024),
    uptime: process.uptime()
  });
});
```

### 9.2 SSE Authenticated Stream

```python
@app.get("/events/authenticated")
async def authenticated_sse(request: Request, token: str = Header(None)):
    # Validate JWT
    try:
        payload = verify_jwt(token, SECRET_KEY)
        user_id = payload['sub']
    except JWTError:
        return Response(status_code=401)
    
    async def event_stream():
        queue = asyncio.Queue()
        await subscription_manager.subscribe(user_id, queue)
        try:
            while True:
                event = await queue.get()
                yield f"id: {event['id']}\ndata: {json.dumps(event['data'])}\n\n"
        except asyncio.CancelledError:
            await subscription_manager.unsubscribe(user_id, queue)
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 9.3 Multi-Protocol Real-Time Gateway

```javascript
// Single gateway that normalizes WebSocket, SSE, and gRPC streaming
class RealTimeGateway {
  constructor() {
    this.subscriptions = new Map(); // channel → Set<{transport, send}>
  }

  subscribe(client, channel, transport) {
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set());
    }
    const entry = { transport, send: this.createSender(transport) };
    this.subscriptions.get(channel).add(entry);
    return () => this.subscriptions.get(channel)?.delete(entry);
  }

  createSender(transport) {
    switch (transport.type) {
      case 'websocket':
        return (data) => transport.ws.send(JSON.stringify(data));
      case 'sse':
        return (data) => transport.res.write(`data: ${JSON.stringify(data)}\n\n`);
      case 'grpc-stream':
        return (data) => transport.write(data); // Protobuf encoded
      default:
        throw new Error(`Unknown transport: ${transport.type}`);
    }
  }

  publish(channel, data) {
    const subscribers = this.subscriptions.get(channel);
    if (subscribers) {
      subscribers.forEach(({ send }) => send(data));
    }
  }
}
```

---

## 10. Future Trends

### 10.1 HTTP/3 (QUIC) and Real-Time

HTTP/3 uses QUIC (UDP-based), which eliminates head-of-line blocking and improves real-time performance. Web browsers are already HTTP/3-enabled.

**Implications for real-time:**
- WebSocket over HTTP/3 will benefit from QUIC's 0-RTT connection establishment
- SSE will see reduced latency over HTTP/3 multiplexing
- WebRTC data channels over QUIC are being standardized

### 10.2 WebTransport

WebTransport (W3C/IETF) is a new browser API built on HTTP/3 QUIC, offering:
- Reliable and unreliable (UDP-like) streams
- Bidirectional streams
- Datagram messages
- Native WebSocket-like API with QUIC benefits

```javascript
// WebTransport API (Chrome/Edge already support)
const transport = new WebTransport('https://api.example.com/quic');
await transport.ready;

const stream = await transport.createBidirectionalStream();
const writer = stream.writable.getWriter();
const reader = stream.readable.getReader();

// Send
await writer.write(new TextEncoder().encode(JSON.stringify({ type: 'ping' })));

// Receive
const { value } = await reader.read();
const msg = JSON.parse(new TextDecoder().decode(value));
```

### 10.3 Edge-Native Real-Time

Running WebSocket/SSE servers at the edge (Cloudflare Workers, Fastly Compute):
- Sub-5ms latency from anywhere
- Durable Objects for stateful WebSocket connections at the edge
- No cold starts unlike traditional serverless

```javascript
// Cloudflare Durable Object WebSocket handler
export class WebSocketServer extends DurableObject {
  async fetch(request) {
    const upgrade = request.headers.get('Upgrade');
    if (!upgrade || upgrade !== 'websocket') {
      return new Response('Expected Upgrade: websocket', { status: 426 });
    }

    const { socket, response } = await WebSocketServer.accept(request, {});
    socket.addEventListener('message', (e) => this.handleMessage(e));
    socket.addEventListener('close', (e) => this.handleClose(e));

    return response;
  }

  handleMessage(event) {
    this.socket.send(event.data);
  }
}
```

### 10.4 GraphQL Live Queries

GraphQL Live Queries automatically re-execute resolvers when underlying data changes — replacing subscription boilerplate:

```graphql
# Live query (no subscription setup needed)
query LiveStock($symbol: String!) {
  stock(symbol: $symbol) @live {
    price
    volume
    timestamp
  }
}
```

### 10.5 AI Agent Communication Protocols

Emerging standards for AI-to-AI real-time communication:
- **MCP (Model Context Protocol)** — Anthropic's protocol for AI agent tool use
- **A2A (Agent-to-Agent)** — For direct agent negotiation and handoff
- **Multi-agent orchestration** via shared real-time state (CRDT-based)

---

*Last updated: 2026-04-22 | Version: 3.0*
