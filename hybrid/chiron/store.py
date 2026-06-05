"""통합 저장소: *선언적 지식*(agi 방식)과 *절차적 스킬*(hermes 방식)이 출처
(provenance)와 함께 한곳에 나란히 사는 유일한 장소.

이것이 구조적 융합 지점이다. agi는 지식을 MySQL+Neo4j에, hermes는 스킬을 Markdown
파일에 보관했다. Chiron은 둘 다 하나의 SQLite 데이터베이스에 담아서 *승격*
단계(지식 -> 스킬)가 ETL 작업이 아니라 로컬 트랜잭션이 되게 한다.

두 부모로부터 이어받은 설계 규칙:
  * hermes: 절대 삭제하지 않는다 — 보관(archive)한다. 모든 기록은 출처를 갖는다.
  * agi: 엣지는 생명주기 상태를 갖는다 (hypothesis -> validated / rejected).
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass


def _now() -> float:
    return time.time()


SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'unknown',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY,
    src INTEGER NOT NULL,
    dst INTEGER NOT NULL,
    relation TEXT NOT NULL,
    strength REAL NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'hypothesis',   -- 가설|검증됨|기각됨|의심  (hypothesis|validated|rejected|doubtful)
    origin TEXT NOT NULL DEFAULT 'acquired',      -- 수집됨|창발됨  (acquired|emergent)
    provenance TEXT NOT NULL DEFAULT 'evolution',
    created_at REAL NOT NULL,
    UNIQUE(src, dst, relation)
);
CREATE TABLE IF NOT EXISTS gaps (
    keyword TEXT PRIMARY KEY,
    hits INTEGER NOT NULL DEFAULT 1,
    resolved INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    gtype TEXT NOT NULL,            -- 지식공백|능력보완  (KNOWLEDGE_GAP|CAPABILITY_FIX)
    target TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',  -- 활성|완료  (active|done)
    UNIQUE(gtype, target)
);
CREATE TABLE IF NOT EXISTS capability (
    action TEXT PRIMARY KEY,
    attempts INTEGER NOT NULL DEFAULT 0,
    successes INTEGER NOT NULL DEFAULT 0,
    conf_sum REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    body TEXT NOT NULL,
    origin TEXT NOT NULL,           -- 전경|백그라운드리뷰|승격|큐레이션  (foreground|background_review|promoted|curated)
    status TEXT NOT NULL DEFAULT 'active',  -- 활성|오래됨|보관됨  (active|stale|archived)
    pinned INTEGER NOT NULL DEFAULT 0,
    uses INTEGER NOT NULL DEFAULT 0,
    last_used_turn INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS skill_edges (
    skill_id INTEGER NOT NULL,
    edge_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'support',   -- 근거|머리  (support|head)
    created_turn INTEGER NOT NULL,
    PRIMARY KEY (skill_id, edge_id)
);
CREATE TABLE IF NOT EXISTS validations (
    id INTEGER PRIMARY KEY,
    target_type TEXT NOT NULL,      -- 엣지|승격  (edge|promotion)
    target_id INTEGER NOT NULL,
    verdict TEXT NOT NULL,
    reason TEXT,
    confidence REAL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


@dataclass
class Edge:
    id: int
    src_name: str
    dst_name: str
    relation: str
    strength: float
    confidence: float
    status: str
    origin: str


class Store:
    def __init__(self, db_path: str = ":memory:"):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    # -- 감사 로그 --------------------------------------------------------
    def log(self, kind: str, detail: str) -> None:
        self.db.execute("INSERT INTO audit(kind, detail, created_at) VALUES (?,?,?)",
                        (kind, detail, _now()))
        self.db.commit()

    # -- 지식 그래프 ------------------------------------------------------
    def node_id(self, name: str, category: str = "unknown") -> int:
        cur = self.db.execute("SELECT id FROM nodes WHERE name=?", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur = self.db.execute(
            "INSERT INTO nodes(name, category, created_at) VALUES (?,?,?)",
            (name, category, _now()))
        self.db.commit()
        return cur.lastrowid

    def has_node(self, name: str) -> bool:
        return self.db.execute("SELECT 1 FROM nodes WHERE name=?", (name,)).fetchone() is not None

    def add_edge(self, src: str, dst: str, relation: str, strength: float,
                 confidence: float, origin: str = "acquired",
                 provenance: str = "evolution") -> int:
        s, d = self.node_id(src), self.node_id(dst)
        cur = self.db.execute(
            """INSERT OR IGNORE INTO edges
               (src, dst, relation, strength, confidence, origin, provenance, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (s, d, relation, strength, confidence, origin, provenance, _now()))
        self.db.commit()
        if cur.lastrowid:
            return cur.lastrowid
        return self.db.execute(
            "SELECT id FROM edges WHERE src=? AND dst=? AND relation=?",
            (s, d, relation)).fetchone()["id"]

    def set_edge_status(self, edge_id: int, status: str) -> None:
        self.db.execute("UPDATE edges SET status=? WHERE id=?", (status, edge_id))
        self.db.commit()

    def edges_by_status(self, status: str) -> list[Edge]:
        rows = self.db.execute(
            """SELECT e.id, ns.name src, nd.name dst, e.relation, e.strength,
                      e.confidence, e.status, e.origin
               FROM edges e JOIN nodes ns ON e.src=ns.id JOIN nodes nd ON e.dst=nd.id
               WHERE e.status=?""", (status,)).fetchall()
        return [Edge(r["id"], r["src"], r["dst"], r["relation"], r["strength"],
                     r["confidence"], r["status"], r["origin"]) for r in rows]

    def out_edges(self, name: str, only_validated: bool = True) -> list[Edge]:
        clause = "AND e.status='validated'" if only_validated else ""
        rows = self.db.execute(
            f"""SELECT e.id, ns.name src, nd.name dst, e.relation, e.strength,
                       e.confidence, e.status, e.origin
                FROM edges e JOIN nodes ns ON e.src=ns.id JOIN nodes nd ON e.dst=nd.id
                WHERE ns.name=? {clause}""", (name,)).fetchall()
        return [Edge(r["id"], r["src"], r["dst"], r["relation"], r["strength"],
                     r["confidence"], r["status"], r["origin"]) for r in rows]

    def edge_status(self, edge_id: int) -> str | None:
        row = self.db.execute("SELECT status FROM edges WHERE id=?", (edge_id,)).fetchone()
        return row["status"] if row else None

    def edge_exists(self, src: str, dst: str) -> bool:
        row = self.db.execute(
            """SELECT 1 FROM edges e JOIN nodes ns ON e.src=ns.id
               JOIN nodes nd ON e.dst=nd.id WHERE ns.name=? AND nd.name=?""",
            (src, dst)).fetchone()
        return row is not None

    # -- 공백 & 목표 ------------------------------------------------------
    def record_gap(self, keyword: str) -> int:
        self.db.execute(
            """INSERT INTO gaps(keyword, hits) VALUES (?, 1)
               ON CONFLICT(keyword) DO UPDATE SET hits = hits + 1""", (keyword,))
        self.db.commit()
        return self.db.execute("SELECT hits FROM gaps WHERE keyword=?", (keyword,)).fetchone()["hits"]

    def active_gaps(self, min_hits: int) -> list[tuple[str, int]]:
        rows = self.db.execute(
            "SELECT keyword, hits FROM gaps WHERE resolved=0 AND hits>=? ORDER BY hits DESC",
            (min_hits,)).fetchall()
        return [(r["keyword"], r["hits"]) for r in rows]

    def resolve_gap(self, keyword: str) -> None:
        self.db.execute("UPDATE gaps SET resolved=1 WHERE keyword=?", (keyword,))
        self.db.commit()

    def upsert_goal(self, gtype: str, target: str, priority: int) -> None:
        self.db.execute(
            """INSERT OR IGNORE INTO goals(gtype, target, priority) VALUES (?,?,?)""",
            (gtype, target, priority))
        self.db.commit()

    def active_goals(self, limit: int) -> list[tuple[int, str, str]]:
        rows = self.db.execute(
            "SELECT id, gtype, target FROM goals WHERE status='active' ORDER BY priority DESC LIMIT ?",
            (limit,)).fetchall()
        return [(r["id"], r["gtype"], r["target"]) for r in rows]

    def complete_goal(self, goal_id: int) -> None:
        self.db.execute("UPDATE goals SET status='done' WHERE id=?", (goal_id,))
        self.db.commit()

    # -- 능력(capability) -------------------------------------------------
    def record_capability(self, action: str, success: bool, confidence: float) -> None:
        self.db.execute(
            """INSERT INTO capability(action, attempts, successes, conf_sum)
               VALUES (?,1,?,?)
               ON CONFLICT(action) DO UPDATE SET
                 attempts=attempts+1, successes=successes+?, conf_sum=conf_sum+?""",
            (action, int(success), confidence, int(success), confidence))
        self.db.commit()

    def weaknesses(self, min_rate: float, min_conf: float) -> list[str]:
        rows = self.db.execute("SELECT * FROM capability WHERE attempts>=3").fetchall()
        weak = []
        for r in rows:
            rate = r["successes"] / r["attempts"]
            conf = r["conf_sum"] / r["attempts"]
            if rate < min_rate or conf < min_conf:
                weak.append(r["action"])
        return weak

    # -- 검증 기록 --------------------------------------------------------
    def record_validation(self, target_type: str, target_id: int, verdict: str,
                          reason: str, confidence: float) -> None:
        self.db.execute(
            """INSERT INTO validations(target_type, target_id, verdict, reason, confidence, created_at)
               VALUES (?,?,?,?,?,?)""",
            (target_type, target_id, verdict, reason, confidence, _now()))
        self.db.commit()

    # -- 스킬 -------------------------------------------------------------
    def upsert_skill(self, name: str, body: str, origin: str, turn: int) -> int:
        existing = self.db.execute("SELECT id FROM skills WHERE name=?", (name,)).fetchone()
        if existing:
            self.db.execute(
                "UPDATE skills SET body=?, status='active', last_used_turn=? WHERE id=?",
                (body, turn, existing["id"]))
            self.db.commit()
            return existing["id"]
        cur = self.db.execute(
            """INSERT INTO skills(name, body, origin, last_used_turn, created_at)
               VALUES (?,?,?,?,?)""", (name, body, origin, turn, _now()))
        self.db.commit()
        return cur.lastrowid

    def touch_skill(self, name: str, turn: int) -> bool:
        row = self.db.execute("SELECT id FROM skills WHERE name=? AND status!='archived'",
                              (name,)).fetchone()
        if not row:
            return False
        self.db.execute(
            "UPDATE skills SET uses=uses+1, last_used_turn=?, status='active' WHERE id=?",
            (turn, row["id"]))
        self.db.commit()
        return True

    def skills(self, include_archived: bool = False) -> list[sqlite3.Row]:
        clause = "" if include_archived else "WHERE status!='archived'"
        return self.db.execute(f"SELECT * FROM skills {clause} ORDER BY name").fetchall()

    def set_skill_status(self, skill_id: int, status: str) -> None:
        self.db.execute("UPDATE skills SET status=? WHERE id=?", (status, skill_id))
        self.db.commit()

    # -- 스킬 <-> 엣지 출처 링크 (Phase 0: D-3 전제) ----------------------
    def clear_skill_edges(self, skill_id: int) -> None:
        self.db.execute("DELETE FROM skill_edges WHERE skill_id=?", (skill_id,))
        self.db.commit()

    def link_skill_edge(self, skill_id: int, edge_id: int, role: str, turn: int) -> None:
        self.db.execute(
            """INSERT OR IGNORE INTO skill_edges(skill_id, edge_id, role, created_turn)
               VALUES (?,?,?,?)""", (skill_id, edge_id, role, turn))
        self.db.commit()

    def skill_support_edge_ids(self, skill_id: int) -> list[int]:
        rows = self.db.execute(
            "SELECT edge_id FROM skill_edges WHERE skill_id=?", (skill_id,)).fetchall()
        return [r["edge_id"] for r in rows]

    def skills_depending_on(self, edge_id: int) -> list[int]:
        rows = self.db.execute(
            "SELECT skill_id FROM skill_edges WHERE edge_id=?", (edge_id,)).fetchall()
        return [r["skill_id"] for r in rows]

    def pin_skill(self, name: str, pinned: bool = True) -> None:
        self.db.execute("UPDATE skills SET pinned=? WHERE name=?", (int(pinned), name))
        self.db.commit()

    def close(self) -> None:
        self.db.close()
