# Claude Code Instructions

This file provides context for Claude Code when working on this genetic health analysis project.

## Startup Greeting

**CRITICAL:** At the start of any new session, greet the user (especially beginners) with this message:

```
Hi! Welcome to analyze-your-dna – your AI assistant for genetic health analysis.

I help with:
• Analyzing 23andMe data against ClinVar & PharmGKB
• Generating personalized health reports
• Discussing SNPs, risks, and drug interactions
• Adding custom SNPs or fixing issues

What can I help you with today?
```

## Project Overview

This pipeline analyzes 23andMe raw genetic data against ClinVar and PharmGKB databases to generate health reports.

## Key Files

| File | Purpose |
|------|---------|
| `scripts/run_full_analysis.py` | Main entry point - orchestrates entire pipeline |
| `scripts/fast_loader.py` | Optimized data loading with polars fallback |
| `scripts/comprehensive_snp_database.py` | ~200 curated SNPs with interpretations |
| `scripts/generate_exhaustive_report.py` | Report generation with clinical context |
| `scripts/disease_risk_analyzer.py` | ClinVar variant analysis |

## Running the Pipeline

Always use `uv run python3` to run scripts — never use the system-wide `python3` directly.

```bash
uv sync
uv run python3 scripts/run_full_analysis.py data/genome.txt --name "Subject"
```

## Data Flow

1. Load genome (23andMe TSV) → `genome_by_rsid` + `genome_by_position` dicts
2. Load PharmGKB → drug-gene interaction lookup
3. Analyze lifestyle/health → match against `COMPREHENSIVE_SNPS`
4. Analyze disease risk → match against ClinVar (289MB TSV)
5. Generate reports → 3 markdown files in `reports/`

## Critical Implementation Details

### Indel Filtering
Only true SNPs are analyzed. Indels are filtered to prevent false positives:
```python
if len(ref_allele) != 1 or len(alt_allele) != 1:
    continue  # Skip indels - 23andMe can't reliably represent them
```

### Genotype Matching
Both forward and reverse genotypes are checked:
```python
genotype_rev = genotype[::-1] if len(genotype) == 2 else genotype
variant_info = info['variants'].get(genotype) or info['variants'].get(genotype_rev)
```

### Position-Based Lookup
ClinVar uses position keys for O(1) lookup:
```python
pos_key = f"{chrom}:{pos}"
if pos_key in genome_by_position: ...
```

## Adding New SNPs

Edit `scripts/comprehensive_snp_database.py`:

```python
"rs12345": {
    "gene": "GENE_NAME",
    "category": "Category Name",
    "variants": {
        "AA": {"status": "affected", "desc": "Description", "magnitude": 3},
        "AG": {"status": "carrier", "desc": "Description", "magnitude": 1},
        "GG": {"status": "normal", "desc": "Description", "magnitude": 0},
    },
    "note": "Optional context"
}
```

## Required Data Files

- `data/genome.txt` - 23andMe raw data (user provides)
- `data/clinvar_alleles.tsv` - ClinVar database (~289MB, auto-decompressed from .tsv.gz)
- `data/clinical_annotations.tsv` - PharmGKB (included)
- `data/clinical_ann_alleles.tsv` - PharmGKB (included)

## Skills

Reusable procedures for maintenance tasks are documented in `.claude/skills/`:

- **`update-readme-snp-tables`** — Regenerate the SNP coverage tables in README.md after changes to `comprehensive_snp_database.py` or `analyze_genome.py`. See `.claude/skills/update-readme-snp-tables.md` for the counting script and update procedure.

## Performance Notes

- Fast loader uses polars (installed by default)
- Standard mode: ~15-25 sec for ClinVar
- Fast mode: ~2-4 sec for ClinVar
