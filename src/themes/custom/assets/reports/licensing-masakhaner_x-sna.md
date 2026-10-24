# Licensing report — MasakhaNER-X chiShona (`sn` / `sna`)

Generated: 2026-10-14 (metadata and documentation review)
Status: **RESOLVED_NONCOMMERCIAL** — `CC-BY-NC-4.0`
Decision: HF **MasakhaNER-X JSONL** is the primary candidate source of record;
GitHub **MasakhaNER 2.0 / sna CoNLL** is retained as a documented alternative.

## 1. Verified upstream source and revision

| | |
|---|---|
| Candidate repository | https://huggingface.co/datasets/masakhane/masakhaner-x |
| Candidate revision | `8fc2213823e45e5bdf0ddca7680b64fc2faacf4b` (2024-11-21) |
| Candidate contents | card + loader only (`README.md`, `masakhaner-x.py`, `.gitattributes`) — **no data** |
| Data host repository | https://github.com/masakhane-io/masakhane-ner |
| Data host path | `xtreme-up/MasakhaNER-X` |
| Data host revision | `ba5843cd08aa491d5f96a5e809e71eb9ec461391` (2025-10-15, = `main` HEAD) |

The HF loader downloads `{train,validation,test}/sn.jsonl` from the GitHub path
on the **moving `main`** branch. We pin to the commit above.

### Files and expected sizes

| Split | File | Size (bytes) | git blob SHA-1 |
|---|---|---:|---|
| train | `xtreme-up/MasakhaNER-X/train/sn.jsonl` | 584,209 | `51fcfb954f2f330e7f6955009c157ba01b639439` |
| validation | `xtreme-up/MasakhaNER-X/validation/sn.jsonl` | 378,655 | `a8052446f96968da1f64be7f42488c1ca5b754c6` |
| test | `xtreme-up/MasakhaNER-X/test/sn.jsonl` | 410,445 | `0ea5a14f4388db11368b48d57387421e4f5a021a` |
| **total** | | **1,373,309** | |

Declared split counts (HF card, `sn`): train 1441 / validation 887 / test 1000.
Schema: `{example_id, language:"sna", text, spans:[{start_byte,limit_byte,label}], target}`,
labels `PER, ORG, LOC, DATE`, spans are UTF-8 byte offsets.

## 2. Licence evidence and permitted uses

Convergent evidence (all pointing to **CC BY-NC 4.0**, non-commercial):

1. **GitHub LICENSE** (canonical): *"The Masakhane-NER data is under CC-NC
   Attribution-NonCommercial 4.0 International"* — with Apache-2.0 reserved for code.
2. **GitHub root README** ("License information"): *"The license of the NER
   dataset is in CC-BY-4.0-NC (…/by-nc/4.0/)"* — MasakhaNER-X listed under this statement.
3. **GitHub `MasakhaNER2.0/README.md`**: same CC-BY-4.0-NC statement.
4. **HF card body** (`masakhaner-x` *and* `masakhaner2`, "Licensing Information"):
   *"The licensing status of the data is CC 4.0 Non-Commercial"*.
5. **Paper / project docs**: MasakhaNER 2.0 (EMNLP 2022), MasakhaNER 1.0 (TACL 2021),
   and XTREME-UP (Findings EMNLP 2023) describe construction but state the data
   licence on GitHub/HF, not in the paper. XTREME-UP's code repo is Apache-2.0
   (code only) and does **not** override the data licence.

| Use | Permitted? |
|---|---|
| Local non-commercial research | Yes |
| Non-commercial redistribution with attribution | Yes |
| Commercial use | **No** |
| Conditions | Attribution to Masakhane / Adelani et al. (2022); licence notice + link; indicate modifications |

## 3. Recorded conflicts

| Layer | Value | Assessment |
|---|---|---|
| HF `masakhaner-x` frontmatter | `license: unknown` | Metadata anomaly; contradicted by card body prose |
| HF `masakhaner2` frontmatter | `license: afl-3.0` | Metadata anomaly; contradicted by all prose |
| GitHub `LICENSE` | Apache-2.0 (code) + CC BY-NC 4.0 (data) | Scope resolved by the file's own prose |
| GitHub README | `CC-BY-4.0-NC` | Non-standard SPDX name → resolves to CC BY-NC 4.0 |
| Underlying monolingual text | per news site; chiShona source declared CC BY 4.0 | Applies to raw source text, not annotations |

**Important:** HTTP 200 responses and pinned URLs were used only to confirm that
the files exist and are stable. They do **not** constitute permission.

## 4. Recommended next action

1. Confirm (human sign-off) that the intended DARE use is **strictly
   non-commercial** and that attribution conditions are acceptable.
2. Only then download the three pinned JSONL files and run:
   `python3 scripts/inspect_dataset.py --validate data/masakhaner-x/sna/jsonl/*/sn.jsonl`
3. Do not redistribute raw underlying news text before reviewing per-site licences.
4. Consider obtaining written confirmation from the Masakhane rights holders.

The prior dry-run outputs (`manifests/masakhaner_x.sna.json`,
`reports/inspection-masakhaner_x-sna-20261014.md`) are preserved unchanged.
