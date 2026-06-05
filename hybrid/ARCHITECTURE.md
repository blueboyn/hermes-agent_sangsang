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
