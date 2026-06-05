"""LLM abstraction.

Chiron never calls a provider directly — it talks to an ``LLMClient``. Two
implementations ship here:

  * ``StubLLM`` — fully deterministic, offline. It lets the entire
    self-evolution loop run (and be unit-tested) with no API key. It mimics the
    *shape* of real responses: knowledge extraction, edge validation, skill
    synthesis. Heuristics are intentionally simple but plausible.
  * ``OpenAICompatibleLLM`` — a thin client for any OpenAI-compatible endpoint
    (OpenRouter, LM Studio, Anthropic-compat, local). Used when configured.

This mirrors hermes' provider-agnostic design and agi's "graceful degradation":
if no LLM is reachable, the stub keeps the loop alive.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol


# ----------------------------------------------------------------------------
# Structured response shapes (so callers never parse free text twice)
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
# Offline deterministic stub
# ----------------------------------------------------------------------------
_CAUSAL_HINTS = ("cause", "lead", "increase", "raise", "improve", "유발", "상승", "향상", "초래")
_STOP = {"a", "an", "the", "of", "and", "to", "in", "is", "are", "그", "이", "수", "및"}


class StubLLM:
    """Deterministic stand-in. No network, no randomness."""

    def extract_facts(self, topic: str, text: str) -> list[Fact]:
        """Turn 'A -> B -> C' style seed text into causal edges.

        The demo feeds simple arrow-notation 'knowledge'; real text would be
        parsed by a real model. We keep extraction transparent for testing.
        """
        facts: list[Fact] = []
        for line in text.splitlines():
            line = line.strip()
            if "->" not in line:
                continue
            chain = [p.strip() for p in line.split("->") if p.strip()]
            for i in range(len(chain) - 1):
                src, dst = chain[i], chain[i + 1]
                # plausibility heuristic: shorter, content-bearing links score higher
                conf = round(0.55 + 0.1 * min(len(src.split()), 3) / 3, 3)
                facts.append(Fact(src=src, dst=dst, relation="causes",
                                  strength=0.7, confidence=conf))
        return facts

    def validate_edge(self, src: str, relation: str, dst: str, confidence: float) -> Verdict:
        """Approve causal-looking, non-self edges; flag the rest as doubtful."""
        if src.lower() == dst.lower():
            return Verdict(False, "rejected", "self-loop", 0.95)
        # reject obviously reversed temporal claims the stub can recognise
        if dst.lower() in {"big bang", "빅뱅"}:
            return Verdict(False, "rejected", "effect precedes a cosmic origin", 0.9)
        if confidence >= 0.5:
            return Verdict(True, "valid", "plausible causal mechanism", min(confidence + 0.1, 0.99))
        if confidence >= 0.35:
            return Verdict(False, "doubtful", "weak signal, needs more evidence", confidence)
        return Verdict(False, "rejected", "below confidence floor", confidence)

    def synthesize_skill(self, name: str, facts: list[tuple[str, str, str]]) -> str:
        """Render validated facts into a procedural SKILL.md body."""
        lines = [f"# {name}", "",
                 "_Auto-promoted from validated knowledge. Provenance: promoted._", "",
                 "## When to use", f"When reasoning about **{name}** or its consequences.", "",
                 "## Known causal structure"]
        for src, rel, dst in facts:
            lines.append(f"- `{src}` {rel} `{dst}`")
        lines += ["", "## Procedure",
                  "1. Identify which known cause(s) above are present.",
                  "2. Follow the chain to anticipate downstream effects.",
                  "3. If a step is missing, file a knowledge gap and re-evaluate."]
        return "\n".join(lines)

    def name_umbrella(self, prefix: str, members: list[str]) -> str:
        base = prefix.strip("-_ ") or "general"
        return f"{base}-umbrella"


# ----------------------------------------------------------------------------
# Real provider (best-effort, optional dependency)
# ----------------------------------------------------------------------------
class OpenAICompatibleLLM:
    """Minimal OpenAI-compatible chat client. Falls back to StubLLM on any error."""

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
