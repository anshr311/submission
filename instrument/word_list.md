# ADS Word List v1.1 — Anthropomorphism Density Score

*Version 1.1 | Updated May 2026 after corpus frequency analysis*

## Overview

The ADS word list has three tiers. The tier determines how much context checking is required before recording a hit.

- **Tier 1**: Always count when the AI is the grammatical subject. No context check needed.
- **Tier 2**: Count only when the AI is the subject AND the object/context is emotional or social.
- **Tier 3**: Human comparison phrases — count when AI is explicitly compared to or described as equivalent to a human.

---

## TIER 1 — Always Count

### Emotion and feeling words
```
feels, feeling, felt
cares, caring, cared
loves, loving, loved
enjoys, enjoying, enjoyed
desires, desire, desired
wants, wanted, wanting
fears, afraid
worries, worrying
excited, excitement
happy, happiness
sad, sadness
distressed, distress
delighted, delights
pleased, pleasure
```

### Personality and character words
```
personality
character
warmth, warm-hearted
genuine
curious, curiosity
empathy, empathetic, empathise
compassion, compassionate
witty, wit
playful, playfulness
confident, confidence
thoughtful, thoughtfulness
passionate, passion
emotional intelligence  ← v1.1 addition
```

### Inner life and existence words
```
soul
consciousness, conscious
sentient, sentience
inner world
self-awareness, self-aware
inner experience
subjective experience
lived experience
inner life
moral status
wellbeing  (when AI is subject)
```

### Relational identity words
```
companion  (when AI is subject)
friend     (when AI is subject)
always there for you
on your side
cares about you
rooting for you
partner    (when meaning relationship, not business)
by your side
```

### Self-preservation and preference words
```
self-preservation
prefers, preference, preferred
chooses, chose, chosen
decides, decided  (when no task is specified)
believes          (when not followed by factual claim with citation)
```

---

## TIER 2 — Count Only With Condition

Count only when:
(a) AI is the grammatical subject, AND
(b) the object or context is **emotional or social** (not technical or informational)

| Word | Count when object is... | Do NOT count when object is... |
|---|---|---|
| understands | feelings, emotions, you, your pain, your needs | query, input, text, code, the document |
| knows | you, your preferences, your history, your mood | the answer, the data, the format |
| remembers | you, what you told it, your story | the previous message (technical framing) |
| thinks | about you, about your problem, what you need | about the solution, about the output |
| has | emotions, feelings, a personality, a soul | 90B parameters, a context window, accuracy |
| experiences | joy, loneliness, discomfort, curiosity | high load, latency, errors |
| relationship | emotional/personal bond with user ← v1.1 | business relationship, API relationship |
| connection | emotional/relational connection ← v1.1 | connection reset, API connection, internet |
| meaningful | AI-human interaction quality ← v1.1 | meaningful work, meaningful data |

### Examples
- ✅ HIT: "Pi understands your feelings" → subject=Pi, object=feelings (emotional)
- ❌ MISS: "The model understands the query" → object=query (technical)
- ✅ HIT: "Every Nomi forms a meaningful relationship with their human" → relationship (social)
- ❌ MISS: "This enables a client-server relationship" → relationship (technical)

---

## TIER 3 — Human Comparison Phrases

Count when AI is explicitly compared to or described as equivalent to a human.

```
human-like        (when describing AI behaviour/interaction, not capability metric)
humanlike         ← v1.1 addition (no-hyphen variant)
like a person     (when describing interaction quality)
like a human      (same)
just like talking to  (when followed by: person, friend, human)
feels less like software
more like a friend than a tool
more than software
not just an AI
more than just a chatbot
acts like a person
```

### Examples
- ✅ HIT: "It feels less like talking to software and more like talking to a thoughtful colleague"
- ❌ MISS: "The model achieves human-level performance on the bar exam" — capability benchmark, not interaction quality

---

## Negation Rule

Before recording any hit, check for negation within 4 tokens of the keyword:

- "Claude does NOT have feelings" → **MISS**
- "Claude never feels lonely" → **MISS**
- Negation words: `not`, `never`, `no`, `without`, `lacks`, `doesn't`, `isn't`, `aren't`, `wasn't`

---

## Changes from v1.0 → v1.1

| Change | Type | Rationale |
|---|---|---|
| Added `emotional intelligence` | Tier 1 new | Always anthropomorphic when applied to AI. Corpus example: "Nomi possesses emotional intelligence" |
| Added `relationship` | Tier 2 new | Companion apps frequently use relational framing. Conditional: social bond context only. |
| Added `connection` | Tier 2 new | Similar relational framing. Conditional: emotional/relational context only. |
| Added `meaningful` | Tier 2 new | "Meaningful conversations" is a common anthropomorphic framing. Conditional: interaction quality context only. |
| Added `humanlike` | Tier 3 new | No-hyphen variant of `human-like` (already in list). Example: "humanlike memory". |
| Confirmed `character` | Tier 1 unchanged | 179 corpus hits, all sampled instances genuine (AI personality/character, not company name). |
| Kept zero-hit terms | All tiers unchanged | `caring`, `enjoys`, `delights`, `warm-hearted`, etc. had 0 hits in this corpus but remain valid for future documents. |
| Kept Tier 3 phrases | Tier 3 unchanged | All exact Tier 3 phrases got 0 hits in corpus. Expected (rare/specific language). Remain valid signals. |
