"""Curator (hermes 쪽): 스킬의 생명주기 + 통합.

hermes의 운영 규율을 그대로 이어받는다:
  * LLM 없이 이뤄지는 자동 상태 전이: active -> stale -> archived. 순전히 미사용
    시간(여기서는 턴 수로 측정)에 따라 작동한다.
  * 통합(consolidation): 같은 접두사를 공유하는 형제 스킬들을 umbrella 아래로 병합한다.
  * 절대 삭제하지 않는다 — 오직 보관(archive)한다. 고정(pinned)된 스킬은 건드리지 않는다.

이것은 agi 쪽 지식 성장에 대한 안전 균형추다: 승격이 너무 좁은 스킬을 많이 만들어내더라도,
curator가 라이브러리를 클래스 단위로 유지하고 복구 가능하게 지킨다.
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

    # -- 자동, LLM 없는 생명주기 -----------------------------------------
    def _transition(self, turn: int) -> dict:
        out = {"stale": 0, "archived": 0}
        for s in self.store.skills():
            if s["pinned"]:
                continue
            idle = turn - s["last_used_turn"]
            if idle >= self.cfg.archive_after_uses_idle and s["status"] != "archived":
                self.store.set_skill_status(s["id"], "archived")  # 삭제 아님, 복구 가능
                out["archived"] += 1
            elif idle >= self.cfg.stale_after_uses_idle and s["status"] == "active":
                self.store.set_skill_status(s["id"], "stale")
                out["stale"] += 1
        return out

    # -- umbrella로의 통합 -----------------------------------------------
    def _consolidate(self, turn: int) -> list[str]:
        clusters: dict[str, list] = defaultdict(list)
        for s in self.store.skills():
            if s["pinned"] or s["status"] == "archived":
                continue
            # 선행 토큰으로 클러스터링: 'debugging-flaky-tests' -> 'debugging'
            prefix = s["name"].split("-", 1)[0]
            clusters[prefix].append(s)

        consolidated = []
        for prefix, members in clusters.items():
            if len(members) < self.cfg.curator_min_cluster:
                continue
            umbrella = self.llm.name_umbrella(prefix, [m["name"] for m in members])
            body_parts = [f"# {umbrella}", "",
                          "_통합된 umbrella. 출처(provenance): curated._", ""]
            for m in members:
                body_parts.append(f"## {m['name']}\n\n{m['body']}\n")
            self.store.upsert_skill(umbrella, "\n".join(body_parts), origin="curated", turn=turn)
            # 이제 흡수된 형제들을 보관(archive)한다 (복구 가능)
            for m in members:
                if m["name"] != umbrella:
                    self.store.set_skill_status(m["id"], "archived")
            consolidated.append(umbrella)
        return consolidated
