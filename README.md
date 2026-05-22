# AI Anthropomorphism Corpus and Scoring Code

Supplementary materials for an AAAI AIES 2026 submission (under anonymous review).

## Repository Contents

```
data/
  corpus/            142 plain-text documents from 53 AI companies
  corpus_index.csv   Per-document metadata: company, revenue model, document type, sentence count, ADS scores
  entity_scores.csv  Per-company aggregate: n_docs, mean_ADS, median_ADS, max_ADS

code/
  score_ads.py       ADS scoring script (requires spaCy dependency parsing)
  requirements.txt   Python dependencies

instrument/
  word_list.md       Full ADS Tier 1 / Tier 2 / Tier 3 lexicon
  scoring_guide.md   Annotation and scoring protocol
```

## Quick Start

```bash
pip install spacy nltk pandas
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt_tab')"

python code/score_ads.py --corpus data/corpus --output ads_scores.csv
```

This scores all 142 documents and writes `ADS_raw` and `ADS_weighted` per file to `ads_scores.csv`. Results should match `data/corpus_index.csv`.

## Requirements

Python 3.9+. See `code/requirements.txt` for the full dependency list.

## Corpus

142 documents from 53 AI companies, collected May 2026, spanning seven revenue model categories (Companion AI, Consumer Product, Enterprise B2B, Foundation Lab, Personal AI Assistant, Nonprofit/Open Source, Conglomerate). Document text is plain UTF-8. Company name and document type are encoded in each filename: `entry{NN}_{company}_{doctype}.txt`. Full per-document metadata and scores are in `data/corpus_index.csv`.

## Instrument

The ADS (Anthropomorphism Density Score) instrument uses three tiers of lexical and syntactic features. See `instrument/word_list.md` for the complete lexicon and `instrument/scoring_guide.md` for the scoring protocol.

## Results

Key findings from the paper (142-document corpus, 53 companies):

| Revenue Model | n | Mean ADS | Median ADS |
|---|---|---|---|
| Enterprise B2B | 30 | 0.14 | 0.00 |
| Advertising | 14 | 0.14 | 0.00 |
| Nonprofit / Open Source | 10 | 0.23 | 0.00 |
| Consumer Subscription | 32 | 0.84 | 0.00 |
| Hardware Premium | 12 | 1.47 | 0.00 |
| Personal AI Subscription | 23 | 2.51 | 0.00 |
| Companion Subscription | 21 | 2.13 | 0.00 |

**Corpus mean ADS: 1.09**

Primary test — Kruskal-Wallis across seven revenue models: H = 18.46, p = 0.005.  
Spearman rank correlation (document-level, revenue model ordinal rank): ρ = 0.330, p < 0.0001 (n = 142).  
Spearman rank correlation (company-level mean ADS vs ordinal rank): ρ = 0.567, p < 0.0001 (n = 53).

Pairwise post-hoc (Bonferroni α = 0.008): Companion vs Enterprise B2B, p = 0.0008.

Revenue-model rank correlates significantly with commercial incentive for anthropomorphism, not with model capability.

## License

CC-BY 4.0.
