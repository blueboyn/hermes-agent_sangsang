"""메타인지 (agi 쪽): 자기 모니터링 + 목표 생성.

에이전트 자신의 능력 통계와 해소되지 않은 지식 공백을 지켜보다가, 약점을 우선순위가
매겨진 학습 목표로 전환한다. 이것이 루프의 "무위자연 / 데이터가 무엇을 배워야 할지
알려주게 둔다" 절반에 해당한다.
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
        """공백 + 능력 약점으로부터 활성 목표 집합을 재계산한다."""
        created = 0
        for keyword, hits in self.store.active_gaps(self.cfg.gap_promote_hits):
            # 우선순위는 공백이 얼마나 자주 부딪혔는지에 비례한다
            self.store.upsert_goal("KNOWLEDGE_GAP", keyword, priority=min(hits, 10))
            created += 1
        for action in self.store.weaknesses(self.cfg.weak_success_rate, self.cfg.weak_confidence):
            self.store.upsert_goal("CAPABILITY_FIX", action, priority=8)
            created += 1
        if created:
            self.store.log("goals.update", f"{created} goal(s) refreshed")
        return created
