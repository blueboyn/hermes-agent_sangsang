"""Evolution loop (agi-side): autonomously acquire knowledge for open goals.

In the real agi system this reaches out to arXiv / Wikipedia and runs the text
through an extraction pipeline. Here the "acquirer" is pluggable: the demo
supplies a knowledge source that returns arrow-notation seed text, which the
LLM turns into causal edges. Acquired edges enter as *hypotheses* — they are
NOT trusted until the corrector validates them.
"""

from __future__ import annotations

from typing import Callable

from .store import Store
from .config import Config
from .llm import LLMClient

# A knowledge source maps a topic -> raw text to be mined for facts.
KnowledgeSource = Callable[[str], str]


class EvolutionLoop:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient, source: KnowledgeSource):
        self.store = store
        self.cfg = cfg
        self.llm = llm
        self.source = source

    def run_once(self, max_goals: int | None = None) -> dict:
        max_goals = max_goals or self.cfg.max_goals_per_run
        goals = [g for g in self.store.active_goals(max_goals) if g[1] == "KNOWLEDGE_GAP"]
        added_edges = 0
        for goal_id, _gtype, target in goals:
            text = self.source(target)
            if not text:
                continue
            for fact in self.llm.extract_facts(target, text):
                self.store.add_edge(fact.src, fact.dst, fact.relation,
                                    fact.strength, fact.confidence,
                                    origin="acquired", provenance="evolution")
                added_edges += 1
            self.store.resolve_gap(target)
            self.store.complete_goal(goal_id)
        if added_edges:
            self.store.log("evolution.run", f"acquired {added_edges} hypothesis edge(s)")
        return {"goals": len(goals), "edges": added_edges}
