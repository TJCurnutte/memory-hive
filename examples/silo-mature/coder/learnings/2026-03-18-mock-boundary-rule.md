---
date: 2026-03-18
agent: coder
context: a bug kept passing tests because we were mocking at the wrong layer
confidence: medium
---

# Mock at the system boundary, not inside it

## What happened

A bug in `PaymentProcessor._apply_discount` was passing all tests.
Tests mocked `PaymentProcessor.apply`, so the real discount math was
never executed under test.

## Root cause

The mock was one layer too shallow. We were testing the test
scaffolding, not the system.

## The fix

Keep mocks at the system boundary (the actual edge where we leave our
code: HTTP clients, DB drivers, external APIs, the filesystem). Inside
our own code, use the real implementations with fakes only at the
outermost edge.

## Generalizable rule

**Mock the edge, not the layer one down.** If you're mocking a function
in the same module you're testing, you're almost always making the
test pass without testing what it claims to test.

## For curator

This is a classic testing anti-pattern. Likely applies across agents —
if `reviewer` or any test-writing agent has seen variants, we should
promote to `patterns.md`.
