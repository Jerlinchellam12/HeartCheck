
import os
import time

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from the project .env file
load_dotenv(override=True)

# ----------------------------------------------------------
# PROVIDER: Groq
# ----------------------------------------------------------
# Groq hosts open models (Llama 3.x) behind an OpenAI-compatible API,
# so we reuse the standard `openai` SDK and just point it at Groq's
# base_url. Switched to Groq because Google AI Studio's free tier was
# returning persistent 503 "high demand" errors that blocked testing
# the actual research question (whether prompt structure affects the
# model's response to gendered symptom descriptions) — a chatbot that
# can't reliably answer can't be used to study that at all.

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

client = (
    OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
    if API_KEY else None
)


# ----------------------------------------------------------
# NO CONTENT-STEERING SYSTEM PROMPT, BY DESIGN
# ----------------------------------------------------------
# Earlier versions sent a system prompt instructing the model never to
# downplay symptoms, never reassure, always mention 999, etc. That is
# a reasonable product safeguard, but it is a confound for *this*
# research question: it makes the model's text more constrained than
# the bare consumer chatbots audited in the A1 literature (Zack et
# al. 2024; Rickman 2025), so any bias those papers found could be
# masked here by our own instructions rather than genuinely absent.
#
# generate_response() therefore sends NO system prompt by default —
# the model sees only the conversation, i.e. what a real user would
# actually get from this model. The project's safety floor does not
# depend on the model's wording: the 999 emergency banner and research
# disclaimer in app.py are static HTML, not model-generated, and stay
# on screen regardless of mode, gender, or what the model says.
#
# OPTIONAL_SAFETY_INSTRUCTIONS is kept below, unused by default, so a
# second condition ("raw" vs "safety-prompted") can be run later if
# you want to test directly whether guardrails suppress the bias.

OPTIONAL_SAFETY_INSTRUCTIONS = """
You are HeartCheck, an academic human-AI interaction research prototype.

The application uses fictional patient scenarios only.

Your role is to respond clearly and consistently to the information provided.

Rules:
- Never claim to diagnose a medical condition.
- Never claim that a patient is safe or rule out a heart attack.
- Never invent symptoms or patient information.
- Explain uncertainty in plain language.
- Do not replace professional medical assessment.
- Do not provide personalised treatment instructions.
- Treat this as a research prototype, not a clinical tool.
- For suspected heart attack symptoms in the UK, remind the user
  that they should call 999 immediately.
"""


# ==========================================================
# SIMULATED FALLBACK
# ==========================================================
# Kept as a safety net even on Groq (which has been far more reliable
# in testing than the free Google tier) so the prototype stays
# demonstrable if the key is missing, the account is rate-limited, or
# the network is unavailable. Never presented as a real AI output.

FALLBACK_TEMPLATES = {
    "cardiac": (
        "Based on the description given, the combination of chest-area "
        "discomfort with pain spreading to the arm or jaw is one of the "
        "patterns commonly associated with a possible heart attack. "
        "This cannot be confirmed or ruled out here. If this were a real "
        "situation, this combination would normally be treated as an "
        "emergency."
    ),
    "atypical": (
        "The symptoms described (such as breathlessness, fatigue, nausea "
        "or dizziness) can sometimes appear instead of, or alongside, "
        "chest pain in a possible heart attack, and are sometimes taken "
        "less seriously than chest pain. This cannot be confirmed or "
        "ruled out here."
    ),
    "generic": (
        "The information given has been noted. Some details that would "
        "normally help assess urgency (such as onset, severity or "
        "additional symptoms) may be missing. This response cannot "
        "confirm or rule out a heart attack."
    ),
}

FALLBACK_CLOSING = (
    "This is a predefined demonstration response, not an AI-generated "
    "answer, because the live model was unavailable. For suspected heart "
    "attack symptoms in the UK, call 999 immediately — do not wait for a "
    "chatbot response."
)


def _short_reason(error):
    """Turn an exception into a short, human-readable label for the UI."""

    text = str(error).upper()

    if "API KEY" in text or "AUTHENTICATION" in text or "401" in text:
        return "no/invalid API key configured"
    if "503" in text or "UNAVAILABLE" in text or "502" in text or "504" in text:
        return "model temporarily unavailable"
    if "429" in text or "RATE_LIMIT" in text or "RESOURCE_EXHAUSTED" in text:
        return "rate limit / quota exceeded (429)"
    if "403" in text or "PERMISSION" in text:
        return "permission denied (403)"
    if "404" in text or "NOT_FOUND" in text or "DOES NOT EXIST" in text:
        return "model not found (404)"
    if "500" in text or "INTERNAL" in text:
        return "server error (500)"
    if "CONNECTION" in text or "TIMEOUT" in text:
        return "network/connection error"
    return "unknown error"


def _last_user_text(messages):
    for message in reversed(messages):
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


def _build_simulated_response(messages, error):
    """Build a clearly-labelled simulated reply when the live model fails."""

    lower = _last_user_text(messages).lower()

    if any(k in lower for k in ["chest", "arm", "jaw", "pressure", "tight"]):
        body = FALLBACK_TEMPLATES["cardiac"]
    elif any(k in lower for k in ["breath", "nausea", "fatigue", "dizzy", "sweat"]):
        body = FALLBACK_TEMPLATES["atypical"]
    else:
        body = FALLBACK_TEMPLATES["generic"]

    reason = _short_reason(error)

    text = (
        f"**[SIMULATED DEMO RESPONSE]**\n\n{body}\n\n{FALLBACK_CLOSING}\n\n"
        f"*(Live model unavailable: {reason}.)*"
    )

    return text, reason


def prepare_messages(messages, system_instructions=None):
    """
    Build the chat-completions message list: an optional system
    instruction followed by the conversation history. By default
    system_instructions is None, so nothing is prepended and the
    model responds exactly as it would to a real user — see the note
    above OPTIONAL_SAFETY_INSTRUCTIONS for why.
    """

    formatted = []

    if system_instructions:
        formatted.append({"role": "system", "content": system_instructions})

    for message in messages:
        role = message.get("role", "user")
        role = "assistant" if role == "assistant" else "user"
        formatted.append({
            "role": role,
            "content": str(message.get("content", "")),
        })

    return formatted


def _call_live_model(messages, max_retries=3, system_instructions=None):
    """Call the real Groq-hosted model. Raises on any failure."""

    if not API_KEY:
        raise ValueError("Groq API key not found. Check your .env file.")

    if client is None:
        raise RuntimeError("Groq client could not be initialised.")

    formatted_messages = prepare_messages(messages, system_instructions)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=formatted_messages,
                temperature=0.2,
                max_tokens=900,
            )

            text = response.choices[0].message.content

            if not text:
                raise RuntimeError("Groq returned an empty response.")

            return text

        except Exception as error:
            error_text = str(error)
            upper_error = error_text.upper()

            temporary_error = any(
                code in upper_error
                for code in [
                    "503", "UNAVAILABLE", "500", "INTERNAL", "502", "504",
                ]
            )

            if temporary_error and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(
                    f"Temporary Groq API error. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
                continue

            raise RuntimeError(
                f"HeartCheck API request failed: {error_text}"
            ) from error

    raise RuntimeError("Groq service remained unavailable after retries.")


def generate_response(messages, max_retries=3, system_instructions=None):
    """
    Generate a HeartCheck reply.

    Always tries the live model first. If the live call fails for any
    reason (quota, outage, missing key, etc.), falls back to a clearly
    labelled simulated response so the prototype stays demonstrable.

    system_instructions defaults to None — i.e. the raw model, with no
    added safety wording — so Standard and Structured Chat both show
    what the model actually says. Pass OPTIONAL_SAFETY_INSTRUCTIONS
    here to run a "safety-prompted" comparison condition instead.

    Returns a dict:
        {
            "text":   the reply to display,
            "source": "LIVE" or "SIMULATED",
            "reason": short failure reason, or None if source == "LIVE",
            "error":  the raw exception text, or None if source == "LIVE",
        }
    """

    if not messages:
        raise ValueError("No messages provided.")

    try:
        text = _call_live_model(
            messages,
            max_retries=max_retries,
            system_instructions=system_instructions,
        )
        return {"text": text, "source": "LIVE", "reason": None, "error": None}

    except Exception as error:
        # Logging the response source, as required: printed to the
        # console now; the evaluation stage will also write this to
        # the results CSV alongside each scenario run.
        print(f"[HeartCheck] Falling back to SIMULATED response. Cause: {error}")

        text, reason = _build_simulated_response(messages, error)

        return {
            "text": text,
            "source": "SIMULATED",
            "reason": reason,
            "error": str(error),
        }
