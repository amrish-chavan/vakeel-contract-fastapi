import json
import asyncio

from config import GEMINI_API_KEY
from google import genai
from google.genai import errors as genai_errors
from service.prompt import (
    CONTRACT_ANALYSIS_PROMPT,
)
from models import AnalysisResult, ClauseAnalysis, RiskFlag, RiskLevel

MODEL_NAME = "gemini-3.7-flash"


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=GEMINI_API_KEY)


def _generate_response(prompt: str):
    client = _get_client()
    chat = client.chats.create(model=MODEL_NAME)
    return chat.send_message(prompt)


def _strip_json_fences(raw_text: str) -> str:
    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    return raw_text.strip()

async def analyze_contract(contract_id: str, text_content: str):
    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=text_content[:15000])

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = await asyncio.to_thread(_generate_response, prompt)
            response_text = getattr(response, "text", None)
            if not isinstance(response_text, str) or not response_text.strip():
                raise ValueError("Gemini returned an empty response")

            raw_text = _strip_json_fences(response_text)
            analysis_data = json.loads(raw_text)
            break
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc
        except genai_errors.APIError as exc:
            last_error = exc
            if getattr(exc, "code", None) in {429, 500, 502, 503, 504} and attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            raise RuntimeError(
                f"Gemini API error ({getattr(exc, 'code', 'unknown')}): {exc}"
            ) from exc
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Gemini analysis failed: {exc}") from exc
    else:
        raise RuntimeError(f"Gemini analysis failed: {last_error}")

    key_clauses = [
        ClauseAnalysis(**clause)
        for clause in analysis_data.get("key_clauses", [])
    ]

    risk_flags = []
    for risk in analysis_data.get("risk_flags") or analysis_data.get("rish_flags") or []:
        if "recommendation" not in risk and "reccommedation" in risk:
            risk["recommendation"] = risk.pop("reccommedation")
        risk_flags.append(RiskFlag(**risk))

    overall = analysis_data.get("overall_risk") or analysis_data.get("overall_risk_level") or "low"

    return AnalysisResult(
        contract_id=contract_id,
        summary=analysis_data.get("summary", ""),
        contract_type=analysis_data.get("contract_type", ""),
        key_clauses=key_clauses,
        risk_flags=risk_flags,
        overall_risk=RiskLevel(str(overall).lower()),
        recommendations=analysis_data.get("recommendations") or [],
    )
