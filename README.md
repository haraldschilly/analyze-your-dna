<img src=".github/icon.webp" align="right" width="80" />

# Genetic Health Analysis Pipeline

<br clear="all" />

A comprehensive genetic health analysis pipeline that processes 23andMe raw data to generate detailed health reports using Claude Code or other AI Agents.

![Pipeline Architecture](.github/pipeline-graphics.webp)

## Attribution

This project is derived from work by **Nick Saraev**, originally demonstrated in:

**"I gave an AI my DNA and let it analyze my entire genome"**
YouTube: https://youtu.be/O1ICQworLVc
Website: https://nicksaraev.com

The original concept uses Claude Code (or other agents) to analyze 23andMe genetic data against ClinVar and PharmGKB databases to generate personalized health reports.

---

## AI Assistant Mode (Recommended)

This tool is designed to be used with an AI agent. It allows you to "chat" with your genome, ask follow-up questions, and get explanations in plain English.

**Recommended Agents:**
*   [**Claude Code (Anthropic)**](https://claude.ai/code) - The primary agent this project was designed for.
*   [**Gemini (Google)**](https://ai.google.dev/gemini-api/docs/cli) - Excellent analysis capabilities.
*   [**OpenCode (open source)**](https://opencode.ai/) - Makes use of a variety of models.
*   [**Codex (OpenAI)**](https://openai.com/codex/) - Agent optimized for coding.

### Interactive Session Example

Here is how you can use this tool with an AI agent in your terminal:

```text
> Please analyze my DNA file using the full analysis script.

I will run the full genetic analysis pipeline on your 'genome.txt' file.

$ uv run analyze-dna full-analysis ~/Downloads/genome.txt

======================================================================
FULL GENETIC HEALTH ANALYSIS
======================================================================

>>> Loading genome from /home/user/Downloads/genome.txt
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
   - Note the path to the downloaded file (e.g., `~/Downloads/genome.txt`)

### Running with UV (Recommended)

The ClinVar database (`data/clinvar_alleles.tsv.gz`) will be automatically decompressed on first run.
The genome file is a **required** argument for all analysis commands. Pass the path to your file directly.

```bash
# Full analysis (health + ClinVar disease risk + actionable protocol)
uv run analyze-dna full-analysis path/to/your/genome.txt --name "Your Name"

# Quick analysis (34 curated high-impact SNPs + ClinVar + PharmGKB)
uv run analyze-dna quick-analysis path/to/your/genome.txt

# Comprehensive health optimization report (88 SNPs + PharmGKB)
uv run analyze-dna health-report path/to/your/genome.txt

# See all available commands
uv run analyze-dna --help
```

---

## What It Analyzes

Beyond the full ClinVar database scan (341,000+ clinically annotated variants), the pipeline includes three hand-curated SNP databases covering health conditions, drug responses, and observable traits.

### Comprehensive Health SNPs (88 variants)

Used by the main pipeline (`full-analysis`) for the detailed health report.

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

### Additional Analysis Commands

Beyond the full pipeline, several focused analysis commands are available:

**Quick Analysis** (focused, high-impact)
```bash
uv run analyze-dna quick-analysis path/to/genome.txt
```
Focused analysis using ~34 curated high-impact SNPs (drug metabolism, APOE, clotting factors, etc.) plus ClinVar and PharmGKB. Generates `reports/genetic_report.md`.

**Health Report** (comprehensive optimization)
```bash
uv run analyze-dna health-report path/to/genome.txt
```
Comprehensive health optimization report using ~88 curated SNPs plus PharmGKB drug interactions. Generates `reports/COMPLETE_HEALTH_REPORT.md` with categorized findings and a personalized action plan.

**Traits Report**
```bash
uv run analyze-dna traits path/to/genome.txt --name "Subject"
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
uv run analyze-dna portrait path/to/genome.txt \
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
├── src/analyze_dna/
│   ├── cli.py                 # CLI entry point
│   ├── run_full_analysis.py   # Main analysis logic
│   └── ...                    # Analysis modules
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

Each analysis command requires the genome file path as an argument, making it easy to analyze multiple people without moving files:

```bash
uv run analyze-dna full-analysis ~/Downloads/genome_mom.txt --name "Mom"
uv run analyze-dna full-analysis ~/Downloads/genome_dad.txt --name "Dad"

# Rename outputs to preserve if needed
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
uv run analyze-dna update-clinvar
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

## Attribution

**Original Author & Concept:**
This project is deeply inspired by and based on the work of **Nick Saraev**.
- Original Video: ["I gave an AI my DNA and let it analyze my entire genome"](https://youtu.be/O1ICQworLVc)
- Website: [nicksaraev.com](https://nicksaraev.com)

**Data Sources:**
This software aggregates data from the following public databases:
1.  **PharmGKB**: [Annotated drug-gene interactions](https://www.pharmgkb.org/).
    *   *License:* [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
2.  **ClinVar**: [Public archive of reports of relationships among human variations and phenotypes](https://www.ncbi.nlm.nih.gov/clinvar/).
    *   *License:* Public Domain (National Center for Biotechnology Information).

---

## License & Disclaimer

**Copyright (C) 2026**

### License: GNU GPLv3
This program is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**Why GPLv3?**
This project relies on data from **PharmGKB**, which uses the Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) license. This data license requires that any derived works (including software that interprets this specific data) must be shared under compatible terms to prevent commercial lock-in. GPLv3 is one of the few software licenses explicitly compatible with CC BY-SA 4.0, ensuring that this tool and its derivatives remain open and free for the community.

This project is licensed under **GPLv3** to ensure compatibility with the **CC BY-SA 4.0** license used by the included PharmGKB data.

*   **Code:** GNU General Public License v3.0
*   **Data (PharmGKB):** Creative Commons Attribution-ShareAlike 4.0 International
*   **Data (ClinVar):** Public Domain

See the [LICENSE](LICENSE) file for the full license text.

### ⚠️ IMPORTANT MEDICAL DISCLAIMER
**NOT FOR MEDICAL USE.**

This software is provided for **research, educational, and informational purposes only**.
*   It is **NOT** a clinical diagnostic tool.
*   The reports generated satisfy **NO** regulatory standards (FDA, EMA, etc.).
*   **DO NOT** change your health behavior, diet, or medication based on these results.
*   **ALWAYS** consult a qualified healthcare provider or genetic counselor for interpretation of genetic data.

**NO WARRANTY**
THE PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.
