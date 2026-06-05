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


def test_skill_has_edge_provenance():
    # Phase 0: 승격된 스킬에서 근거 엣지 id 집합을 1쿼리로 역추적 가능해야 한다
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.evolve()
    promoted = [s for s in orch.store.skills() if s["origin"] == "promoted"]
    assert promoted, "승격된 스킬이 있어야 함"
    for s in promoted:
        edge_ids = orch.store.skill_support_edge_ids(s["id"])
        assert len(edge_ids) >= 1
        # 링크가 가리키는 엣지는 실재해야 한다
        assert all(orch.store.edge_status(eid) is not None for eid in edge_ids)
    orch.close()


def test_retraction_archives_skill():
    # Phase 1: 근거 엣지가 rejected로 바뀌면 파생 스킬이 자동 철회(archive)된다
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.evolve()
    skill = next(s for s in orch.store.skills() if s["origin"] == "promoted")
    for eid in orch.store.skill_support_edge_ids(skill["id"]):
        orch.store.set_edge_status(eid, "rejected")
    result = orch.reconciler.reconcile()
    assert skill["name"] in result["retracted"]
    # 활성 목록에서는 빠지지만
    assert skill["name"] not in [s["name"] for s in orch.store.skills()]
    # 보관본으로는 여전히 복구 가능해야 한다
    assert skill["name"] in [s["name"] for s in orch.store.skills(include_archived=True)]
    orch.close()


def test_promoted_skill_not_idle_archived_without_use():
    # Phase 1 (D-5 가드): 소비된 적 없는 promoted 스킬은 idle만으로 archive되지 않는다
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.evolve()
    skill = next(s for s in orch.store.skills() if s["origin"] == "promoted")
    orch.turn = 9999  # 강제로 한참 미사용 상태로
    orch.curator.run(orch.turn)
    active = [s["name"] for s in orch.store.skills()]
    assert skill["name"] in active, "사용 신호 없는 승격 스킬이 idle로 archive되면 안 됨"
    orch.close()


def test_non_derived_skill_survives_reconcile():
    # Reconciler는 지식에서 파생되지 않은(근거 링크 없는) 스킬은 건드리지 않는다
    orch = make_orch()
    orch.store.upsert_skill("manual-note", "body", origin="foreground", turn=1)
    result = orch.reconciler.reconcile()
    assert "manual-note" not in result["retracted"]
    assert "manual-note" in [s["name"] for s in orch.store.skills()]
    orch.close()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all smoke tests passed")
