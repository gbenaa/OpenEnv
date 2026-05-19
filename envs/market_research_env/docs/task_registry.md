# Market Research Task Registry

## Purpose

The task registry records which local market-research tasks are available to the environment.

It is deliberately simple. The registry is not a scheduler, benchmark runner, or task-generation system. It is a small metadata layer that lets developers and scripts discover available task IDs without manually inspecting the task directory.

## Location

The registry lives at:

```text
data/tasks/index.json
```

Task definitions live beside it:

```text
data/tasks/uk_espresso_001.json
data/tasks/uk_air_fryers_001.json
```

## Listing tasks

From the environment directory:

```bash
scripts/list_tasks.sh
```

Expected output shape:

```text
uk_air_fryers_001 | UK | budget air fryers | /air_fryers/index.html
uk_espresso_001 | UK | budget espresso machines | /index.html
```

## Python helper

The helper module is:

```text
server/task_registry.py
```

It exposes:

```text
list_tasks()
load_task(task_id)
build_task_index()
write_task_index()
```

## Why this matters

The second local task means the environment is no longer only a one-task proof of concept. The registry is the first step towards running the same evidence-gathering and scoring harness across multiple bounded market-research tasks.
