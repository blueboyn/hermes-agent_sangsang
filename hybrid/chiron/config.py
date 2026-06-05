"""Chiron의 중앙 설정.

기본값은 전체 폐루프가 (stub LLM으로) 외부 서비스 없이 오프라인으로 동작하도록
튜닝되어 있다. ``Config(...)`` 또는 환경변수로 재정의할 수 있다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- 저장소 ----------------------------------------------------------
    db_path: str = ":memory:"          # SQLite 경로. 데모용 임시 저장은 ":memory:"

    # --- 메타인지 (agi 쪽) ----------------------------------------------
    goal_update_every: int = 5          # 기록된 턴 N회마다 목표 재계산
    auto_evolve_every: int = 10         # 턴 N회마다 진화 루프 트리거
    gap_promote_hits: int = 2           # 공백이 활성 목표가 되는 hit 횟수 기준
    weak_success_rate: float = 0.70     # 이 값 미만의 능력은 약점으로 간주
    weak_confidence: float = 0.40

    # --- 진화 루프 (agi 쪽) ---------------------------------------------
    max_goals_per_run: int = 3

    # --- 검증 게이트 (agi 쪽) -------------------------------------------
    validate_min_confidence: float = 0.30   # 이 값 미만이면 LLM에 묻지 않고 자동 기각
    doubtful_max_retries: int = 3

    # --- 창발 (agi 쪽) --------------------------------------------------
    emergence_max_depth: int = 3
    emergence_min_confidence: float = 0.25
    emergence_decay: float = 0.85           # 홉(hop)당 신뢰도 감쇠율

    # --- 승격 (융합 지점) -----------------------------------------------
    promote_min_validated_edges: int = 2    # 클러스터가 스킬이 되려면 필요한 검증 엣지 수
    promote_min_confidence: float = 0.50    # ...그 위로 요구되는 평균 신뢰도

    # --- 스킬 + curator (hermes 쪽) -------------------------------------
    skill_nudge_interval: int = 4           # 턴 N회마다 백그라운드 리뷰
    stale_after_uses_idle: int = 8          # 스킬이 stale 되기까지의 미사용 턴 수
    archive_after_uses_idle: int = 20       # ...archive 되기까지의 미사용 턴 수 (삭제 아님)
    curator_min_cluster: int = 2            # umbrella로 통합할 최소 형제 스킬 수

    # --- LLM -------------------------------------------------------------
    llm_kind: str = field(default_factory=lambda: os.getenv("CHIRON_LLM", "stub"))
    llm_model: str = field(default_factory=lambda: os.getenv("CHIRON_MODEL", "stub-1"))
    llm_base_url: str = field(default_factory=lambda: os.getenv("CHIRON_BASE_URL", ""))
    llm_api_key: str = field(default_factory=lambda: os.getenv("CHIRON_API_KEY", ""))

    def __post_init__(self) -> None:
        if env_db := os.getenv("CHIRON_DB"):
            self.db_path = env_db
