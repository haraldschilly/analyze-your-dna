#!/usr/bin/env python3
"""
AI Portrait Prompt Generator

Generates detailed prompts for image generation based on genetic traits.
Creates text descriptions suitable for models like Google Imagen, DALL-E, Stable Diffusion.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from traits_snp_database import TRAITS_SNPS
from fast_loader import load_genome_fast
from generate_traits_report import (
    analyze_traits_genome,
    predict_eye_color_mlr,
    complement_genotype,
    check_genotype_match
)


def get_trait_value(genome_by_rsid: dict, rsid: str) -> dict:
    """Get trait info for a specific SNP."""
    if rsid not in TRAITS_SNPS:
        return None

    user_geno = genome_by_rsid.get(rsid)
    if not user_geno or user_geno == '--':
        return None

    matched_geno, variant_info = check_genotype_match(user_geno, TRAITS_SNPS[rsid]['variants'])

    if variant_info:
        return {
            'genotype': user_geno,
            'status': variant_info['status'],
            'description': variant_info['desc'],
            'gene': TRAITS_SNPS[rsid]['gene']
        }
    return None


def generate_portrait_prompt(genome_by_rsid: dict, birth_year: int, sex: str,
                            hair_style: str = "natural", target_age: int = None) -> dict:
    """Generate portrait prompts from genetic data."""

    current_year = datetime.now().year
    age = current_year - birth_year
    if target_age:
        age = target_age

    # Analyze traits
    results = analyze_traits_genome(genome_by_rsid)
    eye_mlr = results['eye_color_mlr']

    # =======================
    # EYE COLOR
    # =======================
    eye_color_desc = "brown eyes"
    eye_confidence = 0

    if eye_mlr['prediction'] != "Inconclusive":
        eye_confidence = eye_mlr['confidence']
        prediction = eye_mlr['prediction'].lower()

        if "blue" in prediction:
            eye_color_desc = "blue eyes"
        elif "brown" in prediction:
            eye_color_desc = "brown eyes"
        elif "intermediate" in prediction or "green" in prediction or "hazel" in prediction:
            eye_color_desc = "hazel green eyes"

    # =======================
    # HAIR COLOR & TEXTURE
    # =======================
    hair_color = "brown"
    hair_texture = "straight"

    # Check MC1R for red hair
    mc1r_score = results['mc1r_red_hair_score']
    if mc1r_score >= 4:
        hair_color = "natural red hair with copper tones"
    elif mc1r_score >= 2:
        hair_color = "dark auburn hair with reddish undertones"
    else:
        # Check SLC45A2 for blonde/dark
        slc45a2 = get_trait_value(genome_by_rsid, 'rs16891982')
        kitlg = get_trait_value(genome_by_rsid, 'rs12821256')

        if slc45a2 and 'light' in slc45a2['status']:
            if kitlg and 'blonde' in kitlg['status']:
                hair_color = "light blonde hair"
            else:
                hair_color = "light brown hair"
        elif slc45a2 and 'dark' in slc45a2['status']:
            hair_color = "dark brown to black hair"
        else:
            hair_color = "medium brown hair"

    # Hair texture
    tchh = get_trait_value(genome_by_rsid, 'rs11803731')
    if tchh:
        if 'curly' in tchh['status']:
            hair_texture = "curly"
        elif 'wavy' in tchh['status']:
            hair_texture = "wavy"
        else:
            hair_texture = "straight"

    # EDAR (East Asian thick straight hair)
    edar = get_trait_value(genome_by_rsid, 'rs3827760')
    if edar and 'thick_straight' in edar['status']:
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
    irf4 = get_trait_value(genome_by_rsid, 'rs12203592')
    if age > 35 and irf4 and 'T' in irf4['genotype']:
        if age > 50:
            hair_modifiers.append("with significant graying throughout")
        else:
            hair_modifiers.append("with early graying at the temples")

    # Balding (males only)
    baldness_risk = False
    if sex.lower() in ['male', 'm', 'man']:
        ar = get_trait_value(genome_by_rsid, 'rs6152')
        chr20 = get_trait_value(genome_by_rsid, 'rs1160312')

        high_risk = (ar and 'high_risk' in ar['status']) or (chr20 and 'high_risk' in chr20['status'])

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

    slc24a5 = get_trait_value(genome_by_rsid, 'rs1426654')
    if slc24a5:
        if 'pale' in slc24a5['status']:
            skin_tone = "pale fair skin"
        elif 'dark' in slc24a5['status']:
            skin_tone = "dark skin"
        else:
            skin_tone = "medium skin tone"

    # Freckles
    has_freckles = False
    if irf4 and 'T' in irf4['genotype']:
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
    pax3_nose = get_trait_value(genome_by_rsid, 'rs11175967')
    if pax3_nose:
        if 'high_bridge' in pax3_nose['status']:
            nose_descriptors.append("high nasal bridge")
        elif 'low_bridge' in pax3_nose['status']:
            nose_descriptors.append("low nasal bridge")

    # Nose shape (DCHS2)
    dchs2_tip = get_trait_value(genome_by_rsid, 'rs2045323')
    if dchs2_tip:
        if 'upturned' in dchs2_tip['status']:
            nose_descriptors.append("slightly upturned nose")
        elif 'hooked' in dchs2_tip['status']:
            nose_descriptors.append("aquiline nose shape")

    # Nose width (RUNX2)
    runx2 = get_trait_value(genome_by_rsid, 'rs1852985')
    if runx2:
        if 'wide_bridge' in runx2['status']:
            nose_descriptors.append("broad nasal bridge")
        elif 'narrow_bridge' in runx2['status']:
            nose_descriptors.append("narrow nasal bridge")

    if nose_descriptors:
        facial_features.append("a " + ", ".join(nose_descriptors[:2]))

    # Chin/Jaw
    ghr = get_trait_value(genome_by_rsid, 'rs6184')
    if ghr:
        if 'prominent' in ghr['status']:
            facial_features.append("a strong, prominent jawline and chin")
        elif 'normal' in ghr['status']:
            facial_features.append("a well-defined jawline")

    # Cleft chin
    cleft = get_trait_value(genome_by_rsid, 'rs2013162')
    if cleft and 'likely' in cleft['status']:
        facial_features.append("a distinctive cleft chin")

    # Earlobes (for side profile)
    earlobes = get_trait_value(genome_by_rsid, 'rs2080401')
    earlobe_type = "attached earlobes"
    if earlobes and 'detached' in earlobes['status']:
        earlobe_type = "free-hanging earlobes"

    # =======================
    # BODY TYPE
    # =======================
    build = "average build"

    # FTO (BMI)
    fto = get_trait_value(genome_by_rsid, 'rs9939609')
    mc4r = get_trait_value(genome_by_rsid, 'rs17782313')

    high_bmi_risk = (fto and 'risk' in fto['status']) or (mc4r and 'risk' in mc4r['status'])

    if high_bmi_risk:
        build = "robust, stocky build"
    else:
        build = "lean, athletic build"

    # Height tendency (simplified - just note if tall/short genes)
    height_genes = ['rs1042725', 'rs6060373', 'rs6440003']
    tall_count = 0
    short_count = 0

    for rsid in height_genes:
        trait = get_trait_value(genome_by_rsid, rsid)
        if trait:
            if 'taller' in trait['status']:
                tall_count += 1
            elif 'shorter' in trait['status']:
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

    # Myopia
    gjd2 = get_trait_value(genome_by_rsid, 'rs524952')
    rasgrf1 = get_trait_value(genome_by_rsid, 'rs8027411')

    wears_glasses = False
    if (gjd2 and 'myopia' in gjd2['status']) or (rasgrf1 and 'myopia' in rasgrf1['status']):
        wears_glasses = True
        accessories.append("wearing modern prescription glasses")

    # Hyperopia (reading glasses if older)
    if not wears_glasses and age > 40:
        if gjd2 and 'hyperopia' in gjd2['status']:
            accessories.append("wearing reading glasses")

    # =======================
    # ASSEMBLE PROMPTS
    # =======================

    # Age/sex descriptor
    age_sex = f"{age}-year-old {sex.lower()}"

    # Front view
    front_parts = [
        f"A photorealistic portrait of a {age_sex} with {eye_color_desc},",
        hair_full
    ]

    if hair_modifiers:
        front_parts.append(" ".join(hair_modifiers))

    front_parts.append(f"{skin_tone}{freckle_desc},")

    if facial_features:
        front_parts.append(", ".join(facial_features) + ".")

    if accessories:
        front_parts.append("They are " + ", and ".join(accessories) + ".")

    front_parts.append(f"Natural lighting, sharp focus on facial features, {hair_style} hairstyle.")

    front_view = " ".join(front_parts)

    # Side profile
    side_parts = [
        f"Side profile view of the same {age_sex} showing"
    ]

    side_features = []
    if nose_descriptors:
        side_features.append("the " + nose_descriptors[0])
    if ghr and 'prominent' in ghr['status']:
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
    notes.append(f"Eye color: {eye_mlr['prediction']} ({eye_confidence*100:.0f}% confidence)")

    if tchh:
        notes.append(f"Hair: {hair_texture} (TCHH {tchh['genotype']})")

    if irf4 and age > 35 and 'T' in irf4['genotype']:
        notes.append(f"Graying: elevated risk (IRF4 {irf4['genotype']}, age {age})")

    if baldness_risk and sex.lower() in ['male', 'm', 'man']:
        notes.append(f"Male pattern baldness: high risk (age {age})")

    if wears_glasses:
        notes.append(f"Glasses: myopia risk elevated")

    if fto:
        notes.append(f"Build: FTO {fto['genotype']} ({fto['status']})")

    # Construct output
    prompt_output = {
        'subject': age_sex,
        'front_view': front_view,
        'side_profile': side_profile,
        'body_type': body_desc,
        'notes': notes,
        'eye_color_confidence': eye_confidence,
        'traits_used': len([k for k in genome_by_rsid.keys() if k in TRAITS_SNPS])
    }

    return prompt_output


def format_prompt_output(prompt_data: dict) -> str:
    """Format prompt data as readable text."""

    output = []
    output.append("=" * 60)
    output.append("PORTRAIT GENERATION PROMPT")
    output.append("=" * 60)
    output.append("")
    output.append(f"Subject: {prompt_data['subject']}")
    output.append("")
    output.append("FACE (Front View):")
    output.append(prompt_data['front_view'])
    output.append("")
    output.append("FACE (Side Profile):")
    output.append(prompt_data['side_profile'])
    output.append("")
    output.append("BODY TYPE:")
    output.append(prompt_data['body_type'])
    output.append("")
    output.append("=" * 60)
    output.append("GENERATION NOTES")
    output.append("=" * 60)

    for note in prompt_data['notes']:
        output.append(f"- {note}")

    output.append("")
    output.append(f"Traits analyzed: {prompt_data['traits_used']} genetic markers")
    output.append(f"Eye color confidence: {prompt_data['eye_color_confidence']*100:.0f}%")
    output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI portrait prompts from genetic data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_portrait_prompt.py data/genome.txt --birth-year 1980 --sex male
  python3 generate_portrait_prompt.py data/genome.txt --birth-year 1990 --sex female --hair-style "long, wavy" --output prompt.txt
  python3 generate_portrait_prompt.py data/genome.txt --birth-year 1975 --sex male --target-age 30
        """
    )

    parser.add_argument('genome_file', help="Path to 23andMe genome file")
    parser.add_argument('--birth-year', type=int, required=True, help="Year of birth (e.g., 1980)")
    parser.add_argument('--sex', required=True, choices=['male', 'female', 'man', 'woman', 'm', 'f'],
                       help="Biological sex (affects baldness prediction)")
    parser.add_argument('--hair-style', default="natural", help="Hair style preference (e.g., 'short', 'long and wavy')")
    parser.add_argument('--target-age', type=int, help="Optional: target age for rendering (default: current age)")
    parser.add_argument('--output', '-o', help="Output file (default: print to stdout)")

    args = parser.parse_args()

    # Load genome
    print(f"Loading genome from {args.genome_file}...", file=sys.stderr)
    genome_by_rsid, _ = load_genome_fast(args.genome_file)
    print(f"✓ Loaded {len(genome_by_rsid):,} SNPs", file=sys.stderr)

    # Generate prompt
    print("Generating portrait prompt...", file=sys.stderr)
    prompt_data = generate_portrait_prompt(
        genome_by_rsid,
        args.birth_year,
        args.sex,
        args.hair_style,
        args.target_age
    )

    # Format output
    output_text = format_prompt_output(prompt_data)

    # Write or print
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"\n✅ Portrait prompt written to {output_path}", file=sys.stderr)
    else:
        print(output_text)

    print(f"\n✓ Eye color: {prompt_data['subject']}", file=sys.stderr)


if __name__ == "__main__":
    main()
