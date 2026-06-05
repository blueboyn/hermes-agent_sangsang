"""Corrector (agi-side): the validation gate.

This is the single most important inherited idea from agi: *new knowledge is a
hypothesis until proven*. Every hypothesis/emergent edge is checked — cheaply
rejected if below the confidence floor, otherwise judged by the LLM. Verdicts:

  * valid     -> status 'validated'   (eligible for promotion to a skill)
  * doubtful  -> stays 'doubtful', retried up to N times, then auto-rejected
  * rejected  -> status 'rejected'    (kept for audit, never silently dropped)

Doubt-tracking is in-memory per run, matching agi's "max 3 re-verifications".
"""

from __future__ import annotations

from collections import defaultdict

from .store import Store
from .config import Config
from .llm import LLMClient


class Corrector:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm
        self._doubt_counts: dict[int, int] = defaultdict(int)

    def verify_pending(self) -> dict:
        """Validate every hypothesis + doubtful edge currently in the graph."""
        pending = self.store.edges_by_status("hypothesis") + self.store.edges_by_status("doubtful")
        stats = {"validated": 0, "rejected": 0, "doubtful": 0}
        for e in pending:
            # cheap floor check before spending an LLM call (agi optimisation)
            if e.confidence < self.cfg.validate_min_confidence:
                self.store.set_edge_status(e.id, "rejected")
                self.store.record_validation("edge", e.id, "rejected",
                                             "below confidence floor", e.confidence)
                stats["rejected"] += 1
                continue

            v = self.llm.validate_edge(e.src_name, e.relation, e.dst_name, e.confidence)
            self.store.record_validation("edge", e.id, v.verdict, v.reason, v.confidence)

            if v.verdict == "valid":
                self.store.set_edge_status(e.id, "validated")
                stats["validated"] += 1
            elif v.verdict == "doubtful":
                self._doubt_counts[e.id] += 1
                if self._doubt_counts[e.id] >= self.cfg.doubtful_max_retries:
                    self.store.set_edge_status(e.id, "rejected")
                    self.store.record_validation("edge", e.id, "rejected",
                                                 "exhausted doubt retries", v.confidence)
                    stats["rejected"] += 1
                else:
                    self.store.set_edge_status(e.id, "doubtful")
                    stats["doubtful"] += 1
            else:
                self.store.set_edge_status(e.id, "rejected")
                stats["rejected"] += 1

        self.store.log("corrector.run",
                       f"validated={stats['validated']} rejected={stats['rejected']} "
                       f"doubtful={stats['doubtful']}")
        return stats
