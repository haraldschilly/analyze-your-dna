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
   # Using gdown (recommended)
   pip install gdown
   gdown 1ER1lNS9jcWV0oaUo0_DOa23QRHaUKclt -O data/clinvar_alleles.tsv

   # Or using uv
   uv run pip install gdown
   uv run gdown 1ER1lNS9jcWV0oaUo0_DOa23QRHaUKclt -O data/clinvar_alleles.tsv
   ```

### Running with UV (Recommended)

```bash
# Basic run (pure Python, no extra dependencies)
uv run python scripts/run_full_analysis.py

# With fast mode (5-10x speedup using polars)
uv sync --extra fast
uv run python scripts/run_full_analysis.py

# With custom genome file
uv run python scripts/run_full_analysis.py /path/to/genome.txt

# With subject name in reports
uv run python scripts/run_full_analysis.py --name "Your Name"

# Full example
uv sync --extra fast
uv run python scripts/run_full_analysis.py data/genome.txt --name "John Doe"
```

### Running with Traditional Python

```bash
# Ensure Python 3.10+
python scripts/run_full_analysis.py

# With custom genome file
python scripts/run_full_analysis.py /path/to/genome.txt

# With subject name
python scripts/run_full_analysis.py --name "John Doe"

# Optional: Install polars for faster processing
pip install polars
python scripts/run_full_analysis.py
```

---

## Output Reports

The pipeline generates three reports in the `reports/` directory:

### 1. EXHAUSTIVE_GENETIC_REPORT.md
Lifestyle and health genetics analysis:
- Drug metabolism (CYP enzymes, warfarin sensitivity)
- Methylation (MTHFR, COMT, MTRR)
- Nutrition (vitamin D, omega-3, lactose)
- Fitness (muscle fiber type, exercise response)
- Cardiovascular (blood pressure genes, clotting)
- Sleep/circadian rhythm
- PharmGKB drug-gene interactions

### 2. EXHAUSTIVE_DISEASE_RISK_REPORT.md
Clinical variant analysis from ClinVar:
- Pathogenic variants (affected status)
- Carrier status for recessive conditions
- Risk factors
- Drug response variants
- Protective variants

### 3. ACTIONABLE_HEALTH_PROTOCOL_V3.md
Comprehensive personalized protocol:
- Critical disease findings summary
- Supplement recommendations
- Dietary framework
- Exercise protocol
- Blood pressure management
- Drug-gene interactions
- Testing & monitoring schedule

---

## Project Structure

```
analyze-dna/
├── CLAUDE.md                  # This file
├── pyproject.toml             # UV/pip package configuration
├── .python-version            # Python version (3.12)
├── uv.lock                    # Locked dependencies
├── data/
│   ├── genome.txt             # Your 23andMe raw data (add this)
│   ├── clinvar_alleles.tsv    # ClinVar database (download separately)
│   ├── clinical_annotations.tsv   # PharmGKB annotations (included)
│   ├── clinical_ann_alleles.tsv   # PharmGKB allele data (included)
│   └── clinical_ann_*.tsv     # Additional PharmGKB data (included)
├── scripts/
│   ├── __init__.py            # Package init
│   ├── run_full_analysis.py   # MAIN ENTRY POINT
│   ├── fast_loader.py         # Optimized data loading (polars)
│   ├── comprehensive_snp_database.py  # ~200 curated SNPs
│   ├── generate_exhaustive_report.py  # Report generator
│   ├── disease_risk_analyzer.py       # ClinVar analysis
│   ├── full_health_analysis.py        # Lifestyle analysis
│   └── analyze_genome.py              # Utilities
└── reports/                   # Generated reports (output)
```

---

## Performance

The pipeline supports two modes:

| Mode | ClinVar Processing | Install |
|------|-------------------|---------|
| Standard | ~15-25 seconds | No extra deps |
| Fast (polars) | ~2-4 seconds | `uv sync --extra fast` |

The fast loader uses [polars](https://pola.rs/) for native Rust-based TSV parsing and pre-filters ClinVar to only genome positions before iteration.

---

## Data Requirements

### Genome File Format
The pipeline expects 23andMe raw data format (tab-separated):
```
# rsid  chromosome  position  genotype
rs123   1           12345     AG
```

- Lines starting with `#` are ignored
- Genotype `--` indicates no call (ignored)
- Both rsIDs and position-based matching are used

### Required Data Files

| File | Size | Included | Source |
|------|------|----------|--------|
| genome.txt | ~25MB | No | Your 23andMe download |
| clinvar_alleles.tsv | ~289MB | No | [Download](#quick-start) |
| clinical_annotations.tsv | ~850KB | Yes | PharmGKB |
| clinical_ann_alleles.tsv | ~5.5MB | Yes | PharmGKB |

---

## Running for Multiple People

```bash
# Copy genome file with unique name
cp ~/Downloads/genome_mom.txt data/genome_mom.txt

# Run analysis
uv run python scripts/run_full_analysis.py data/genome_mom.txt --name "Mom"

# Rename outputs to preserve them
mv reports/EXHAUSTIVE_GENETIC_REPORT.md reports/EXHAUSTIVE_GENETIC_REPORT_MOM.md
mv reports/EXHAUSTIVE_DISEASE_RISK_REPORT.md reports/EXHAUSTIVE_DISEASE_RISK_REPORT_MOM.md
mv reports/ACTIONABLE_HEALTH_PROTOCOL_V3.md reports/ACTIONABLE_HEALTH_PROTOCOL_MOM.md
```

---

## Interpretation Guide

### Impact Magnitude Scale (0-6)
- **0**: Informational only
- **1**: Low impact - minor effect
- **2**: Moderate impact - worth noting
- **3**: High impact - actionable
- **4-6**: Very high impact - requires attention

### ClinVar Confidence (Gold Stars)
- **4 stars**: Practice guideline / Expert panel
- **3 stars**: Multiple submitters, no conflicts
- **2 stars**: Multiple submitters with conflicts
- **1 star**: Single submitter
- **0 stars**: No assertion criteria

### Zygosity
- **Homozygous**: Both copies of variant - higher effect
- **Heterozygous + Recessive**: Carrier only - reproductive implications
- **Heterozygous + Dominant**: One copy sufficient - may be affected

---

## Updating Data Sources

### ClinVar (recommended: quarterly)
```bash
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
# Process and convert to required format
```

### PharmGKB (recommended: quarterly)
Download from https://www.pharmgkb.org/downloads (free account required).

---

## Troubleshooting

### "Genome file not found"
Ensure `genome.txt` exists in `data/` or provide full path as argument.

### "ClinVar file not found"
Disease risk analysis will be skipped. Download `clinvar_alleles.tsv` - see Quick Start.

### "PharmGKB files not found"
Drug-gene interactions will be skipped. The files should be included in the repo.

### False positives in disease report
The indel filter should prevent this. Only true SNPs (single nucleotide changes) are analyzed because 23andMe cannot reliably represent insertions/deletions.

---

## Adding Custom SNPs

Edit `scripts/comprehensive_snp_database.py`:

```python
"rs12345": {
    "gene": "GENE_NAME",
    "category": "Category Name",
    "variants": {
        "AA": {"status": "status_name", "desc": "Description", "magnitude": 2},
        "AG": {"status": "other_status", "desc": "Description", "magnitude": 1},
        "GG": {"status": "reference", "desc": "Description", "magnitude": 0},
    },
    "note": "Optional additional context"
}
```

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
