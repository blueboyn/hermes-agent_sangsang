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
