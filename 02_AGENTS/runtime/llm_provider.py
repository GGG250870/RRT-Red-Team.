import os, json
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

    def run(self, agent_id: str, system_prompt: str, payload: Dict[str,Any]):
        model=os.getenv(f"RRT_MODEL_{agent_id}", MODEL_BY_AGENT.get(agent_id,"gpt-5.6-terra"))
        reasoning=REASONING_BY_AGENT.get(agent_id,"medium")

        if self.dry_run:
            return {
              "mode":"DRY_RUN",
              "agent_id":agent_id,
              "model_planned":model,
              "reasoning_effort_planned":reasoning,
              "received_payload_keys":sorted(payload.keys()),
              "message":"Task accepted. Live OpenAI call not executed."
            }

        if not self.client:
            raise RuntimeError("Live mode requested but OPENAI_API_KEY or openai SDK is unavailable.")

        user_input=json.dumps(payload,ensure_ascii=False)
        max_output_tokens=int(os.getenv("RRT_MAX_OUTPUT_TOKENS", "1200"))
        estimated_input_tokens=max(1, len(system_prompt + user_input)//4)
        estimated_usd=estimate_cost_usd(model, estimated_input_tokens, max_output_tokens)
        allowed, reason=check_call_budget(estimated_usd)
        if not allowed:
            raise RuntimeError(f"BUDGET_BLOCK: {reason}")

        response=self.client.responses.create(
            model=model,
            reasoning={"effort":reasoning},
            instructions=system_prompt,
            input=user_input,
            max_output_tokens=max_output_tokens,
        )

        text=getattr(response,"output_text",None)
        if not text:
            text=str(response)

        try:
            parsed=json.loads(text)
            parse_status="PASS"
        except Exception:
            parsed={"raw_output":text}
            parse_status="FAIL_JSON"

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
          "response_id":getattr(response,"id",None),
          "parse_status":parse_status,
          "output":parsed,
          "usage":usage,
          "estimated_cost_usd":round(estimated_usd,6),
          "actual_cost_usd":round(actual_cost_usd,6),
        }
