# Future Implementation Plan

This document outlines the next steps for stabilizing, integrating, and testing the `analyze-your-dna` pipeline. Since real genetic data is sensitive and currently unavailable, we will rely heavily on **synthetic data** and **unit tests** to verify correctness.

## 1. Codebase Refactoring (Immediate Priority)

The current codebase has some duplicated logic between the new Traits modules and the main health pipeline.

### A. Centralize Genotype Matching
**Issue:** `run_full_analysis.py` uses simple dictionary lookups, while `generate_traits_report.py` has robust logic for strand flips (complement) and reversals.
**Plan:**
1.  Move `complement_genotype` and `check_genotype_match` from `scripts/generate_traits_report.py` to `scripts/utils.py`.
2.  Update `scripts/run_full_analysis.py` to use these utility functions.
    *   *Benefit:* This will fix potential false negatives in the health report where the 23andMe file reports a strand flip (e.g., `TT` instead of `AA`) compared to the database.
3.  Update `scripts/generate_portrait_prompt.py` to import from `utils.py`.

### B. Standardize "No-Call" Handling
**Issue:** Different scripts handle missing data (`--`) differently.
**Plan:**
1.  Define a constant `NO_CALL_VALUES = {'--', '-', '00'}` in `utils.py`.
2.  Update `fast_loader.py` to optionally normalize all these to `None` or a consistent sentinel value upon loading.

---

## 2. Pipeline Integration

The Traits and Portrait modules are currently standalone scripts. They need to be part of the main workflow.

### A. Update `run_full_analysis.py`
**Goal:** Running one command generates all insights.
**Plan:**
1.  Import `analyze_traits_genome` and `generate_traits_report` into `run_full_analysis.py`.
2.  Add a step `step_generate_traits_report` after the disease risk analysis.
3.  Add CLI flags:
    *   `--portrait`: If set, also generates `PORTRAIT_PROMPT.txt`.
    *   `--all`: Runs everything (Health, Disease, Traits, Portrait).

### B. Output Organization
**Goal:** Keep the `reports/` folder clean.
**Plan:**
*   Structure output as:
    ```
    reports/
      [Subject_Name]/
        1_HEALTH_REPORT.md
        2_DISEASE_RISK.md
        3_TRAITS_REPORT.md
        4_PORTRAIT_PROMPT.txt
    ```

---

## 3. Testing Strategy (Synthetic Data)

Since we cannot test with real data, we must create **synthetic genomes** that mathematically guarantee specific outcomes.

### A. Create Synthetic Test Genomes
Create a new directory `tests/synthetic_data/` containing:

1.  **`genome_blue_eyes.txt`**:
    *   Hardcode `rs12913832` to `GG` (HERC2).
    *   Hardcode `rs1800407` to `AA`.
    *   *Expectation:* Eye color prediction > 90% Blue.

2.  **`genome_red_hair.txt`**:
    *   Hardcode `rs1805007` (MC1R) to `TT`.
    *   *Expectation:* Hair color prediction "Red".

3.  **`genome_universal_donor.txt`**:
    *   Hardcode `rs8176719` to `DD` (Type O).
    *   *Expectation:* Blood type O.

4.  **`genome_high_risk.txt`**:
    *   Includes known pathogenic ClinVar entries.
    *   *Expectation:* Disease report flags "Pathogenic".

### B. Unit Test Suite
Create `tests/test_traits_analysis.py`:
1.  **Test MLR Math:** Verify that the logistic regression formula correctly sums probabilities to 1.0.
2.  **Test Blood Type Logic:** exhaustively test the 2-SNP logic table (all combinations of `rs8176719` and `rs8176746`).
3.  **Test Strand Flips:** Verify that `check_genotype_match("TT", {"AA": ...})` returns a match.

---

## 4. Documentation

1.  **Update `README.md`**:
    *   Add documentation for the new `generate_traits_report.py` and `generate_portrait_prompt.py`.
    *   Update the "What It Analyzes" table using the `snp_database_stats` utility.
2.  **Add `docs/INTERPRETATION_GUIDE.md`**:
    *   Explain the limitations of polygenic scores (e.g., for height/BMI).
    *   Explain the "Confidence" metrics (Gold Stars) for ClinVar.

---

## 5. Future Features (Blue Sky)

1.  **Ancestry Inference**:
    *   Use a small set of ancestry-informative markers (AIMs) to guess rough super-population (Eur/Asian/Afr) to adjust risk scores.
2.  **Polygenic Risk Scores (PRS)**:
    *   Move beyond single-SNP analysis for complex diseases (Type 2 Diabetes, Coronary Artery Disease) by summing weighted contributions of 100+ SNPs.
3.  **Local API / UI**:
    *   Wrap the python scripts in a simple FastAPI backend.
    *   Serve a lightweight HTML frontend to drag-and-drop the genome file and view reports interactively.
