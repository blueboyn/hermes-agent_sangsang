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
