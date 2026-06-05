"""Orchestrator: 폐쇄형 자가 진화 루프.

두 부모의 루프를 두 가지 시간 척도(timescale)에서 결합한다:

  턴 단위 (hermes의 즉시 리뷰 + agi의 모니터링)
    observe()  -> 능력 기록, 지식 공백 탐지
    nudge      -> N턴마다 백그라운드 스킬 리뷰 실행

  주기 단위 (agi의 진화/창발 + hermes의 큐레이션)
    evolve()   -> 메타인지 목표 -> 지식 수집(가설)
               -> corrector 검증 -> 창발 발견 -> corrector 재검증
               -> 검증된 지식을 스킬로 승격
               -> curator가 스킬을 통합/노후화

`tick()`은 턴 카운터를 진행시키며 도래한 작업을 발동한다. 데모가 이를 구동한다.
실제 운영에서는 주기 단위 절반이 hermes의 idle 트리거 백그라운드 fork 위에서 돌게 된다.
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
from .reconciler import Reconciler
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
        self.reconciler = Reconciler(self.store, self.cfg)
        self.curator = Curator(self.store, self.cfg, self.llm)
        self.turn = 0
        # 백그라운드 리뷰가 스킬을 쓰고자 할 때 발동되는 선택적 훅
        self.background_review: Callable[[int], None] | None = None

    # -- 턴 단위 ----------------------------------------------------------
    def observe(self, action: str, success: bool, confidence: float,
                unknown_terms: list[str] | None = None) -> None:
        """하나의 상호작용 결과와 그것이 드러낸 지식 공백을 기록한다."""
        self.turn += 1
        self.meta.record(action, success, confidence)
        for term in (unknown_terms or []):
            if not self.store.has_node(term):
                self.store.record_gap(term)

        if self.turn % self.cfg.goal_update_every == 0:
            self.meta.update_goals()
        if self.cfg.skill_nudge_interval and self.turn % self.cfg.skill_nudge_interval == 0:
            if self.background_review:
                self.background_review(self.turn)  # hermes식 즉시 리뷰
        if self.turn % self.cfg.auto_evolve_every == 0:
            self.evolve()

    def use_skill(self, name: str) -> bool:
        """스킬을 사용됨으로 표시한다 (stale/archive 경로에서 벗어나게 함)."""
        return self.store.touch_skill(name, self.turn)

    # -- 주기 단위 --------------------------------------------------------
    def evolve(self) -> dict:
        """하나의 완전한 진화 사이클: 수집 -> 검증 -> 발견 -> 검증 -> 승격 -> 큐레이션."""
        self.meta.update_goals()
        acquired = self.evolution.run_once()
        v1 = self.corrector.verify_pending()
        emerged = self.emergence.discover()
        v2 = self.corrector.verify_pending()
        promoted = self.promoter.promote(self.turn)
        # 지식이 바뀌었으니(이번 사이클의 기각 포함) 파생 스킬을 정합화한다.
        # 철회된 지식이 umbrella로 통합되지 않도록 curator보다 먼저 실행한다.
        reconciled = self.reconciler.reconcile()
        curated = self.curator.run(self.turn)
        report = {
            "turn": self.turn,
            "acquired_edges": acquired["edges"],
            "validated": v1["validated"] + v2["validated"],
            "rejected": v1["rejected"] + v2["rejected"],
            "emergent": emerged["discovered"],
            "promoted_skills": promoted["promoted"],
            "retracted_skills": reconciled["retracted"],
            "curator": curated,
        }
        self.store.log("evolve.cycle", str(report))
        return report

    # -- 내부 상태 조회 ---------------------------------------------------
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
