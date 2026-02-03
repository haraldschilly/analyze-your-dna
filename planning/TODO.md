# Traits Analysis Extension - TODO

## Goals

1. **Traits Report Script** - New script generating a traits report (observable characteristics, not diseases)
2. **AI Image Prompt Generator** - Script that outputs a detailed prompt for image generators based on DNA + user input

---

## Getting Started (for implementing model)

### Key Files to Reference
```
scripts/comprehensive_snp_database.py  # Pattern for SNP database structure
scripts/generate_exhaustive_report.py  # Pattern for report generation
scripts/fast_loader.py                 # How genome data is loaded (returns genome_by_rsid dict)
scripts/full_health_analysis.py        # Pattern for analyzing SNPs against database
```

### How to Run Existing Pipeline
```bash
uv run python3 scripts/run_full_analysis.py data/genome.txt --name "Subject"
```

### SNP Database Pattern (from comprehensive_snp_database.py)
```python
"rs12913832": {
    "gene": "HERC2",
    "category": "Eye Color",
    "variants": {
        "GG": {"status": "blue", "desc": "Blue eyes - HERC2 enhancer inactive", "magnitude": 0},
        "AG": {"status": "intermediate", "desc": "Hazel/Green - heterozygous", "magnitude": 1},
        "AA": {"status": "brown", "desc": "Brown eyes - full OCA2 expression", "magnitude": 0},
    },
    "note": "Master switch for eye color, explains ~74% of blue/brown variance"
}
```

### Eye Color MLR Coefficients (from planning docs Table 2)
For multinomial logistic regression (Blue vs Brown, Intermediate vs Brown):
```python
EYE_COLOR_COEFFICIENTS = {
    "intercept":   {"blue": 0.50,  "inter": -1.20},
    "rs12913832": {"allele": "G", "blue": 4.52,  "inter": 0.45},  # HERC2
    "rs1800407":  {"allele": "A", "blue": 1.20,  "inter": 1.50},  # OCA2
    "rs16891982": {"allele": "C", "blue": 0.85,  "inter": 0.60},  # SLC45A2 (note: C is light allele here)
    "rs1393350":  {"allele": "T", "blue": 0.40,  "inter": 0.35},  # TYR
    "rs12896399": {"allele": "T", "blue": 0.25,  "inter": 0.20},  # SLC24A4
    "rs12203592": {"allele": "T", "blue": 0.15,  "inter": 0.10},  # IRF4
}
# Dosage = count of effect allele (0, 1, or 2)
# logit_blue = intercept_blue + sum(dosage_i * beta_blue_i)
# P(blue) = exp(logit_blue) / (1 + exp(logit_blue) + exp(logit_inter))
```

### Genome Data Access Pattern
```python
from scripts.fast_loader import load_genome_fast
genome_by_rsid, genome_by_position = load_genome_fast("data/genome.txt")

# Lookup: genome_by_rsid.get("rs12913832") → "GG" or "AG" or "AA" or None
# Handle no-calls: "--" appears as None after loading
```

### Strand Complement (ADD THIS to utils.py or new file)
```python
COMPLEMENT = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
def complement_genotype(geno: str) -> str:
    """Convert genotype to opposite strand: AA→TT, CG→GC"""
    return ''.join(COMPLEMENT.get(b, b) for b in geno)

def check_genotype_match(user_geno: str, expected_variants: dict) -> tuple:
    """Check user genotype against expected, handling strand flip and reversal."""
    if user_geno in expected_variants:
        return user_geno, expected_variants[user_geno]
    # Try reversed (AG vs GA)
    rev = user_geno[::-1]
    if rev in expected_variants:
        return rev, expected_variants[rev]
    # Try complement (AA vs TT)
    comp = complement_genotype(user_geno)
    if comp in expected_variants:
        return comp, expected_variants[comp]
    # Try complement + reversed
    comp_rev = comp[::-1]
    if comp_rev in expected_variants:
        return comp_rev, expected_variants[comp_rev]
    return None, None
```

---

## Planning Documents Summary

### Source Documents (from Gemini Research)
- `20260202-dna-phenotype.md` - HIrisPlex-S system, eye/hair/skin prediction with regression coefficients
- `20260202-genetic-trait-data-expansion.md` - Taste, metabolism, morphology, behavioral traits
- `20260202-dna-phenotyping-AI-image-gen.md` - G2P engine and AI prompt generation spec

### Known Issues
- Formula images exported as `![][imageN]` placeholders - need original docs to recover:
  - Logit equations for eye color prediction
  - Softmax probability conversion
  - Polygenic score calculations
  - Some threshold values

---

## Part 1: Traits Report (`scripts/generate_traits_report.py`)

### Architecture
Model after existing `generate_exhaustive_report.py`:
- Input: genome data (from fast_loader)
- Output: Markdown report in `reports/TRAITS_REPORT.md`
- Uses new traits database

### Expected Report Structure
```markdown
# Genetic Traits Report for [Name]
Generated: [date]

## Pigmentation

### Eye Color
**Prediction: Blue (94% confidence)**

Your genotype at the HERC2 master switch (rs12913832) is GG, which strongly
predicts blue eyes. Supporting markers:
- OCA2 rs1800407: AA (lightening modifier)
- SLC24A4 rs12896399: TT (lighter shade)

| Outcome | Probability |
|---------|-------------|
| Blue | 94% |
| Intermediate (Green/Hazel) | 4% |
| Brown | 2% |

### Hair Color
**Prediction: Light Brown / Dark Blonde**
...

## Taste & Smell

### Bitter Taste Sensitivity
**Result: Medium Taster (PAV/AVI)**
You can taste bitter compounds like PTC but find them tolerable...

### Cilantro
**Result: Likely enjoys cilantro (AA at rs72921001)**
...

## Physical Traits

### Blood Type
**Derived: Type A**
Based on rs8176719 (ID) and rs8176746 (GG)...

## Vision

### Refractive Tendencies
- Myopia risk: Elevated (A allele at GJD2)
- Astigmatism risk: Average
...
```

### New SNP Database: `scripts/traits_snp_database.py`

Categories to implement:

#### A. Pigmentation (HIrisPlex-S) - HIGH PRIORITY
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Eye Color** | rs12913832 (HERC2 - master switch), rs1800407 (OCA2), rs12896399 (SLC24A4), rs16891982 (SLC45A2), rs1393350 (TYR), rs12203592 (IRF4) | Multinomial logistic regression: Blue/Intermediate/Brown. GG at HERC2 = blue, AA = brown |
| **Hair Color** | rs1805007, rs1805008, rs1805009, rs11547464 (MC1R - red hair), rs16891982 (SLC45A2), rs12821256 (KITLG) | Check MC1R first for red (3 R-alleles), then SLC45A2 for blonde/dark spectrum |
| **Skin Tone** | rs1426654 (SLC24A5 - "golden" mutation), rs16891982 (SLC45A2), rs1126809 (TYR), rs6119471 (ASIP) | AA at SLC24A5 = pale (nearly fixed in Europeans), GG = dark. ASIP A = lighter/pheomelanin |
| **Freckles** | rs12203592 (IRF4), MC1R variants | T allele at IRF4 = freckles |

#### B. Chemosensory Traits
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Bitter Taste (PTC/PROP)** | rs713598, rs1726866, rs10246939 (TAS2R38) | PAV/AVI haplotype. PAV/PAV = super-taster, AVI/AVI = non-taster |
| **Cilantro Aversion** | rs72921001 (OR6A2) | CC = soapy taste, AA = enjoys cilantro |
| **Asparagus Urine Smell** | rs1332938 (OR2M7) | AA = can't smell, GG/GA = can smell |
| **Sweet Preference** | rs35744813, rs307355 (TAS1R3), rs12878143, rs80115239 (SLC2A2) | T allele at SLC2A2 = "sweet tooth" |

#### C. Metabolic Traits (some overlap with existing)
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Alcohol Flush** | rs671 (ALDH2) | AG = severe flush + cancer risk, AA = can't drink |
| **Caffeine Metabolism** | rs762551 (CYP1A2) | Already in db but frame as "how long caffeine lasts" |
| **Lactose Tolerance** | rs4988235 (MCM6 - European), rs41380347 (East African), rs41525747 (East African) | CC = intolerant (ancestral), T = tolerant. Different SNPs evolved independently in African pastoralists |

#### D. Dermatological/Morphological
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Hair Texture** | rs11803731 (TCHH), rs3827760 (EDAR) | TCHH: TT=straight, AA=curly. EDAR: G=thick straight (East Asian) |
| **Earwax Type** | rs17822931 (ABCC11) | GG/GA = wet/sticky, AA = dry/flaky + less body odor |
| **Male Pattern Baldness** | rs6152 (AR), rs1160312 | Age-dependent trait, males only |
| **Premature Graying** | rs12203592 (IRF4) | T allele = early graying after 35 |
| **Stretch Marks** | rs7787362 (ELN) | C allele = reduced elastin, more prone to striae |

#### E. Facial Morphology
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Nose Shape** | rs2045323 (DCHS2), rs11170678 (DCHS2), rs1852985 (RUNX2), rs11175967 (PAX3), rs17421627 (PAX1) | DCHS2 = pointiness/tip angle, RUNX2 = bridge width, PAX3 = bridge height, PAX1 = nostril breadth |
| **Chin/Jaw** | rs6184, rs6180, rs6182 (GHR), rs3827760 (EDAR) | GHR A = prominent chin/prognathism, EDAR G = reduced chin prominence |
| **Cleft Chin** | rs2013162 area | |
| **Earlobes** | rs2080401 (GPR126) | C = detached, T = attached |
| **Unibrow** | rs9852899 (PAX3) | T = higher likelihood |
| **Widow's Peak** | LRP2, ZNF219 area | No specific rsID in 23andMe, polygenic |
| **Cheek Dimples** | TENM2 area (chr5) | No single SNP predicts well, highly heritable but polygenic |

#### F. Anthropometrics
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Height** | rs1042725 (HMGA2), rs6060373 (GDF5), rs6440003 (ZBTB38), rs16896068 (LCORL), rs2282978 (CDK6), rs64399 (HHIP) | Highly polygenic. Use top SNPs for "tendency" |
| **BMI/Weight** | rs9939609 (FTO), rs1421085 (FTO proxy), rs17782313 (MC4R) | FTO AA = ~3kg heavier, can be attenuated by exercise |
| **Muscle Composition** | rs1815739 (ACTN3) | Already in db. CC=power/sprinter, TT=endurance |
| **Finger Length Ratio (2D:4D)** | rs314277 (LIN28B) | A = higher ratio (longer index), biomarker for prenatal testosterone |

#### G. Neurological/Behavioral
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Chronotype** | rs1801260 (CLOCK) | T = morning person, C = night owl. Already partially covered |
| **Photic Sneeze (ACHOO)** | rs10427255 (ZEB2) | C = sneezes from bright light |
| **Misophonia** | rs1868790 (TENM2) | A = rage at chewing sounds |
| **Motion Sickness** | rs3758987, rs1800544 (ADRA2A) | GG at ADRA2A = susceptible |
| **Perfect Pitch** | rs3057 (ASAP1) | CT = genetic potential (requires training) |
| **Mosquito Attractiveness** | rs5750339, rs11751172 | Polygenic (285 markers in full model), HLA/FUT2 also contribute |

#### H. Blood Type (derived)
Two-SNP derivation:

**Step 1: rs8176719 (O deletion check)**
- `DD` or `--` or `-/-` → Type O (both alleles broken)
- `II` or `GG` or has insertion → functional, proceed to step 2
- `ID` or `G-` → one functional allele, proceed to step 2

**Step 2: rs8176746 (A vs B determinant)** - only if functional from step 1
- `GG` → Type A transferase
- `TT` → Type B transferase
- `GT` → Type AB (if both alleles functional) or A/B (if one O)

**Combined logic:**
| rs8176719 | rs8176746 | Blood Type |
|-----------|-----------|------------|
| DD | any | **O** |
| ID | GG | **A** |
| ID | TT | **B** |
| ID | GT | A or B (ambiguous) |
| II | GG | **A** |
| II | TT | **B** |
| II | GT | **AB** |

Note: 23andMe uses inconsistent indel notation - check for D, -, II, GG variants

#### I. Vision / Refractive Errors
| Trait | Key SNPs | Notes |
|-------|----------|-------|
| **Myopia (nearsighted)** | rs524952 (GJD2), rs8027411 (RASGRF1) | A at GJD2 = nearsighted risk |
| **Hyperopia (farsighted)** | rs524952 (GJD2) | TT = protective, shorter axial length |
| **Astigmatism** | rs7677751 (PDGFRA), rs3771395 (VAX2) | T at rs7677751 = 1.26x risk (GWAS lead SNP) |
| **AMD Risk** | rs1061170 (CFH), rs10490924 (ARMS2) | C at CFH = 7.4x risk |
| **Glaucoma Risk** | rs4656461 (TMCO1) | G = elevated IOP risk |

Sources for astigmatism:
- [PDGFRA GWAS meta-analysis (Fan et al.)](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1002402)
- [UK Biobank corneal astigmatism GWAS](https://pmc.ncbi.nlm.nih.gov/articles/PMC6267700/)
- [VAX2 candidate gene study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3576051/)

---

## Part 2: AI Image Prompt Generator (`scripts/generate_portrait_prompt.py`)

### User Inputs Required
- Year of birth (to calculate current age)
- Sex (male/female)
- Hair length/style (user preference, not genetic)
- Optional: "target age" for rendering

### Output
Structured prompt for SDXL/DALL-E with:
1. Base subject descriptor (age, sex)
2. Pigmentation tokens (eye color, hair color, skin tone)
3. Morphology tokens (nose, chin, build)
4. Texture tokens (freckles, hair texture)
5. Age-dependent modifiers (graying, balding)
6. Accessories (glasses if myopia)
7. Style wrapper (photorealistic keywords)
8. Negative prompt

### Prompt Token Weighting (from docs)
```
(freckles:1.3)
(blue eyes:1.2)
red hair:1.4
curly hair:1.2
```

### Views to Generate
- Front view (face portrait)
- Side profile
- Body shape descriptor (separate section)

### Age-Dependent Logic
| Age Range | Modifications |
|-----------|---------------|
| < 25 | Ignore balding |
| 30-50 | "Receding hairline" if high risk |
| > 35 | "Salt and pepper" if graying risk |
| > 40 | "Reading glasses" if hyperopia |
| > 50 | "Bald pate" if high balding risk |

### Expected Output Format
```
=== PORTRAIT PROMPT ===

Subject: 45-year-old male

FACE (Front View):
A photorealistic portrait of a 45-year-old Caucasian man with blue eyes,
light brown wavy hair with early graying at the temples, fair skin with
light freckling across the nose and cheeks, a prominent aquiline nose with
high bridge, and a strong defined jawline. He wears modern rectangular
prescription glasses. Natural lighting, sharp focus on facial features.

FACE (Side Profile):
Side profile view of the same man showing the aquiline nose shape, slightly
receding hairline, attached earlobes, and strong chin projection.

BODY TYPE:
Medium-tall stature with an average to slightly robust build.

=== GENERATION NOTES ===
- Eye color confidence: 94% blue
- Hair: wavy (TCHH AT), graying risk elevated (IRF4 TT, age 45)
- Glasses: myopia risk elevated (GJD2 AA)
- Build: FTO AT (moderate BMI tendency)
```

### CLI Interface
```bash
uv run python3 scripts/generate_portrait_prompt.py data/genome.txt \
    --birth-year 1980 \
    --sex male \
    --hair-style "short, neat" \
    --output prompts/portrait.txt
```

The "output" is optional, and can be omitted to print to stdout instead.

---

## Implementation Order

### Phase 1: Foundation
1. [ ] Create `scripts/traits_snp_database.py` with all trait SNPs
2. [ ] Add strand complement utility (A↔T, C↔G) — currently only reversal exists, not complement
   ```python
   COMPLEMENT = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
   def complement_genotype(geno):
       return ''.join(COMPLEMENT.get(b, b) for b in geno)
   # "AA" → "TT", "CG" → "GC"
   ```
3. [ ] Add no-call handling: "--" → None, with "Inconclusive" reporting for critical SNPs

### Phase 2: Traits Report
3. [ ] Create `scripts/generate_traits_report.py`
4. [ ] Implement category-by-category analysis
5. [ ] Add probability calculations for pigmentation (need formula coefficients)
6. [ ] Generate markdown report with interpretations

### Phase 3: Portrait Prompt Generator
7. [ ] Create `scripts/generate_portrait_prompt.py`
8. [ ] Implement trait → token mapping
9. [ ] Add age-dependent modifiers
10. [ ] Build prompt assembly with weights
11. [ ] Add user input handling (CLI args or interactive)

### Phase 4: Integration
12. [ ] Add to `run_full_analysis.py` as optional output
13. [ ] Update README with new features
14. [ ] Add tests

---

## Decisions Made

1. **Eye Color Prediction**: Full MLR with probabilities
   - Use approximate coefficients from planning docs
   - Output like "Blue: 94%, Intermediate: 4%, Brown: 2%"
   - May need to look up Walsh et al. 2011/2013 for exact coefficients

2. **Ancestry Handling**: Add as optional input
   - `--ancestry european|east_asian|african|south_asian|mixed` (default: european)
   - Adjust SNP weights/interpretation per ancestry
   - Different lactose SNPs for non-European ancestry
   - Note limitations when ancestry not specified

3. **Image Generator Target**: Generic format
   - Primary target: Google Imagen/Banana-pro
   - Keep prompt format generic (natural language, no SDXL-specific weighting syntax)
   - Output as descriptive text that works across models

4. **Report Name**: "Traits Report" (simple, clear)

---

## SNP Quick Reference (Master Lookup)

### Pigmentation
| rsID | Gene | Effect/Ref | Prediction |
|------|------|------------|------------|
| rs12913832 | HERC2 | G/A | G=Blue, A=Brown |
| rs1800407 | OCA2 | A/G | A=Light, G=Dark |
| rs16891982 | SLC45A2 | G/C | G=Blonde/Pale, C=Dark |
| rs1426654 | SLC24A5 | A/G | A=Pale, G=Dark |
| rs1805007 | MC1R | T/C | T=Red hair |
| rs12203592 | IRF4 | T/C | T=Freckles+Graying |

### Morphology
| rsID | Gene | Effect/Ref | Prediction |
|------|------|------------|------------|
| rs11803731 | TCHH | A/T | A=Curly, T=Straight |
| rs3827760 | EDAR | G/A | G=Thick straight hair, flat nose |
| rs9939609 | FTO | A/T | A=Higher BMI |
| rs17822931 | ABCC11 | A/G | A=Dry earwax, no odor |

### Taste/Metabolism
| rsID | Gene | Effect/Ref | Prediction |
|------|------|------------|------------|
| rs713598 | TAS2R38 | C/G | Part of PAV/AVI haplotype |
| rs72921001 | OR6A2 | C/A | C=Cilantro aversion |
| rs671 | ALDH2 | A/G | A=Alcohol flush |
| rs4988235 | MCM6 | T/C | T=Lactose tolerant |

### Vision / Refractive
| rsID | Gene | Effect/Ref | Prediction |
|------|------|------------|------------|
| rs524952 | GJD2 | A/T | A=Myopia risk, T=Hyperopia tendency |
| rs8027411 | RASGRF1 | T/G | T=High myopia risk |
| rs7677751 | PDGFRA | T/C | T=Astigmatism risk (1.26x) |
| rs3771395 | VAX2 | ?/? | Refractive astigmatism |
| rs1061170 | CFH | C/T | C=AMD risk (7.4x) |
| rs10490924 | ARMS2 | T/G | T=AMD risk |
| rs4656461 | TMCO1 | G/? | G=Glaucoma/elevated IOP |

---

## Files to Create

```
scripts/
  traits_snp_database.py      # New trait SNPs
  generate_traits_report.py   # Traits markdown report
  generate_portrait_prompt.py # AI image prompt generator
```

## Files to Modify

```
scripts/run_full_analysis.py  # Add traits report generation
README.md                      # Document new features
```

---

## Quick Start Checklist

**Start here:**
1. Read `scripts/comprehensive_snp_database.py` to understand the SNP entry format
2. Read `scripts/full_health_analysis.py` to see how analysis loops work
3. Create `scripts/traits_snp_database.py` with the SNPs from the tables above
4. Create `scripts/generate_traits_report.py` modeling after `generate_exhaustive_report.py`
5. Test with: `uv run python3 scripts/generate_traits_report.py data/genome.txt`

**Key principle:** Each trait should have clear genotype→interpretation mappings. For complex traits like eye color, implement the probability model. For simple traits like earwax, just map genotype to outcome.
