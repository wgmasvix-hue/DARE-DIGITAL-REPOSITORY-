# Final project report

Generated: 2026-10-14T04:31:30Z  |  by `scripts/make_final_report.py`

**Dataset:** MasakhaNER-X chiShona (sn/sna)

## Phase status
- **1 documentation**: complete
- **2 harvesting engine**: complete
- **3 catalogue and licence gate**: complete
- **4 masakhaner x pipeline**: complete
- **5 normalisation**: complete
- **6 ner baselines**: complete
- **7 zw evaluation framework**: complete (framework only; no corpus)
- **8 providers**: complete (optional providers documented)
- **9 dare export**: complete (metadata proposal only)
- **10 release bundle**: complete (local, metadata-only)
- **11 final report**: complete

## Source and licence
- Repository: masakhane-io/masakhane-ner
- Revision: `ba5843cd08aa491d5f96a5e809e71eb9ec461391`
- Licence: CC-BY-NC-4.0 (RESOLVED_NONCOMMERCIAL)

## Corpus
- **train** `sn.jsonl` — 584209 bytes, `3313b18fc397`, labels=DATE,LOC,ORG,PER
- **validation** `sn.jsonl` — 378655 bytes, `c1e10549860c`, labels=DATE,LOC,ORG,PER
- **test** `sn.jsonl` — 410445 bytes, `c4f7663958d6`, labels=DATE,LOC,ORG,PER

| split | records | spans | errors |
|---|---|---|---|
| train | 1441 | 2950 | 0 |
| validation | 887 | 2037 | 0 |
| test | 1000 | 2174 | 0 |

Readiness: **GO (with environment setup required)**

## Validation and integrity
- Validation status: **PASS**
- Cross-split leakage detected: **False**

## NER baselines (test, entity-level micro)
| baseline | precision | recall | F1 |
|---|---|---|---|
| null | 0.0 | 0.0 | 0.0 |
| gazetteer | 0.5947 | 0.4271 | 0.4972 |
| most_frequent_token | 0.0 | 0.0 | 0.0 |
| averaged_perceptron | 0.7453 | 0.6338 | 0.685 |

## Catalogue
- Datasets: 5
  - DISCOVERED: 2
  - LICENCE_PENDING: 1
  - METADATA_VERIFIED: 1
  - VALIDATED: 1

## Release bundle
- Dataset: masakhaner-x
- Revision: `ba5843cd08aa491d5f96a5e809e71eb9ec461391`
- Mode: metadata-only
- Members: 28

## Governance
- Default distribution: metadata-only
- Commercial use: False
- Attribution required: True
- Personal data: required before any speech/voice data use

## Pending approval gates
- Publishing or uploading data/weights (incl. Hugging Face).
- DARE/DSpace ingest (only a metadata proposal has been produced).
- Installing large ML packages or training a transformer model.
- Any use of personal/identifiable speech data.

## Limitations
- NER figures are simple baselines, not state-of-the-art.
- The averaged perceptron has no Viterbi decoding.
- No Zimbabwe-specific evaluation corpus is shipped.
- Only one Zimbabwean language (chiShona) has been fully validated.

## Reproduce
```
python3 scripts/dare.py discover
python3 scripts/dare.py catalogue
python3 scripts/dare.py validate
python3 scripts/dare.py splits
python3 scripts/dare.py normalise --split train
python3 scripts/dare.py ner
python3 scripts/dare.py dare-export
python3 -m unittest discover -s tests
python3 scripts/make_release.py --dataset masakhaner_x
```
