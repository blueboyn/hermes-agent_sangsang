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
