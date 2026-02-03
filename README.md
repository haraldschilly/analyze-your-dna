<img src=".github/icon.webp" align="right" width="80" />

# Genetic Health Analysis Pipeline

<br clear="all" />

A comprehensive genetic health analysis pipeline that processes 23andMe raw data to generate detailed health reports using Claude Code or other AI Agents.

![Pipeline Architecture](.github/pipeline-graphics.webp)

## Attribution

This project is derived from work by **Nick Saraev**, originally demonstrated in:

**"I gave an AI my DNA and let it analyze my entire genome"**
YouTube: https://youtu.be/O1ICQworLVc

The original concept uses Claude Code to analyze 23andMe genetic data against ClinVar and PharmGKB databases to generate personalized health reports.

---

## AI Assistant Mode (Recommended)

This tool is designed to be used with an AI agent. It allows you to "chat" with your genome, ask follow-up questions, and get explanations in plain English.

**Recommended Agents:**
*   [**Claude Code (Anthropic)**](https://claude.ai/code) - The primary agent this project was designed for.
*   [**Gemini (Google)**](https://ai.google.dev/gemini-api/docs/cli) - Excellent analysis capabilities.
*   [**OpenCode (open source)**](https://opencode.ai/) - can make use of a variety of models.
*   [**Codex (OpenAI)**](https://openai.com/codex/) - Agent optimized for coding.

### Interactive Session Example

Here is how you can use this tool with an AI agent in your terminal:

```text
> Please analyze my DNA file using the full analysis script.

I will run the full genetic analysis pipeline on your 'genome.txt' file.

$ uv run python scripts/run_full_analysis.py data/genome.txt

======================================================================
FULL GENETIC HEALTH ANALYSIS
======================================================================

>>> Loading genome from data/genome.txt
    Using optimized Polars loader (v1.2.0)
    Loaded 638,124 SNPs

>>> Loading PharmGKB data
    Loaded 8,142 drug-gene interactions

>>> Running lifestyle/health analysis
    Found 45 lifestyle/health findings
    Found 12 drug-gene interactions

>>> Loading ClinVar and analyzing disease risk
    Using optimized Polars loader (v1.2.0)
    ClinVar entries scanned: 341,293
    Pathogenic variants: 2
    Likely pathogenic: 1
    Risk factors: 28

>>> Generating reports...
    Written to: reports/EXHAUSTIVE_GENETIC_REPORT.md
    Written to: reports/EXHAUSTIVE_DISEASE_RISK_REPORT.md
    Written to: reports/ACTIONABLE_HEALTH_PROTOCOL_V3.md

======================================================================
ANALYSIS COMPLETE
======================================================================

I have generated three comprehensive reports for you.
1. Your genetic health overview found 45 notable lifestyle variants.
2. The disease risk scan identified 2 pathogenic variants (see 'EXHAUSTIVE_DISEASE_RISK_REPORT.md').
3. I've created a personalized 'ACTIONABLE_HEALTH_PROTOCOL_V3.md' with supplement and diet recommendations.

Would you like me to summarize the high-impact findings for you?
```

---

## Expert Mode (Manual Execution)

If you prefer to run the scripts yourself without an AI agent:

### Prerequisites

1. **Install `uv` (Fastest Python Manager):**
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Get your 23andMe raw data:**
   - Log into 23andMe → Settings → Download Raw Data
   - Save as `data/genome.txt`

### Running with UV (Recommended)

The ClinVar database (`data/clinvar_alleles.tsv.gz`) will be automatically decompressed on first run.

```bash
# Basic run (pure Python, no extra dependencies)
uv run python scripts/run_full_analysis.py

# With fast mode (5-10x speedup using polars)
uv sync --extra fast
uv run python scripts/run_full_analysis.py

# With custom genome file and subject name
uv run python scripts/run_full_analysis.py data/genome.txt --name "Your Name"
```

---

## What It Analyzes

Beyond the full ClinVar database scan (341,000+ clinically annotated variants), the pipeline includes three hand-curated SNP databases covering health conditions, drug responses, and observable traits.

### Comprehensive Health SNPs (88 variants)

Used by the main pipeline (`run_full_analysis.py`) for the detailed health report.

| Category | SNPs | Genes | Genes Covered |
|----------|------|-------|---------------|
| Drug Metabolism | 12 | 10 | CYP1A2, CYP2C19, CYP2C9, CYP2D6, CYP3A5, DPYD, HLA-B, SLCO1B1, TPMT, VKORC1 |
| Nutrition | 9 | 9 | APOA2, BCMO1, FADS1, FTO, FUT2, GC, MCM6/LCT, PPARG, TCF7L2 |
| Cardiovascular | 9 | 8 | ACE, ADRB1, AGT, AGTR1, APOE, F2, F5, GNB3 |
| Fitness | 8 | 8 | ACE, ACTN3, ADRB2, ADRB3, COL1A1, COL5A1, PPARA, PPARGC1A |
| Methylation | 6 | 5 | CBS, MTHFR, MTR, MTRR, PEMT |
| Neurotransmitters | 6 | 5 | ANKK1/DRD2, BDNF, COMT, OPRM1, SLC6A4 |
| Detoxification | 5 | 3 | GSTP1, NAT2, SOD2 |
| Sleep/Circadian | 4 | 4 | ARNTL, CLOCK, MTNR1B, PER2 |
| Skin | 4 | 2 | IRF4, MC1R |
| Mental Health | 4 | 4 | CACNA1C, FKBP5, HTR2A, MIR137 |
| Caffeine Response | 3 | 2 | ADA, ADORA2A |
| Autoimmune | 3 | 3 | HLA-DQA1, PTPN22, STAT4 |
| Longevity | 3 | 3 | CETP, FOXO3, TP53 |
| Inflammation | 2 | 2 | IL6, TNF |
| Iron Metabolism | 2 | 1 | HFE |
| Alcohol | 2 | 2 | ADH1B, ALDH2 |
| Hormone Regulation | 2 | 2 | CYP19A1, FSHR |
| Bone Health | 2 | 2 | ESR1, LRP5 |
| Respiratory | 1 | 1 | SERPINA1 |
| Cancer Predisposition | 1 | 1 | CHEK2 |

### Curated High-Impact SNPs (34 variants)

Used by `analyze_genome.py` for a focused report on the most critical/actionable findings.

| Category | SNPs | Genes | Genes Covered |
|----------|------|-------|---------------|
| Drug Metabolism | 13 | 10 | CYP1A2, CYP2C19, CYP2C9, CYP2D6, CYP3A5, DPYD, HLA-B, SLCO1B1, TPMT, VKORC1 |
| Detoxification | 3 | 2 | GSTP1, NAT2 |
| Caffeine Response | 2 | 1 | ADORA2A |
| Cardiovascular/Neuro | 2 | 1 | APOE |
| Blood Clotting | 2 | 2 | F2, F5 |
| Methylation | 2 | 1 | MTHFR |
| Nutrition | 2 | 2 | GC, MCM6/LCT |
| Iron Metabolism | 2 | 1 | HFE |
| Neurotransmitters | 1 | 1 | COMT |
| Autoimmune | 1 | 1 | HLA-DQA1 |
| Cancer Risk | 1 | 1 | BRCA1 |
| Drug Safety | 1 | 1 | G6PD |
| Lung/Liver | 1 | 1 | SERPINA1 |
| Metabolism | 1 | 1 | FTO |

### Observable Traits SNPs (67 variants)

Used by `generate_traits_report.py` for physical characteristics, sensory traits, and morphology.

| Category | SNPs | Genes | Genes Covered |
|----------|------|-------|---------------|
| Eye Color | 6 | 6 | HERC2, IRF4, OCA2, SLC24A4, SLC45A2, TYR |
| Height | 6 | 6 | CDK6, GDF5, HHIP, HMGA2, LCORL, ZBTB38 |
| Hair Color | 5 | 2 | KITLG, MC1R |
| Nose Shape | 5 | 4 | DCHS2, PAX1, PAX3, RUNX2 |
| Sweet Preference | 4 | 2 | SLC2A2, TAS1R3 |
| Skin Tone | 3 | 3 | ASIP, SLC24A5, TYR |
| Bitter Taste | 3 | 1 | TAS2R38 |
| Chin/Jaw | 3 | 1 | GHR |
| Lactose Tolerance | 2 | 1 | MCM6 |
| Hair Texture | 2 | 2 | EDAR, TCHH |
| Male Pattern Baldness | 2 | 2 | AR, chromosome 20p11 |
| BMI/Weight | 2 | 2 | FTO, MC4R |
| Motion Sickness | 2 | 2 | ADRA2A, near PVRL3 |
| Mosquito Attractiveness | 2 | 2 | HLA region, unknown |
| Blood Type | 2 | 1 | ABO |
| Myopia | 2 | 2 | GJD2, RASGRF1 |
| Astigmatism | 2 | 2 | PDGFRA, VAX2 |
| AMD Risk | 2 | 2 | ARMS2, CFH |
| Cilantro Aversion | 1 | 1 | OR6A2 |
| Asparagus Smell | 1 | 1 | OR2M7 |
| Earwax Type | 1 | 1 | ABCC11 |
| Stretch Marks | 1 | 1 | ELN |
| Earlobes | 1 | 1 | GPR126 |
| Unibrow | 1 | 1 | PAX3 |
| Cleft Chin | 1 | 1 | near MYH16 |
| Finger Ratio | 1 | 1 | LIN28B |
| Photic Sneeze | 1 | 1 | ZEB2 |
| Misophonia | 1 | 1 | TENM2 |
| Perfect Pitch | 1 | 1 | ASAP1 |
| Glaucoma Risk | 1 | 1 | TMCO1 |

### ClinVar Database Scan

In addition to the curated SNPs above, the pipeline scans your entire genome against the **ClinVar database** (341,000+ variants) to find pathogenic/likely pathogenic variants, risk factors, drug responses, and protective variants. This catches rare or newly classified variants that aren't in the curated lists.

---

## Output Reports

The pipeline generates three reports in `reports/`:

| Report | Description |
|--------|-------------|
| `EXHAUSTIVE_GENETIC_REPORT.md` | Drug metabolism, methylation, nutrition, fitness, cardiovascular, sleep genetics |
| `EXHAUSTIVE_DISEASE_RISK_REPORT.md` | Pathogenic variants, carrier status, risk factors from ClinVar |
| `ACTIONABLE_HEALTH_PROTOCOL_V3.md` | Personalized supplements, diet, exercise, monitoring recommendations |

### Optional: Trait Analysis Scripts

Two additional scripts analyze observable physical and sensory traits (not run by default):

**Traits Report**
```bash
uv run python3 scripts/generate_traits_report.py data/genome.txt --name "Subject"
```
Generates a comprehensive traits report covering:
- **Pigmentation**: Eye color (with MLR probability model), hair color/texture, skin tone, freckles
- **Taste & Smell**: Bitter taste sensitivity (PTC), cilantro aversion, asparagus smell, sweet preference
- **Physical Traits**: Blood type (derived), height tendency, BMI predisposition, muscle composition
- **Facial Morphology**: Nose shape, chin/jaw, earlobes, cleft chin
- **Vision**: Myopia, hyperopia, astigmatism risk
- **Other**: Earwax type, hair texture, male pattern baldness (age-dependent)

**AI Portrait Prompt Generator (Experimental)**
```bash
uv run python3 scripts/generate_portrait_prompt.py data/genome.txt \
    --birth-year 1980 --sex male --hair-style "short" \
    --output prompts/portrait.txt
```
Generates natural language image prompts for AI image generators (Google Imagen, DALL-E, Stable Diffusion) based on genetic traits combined with user inputs (age, sex, hair style preference). Includes:
- Front view and side profile descriptions
- Age-dependent traits (graying after 35, male pattern baldness with age thresholds)
- Body type and facial features from genetic markers
- Accessories (glasses if myopia risk detected)

This is an experimental feature exploring DNA-based image generation.

---

## Project Structure

```
analyze-dna/
├── README.md                  # This file
├── CLAUDE.md                  # Instructions for Claude Code
├── pyproject.toml             # UV/pip package configuration
├── data/
│   ├── genome.txt             # Your 23andMe raw data (add this)
│   ├── clinvar_alleles.tsv.gz # ClinVar database (auto-extracted on run)
│   └── clinical_*.tsv         # PharmGKB data (included)
├── scripts/
│   ├── run_full_analysis.py   # Main entry point
│   ├── fast_loader.py         # Optimized loading (polars)
│   └── *.py                   # Analysis modules
└── reports/                   # Generated reports
```

---

## Performance

| Mode | ClinVar Processing | Notes |
|------|-------------------|-------|
| Default (polars) | ~2-4 seconds | Polars installed by default |
| CSV fallback | ~15-25 seconds | Used when polars unavailable |

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
| clinvar_alleles.tsv.gz | ~60MB (zipped) | **Yes** | Included (auto-extracted to 289MB) |
| clinical_annotations.tsv | ~850KB | Yes | PharmGKB |
| clinical_ann_alleles.tsv | ~5.5MB | Yes | PharmGKB |

### Updating Data (Quarterly Recommended)

**ClinVar** (automatic):
```bash
uv run python scripts/update_clinvar.py
```

This downloads the latest `variant_summary.txt.gz` from NCBI and converts it to the required format. The script:
- Filters for GRCh37 assembly (23andMe coordinates)
- Computes gold_stars from ReviewStatus
- Creates both `.tsv` and `.tsv.gz` files

**PharmGKB** (manual): https://www.pharmgkb.org/downloads (free account required)
- Download "Clinical Annotations" files
- Replace `data/clinical_annotations.tsv` and `data/clinical_ann_alleles.tsv`

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
