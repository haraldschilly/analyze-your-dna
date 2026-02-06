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
AI Portrait Prompt Generator

Generates detailed prompts for image generation based on genetic traits.
Creates text descriptions suitable for models like Google Imagen, DALL-E, Stable Diffusion.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .fast_loader import load_genome_fast
from .generate_traits_report import analyze_traits_genome, check_genotype_match, get_genotype
from .traits_snp_database import TRAITS_SNPS


def get_trait_value(genome_by_rsid: dict, rsid: str) -> dict | None:
    """Get trait info for a specific SNP."""
    if rsid not in TRAITS_SNPS:
        return None

    user_geno = get_genotype(genome_by_rsid, rsid)
    if not user_geno or user_geno == "--":
        return None

    _, variant_info = check_genotype_match(user_geno, TRAITS_SNPS[rsid]["variants"])

    if variant_info:
        return {
            "genotype": user_geno,
            "status": variant_info["status"],
            "description": variant_info["desc"],
            "gene": TRAITS_SNPS[rsid]["gene"],
        }
    return None


def generate_portrait_prompt(  # pylint: disable=too-many-positional-arguments
    genome_by_rsid: dict,
    birth_year: int,
    sex: str,
    hair_style: str = "natural",
    target_age: int | None = None,
    glasses: str | None = None,
) -> dict:
    """Generate portrait prompts from genetic data."""

    current_year = datetime.now().year
    age = current_year - birth_year
    if target_age:
        age = target_age

    # Analyze traits
    results = analyze_traits_genome(genome_by_rsid)
    eye_mlr = results["eye_color_mlr"]

    # =======================
    # EYE COLOR
    # =======================
    eye_color_desc = "brown eyes"
    eye_confidence = 0

    # pylint: disable=unsubscriptable-object
    if eye_mlr and eye_mlr["prediction"] != "Inconclusive":
        eye_confidence = eye_mlr["confidence"]
        prediction = eye_mlr["prediction"].lower()

        if "blue" in prediction:
            eye_color_desc = "blue eyes"
        elif "brown" in prediction:
            eye_color_desc = "brown eyes"
        elif "intermediate" in prediction or "green" in prediction or "hazel" in prediction:
            eye_color_desc = "hazel green eyes"
    # pylint: enable=unsubscriptable-object

    # =======================
    # HAIR COLOR & TEXTURE
    # =======================
    hair_color = "brown"
    hair_texture = "straight"

    # Check MC1R for red hair
    mc1r_score = results["mc1r_red_hair_score"]
    if mc1r_score >= 4:
        hair_color = "natural red hair with copper tones"
    elif mc1r_score >= 2:
        hair_color = "dark auburn hair with reddish undertones"
    else:
        # Check SLC45A2 for blonde/dark
        slc45a2 = get_trait_value(genome_by_rsid, "rs16891982")
        kitlg = get_trait_value(genome_by_rsid, "rs12821256")

        if slc45a2 and "light" in slc45a2["status"]:
            if kitlg and "blonde" in kitlg["status"]:
                hair_color = "light blonde hair"
            else:
                hair_color = "light brown hair"
        elif slc45a2 and "dark" in slc45a2["status"]:
            hair_color = "dark brown to black hair"
        else:
            hair_color = "medium brown hair"

    # Hair texture
    tchh = get_trait_value(genome_by_rsid, "rs11803731")
    if tchh:
        if "curly" in tchh["status"]:
            hair_texture = "curly"
        elif "wavy" in tchh["status"]:
            hair_texture = "wavy"
        else:
            hair_texture = "straight"

    # EDAR (East Asian thick straight hair)
    edar = get_trait_value(genome_by_rsid, "rs3827760")
    if edar and "thick_straight" in edar["status"]:
        hair_texture = "thick, coarse, straight"

    # Combine hair
    hair_full = f"{hair_color.split()[0]} {hair_texture} {' '.join(hair_color.split()[1:])}"
    if "hair" not in hair_full:
        hair_full += " hair"

    # =======================
    # AGE-DEPENDENT HAIR MODS
    # =======================
    hair_modifiers = []

    # Graying (IRF4)
    irf4 = get_trait_value(genome_by_rsid, "rs12203592")
    if age > 35 and irf4 and "T" in irf4["genotype"]:
        if age > 50:
            hair_modifiers.append("with significant graying throughout")
        else:
            hair_modifiers.append("with early graying at the temples")

    # Balding (males only)
    baldness_risk = False
    if sex.lower() in ["male", "m", "man"]:
        ar = get_trait_value(genome_by_rsid, "rs6152")
        chr20 = get_trait_value(genome_by_rsid, "rs1160312")

        high_risk = (ar and "high_risk" in ar["status"]) or (chr20 and "high_risk" in chr20["status"])

        if high_risk:
            baldness_risk = True
            if age < 25:
                # Ignore
                pass
            elif age < 40:
                hair_modifiers.append("with slight recession at the temples")
            elif age < 50:
                hair_modifiers.append("with receding hairline and thinning crown")
            else:
                hair_full = "male pattern baldness with horseshoe pattern of hair remaining at sides and back"
                hair_modifiers = []

    # =======================
    # SKIN TONE & FRECKLES
    # =======================
    skin_tone = "fair skin"

    slc24a5 = get_trait_value(genome_by_rsid, "rs1426654")
    if slc24a5:
        if "pale" in slc24a5["status"]:
            skin_tone = "pale fair skin"
        elif "dark" in slc24a5["status"]:
            skin_tone = "dark skin"
        else:
            skin_tone = "medium skin tone"

    # Freckles
    has_freckles = False
    if irf4 and "T" in irf4["genotype"]:
        has_freckles = True

    freckle_desc = ""
    if has_freckles:
        if mc1r_score >= 2:
            freckle_desc = " with prominent freckles across the nose, cheeks, and forehead"
        else:
            freckle_desc = " with light freckling on the nose and cheeks"

    # =======================
    # FACIAL FEATURES
    # =======================
    facial_features = []

    # Nose
    nose_descriptors = []

    # Nose bridge height (PAX3)
    pax3_nose = get_trait_value(genome_by_rsid, "rs11175967")
    if pax3_nose:
        if "high_bridge" in pax3_nose["status"]:
            nose_descriptors.append("high nasal bridge")
        elif "low_bridge" in pax3_nose["status"]:
            nose_descriptors.append("low nasal bridge")

    # Nose shape (DCHS2)
    dchs2_tip = get_trait_value(genome_by_rsid, "rs2045323")
    if dchs2_tip:
        if "upturned" in dchs2_tip["status"]:
            nose_descriptors.append("slightly upturned nose")
        elif "hooked" in dchs2_tip["status"]:
            nose_descriptors.append("aquiline nose shape")

    # Nose width (RUNX2)
    runx2 = get_trait_value(genome_by_rsid, "rs1852985")
    if runx2:
        if "wide_bridge" in runx2["status"]:
            nose_descriptors.append("broad nasal bridge")
        elif "narrow_bridge" in runx2["status"]:
            nose_descriptors.append("narrow nasal bridge")

    if nose_descriptors:
        nose_desc = ", ".join(nose_descriptors[:2])
        article = "an" if nose_desc[0].lower() in "aeiou" else "a"
        facial_features.append(f"{article} {nose_desc}")

    # Chin/Jaw
    ghr = get_trait_value(genome_by_rsid, "rs6184")
    if ghr:
        if "prominent" in ghr["status"]:
            facial_features.append("a strong, prominent jawline and chin")
        elif "normal" in ghr["status"]:
            facial_features.append("a well-defined jawline")

    # Cleft chin
    cleft = get_trait_value(genome_by_rsid, "rs2013162")
    if cleft and "likely" in cleft["status"]:
        facial_features.append("a distinctive cleft chin")

    # Earlobes (for side profile)
    earlobes = get_trait_value(genome_by_rsid, "rs2080401")
    earlobe_type = "attached earlobes"
    if earlobes and "detached" in earlobes["status"]:
        earlobe_type = "free-hanging earlobes"

    # =======================
    # BODY TYPE
    # =======================
    build = "average build"

    # FTO (BMI)
    fto = get_trait_value(genome_by_rsid, "rs9939609")
    mc4r = get_trait_value(genome_by_rsid, "rs17782313")

    high_bmi_risk = (fto and "risk" in fto["status"]) or (mc4r and "risk" in mc4r["status"])

    if high_bmi_risk:
        build = "robust, stocky build"
    else:
        build = "lean, athletic build"

    # Height tendency (simplified - just note if tall/short genes)
    height_genes = ["rs1042725", "rs6060373", "rs6440003"]
    tall_count = 0
    short_count = 0

    for rsid in height_genes:
        trait = get_trait_value(genome_by_rsid, rsid)
        if trait:
            if "taller" in trait["status"]:
                tall_count += 1
            elif "shorter" in trait["status"]:
                short_count += 1

    if tall_count > short_count:
        stature = "tall stature"
    elif short_count > tall_count:
        stature = "shorter stature"
    else:
        stature = "average height"

    # =======================
    # ACCESSORIES (Vision)
    # =======================
    accessories = []

    # User-specified glasses override genetic prediction
    if glasses:
        accessories.append(f"wearing {glasses} glasses")
        wears_glasses = True
    else:
        # Fall back to genetic prediction
        gjd2 = get_trait_value(genome_by_rsid, "rs524952")
        rasgrf1 = get_trait_value(genome_by_rsid, "rs8027411")

        wears_glasses = False
        if (gjd2 and "myopia" in gjd2["status"]) or (rasgrf1 and "myopia" in rasgrf1["status"]):
            wears_glasses = True
            accessories.append("wearing modern prescription glasses")

        # Hyperopia (reading glasses if older)
        if not wears_glasses and age > 40:
            if gjd2 and "hyperopia" in gjd2["status"]:
                accessories.append("wearing reading glasses")

    # =======================
    # ASSEMBLE PROMPTS
    # =======================

    # Age/sex descriptor
    age_sex = f"{age}-year-old {sex.lower()}"

    # Front view
    front_parts = [f"A photorealistic portrait of a {age_sex} with {eye_color_desc},", f"{hair_full},"]

    if hair_modifiers:
        front_parts.append(" ".join(hair_modifiers) + ",")

    front_parts.append(f"{skin_tone}{freckle_desc},")

    if facial_features:
        front_parts.append(", ".join(facial_features) + ".")

    if accessories:
        front_parts.append("They are " + ", and ".join(accessories) + ".")

    front_parts.append(f"Natural lighting, sharp focus on facial features, {hair_style} hairstyle.")

    front_view = " ".join(front_parts)

    # Side profile
    side_parts = [f"Side profile view of the same {age_sex} showing"]

    side_features = []
    if nose_descriptors:
        side_features.append("the " + nose_descriptors[0])
    if ghr and "prominent" in ghr["status"]:
        side_features.append("strong chin projection")
    side_features.append(earlobe_type)

    if baldness_risk and age >= 40:
        side_features.append("hairline recession visible from the side")

    side_parts.append(", ".join(side_features) + ".")

    side_profile = " ".join(side_parts)

    # Body type
    body_desc = f"{stature.capitalize()} with {build}."

    # =======================
    # GENERATION NOTES
    # =======================
    notes = []
    # pylint: disable=unsubscriptable-object
    notes.append(f"Eye color: {eye_mlr['prediction']} ({eye_confidence * 100:.0f}% confidence)")
    # pylint: enable=unsubscriptable-object

    if tchh:
        notes.append(f"Hair: {hair_texture} (TCHH {tchh['genotype']})")

    if irf4 and age > 35 and "T" in irf4["genotype"]:
        notes.append(f"Graying: elevated risk (IRF4 {irf4['genotype']}, age {age})")

    if baldness_risk and sex.lower() in ["male", "m", "man"]:
        notes.append(f"Male pattern baldness: high risk (age {age})")

    if wears_glasses:
        notes.append("Glasses: myopia risk elevated")

    if fto:
        notes.append(f"Build: FTO {fto['genotype']} ({fto['status']})")

    # Construct output
    # pylint: disable=unsubscriptable-object
    prompt_output = {
        "subject": age_sex,
        "front_view": front_view,
        "side_profile": side_profile,
        "body_type": body_desc,
        "notes": notes,
        "eye_color_confidence": eye_confidence,
        "traits_used": len([k for k in genome_by_rsid.keys() if k in TRAITS_SNPS]),
    }

    return prompt_output


def format_prompt_output(prompt_data: dict) -> str:
    """Format prompt data as readable text for image generation."""

    output = []
    output.append("=" * 70)
    output.append("GENETIC PORTRAIT GENERATION PROMPT")
    output.append("=" * 70)
    output.append("")

    # === LAYOUT INSTRUCTIONS ===
    output.append("LAYOUT:")
    output.append("-" * 70)
    output.append("Create a single image containing 3 portrait views arranged as follows:")
    output.append("")
    output.append("  ┌─────────────────┬─────────────────────────┐")
    output.append("  │                 │                         │")
    output.append("  │   FRONT VIEW    │                         │")
    output.append("  │   (Face)        │      FULL BODY          │")
    output.append("  │                 │      (Front view)       │")
    output.append("  ├─────────────────┤                         │")
    output.append("  │                 │                         │")
    output.append("  │   SIDE PROFILE  │                         │")
    output.append("  │   (Left side)   │                         │")
    output.append("  │                 │                         │")
    output.append("  └─────────────────┴─────────────────────────┘")
    output.append("")
    output.append("- Left column: Split horizontally 50/50")
    output.append("  - Top left: Face portrait from the front")
    output.append("  - Bottom left: Face portrait from the left side (profile)")
    output.append("- Right column: Full height, full body view from the front")
    output.append("")

    # === STYLE INSTRUCTIONS ===
    output.append("STYLE:")
    output.append("-" * 70)
    output.append(
        "Pencil drawing with detailed shading, resembling a professional "
        "forensic sketch or computer-generated police composite. Fine pencil "
        "strokes with careful crosshatching for shadows and depth. Highly "
        "detailed facial features with realistic proportions. Clean, "
        "professional quality suitable for identification purposes."
    )
    output.append("")
    output.append("Background: Pure white (#FFFFFF), clean and uncluttered.")
    output.append("")

    # === SUBJECT DESCRIPTION ===
    output.append("SUBJECT:")
    output.append("-" * 70)
    output.append(f"A {prompt_data['subject']}")
    output.append("")

    # === PANEL 1: FRONT VIEW ===
    output.append("PANEL 1 - FACE (Front View, Top Left):")
    output.append("-" * 70)
    # Replace "photorealistic portrait" with sketch-appropriate description
    front_view = (
        prompt_data["front_view"]
        .replace("A photorealistic portrait of", "A detailed pencil sketch of")
        .replace(
            "Natural lighting, sharp focus on facial features,", "Fine pencil shading emphasizing facial structure,"
        )
    )
    output.append(front_view)
    output.append("")

    # === PANEL 2: SIDE PROFILE ===
    output.append("PANEL 2 - FACE (Side Profile, Bottom Left):")
    output.append("-" * 70)
    side_view = prompt_data["side_profile"].replace(
        "Side profile view of the same", "Pencil sketch side profile of the same"
    )
    output.append(side_view)
    output.append("")

    # === PANEL 3: FULL BODY ===
    output.append("PANEL 3 - FULL BODY (Front View, Right Side):")
    output.append("-" * 70)
    output.append(
        f"Full body pencil sketch of the same {prompt_data['subject']}, "
        f"standing in a neutral pose facing forward. "
        f"{prompt_data['body_type']} "
        "Proportional figure drawing with attention to body structure "
        "and posture. Clothing: simple casual attire (t-shirt and pants) "
        "to show body proportions without distraction."
    )
    output.append("")

    # === GENERATION NOTES ===
    output.append("=" * 70)
    output.append("GENERATION NOTES (Genetic Basis)")
    output.append("=" * 70)

    for note in prompt_data["notes"]:
        output.append(f"• {note}")

    output.append("")
    output.append(f"Traits analyzed: {prompt_data['traits_used']} genetic markers")
    output.append(f"Eye color confidence: {prompt_data['eye_color_confidence'] * 100:.0f}%")
    output.append("")

    # === NEGATIVE PROMPT ===
    output.append("NEGATIVE PROMPT (Avoid):")
    output.append("-" * 70)
    output.append(
        "Color, photography, photorealistic, blurry, low quality, "
        "cartoonish, anime, distorted features, extra limbs, "
        "deformed, disfigured, bad anatomy, watermark, signature, "
        "text, colored background, busy background."
    )
    output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI portrait prompts from genetic data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_portrait_prompt.py ~/Downloads/genome.txt --birth-year 1980 --sex male
  python3 generate_portrait_prompt.py ~/Downloads/genome.txt --birth-year 1990 --sex female --hair-style "long, wavy" --output prompt.txt
  python3 generate_portrait_prompt.py ~/Downloads/genome.txt --birth-year 1975 --sex male --target-age 30
        """,
    )

    parser.add_argument("genome_file", help="Path to 23andMe genome file")
    parser.add_argument("--birth-year", type=int, required=True, help="Year of birth (e.g., 1980)")
    parser.add_argument(
        "--sex",
        required=True,
        choices=["male", "female", "man", "woman", "m", "f"],
        help="Biological sex (affects baldness prediction)",
    )
    parser.add_argument(
        "--hair-style", default="natural", help="Hair style preference (e.g., 'short', 'long and wavy')"
    )
    parser.add_argument("--target-age", type=int, help="Optional: target age for rendering (default: current age)")
    parser.add_argument(
        "--glasses",
        help="Optional: glasses description (e.g., 'black thick frame', 'round wireframe', 'reading glasses')",
    )
    parser.add_argument("--output", "-o", help="Output file (default: print to stdout)")

    args = parser.parse_args()

    # Load genome
    print(f"Loading genome from {args.genome_file}...", file=sys.stderr)
    genome_by_rsid, _ = load_genome_fast(args.genome_file)
    print(f"✓ Loaded {len(genome_by_rsid):,} SNPs", file=sys.stderr)

    # Generate prompt
    print("Generating portrait prompt...", file=sys.stderr)
    prompt_data = generate_portrait_prompt(
        genome_by_rsid, args.birth_year, args.sex, args.hair_style, args.target_age, args.glasses
    )

    # Format output
    output_text = format_prompt_output(prompt_data)

    # Write or print
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"\n✅ Portrait prompt written to {output_path}", file=sys.stderr)
    else:
        print(output_text)

    print(f"\n✓ Eye color: {prompt_data['subject']}", file=sys.stderr)


if __name__ == "__main__":
    main()
