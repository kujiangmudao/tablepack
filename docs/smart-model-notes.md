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

### Free models (via opencode CLI gateway)

Free-tier models **reject direct HTTP clients** (`FreeTierError`); they only
work from within the opencode runtime. Measured by shelling out to the local
opencode 1.18.30 CLI (`opencode run -m opencode/<model>`), one call per table,
on two real hard-case tables:

- **ZhangKe tab2** — 16×9, two-level headers (`工业分析(%)`+`Mad/Ad/Vdaf`,
  `元素含量(daf)/%`+`C/H/0/N/S`), with the classic `0`→`O` OCR slip
- **XueHaijun tab2** — 8×8, two-level headers (`工业分析`+`Mad/Ad/Vdaf`,
  `各种硫占比`+`Ss,d/Sp,d/So,d`), with a lost-decimal value `3859(6)`

| Model | ZhangKe tab2 | XueHaijun tab2 | Notes |
|---|---|---|---|
| `mimo-v2.6-flash-free` | pass | pass | multi-level merged + `0`→`O` fixed; also flagged `3859(6)`→`38.59(6)` |
| `longcat-2.5-preview-free` | pass | pass | same quality; flagged the lost decimal too |
| `muse-spark-1.3-contributor-free` | pass | pass | same quality; caught both anomalies |
| `space-bunny-free` | pass | pass | merged headers, noted row-pair structure |
| `cat-jam-free` | pass | pass | clean, fewer notes |
| `step-5-preview-free` | pass | pass | merged headers, caught lost decimal + whitespace |
| `big-pickle` | pass (1 retry) | pass | caught `0`→`O`; needed one retry (gateway hiccup) |
| `nemotron-3.5-lightning-free` | partial | partial | merges only some levels, keeps raw `0`; usable but weakest |

**Takeaway:** free models via the CLI gateway match `deepseek-chat` quality on
these cases — the smart layer does **not** require a paid API. Two operational
caveats:

1. Rapid consecutive free calls degrade responses ("no table grid provided");
   space calls ~10s apart and retry once on empty output.
2. Free models are sensitive to prompt shape — keep the JSON grid on the **same
   line** as the instructions (a newline between instructions and the grid
   makes them "lose" the table).

## Notes & caveats

- The model must return strict JSON; malformed or out-of-range output is
  ignored and the raw grid is kept (warnings are shown, never silently
  swallowed).
- Smart notes appear in the package notes (`## AI smart-layer notes (--smart)`)
  and **never turn a successful package into `问题说明.md` / `issues.md`**.
- Cost figures are order-of-magnitude from vendor list prices — check current
  pricing of your provider before relying on numbers.
