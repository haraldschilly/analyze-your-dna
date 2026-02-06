# Claude Code Instructions

This file provides context for Claude Code when working on this genetic health analysis project.

## Project Overview

This pipeline analyzes 23andMe raw genetic data against ClinVar and PharmGKB databases to generate health reports.

## Key Files

| File | Purpose |
|------|---------|
| `src/analyze_dna/cli.py` | Main CLI entry point (Click commands) |
| `src/analyze_dna/run_full_analysis.py` | Full pipeline: health + disease risk + action plan |
| `src/analyze_dna/analyze_genome.py` | Quick analysis with ~34 curated high-impact SNPs |
| `src/analyze_dna/full_health_analysis.py` | Comprehensive health optimization report |
| `src/analyze_dna/fast_loader.py` | Optimized data loading with polars fallback |
| `src/analyze_dna/comprehensive_snp_database.py` | ~200 curated SNPs with interpretations |
| `src/analyze_dna/traits_snp_database.py` | ~100 curated trait SNPs (pigmentation, morphology, taste, vision) |
| `src/analyze_dna/generate_exhaustive_report.py` | Report generation with clinical context |
| `src/analyze_dna/generate_traits_report.py` | Traits report (observable characteristics) |
| `src/analyze_dna/generate_portrait_prompt.py` | AI portrait prompt generator from genetic traits |
| `src/analyze_dna/disease_risk_analyzer.py` | ClinVar variant analysis |
| `planning/TODO.md` | **Active task tracking** - check here for open work items |

## Running the Pipeline

The project is structured as a Python package with a Click CLI. Always use `uv run analyze-dna` — the genome file is a **required** argument for all analysis commands.

```
uv sync
uv run analyze-dna full-analysis path/to/genome.txt --name "Subject"
```

### Available CLI Commands

| Command | Description | Output |
|---------|-------------|--------|
| `full-analysis GENOME` | Full pipeline: health + ClinVar disease risk + action plan | 3 reports in `reports/` |
| `quick-analysis GENOME` | Focused analysis with ~34 curated high-impact SNPs + ClinVar | `reports/genetic_report.md` |
| `health-report GENOME` | Comprehensive health optimization (~88 SNPs + PharmGKB) | `reports/COMPLETE_HEALTH_REPORT.md` |
| `traits GENOME` | Observable traits (pigmentation, taste, morphology, vision) | `reports/TRAITS_REPORT.md` |
| `portrait GENOME` | AI portrait prompt generator from genetic traits | stdout or `--output` file |
| `update-clinvar` | Download and convert latest ClinVar database | `data/clinvar_alleles.tsv*` |

All analysis commands require the genome file path as the first argument (e.g., `~/Downloads/genome.txt`).

## Testing

Before pushing any changes, ensure all tests pass:

```bash
uv run pytest
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

## Code Style Conventions

- **Multi-line Lists**: For lists with many elements (typically > 6), favor a columnar format with one element per line and a trailing comma after the last element.
  ```python
  long_list = [
      "element_1",
      "element_2",
      "element_3",
      "element_4",
      "element_5",
      "element_6",
      "element_7",
  ]
  ```

## Adding New SNPs

Edit `src/analyze_dna/comprehensive_snp_database.py`:

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

- `data/clinvar_alleles.tsv` - ClinVar database (~289MB, auto-decompressed from .tsv.gz)
- `data/clinical_annotations.tsv` - PharmGKB (included)
- `data/clinical_ann_alleles.tsv` - PharmGKB (included)
- **User Genome** - 23andMe raw data (user provides path)

## Skills

Reusable procedures for maintenance tasks are documented in `.claude/skills/`:

- **`update-readme-snp-tables`** — Regenerate the SNP coverage tables in README.md after changes to `comprehensive_snp_database.py` or `analyze_genome.py`. See `.claude/skills/update-readme-snp-tables.md` for the counting script and update procedure.

## Performance Notes

- Fast loader uses polars (installed by default)
- Standard mode: ~15-25 sec for ClinVar
- Fast mode: ~2-4 sec for ClinVar
