"""Orchestrator: the closed self-evolution loop.

Combines both parents' loops on two timescales:

  Per-turn (hermes' immediate review + agi's monitoring)
    observe()  -> record capability, detect knowledge gaps
    nudge      -> every N turns, run background skill review

  Periodic (agi's evolution/emergence + hermes' curation)
    evolve()   -> meta-cognition goals -> acquire knowledge (hypotheses)
               -> corrector validates -> emergence discovers -> corrector again
               -> promote validated knowledge into skills
               -> curator consolidates / ages skills

`tick()` advances the turn counter and fires whatever is due. The demo drives
this; in production the periodic half would run on hermes' idle-triggered
background fork.
"""

from __future__ import annotations

from typing import Callable

from .config import Config
from .store import Store
from .llm import build_llm, LLMClient
from .metacognition import MetaCognition
from .evolution import EvolutionLoop, KnowledgeSource
from .corrector import Corrector
from .emergence import EmergenceDetector
from .promotion import Promoter
from .curator import Curator


class Orchestrator:
    def __init__(self, cfg: Config | None = None,
                 knowledge_source: KnowledgeSource | None = None,
                 llm: LLMClient | None = None):
        self.cfg = cfg or Config()
        self.store = Store(self.cfg.db_path)
        self.llm = llm or build_llm(self.cfg)
        self.meta = MetaCognition(self.store, self.cfg)
        self.evolution = EvolutionLoop(self.store, self.cfg, self.llm,
                                       knowledge_source or (lambda t: ""))
        self.corrector = Corrector(self.store, self.cfg, self.llm)
        self.emergence = EmergenceDetector(self.store, self.cfg)
        self.promoter = Promoter(self.store, self.cfg, self.llm)
        self.curator = Curator(self.store, self.cfg, self.llm)
        self.turn = 0
        # optional hook fired when the background review wants to write a skill
        self.background_review: Callable[[int], None] | None = None

    # -- per-turn ---------------------------------------------------------
    def observe(self, action: str, success: bool, confidence: float,
                unknown_terms: list[str] | None = None) -> None:
        """Record one interaction outcome and any knowledge gaps it exposed."""
        self.turn += 1
        self.meta.record(action, success, confidence)
        for term in (unknown_terms or []):
            if not self.store.has_node(term):
                self.store.record_gap(term)

        if self.turn % self.cfg.goal_update_every == 0:
            self.meta.update_goals()
        if self.cfg.skill_nudge_interval and self.turn % self.cfg.skill_nudge_interval == 0:
            if self.background_review:
                self.background_review(self.turn)  # hermes-style immediate review
        if self.turn % self.cfg.auto_evolve_every == 0:
            self.evolve()

    def use_skill(self, name: str) -> bool:
        """Mark a skill as used (keeps it out of the stale/archive path)."""
        return self.store.touch_skill(name, self.turn)

    # -- periodic ---------------------------------------------------------
    def evolve(self) -> dict:
        """One full evolution cycle: acquire -> validate -> discover ->
        validate -> promote -> curate."""
        self.meta.update_goals()
        acquired = self.evolution.run_once()
        v1 = self.corrector.verify_pending()
        emerged = self.emergence.discover()
        v2 = self.corrector.verify_pending()
        promoted = self.promoter.promote(self.turn)
        curated = self.curator.run(self.turn)
        report = {
            "turn": self.turn,
            "acquired_edges": acquired["edges"],
            "validated": v1["validated"] + v2["validated"],
            "rejected": v1["rejected"] + v2["rejected"],
            "emergent": emerged["discovered"],
            "promoted_skills": promoted["promoted"],
            "curator": curated,
        }
        self.store.log("evolve.cycle", str(report))
        return report

    # -- introspection ----------------------------------------------------
    def snapshot(self) -> dict:
        skills = self.store.skills(include_archived=True)
        return {
            "turn": self.turn,
            "skills": [(s["name"], s["origin"], s["status"]) for s in skills],
            "validated_edges": len(self.store.edges_by_status("validated")),
            "rejected_edges": len(self.store.edges_by_status("rejected")),
            "open_gaps": self.store.active_gaps(1),
        }

    def close(self) -> None:
        self.store.close()
