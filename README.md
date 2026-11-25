# HeartCheck

**README prose word count: ~956 words** (excluding headings, code blocks, and commands)

## Project overview

HeartCheck is an academic research prototype exploring whether structured, human-in-the-loop conversational design produces more consistent AI responses to gendered descriptions of possible heart attack symptoms than a standard free-text chatbot. It was built for an Intelligent Interactive Systems module project, developing the research question from an earlier literature review on gender bias in conversational AI symptom checkers.

## Research question

Does a structured interaction — consistent follow-up questions plus an editable, human-confirmed summary — produce more consistent symptom recognition and urgency advice across matched male/female fictional scenarios than a standard free-text chatbot, using the same underlying model?

## Current scope / status

- **Implemented**: Standard Chat (free-text) and Structured Chat (guided questions → generated summary → user edits/confirms → sent to the model), with multi-turn follow-up in both.
- **Implemented**: a live Groq-hosted model with retry handling, and a clearly labelled SIMULATED fallback (visible reason, retry button) for when the live call fails.
- **Implemented**: an exploratory probe (`evaluation/quick_probe.py`) running 4 matched symptom scenarios × 2 genders × 3 repeats (24 live calls) through the raw model, with results in `evaluation/quick_probe_output.md`.
- **Simulated**: the fallback responses themselves are predefined text, used only when the live model is unavailable — never presented as real AI output.
- **Planned, not yet built**: a formal, scored CSV evaluation framework (stubbed in `evaluation/evaluate.py`); a system diagram; storyboards/screenshots.
- Fictional, role-played scenarios only — this is a research prototype, not a medical device, and gives no diagnosis.

## Technology stack

- Python 3.12, Streamlit (UI).
- Groq (console.groq.com), model `openai/gpt-oss-120b`, called through the `openai` Python SDK pointed at Groq's OpenAI-compatible endpoint. Originally built against Google's Gemini/Gemma via `google-genai`; switched to Groq because the Google AI Studio free tier returned persistent 503 "high demand" errors that blocked actually testing the research question.
- `python-dotenv` for configuration.
- Not yet decided: whether a second model will be added later for a "does bias vary by model" comparison — `GROQ_MODEL` is already swappable via `.env` for this.

## Running the app

```
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

### Getting a Groq key (free, no card required)

1. Sign up at console.groq.com
2. API Keys → Create API Key
3. Paste it into `.env` as `GROQ_API_KEY` (never commit this file — it's gitignored)

If no key is set, or the live call fails for any reason, the app still works: it shows a clearly labelled simulated reply instead of crashing.

## Using the two modes

- **Standard Chat**: type a fictional patient's symptoms in free text; the model replies, and the conversation can continue.
- **Structured Chat**: fill in the guided fields (gender, symptoms, onset, severity, additional symptoms) → review the generated summary → edit anything wrong → confirm → it's sent to the model. The editable-summary step is the human-in-the-loop design the project is actually testing.

## Running the probe / inspecting results

```
python -m evaluation.quick_probe
```

Runs the 4 matched scenario pairs × 3 repeats and writes `evaluation/quick_probe_output.md` (a flag-frequency summary table, then full transcripts). The file currently in the repository is the real output from the last run, not a manually written example.

## Development record

Commit history: https://github.com/Jerlinchellam12/HeartCheck/commits/main — 3 commits, grouped by feature area (git was initialised after the initial build, not from day one, so grouping reflects feature area rather than a strict day-by-day diary):

1. `1d0e299` — Streamlit app: both chat modes, human-in-the-loop summary review, hardcoded 999/disclaimer banner.
2. `9e36fd9` — LLM layer: switched from Google Gemini (unreliable free tier) to Groq; added retry handling and the simulated fallback with visible labelling; removed the custom safety system prompt by design (see below).
3. `6ef4609` — Exploratory gender-bias probe script and its first real, 3×-repeated, 24-call results.

**A deliberate design change worth explaining**: earlier versions sent the model a system prompt instructing it never to downplay symptoms, always mention 999, etc. That instruction is removed by default now. Reason: it made the model's output more constrained than the bare consumer chatbots audited in the A1 literature, which would have hidden exactly the effect this project is trying to observe. The app's actual safety floor (the 999 banner and disclaimer) is static HTML, independent of what the model says, so removing the steering prompt from the model call was safe to do. This was verified by testing: the raw model, unprompted, gave UK-inappropriate advice (911 instead of 999) and unsolicited personalised treatment steps — itself a relevant observation, not just a side effect of the change.

## Testing

- `python test_api.py` — quick live/simulated connectivity check.
- `python -m evaluation.quick_probe` — the matched-scenario probe (makes ~24 real API calls).
- Manually tested both modes for empty input, mode switching, follow-up turns, and the summary-edit-then-resubmit flow.

## Known limitations

- Mostly single-run interactive testing; the formal probe used 3 repeats per condition, which is still exploratory, not statistically powered.
- One model only (Groq's `openai/gpt-oss-120b`) — the A1 literature found bias effects vary by model, so results here may not generalise to other models.
- The probe's keyword-based "flags" are a convenience for spotting patterns quickly, not a validated scoring method.
- No formal CSV evaluation framework yet (planned — see `evaluation/evaluate.py`).

## AI assistance statement

I used Claude Code throughout development: to inspect and debug the existing codebase, implement the simulated-fallback mechanism, migrate the LLM provider, write the gender-bias probe script, and advise on git/GitHub setup. The research question, the four matched scenario types, and the structured-vs-standard interaction design all come from my own A1 literature review, not from the AI. I made the key decisions myself at each step — for example, choosing Groq after Claude presented the provider trade-offs, choosing to remove the system prompt so the raw model's behaviour could actually be observed, and choosing to run the probe three times per condition instead of accepting a single run as evidence. I ran every git command myself from my own terminal rather than having it done for me, so the commit history reflects my own actions. I read the model outputs directly and checked them myself — including catching that one raw response gave a US emergency number and personalised treatment advice — rather than taking Claude's summaries at face value.

## Repository structure

```
app.py                              Streamlit app (both chat modes)
utils/llm.py                        Groq integration, retry, simulated fallback
evaluation/quick_probe.py           Exploratory gender-bias probe (built, run)
evaluation/quick_probe_output.md    Its latest real output
evaluation/evaluate.py              Planned formal evaluation framework (stub)
test_api.py                         Quick connectivity check
.env.example                        Template for your own API key
```

## Additional files

No accompanying ZIP — everything needed is in this repository.
