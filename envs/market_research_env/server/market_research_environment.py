"""Browser-backed market research environment implementation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment

from market_research_env.models import (
    EvidenceRecord,
    MarketResearchAction,
    MarketResearchObservation,
    MarketResearchState,
)
from market_research_env.server.compliance import ComplianceChecker
from market_research_env.server.evidence_store import EvidenceStore
from market_research_env.server.extractors import clean_text, excerpt
from market_research_env.server.exporters import write_evidence_bundle_exports
from market_research_env.server.local_web_server import LocalWebServer
from market_research_env.server.logger import TrajectoryLogger
from market_research_env.server.scorer import MarketResearchScorer


class LocalMarketResearchTask:
    """BrowserGym task wrapper that opens the controlled local mini-web."""

    def __init__(self, base_url: str, start_path: str = "/index.html", seed: int = 1, **kwargs: Any) -> None:
        del kwargs
        self.base_url = base_url.rstrip("/")
        self.start_path = start_path
        self.seed = seed
        self.viewport = {"width": 1280, "height": 720}
        self.slow_mo = 100
        self.timeout = 10000
        self.locale = None
        self.timezone_id = None
        self.geolocation = None

    def setup(self, page: Any) -> tuple[str, dict[str, Any]]:
        page.goto(self.base_url + self.start_path)
        return "Gather and evaluate controlled market-research evidence.", {}

    def teardown(self) -> None:
        pass

    def validate(self, page: Any, chat_messages: list[str]) -> tuple[float, bool, str, dict[str, Any]]:
        del page, chat_messages
        return 0.0, False, "", {}

    def cheat(self, page: Any, chat_messages: list[str]) -> None:
        del page, chat_messages


class MarketResearchEnvironment(
    Environment[MarketResearchAction, MarketResearchObservation, MarketResearchState]
):
    """Controlled browser-based market research environment."""

    SUPPORTS_CONCURRENT_SESSIONS = True
    REQUIRES_SINGLE_THREAD_EXECUTOR = True

    def __init__(
        self,
        task_id: str = "uk_espresso_001",
        headless: bool = True,
        max_steps: int | None = None,
        output_dir: str | None = None,
    ) -> None:
        super().__init__()

        package_root = Path(__file__).resolve().parents[1]
        self.package_root = package_root
        self.local_web_dir = package_root / "local_web"
        self.task_id = task_id
        self.headless = headless
        self.output_dir = Path(output_dir or os.getenv("MARKET_RESEARCH_OUTPUT_DIR", "/tmp/market_research_env"))

        self._task = self._load_task(task_id)
        self._max_steps = int(max_steps or self._task.get("max_steps", 50))

        self._state = MarketResearchState(
            episode_id=str(uuid4()),
            task_id=task_id,
            max_steps=self._max_steps,
        )

        self._web_server: LocalWebServer | None = None
        self._browser_env = None
        self._base_url = ""
        self._current_url = ""
        self._page_text = ""
        self._links: list[dict[str, str]] = []
        self._last_action_error: str | None = None
        self._last_score_details: dict[str, Any] = {}
        self._last_export_paths: dict[str, str] = {}

        self.evidence_store = EvidenceStore()
        self.scorer = MarketResearchScorer()
        self.logger = TrajectoryLogger(self.output_dir / "trajectories")
        self.compliance: ComplianceChecker | None = None

    def _load_task(self, task_id: str) -> dict[str, Any]:
        task_path = self.package_root / "data" / "tasks" / f"{task_id}.json"
        return json.loads(task_path.read_text(encoding="utf-8"))

    def reset(self, seed: int | None = None, **kwargs: Any) -> MarketResearchObservation:
        del kwargs

        self.close_browser_only()
        self.evidence_store.clear()
        self.logger.reset()
        self._last_action_error = None
        self._last_score_details = {}
        self._last_export_paths = {}
        self._links = []
        self._page_text = ""

        if self._web_server is None:
            self._web_server = LocalWebServer(self.local_web_dir)
        self._base_url = self._web_server.start()
        self.compliance = ComplianceChecker(self._base_url)

        self._state = MarketResearchState(
            episode_id=str(uuid4()),
            step_count=0,
            task_id=self.task_id,
            max_steps=self._max_steps,
        )

        self._initialize_browser(seed=seed)
        self._refresh_page_snapshot()

        self.logger.log("reset", {"task_id": self.task_id, "base_url": self._base_url})
        return self._observation(message="Market research episode ready.", reward=0.0, done=False)

    def _initialize_browser(self, seed: int | None = None) -> None:
        try:
            from browsergym.core.env import BrowserEnv
        except ImportError as exc:
            raise ImportError(
                "BrowserGym is required for market_research_env. Install with: pip install -e envs/market_research_env"
            ) from exc

        start_path = self._task.get("start_path", "/index.html")
        self._browser_env = BrowserEnv(
            task_entrypoint=LocalMarketResearchTask,
            task_kwargs={"base_url": self._base_url, "start_path": start_path},
            headless=self.headless,
        )
        self._browser_env.reset()

    def step(self, action: MarketResearchAction, **kwargs: Any) -> MarketResearchObservation:
        del kwargs

        if not isinstance(action, MarketResearchAction):
            raise TypeError(f"Expected MarketResearchAction, got {type(action)}")
        if self._browser_env is None:
            raise RuntimeError("Environment has not been reset")

        self._state.step_count += 1
        self._last_action_error = None
        self._last_score_details = {}
        reward = 0.0
        done = False
        message = ""

        try:
            if action.action_type == "goto":
                reward, message = self._action_goto(action)
            elif action.action_type == "click":
                reward, message = self._action_click(action)
            elif action.action_type == "fill":
                reward, message = self._action_fill(action)
            elif action.action_type == "scroll":
                reward, message = self._action_scroll(action)
            elif action.action_type == "extract_page_text":
                self._refresh_page_snapshot()
                message = "Extracted page text."
            elif action.action_type == "extract_links":
                self._extract_links()
                message = "Extracted page links."
            elif action.action_type == "capture_evidence":
                reward, message = self._action_capture_evidence(action)
            elif action.action_type == "accept_evidence":
                reward, message = self._action_accept_evidence(action)
            elif action.action_type == "reject_evidence":
                reward, message = self._action_reject_evidence(action)
            elif action.action_type == "submit_bundle":
                reward, done, message = self._action_submit_bundle()
            elif action.action_type == "noop":
                message = "No operation."
            else:
                raise ValueError(f"Unsupported action_type: {action.action_type}")
        except Exception as exc:
            self._last_action_error = str(exc)
            reward = -0.5
            message = f"Action failed: {exc}"

        self._state.cum_reward += float(reward)
        if self._state.step_count >= self._state.max_steps:
            done = True
            message = message or "Maximum step count reached."

        self._update_counts()
        self.logger.log(
            "step",
            {
                "action": action.model_dump(),
                "reward": reward,
                "done": done,
                "message": message,
                "error": self._last_action_error,
                "score_details": self._last_score_details,
            },
        )

        if done:
            self._state.submitted = self._state.submitted or action.action_type == "submit_bundle"
            self.logger.write(self._state.episode_id or "episode")

        return self._observation(message=message, reward=reward, done=done)

    def _page(self) -> Any:
        if self._browser_env is None:
            raise RuntimeError("Browser environment is not initialised")
        return self._browser_env.unwrapped.page

    def _action_goto(self, action: MarketResearchAction) -> tuple[float, str]:
        assert self.compliance is not None
        target = self.compliance.normalise_url(action.url)
        if not self.compliance.is_allowed_url(target):
            self._state.disallowed_visit_count += 1
            return -5.0, f"Blocked disallowed URL: {target}"

        self._page().goto(target)
        self._page().wait_for_load_state("domcontentloaded")
        self._refresh_page_snapshot()
        return 0.0, f"Navigated to {target}"

    def _action_click(self, action: MarketResearchAction) -> tuple[float, str]:
        if action.selector:
            self._page().click(action.selector)
        elif action.bid:
            self._browser_env.step(f'click("{action.bid}")')
        else:
            raise ValueError("click requires selector or bid")
        self._refresh_page_snapshot()
        return 0.0, "Clicked element."

    def _action_fill(self, action: MarketResearchAction) -> tuple[float, str]:
        if not action.text:
            raise ValueError("fill requires text")
        if action.selector:
            self._page().fill(action.selector, action.text)
        elif action.bid:
            self._browser_env.step(f'fill("{action.bid}", "{action.text}")')
        else:
            raise ValueError("fill requires selector or bid")
        self._refresh_page_snapshot()
        return 0.0, "Filled element."

    def _action_scroll(self, action: MarketResearchAction) -> tuple[float, str]:
        delta = 600 if action.direction != "up" else -600
        self._page().mouse.wheel(0, delta)
        self._refresh_page_snapshot()
        return 0.0, f"Scrolled {action.direction or 'down'}."

    def _action_capture_evidence(self, action: MarketResearchAction) -> tuple[float, str]:
        self._refresh_page_snapshot()
        if not action.claim:
            raise ValueError("capture_evidence requires claim")

        record = self.evidence_store.capture(
            claim=action.claim,
            claim_type=action.claim_type or "general",
            source_url=self._current_url,
            rationale=action.rationale or "",
            reliability=action.reliability or "unknown",
            freshness=action.freshness or "unknown",
            commercial_usefulness=action.commercial_usefulness or "unknown",
            user_usefulness=action.user_usefulness or "unknown",
            compliance_notes=action.compliance_notes or "",
            extracted_text_excerpt=excerpt(self._page_text),
            metadata=action.action_metadata,
        )
        reward, details = self.scorer.score_capture(record)
        self._last_score_details = details
        return reward, f"Captured evidence {record.evidence_id}."

    def _action_accept_evidence(self, action: MarketResearchAction) -> tuple[float, str]:
        if not action.evidence_id:
            raise ValueError("accept_evidence requires evidence_id")
        record = self.evidence_store.accept(action.evidence_id)
        reward, details = self.scorer.score_accept(record)
        self._last_score_details = details
        return reward, f"Accepted evidence {record.evidence_id}."

    def _action_reject_evidence(self, action: MarketResearchAction) -> tuple[float, str]:
        if not action.evidence_id:
            raise ValueError("reject_evidence requires evidence_id")
        record = self.evidence_store.reject(action.evidence_id, action.rejection_reason or "")
        reward, details = self.scorer.score_reject(record)
        self._last_score_details = details
        return reward, f"Rejected evidence {record.evidence_id}."

    def _action_submit_bundle(self) -> tuple[float, bool, str]:
        assert self.compliance is not None

        accepted = self.evidence_store.accepted()
        rejected = self.evidence_store.rejected()
        text_values = []
        for record in accepted + rejected:
            text_values.extend(
                [
                    record.claim,
                    record.rationale,
                    record.compliance_notes,
                    record.extracted_text_excerpt,
                    record.source_url,
                ]
            )

        has_affiliate_awareness = self.compliance.affiliate_awareness_present(text_values)
        minimum_accepted = int(self._task.get("minimum_accepted_evidence", 5))
        minimum_rejected = int(self._task.get("minimum_rejected_evidence", 2))

        reward, success, details = self.scorer.score_submit(
            accepted_count=len(accepted),
            rejected_count=len(rejected),
            has_affiliate_awareness=has_affiliate_awareness,
            minimum_accepted=minimum_accepted,
            minimum_rejected=minimum_rejected,
            disallowed_visit_count=self._state.disallowed_visit_count,
            accepted_records=accepted,
            rejected_records=rejected,
        )
        self._last_score_details = details
        self._state.submitted = True

        bundle = self._bundle()
        bundle["cum_reward"] = self._state.cum_reward + float(reward)
        self._last_export_paths = write_evidence_bundle_exports(
            output_dir=self.output_dir / "bundles",
            episode_id=self._state.episode_id or "episode",
            bundle=bundle,
            score_details=details,
        )
        self.logger.log("bundle_export", {"export_paths": self._last_export_paths})

        return reward, True, "Submitted evidence bundle." if success else "Submitted incomplete or weak evidence bundle."

    def _refresh_page_snapshot(self) -> None:
        page = self._page()
        self._current_url = page.url
        self._page_text = clean_text(page.inner_text("body"))
        self._state.current_url = self._current_url

    def _extract_links(self) -> None:
        page = self._page()
        links = page.eval_on_selector_all(
            "a",
            "(els) => els.map((a) => ({text: a.innerText || '', href: a.href || ''}))",
        )
        self._links = [{"text": clean_text(item.get("text", "")), "href": item.get("href", "")} for item in links]
        self._refresh_page_snapshot()

    def _update_counts(self) -> None:
        self._state.accepted_count = len(self.evidence_store.accepted())
        self._state.rejected_count = len(self.evidence_store.rejected())
        self._state.pending_count = len(self.evidence_store.pending())

    def _bundle(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "accepted_evidence": [record.model_dump() for record in self.evidence_store.accepted()],
            "rejected_evidence": [record.model_dump() for record in self.evidence_store.rejected()],
            "pending_evidence": [record.model_dump() for record in self.evidence_store.pending()],
            "cum_reward": self._state.cum_reward,
            "submitted": self._state.submitted,
            "export_paths": self._last_export_paths,
        }

    def _observation(self, message: str, reward: float | None, done: bool) -> MarketResearchObservation:
        self._update_counts()
        return MarketResearchObservation(
            message=message,
            task=self._task,
            url=self._current_url,
            page_text=self._page_text,
            links=self._links,
            pending_evidence=self.evidence_store.pending(),
            accepted_evidence=self.evidence_store.accepted(),
            rejected_evidence=self.evidence_store.rejected(),
            evidence_bundle=self._bundle() if self._state.submitted or done else {},
            last_action_error=self._last_action_error,
            score_details=self._last_score_details,
            reward=reward,
            done=done,
        )

    @property
    def state(self) -> MarketResearchState:
        return self._state

    def close_browser_only(self) -> None:
        if self._browser_env is not None:
            try:
                self._browser_env.close()
            except Exception:
                pass
            self._browser_env = None

    def close(self) -> None:
        self.close_browser_only()
        if self._web_server is not None:
            self._web_server.stop()
            self._web_server = None
