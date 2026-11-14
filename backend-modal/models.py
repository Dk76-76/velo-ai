import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")


def generate_ai_response(system_prompt: str, user_prompt: str) -> dict:
    """100% Pure Groq Multi-Model Brain (Auto-detects active Llama/Qwen models)"""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY missing in .env file!")

    client = Groq(api_key=GROQ_API_KEY, timeout=20.0)
    live_models = [m.id for m in client.models.list().data]

    chat_models = [
        m for m in live_models
        if not any(skip in m.lower() for skip in ["whisper", "guard", "tts", "vision", "embed", "playai", "allam"])
    ]

    preferred = sorted(
        chat_models,
        key=lambda x: (
            0 if "llama-3.3" in x.lower() else
            1 if "llama-3.1" in x.lower() else
            2 if "llama" in x.lower() else 3
        )
    )

    last_error = None
    for model_name in preferred[:4]:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            return {
                "text": completion.choices[0].message.content,
                "model_used": f"Groq ({model_name})"
            }
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Groq models failed: {last_error}")