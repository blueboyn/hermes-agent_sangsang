"""Reconciler (Phase 1: D-3 본체): 지식이 바뀌면 행동이 따라오게 한다.

승격(promotion)은 단방향 다리였다 — 한번 검증된 사슬에서 스킬이 나오면, 나중에 그
근거 엣지가 rejected로 뒤집혀도 스킬을 끌어내릴 방법이 없었다(자가 진화 시스템의
자기모순). Reconciler가 그 역방향을 채운다:

  근거 엣지가 더 이상 충분히 살아있지(validated) 않으면 → 해당 스킬을 **철회(retract)**한다.

핵심 불변식은 그대로 지킨다 — 철회는 삭제가 아니라 보관(archive)이다. origin은 보존되고,
철회 사유가 감사 로그(validations: 'retraction')에 남으며, `skills(include_archived=True)`
로 언제든 복구 가능하다.

근거 링크(skill_edges)가 없는 스킬(foreground / background_review / curated 중 직접
저작된 것)은 자연히 대상에서 빠진다 — 이 모듈은 *지식에서 파생된* 스킬만 다룬다.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class Reconciler:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def reconcile(self) -> dict:
        """살아있는 근거가 임계 미만으로 떨어진 파생 스킬을 철회(archive)한다."""
        retracted: list[str] = []
        for s in self.store.skills():  # 보관되지 않은 스킬만
            support_ids = self.store.skill_support_edge_ids(s["id"])
            if not support_ids:
                continue  # 지식에서 파생되지 않은 스킬 — 대상 아님
            live = [eid for eid in support_ids
                    if self.store.edge_status(eid) == "validated"]
            if len(live) < self.cfg.promote_min_validated_edges:
                self.store.set_skill_status(s["id"], "archived")  # 삭제 아님, 복구 가능
                self.store.record_validation(
                    "retraction", s["id"], "archive",
                    f"근거 약화: {len(live)}/{len(support_ids)} 엣지만 validated", 0.0)
                retracted.append(s["name"])
        if retracted:
            self.store.log("reconcile.run", f"retracted: {', '.join(retracted)}")
        return {"retracted": retracted}
