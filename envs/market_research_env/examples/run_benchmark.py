"""Run repeated market-research baseline episodes and summarise results."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


def capture_and_accept(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    **kwargs: Any,
) -> None:
    """Capture and accept one evidence item."""
    obs = env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = obs.pending_evidence[-1].evidence_id
    env.step(MarketResearchAction(action_type="accept_evidence", evidence_id=evidence_id))


def capture_and_reject(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    reason: str,
    **kwargs: Any,
) -> None:
    """Capture and reject one evidence item."""
    obs = env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = obs.pending_evidence[-1].evidence_id
    env.step(
        MarketResearchAction(
            action_type="reject_evidence",
            evidence_id=evidence_id,
            rejection_reason=reason,
        )
    )


def run_espresso_baseline_episode() -> dict[str, Any]:
    """Run the known-good espresso baseline once and return a compact result."""
    env = MarketResearchEnvironment(task_id="uk_espresso_001", headless=True)
    started_at = time.perf_counter()

    try:
        env.reset()

        env.step(MarketResearchAction(action_type="goto", url="/product_a.html"))
        capture_and_accept(
            env,
            "BrewStart Compact 15 Bar is listed at £149.",
            "price",
            "Current product price signal from controlled product page.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_b.html"))
        capture_and_accept(
            env,
            "CremaGo Manual Espresso is listed at £119 with limited stock.",
            "price",
            "Current price and availability signal.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_c.html"))
        capture_and_accept(
            env,
            "BaristaLite Mini is listed at £179 and positioned as an easy-cleaning budget option.",
            "product",
            "Product candidate and positioning evidence.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_1.html"))
        capture_and_accept(
            env,
            "Competitor review themes include value, cleaning effort, milk steaming quality, and beginner friendliness.",
            "competitor",
            "Competitor-positioning evidence for the buying guide.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_2.html"))
        capture_and_accept(
            env,
            "User-risk themes include weak steam pressure, inconsistent temperature, noisy pumps, and grinder expectations.",
            "risk",
            "User-centred risk evidence for recommendation quality.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/affiliate_terms.html"))
        capture_and_accept(
            env,
            "Affiliate buying guides must disclose commission and note that prices and availability may change.",
            "affiliate",
            "Compliance evidence for affiliate-disclosure awareness.",
            freshness="current",
            reliability="controlled_local_page",
            compliance_notes="Affiliate disclosure awareness present.",
        )

        env.step(MarketResearchAction(action_type="goto", url="/stale_price_page.html"))
        capture_and_reject(
            env,
            "BrewStart Compact was £79 in a 2022 flash sale.",
            "price",
            "Archived price claim is stale and not current price evidence.",
            "Stale archived price from 2022 should not be accepted as current.",
            freshness="stale",
        )

        env.step(MarketResearchAction(action_type="goto", url="/misleading_claim_page.html"))
        capture_and_reject(
            env,
            "A £99 machine makes professional cafe-quality espresso for every user with no grinder, no skill, and no maintenance.",
            "review",
            "Unsupported sales claim with no tests or source data.",
            "Unsupported and misleading claim.",
            reliability="unsupported",
        )

        obs = env.step(MarketResearchAction(action_type="submit_bundle"))
        elapsed_seconds = round(time.perf_counter() - started_at, 3)
        bundle = obs.evidence_bundle

        return {
            "task_id": bundle.get("task_id"),
            "episode_id": env.state.episode_id,
            "success": bool(obs.score_details.get("success")),
            "done": bool(obs.done),
            "cum_reward": float(bundle.get("cum_reward", 0.0)),
            "accepted_count": len(bundle.get("accepted_evidence", [])),
            "rejected_count": len(bundle.get("rejected_evidence", [])),
            "pending_count": len(bundle.get("pending_evidence", [])),
            "reasons": obs.score_details.get("reasons", []),
            "export_paths": bundle.get("export_paths", {}),
            "elapsed_seconds": elapsed_seconds,
        }

    finally:
        env.close()


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a compact benchmark summary from repeated run results."""
    rewards = [float(item["cum_reward"]) for item in results]
    success_count = sum(1 for item in results if item.get("success"))

    return {
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "benchmark": "espresso_scripted_baseline",
        "runs": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results) if results else 0.0,
        "mean_reward": statistics.mean(rewards) if rewards else 0.0,
        "min_reward": min(rewards) if rewards else 0.0,
        "max_reward": max(rewards) if rewards else 0.0,
        "results": results,
    }


def write_summary(summary: dict[str, Any], output_dir: Path) -> dict[str, str]:
    """Write benchmark summary as JSON and Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"{stamp}_espresso_baseline_benchmark.json"
    markdown_path = output_dir / f"{stamp}_espresso_baseline_benchmark.md"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Espresso Baseline Benchmark",
        "",
        f"Created at: {summary['created_at']}",
        f"Runs: {summary['runs']}",
        f"Success count: {summary['success_count']}",
        f"Success rate: {summary['success_rate']:.2f}",
        f"Mean reward: {summary['mean_reward']:.2f}",
        f"Minimum reward: {summary['min_reward']:.2f}",
        f"Maximum reward: {summary['max_reward']:.2f}",
        "",
        "## Runs",
        "",
        "| Run | Success | Reward | Accepted | Rejected | Pending | Episode ID |",
        "|---:|:---:|---:|---:|---:|---:|---|",
    ]

    for index, item in enumerate(summary["results"], start=1):
        lines.append(
            "| {index} | {success} | {reward:.2f} | {accepted} | {rejected} | {pending} | {episode} |".format(
                index=index,
                success="yes" if item.get("success") else "no",
                reward=float(item.get("cum_reward", 0.0)),
                accepted=int(item.get("accepted_count", 0)),
                rejected=int(item.get("rejected_count", 0)),
                pending=int(item.get("pending_count", 0)),
                episode=item.get("episode_id", ""),
            )
        )

    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": str(json_path), "markdown": str(markdown_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated market-research baseline episodes.")
    parser.add_argument("--runs", type=int, default=3, help="Number of repeated baseline runs.")
    parser.add_argument(
        "--output-dir",
        default="/tmp/market_research_env/benchmarks",
        help="Directory for benchmark JSON and Markdown summaries.",
    )
    args = parser.parse_args()

    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")

    results: list[dict[str, Any]] = []
    for run_index in range(1, args.runs + 1):
        result = run_espresso_baseline_episode()
        results.append(result)
        print(
            "run={run} success={success} reward={reward} accepted={accepted} rejected={rejected}".format(
                run=run_index,
                success=result["success"],
                reward=result["cum_reward"],
                accepted=result["accepted_count"],
                rejected=result["rejected_count"],
            )
        )

    summary = build_summary(results)
    paths = write_summary(summary, Path(args.output_dir))

    print(f"runs={summary['runs']}")
    print(f"success_count={summary['success_count']}")
    print(f"success_rate={summary['success_rate']:.2f}")
    print(f"mean_reward={summary['mean_reward']:.2f}")
    print(f"json={paths['json']}")
    print(f"markdown={paths['markdown']}")


if __name__ == "__main__":
    main()
