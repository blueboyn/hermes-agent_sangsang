# Chiron — a hybrid self-evolution engine

> Knowledge grows like **상상이(agi)**. Behaviour changes like **Hermes**.
> But nothing steers the agent until it has passed the gate.

Chiron is a small, self-contained engine that fuses the two self-evolution
philosophies found in the sibling repos `agi` and `hermes-agent_sangsang`:

| Parent | What it evolves | Strength Chiron keeps |
|--------|-----------------|------------------------|
| **agi / 상상이** | *Declarative knowledge* — a causal graph that grows by detecting gaps, acquiring knowledge, and discovering novel connections (emergence). | The system can genuinely **learn new things about the world** and form new hypotheses. |
| **Hermes** | *Procedural skill* — reusable `SKILL.md` know-how, captured from experience, consolidated and aged by a curator, never deleted. | **Safe, recoverable, operational** self-improvement with provenance and human control. |

The problem with each on its own:

- agi can be **wrong at scale** — a hallucinated fact enters the graph and
  silently underpins later reasoning. Pollution compounds.
- Hermes is **safe but never gets smarter about the world** — it only refines
  *how it works*, never *what it knows*.

**Chiron's thesis:** let knowledge grow freely (agi), but **gate every new fact
through validation**, and **promote only validated, recurring knowledge into
procedural skills** (Hermes). A fact may be wrong — but it cannot influence the
agent's behaviour until it has (a) survived the validation gate and (b) formed a
stable, recurring pattern worth turning into a skill.

```
gaps ─▶ goals ─▶ acquire(hypotheses) ─▶ [VALIDATION GATE] ─▶ validated knowledge
                                              │                        │
                              emergence ◀─────┘                        ▼
                          (novel hypotheses) ─▶ [GATE again] ─▶ ─▶ PROMOTION ─▶ skills
                                                                          │
                                                          curator: consolidate / age / archive
                                                            (never delete · provenance · pin)
```

## Quick start (fully offline — no API key, no DB server)

```bash
cd hybrid
python3 examples/demo.py      # end-to-end walkthrough
python3 tests/test_smoke.py   # or: pytest -q
```

The demo uses a deterministic **stub LLM** and in-memory SQLite, so the entire
closed loop runs with zero external dependencies. To use a real model:

```bash
export CHIRON_LLM=openai
export CHIRON_BASE_URL=https://openrouter.ai/api/v1   # any OpenAI-compatible endpoint
export CHIRON_API_KEY=sk-...
export CHIRON_MODEL=anthropic/claude-3.5-sonnet
```

## What the demo shows

1. **Gaps → goals.** Interactions mention unknown terms; repeated misses become
   prioritized `KNOWLEDGE_GAP` goals (agi's meta-cognition).
2. **Acquire → validate.** The evolution loop pulls knowledge for open goals as
   *hypotheses*; the **corrector** validates each edge. `coral bleaching → big
   bang` is rejected — an effect can't precede a cosmic origin.
3. **Emergence → validate again.** New transitive shortcuts are discovered and
   held to the *same* evidentiary bar; weak ones are rejected.
4. **Promotion (the fusion).** Topics whose validated causal chain is strong and
   recurring are synthesized into `knowledge-*` skills (`origin=promoted`).
5. **Curation (Hermes discipline).** Sibling skills (`debugging-*`,
   `knowledge-*`) are consolidated under `*-umbrella` skills; absorbed siblings
   are **archived, not deleted**.

## Layout

```
hybrid/
├── README.md            ← you are here
├── ARCHITECTURE.md      ← the fusion design, component-by-component
├── requirements.txt     ← stdlib only
├── chiron/
│   ├── config.py        ← all thresholds / knobs
│   ├── store.py         ← unified SQLite store: knowledge graph + skills + provenance + audit
│   ├── llm.py           ← LLMClient protocol · offline StubLLM · OpenAI-compatible client
│   ├── metacognition.py ← [agi] capability tracking + goal generation
│   ├── evolution.py     ← [agi] acquire knowledge for open goals (as hypotheses)
│   ├── corrector.py     ← [agi] THE VALIDATION GATE (valid / doubtful / rejected)
│   ├── emergence.py     ← [agi] discover novel transitive shortcuts
│   ├── promotion.py     ← [FUSION] validated knowledge chain → procedural skill
│   ├── curator.py       ← [hermes] consolidate · age · archive (never delete)
│   └── orchestrator.py  ← the closed loop on two timescales (per-turn + periodic)
├── examples/demo.py
└── tests/test_smoke.py
```

## Design invariants (inherited, on purpose)

- **Hypothesis until proven** (agi): acquired and emergent edges start as
  `hypothesis` and only become `validated` through the corrector.
- **Never delete** (Hermes): the curator archives; archives are recoverable.
- **Provenance on every write**: skills carry `origin ∈ {foreground,
  background_review, promoted, curated}`; only agent-grown skills are curator-managed.
- **Graceful degradation**: no reachable LLM ⇒ the stub keeps the loop alive.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full rationale and the mapping
back to specific mechanisms in `agi` and `hermes`.
