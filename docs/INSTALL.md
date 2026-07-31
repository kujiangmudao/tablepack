# Install guide — two paths

**Product & repo: [TablePack](https://github.com/kujiangmudao/tablepack)** · CLI: `python -m pdf_excel`

## Promise: no MinerU tutorial required

TablePack **wraps MinerU**. After MinerU is present on the machine:

- Put PDFs in `pdf/`
- Run `python -m pdf_excel`
- Collect packages under `output/`

You do **not** need to learn MinerU CLI usage, flags, or intermediate JSON.  
(Path B even installs MinerU for you into an isolated venv.)

Choose your path:

| You already have MinerU CLI | You do **not** have MinerU yet |
|-----------------------------|--------------------------------|
| [Path A](#path-a-already-have-mineru) | [Path B](#path-b-one-command-mineru--tablepack) |

---

## Path A — Already have MinerU

You only need this repo + the agent skill. **Knowing how to use MinerU by hand is optional.**

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
pip install -r requirements.txt
cp config.example.yaml config.yaml
# set mineru_bin to your mineru executable if it is not on PATH
```

**Use with agent (OpenCode / Cursor / …)**

1. Open this repo as the workspace.
2. Load skill: `skills/pdf-table-to-excel/SKILL.md`  
   Raw: https://raw.githubusercontent.com/kujiangmudao/tablepack/main/skills/pdf-table-to-excel/SKILL.md
3. Say: `转表格` / `再转一批` / `/pdf-table-to-excel`

**CLI**

```bash
cp examples/demo/demo_sample.pdf pdf/   # optional demo
python -m pdf_excel
python -m pdf_excel --dry-config
```

If `mineru` is on `PATH`, discovery is automatic. Otherwise:

```yaml
# config.yaml
mineru_bin: C:/path/to/mineru.exe   # or /usr/local/bin/mineru
```

---

## Path B — One-command MinerU + TablePack (safe / isolated)

Scripts create a **dedicated virtualenv** `.venv-mineru` (does not overwrite your system site-packages), install the **official** `mineru[all]` package, install this project’s deps, and write `config.yaml`.

After setup you still **only run TablePack** — no separate MinerU workflow to memorize.

### Windows (PowerShell)

```powershell
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
powershell -ExecutionPolicy Bypass -File scripts\install_mineru.ps1
.\.venv-mineru\Scripts\Activate.ps1
python -m pdf_excel --dry-config
```

### Linux / macOS

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
chmod +x scripts/install_mineru.sh
./scripts/install_mineru.sh
source .venv-mineru/bin/activate
python -m pdf_excel --dry-config
```

### After install

```bash
mkdir -p pdf
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample
```

Put your own PDFs in `pdf/` and run `python -m pdf_excel`.

### What “safe” means here

- Isolated venv under the project (`.venv-mineru/`)
- Official PyPI / uv install of `mineru[all]` (see [MinerU](https://github.com/opendatalab/MinerU))
- No need to run installers as Administrator (unless your Python requires it)
- `config.yaml` is gitignored — machine paths stay local

First successful MinerU parse may download models (official MinerU behavior). Use a normal network connection.

### Agent skill after Path B

Same as Path A: open this repo, load `skills/pdf-table-to-excel/SKILL.md`, ensure the shell uses `.venv-mineru` when running commands.

---

## Verify

```bash
python -m pdf_excel --dry-config
# mineru_bin should point to a real executable
mineru --help
# or:  .venv-mineru\Scripts\mineru.exe --help
```

## Optional: GPU / advanced backends

TablePack defaults to MinerU `pipeline` backend (broad compatibility).  
If your machine has a GPU and a MinerU install that supports `vlm` / `hybrid`, set in `config.yaml`:

```yaml
backend: vlm   # only if your MinerU install supports it
```

See upstream docs: https://opendatalab.github.io/MinerU/quick_start/

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| `MinerU CLI not found` | Re-run install script; check `config.yaml` → `mineru_bin` |
| `mineru` missing on Windows | Use full path to `.venv-mineru\Scripts\mineru.exe` |
| Demo PDF works, real PDF fails | Check `output/<name>/问题说明.md` — empty tables are documented, not invented |
| Want only package layout | Open `examples/demo_output/demo_sample/` (no MinerU required) |

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
