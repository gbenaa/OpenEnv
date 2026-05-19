# Negative-Control Tasks

## Purpose

Negative-control tasks test whether the environment can represent cases where the correct commercial conclusion is caution or refusal.

The first negative-control task is:

```text
uk_smart_rings_negative_001
```

The intended conclusion is:

```text
insufficient_evidence
```

## Why this matters

A market-research harness should not only reward agents for assembling positive buying-guide evidence. It should also reward agents for identifying when evidence is weak, stale, unsupported, or commercially unsafe.

This prevents a simple activity-maximising agent from treating every task as a recommendation task.

## Current negative-control design

The task uses a controlled local mini-web under:

```text
local_web/smart_rings_negative/
```

It contains deliberately weak sources:

```text
unverified product claim
forum warning
stale archived review
unsupported health and sensor claim
affiliate caution page
```

A good run should reject the weak, stale, and unsupported claims, then accept a compliance or insufficiency item that explains why an affiliate buying guide should not yet be written.

## Current success shape

The current environment still uses the general submit-bundle mechanism. For this task, success requires:

```text
accepted evidence count >= 1
rejected evidence count >= 3
affiliate-disclosure awareness present
no disallowed external URL visits
```

This is a first controlled approximation of an insufficient-evidence conclusion.
