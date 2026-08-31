# Evaluation

## Purpose

The evaluation system makes the RAG behavior measurable instead of anecdotal. It is small by design, but it demonstrates the habits expected in applied LLM systems: retrieval checks, answer checks, refusal checks, reports, and regression tests.

## Dataset

Dataset path:

```text
data/eval_sets/synthetic_compliance_eval.json
```

Each case includes:

- `id`
- `query`
- `expected_sources`
- `should_refuse`
- `notes`

The data is synthetic and safe for a public repository.

## Metrics

Retrieval:

- `retrieval_hit_rate`: whether at least one expected source appears in top-k retrieved chunks.
- `mean_source_match_accuracy`: fraction of expected sources retrieved for each case.

Answer quality:

- `citation_presence_rate`: non-refusal answers should include citation markers like `[policy.md#chunk-0]`.
- `mean_groundedness_score`: heuristic overlap between answer content terms and retrieved context terms.
- `refusal_accuracy`: expected refusal behavior compared with observed refusal behavior.
- `answer_length_sanity_rate`: detects responses that are too short or excessively long.

## Running Evaluation

```bash
python scripts/run_eval.py
```

The report is written to:

```text
reports/eval/evaluation_report.json
```

The API can also run evaluation:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"top_k":4}'
```

## Known Limits

The groundedness check is heuristic. It is useful for regression signals, not a complete factuality evaluator.

Future work can add:

- larger eval sets;
- adversarial cases;
- model-graded evaluation;
- citation span verification;
- provider-specific latency and cost metrics.
