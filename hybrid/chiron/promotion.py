"""승격 (융합 지점): 검증된 선언적 지식을 절차적 스킬로 전환한다.

이 모듈이 Chiron의 핵심이다. agi는 지식 그래프를 키우고, hermes는 스킬을 키우지만,
어느 쪽도 둘을 잇지 않는다. 승격은 다음을 수행한다:

  1. 각 *사슬 머리(chain head)* — 인과 사슬을 이끄는 주제(검증된 엣지들 사이에서
     출발점(source)이지만 도착점(destination)은 한 번도 되지 않는 노드) — 를 찾는다.
  2. 그 머리로부터 도달 가능한 *검증된* 엣지의 사슬 전체를 모은다.
  3. 사슬이 충분히 많고 신뢰도가 높은 검증 엣지를 가진 머리는 노이즈가 아니라 안정적이고
     재사용 가능한 패턴으로 간주되어 SKILL.md로 합성된다.
  4. 스킬은 origin='promoted'(승격)로 기록된다.

따라서 하나의 사실은 (a) 검증 게이트를 통과하고 (b) 반복되는 다단계 패턴을 형성한
뒤에야 비로소 *스킬*(에이전트가 실제로 따르게 되는 것)이 된다. 지식은 틀릴 수 있지만,
절차적 지위를 얻기 전까지는 행동을 조용히 좌우할 수 없다.
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
        """`head`로부터 도달 가능한 모든 검증 엣지 (비순환 BFS)."""
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

        # 사슬 머리: 사슬을 이끌지만 자신은 하류 결과가 아닌 노드
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
            skill_id = self.store.upsert_skill(name, body, origin="promoted", turn=turn)
            # Phase 0: 스킬이 어떤 검증 엣지에서 나왔는지 구조적으로 기록한다.
            # 재승격 시 링크를 현재 사슬과 일치하도록 새로 고친다 (오래된 링크 제거).
            self.store.clear_skill_edges(skill_id)
            for e in chain:
                role = "head" if e.src_name == head else "support"
                self.store.link_skill_edge(skill_id, e.id, role, turn)
            self.store.record_validation("promotion", self.store.node_id(head),
                                         "approve", f"{len(chain)} validated edges", avg_conf)
            promoted.append(name)

        if promoted:
            self.store.log("promotion.run", f"promoted skills: {', '.join(promoted)}")
        return {"promoted": promoted}
