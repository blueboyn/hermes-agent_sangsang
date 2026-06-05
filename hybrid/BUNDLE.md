# Chiron — 하이브리드 자가 진화 엔진 · 전체 소스 번들

> 이 단일 파일은 `hybrid/` 프로젝트의 **모든 문서와 소스코드**를 하나로 묶은 것입니다.
> Claude(또는 다른 LLM)에게 통째로 붙여넣어 프로젝트 전체 맥락을 한 번에 전달하는 용도입니다.


생성일: 2026-06-05  ·  레포: `hermes-agent_sangsang`  ·  브랜치: `claude/hermes-agi-self-evolution-jBgjI`


## 파일 목록

```
hybrid/
├── README.md
├── ARCHITECTURE.md
├── CONCEPT_KR.md
├── requirements.txt
├── chiron/__init__.py
├── chiron/config.py
├── chiron/store.py
├── chiron/llm.py
├── chiron/metacognition.py
├── chiron/evolution.py
├── chiron/corrector.py
├── chiron/emergence.py
├── chiron/promotion.py
├── chiron/curator.py
├── chiron/orchestrator.py
├── examples/demo.py
├── tests/test_smoke.py
```

## 목차

1. [`README.md`](#1-readmemd)
2. [`ARCHITECTURE.md`](#2-architecturemd)
3. [`CONCEPT_KR.md`](#3-conceptkrmd)
4. [`requirements.txt`](#4-requirementstxt)
5. [`chiron/__init__.py`](#5-chironinitpy)
6. [`chiron/config.py`](#6-chironconfigpy)
7. [`chiron/store.py`](#7-chironstorepy)
8. [`chiron/llm.py`](#8-chironllmpy)
9. [`chiron/metacognition.py`](#9-chironmetacognitionpy)
10. [`chiron/evolution.py`](#10-chironevolutionpy)
11. [`chiron/corrector.py`](#11-chironcorrectorpy)
12. [`chiron/emergence.py`](#12-chironemergencepy)
13. [`chiron/promotion.py`](#13-chironpromotionpy)
14. [`chiron/curator.py`](#14-chironcuratorpy)
15. [`chiron/orchestrator.py`](#15-chironorchestratorpy)
16. [`examples/demo.py`](#16-examplesdemopy)
17. [`tests/test_smoke.py`](#17-teststestsmokepy)

---

## 1. `README.md`

````markdown
# Chiron — 하이브리드 자가 진화 엔진

> 지식은 **상상이(agi)**처럼 자란다. 행동은 **Hermes**처럼 바뀐다.
> 하지만 그 무엇도 게이트를 통과하기 전까지는 에이전트를 조종하지 못한다.

Chiron은 자매 레포 `agi`와 `hermes-agent_sangsang`에서 발견되는 두 가지 자가 진화
철학을 융합한, 작고 자족적인 엔진이다:

| 부모 | 무엇을 진화시키나 | Chiron이 취하는 강점 |
|------|------------------|----------------------|
| **agi / 상상이** | *선언적 지식* — 공백을 탐지하고, 지식을 수집하며, 새로운 연결을 발견(창발)하면서 자라는 인과 그래프. | 시스템이 **세상에 대해 진짜로 새로운 것을 배우고** 새 가설을 세울 수 있다. |
| **Hermes** | *절차적 능력* — 경험에서 포착되어 curator가 통합·노후화하지만 결코 삭제하지 않는, 재사용 가능한 `SKILL.md` 노하우. | 출처와 사람의 통제가 있는 **안전하고 복구 가능하며 운영에 강한** 자기 개선. |

각각을 단독으로 썼을 때의 문제:

- agi는 **대규모로 틀릴 수 있다** — 환각으로 만들어진 사실이 그래프에 들어가 이후
  추론을 조용히 떠받친다. 오염이 복리로 누적된다.
- Hermes는 **안전하지만 세상에 대해 결코 더 똑똑해지지 않는다** — *일하는 방식*만
  다듬을 뿐, *무엇을 아는지*는 늘 그대로다.

**Chiron의 명제:** 지식은 자유롭게 자라게 두되(agi), **모든 새 사실을 검증 게이트에
통과시키고**, **검증되고 반복되는 지식만 절차적 스킬로 승격시킨다**(Hermes). 사실은
틀릴 수 있지만 — (a) 검증 게이트를 통과하고 (b) 스킬로 만들 가치가 있는 안정적이고
반복되는 패턴을 형성하기 전까지는 에이전트의 행동에 영향을 줄 수 없다.

```
공백 ─▶ 목표 ─▶ 수집(가설) ─▶ [검증 게이트] ─▶ 검증된 지식
                                   │                     │
                       창발 ◀──────┘                     ▼
                    (새 가설) ─▶ [게이트 재검증] ─▶ ─▶ 승격 ─▶ 스킬
                                                            │
                                          curator: 통합 / 노후화 / 보관
                                            (삭제 없음 · 출처 · 고정(pin))
```

## 빠른 시작 (완전 오프라인 — API 키도, DB 서버도 불필요)

```bash
cd hybrid
python3 examples/demo.py      # 엔드투엔드 시연
python3 tests/test_smoke.py   # 또는: pytest -q
```

데모는 결정론적 **stub LLM**과 인메모리 SQLite를 사용하므로, 외부 의존성 0으로 전체
폐루프가 돈다. 실제 모델을 쓰려면:

```bash
export CHIRON_LLM=openai
export CHIRON_BASE_URL=https://openrouter.ai/api/v1   # OpenAI 호환이면 어떤 엔드포인트든
export CHIRON_API_KEY=sk-...
export CHIRON_MODEL=anthropic/claude-3.5-sonnet
```

## 데모가 보여주는 것

1. **공백 → 목표.** 상호작용에서 모르는 용어가 언급되고, 반복된 실패는 우선순위가
   매겨진 `KNOWLEDGE_GAP` 목표가 된다 (agi의 메타인지).
2. **수집 → 검증.** 진화 루프가 열린 목표를 위해 지식을 *가설*로 끌어온다.
   **corrector**가 각 엣지를 검증한다. `coral bleaching → big bang`은 기각된다 —
   결과가 우주의 기원보다 먼저 올 수 없으므로.
3. **창발 → 재검증.** 새로운 추이적 지름길이 발견되고 *동일한* 증거 기준에 묶인다.
   약한 것들은 기각된다.
4. **승격(융합 지점).** 검증된 인과 사슬이 강하고 반복되는 주제는 `knowledge-*`
   스킬로 합성된다 (`origin=promoted`).
5. **큐레이션(Hermes 규율).** 형제 스킬(`debugging-*`, `knowledge-*`)이 `*-umbrella`
   스킬 아래로 통합되고, 흡수된 형제는 **삭제가 아니라 보관(archive)**된다.

## 구성

```
hybrid/
├── README.md            ← 지금 보는 문서
├── ARCHITECTURE.md      ← 융합 설계, 컴포넌트별 상세
├── requirements.txt     ← 표준 라이브러리만
├── chiron/
│   ├── config.py        ← 모든 임계값 / 노브
│   ├── store.py         ← 통합 SQLite 저장소: 지식 그래프 + 스킬 + 출처 + 감사로그
│   ├── llm.py           ← LLMClient 프로토콜 · 오프라인 StubLLM · OpenAI 호환 클라이언트
│   ├── metacognition.py ← [agi] 능력 추적 + 목표 생성
│   ├── evolution.py     ← [agi] 열린 목표를 위한 지식 수집 (가설로)
│   ├── corrector.py     ← [agi] 검증 게이트 (valid / doubtful / rejected)
│   ├── emergence.py     ← [agi] 새로운 추이적 지름길 발견
│   ├── promotion.py     ← [융합] 검증된 지식 사슬 → 절차적 스킬
│   ├── curator.py       ← [hermes] 통합 · 노후화 · 보관 (삭제 없음)
│   └── orchestrator.py  ← 두 시간 척도(턴 단위 + 주기 단위)의 폐루프
├── examples/demo.py
└── tests/test_smoke.py
```

## 설계 불변식 (의도적으로 물려받은 것)

- **증명 전까지는 가설** (agi): 수집·창발 엣지는 `hypothesis`로 시작하며 corrector를
  통해서만 `validated`가 된다.
- **절대 삭제하지 않음** (Hermes): curator는 보관(archive)한다. 보관본은 복구 가능하다.
- **모든 기록에 출처(provenance)**: 스킬은 `origin ∈ {foreground, background_review,
  promoted, curated}`을 갖는다. 에이전트가 키운 스킬만 curator의 관리 대상이다.
- **우아한 성능 저하**: 도달 가능한 LLM이 없으면 ⇒ stub이 루프를 계속 살려둔다.

전체 근거와 `agi`·`hermes`의 특정 메커니즘으로의 매핑은 [ARCHITECTURE.md](ARCHITECTURE.md)를
참고하라.
````

---

## 2. `ARCHITECTURE.md`

````markdown
# Chiron 아키텍처 — 두 자가 진화 철학의 융합

이 문서는 Chiron이 *왜* 이렇게 만들어졌는지를 설명하고, 각 조각이 `agi/상상이` 또는
`hermes`로부터 물려받은 메커니즘으로 어떻게 매핑되는지 정리한다.

## 1. 두 부모, 각각 한 문단으로

**agi / 상상이**는 자가 진화를 **지식 성장**으로 다룬다. 인과 지식 그래프(MySQL +
Neo4j)가 길고 자율적인 파이프라인을 통해 확장된다: `meta_cognition`이 약점과 해소되지
않은 `knowledge_gap`을 탐지 → `evolution_loop`가 논문/위키를 자동 수집해 사건+관계를
추출 → `emergence_detector`가 새로운 간접 경로, 다리 노드, 유추를 발견 → `corrector`가
그 발견들을 LLM으로 검증(valid/doubtful/rejected, 방향 뒤집기 포함) → 검증된 경로는
해석되고 *고착(solidify)*된다. 새 파이썬 핸들러까지 생성할 수 있다(`module_factory`).
야심차고 세상에 대해 진짜로 배우지만 — 잘못된 사실이 한번 고착되면 이후 추론을 조용히
떠받칠 수 있다.

**hermes**는 자가 진화를 **절차적 능력 성장**으로 다룬다. 단위는 재사용 가능한
`SKILL.md`다. 턴이 끝나면 백그라운드 리뷰 fork가 "재사용 가능한 절차를 배웠나 / 교정을
받았나?"를 자문하고 스킬을 쓰거나 패치한다. 주간 `curator`가 형제 스킬들을 클래스 단위
umbrella로 통합하고, 미사용 스킬을 `stale`/`archived`로 노후화하며, **결코 삭제하지
않는다**. 모든 기록은 출처를 가지며, 번들/고정 스킬은 보호된다. 안전하고 복구 가능하며
운영에 성숙했지만 — 세상에 대한 새 사실은 결코 배우지 않고, 자신이 일하는 방식만 배운다.

## 2. Chiron이 메우는 간극

어느 부모도 두 종류의 기억을 잇지 않는다:

- agi는 **선언적** 지식을 키우지만 "이것이 이제 내가 따라야 할 재사용 가능한 절차다"라는
  개념이 없다.
- hermes는 **절차적** 능력을 키우지만 새 지식을 *발견*하는 메커니즘이 없다 — 사람이나
  세션이 이미 시연한 것만 포착한다.

Chiron은 **승격 다리(promotion bridge)**를 추가한다: 안정적이고 반복되는 패턴을 형성한
검증된 선언적 지식을 절차적 스킬로 합성한다. 이로써 에이전트는 hermes의 안전 모델 아래에서
agi의 도달 범위(새로운 것을 배울 수 있음)를 얻는다 — 그 배움은 검증되고 *승격되기*
전까지 행동을 좌우할 수 없으며, 언제나 복구 가능하다.

## 3. 통합 저장소 (`store.py`)

agi는 지식을 MySQL과 Neo4j에 흩뿌렸고, hermes는 스킬을 Markdown 파일로 보관했다.
Chiron은 **둘 다** 하나의 SQLite에 담아 승격이 시스템 간 ETL이 아니라 로컬 트랜잭션이
되게 한다:

- `nodes`, `edges` — 인과 지식 그래프. 엣지는 **생명주기 상태**(`hypothesis →
  validated | rejected | doubtful`)와 `origin`(`acquired | emergent`)을 가지며, agi를
  그대로 반영한다.
- `gaps`, `goals`, `capability` — 메타인지 상태.
- `skills` — hermes의 필드를 가진 절차적 기억: `origin`(`foreground |
  background_review | promoted | curated`), `status`(`active | stale | archived`),
  `pinned`, `uses`, `last_used_turn`.
- `validations`, `audit` — 모든 판정과 모든 상태 변화가 기록된다. 그 무엇도 조용히
  일어나지 않는다.

## 4. 컴포넌트와 그 계보

| 모듈 | 물려받은 출처 | 역할 |
|------|---------------|------|
| `metacognition.py` | agi `meta_cognition.py` | 행동별 성공/신뢰도 추적; 공백 + 약점을 우선순위 목표로 전환. |
| `evolution.py` | agi `evolution_loop.py` | 열린 `KNOWLEDGE_GAP` 목표마다 교체 가능한 소스로 지식을 수집하고 엣지를 **가설로** 추가. |
| `corrector.py` | agi `corrector.py` | **검증 게이트.** 신뢰도 하한 미달은 값싸게 기각, 아니면 LLM이 판정: valid / doubtful(≤N회 재시도 후 기각) / rejected. |
| `emergence.py` | agi `emergence_detector.py` | *검증된* 엣지에 대해 BFS를 돌려 추이적 지름길을 발견, 새 가설로 삽입(그래서 게이트를 다시 거침). |
| `promotion.py` | **신규 (융합 지점)** | 검증된 인과 사슬을 모아, 강하고 반복되면 `knowledge-*` 스킬을 `origin=promoted`로 합성. |
| `curator.py` | hermes `curator.py` | 스킬 노후화(`active→stale→archived`), 같은 접두사 형제를 `*-umbrella`로 통합, **삭제 아닌 보관**, `pinned` 존중. |
| `orchestrator.py` | 양쪽 | 두 시간 척도에서 폐루프 구동. |

## 5. 두 시간 척도의 폐루프

**턴 단위 (즉시 — hermes의 리뷰 + agi의 모니터링).**
`observe(action, success, confidence, unknown_terms)`:
- 능력 통계와 모든 지식 공백을 기록하고,
- `goal_update_every` 턴마다 목표를 재계산하며,
- `skill_nudge_interval` 턴마다 **백그라운드 리뷰** 훅을 발동(hermes식 즉시 스킬 포착),
- `auto_evolve_every` 턴마다 완전한 주기 사이클을 실행.

**주기 단위 (agi의 진화/창발 + hermes의 큐레이션).** `evolve()`:
```
update_goals
  → evolution.run_once()      # 가설 수집
  → corrector.verify_pending()# 게이트
  → emergence.discover()      # 새 가설
  → corrector.verify_pending()# 게이트 재실행
  → promoter.promote()        # 검증된 사슬 → 스킬   ← 융합 지점
  → curator.run()             # 통합 / 노후화 / 보관
```

이 순서가 곧 안전 논리를 구체화한 것이다: "시스템이 생각을 떠올렸다"와 "그 생각이
행동을 좌우하는 스킬이 되었다" 사이에 **두 개의 게이트**가 서 있다.

## 6. 왜 agi 단독보다 안전하고, hermes 단독보다 똑똑한가

- **agi 대비:** 환각 엣지는 게이트에서 기각되거나 — 그저 그럴듯해서 통과하더라도 —
  승격이 스킬로 만들어낼 만큼 강하고 반복되는 사슬을 *함께* 형성하지 않는 한 행동에
  영향을 줄 수 없다. 그리고 설령 그렇더라도 curator가 보관할 수 있다. 조용한 "영원히
  고착" 같은 건 없다.
- **hermes 대비:** 에이전트는 더 이상 *일하는 방식*을 다듬는 데 머무르지 않는다.
  공백 → 수집 → 창발을 통해 진짜로 새로운 지식을 형성한다 — 다만 들어오는 길에 hermes의
  안전세(출처, 보관, 검증)를 낸다.

## 7. 의도적으로 단순화한 부분 (그리고 실제 시스템과의 차이)

이것은 **설계 + 동작 스켈레톤**이지 프로덕션 시스템이 아니다. stub LLM은 투명한
휴리스틱을 써서 루프를 결정론적이고 테스트 가능하게 만든다. 지식 "소스"는 실제
arXiv/위키피디아 검색이 아니라 화살표 표기 시드 텍스트다. 그래프는 Neo4j가 아니라
SQLite다. 주기 루프는 hermes의 idle 트리거 백그라운드 fork가 아니라 명시적으로 구동된다.
이 각각은 명확히 표시된 단일 이음새(seam)다:

- env 변수로 `StubLLM`을 `OpenAICompatibleLLM`(이미 구현됨)으로 교체,
- `knowledge_source`를 실제 검색기로 교체,
- 그래프 규모가 필요하면 `store.py`를 Neo4j/Postgres로 백업,
- `Orchestrator.evolve()`를 hermes의 idle/cron 스케줄러 위로 이동.

아키텍처 — 공백 → 목표 → 수집 → **게이트** → 창발 → **게이트** → **승격** → 큐레이션,
전부 출처가 추적되고 복구 가능 — 이것이 기여한 바이며, 오늘 당장 돈다.
````

---

## 3. `CONCEPT_KR.md`

````markdown
# Chiron 컨셉 요약 & 설명서

> **한 줄 정의** — 지식은 *상상이(agi)*처럼 스스로 자라되, *Hermes*처럼 검증 게이트를
> 통과하고 반복 확인된 지식만 "스킬(절차서)"로 승격되어 행동에 영향을 주는,
> 안전하고 복구 가능한 하이브리드 자가 진화 엔진.

---

## 1. 왜 만들었나 (배경)

두 개의 자가 진화 시스템을 비교한 결과:

| | **agi / 상상이** | **Hermes** |
|---|---|---|
| 진화 대상 | **지식**(무엇을 아는가) | **능력**(어떻게 일하는가) |
| 단위 | 인과 지식그래프의 노드·관계 | 재사용 스킬(`SKILL.md`) |
| 강점 | 세상을 새로 배우고 새 가설을 세움 | 안전·복구·운영 성숙도 |
| 약점 | 틀린 지식이 누적·오염될 위험 | 세상 지식은 영원히 그대로 |

- **agi 단독** → 똑똑하지만 위험 (환각이 그래프에 박혀 복리로 오염)
- **Hermes 단독** → 안전하지만 진짜로 똑똑해지지 않음 (노하우만 정리)

**Chiron의 답** → 둘의 장점만 합친다:
> 지식은 자유롭게 자라게 두고, **두 개의 게이트**를 세워 검증된 것만 행동으로 이어지게.

---

## 2. 핵심 컨셉 (그림 한 장)

```
공백 ─▶ 목표 ─▶ 수집(가설) ─▶ [게이트1: 검증] ─▶ 검증된 지식
                                  │                      │
                      창발 ◀──────┘                      ▼
                  (새 가설) ─▶ [게이트2: 재검증] ─▶ 승격 ─▶ 스킬
                                                         │
                                       curator: 통합 / 노후화 / 보관
                                         (삭제 없음 · 출처 · 고정)
```

**핵심 아이디어 = "승격(Promotion)"**
- 하나의 사실은 ① 검증 게이트를 통과하고 ② 반복되는 패턴을 형성한 뒤에야
  비로소 **스킬**(에이전트가 실제 따르는 것)이 된다.
- 틀린 지식이 들어와도 → 게이트에서 걸리거나, 통과해도 행동을 조용히 좌우 못 함.

---

## 3. 동작 흐름 (5단계)

1. **공백 → 목표**
   모르는 주제를 만나면 `knowledge_gap`으로 기록 → 반복되면 우선순위 학습 목표가 됨.
   *(agi의 메타인지)*

2. **수집 → 검증 (게이트1)**
   목표에 대해 지식을 *가설*로 수집 → `corrector`가 인과 타당성 검증.
   예: `coral bleaching → big bang`은 기각(결과가 우주 기원보다 먼저일 수 없음).

3. **창발 → 재검증 (게이트2)**
   검증된 그래프에서 새로운 간접 경로(A→B→C인데 A→C는 없던 것)를 스스로 발견 →
   동일한 검증 기준에 다시 묶임. *(agi의 emergence)*

4. **승격 (★융합 지점)**
   검증된 인과 사슬이 충분히 강하고 반복되면 → `knowledge-*` 스킬로 합성.
   `origin=promoted`로 출처 기록.

5. **큐레이션 (Hermes 규율)**
   형제 스킬을 `*-umbrella`로 통합 / 미사용은 노후화 / **삭제 대신 보관(archive)**.

---

## 4. 두 시간 척도

| 척도 | 시점 | 하는 일 | 출처 |
|---|---|---|---|
| **턴 단위(즉시)** | 매 상호작용 후 | 능력 기록, 공백 탐지, 백그라운드 스킬 리뷰 | Hermes + agi |
| **주기 단위** | N턴마다 / idle 시 | 수집→검증→창발→검증→승격→큐레이션 | agi + Hermes |

---

## 5. 안전 설계 (의도적으로 물려받음)

- **증명 전까지는 가설** — 모든 수집/창발 엣지는 `hypothesis`로 시작, 검증 후에만 `validated`
- **절대 삭제하지 않음** — curator는 보관(archive)만, 복구 가능
- **모든 기록에 출처** — `origin ∈ {foreground, background_review, promoted, curated}`
- **우아한 성능 저하** — LLM 없어도 stub이 루프 유지

---

## 6. 사용법 (실행)

```bash
cd hybrid

# 전체 자가진화 폐루프 시연 (오프라인, API키 불필요)
python3 examples/demo.py

# 테스트 (5개)
python3 tests/test_smoke.py
```

**필요한 것**: Python 3.11+ **만** (외부 패키지·DB·API키 전부 불필요)

**실제 LLM 연결 시** (선택):
```bash
export CHIRON_LLM=openai
export CHIRON_BASE_URL=https://openrouter.ai/api/v1   # OpenAI 호환 엔드포인트
export CHIRON_API_KEY=sk-...
export CHIRON_MODEL=anthropic/claude-3.5-sonnet
```

---

## 7. 파일 구성

```
hybrid/
├── README.md            전체 소개
├── ARCHITECTURE.md      상세 설계 & 부모 시스템 매핑
├── CONCEPT_KR.md        ← 지금 이 문서 (컨셉 요약 & 설명서)
├── requirements.txt     표준 라이브러리만
├── chiron/
│   ├── config.py        모든 설정값
│   ├── store.py         통합 SQLite (지식그래프 + 스킬 + 출처 + 감사로그)
│   ├── llm.py           LLM 인터페이스 · 오프라인 stub · OpenAI 호환 클라이언트
│   ├── metacognition.py [agi] 능력 추적 + 목표 생성
│   ├── evolution.py     [agi] 지식 수집 (가설)
│   ├── corrector.py     [agi] 검증 게이트
│   ├── emergence.py     [agi] 새 인과 경로 발견
│   ├── promotion.py     [융합] 검증된 지식 → 스킬 승격
│   ├── curator.py       [hermes] 통합·노후화·보관
│   └── orchestrator.py  폐루프 (턴 단위 + 주기 단위)
├── examples/demo.py
└── tests/test_smoke.py
```

---

## 8. 한 줄 결론

> **agi의 "똑똑함" + Hermes의 "안전함"** —
> 검증과 승격이라는 두 관문으로, 자라는 지식과 신뢰할 수 있는 행동을 동시에 얻는다.

---

*프로젝트 위치: `hermes-agent_sangsang` 레포 · `claude/hermes-agi-self-evolution-jBgjI` 브랜치 · `hybrid/` 폴더*
````

---

## 4. `requirements.txt`

````text
# Chiron은 파이썬 표준 라이브러리만으로 동작한다 (sqlite3, dataclasses, ...).
# 오프라인 데모와 테스트 스위트에 필요한 서드파티 패키지는 없다.
#
# 선택 사항: CHIRON_LLM=openai 로 실제 LLM을 연결할 때
#   - 추가 패키지 불필요: OpenAI 호환 클라이언트는 표준 라이브러리의 urllib을 사용한다.
#
# 선택적 개발 도구:
# pytest>=7.0    # `pytest -q` 로도 tests/test_smoke.py 가 실행된다
````

---

## 5. `chiron/__init__.py`

````python
"""Chiron — 하이브리드 자가 진화 엔진.

Chiron은 기계의 자가 진화에 대한 상호 보완적인 두 가지 접근을 융합한다:

  * **agi / 상상이**는 *선언적 지식(declarative knowledge)*을 키운다: 지식 공백을
    탐지하고, 지식을 수집하며, 그래프 안에서 새로운 인과 연결을 발견한다.
  * **hermes**는 *절차적 능력(procedural skill)*을 키운다: "어떤 부류의 작업을
    어떻게 하는지"를 재사용 가능하고, 통합되며, 복구 가능한 산출물로 포착한다.

융합 명제(ARCHITECTURE.md 참고): 지식은 자유롭게 자라게 두되, 모든 새 사실은
검증을 거치게 하고, *검증되고 반복되는* 지식만 절차적 스킬로 승격시킨다. 그 무엇도
삭제되지 않으며(오직 보관/archive만), 모든 기록은 출처(provenance)를 갖는다.
"""

from .config import Config
from .store import Store
from .orchestrator import Orchestrator

__all__ = ["Config", "Store", "Orchestrator"]
__version__ = "0.1.0"
````

---

## 6. `chiron/config.py`

````python
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
````

---

## 7. `chiron/store.py`

````python
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

    def pin_skill(self, name: str, pinned: bool = True) -> None:
        self.db.execute("UPDATE skills SET pinned=? WHERE name=?", (int(pinned), name))
        self.db.commit()

    def close(self) -> None:
        self.db.close()
````

---

## 8. `chiron/llm.py`

````python
"""LLM 추상화 계층.

Chiron은 절대 공급자(provider)를 직접 호출하지 않는다 — 항상 ``LLMClient``와
대화한다. 여기에는 두 가지 구현이 들어 있다:

  * ``StubLLM`` — 완전히 결정론적이며 오프라인. API 키 없이도 전체 자가 진화 루프를
    실행(및 단위 테스트)할 수 있게 해준다. 실제 응답의 *형태*를 모방한다: 지식 추출,
    엣지 검증, 스킬 합성. 휴리스틱은 의도적으로 단순하지만 그럴듯하다.
  * ``OpenAICompatibleLLM`` — OpenAI 호환 엔드포인트(OpenRouter, LM Studio,
    Anthropic 호환, 로컬 등)를 위한 얇은 클라이언트. 설정되면 사용된다.

이는 hermes의 공급자 비종속(provider-agnostic) 설계와 agi의 "우아한 성능 저하
(graceful degradation)"를 함께 반영한다: 도달 가능한 LLM이 없으면 stub이 루프를
계속 살려둔다.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol


# ----------------------------------------------------------------------------
# 구조화된 응답 형태 (호출자가 자유 텍스트를 두 번 파싱하지 않도록)
# ----------------------------------------------------------------------------
@dataclass
class Fact:
    src: str
    dst: str
    relation: str
    strength: float
    confidence: float


@dataclass
class Verdict:
    passed: bool
    verdict: str          # "valid" | "rejected" | "doubtful"
    reason: str
    confidence: float


class LLMClient(Protocol):
    def extract_facts(self, topic: str, text: str) -> list[Fact]: ...
    def validate_edge(self, src: str, relation: str, dst: str, confidence: float) -> Verdict: ...
    def synthesize_skill(self, name: str, facts: list[tuple[str, str, str]]) -> str: ...
    def name_umbrella(self, prefix: str, members: list[str]) -> str: ...


# ----------------------------------------------------------------------------
# 오프라인 결정론적 stub
# ----------------------------------------------------------------------------
_CAUSAL_HINTS = ("cause", "lead", "increase", "raise", "improve", "유발", "상승", "향상", "초래")
_STOP = {"a", "an", "the", "of", "and", "to", "in", "is", "are", "그", "이", "수", "및"}


class StubLLM:
    """결정론적 대역(stand-in). 네트워크도, 무작위성도 없다."""

    def extract_facts(self, topic: str, text: str) -> list[Fact]:
        """'A -> B -> C' 형태의 시드 텍스트를 인과 엣지로 변환한다.

        데모는 단순한 화살표 표기 '지식'을 공급한다. 실제 텍스트라면 진짜 모델이
        파싱할 것이다. 테스트를 위해 추출 과정을 투명하게 유지한다.
        """
        facts: list[Fact] = []
        for line in text.splitlines():
            line = line.strip()
            if "->" not in line:
                continue
            chain = [p.strip() for p in line.split("->") if p.strip()]
            for i in range(len(chain) - 1):
                src, dst = chain[i], chain[i + 1]
                # 그럴듯함 휴리스틱: 짧고 내용이 있는 링크일수록 높은 점수
                conf = round(0.55 + 0.1 * min(len(src.split()), 3) / 3, 3)
                facts.append(Fact(src=src, dst=dst, relation="causes",
                                  strength=0.7, confidence=conf))
        return facts

    def validate_edge(self, src: str, relation: str, dst: str, confidence: float) -> Verdict:
        """인과처럼 보이고 자기 자신이 아닌 엣지는 승인하고, 나머지는 의심으로 표시한다."""
        if src.lower() == dst.lower():
            return Verdict(False, "rejected", "self-loop", 0.95)
        # stub이 인지할 수 있는 명백히 시간 역전된 주장은 기각한다
        if dst.lower() in {"big bang", "빅뱅"}:
            return Verdict(False, "rejected", "결과가 우주의 기원보다 먼저 올 수 없음", 0.9)
        if confidence >= 0.5:
            return Verdict(True, "valid", "그럴듯한 인과 메커니즘", min(confidence + 0.1, 0.99))
        if confidence >= 0.35:
            return Verdict(False, "doubtful", "신호가 약함, 추가 근거 필요", confidence)
        return Verdict(False, "rejected", "신뢰도 하한 미달", confidence)

    def synthesize_skill(self, name: str, facts: list[tuple[str, str, str]]) -> str:
        """검증된 사실들을 절차적 SKILL.md 본문으로 렌더링한다."""
        lines = [f"# {name}", "",
                 "_검증된 지식에서 자동 승격됨. 출처(provenance): promoted._", "",
                 "## 언제 사용하나", f"**{name}** 또는 그 결과에 대해 추론할 때.", "",
                 "## 알려진 인과 구조"]
        for src, rel, dst in facts:
            lines.append(f"- `{src}` {rel} `{dst}`")
        lines += ["", "## 절차",
                  "1. 위의 알려진 원인 중 무엇이 존재하는지 식별한다.",
                  "2. 사슬을 따라가며 하류(downstream) 결과를 예측한다.",
                  "3. 빠진 단계가 있으면 지식 공백으로 등록하고 재평가한다."]
        return "\n".join(lines)

    def name_umbrella(self, prefix: str, members: list[str]) -> str:
        base = prefix.strip("-_ ") or "general"
        return f"{base}-umbrella"


# ----------------------------------------------------------------------------
# 실제 공급자 (최선 노력, 선택적 의존성)
# ----------------------------------------------------------------------------
class OpenAICompatibleLLM:
    """최소한의 OpenAI 호환 chat 클라이언트. 오류 발생 시 StubLLM으로 폴백한다."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._fallback = StubLLM()

    def _chat(self, system: str, user: str) -> str:
        import urllib.request
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]

    def extract_facts(self, topic: str, text: str) -> list[Fact]:
        try:
            out = self._chat(
                "Extract causal edges as JSON list of {src,dst,relation,strength,confidence}.",
                f"Topic: {topic}\n\n{text}")
            raw = json.loads(re.search(r"\[.*\]", out, re.S).group(0))
            return [Fact(d["src"], d["dst"], d.get("relation", "causes"),
                         float(d.get("strength", 0.6)), float(d.get("confidence", 0.6)))
                    for d in raw]
        except Exception:
            return self._fallback.extract_facts(topic, text)

    def validate_edge(self, src: str, relation: str, dst: str, confidence: float) -> Verdict:
        try:
            out = self._chat(
                'Reply JSON {"passed":bool,"verdict":"valid|rejected|doubtful","reason":str,"confidence":float}.',
                f"Is this causal claim sound? {src} --{relation}--> {dst}")
            d = json.loads(re.search(r"\{.*\}", out, re.S).group(0))
            return Verdict(bool(d["passed"]), d["verdict"], d.get("reason", ""),
                           float(d.get("confidence", confidence)))
        except Exception:
            return self._fallback.validate_edge(src, relation, dst, confidence)

    def synthesize_skill(self, name: str, facts: list[tuple[str, str, str]]) -> str:
        try:
            joined = "\n".join(f"{s} {r} {d}" for s, r, d in facts)
            return self._chat("Write a concise procedural SKILL.md (markdown).",
                              f"Skill name: {name}\nValidated facts:\n{joined}")
        except Exception:
            return self._fallback.synthesize_skill(name, facts)

    def name_umbrella(self, prefix: str, members: list[str]) -> str:
        return self._fallback.name_umbrella(prefix, members)


def build_llm(cfg) -> LLMClient:
    if cfg.llm_kind == "openai" and cfg.llm_base_url:
        return OpenAICompatibleLLM(cfg.llm_base_url, cfg.llm_api_key, cfg.llm_model)
    return StubLLM()
````

---

## 9. `chiron/metacognition.py`

````python
"""메타인지 (agi 쪽): 자기 모니터링 + 목표 생성.

에이전트 자신의 능력 통계와 해소되지 않은 지식 공백을 지켜보다가, 약점을 우선순위가
매겨진 학습 목표로 전환한다. 이것이 루프의 "무위자연 / 데이터가 무엇을 배워야 할지
알려주게 둔다" 절반에 해당한다.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class MetaCognition:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def record(self, action: str, success: bool, confidence: float) -> None:
        self.store.record_capability(action, success, confidence)

    def update_goals(self) -> int:
        """공백 + 능력 약점으로부터 활성 목표 집합을 재계산한다."""
        created = 0
        for keyword, hits in self.store.active_gaps(self.cfg.gap_promote_hits):
            # 우선순위는 공백이 얼마나 자주 부딪혔는지에 비례한다
            self.store.upsert_goal("KNOWLEDGE_GAP", keyword, priority=min(hits, 10))
            created += 1
        for action in self.store.weaknesses(self.cfg.weak_success_rate, self.cfg.weak_confidence):
            self.store.upsert_goal("CAPABILITY_FIX", action, priority=8)
            created += 1
        if created:
            self.store.log("goals.update", f"{created} goal(s) refreshed")
        return created
````

---

## 10. `chiron/evolution.py`

````python
"""진화 루프 (agi 쪽): 열려 있는 목표를 위해 자율적으로 지식을 수집한다.

실제 agi 시스템에서는 arXiv / 위키피디아로 나가서 텍스트를 추출 파이프라인에 통과시킨다.
여기서는 "수집기(acquirer)"가 교체 가능하다: 데모는 화살표 표기 시드 텍스트를 돌려주는
지식 소스를 공급하고, LLM이 이를 인과 엣지로 변환한다. 수집된 엣지는 *가설(hypothesis)*
로 들어온다 — corrector가 검증하기 전까지는 신뢰되지 않는다.
"""

from __future__ import annotations

from typing import Callable

from .store import Store
from .config import Config
from .llm import LLMClient

# 지식 소스: 주제(topic) -> 사실을 캐낼 원시 텍스트
KnowledgeSource = Callable[[str], str]


class EvolutionLoop:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient, source: KnowledgeSource):
        self.store = store
        self.cfg = cfg
        self.llm = llm
        self.source = source

    def run_once(self, max_goals: int | None = None) -> dict:
        max_goals = max_goals or self.cfg.max_goals_per_run
        goals = [g for g in self.store.active_goals(max_goals) if g[1] == "KNOWLEDGE_GAP"]
        added_edges = 0
        for goal_id, _gtype, target in goals:
            text = self.source(target)
            if not text:
                continue
            for fact in self.llm.extract_facts(target, text):
                self.store.add_edge(fact.src, fact.dst, fact.relation,
                                    fact.strength, fact.confidence,
                                    origin="acquired", provenance="evolution")
                added_edges += 1
            self.store.resolve_gap(target)
            self.store.complete_goal(goal_id)
        if added_edges:
            self.store.log("evolution.run", f"acquired {added_edges} hypothesis edge(s)")
        return {"goals": len(goals), "edges": added_edges}
````

---

## 11. `chiron/corrector.py`

````python
"""Corrector (agi 쪽): 검증 게이트.

agi로부터 물려받은 가장 중요한 발상이다: *새 지식은 증명되기 전까지 가설이다.* 모든
가설/창발 엣지가 검사된다 — 신뢰도 하한 미달이면 값싸게 기각하고, 아니면 LLM이 판정한다.
판정(verdict):

  * valid     -> 상태 'validated'  (스킬로의 승격 자격 획득)
  * doubtful  -> 'doubtful' 유지, N회까지 재시도 후 자동 기각
  * rejected  -> 상태 'rejected'   (감사를 위해 보존, 절대 조용히 버리지 않음)

의심 추적(doubt-tracking)은 실행 단위의 메모리에서 이뤄지며, agi의 "최대 3회 재검증"과
일치한다.
"""

from __future__ import annotations

from collections import defaultdict

from .store import Store
from .config import Config
from .llm import LLMClient


class Corrector:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm
        self._doubt_counts: dict[int, int] = defaultdict(int)

    def verify_pending(self) -> dict:
        """현재 그래프에 있는 모든 가설 + 의심 엣지를 검증한다."""
        pending = self.store.edges_by_status("hypothesis") + self.store.edges_by_status("doubtful")
        stats = {"validated": 0, "rejected": 0, "doubtful": 0}
        for e in pending:
            # LLM 호출 전 값싼 하한 검사 (agi의 최적화)
            if e.confidence < self.cfg.validate_min_confidence:
                self.store.set_edge_status(e.id, "rejected")
                self.store.record_validation("edge", e.id, "rejected",
                                             "신뢰도 하한 미달", e.confidence)
                stats["rejected"] += 1
                continue

            v = self.llm.validate_edge(e.src_name, e.relation, e.dst_name, e.confidence)
            self.store.record_validation("edge", e.id, v.verdict, v.reason, v.confidence)

            if v.verdict == "valid":
                self.store.set_edge_status(e.id, "validated")
                stats["validated"] += 1
            elif v.verdict == "doubtful":
                self._doubt_counts[e.id] += 1
                if self._doubt_counts[e.id] >= self.cfg.doubtful_max_retries:
                    self.store.set_edge_status(e.id, "rejected")
                    self.store.record_validation("edge", e.id, "rejected",
                                                 "의심 재시도 횟수 소진", v.confidence)
                    stats["rejected"] += 1
                else:
                    self.store.set_edge_status(e.id, "doubtful")
                    stats["doubtful"] += 1
            else:
                self.store.set_edge_status(e.id, "rejected")
                stats["rejected"] += 1

        self.store.log("corrector.run",
                       f"validated={stats['validated']} rejected={stats['rejected']} "
                       f"doubtful={stats['doubtful']}")
        return stats
````

---

## 12. `chiron/emergence.py`

````python
"""창발 탐지기 (agi 쪽): *새로운* 인과 경로를 발견한다.

이미 검증된 엣지들의 그래프를 탐색하여, 아직 직접적으로 주장되지 않은 간접 연결을
찾는다(A -> B -> C는 있지만 A -> C는 없는 경우). 각 발견은 새로운 창발 가설 엣지로
삽입되므로, 그 자체로 corrector를 통과해야만 승격될 수 있다. 이것이 시스템이 "새로운
생각을 떠올리는" 방식이며 — 동시에 그 생각이 수집된 지식과 동일한 증거 기준에 묶이는
방식이다.
"""

from __future__ import annotations

from .store import Store
from .config import Config


class EmergenceDetector:
    def __init__(self, store: Store, cfg: Config):
        self.store = store
        self.cfg = cfg

    def discover(self) -> dict:
        """검증된 엣지에 대해 BFS를 수행하고, 추이적(transitive) 지름길을 가설로 방출한다."""
        # 검증된 엣지만으로 인접 리스트를 구성한다
        validated = self.store.edges_by_status("validated")
        adj: dict[str, list[tuple[str, float]]] = {}
        for e in validated:
            adj.setdefault(e.src_name, []).append((e.dst_name, e.strength * e.confidence))

        discovered = 0
        for start in list(adj.keys()):
            # `start`로부터 길이 >= 2인 경로 탐색
            stack = [(start, [start], 1.0)]
            while stack:
                node, path, score = stack.pop()
                if len(path) - 1 >= self.cfg.emergence_max_depth:
                    continue
                for nxt, w in adj.get(node, []):
                    if nxt in path:
                        continue  # 순환 금지
                    new_score = score * w * self.cfg.emergence_decay
                    new_path = path + [nxt]
                    # 창발적 지름길: 양 끝점이 아직 직접 연결되지 않은 경우
                    if len(new_path) >= 3 and new_score >= self.cfg.emergence_min_confidence \
                            and not self.store.edge_exists(start, nxt):
                        self.store.add_edge(
                            start, nxt, "leads-to", strength=0.6,
                            confidence=round(new_score, 3),
                            origin="emergent", provenance="emergence")
                        discovered += 1
                    stack.append((nxt, new_path, new_score))

        if discovered:
            self.store.log("emergence.run", f"discovered {discovered} emergent shortcut(s)")
        return {"discovered": discovered}
````

---

## 13. `chiron/promotion.py`

````python
"""승격 (융합 지점): 검증된 선언적 지식을 절차적 스킬로 전환한다.

이 모듈이 Chiron의 핵심이다. agi는 지식 그래프를 키우고, hermes는 스킬을 키우지만,
어느 쪽도 둘을 잇지 않는다. 승격은 다음을 수행한다:

  1. 각 *사슬 머리(chain head)* — 인과 사슬을 이끄는 주제(검증된 엣지들 사이에서
     출발점(source)이지만 도착점(destination)은 한 번도 되지 않는 노드) — 를 찾는다.
  2. 그 머리로부터 도달 가능한 *검증된* 엣지의 사슬 전체를 모은다.
  3. 사슬이 충분히 많고 신뢰도가 높은 검증 엣지를 가진 머리는 노이즈가 아니라 안정적이고
     재사용 가능한 패턴으로 간주되어 SKILL.md로 합성된다.
  4. 스킬은 origin='promoted'(승격)로 기록된다.

따라서 하나의 사실은 (a) 검증 게이트를 통과하고 (b) 반복되는 다단계 패턴을 형성한
뒤에야 비로소 *스킬*(에이전트가 실제로 따르게 되는 것)이 된다. 지식은 틀릴 수 있지만,
절차적 지위를 얻기 전까지는 행동을 조용히 좌우할 수 없다.
"""

from __future__ import annotations

from .store import Store, Edge
from .config import Config
from .llm import LLMClient


def _slug(name: str) -> str:
    return "knowledge-" + "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


class Promoter:
    def __init__(self, store: Store, cfg: Config, llm: LLMClient):
        self.store = store
        self.cfg = cfg
        self.llm = llm

    def _reachable_chain(self, head: str, by_src: dict[str, list[Edge]]) -> list[Edge]:
        """`head`로부터 도달 가능한 모든 검증 엣지 (비순환 BFS)."""
        seen_edges: list[Edge] = []
        visited_nodes = {head}
        frontier = [head]
        while frontier:
            node = frontier.pop()
            for e in by_src.get(node, []):
                if e.id in {x.id for x in seen_edges}:
                    continue
                seen_edges.append(e)
                if e.dst_name not in visited_nodes:
                    visited_nodes.add(e.dst_name)
                    frontier.append(e.dst_name)
        return seen_edges

    def promote(self, turn: int) -> dict:
        validated = self.store.edges_by_status("validated")
        by_src: dict[str, list[Edge]] = {}
        sources, dests = set(), set()
        for e in validated:
            by_src.setdefault(e.src_name, []).append(e)
            sources.add(e.src_name)
            dests.add(e.dst_name)

        # 사슬 머리: 사슬을 이끌지만 자신은 하류 결과가 아닌 노드
        heads = sources - dests
        promoted = []
        for head in sorted(heads):
            chain = self._reachable_chain(head, by_src)
            if len(chain) < self.cfg.promote_min_validated_edges:
                continue
            avg_conf = sum(e.confidence for e in chain) / len(chain)
            if avg_conf < self.cfg.promote_min_confidence:
                continue

            facts = [(e.src_name, e.relation, e.dst_name) for e in chain]
            name = _slug(head)
            body = self.llm.synthesize_skill(head, facts)
            self.store.upsert_skill(name, body, origin="promoted", turn=turn)
            self.store.record_validation("promotion", self.store.node_id(head),
                                         "approve", f"{len(chain)} validated edges", avg_conf)
            promoted.append(name)

        if promoted:
            self.store.log("promotion.run", f"promoted skills: {', '.join(promoted)}")
        return {"promoted": promoted}
````

---

## 14. `chiron/curator.py`

````python
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
````

---

## 15. `chiron/orchestrator.py`

````python
"""Orchestrator: 폐쇄형 자가 진화 루프.

두 부모의 루프를 두 가지 시간 척도(timescale)에서 결합한다:

  턴 단위 (hermes의 즉시 리뷰 + agi의 모니터링)
    observe()  -> 능력 기록, 지식 공백 탐지
    nudge      -> N턴마다 백그라운드 스킬 리뷰 실행

  주기 단위 (agi의 진화/창발 + hermes의 큐레이션)
    evolve()   -> 메타인지 목표 -> 지식 수집(가설)
               -> corrector 검증 -> 창발 발견 -> corrector 재검증
               -> 검증된 지식을 스킬로 승격
               -> curator가 스킬을 통합/노후화

`tick()`은 턴 카운터를 진행시키며 도래한 작업을 발동한다. 데모가 이를 구동한다.
실제 운영에서는 주기 단위 절반이 hermes의 idle 트리거 백그라운드 fork 위에서 돌게 된다.
"""

from __future__ import annotations

from typing import Callable

from .config import Config
from .store import Store
from .llm import build_llm, LLMClient
from .metacognition import MetaCognition
from .evolution import EvolutionLoop, KnowledgeSource
from .corrector import Corrector
from .emergence import EmergenceDetector
from .promotion import Promoter
from .curator import Curator


class Orchestrator:
    def __init__(self, cfg: Config | None = None,
                 knowledge_source: KnowledgeSource | None = None,
                 llm: LLMClient | None = None):
        self.cfg = cfg or Config()
        self.store = Store(self.cfg.db_path)
        self.llm = llm or build_llm(self.cfg)
        self.meta = MetaCognition(self.store, self.cfg)
        self.evolution = EvolutionLoop(self.store, self.cfg, self.llm,
                                       knowledge_source or (lambda t: ""))
        self.corrector = Corrector(self.store, self.cfg, self.llm)
        self.emergence = EmergenceDetector(self.store, self.cfg)
        self.promoter = Promoter(self.store, self.cfg, self.llm)
        self.curator = Curator(self.store, self.cfg, self.llm)
        self.turn = 0
        # 백그라운드 리뷰가 스킬을 쓰고자 할 때 발동되는 선택적 훅
        self.background_review: Callable[[int], None] | None = None

    # -- 턴 단위 ----------------------------------------------------------
    def observe(self, action: str, success: bool, confidence: float,
                unknown_terms: list[str] | None = None) -> None:
        """하나의 상호작용 결과와 그것이 드러낸 지식 공백을 기록한다."""
        self.turn += 1
        self.meta.record(action, success, confidence)
        for term in (unknown_terms or []):
            if not self.store.has_node(term):
                self.store.record_gap(term)

        if self.turn % self.cfg.goal_update_every == 0:
            self.meta.update_goals()
        if self.cfg.skill_nudge_interval and self.turn % self.cfg.skill_nudge_interval == 0:
            if self.background_review:
                self.background_review(self.turn)  # hermes식 즉시 리뷰
        if self.turn % self.cfg.auto_evolve_every == 0:
            self.evolve()

    def use_skill(self, name: str) -> bool:
        """스킬을 사용됨으로 표시한다 (stale/archive 경로에서 벗어나게 함)."""
        return self.store.touch_skill(name, self.turn)

    # -- 주기 단위 --------------------------------------------------------
    def evolve(self) -> dict:
        """하나의 완전한 진화 사이클: 수집 -> 검증 -> 발견 -> 검증 -> 승격 -> 큐레이션."""
        self.meta.update_goals()
        acquired = self.evolution.run_once()
        v1 = self.corrector.verify_pending()
        emerged = self.emergence.discover()
        v2 = self.corrector.verify_pending()
        promoted = self.promoter.promote(self.turn)
        curated = self.curator.run(self.turn)
        report = {
            "turn": self.turn,
            "acquired_edges": acquired["edges"],
            "validated": v1["validated"] + v2["validated"],
            "rejected": v1["rejected"] + v2["rejected"],
            "emergent": emerged["discovered"],
            "promoted_skills": promoted["promoted"],
            "curator": curated,
        }
        self.store.log("evolve.cycle", str(report))
        return report

    # -- 내부 상태 조회 ---------------------------------------------------
    def snapshot(self) -> dict:
        skills = self.store.skills(include_archived=True)
        return {
            "turn": self.turn,
            "skills": [(s["name"], s["origin"], s["status"]) for s in skills],
            "validated_edges": len(self.store.edges_by_status("validated")),
            "rejected_edges": len(self.store.edges_by_status("rejected")),
            "open_gaps": self.store.active_gaps(1),
        }

    def close(self) -> None:
        self.store.close()
````

---

## 16. `examples/demo.py`

````python
"""Chiron 하이브리드 자가 진화 루프의 오프라인 엔드투엔드 데모.

실행:  python -m examples.demo      (hybrid/ 디렉터리에서)
  또는: python examples/demo.py

API 키도, 데이터베이스 서버도 필요 없다 — 모든 것이 stub LLM + 인메모리 SQLite 위에서
돈다. 융합의 전 과정을 한눈에 보여준다:

  지식 공백 -> 목표 -> 수집(가설) -> 검증 게이트
  -> 창발 -> 검증 -> 스킬로의 승격(PROMOTION) -> curator 통합
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chiron import Config, Orchestrator  # noqa: E402


# 에이전트가 학습할 수 있는 작은 "세계". 각 주제는 화살표 표기 인과 시드 텍스트를
# 산출한다 — 실제 시스템에서 arXiv/위키피디아 텍스트를 대신하는 자리.
WORLD = {
    "typhoon": "typhoon -> sea temperature rise -> ocean acidification -> coral bleaching",
    "quantum computer": "quantum computer -> superposition -> processing speed -> ai breakthrough",
    "interest rate": "interest rate -> borrowing cost -> consumer spending -> supply disruption",
    "oil price": "oil price -> transport cost -> consumer spending -> supply disruption",
    # 검증 게이트가 기각하는 모습을 보여주기 위한 의도적으로 잘못된 항목:
    "bad": "coral bleaching -> big bang",
}


def knowledge_source(topic: str) -> str:
    return WORLD.get(topic, "")


def make_background_review(orch: Orchestrator):
    """hermes식 즉시 리뷰: 사용자가 가르쳐 준 절차를 스킬로 포착한다.

    세션 동안 두 개의 형제 'debugging-*' 스킬을 작성하여, 나중에 curator가 umbrella로
    통합할 거리를 만든다.
    """
    siblings = [
        ("debugging-flaky-tests",
         "## 절차\n1. 격리하여 재실행한다.\n2. 공유 상태를 점검한다.\n3. 실행 순서를 이분 탐색한다."),
        ("debugging-async-hangs",
         "## 절차\n1. 대기 중인 태스크를 덤프한다.\n2. await 안 한 코루틴을 찾는다.\n3. 타임아웃을 추가한다."),
    ]

    def _review(turn: int) -> None:
        name, proc = siblings[(turn // orch.cfg.skill_nudge_interval - 1) % len(siblings)]
        body = (f"# {name}\n\n_세션 신호에서 포착됨. "
                f"출처(provenance): background_review._\n\n{proc}")
        orch.store.upsert_skill(name, body, origin="background_review", turn=turn)
        orch.store.log("background_review", f"turn {turn}: wrote {name}")
    return _review


def banner(title: str) -> None:
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64)


def main() -> None:
    cfg = Config(auto_evolve_every=5, goal_update_every=2, skill_nudge_interval=4,
                 emergence_min_confidence=0.10)  # 지름길이 드러나도록 하한을 낮춤
    orch = Orchestrator(cfg=cfg, knowledge_source=knowledge_source)
    orch.background_review = make_background_review(orch)

    banner("PHASE 1 — 상호작용이 지식 공백을 드러낸다")
    # 에이전트가 여러 주제에 대해 '질문받는다'. 모르는 용어는 공백이 된다.
    interactions = [
        ("answer", True, 0.8, ["typhoon"]),
        ("answer", True, 0.7, ["typhoon"]),
        ("answer", False, 0.3, ["quantum computer"]),
        ("answer", True, 0.6, ["quantum computer"]),
        ("answer", True, 0.9, ["interest rate"]),
        ("answer", False, 0.4, ["interest rate"]),
        ("answer", True, 0.8, ["oil price"]),
        ("answer", True, 0.85, ["oil price"]),
    ]
    for action, ok, conf, terms in interactions:
        orch.observe(action, ok, conf, unknown_terms=terms)
        print(f"  turn {orch.turn:>2}: {terms[0]!r:<18} 에 대해 질문받음 "
              f"-> 공백 기록됨 (hit 누적 중)")

    banner("PHASE 2 — 명시적 진화 사이클 1회 실행")
    report = orch.evolve()
    for k, v in report.items():
        print(f"  {k:<16}: {v}")

    banner("PHASE 3 — 작동하는 검증 게이트")
    # 잘못된 사실을 강제로 수집하게 한 뒤 corrector가 기각하는 것을 본다.
    orch.store.record_gap("bad")
    orch.store.record_gap("bad")
    orch.meta.update_goals()
    orch.evolution.run_once()
    stats = orch.corrector.verify_pending()
    print(f"  corrector 판정: {stats}")
    print("  (coral bleaching -> big bang 은 기각됨: 결과가 우주의 기원보다 먼저 올 수 없음)")

    banner("PHASE 4 — 승격 + curator 통합")
    orch.promoter.promote(orch.turn)
    orch.curator.run(orch.turn)

    banner("최종 스냅샷")
    snap = orch.snapshot()
    print(f"  turn={snap['turn']}  validated_edges={snap['validated_edges']}  "
          f"rejected_edges={snap['rejected_edges']}")
    print("  스킬 (이름 / 출처 / 상태):")
    for name, origin, status in snap["skills"]:
        print(f"    - {name:<34} {origin:<18} {status}")

    print("\n  주목할 점:")
    print("   * 'knowledge-*' 스킬은 검증된 그래프 지식에서 승격(PROMOTED)되었다 (agi -> hermes).")
    print("   * 'debugging-flaky-tests' 는 hermes식 백그라운드 리뷰에서 나왔다.")
    print("   * 형제 스킬들은 curator에 의해 '*-umbrella' 아래로 통합되었다.")
    print("   * 그 무엇도 삭제되지 않았다 — 흡수된 스킬은 'archived'로 복구 가능하다.")

    orch.close()


if __name__ == "__main__":
    main()
````

---

## 17. `tests/test_smoke.py`

````python
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
````
