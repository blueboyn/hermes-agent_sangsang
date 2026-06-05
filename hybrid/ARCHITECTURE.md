# Chiron architecture — fusing two self-evolution philosophies

This document explains *why* Chiron is built the way it is, and maps each piece
back to the mechanism it inherits from `agi/상상이` or `hermes`.

## 1. The two parents, in one paragraph each

**agi / 상상이** treats self-evolution as **knowledge growth**. A causal
knowledge graph (MySQL + Neo4j) expands through a long autonomous pipeline:
`meta_cognition` detects weaknesses and unmet `knowledge_gap`s → `evolution_loop`
auto-collects papers/wiki and extracts events+relations → `emergence_detector`
finds novel indirect paths, bridge nodes, and analogies → `corrector` validates
those discoveries with an LLM (valid/doubtful/rejected, with direction reversal)
→ validated paths are interpreted and *solidified*. It can even generate new
Python handlers (`module_factory`). It is ambitious and genuinely learns about
the world — but a wrong fact, once solidified, can quietly underpin later
reasoning.

**hermes** treats self-evolution as **procedural skill growth**. The unit is a
reusable `SKILL.md`. After turns, a background-review fork asks "did I learn a
reusable procedure / get corrected?" and writes or patches a skill. A weekly
`curator` consolidates sibling skills into class-level umbrellas, ages unused
ones to `stale`/`archived`, and **never deletes**. Every write carries
provenance; bundled/pinned skills are protected. It is safe, recoverable, and
operationally mature — but it never learns new facts about the world, only how
it works.

## 2. The gap Chiron closes

Neither parent connects the two kinds of memory:

- agi grows **declarative** knowledge with no notion of "this is now a reusable
  procedure I should be guided by."
- hermes grows **procedural** skill with no mechanism to *discover* new
  knowledge — it only captures what a human or a session already demonstrated.

Chiron adds a **promotion bridge**: validated declarative knowledge that forms a
stable, recurring pattern is synthesized into a procedural skill. This gives the
agent agi's reach (it can learn new things) under hermes' safety model (those
learnings can't steer behaviour until validated *and* promoted, and are always
recoverable).

## 3. The unified store (`store.py`)

agi spread knowledge across MySQL and Neo4j; hermes kept skills as Markdown
files. Chiron puts **both** in one SQLite database so promotion is a local
transaction rather than a cross-system ETL:

- `nodes`, `edges` — the causal knowledge graph. Edges carry a **lifecycle
  status** (`hypothesis → validated | rejected | doubtful`) and an `origin`
  (`acquired | emergent`), directly mirroring agi.
- `gaps`, `goals`, `capability` — meta-cognition state.
- `skills` — procedural memory with hermes' fields: `origin`
  (`foreground | background_review | promoted | curated`), `status`
  (`active | stale | archived`), `pinned`, `uses`, `last_used_turn`.
- `validations`, `audit` — every verdict and every state change is recorded.
  Nothing happens silently.

## 4. Components and their lineage

| Module | Inherits from | Role |
|--------|---------------|------|
| `metacognition.py` | agi `meta_cognition.py` | Track per-action success/confidence; turn gaps + weaknesses into prioritized goals. |
| `evolution.py` | agi `evolution_loop.py` | For each open `KNOWLEDGE_GAP` goal, acquire knowledge via a pluggable source and add edges **as hypotheses**. |
| `corrector.py` | agi `corrector.py` | **The validation gate.** Cheap confidence-floor reject, else LLM judges each edge: valid / doubtful (retried ≤N, then rejected) / rejected. |
| `emergence.py` | agi `emergence_detector.py` | BFS over *validated* edges to discover transitive shortcuts, inserted as new hypotheses (so they face the gate too). |
| `promotion.py` | **new (the fusion)** | Gather each validated causal chain; if strong and recurring, synthesize a `knowledge-*` skill with `origin=promoted`. |
| `curator.py` | hermes `curator.py` | Age skills (`active→stale→archived`), consolidate sibling prefixes into `*-umbrella` skills, **archive not delete**, respect `pinned`. |
| `orchestrator.py` | both | Drive the closed loop on two timescales. |

## 5. The closed loop, on two timescales

**Per-turn (immediate — hermes' review + agi's monitoring).**
`observe(action, success, confidence, unknown_terms)`:
- records capability stats and any knowledge gaps,
- every `goal_update_every` turns, recomputes goals,
- every `skill_nudge_interval` turns, fires the **background review** hook
  (hermes-style immediate skill capture),
- every `auto_evolve_every` turns, runs a full periodic cycle.

**Periodic (agi's evolution/emergence + hermes' curation).** `evolve()`:
```
update_goals
  → evolution.run_once()      # acquire hypotheses
  → corrector.verify_pending()# GATE
  → emergence.discover()      # new hypotheses
  → corrector.verify_pending()# GATE again
  → promoter.promote()        # validated chains → skills   ← THE FUSION
  → curator.run()             # consolidate / age / archive
```

The ordering is the safety argument made concrete: **two gates** stand between
"the system had an idea" and "the idea became a skill that guides behaviour."

## 6. Why this is safer than agi alone, smarter than hermes alone

- **Versus agi:** a hallucinated edge is rejected at the gate, or — if it slips
  through as merely plausible — it still cannot influence behaviour unless it
  *also* forms a strong recurring chain that promotion turns into a skill. And
  even then the curator can archive it. There is no silent "solidified forever."
- **Versus hermes:** the agent is no longer limited to refining *how* it works.
  Through gaps → acquisition → emergence it forms genuinely new knowledge — but
  pays hermes' safety tax (provenance, archival, validation) on the way in.

## 7. What is intentionally simplified (and where the real systems differ)

This is a **design + working skeleton**, not a production system. The stub LLM
uses transparent heuristics so the loop is deterministic and testable; the
knowledge "source" is arrow-notation seed text instead of real arXiv/Wikipedia
retrieval; the graph is SQLite rather than Neo4j; and the periodic loop is driven
explicitly rather than by hermes' idle-triggered background fork. Each of these
is a single, clearly-marked seam:

- swap `StubLLM` for `OpenAICompatibleLLM` (already implemented) via env vars,
- replace `knowledge_source` with a real retriever,
- back `store.py` with Neo4j/Postgres if graph scale demands it,
- move `Orchestrator.evolve()` onto hermes' idle/cron scheduler.

The architecture — gaps → goals → acquire → **gate** → emerge → **gate** →
**promote** → curate, all provenance-tracked and recoverable — is the
contribution, and it runs today.
