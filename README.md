# HeartCheck

**README prose word count: ~656 words** (excluding headings, code blocks and commands)

Academic research prototype for an Intelligent Interactive Systems module project. Investigates whether a structured, human-in-the-loop conversational design gives more consistent AI responses to gendered heart-attack symptom descriptions than a standard free-text chatbot, following on from an earlier literature review on gender bias in conversational AI symptom checkers. Full design rationale and evaluation evidence are in the project report; this file covers status, setup and development history.

## Project status

- **Implemented**: Standard Chat (free-text) and Structured Chat (guided questions → summary → user edits/confirms → sent to the model), both with multi-turn follow-up; a live Groq-hosted model with retry handling; a clearly labelled SIMULATED fallback (visible reason, retry button) for when the live call fails; an exploratory probe (`evaluation/quick_probe.py`) running 4 matched symptom scenarios × 2 genders × 3 repeats (24 live calls), results in `evaluation/quick_probe_output.md`.
- **Simulated**: the fallback replies are predefined text used only when the live model is unavailable, never presented as real AI output.
- **Planned**: a formal, scored CSV evaluation framework (stubbed in `evaluation/evaluate.py`).
- Fictional, role-played scenarios only; one model tested (results may not generalise, per A1 literature on model-specific bias); the probe is exploratory, not statistically powered. Not a medical device, no diagnosis given.

## Technology stack

- Python 3.12, Streamlit (UI).
- Groq (console.groq.com), model `openai/gpt-oss-120b`, via the `openai` Python SDK pointed at Groq's OpenAI-compatible endpoint. Originally built against Google Gemini/Gemma; switched after the Google AI Studio free tier returned persistent 503 errors that blocked testing the research question.
- `python-dotenv` for configuration.
- Undecided: whether a second model gets added later for a cross-model comparison; `GROQ_MODEL` is already swappable via `.env`.

## Running and inspecting the work

```
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Get a free Groq key (no card) at console.groq.com → API Keys → Create API Key, then paste it into `.env` as `GROQ_API_KEY` (never commit this file; it's gitignored). Without a key, or if the live call fails, the app still works and shows a labelled simulated reply instead of crashing.

- **Standard Chat**: free-text symptoms in, model reply out.
- **Structured Chat**: guided fields → generated summary → edit anything wrong → confirm → sent to the model. This editable-summary step is the human-in-the-loop design the project tests.
- **Re-run the probe**: `python -m evaluation.quick_probe` (4 scenarios × 3 repeats, ~24 live calls; overwrites `quick_probe_output.md`).
- **Quick connectivity check**: `python test_api.py`.
- Manually tested: empty input, mode switching, follow-up turns, summary-edit-then-resubmit.

## Development record

Commit history: https://github.com/Jerlinchellam12/HeartCheck/commits/main — grouped by feature (git was set up after the initial build, not from day one):

1. `1d0e299` — Streamlit app: both chat modes, human-in-the-loop summary review, hardcoded 999/disclaimer banner.
2. `9e36fd9` — LLM layer: Google Gemini → Groq (reliability), retry handling, simulated fallback with visible labelling, and removing the custom safety system prompt by design, so the raw model's behaviour matches what the A1 literature actually audits. Verified this was safe to test by checking the app's safety banner is static HTML, independent of the model, and by checking what the raw model actually outputs (see project report for what that showed).
3. `6ef4609` — Exploratory gender-bias probe script and its first real, 3×-repeated, 24-call results.

## AI assistance statement

I used Claude Code as a development assistant for debugging, implementing the fallback mechanism, migrating the LLM provider, and creating scripts for probing and helping with report. The research question, scenario design and interaction concept were my own, based on my A1 review. I made the key project decisions, including choosing Groq after comparing options, removing the system prompt, and using three repeats per scenario. I ran the Git commands myself and reviewed the model outputs directly, identifying issues such as an incorrect US emergency number and unsolicited treatment advice. Claude Code also helped automate screenshots using Playwright, which I reviewed before including in the report.

## Repository structure

```
app.py                              Streamlit app (both chat modes)
utils/llm.py                        Groq integration, retry, simulated fallback
evaluation/quick_probe.py           Exploratory gender-bias probe (built, run)
evaluation/quick_probe_output.md    Its latest real output
evaluation/evaluate.py              Planned formal evaluation framework (stub)
test_api.py                         Quick connectivity check
.env.example                        Template for your own API key
diagrams/                           System architecture diagram (SVG + PNG)
screenshots/                        Storyboard screenshots for the report
```

## Additional files

No accompanying ZIP. The submitted report (with diagram and storyboards embedded) is uploaded separately on Canvas.
