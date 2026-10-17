# Evaluation: real-corpus run (45 papers, 188 tables)

This page records a corpus-level evaluation of TablePack on **real Chinese
journal papers** (geology / coal-quality domain), using MinerU raw caches —
no re-parsing, no synthetic data.

## What was measured

For every table in the cached corpus, TablePack rebuilds the grid and applies
the header-gap fingerprint (`should_enhance`), then records:

- number of papers and tables,
- tables whose header structure needs repair (multi-level / merged headers),
- table size distribution,
- smart-layer behavior on representative hard cases across models.

The trigger test is deterministic and runs before any LLM call, so these
numbers do **not** depend on model availability.

## Results

| Metric | Value |
|---|---|
| Papers | 45 |
| Tables extracted | 188 |
| Tables needing header repair (fingerprint hit) | **92 (48.9%)** |
| Average table size | 14.7 rows × 8.8 columns |
| Largest table | 148 rows × 25 columns |
| Automated tests | 44, all passing |

Clean tables cost **zero** LLM calls: only the 48.9% with structural gaps are
sent to the smart layer.

## Smart-layer model comparison

Two hard-case tables (multi-level headers + OCR slips) were used as a frozen
benchmark, run through **8 free models** plus `deepseek-chat` as a paid
baseline (via the opencode CLI gateway for free models):

| Model | Result |
|---|---|
| `deepseek-chat` (paid baseline) | 2/2 tables repaired correctly |
| mimo-v2.6-flash-free, longcat-2.5-preview-free, muse-spark-1.3-contributor-free, space-bunny-free, cat-jam-free, step-5-preview-free, big-pickle | 2/2 tables repaired correctly |
| nemotron-3.5-lightning-free | usable, but weakest of the set |

Quality cases caught by the smart layer in real tables (verified by hand):

- `0` → `O` (oxygen symbol misread by OCR),
- `3859(6)` → `38.59(6)` (lost decimal point; the value is out of range for
  that column).

## Reproduce

```bash
# cached MinerU output in work/ is reused automatically
python -m pdf_excel --smart <paper name filter>
```

The smart layer needs an OpenAI-compatible endpoint (`llm_base_url` +
`llm_model`, key in `PDF_EXCEL_LLM_API_KEY`). With the opencode CLI gateway,
free models can be used at zero API cost — see
[smart-model-notes.md](smart-model-notes.md) for the measured setup.

## Limitations (read before quoting these numbers)

- **48.9% is the trigger rate of the header-gap fingerprint, not a repair
  success rate.** Per-table repairs are validated deterministically (column
  count, no out-of-range names, fallback to the raw grid) and were verified on
  the frozen two-table benchmark and manual spot checks.
- The pipeline **never fabricates data**: when validation fails, the original
  grid is kept and a warning is written to the notes.
- The corpus is domain-specific (Chinese geology journals). Trigger rates may
  differ in other domains and layouts.
