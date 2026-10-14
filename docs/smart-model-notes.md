# Smart layer (`--smart`) — model results & cost

The optional smart layer asks an **OpenAI-compatible LLM** to:

1. flatten merged / multi-level table headers into **one clear header row**
   (e.g. `工业分析` + `Mad` → `工业分析_Mad`), and
2. report suspicious cells in the package notes (OCR slips, inconsistent
   values, glued rows).

Clean tables cost **zero** API calls — only tables whose header row has gaps
(the fingerprint of merged / multi-level headers) trigger a call. Any failure
falls back to the raw MinerU grid.

This page records **measured results** so you can pick a model with
confidence. The table grows as more models get measured (free tiers included).

## How it is measured

- Corpus: real Chinese geology papers (MinerU raw cache), tables with merged /
  multi-level headers (the classic hard case)
- Command: `python -m pdf_excel --smart <name filter>` on a cached paper
  (no MinerU re-run)
- Pass criteria: header row flattened correctly, notes written, package intact

## Results

| Model | Endpoint | Outcome | Cost per paper (~8 tables) |
|---|---|---|---|
| `deepseek-chat` | `https://api.deepseek.com` | 6/6 eligible tables fixed. Also caught an OCR error (`0` → `O`, oxygen) and a value anomaly (`3859(6)` vs range `37.00~42.39`) | ≈ 1–2 万 tokens ≈ **RMB 0.0x** (order of magnitude) |

## Notes & caveats

- The model must return strict JSON; malformed or out-of-range output is
  ignored and the raw grid is kept (warnings are shown, never silently
  swallowed).
- Smart notes appear in the package notes (`## AI smart-layer notes (--smart)`)
  and **never turn a successful package into `问题说明.md` / `issues.md`**.
- Cost figures are order-of-magnitude from vendor list prices — check current
  pricing of your provider before relying on numbers.
