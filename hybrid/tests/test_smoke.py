"""Chiron 하이브리드 루프의 스모크 테스트. 실행: python -m pytest -q  (또는
assert 기반 점검을 위해 python tests/test_smoke.py 로 직접 실행)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chiron import Config, Orchestrator  # noqa: E402


def _world(topic: str) -> str:
    return {
        "typhoon": "typhoon -> sea temperature rise -> coral bleaching",
        "oil price": "oil price -> transport cost -> consumer spending",
        "bad": "x -> big bang",
    }.get(topic, "")


def make_orch() -> Orchestrator:
    cfg = Config(gap_promote_hits=1, promote_min_validated_edges=2,
                 promote_min_confidence=0.4)
    return Orchestrator(cfg=cfg, knowledge_source=_world)


def test_gap_to_goal():
    # 공백이 KNOWLEDGE_GAP 목표로 전환되는지 확인
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.meta.update_goals()
    goals = orch.store.active_goals(10)
    assert any(t == "typhoon" and gt == "KNOWLEDGE_GAP" for _, gt, t in goals)
    orch.close()


def test_acquire_validate_promote():
    # 수집 -> 검증 -> 승격이 스킬을 만들어내는지 확인
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.store.record_gap("oil price")
    report = orch.evolve()
    assert report["acquired_edges"] > 0
    assert report["validated"] > 0
    # 최소 한 주제는 스킬로 승격되어야 한다
    skill_names = [s["name"] for s in orch.store.skills()]
    assert any(n.startswith("knowledge-") for n in skill_names)
    orch.close()


def test_validation_gate_rejects_bad_edge():
    # 검증 게이트가 잘못된 엣지를 기각하는지 확인
    orch = make_orch()
    orch.store.record_gap("bad")
    orch.meta.update_goals()
    orch.evolution.run_once()
    orch.corrector.verify_pending()
    assert len(orch.store.edges_by_status("rejected")) >= 1
    orch.close()


def test_curator_never_deletes():
    # curator는 삭제하지 않고 보관(archive)만 하는지 확인
    orch = make_orch()
    orch.store.upsert_skill("foo-a", "body", origin="promoted", turn=1)
    orch.store.upsert_skill("foo-b", "body", origin="promoted", turn=1)
    orch.turn = 100  # 모든 스킬을 강제로 미사용 상태로
    orch.curator.run(orch.turn)
    # 흡수/노후화된 스킬도 여전히 존재해야 한다 (archived 상태, 사라지지 않음)
    all_names = [s["name"] for s in orch.store.skills(include_archived=True)]
    assert "foo-a" in all_names and "foo-b" in all_names
    orch.close()


def test_provenance_origins_present():
    # 출처(origin)가 올바르게 기록되는지 확인
    orch = make_orch()
    orch.background_review = lambda turn: orch.store.upsert_skill(
        "manual-x", "b", origin="background_review", turn=turn)
    orch.store.record_gap("typhoon")
    orch.store.record_gap("oil price")
    orch.evolve()
    orch.background_review(orch.turn)
    origins = {s["origin"] for s in orch.store.skills(include_archived=True)}
    assert "promoted" in origins
    assert "background_review" in origins
    orch.close()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all smoke tests passed")
