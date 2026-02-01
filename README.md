# Genetic Health Analysis Pipeline

A comprehensive genetic health analysis pipeline that processes 23andMe raw data to generate detailed health reports using Claude Code.

## Attribution

This project is derived from work by **Nick Saraev**, originally demonstrated in:

**"I gave an AI my DNA and let it analyze my entire genome"**
YouTube: https://youtu.be/O1ICQworLVc

The original concept uses Claude Code to analyze 23andMe genetic data against ClinVar and PharmGKB databases to generate personalized health reports.

---

## Quick Start

### Prerequisites

1. **Get your 23andMe raw data:**
   - Log into 23andMe → Settings → Download Raw Data
   - Save as `data/genome.txt`

2. **Download ClinVar database** (~289MB, required for disease analysis):
   ```bash
   pip install gdown
   gdown 1ER1lNS9jcWV0oaUo0_DOa23QRHaUKclt -O data/clinvar_alleles.tsv
   ```

### Running with UV (Recommended)

```bash
# Basic run (pure Python, no extra dependencies)
uv run python scripts/run_full_analysis.py

# With fast mode (5-10x speedup using polars)
uv sync --extra fast
uv run python scripts/run_full_analysis.py

# With custom genome file and subject name
uv run python scripts/run_full_analysis.py data/genome.txt --name "Your Name"
```

### Running with Traditional Python

```bash
# Ensure Python 3.10+
python scripts/run_full_analysis.py

# Optional: Install polars for faster processing
pip install polars
python scripts/run_full_analysis.py --name "Your Name"
```

---

## Output Reports

The pipeline generates three reports in `reports/`:

| Report | Description |
|--------|-------------|
| `EXHAUSTIVE_GENETIC_REPORT.md` | Drug metabolism, methylation, nutrition, fitness, cardiovascular, sleep genetics |
| `EXHAUSTIVE_DISEASE_RISK_REPORT.md` | Pathogenic variants, carrier status, risk factors from ClinVar |
| `ACTIONABLE_HEALTH_PROTOCOL_V3.md` | Personalized supplements, diet, exercise, monitoring recommendations |

---

## Project Structure

```
analyze-dna/
├── README.md                  # This file
├── CLAUDE.md                  # Instructions for Claude Code
├── pyproject.toml             # UV/pip package configuration
├── data/
│   ├── genome.txt             # Your 23andMe raw data (add this)
│   ├── clinvar_alleles.tsv    # ClinVar database (download separately)
│   └── clinical_*.tsv         # PharmGKB data (included)
├── scripts/
│   ├── run_full_analysis.py   # Main entry point
│   ├── fast_loader.py         # Optimized loading (polars)
│   └── *.py                   # Analysis modules
└── reports/                   # Generated reports
```

---

## Performance

| Mode | ClinVar Processing | Install |
|------|-------------------|---------|
| Standard | ~15-25 seconds | No extra deps |
| Fast (polars) | ~2-4 seconds | `uv sync --extra fast` |

---

## Running for Multiple People

```bash
cp ~/Downloads/genome_mom.txt data/genome_mom.txt
uv run python scripts/run_full_analysis.py data/genome_mom.txt --name "Mom"

# Rename outputs to preserve
mv reports/EXHAUSTIVE_GENETIC_REPORT.md reports/EXHAUSTIVE_GENETIC_REPORT_MOM.md
```

---

## Data Sources

| File | Size | Included | Source |
|------|------|----------|--------|
| genome.txt | ~25MB | No | Your 23andMe download |
| clinvar_alleles.tsv | ~289MB | No | [Download command above](#prerequisites) |
| clinical_annotations.tsv | ~850KB | Yes | PharmGKB |
| clinical_ann_alleles.tsv | ~5.5MB | Yes | PharmGKB |

### Updating Data (Quarterly Recommended)

- **ClinVar**: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
- **PharmGKB**: https://www.pharmgkb.org/downloads (free account)

---

## Limitations

1. **Not a clinical diagnosis** - For informational purposes only
2. **Population differences** - Associations may vary by ancestry
3. **Incomplete penetrance** - Not everyone with variant develops condition
4. **Evolving science** - Classifications change as research progresses
5. **Indels not analyzed** - Only single nucleotide variants from 23andMe

---

## License

This analysis pipeline is for personal/educational use. Not for clinical or diagnostic purposes.

**Original concept by Nick Saraev** - https://youtu.be/O1ICQworLVc
