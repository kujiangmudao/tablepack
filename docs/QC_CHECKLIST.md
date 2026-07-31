# Visual QC checklist

Use after every automatic package. Print or copy into batch notes if needed.

## Per PDF

- [ ] Package exists: `output/<stem>/`
- [ ] Excel name matches PDF stem
- [ ] `原始表格/` present and non-empty when tables exist
- [ ] `图片/` has non-table figures (when PDF has any)
- [ ] Exactly one of `转换说明.md` / `问题说明.md` (or both if you prefer — pipeline writes one primary note)

## Per sheet / table

- [ ] Sheet title corresponds to the correct caption (no table-2+3 glue)
- [ ] Page number metadata matches source page
- [ ] Column count matches original (watch multi-level headers)
- [ ] Row count matches (watch multi-page splits)
- [ ] Header cells correct after OCR cleanup (`Al2O3`, `w/%`, …)
- [ ] Sample / well / coal-seam IDs: subscripts and `#` intact
- [ ] Numeric cells match print (spot-check full rows, not just first)
- [ ] Merged cells: top-left holds value; no accidental duplication
- [ ] No invented filler rows for empty MinerU nodes

## When something is wrong

1. Prefer **rewrite that sheet** from the table screenshot (openpyxl / manual Excel).
2. Landscape disaster → rotate crop → OCR → rebuild grid carefully.
3. Print itself inconsistent → keep printed values + note the conflict.
4. Cannot recover → leave sheet out or mark clearly + `问题说明.md`.

## Sign-off template

```markdown
## QC sign-off — <stem>
- Date:
- Reviewer:
- Tables checked: N / N
- Fixed sheets:
- Residual risks:
```
