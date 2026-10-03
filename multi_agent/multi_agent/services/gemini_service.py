import json
import os
import re

from dotenv import load_dotenv
from google import genai
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "backend" / ".env")
load_dotenv()
_api_key = os.getenv("GEMINI_API_KEY")
_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
_client = genai.Client(api_key=_api_key) if _api_key else None
_llm_call_count = 0


def reset_metrics():
    global _llm_call_count
    _llm_call_count = 0


def get_metrics():
    return {"llm_calls": _llm_call_count}


def generate_text(prompt: str) -> str:
    if _client is None:
        raise RuntimeError("Chưa cấu hình GEMINI_API_KEY")
    global _llm_call_count
    _llm_call_count += 1
    response = _client.models.generate_content(model=_model, contents=prompt)
    return response.text or ""


def generate_json(prompt: str):
    text = generate_text(prompt).strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Gemini không trả về JSON hợp lệ")
        return json.loads(match.group(0))
