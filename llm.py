import os
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "deepseek-r1")


def ask_llm(prompt, mode="chat"):

    if MODEL_PROVIDER == "gemini":
        return ask_gemini(prompt)

    elif MODEL_PROVIDER == "ollama":

        if mode == "research":
            return ask_ollama(
                prompt,
                model=RESEARCH_MODEL,
                max_tokens=600,
                temperature=0.1
            )

        else:
            return ask_ollama(
                prompt,
                model=DEFAULT_MODEL,
                max_tokens=400,
                temperature=0.3
            )

    else:
        return "Invalid MODEL_PROVIDER"


# ==============================
# GEMINI
# ==============================

def ask_gemini(prompt):

    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("Gemini error:", e)
        return "AI provider error."


# ==============================
# OLLAMA
# ==============================

def ask_ollama(prompt, model, max_tokens=400, temperature=0.3):

    try:

        system_prompt = """
You are Shadow AI, an advanced private AI assistant.

Identity:
- Your name is Shadow AI.
- You run locally and prioritize privacy.
- You assist users with technical questions, cybersecurity tasks, research, and general knowledge.

Behavior:
- Be clear, concise, and professional.
- Never say you do not have a name.
- Always refer to yourself as Shadow AI if needed.
- Provide accurate and helpful responses.
"""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            },
            timeout=300
        )

        if response.status_code != 200:
            return "Model error occurred."

        data = response.json()

        return data.get("response", "")

    except requests.exceptions.Timeout:
        return "Model timed out. Try smaller input."

    except Exception as e:
        print("Ollama error:", e)
        return "Model error occurred."