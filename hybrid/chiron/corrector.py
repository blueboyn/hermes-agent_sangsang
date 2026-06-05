"""Corrector (agi 쪽): 검증 게이트.

agi로부터 물려받은 가장 중요한 발상이다: *새 지식은 증명되기 전까지 가설이다.* 모든
가설/창발 엣지가 검사된다 — 신뢰도 하한 미달이면 값싸게 기각하고, 아니면 LLM이 판정한다.
판정(verdict):

  * valid     -> 상태 'validated'  (스킬로의 승격 자격 획득)
  * doubtful  -> 'doubtful' 유지, N회까지 재시도 후 자동 기각
  * rejected  -> 상태 'rejected'   (감사를 위해 보존, 절대 조용히 버리지 않음)

의심 추적(doubt-tracking)은 실행 단위의 메모리에서 이뤄지며, agi의 "최대 3회 재검증"과
일치한다.
"""

from __future__ import annotations

from collections import defaultdict

from .store import Store
from .config import Config
from .llm import LLMClient


class Corrector:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm
        self._doubt_counts: dict[int, int] = defaultdict(int)

    def verify_pending(self) -> dict:
        """현재 그래프에 있는 모든 가설 + 의심 엣지를 검증한다."""
        pending = self.store.edges_by_status("hypothesis") + self.store.edges_by_status("doubtful")
        stats = {"validated": 0, "rejected": 0, "doubtful": 0}
        for e in pending:
            # LLM 호출 전 값싼 하한 검사 (agi의 최적화)
            if e.confidence < self.cfg.validate_min_confidence:
                self.store.set_edge_status(e.id, "rejected")
                self.store.record_validation("edge", e.id, "rejected",
                                             "신뢰도 하한 미달", e.confidence)
                stats["rejected"] += 1
                continue

            v = self.llm.validate_edge(e.src_name, e.relation, e.dst_name, e.confidence)
            self.store.record_validation("edge", e.id, v.verdict, v.reason, v.confidence)

            if v.verdict == "valid":
                self.store.set_edge_status(e.id, "validated")
                stats["validated"] += 1
            elif v.verdict == "doubtful":
                self._doubt_counts[e.id] += 1
                if self._doubt_counts[e.id] >= self.cfg.doubtful_max_retries:
                    self.store.set_edge_status(e.id, "rejected")
                    self.store.record_validation("edge", e.id, "rejected",
                                                 "의심 재시도 횟수 소진", v.confidence)
                    stats["rejected"] += 1
                else:
                    self.store.set_edge_status(e.id, "doubtful")
                    stats["doubtful"] += 1
            else:
                self.store.set_edge_status(e.id, "rejected")
                stats["rejected"] += 1

        self.store.log("corrector.run",
                       f"validated={stats['validated']} rejected={stats['rejected']} "
                       f"doubtful={stats['doubtful']}")
        return stats
