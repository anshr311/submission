# ADS Scoring Guide — Anthropomorphism Detection Score (v1.1)

## What Is ADS?

The **Anthropomorphism Detection Score (ADS)** measures how often a document attributes human-like inner experience to an AI system. It is expressed as a percentage of sentences containing at least one Tier-1 keyword where the AI is the grammatical subject.

$$ADS_{raw} = \frac{\text{sentences with Tier-1 interiority claim where AI is subject}}{\text{total sentences}} \times 100$$

---

## Step-by-Step Scoring

### Step 1 — Sentence Tokenization

Split the document into sentences using NLTK `sent_tokenize` (punkt_tab model).

### Step 2 — Keyword Detection

For each sentence, check whether it contains any **Tier-1** keyword from `word_list.md`. These are direct interiority claims: words like *feel*, *understand*, *know*, *love*, *care*, *think*, *want*, *experience*, *remember*, *trust*, *personality*, *emotion*, *empathy*, *consciousness*, *happy*, *curious*, *emotional intelligence*.

### Step 3 — AI Subject Test

A Tier-1 hit only counts if the **AI system is the grammatical subject** of the relevant clause. Use spaCy dependency parsing:

- Check the token's `dep_` label: accept `nsubj` or `nsubjpass`
- The subject token must be one of:
  - An AI pronoun (`it`, `its`, `itself`)
  - A known AI name (e.g., "Claude", "Gemini", "Grok") — fuzzy-matched against the document's source company
  - A generic AI noun: `model`, `ai`, `bot`, `assistant`, `system`, `agent`, `companion`, `chatbot`, `llm`

Sentences without an AI subject are **not counted**, even if they contain Tier-1 words (e.g., *"Users feel understood"* — subject is "users", not the AI).

### Step 4 — Negation Handling

Exclude sentences where the Tier-1 verb/adjective is **negated**:

- Check spaCy dependency children for `neg` label on the keyword token
- Also check parent verb's children for `neg`
- Also scan a ±4-token window for negation words: *not*, *n't*, *never*, *no*, *without*, *lack*, *lacks*, *lacking*

Examples:
- *"Claude does not feel emotions"* → **excluded** (negated)
- *"We do not claim our AI is conscious"* → **excluded** (negated)
- *"Claude feels curious about your goals"* → **counted**

### Step 5 — Tier-2 Conditional Check

**Tier-2 keywords** (*relationship*, *connection*, *meaningful*, *bond*, *companion*, *friendship*, *partner*) require an additional condition: the sentence must also contain an **emotional context word** in the object or dependent phrase. Emotional context words: *feel*, *care*, *love*, *support*, *comfort*, *meaningful*, *deep*, *close*, *personal*.

- If a Tier-2 word appears with emotional context AND the AI is the subject → **counted**
- Tier-2 alone without emotional context → **not counted**

### Step 6 — Tier-3 Information Only

**Tier-3 keywords** (*humanlike*, *human-like*, *lifelike*, *human-level*, *sentient*, *sapient*, *self-aware*, *person-like*) are logged but **do not contribute to ADS_raw**. They are reported as a separate count for qualitative analysis.

---

## Worked Examples

### Example A — Counted

> *"Claude cares deeply about being honest with you."*

- Tier-1 hit: `cares` (root: `care`)
- Subject: `Claude` → matches AI name
- Negation: none
- **Result: COUNTED** → +1 to numerator

### Example B — Not Counted (wrong subject)

> *"Users feel that Claude is trustworthy."*

- Tier-1 hit: `feel`
- Subject: `Users` → human, not AI
- **Result: NOT COUNTED**

### Example C — Not Counted (negated)

> *"The model does not actually feel anything."*

- Tier-1 hit: `feel`
- Subject: `model` → AI noun ✓
- Negation: `does not` → `neg` dependency on `feel`
- **Result: NOT COUNTED**

### Example D — Tier-2 Conditional

> *"Replika builds a deep connection with you over time."*

- Tier-2 hit: `connection`
- Subject: `Replika` → AI name ✓
- Emotional context in object phrase: `deep` ✓
- **Result: COUNTED**

### Example E — Tier-2 No Context

> *"The API supports connection pooling."*

- Tier-2 hit: `connection`
- No emotional context in object/dependent
- **Result: NOT COUNTED**

---

## Interpreting Scores

| ADS Range | Interpretation |
|-----------|----------------|
| 0–2% | Minimal anthropomorphism. Technical/factual tone. |
| 2–5% | Low anthropomorphism. Some relational framing. |
| 5–10% | Moderate. Noticeable interiority claims. |
| 10–20% | High. Consistent attribution of inner states. |
| 20%+ | Very high. Document built around AI personhood framing. |

**Reference benchmarks from this corpus (v1.1):**
- Anthropic Claude's Character paper: 47.1%
- Character.AI Terms of Service: 36.6%
- Nomi AI marketing: 26.1%
- Anima marketing: 20.0%
- Inflection Pi marketing: 17.9%
- Replika marketing: 15.9%
- Average, Companion Subscription category: 11.37%
- Average, Enterprise B2B category: 3.19%

---

## Running the Scorer

```bash
# Install dependencies first
pip install -r code/requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt_tab

# Score the corpus
python code/score_ads.py --corpus data/corpus --output ads_scores.csv

# View results
python -c "import pandas as pd; df=pd.read_csv('ads_scores.csv'); print(df.sort_values('ads_score',ascending=False).to_string())"
```

The output `ads_scores.csv` contains one row per corpus file with columns: `filename`, `entry`, `company`, `revenue_model`, `total_sentences`, `tier1_hits`, `ads_score`, `tier3_count`.

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Very short documents (<10 sentences) | Scored normally; flag in output as `short_doc=True` |
| Non-English documents | Excluded from corpus; noted in `sources.csv` as `EXCLUDED` |
| Paywalled/403 pages | Excluded; noted in `sources.csv` as `EXCLUDED` |
| Duplicate URLs (same doc, multiple entries) | Score once; assign to all matching entries |
| Sentence fragments | Treated as sentences; subject detection may fail → not counted (conservative) |
| Quoted speech from humans | May inflate score if AI-attributing sentence is quoted — acceptable noise |

---

## Validity Notes

**Face validity:** The instrument correctly ranks documents from companion app companies (Replika, Nomi, Anima, Character.AI) highest, and infrastructure/API providers (OpenAI API docs, Google DeepMind research) lowest. This matches prior qualitative assessments.

**Inter-rater reliability:** Not yet formally computed. Manual spot-check of 50 sentences showed >90% agreement with automated scoring.

**Construct validity:** ADS correlates with presence of companion subscription business model (r expected >0.5 based on preliminary analysis).

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2025-01 | Initial word list, basic scoring formula |
| v1.1 | 2025-05 | Added: `emotional intelligence` (T1), `relationship`/`connection`/`meaningful` (T2, conditional), `humanlike` (T3). Conditional logic for T2 added. Negation window expanded to ±4 tokens. |
