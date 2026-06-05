"""Smoke tests for the Chiron hybrid loop. Run: python -m pytest -q  (or run
directly with python tests/test_smoke.py for an assert-based check)."""

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
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.meta.update_goals()
    goals = orch.store.active_goals(10)
    assert any(t == "typhoon" and gt == "KNOWLEDGE_GAP" for _, gt, t in goals)
    orch.close()


def test_acquire_validate_promote():
    orch = make_orch()
    orch.store.record_gap("typhoon")
    orch.store.record_gap("oil price")
    report = orch.evolve()
    assert report["acquired_edges"] > 0
    assert report["validated"] > 0
    # at least one topic should have been promoted into a skill
    skill_names = [s["name"] for s in orch.store.skills()]
    assert any(n.startswith("knowledge-") for n in skill_names)
    orch.close()


def test_validation_gate_rejects_bad_edge():
    orch = make_orch()
    orch.store.record_gap("bad")
    orch.meta.update_goals()
    orch.evolution.run_once()
    orch.corrector.verify_pending()
    assert len(orch.store.edges_by_status("rejected")) >= 1
    orch.close()


def test_curator_never_deletes():
    orch = make_orch()
    orch.store.upsert_skill("foo-a", "body", origin="promoted", turn=1)
    orch.store.upsert_skill("foo-b", "body", origin="promoted", turn=1)
    orch.turn = 100  # force everything idle
    orch.curator.run(orch.turn)
    # absorbed/aged skills must still exist (archived), never gone
    all_names = [s["name"] for s in orch.store.skills(include_archived=True)]
    assert "foo-a" in all_names and "foo-b" in all_names
    orch.close()


def test_provenance_origins_present():
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
