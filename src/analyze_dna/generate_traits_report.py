#!/usr/bin/env python3
# Copyright (C) 2026 Analyze Your DNA Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Genetic Traits Report Generator

Analyzes observable characteristics: pigmentation, taste, morphology, vision, etc.
Excludes disease/health traits (covered in separate health reports).
"""

import io
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .fast_loader import load_genome_fast
from .traits_snp_database import EYE_COLOR_MLR, TRAITS_SNPS


def complement_genotype(geno: str) -> str:
    """Convert genotype to opposite strand: AA→TT, CG→GC"""
    COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C", "-": "-", "D": "D", "I": "I"}
    return "".join(COMPLEMENT.get(b, b) for b in geno)


def get_genotype(genome_by_rsid: dict, rsid: str) -> str | None:
    """Extract genotype string from genome dict, handling both old and new formats."""
    entry = genome_by_rsid.get(rsid)
    if entry is None:
        return None
    # New format: dict with 'genotype' key
    if isinstance(entry, dict):
        val = entry.get("genotype")
        return str(val) if val is not None else None
    # Old format: direct string
    return str(entry)


def check_genotype_match(user_geno: str, expected_variants: dict) -> tuple:
    """Check user genotype against expected, handling strand flip and reversal."""
    if not user_geno or user_geno == "--":
        return None, None

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


def predict_eye_color_mlr(genome_by_rsid: dict) -> dict:
    """Predict eye color using multinomial logistic regression."""

    # Calculate logits for Blue and Intermediate (Brown is reference)
    logit_blue = EYE_COLOR_MLR["intercept"]["blue"]
    logit_inter = EYE_COLOR_MLR["intercept"]["inter"]

    snp_contributions = []
    missing_critical = []

    for snp_rsid in ["rs12913832", "rs1800407", "rs16891982", "rs1393350", "rs12896399", "rs12203592"]:
        genotype = get_genotype(genome_by_rsid, snp_rsid)

        if not genotype or genotype == "--":
            if snp_rsid == "rs12913832":  # Critical SNP
                missing_critical.append(snp_rsid)
            continue

        coeffs = EYE_COLOR_MLR[snp_rsid]
        effect_allele = coeffs["allele"]

        # Count dosage of effect allele (0, 1, or 2)
        dosage = genotype.count(effect_allele)

        if dosage > 0:
            logit_blue += dosage * coeffs["blue"]
            logit_inter += dosage * coeffs["inter"]
            snp_contributions.append(
                {"rsid": snp_rsid, "genotype": genotype, "effect_allele": effect_allele, "dosage": dosage}
            )

    if missing_critical:
        return {
            "prediction": "Inconclusive",
            "confidence": 0,
            "probabilities": {"Blue": 0, "Intermediate": 0, "Brown": 0},
            "reason": f"Critical SNP {missing_critical[0]} is missing",
            "contributions": [],
        }

    # Softmax: convert logits to probabilities
    exp_blue = math.exp(logit_blue)
    exp_inter = math.exp(logit_inter)
    exp_brown = 1.0  # Reference category

    total = exp_blue + exp_inter + exp_brown

    prob_blue = exp_blue / total
    prob_inter = exp_inter / total
    prob_brown = exp_brown / total

    # Determine prediction (IrisPlex standard: >70% threshold for definitive call)
    if prob_blue > 0.70:
        prediction = "Blue"
        confidence = prob_blue
    elif prob_brown > 0.70:
        prediction = "Brown"
        confidence = prob_brown
    elif prob_inter > 0.40:
        prediction = "Intermediate (Green/Hazel)"
        confidence = prob_inter
    else:
        prediction = "Mixed/Indeterminate"
        confidence = max(prob_blue, prob_inter, prob_brown)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": {"Blue": prob_blue, "Intermediate": prob_inter, "Brown": prob_brown},
        "contributions": snp_contributions,
    }


def derive_blood_type(genome_by_rsid: dict) -> dict:
    """Derive blood type from rs8176719 (O deletion) and rs8176746 (A/B)."""

    o_deletion_geno = get_genotype(genome_by_rsid, "rs8176719")
    ab_geno = get_genotype(genome_by_rsid, "rs8176746")

    if not o_deletion_geno or not ab_geno:
        return {
            "blood_type": "Unknown",
            "reason": "Missing required SNPs",
            "o_status": o_deletion_geno or "Missing",
            "ab_status": ab_geno or "Missing",
        }

    # Normalize indel notation
    o_deletion_geno = o_deletion_geno.replace("-", "D")

    # Step 1: Check O deletion status
    if o_deletion_geno in ["DD", "D/D"]:
        return {
            "blood_type": "O",
            "reason": "Both alleles have deletion - no functional transferase",
            "o_status": o_deletion_geno,
            "ab_status": "N/A (both alleles non-functional)",
        }

    # Step 2: Determine A vs B
    has_functional = "I" in o_deletion_geno or "G" in o_deletion_geno

    if not has_functional:
        return {
            "blood_type": "Unknown",
            "reason": f"Cannot interpret O-status genotype: {o_deletion_geno}",
            "o_status": o_deletion_geno,
            "ab_status": ab_geno,
        }

    one_o_allele = o_deletion_geno.count("D") == 1 or o_deletion_geno.count("-") == 1

    if ab_geno == "GG":
        blood_type = "A"
    elif ab_geno == "TT":
        blood_type = "B"
    elif ab_geno in ["GT", "TG"]:
        if one_o_allele:
            blood_type = "A or B (ambiguous - one O allele)"
        else:
            blood_type = "AB"
    else:
        blood_type = f"Unknown ({ab_geno})"

    return {
        "blood_type": blood_type,
        "reason": "Derived from two-SNP logic",
        "o_status": o_deletion_geno,
        "ab_status": ab_geno,
    }


def analyze_traits_genome(genome_by_rsid: dict) -> dict:
    """Analyze genome against traits database."""

    results: dict[str, Any] = {
        "findings": [],
        "by_category": defaultdict(list),
        "eye_color_mlr": None,
        "blood_type": None,
        "mc1r_red_hair_score": 0,
        "summary": {
            "total_snps": len(genome_by_rsid),
            "analyzed_traits": 0,
        },
    }

    # Analyze each trait SNP
    for rsid, info in TRAITS_SNPS.items():
        user_geno = get_genotype(genome_by_rsid, rsid)

        if not user_geno or user_geno == "--":
            continue

        matched_geno, variant_info = check_genotype_match(user_geno, info["variants"])

        if variant_info:
            finding = {
                "rsid": rsid,
                "gene": info["gene"],
                "category": info["category"],
                "genotype": user_geno,
                "matched_genotype": matched_geno,
                "status": variant_info["status"],
                "description": variant_info["desc"],
                "magnitude": variant_info["magnitude"],
                "note": info.get("note", ""),
            }
            results["findings"].append(finding)
            results["by_category"][info["category"]].append(finding)
            results["summary"]["analyzed_traits"] += 1

            # Track MC1R for red hair check
            if info["gene"] == "MC1R" and "red_hair" in variant_info["status"]:
                results["mc1r_red_hair_score"] += variant_info["magnitude"]

    # Special analyses
    results["eye_color_mlr"] = predict_eye_color_mlr(genome_by_rsid)
    results["blood_type"] = derive_blood_type(genome_by_rsid)

    return results


def generate_traits_report(results: dict, subject_name: str) -> str:
    """Generate markdown traits report and return as string."""
    f = io.StringIO()
    # Header
    f.write(f"# Genetic Traits Report for {subject_name}\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    f.write("This report analyzes observable characteristics based on genetic variants. ")
    f.write("It covers pigmentation, taste/smell, physical features, and vision traits.\n\n")
    f.write("---\n\n")

    # Executive Summary
    f.write("## Executive Summary\n\n")
    f.write(f"- **Total SNPs in genome:** {results['summary']['total_snps']:,}\n")
    f.write(f"- **Trait SNPs analyzed:** {results['summary']['analyzed_traits']}\n")
    eye_summary = results["eye_color_mlr"]
    if eye_summary["prediction"] == "Inconclusive":
        f.write("- **Eye color prediction:** Inconclusive\n")
    else:
        probs_summary = eye_summary["probabilities"]
        # Show all colors with >=5% probability
        relevant = sorted(
            ((color, p) for color, p in probs_summary.items() if p >= 0.05),
            key=lambda x: x[1],
            reverse=True,
        )
        prob_str = ", ".join(f"{color} {p * 100:.0f}%" for color, p in relevant)
        f.write(f"- **Eye color prediction:** {prob_str}\n")
    f.write(f"- **Blood type (derived):** {results['blood_type']['blood_type']}\n")
    f.write("\n---\n\n")

    # =====================================================================
    # SECTION A: PIGMENTATION
    # =====================================================================
    f.write("## Pigmentation\n\n")

    # Eye Color (with MLR)
    f.write("### Eye Color\n\n")
    eye_mlr = results["eye_color_mlr"]

    if eye_mlr["prediction"] == "Inconclusive":
        f.write("**Prediction: Inconclusive**\n\n")
        f.write(f"Reason: {eye_mlr['reason']}\n\n")
    else:
        f.write(f"**Prediction: {eye_mlr['prediction']}** ")
        f.write(f"({eye_mlr['confidence'] * 100:.0f}% confidence)\n\n")

        # Probability table (only show categories with >=5% probability)
        probs = eye_mlr["probabilities"]
        display_names = {
            "Blue": "Blue",
            "Intermediate": "Intermediate (Green/Hazel)",
            "Brown": "Brown",
        }
        relevant_probs = sorted(
            ((k, v) for k, v in probs.items() if v >= 0.05),
            key=lambda x: x[1],
            reverse=True,
        )
        if relevant_probs:
            f.write("| Outcome | Probability |\n")
            f.write("|---------|-------------|\n")
            for color, prob in relevant_probs:
                f.write(f"| {display_names[color]} | {prob * 100:.1f}% |\n")
            f.write("\n")

        # Key contributors
        if eye_mlr["contributions"]:
            f.write("**Key genetic contributors:**\n\n")
            for contrib in eye_mlr["contributions"]:
                if contrib["dosage"] > 0:
                    gene = TRAITS_SNPS[contrib["rsid"]]["gene"]
                    f.write(f"- `{contrib['rsid']}` ({gene}): {contrib['genotype']} ")
                    f.write(f"({contrib['dosage']} copies of {contrib['effect_allele']} allele)\n")
            f.write("\n")

        # Find HERC2 master switch
        herc2_findings = [f for f in results["by_category"].get("Eye Color", []) if f["rsid"] == "rs12913832"]
        if herc2_findings:
            herc2 = herc2_findings[0]
            f.write(f"Your genotype at the HERC2 master switch (rs12913832) is **{herc2['genotype']}**, ")
            f.write(f"which {herc2['description'].lower()}.\n\n")

    # Hair Color
    f.write("### Hair Color\n\n")

    # Check for red hair first (epistatic)
    red_score = results["mc1r_red_hair_score"]
    if red_score >= 4:
        f.write("**Prediction: Red/Ginger Hair**\n\n")
        f.write("You carry two or more MC1R loss-of-function variants (R-alleles), ")
        f.write("which causes pheomelanin production instead of eumelanin. ")
        f.write("This is highly likely to result in red or ginger hair.\n\n")
    elif red_score >= 2:
        f.write("**Prediction: Red Hair Carrier**\n\n")
        f.write("You carry one MC1R R-allele. While you likely don't have fully red hair, ")
        f.write("you may have auburn highlights, reddish undertones, or a ginger beard (if male).\n\n")
    else:
        # Check SLC45A2 and KITLG for blonde/dark spectrum
        slc45a2 = [f for f in results["findings"] if f["rsid"] == "rs16891982"]
        kitlg = [f for f in results["findings"] if f["rsid"] == "rs12821256"]

        if slc45a2 and "light" in slc45a2[0]["status"]:
            if kitlg and "blonde" in kitlg[0]["status"]:
                f.write("**Prediction: Blonde / Light Brown**\n\n")
                f.write("Combination of SLC45A2 (light) and KITLG (blonde driver) suggests ")
                f.write("light hair color - likely blonde to light brown.\n\n")
            else:
                f.write("**Prediction: Light Brown**\n\n")
                f.write("SLC45A2 indicates lighter pigmentation.\n\n")
        elif slc45a2 and "dark" in slc45a2[0]["status"]:
            f.write("**Prediction: Dark Brown / Black**\n\n")
            f.write("SLC45A2 indicates darker pigmentation.\n\n")
        else:
            f.write("**Prediction: Medium Brown**\n\n")
            f.write("Intermediate hair color most likely.\n\n")

    # MC1R details
    mc1r_findings = [f for f in results["findings"] if f["gene"] == "MC1R"]
    if mc1r_findings:
        f.write("**MC1R variants detected:**\n\n")
        for finding in mc1r_findings:
            f.write(f"- `{finding['rsid']}`: {finding['genotype']} - {finding['description']}\n")
        f.write("\n")

    # Skin Tone
    f.write("### Skin Tone\n\n")
    slc24a5 = [f for f in results["findings"] if f["rsid"] == "rs1426654"]
    if slc24a5:
        finding = slc24a5[0]
        f.write(f"**Primary indicator (SLC24A5):** {finding['genotype']}\n\n")
        f.write(f"{finding['description']}\n\n")

        if finding["genotype"] in ["AA", "AG", "GA"]:
            f.write("The A allele at SLC24A5 is the 'golden mutation' - nearly fixed in Europeans ")
            f.write("and explains ~25-38% of European-African skin tone difference.\n\n")

    # Freckles
    irf4 = [f for f in results["findings"] if f["rsid"] == "rs12203592"]
    if irf4:
        finding = irf4[0]
        f.write("**Freckles (IRF4):** ")
        if "T" in finding["genotype"]:
            f.write(f"Likely present - {finding['description']}\n\n")
        else:
            f.write(f"Less likely - {finding['description']}\n\n")

    # =====================================================================
    # SECTION B: TASTE & SMELL
    # =====================================================================
    f.write("---\n\n## Taste & Smell\n\n")

    # Bitter Taste (TAS2R38 haplotype)
    tas2r38_snps = [f for f in results["findings"] if f["gene"] == "TAS2R38"]
    if tas2r38_snps and len(tas2r38_snps) == 3:
        f.write("### Bitter Taste Sensitivity (PTC/PROP)\n\n")

        # Count PAV and AVI alleles across the 3 SNPs
        # This is simplified - real haplotype phasing would be better
        pav_count = sum(1 for snp in tas2r38_snps if "taster" in snp["status"].lower())

        if pav_count >= 2:
            f.write("**Result: Taster (likely PAV/PAV or PAV/AVI)**\n\n")
            f.write("You can taste bitter compounds like PTC and PROP. You likely find ")
            f.write("cruciferous vegetables (broccoli, Brussels sprouts) more bitter.\n\n")
        elif pav_count == 1:
            f.write("**Result: Medium Taster (likely PAV/AVI)**\n\n")
            f.write("You can detect bitterness but find it tolerable.\n\n")
        else:
            f.write("**Result: Non-Taster (likely AVI/AVI)**\n\n")
            f.write("You have reduced ability to taste certain bitter compounds. ")
            f.write("Cruciferous vegetables may taste milder or sweeter to you.\n\n")

        f.write("**TAS2R38 genotypes:**\n\n")
        for snp in tas2r38_snps:
            f.write(f"- `{snp['rsid']}`: {snp['genotype']}\n")
        f.write("\n")

    # Other taste/smell traits
    for category in ["Cilantro Aversion", "Asparagus Smell", "Sweet Preference"]:
        findings = results["by_category"].get(category, [])
        if findings:
            f.write(f"### {category}\n\n")
            for finding in findings:
                f.write(f"**{finding['gene']} ({finding['rsid']}):** {finding['genotype']}\n\n")
                f.write(f"{finding['description']}\n\n")

    # =====================================================================
    # SECTION C: PHYSICAL TRAITS
    # =====================================================================
    f.write("---\n\n## Physical Traits\n\n")

    # Blood Type
    f.write("### Blood Type (Derived)\n\n")
    blood_type = results["blood_type"]
    f.write(f"**Predicted Blood Type: {blood_type['blood_type']}**\n\n")
    f.write(f"Based on rs8176719 (O deletion): `{blood_type['o_status']}`\n")
    f.write(f"Based on rs8176746 (A/B determinant): `{blood_type['ab_status']}`\n\n")
    f.write(f"*Note: {blood_type['reason']}*\n\n")

    # Hair Texture
    hair_texture = results["by_category"].get("Hair Texture", [])
    if hair_texture:
        f.write("### Hair Texture\n\n")
        for finding in hair_texture:
            f.write(f"**{finding['gene']} ({finding['rsid']}):** {finding['genotype']}\n\n")
            f.write(f"{finding['description']}\n\n")

    # Earwax Type
    earwax = results["by_category"].get("Earwax Type", [])
    if earwax:
        f.write("### Earwax Type & Body Odor\n\n")
        finding = earwax[0]
        f.write(f"**ABCC11 ({finding['rsid']}):** {finding['genotype']}\n\n")
        f.write(f"{finding['description']}\n\n")
        if finding["genotype"] == "AA":
            f.write("*The AA genotype also results in significantly reduced body odor - ")
            f.write("a pleiotropic effect of the same gene.*\n\n")

    # Facial Morphology
    f.write("### Facial Features\n\n")
    for category in ["Nose Shape", "Chin/Jaw", "Earlobes", "Unibrow", "Cleft Chin"]:
        findings = results["by_category"].get(category, [])
        if findings:
            f.write(f"**{category}:**\n\n")
            for finding in findings:
                f.write(f"- `{finding['rsid']}` ({finding['gene']}): {finding['genotype']} - ")
                f.write(f"{finding['description']}\n")
            f.write("\n")

    # Anthropometrics
    f.write("### Body Type Tendencies\n\n")

    height_findings = results["by_category"].get("Height", [])
    if height_findings:
        f.write(f"**Height genes:** {len(height_findings)} variants detected\n\n")
        f.write("*Note: Height is highly polygenic (~700+ variants). ")
        f.write("These top SNPs show tendency direction only.*\n\n")

    bmi_findings = results["by_category"].get("BMI/Weight", [])
    if bmi_findings:
        f.write("**BMI/Weight:**\n\n")
        for finding in bmi_findings:
            f.write(f"- `{finding['rsid']}` ({finding['gene']}): {finding['genotype']} - ")
            f.write(f"{finding['description']}\n")
        f.write("\n")

    # =====================================================================
    # SECTION D: VISION
    # =====================================================================
    f.write("---\n\n## Vision & Refractive Traits\n\n")

    for category in ["Myopia", "Astigmatism", "AMD Risk", "Glaucoma Risk"]:
        findings = results["by_category"].get(category, [])
        if findings:
            f.write(f"### {category}\n\n")
            for finding in findings:
                f.write(f"**{finding['gene']} ({finding['rsid']}):** {finding['genotype']}\n\n")
                f.write(f"{finding['description']}\n\n")
                if finding["magnitude"] >= 2:
                    f.write(f"⚠️ *Impact level: {finding['magnitude']}/3*\n\n")

    # =====================================================================
    # SECTION E: BEHAVIORAL/NEUROLOGICAL
    # =====================================================================
    f.write("---\n\n## Behavioral & Neurological Traits\n\n")

    for category in ["Photic Sneeze", "Misophonia", "Motion Sickness", "Perfect Pitch", "Mosquito Attractiveness"]:
        findings = results["by_category"].get(category, [])
        if findings:
            f.write(f"### {category}\n\n")
            for finding in findings:
                f.write(f"**{finding['gene']} ({finding['rsid']}):** {finding['genotype']}\n\n")
                f.write(f"{finding['description']}\n\n")

    # =====================================================================
    # DISCLAIMER
    # =====================================================================
    f.write("---\n\n## Important Notes\n\n")
    f.write("### Understanding This Report\n\n")
    f.write("- **Observable traits are probabilistic:** Genes provide tendencies, not certainties\n")
    f.write("- **Environment matters:** Hair dye, diet, sun exposure all affect phenotype\n")
    f.write("- **MLR predictions:** Eye color probabilities are based on the IrisPlex model\n")
    f.write("- **Blood type derivation:** Inferred from two SNPs, may have ambiguity\n")
    f.write("- **Polygenic traits:** Height, BMI involve hundreds of genes - these show direction only\n")
    f.write("- **Population differences:** Some trait associations are population-specific\n\n")
    f.write("### For Vision Findings\n\n")
    f.write("- AMD and glaucoma risk variants are **not deterministic**\n")
    f.write("- Regular eye exams are important regardless of genetic risk\n")
    f.write("- Myopia risk can be modulated by environmental factors (screen time, outdoor activity)\n\n")
    f.write("---\n\n")
    f.write("*Report generated using HIrisPlex-S system for pigmentation, ")
    f.write("GWAS-validated SNPs for morphology, and population genetics data.*\n")

    return f.getvalue()


def run_traits_report(genome_path: Path, subject_name: str, output_dir: Path | None):
    """Run the traits report generation."""
    import click

    click.echo(f"Loading genome from {genome_path}...", err=True)
    genome_by_rsid, _ = load_genome_fast(genome_path)
    click.echo(f"✓ Loaded {len(genome_by_rsid):,} SNPs", err=True)

    click.echo("Analyzing traits...", err=True)
    results = analyze_traits_genome(genome_by_rsid)
    click.echo(f"✓ Analyzed {results['summary']['analyzed_traits']} trait markers", err=True)

    # Generate report
    click.echo("Generating report...", err=True)
    report = generate_traits_report(results, subject_name)

    if output_dir is None:
        click.echo(report)
    else:
        output_path = output_dir / "TRAITS_REPORT.md"
        output_path.write_text(report, encoding="utf-8")
        click.echo(f"  Written: {output_path}", err=True)

    click.echo("\n✅ Traits report generated successfully!", err=True)
    # pylint: disable=unsubscriptable-object  # False positive - results is a dict
    click.echo(f"   Eye color: {results['eye_color_mlr']['prediction']}", err=True)
    click.echo(f"   Blood type: {results['blood_type']['blood_type']}", err=True)
    click.echo(f"   Traits analyzed: {results['summary']['analyzed_traits']}", err=True)


# Note: Use the CLI instead of running this module directly:
# uv run analyze-dna traits <genome> --output <dir> [--name "Name"]
