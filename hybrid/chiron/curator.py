"""Curator (hermes-side): lifecycle + consolidation of skills.

Carries over hermes' operational discipline:
  * Automatic state transitions with NO LLM: active -> stale -> archived,
    driven purely by idle time (measured in turns here).
  * Consolidation: sibling skills sharing a prefix are merged under an umbrella.
  * NEVER delete — only archive. Pinned skills are untouchable.

This is the safety counterweight to the agi-side knowledge growth: even if
promotion produces too many narrow skills, the curator keeps the library
class-level and recoverable.
"""

from __future__ import annotations

from collections import defaultdict

from .store import Store
from .config import Config
from .llm import LLMClient


class Curator:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm

    def run(self, turn: int) -> dict:
        transitions = self._transition(turn)
        consolidations = self._consolidate(turn)
        self.store.log("curator.run",
                       f"stale={transitions['stale']} archived={transitions['archived']} "
                       f"consolidated={len(consolidations)}")
        return {**transitions, "consolidations": consolidations}

    # -- automatic, no-LLM lifecycle -------------------------------------
    def _transition(self, turn: int) -> dict:
        out = {"stale": 0, "archived": 0}
        for s in self.store.skills():
            if s["pinned"]:
                continue
            idle = turn - s["last_used_turn"]
            if idle >= self.cfg.archive_after_uses_idle and s["status"] != "archived":
                self.store.set_skill_status(s["id"], "archived")  # recoverable, not deleted
                out["archived"] += 1
            elif idle >= self.cfg.stale_after_uses_idle and s["status"] == "active":
                self.store.set_skill_status(s["id"], "stale")
                out["stale"] += 1
        return out

    # -- consolidation into umbrellas ------------------------------------
    def _consolidate(self, turn: int) -> list[str]:
        clusters: dict[str, list] = defaultdict(list)
        for s in self.store.skills():
            if s["pinned"] or s["status"] == "archived":
                continue
            # cluster on the leading token: 'debugging-flaky-tests' -> 'debugging'
            prefix = s["name"].split("-", 1)[0]
            clusters[prefix].append(s)

        consolidated = []
        for prefix, members in clusters.items():
            if len(members) < self.cfg.curator_min_cluster:
                continue
            umbrella = self.llm.name_umbrella(prefix, [m["name"] for m in members])
            body_parts = [f"# {umbrella}", "",
                          "_Consolidated umbrella. Provenance: curated._", ""]
            for m in members:
                body_parts.append(f"## {m['name']}\n\n{m['body']}\n")
            self.store.upsert_skill(umbrella, "\n".join(body_parts), origin="curated", turn=turn)
            # archive the now-absorbed siblings (recoverable)
            for m in members:
                if m["name"] != umbrella:
                    self.store.set_skill_status(m["id"], "archived")
            consolidated.append(umbrella)
        return consolidated
