"""Central configuration for Chiron.

Defaults are tuned so the whole closed loop runs offline (with the stub LLM)
without any external services. Override via ``Config(...)`` or environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- storage ---------------------------------------------------------
    db_path: str = ":memory:"          # SQLite path; ":memory:" for ephemeral demo

    # --- meta-cognition (agi-side) --------------------------------------
    goal_update_every: int = 5          # recompute goals every N recorded turns
    auto_evolve_every: int = 10         # trigger evolution loop every N turns
    gap_promote_hits: int = 2           # a gap becomes an active goal at this hit count
    weak_success_rate: float = 0.70     # capability below this is a weakness
    weak_confidence: float = 0.40

    # --- evolution loop (agi-side) --------------------------------------
    max_goals_per_run: int = 3

    # --- validation gate (agi-side) -------------------------------------
    validate_min_confidence: float = 0.30   # below this, auto-reject without asking the LLM
    doubtful_max_retries: int = 3

    # --- emergence (agi-side) -------------------------------------------
    emergence_max_depth: int = 3
    emergence_min_confidence: float = 0.25
    emergence_decay: float = 0.85           # confidence decay per hop

    # --- promotion (THE FUSION) -----------------------------------------
    promote_min_validated_edges: int = 2    # a cluster needs this many validated edges
    promote_min_confidence: float = 0.50    # ...above this avg confidence to become a skill

    # --- skills + curator (hermes-side) ---------------------------------
    skill_nudge_interval: int = 4           # background review every N turns
    stale_after_uses_idle: int = 8          # turns of non-use before a skill goes stale
    archive_after_uses_idle: int = 20       # ...before it is archived (never deleted)
    curator_min_cluster: int = 2            # min sibling skills to consolidate into an umbrella

    # --- llm -------------------------------------------------------------
    llm_kind: str = field(default_factory=lambda: os.getenv("CHIRON_LLM", "stub"))
    llm_model: str = field(default_factory=lambda: os.getenv("CHIRON_MODEL", "stub-1"))
    llm_base_url: str = field(default_factory=lambda: os.getenv("CHIRON_BASE_URL", ""))
    llm_api_key: str = field(default_factory=lambda: os.getenv("CHIRON_API_KEY", ""))

    def __post_init__(self) -> None:
        if env_db := os.getenv("CHIRON_DB"):
            self.db_path = env_db
