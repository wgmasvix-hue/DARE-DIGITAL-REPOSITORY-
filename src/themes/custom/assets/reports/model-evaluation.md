# Shona NER baseline evaluation

Generated: 2026-10-14T04:24:39Z  |  by `darelang.ner.run`

Dataset: MasakhaNER-X chiShona (sn/sna). Baseline only — no transformer model was trained or evaluated.

## Data
- train=1441 validation=887 test=1000 records
- Labels: PER, ORG, LOC, DATE

## Results (entity-level, exact match)

### null (span)
- **validation**: P=0.0000 R=0.0000 F1=0.0000 | macro-F1=0.0000 | invalid predictions=0
    - PER: P=0.0000 R=0.0000 F1=0.0000
    - ORG: P=0.0000 R=0.0000 F1=0.0000
    - LOC: P=0.0000 R=0.0000 F1=0.0000
    - DATE: P=0.0000 R=0.0000 F1=0.0000
- **test**: P=0.0000 R=0.0000 F1=0.0000 | macro-F1=0.0000 | invalid predictions=0
    - PER: P=0.0000 R=0.0000 F1=0.0000
    - ORG: P=0.0000 R=0.0000 F1=0.0000
    - LOC: P=0.0000 R=0.0000 F1=0.0000
    - DATE: P=0.0000 R=0.0000 F1=0.0000

### gazetteer (span)
- **validation**: P=0.5942 R=0.4277 F1=0.4974 | macro-F1=0.5137 | invalid predictions=0
    - PER: P=0.5464 R=0.2849 F1=0.3745
    - ORG: P=0.6345 R=0.4945 F1=0.5558
    - LOC: P=0.5763 R=0.4501 F1=0.5055
    - DATE: P=0.6084 R=0.6299 F1=0.6190
- **test**: P=0.5947 R=0.4271 F1=0.4972 | macro-F1=0.5118 | invalid predictions=0
    - PER: P=0.5656 R=0.3135 F1=0.4034
    - ORG: P=0.6074 R=0.4662 F1=0.5275
    - LOC: P=0.6090 R=0.4683 F1=0.5295
    - DATE: P=0.5970 R=0.5772 F1=0.5869

### most_frequent_token (token(BIO))
- **validation**: P=0.0000 R=0.0000 F1=0.0000 | macro-F1=0.0000 | invalid predictions=0
    - PER: P=0.0000 R=0.0000 F1=0.0000
    - ORG: P=0.0000 R=0.0000 F1=0.0000
    - LOC: P=0.0000 R=0.0000 F1=0.0000
    - DATE: P=0.0000 R=0.0000 F1=0.0000
- **test**: P=0.0000 R=0.0000 F1=0.0000 | macro-F1=0.0000 | invalid predictions=0
    - PER: P=0.0000 R=0.0000 F1=0.0000
    - ORG: P=0.0000 R=0.0000 F1=0.0000
    - LOC: P=0.0000 R=0.0000 F1=0.0000
    - DATE: P=0.0000 R=0.0000 F1=0.0000

### averaged_perceptron (token(BIO))
- **validation**: P=0.7655 R=0.6439 F1=0.6995 | macro-F1=0.6795 | invalid predictions=0
    - PER: P=0.8111 R=0.7197 F1=0.7626
    - ORG: P=0.7625 R=0.6503 F1=0.7019
    - LOC: P=0.7003 R=0.5360 F1=0.6073
    - DATE: P=0.7277 R=0.5810 F1=0.6462
- **test**: P=0.7453 R=0.6338 F1=0.6850 | macro-F1=0.6690 | invalid predictions=0
    - PER: P=0.8073 R=0.7193 F1=0.7608
    - ORG: P=0.7050 R=0.6159 F1=0.6574
    - LOC: P=0.7156 R=0.5482 F1=0.6208
    - DATE: P=0.7054 R=0.5809 F1=0.6371

## Limitations
- Baselines are not state-of-the-art; they establish lower bounds.
- The averaged perceptron classifies tokens independently (no Viterbi).
- Span matching is exact on (label, surface) per sentence.
- Transformer baselines were not run (packages not installed).
