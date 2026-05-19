"""Run simple strategy comparisons for the market research environment.

This script adds deliberately poor baselines so the benchmark can demonstrate
that the scorer distinguishes useful research behaviour from weak behaviour.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


@dataclass
class StrategyRunResult:
    strategy: str
    run_index: int
    success: bool
    reward: float
    accepted: int
    rejected: int
    pending: int
    reasons: list[str]


def capture(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    **kwargs,
) -> str:
    """Capture an evidence item and return its evidence ID."""
    obs = env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    return obs.pending_evidence[-1].evidence_id


def accept(env: MarketResearchEnvironment, evidence_id: str) -> None:
    """Accept a captured evidence item."""
    env.step(MarketResearchAction(action_type="accept_evidence", evidence_id=evidence_id))


def reject(env: MarketResearchEnvironment, evidence_id: str, reason: str) -> None:
    """Reject a captured evidence item."""
    env.step(
        MarketResearchAction(
            action_type="reject_evidence",
            evidence_id=evidence_id,
            rejection_reason=reason,
        )
    )


def capture_and_accept(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    **kwargs,
) -> None:
    evidence_id = capture(env, claim, claim_type, rationale, **kwargs)
    accept(env, evidence_id)


def capture_and_reject(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    reason: str,
    **kwargs,
) -> None:
    evidence_id = capture(env, claim, claim_type, rationale, **kwargs)
    reject(env, evidence_id, reason)


def add_good_evidence(env: MarketResearchEnvironment, include_affiliate: bool = True) -> None:
    """Add the six accepted evidence items used by the successful baseline."""
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

    if include_affiliate:
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


def add_good_rejections(env: MarketResearchEnvironment) -> None:
    """Add the two rejected evidence items used by the successful baseline."""
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


def strategy_successful_baseline(env: MarketResearchEnvironment) -> None:
    """Good baseline: accept useful evidence and reject weak evidence."""
    add_good_evidence(env, include_affiliate=True)
    add_good_rejections(env)


def strategy_accept_everything(env: MarketResearchEnvironment) -> None:
    """Bad baseline: accepts useful evidence, stale evidence, and unsupported claims."""
    add_good_evidence(env, include_affiliate=True)

    env.step(MarketResearchAction(action_type="goto", url="/stale_price_page.html"))
    capture_and_accept(
        env,
        "BrewStart Compact was £79 in a 2022 flash sale.",
        "price",
        "Archived price claim is stale and not current price evidence.",
        freshness="stale",
    )

    env.step(MarketResearchAction(action_type="goto", url="/misleading_claim_page.html"))
    capture_and_accept(
        env,
        "A £99 machine makes professional cafe-quality espresso for every user with no grinder, no skill, and no maintenance.",
        "review",
        "Unsupported sales claim with no tests or source data.",
        reliability="unsupported",
    )


def strategy_duplicate_evidence(env: MarketResearchEnvironment) -> None:
    """Bad baseline: repeats the same accepted evidence to game the threshold."""
    env.step(MarketResearchAction(action_type="goto", url="/product_a.html"))

    for index in range(6):
        capture_and_accept(
            env,
            "BrewStart Compact 15 Bar is listed at £149.",
            "price",
            f"Repeated product price signal number {index + 1}.",
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

    add_good_rejections(env)


def strategy_no_disclosure(env: MarketResearchEnvironment) -> None:
    """Bad baseline: gathers evidence but omits affiliate-disclosure awareness."""
    add_good_evidence(env, include_affiliate=False)
    add_good_rejections(env)


STRATEGIES = {
    "successful_baseline": strategy_successful_baseline,
    "accept_everything": strategy_accept_everything,
    "duplicate_evidence": strategy_duplicate_evidence,
    "no_disclosure": strategy_no_disclosure,
}


def run_strategy(strategy_name: str, run_index: int) -> StrategyRunResult:
    """Run one strategy once and return a compact result."""
    env = MarketResearchEnvironment(headless=True)

    try:
        env.reset()
        STRATEGIES[strategy_name](env)
        obs = env.step(MarketResearchAction(action_type="submit_bundle"))

        return StrategyRunResult(
            strategy=strategy_name,
            run_index=run_index,
            success=bool(obs.score_details.get("success")),
            reward=float(obs.evidence_bundle.get("cum_reward", obs.reward or 0.0)),
            accepted=len(obs.evidence_bundle.get("accepted_evidence", [])),
            rejected=len(obs.evidence_bundle.get("rejected_evidence", [])),
            pending=len(obs.evidence_bundle.get("pending_evidence", [])),
            reasons=list(obs.score_details.get("reasons", [])),
        )
    finally:
        env.close()


def summarise_results(results: list[StrategyRunResult]) -> dict:
    """Summarise strategy results in a stable JSON-friendly structure."""
    by_strategy: dict[str, list[StrategyRunResult]] = defaultdict(list)
    for result in results:
        by_strategy[result.strategy].append(result)

    strategies = {}
    for name, items in sorted(by_strategy.items()):
        strategies[name] = {
            "runs": len(items),
            "success_count": sum(1 for item in items if item.success),
            "success_rate": sum(1 for item in items if item.success) / len(items),
            "mean_reward": mean(item.reward for item in items),
            "mean_accepted": mean(item.accepted for item in items),
            "mean_rejected": mean(item.rejected for item in items),
            "reasons": sorted({reason for item in items for reason in item.reasons}),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result_count": len(results),
        "strategies": strategies,
        "runs": [asdict(result) for result in results],
    }


def write_summary(summary: dict, output_dir: Path) -> dict[str, str]:
    """Write JSON and Markdown strategy benchmark summaries."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"{timestamp}_strategy_benchmark.json"
    md_path = output_dir / f"{timestamp}_strategy_benchmark.md"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Market Research Strategy Benchmark",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "| Strategy | Runs | Success rate | Mean reward | Mean accepted | Mean rejected |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for name, data in summary["strategies"].items():
        lines.append(
            f"| {name} | {data['runs']} | {data['success_rate']:.2f} | "
            f"{data['mean_reward']:.2f} | {data['mean_accepted']:.2f} | {data['mean_rejected']:.2f} |"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": str(json_path), "markdown": str(md_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run simple strategy benchmarks.")
    parser.add_argument("--runs", type=int, default=1, help="Runs per strategy.")
    parser.add_argument(
        "--strategies",
        nargs="+",
        default=list(STRATEGIES),
        choices=sorted(STRATEGIES),
        help="Strategies to run.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/market_research_env/benchmarks",
        help="Directory for JSON and Markdown benchmark summaries.",
    )
    args = parser.parse_args()

    results: list[StrategyRunResult] = []
    for strategy_name in args.strategies:
        for run_index in range(1, args.runs + 1):
            result = run_strategy(strategy_name, run_index)
            results.append(result)
            print(
                f"strategy={result.strategy} run={result.run_index} "
                f"success={result.success} reward={result.reward:.1f} "
                f"accepted={result.accepted} rejected={result.rejected}"
            )

    summary = summarise_results(results)
    paths = write_summary(summary, Path(args.output_dir))

    for name, data in summary["strategies"].items():
        print(
            f"{name}: runs={data['runs']} success_rate={data['success_rate']:.2f} "
            f"mean_reward={data['mean_reward']:.2f}"
        )

    print(f"json={paths['json']}")
    print(f"markdown={paths['markdown']}")


if __name__ == "__main__":
    main()
