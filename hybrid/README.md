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
