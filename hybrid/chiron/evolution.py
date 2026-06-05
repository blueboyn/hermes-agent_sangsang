"""진화 루프 (agi 쪽): 열려 있는 목표를 위해 자율적으로 지식을 수집한다.

실제 agi 시스템에서는 arXiv / 위키피디아로 나가서 텍스트를 추출 파이프라인에 통과시킨다.
여기서는 "수집기(acquirer)"가 교체 가능하다: 데모는 화살표 표기 시드 텍스트를 돌려주는
지식 소스를 공급하고, LLM이 이를 인과 엣지로 변환한다. 수집된 엣지는 *가설(hypothesis)*
로 들어온다 — corrector가 검증하기 전까지는 신뢰되지 않는다.
"""

from __future__ import annotations

from typing import Callable

from .store import Store
from .config import Config
from .llm import LLMClient

# 지식 소스: 주제(topic) -> 사실을 캐낼 원시 텍스트
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
