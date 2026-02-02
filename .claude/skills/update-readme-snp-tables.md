# Skill: Update README SNP Tables

## Description

Regenerate the "What It Analyzes" SNP coverage tables in `README.md` after changes to the curated SNP databases.

## When to Use

Run this after adding, removing, or recategorizing SNPs in:
- `scripts/comprehensive_snp_database.py` (COMPREHENSIVE_SNPS)
- `scripts/analyze_genome.py` (CURATED_SNPS)

## Steps

1. Run the counting function from `scripts/utils.py`:

```bash
cd /home/hsy/p/analyze-your-dna
uv run python3 -c "import sys; sys.path.insert(0, 'scripts'); from utils import snp_database_stats; snp_database_stats()"
```

2. Update the two tables in the `## What It Analyzes` section of `README.md`:
   - **Comprehensive Health SNPs** table: from COMPREHENSIVE_SNPS output, update the total count in the heading and all rows
   - **Curated High-Impact SNPs** table: from CURATED_SNPS output, update the total count in the heading and all rows
   - Tables are sorted by SNP count descending (most SNPs first)
   - Table format: `| Category | SNPs | Genes | Genes Covered |`

3. Verify the edit looks correct by reading the updated section.
