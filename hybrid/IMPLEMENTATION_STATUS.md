# Chiron 구현 현황 (분석서 대비)

외부 코드 리뷰(`Chiron 분석서 & 실행 계획`, 2026-06-05)의 결함 6건과 Phase 계획에
대한 실제 구현 진행 상황. 진단은 전부 타당했고, 그에 맞춰 단계적으로 반영 중.

## 결함별 상태

| ID | 결함 | 심각도 | 상태 | 조치 |
|----|------|:---:|:---:|------|
| D-3 | 강등 경로 + skill↔edge 링크 부재 | 🔴 | ✅ **완료** | `skill_edges` 정션 테이블 + `Reconciler` (지식 변화 시 철회) |
| D-5 | 스킬 자기소멸(소비 신호 부재) | 🟠 | ✅ **가드 완료** | curator가 미소비 promoted 스킬을 idle-archive에서 제외. 실제 소비 채널은 Phase 4 |
| D-6 | 데모 게이트 시연이 연극 | 🟡 | ✅ **완료** | PHASE 3에 stub 하드코딩임을 명시하는 정직한 라벨 추가 |
| D-2 | 검증 게이트 확증편향 | 🔴 | ⏳ Phase 2 | PMI 독립 prior + 추출/검증 모델 분리 (예정) |
| D-4 | confidence 의미 혼용 | 🟠 | ⏳ Phase 2 | conf 3필드 분리(extract/path/verify) (예정) |
| D-1 | "반복" 미구현 | 🔴 | ⏳ Phase 3 | `recurrence` 카운터 + 승격 조건 추가 (예정) |

## Phase 0 — 기반 (완료)

- **`skill_edges` 테이블** (`store.py`): `(skill_id, edge_id, role, created_turn)`.
  역추적/의존성 조회 API: `skill_support_edge_ids`, `skills_depending_on`,
  `edge_status`, `link_skill_edge`, `clear_skill_edges`.
- **승격 시 링크 기록** (`promotion.py`): 사슬의 각 엣지를 `head`/`support` 역할로
  연결. 재승격 시 현재 사슬과 일치하도록 링크를 새로 고침.
- **정직한 데모 라벨** (`demo.py` PHASE 3, D-6).
- 회귀 테스트: `test_skill_has_edge_provenance`.

## Phase 1 — 강등/조정 루프 (완료)

- **`Reconciler`** (`reconciler.py`): 근거 엣지의 live(validated) 수가
  `promote_min_validated_edges` 미만으로 떨어진 파생 스킬을 **철회(archive)**.
  삭제 아님 — origin 보존, `validations`에 `retraction` 사유 기록, 복구 가능.
- **orchestrator 통합**: `evolve()`에서 promote 직후·curator 직전에 `reconcile()`
  실행(철회된 지식이 umbrella로 통합되지 않도록).
- **D-5 가드** (`curator.py`): 한 번도 소비되지 않은 `origin='promoted'` 스킬은
  idle 기반 stale/archive 대상에서 제외. (지식 변화에 의한 철회는 Reconciler가 담당.)
- **출처 링크 전파** (`curator.py`): 통합 시 흡수된 형제의 근거 엣지를 umbrella에
  이어 붙여, Reconciler가 통합된 스킬도 철회할 수 있게 함.
- 회귀 테스트: `test_retraction_archives_skill`,
  `test_promoted_skill_not_idle_archived_without_use`,
  `test_non_derived_skill_survives_reconcile`.

## 검증

- 스모크 테스트 **9/9 통과** (기존 5 + 신규 4).
- 오프라인 데모: PHASE 5에서 근거 엣지를 뒤집자 `knowledge-umbrella`가 자동 철회되고
  복구 가능한 archived 상태로 전이됨을 실증.

## 다음 (미착수)

- **Phase 2** (무결성): D-2 PMI 독립 prior(상상이 wordrelation 자산 확인 선행) +
  추출≠검증 모델 분리, D-4 conf 3필드 분리.
- **Phase 3** ("반복"): D-1 recurrence 게이트.
- **Phase 4** (본체 접합): 실 LLM/수집기/Neo4j/소비 채널 — *이 환경 밖, 본체 인프라
  필요*. 인터페이스(store 백엔드 추상화, 소비 채널 훅)까지만 여기서 준비.
