"""Emergence detector (agi-side): discover *novel* causal paths.

Walks the graph of already-validated edges to find indirect connections that
are not yet asserted directly (A -> B -> C, but no A -> C). Each discovery is
inserted as a NEW emergent hypothesis edge so it must itself pass the corrector
before it can ever be promoted. This is how the system "has a new idea" — and
how that idea is still held to the same evidentiary bar as acquired knowledge.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class EmergenceDetector:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def discover(self) -> dict:
        """BFS over validated edges; emit transitive shortcuts as hypotheses."""
        # build adjacency from validated edges only
        validated = self.store.edges_by_status("validated")
        adj: dict[str, list[tuple[str, float]]] = {}
        for e in validated:
            adj.setdefault(e.src_name, []).append((e.dst_name, e.strength * e.confidence))

        discovered = 0
        for start in list(adj.keys()):
            # explore paths of length >= 2 from `start`
            stack = [(start, [start], 1.0)]
            while stack:
                node, path, score = stack.pop()
                if len(path) - 1 >= self.cfg.emergence_max_depth:
                    continue
                for nxt, w in adj.get(node, []):
                    if nxt in path:
                        continue  # no cycles
                    new_score = score * w * self.cfg.emergence_decay
                    new_path = path + [nxt]
                    # an emergent shortcut: endpoints not yet directly linked
                    if len(new_path) >= 3 and new_score >= self.cfg.emergence_min_confidence \
                            and not self.store.edge_exists(start, nxt):
                        self.store.add_edge(
                            start, nxt, "leads-to", strength=0.6,
                            confidence=round(new_score, 3),
                            origin="emergent", provenance="emergence")
                        discovered += 1
                    stack.append((nxt, new_path, new_score))

        if discovered:
            self.store.log("emergence.run", f"discovered {discovered} emergent shortcut(s)")
        return {"discovered": discovered}
