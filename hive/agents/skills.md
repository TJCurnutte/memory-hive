# Coding Skills — Coder Agent
> Compiled: 2026-04-22 | Session: coder

---

### Skill 1: Error Handling

**Rule:** Errors should be either **handled explicitly** or **propagated with context** — never silently swallowed.

**Why it matters:**
Unhandled errors cause crashes, security vulnerabilities, and corrupted state. Silent failures are the hardest bugs to debug because they leave no trace. Explicit error handling makes failures predictable and recoverable.

**Practice Exercise:**
Write a function `fetch_user(user_id)` that:
1. Catches database connection errors — returns `None` with a log warning
2. Catches "user not found" — returns a typed `UserNotFoundError` (not `None`)
3. Catches unexpected errors — re-raises with context: `"Failed to fetch user {user_id}: {original_error}"`
4. Never has a bare `except: pass` anywhere

```python
# Checklist:
# [ ] Wrap network/disk calls in try/except
# [ ] Catch specific exceptions, not bare Exception
# [ ] Log with context (user_id, operation, original error)
# [ ] Re-raise with added context for unexpected errors
# [ ] Never return None as a "no error happened" signal — use a Result type
```

---

### Skill 2: API Design

**Rule:** APIs should be **hard to misuse** and **easy to use correctly** — self-documenting, consistent, and constrained.

**Why it matters:**
A good API prevents entire classes of bugs at call sites. Bad APIs make correctness require reading implementation details. Clear contracts between caller and callee reduce integration bugs and make refactoring safe.

**Practice Exercise:**
Design an API for a `UserService` with these methods. For each, write the function signature, docstring, and type hints before writing any implementation:

```python
class UserService:
    # Check: can someone call this incorrectly? Can you make it impossible?
    
    async def create_user(self, email: str, password: str) -> User:
        """
        Creates a new user account.
        
        Args:
            email: Valid email address (validated internally)
            password: Must be >= 12 chars, validated internally
            
        Returns:
            Newly created User with hashed password (never raw)
            
        Raises:
            EmailTakenError: if email already exists
            ValidationError: if email/password invalid
            
        DO NOT ALLOW: partial updates, missing fields, raw password exposure
        """
        ...
```

**Checklist:**
- [ ] All inputs validated at the boundary (not deep in the function)
- [ ] Return types are specific (not `dict`, `list`, or `Any`)
- [ ] Errors are raised with specific exception types
- [ ] Side effects (DB writes, email sends) are explicit and documented
- [ ] No "magic" behavior — caller can predict what will happen

---

### Skill 3: Performance Optimization

**Rule:** **Measure first, optimize second** — use profiling data, not intuition, to find bottlenecks.

**Why it matters:**
Premature optimization wastes time and creates complex, hard-to-maintain code. The fastest code is code you don't write. The second fastest is code that's actually measured and targeted.

**Practice Exercise:**
1. Profile this function — find the slowest 3 operations without changing any code:
   - Run in a profiler (cProfile for Python, Chrome DevTools for JS)
   - Identify: network calls, loop iterations, repeated computations
2. Fix only what profiling reveals — in this order of impact:
   - Remove N+1 queries → batch fetch
   - Add caching for repeated computations
   - Add database indexes for slow queries
   - Only then: optimize algorithms

```python
# BEFORE:
def get_user_posts(user_id):
    posts = db.query("SELECT * FROM posts WHERE user_id = ?", user_id)
    result = []
    for post in posts:
        author = db.query("SELECT * FROM users WHERE id = ?", post.author_id)
        result.append({"post": post, "author": author})
    return result

# AFTER (measure first, then):
async def get_user_posts(user_id):
    posts = await db.query_all("SELECT * FROM posts WHERE user_id = ?", user_id)
    if not posts:
        return []
    
    # Batch fetch authors — one query instead of N
    author_ids = list(set(p.author_id for p in posts))
    authors = await db.query_all(
        "SELECT * FROM users WHERE id IN (?)", author_ids
    )
    authors_by_id = {a.id: a for a in authors}
    
    return [{"post": p, "author": authors_by_id[p.author_id]} for p in posts]
```

**Checklist:**
- [ ] Used a profiler before optimizing
- [ ] Optimized the biggest bottleneck, not multiple small ones
- [ ] Added caching for repeated computations (> 1 call with same input)
- [ ] Batch operations when fetching related data
- [ ] Measured the improvement with a before/after benchmark

---

### Skill 4: Testing & Debugging

**Rule:** Write tests that **verify behavior**, not **implementation details** — if you refactor and tests break, the tests are wrong.

**Why it matters:**
Tests tied to implementation break on every refactor, even when behavior is correct. Tests that verify behavior survive refactoring and catch real regressions. The goal is a test suite that gives confidence, not one that documents how the code currently works.

**Practice Exercise:**
Refactor this brittle test into a behavior-focused one:

```python
# BRITTLE — tests implementation:
def test_user_controller_creates_user():
    controller = UserController(user_repo=MockUserRepo())
    controller.create_user(email="test@test.com", password="secret123")
    assert controller.user_repo.create.called_once()
    assert controller.user_repo.create.call_args[0][0] == "test@test.com"  # exposes internals

# BETTER — tests behavior:
def test_create_user_returns_user_with_hashed_password():
    service = UserService(user_repo=FakeUserRepo())
    
    user = service.create_user(email="test@test.com", password="secret123")
    
    assert user.email == "test@test.com"
    assert user.password != "secret123"  # raw password never stored
    assert user.id is not None
    # Doesn't care about which methods were called — just the outcome

# RULE: if you rename a private method and tests break, the tests are brittle
```

**Checklist:**
- [ ] Tests call the public API, not internal methods
- [ ] Tests assert on outcomes (return value, side effects), not on call counts/mocks
- [ ] Each test has one clear assertion focus
- [ ] Tests are fast (no real DB/API calls — use fakes or test containers)
- [ ] Tests are deterministic — no flaky time-based or random assertions

---

### Skill 5: Security-First Coding

**Rule:** Treat **all external input as untrusted** — validate at the boundary, escape at the output, never trust implicit assumptions.

**Why it matters:**
Most security vulnerabilities (OWASP Top 10) come from trusting user input without validation. Security bugs can leak data, allow unauthorized access, or compromise the entire system. Secure code is a habit, not a checklist you run once.

**Practice Exercise:**
Review this code and fix all security issues (without changing the business logic):

```python
# PROBLEMS (find and fix them all):
def search_users(query, user_id_from_session):
    sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    result = db.execute(sql)
    return result

def update_profile(user_id_from_session, bio):
    user = db.get("SELECT * FROM users WHERE id = ?", user_id_from_session)
    user.bio = bio
    user.save()

def export_data(format, user_id_from_session):
    if format == "json":
        return json.dumps(user_data)
    elif format == "csv":
        return "name,email\n" + csv_data
    # What if format == "..\..\etc\passwd"?
```

**Checklist:**
- [ ] No string interpolation in SQL queries — use parameterized queries
- [ ] All user input validated before use (type, length, format)
- [ ] Authorization checked on every operation (not just at login)
- [ ] Secrets never in code — use env vars or secrets manager
- [ ] File paths sanitized if user-provided
- [ ] Output encoded appropriately (HTML escaping, etc.)
- [ ] Rate limiting on public endpoints
- [ ] Sensitive data not logged (passwords, tokens, PII)

---

## General Principle

> **Write code for the next developer** (which might be future you). Every decision should make the code: easier to understand, harder to break, safer to change.