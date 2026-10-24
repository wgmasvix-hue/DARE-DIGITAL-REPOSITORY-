# Validation report — MasakhaNER-X chiShona (`sn` / `sna`)

Generated: 2026-10-14  |  Licence: **CC-BY-NC-4.0** (non-commercial)
Source revision: `ba5843cd08aa491d5f96a5e809e71eb9ec461391`

Scope: strictly non-commercial research and educational use. Downloaded from the
pinned GitHub revision only; the Hugging Face loader's moving `main` branch was
**not** used. No audio or unrelated datasets were fetched.

## Files, sizes and checksums

| Split | Path | Bytes | SHA-256 | git blob SHA-1 |
|---|---|---:|---|---|
| train | `data/masakhaner-x/sna/jsonl/train/sn.jsonl` | 584,209 | `3313b18fc397665d2a52f370292ba5c12d98fdf92b0860e45c162b0df42827b0` | `51fcfb954f2f330e7f6955009c157ba01b639439` |
| validation | `data/masakhaner-x/sna/jsonl/validation/sn.jsonl` | 378,655 | `c1e10549860ce753e780cb2589bffcfdb87c058d46ea81f9192651987586f9bd` | `a8052446f96968da1f64be7f42488c1ca5b754c6` |
| test | `data/masakhaner-x/sna/jsonl/test/sn.jsonl` | 410,445 | `c4f7663958d64871bf5bf6717ad88b193483174563005f4535fb59a8971b7c50` | `0ea5a14f4388db11368b48d57387421e4f5a021a` |

All three matched their expected byte size and git blob SHA-1; writes were atomic.

## Validation results

| Split | Records | Entity spans | PER | ORG | LOC | DATE | Dup IDs | Empty | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 1441 | 2950 | 1035 | 1035 | 548 | 332 | 0 | 0 | 0 |
| validation | 887 | 2037 | 727 | 640 | 415 | 255 | 0 | 0 | 0 |
| test | 1000 | 2174 | 763 | 640 | 496 | 275 | 0 | 0 | 0 |

Record counts match the declared HF splits (1441 / 887 / 1000). Original
train/validation/test splits were preserved with no re-splitting or filtering.

Checks performed (all passed): JSONL syntax; UTF-8 decoding; unique `example_id`;
non-empty `text`; label set restricted to PER/ORG/LOC/DATE; byte offsets within
`text` and aligned to UTF-8 character boundaries.

**Warnings:** none. **Errors:** none. **Quarantined files:** none.

## Licence and attribution

- Data licence: **CC BY-NC 4.0** — Attribution-NonCommercial 4.0 International.
- Commercial use: not permitted. Redistribution: allowed for non-commercial
  purposes with attribution.
- Attribution required: Masakhane / Adelani et al. (2022), *MasakhaNER 2.0*,
  EMNLP 2022 — https://aclanthology.org/2022.emnlp-main.298/ (see `ATTRIBUTION.md`).
- Underlying news text retains per-site licences; do not redistribute raw source
  text without review.

## Outputs

- Download manifest: `manifests/masakhaner_x.sna.download.json`
- Machine-readable validation: `reports/validation-masakhaner_x-sna-20261014.json`
- Source descriptor: `sources/masakhaner_x.json`
- Licensing report: `reports/licensing-masakhaner_x-sna.md`
