"""Promotion (THE FUSION): turn validated declarative knowledge into procedural
skills.

This module is the whole point of Chiron. agi grows a knowledge graph; hermes
grows skills. Neither bridges the two. Promotion does:

  1. Find each *chain head* — a topic that drives a causal chain (a node that is
     a source but never a destination among validated edges).
  2. Gather the whole reachable chain of *validated* edges from that head.
  3. A head whose chain has enough validated, high-confidence edges is deemed a
     stable, reusable pattern — not noise — and is synthesized into a SKILL.md.
  4. The skill is written with provenance='promoted'.

So a fact only becomes a *skill* (a thing the agent will actually be guided by)
after it survived the validation gate AND forms a recurring multi-step pattern.
Knowledge may be wrong, but it can't silently steer behaviour until it has
earned procedural status.
"""

from __future__ import annotations

from .store import Store, Edge
from .config import Config
from .llm import LLMClient


def _slug(name: str) -> str:
    return "knowledge-" + "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


class Promoter:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm

    def _reachable_chain(self, head: str, by_src: dict[str, list[Edge]]) -> list[Edge]:
        """All validated edges reachable from `head` (acyclic BFS)."""
        seen_edges: list[Edge] = []
        visited_nodes = {head}
        frontier = [head]
        while frontier:
            node = frontier.pop()
            for e in by_src.get(node, []):
                if e.id in {x.id for x in seen_edges}:
                    continue
                seen_edges.append(e)
                if e.dst_name not in visited_nodes:
                    visited_nodes.add(e.dst_name)
                    frontier.append(e.dst_name)
        return seen_edges

    def promote(self, turn: int) -> dict:
        validated = self.store.edges_by_status("validated")
        by_src: dict[str, list[Edge]] = {}
        sources, dests = set(), set()
        for e in validated:
            by_src.setdefault(e.src_name, []).append(e)
            sources.add(e.src_name)
            dests.add(e.dst_name)

        # chain heads: drive a chain but aren't themselves a downstream effect
        heads = sources - dests
        promoted = []
        for head in sorted(heads):
            chain = self._reachable_chain(head, by_src)
            if len(chain) < self.cfg.promote_min_validated_edges:
                continue
            avg_conf = sum(e.confidence for e in chain) / len(chain)
            if avg_conf < self.cfg.promote_min_confidence:
                continue

            facts = [(e.src_name, e.relation, e.dst_name) for e in chain]
            name = _slug(head)
            body = self.llm.synthesize_skill(head, facts)
            self.store.upsert_skill(name, body, origin="promoted", turn=turn)
            self.store.record_validation("promotion", self.store.node_id(head),
                                         "approve", f"{len(chain)} validated edges", avg_conf)
            promoted.append(name)

        if promoted:
            self.store.log("promotion.run", f"promoted skills: {', '.join(promoted)}")
        return {"promoted": promoted}
