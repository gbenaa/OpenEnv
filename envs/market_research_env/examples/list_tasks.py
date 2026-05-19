"""List available market-research tasks."""

from __future__ import annotations

from market_research_env.server.task_registry import list_tasks


def main() -> None:
    for task in list_tasks():
        print(
            f"{task['task_id']} | {task.get('market', '')} | "
            f"{task.get('category', '')} | {task.get('start_path', '')}"
        )


if __name__ == "__main__":
    main()
