# Examples

## Expected package layout

See `sample_output_layout/` for a **structure-only** illustration (no real thesis data).

## Synthetic table HTML

Unit tests under `tests/` exercise rowspan/colspan HTML → grid conversion without PDFs.

## Agent skill

Copy or symlink:

```text
skills/pdf-table-to-excel/SKILL.md
```

into your agent’s skills directory, and keep the repo’s `AGENTS.md` in the project root when working here.

## Private batch fix scripts

Local one-off scripts such as `fix_batch3.py` often contain **private reconstructed tables**. They are **gitignored** on purpose. Prefer:

1. Fixing upstream parsing/normalization in the package
2. Adding synthetic tests
3. Documenting the pitfall in `docs/TROUBLESHOOTING.md`
