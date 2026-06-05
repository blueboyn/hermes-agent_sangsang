"""창발 탐지기 (agi 쪽): *새로운* 인과 경로를 발견한다.

이미 검증된 엣지들의 그래프를 탐색하여, 아직 직접적으로 주장되지 않은 간접 연결을
찾는다(A -> B -> C는 있지만 A -> C는 없는 경우). 각 발견은 새로운 창발 가설 엣지로
삽입되므로, 그 자체로 corrector를 통과해야만 승격될 수 있다. 이것이 시스템이 "새로운
생각을 떠올리는" 방식이며 — 동시에 그 생각이 수집된 지식과 동일한 증거 기준에 묶이는
방식이다.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class EmergenceDetector:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def discover(self) -> dict:
        """검증된 엣지에 대해 BFS를 수행하고, 추이적(transitive) 지름길을 가설로 방출한다."""
        # 검증된 엣지만으로 인접 리스트를 구성한다
        validated = self.store.edges_by_status("validated")
        adj: dict[str, list[tuple[str, float]]] = {}
        for e in validated:
            adj.setdefault(e.src_name, []).append((e.dst_name, e.strength * e.confidence))

        discovered = 0
        for start in list(adj.keys()):
            # `start`로부터 길이 >= 2인 경로 탐색
            stack = [(start, [start], 1.0)]
            while stack:
                node, path, score = stack.pop()
                if len(path) - 1 >= self.cfg.emergence_max_depth:
                    continue
                for nxt, w in adj.get(node, []):
                    if nxt in path:
                        continue  # 순환 금지
                    new_score = score * w * self.cfg.emergence_decay
                    new_path = path + [nxt]
                    # 창발적 지름길: 양 끝점이 아직 직접 연결되지 않은 경우
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
