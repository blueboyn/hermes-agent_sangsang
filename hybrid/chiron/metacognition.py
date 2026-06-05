"""Meta-cognition (agi-side): self-monitoring + goal generation.

Watches the agent's own capability stats and unmet knowledge gaps, then turns
weaknesses into prioritized learning goals. This is the "무위자연 / let the data
tell you what to learn" half of the loop.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class MetaCognition:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def record(self, action: str, success: bool, confidence: float) -> None:
        self.store.record_capability(action, success, confidence)

    def update_goals(self) -> int:
        """Recompute the active goal set from gaps + capability weaknesses."""
        created = 0
        for keyword, hits in self.store.active_gaps(self.cfg.gap_promote_hits):
            # priority scales with how often the gap has been hit
            self.store.upsert_goal("KNOWLEDGE_GAP", keyword, priority=min(hits, 10))
            created += 1
        for action in self.store.weaknesses(self.cfg.weak_success_rate, self.cfg.weak_confidence):
            self.store.upsert_goal("CAPABILITY_FIX", action, priority=8)
            created += 1
        if created:
            self.store.log("goals.update", f"{created} goal(s) refreshed")
        return created
