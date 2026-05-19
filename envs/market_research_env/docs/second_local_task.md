# Second Local Market Task

## Purpose

The second task proves that the market research environment is not hard-coded only for `uk_espresso_001`.

It adds:

```text
uk_air_fryers_001
```

The task uses a separate controlled local mini-web under:

```text
local_web/air_fryers/
```

## Task objective

The task asks the agent to assess whether there is enough reliable evidence to support a UK affiliate buying guide on budget air fryers.

## Signals represented

The local pages include:

```text
product candidates
price range
capacity and household fit
review themes
competitor activity
affiliate suitability
user risks
stale price evidence
unsupported sales claim evidence
```

## Why this matters

The first task demonstrated the action, evidence, scoring, and export loop for budget espresso machines.

The second task demonstrates that the same environment structure can support a different market category, a different start page, and a different local page set.

## Current validation

The integration smoke test verifies that:

```text
the second task file loads
the browser starts on /air_fryers/index.html
the task category is budget air fryers
the page text mentions budget air fryers
the expected local task links are discoverable
```

A full scripted baseline for this second task can be added later if needed.
