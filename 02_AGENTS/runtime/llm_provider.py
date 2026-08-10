import os, json, re, time
from typing import Dict, Any

try:
    from openai import OpenAI
except Exception:
    OpenAI=None

from cost_control import estimate_cost_usd, check_call_budget

MODEL_BY_AGENT={
    "A1_DISCOVERY":"gpt-5.6-luna",
    "A2_ENTITY_SCOPE":"gpt-5.6-luna",
    "A3_DEEP_SCAN":"gpt-5.6-terra",
    "A4_EVIDENCE_AUDITOR":"gpt-5.6-sol",
    "A5_TARGET_MATCH":"gpt-5.6-terra",
    "A6_BENCHMARK":"gpt-5.6-terra",
    "A7_RED_TEAM":"gpt-5.6-sol",
    "A8_COMMERCIAL_GATE":"gpt-5.6-terra",
    "A9_QA_ORCHESTRATOR":"gpt-5.6-sol",
}

REASONING_BY_AGENT={
    "A1_DISCOVERY":"low",
    "A2_ENTITY_SCOPE":"low",
    "A3_DEEP_SCAN":"medium",
    "A4_EVIDENCE_AUDITOR":"high",
    "A5_TARGET_MATCH":"medium",
    "A6_BENCHMARK":"medium",
    "A7_RED_TEAM":"high",
    "A8_COMMERCIAL_GATE":"medium",
    "A9_QA_ORCHESTRATOR":"high",
}

MAX_OUTPUT_BY_AGENT={
    "A1_DISCOVERY":2200,
    "A2_ENTITY_SCOPE":1600,
    "A3_DEEP_SCAN":4200,
    "A4_EVIDENCE_AUDITOR":3000,
    "A5_TARGET_MATCH":1600,
    "A6_BENCHMARK":3200,
    "A7_RED_TEAM":2000,
    "A8_COMMERCIAL_GATE":1600,
    "A9_QA_ORCHESTRATOR":1800,
}

WEB_ENABLED_AGENTS={"A1_DISCOVERY","A2_ENTITY_SCOPE","A3_DEEP_SCAN","A6_BENCHMARK"}


def _normalize_url(value):
    if not value or not isinstance(value, str):
        return value
    value=value.strip().replace("\\", "")
    md=re.fullmatch(r"\s*\[(https?://[^\]]+)\]\((https?://[^)]+)\)\s*", value)
    if md:
        return md.group(2).rstrip(".,)")
    urls=re.findall(r"https?://[^\s\]\)]+", value)
    if urls:
        return urls[0].rstrip(".,)")
    return value.rstrip(".,)")


def _normalize_payload(payload):
    clean=dict(payload or {})
    if "official_domain" in clean:
        clean["official_domain"]=_normalize_url(clean.get("official_domain"))
    return clean


def _response_incomplete_reason(response):
    details=getattr(response,"incomplete_details",None)
    if not details:
        return None
    if isinstance(details, dict):
        return details.get("reason") or str(details)
    return getattr(details,"reason",None) or str(details)


def _is_retryable_error(exc):
    text=str(exc).lower()
    markers=(
        "error code: 520",
        "error code: 502",
        "error code: 503",
        "error code: 504",
        "retryable': true",
        'retryable": true',
        "rate limit",
        "temporarily unavailable",
        "connection error",
        "timeout",
    )
    return any(m in text for m in markers)


class LLMProvider:
    def __init__(self, dry_run=True):
        self.dry_run=dry_run
        raw_key=os.getenv("OPENAI_API_KEY")
        self.api_key=raw_key.strip() if raw_key else None
        self.client=OpenAI(api_key=self.api_key) if (not dry_run and self.api_key and OpenAI) else None

    def readiness(self):
        return {
            "openai_sdk_available": OpenAI is not None,
            "api_key_present": bool(self.api_key),
            "live_ready": bool(OpenAI is not None and self.api_key),
        }

    def _tools_for_agent(self, agent_id: str, payload: Dict[str,Any]):
        if agent_id not in WEB_ENABLED_AGENTS:
            return []
        domain=_normalize_url(payload.get("official_domain"))
        tool={"type":"web_search","search_context_size":"low"}
        if domain:
            try:
                from urllib.parse import urlparse
                host=urlparse(domain).netloc or domain
                host=host.split(":")[0].strip().lower()
                if host.startswith("www."):
                    host=host[4:]
                if host:
                    tool["filters"]={"allowed_domains":[host]}
            except Exception:
                pass
        return [tool]

    def run(self, agent_id: str, system_prompt: str, payload: Dict[str,Any]):
        payload=_normalize_payload(payload)
        model=os.getenv(f"RRT_MODEL_{agent_id}", MODEL_BY_AGENT.get(agent_id,"gpt-5.6-terra"))
        reasoning=REASONING_BY_AGENT.get(agent_id,"medium")
        tools=self._tools_for_agent(agent_id,payload)

        if self.dry_run:
            return {
              "mode":"DRY_RUN",
              "agent_id":agent_id,
              "model_planned":model,
              "reasoning_effort_planned":reasoning,
              "tools_planned":[t.get("type") for t in tools],
              "normalized_official_domain":payload.get("official_domain"),
              "received_payload_keys":sorted(payload.keys()),
              "message":"Task accepted. Live OpenAI call not executed."
            }

        if not self.client:
            raise RuntimeError("Live mode requested but OPENAI_API_KEY or openai SDK is unavailable.")

        user_input=json.dumps(payload,ensure_ascii=False)
        default_max=MAX_OUTPUT_BY_AGENT.get(agent_id,1600)
        max_output_tokens=int(os.getenv(f"RRT_MAX_OUTPUT_TOKENS_{agent_id}", os.getenv("RRT_MAX_OUTPUT_TOKENS", str(default_max))))
        estimated_input_tokens=max(1, len(system_prompt + user_input)//4)
        estimated_usd=estimate_cost_usd(model, estimated_input_tokens, max_output_tokens)
        allowed, reason=check_call_budget(estimated_usd)
        if not allowed:
            raise RuntimeError(f"BUDGET_BLOCK: {reason}")

        kwargs={
            "model":model,
            "reasoning":{"effort":reasoning},
            "instructions":system_prompt,
            "input":user_input,
            "max_output_tokens":max_output_tokens,
        }
        if tools:
            kwargs["tools"]=tools
            kwargs["tool_choice"]="auto"

        max_attempts=max(1, int(os.getenv("RRT_API_MAX_ATTEMPTS", "3")))
        base_delay=max(1.0, float(os.getenv("RRT_API_RETRY_BASE_SECONDS", "2")))
        response=None
        last_error=None
        for attempt in range(1, max_attempts + 1):
            try:
                response=self.client.responses.create(**kwargs)
                break
            except Exception as exc:
                last_error=exc
                if attempt >= max_attempts or not _is_retryable_error(exc):
                    raise
                time.sleep(base_delay * (2 ** (attempt - 1)))
        if response is None:
            raise last_error or RuntimeError("OpenAI call failed without response")

        text=getattr(response,"output_text",None)
        if not text:
            text=str(response)

        incomplete_reason=_response_incomplete_reason(response)
        try:
            parsed=json.loads(text)
            parse_status="PASS"
        except Exception:
            parsed={"raw_output":text}
            parse_status="TRUNCATED_JSON" if incomplete_reason in {"max_output_tokens","max_tokens"} else "FAIL_JSON"

        usage={}
        actual_cost_usd=0.0
        try:
            u=response.usage
            usage={
              "input_tokens":getattr(u,"input_tokens",None),
              "output_tokens":getattr(u,"output_tokens",None),
              "total_tokens":getattr(u,"total_tokens",None),
            }
            actual_cost_usd=estimate_cost_usd(model, usage.get("input_tokens") or 0, usage.get("output_tokens") or 0)
        except Exception:
            pass

        return {
          "mode":"LIVE_OPENAI_RESPONSES",
          "agent_id":agent_id,
          "model":model,
          "reasoning_effort":reasoning,
          "tools_enabled":[t.get("type") for t in tools],
          "normalized_official_domain":payload.get("official_domain"),
          "response_id":getattr(response,"id",None),
          "parse_status":parse_status,
          "incomplete_reason":incomplete_reason,
          "output":parsed,
          "usage":usage,
          "estimated_cost_usd":round(estimated_usd,6),
          "actual_cost_usd":round(actual_cost_usd,6),
        }
