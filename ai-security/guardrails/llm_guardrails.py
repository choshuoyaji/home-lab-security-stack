"""
LLM Input/Output Security Guardrails
Validates and sanitizes user input and LLM output to prevent
prompt injection, data leakage, and insecure output handling.

Author: Takahiro Oda
"""

import re
import base64
from typing import Optional


class LLMGuardrails:
    """Input/output security guardrails for LLM applications"""

    INJECTION_PATTERNS = [
        r"ignore (?:all )?(?:previous|above|prior) (?:instructions|prompts)",
        r"you are now (?:in )?(?:DAN|developer|unrestricted) mode",
        r"(?:forget|disregard) (?:your|all) (?:rules|instructions|guidelines)",
        r"(?:system|admin) prompt[:\s]",
        r"<\|(?:im_start|system|endoftext)\|>",
        r"\[INST\].*?\[/INST\]",
        r"(?:base64|rot13|hex)[\s_]?(?:decode|encode)",
    ]

    OUTPUT_BLOCK_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        r"\b(?:sk-|pk_live_|AKIA)[A-Za-z0-9]{20,}\b",
        r"(?:password|secret|token)\s*[:=]\s*\S+",
    ]

    def __init__(self, max_input_length=4096, max_output_length=8192):
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.injection_regex = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]
        self.output_regex = [re.compile(p) for p in self.OUTPUT_BLOCK_PATTERNS]

    def validate_input(self, user_input: str) -> dict:
        """Validate and sanitize user input before LLM processing"""
        result = {
            "safe": True,
            "sanitized_input": user_input,
            "warnings": [],
            "blocked": False,
            "risk_score": 0.0,
        }

        if len(user_input) > self.max_input_length:
            result["sanitized_input"] = user_input[: self.max_input_length]
            result["warnings"].append(
                f"Input truncated from {len(user_input)} chars"
            )
            result["risk_score"] += 0.1

        for pattern in self.injection_regex:
            if pattern.search(user_input):
                result["safe"] = False
                result["blocked"] = True
                result["warnings"].append(
                    f"Prompt injection detected: {pattern.pattern[:50]}"
                )
                result["risk_score"] += 0.8

        if self._detect_encoding_attack(user_input):
            result["warnings"].append("Possible encoding-based attack")
            result["risk_score"] += 0.5

        return result

    def validate_output(self, llm_output: str) -> dict:
        """Validate LLM output before returning to user"""
        result = {
            "safe": True,
            "sanitized_output": llm_output,
            "redacted_items": [],
        }

        sanitized = llm_output
        for pattern in self.output_regex:
            matches = pattern.findall(sanitized)
            if matches:
                result["redacted_items"].extend(matches)
                sanitized = pattern.sub("[REDACTED]", sanitized)

        if result["redacted_items"]:
            result["safe"] = False
            result["sanitized_output"] = sanitized

        if len(sanitized) > self.max_output_length:
            result["sanitized_output"] = sanitized[: self.max_output_length]

        return result

    def _detect_encoding_attack(self, text: str) -> bool:
        """Detect base64/hex encoded injection attempts"""
        b64_pattern = re.findall(r"[A-Za-z0-9+/]{20,}={0,2}", text)
        for candidate in b64_pattern:
            try:
                decoded = base64.b64decode(candidate).decode(
                    "utf-8", errors="ignore"
                )
                for pattern in self.injection_regex:
                    if pattern.search(decoded):
                        return True
            except Exception:
                continue
        return False
