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
Genetic Traits SNP Database
Observable characteristics: pigmentation, taste, morphology, vision, etc.
Excludes disease/health traits (those are in comprehensive_snp_database.py)
"""

from typing import Any

from .types import SnpDatabase

TRAITS_SNPS: SnpDatabase = {
    # =========================================================================
    # SECTION A: PIGMENTATION (HIrisPlex-S System)
    # =========================================================================
    # Eye Color - Master switch
    "rs12913832": {
        "gene": "HERC2",
        "category": "Eye Color",
        "variants": {
            "GG": {
                "status": "blue",
                "desc": "Blue eyes - HERC2 enhancer inactive, OCA2 expression suppressed",
                "magnitude": 0,
            },
            "AG": {
                "status": "intermediate",
                "desc": "Green/Hazel eyes - heterozygous, intermediate melanin production",
                "magnitude": 1,
            },
            "GA": {
                "status": "intermediate",
                "desc": "Green/Hazel eyes - heterozygous, intermediate melanin production",
                "magnitude": 1,
            },
            "AA": {
                "status": "brown",
                "desc": "Brown eyes - full OCA2 expression, high melanin in iris",
                "magnitude": 0,
            },
        },
        "note": "Master switch for eye color, explains ~74% of blue/brown variance. Critical for MLR prediction.",
    },
    # Eye Color - Modifier loci
    "rs1800407": {
        "gene": "OCA2",
        "category": "Eye Color",
        "variants": {
            "AA": {
                "status": "lightening",
                "desc": "Lightening effect - Arg419Gln reduces melanin, shifts hazel→green/blue",
                "magnitude": 1,
            },
            "AG": {"status": "intermediate", "desc": "Moderate lightening effect", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Moderate lightening effect", "magnitude": 0},
            "GG": {
                "status": "darkening",
                "desc": "No lightening - ancestral allele, darker pigmentation",
                "magnitude": 0,
            },
        },
        "note": "In heterozygous HERC2 (AG), this shifts outcome toward lighter colors",
    },
    "rs12896399": {
        "gene": "SLC24A4",
        "category": "Eye Color",
        "variants": {
            "TT": {
                "status": "lighter",
                "desc": "Lighter iris pigmentation - associated with lighter blue/grey shades",
                "magnitude": 0,
            },
            "TG": {"status": "intermediate", "desc": "Intermediate effect", "magnitude": 0},
            "GT": {"status": "intermediate", "desc": "Intermediate effect", "magnitude": 0},
            "GG": {"status": "darker", "desc": "Darker pigmentation within eye color category", "magnitude": 0},
        },
        "note": "Affects shade intensity within eye color category",
    },
    "rs16891982": {
        "gene": "SLC45A2",
        "category": "Eye Color",
        "variants": {
            "GG": {"status": "light", "desc": "Light effect - Phe374Leu, clear blue/green eyes", "magnitude": 0},
            "GC": {"status": "intermediate", "desc": "Intermediate pigmentation", "magnitude": 0},
            "CG": {"status": "intermediate", "desc": "Intermediate pigmentation", "magnitude": 0},
            "CC": {"status": "dark", "desc": "Darker effect - ancestral, muddy/dark pigment", "magnitude": 0},
        },
        "note": "Also affects hair and skin pigmentation (shared locus)",
    },
    "rs1393350": {
        "gene": "TYR",
        "category": "Eye Color",
        "variants": {
            "GG": {"status": "high_activity", "desc": "Normal tyrosinase activity - darker eyes", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate melanin synthesis", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate melanin synthesis", "magnitude": 0},
            "AA": {"status": "reduced", "desc": "Reduced tyrosinase activity - lighter eyes", "magnitude": 0},
        },
        "note": "Tyrosinase is rate-limiting enzyme in melanin synthesis; A allele reduces activity",
    },
    "rs12203592": {
        "gene": "IRF4",
        "category": "Eye Color",
        "variants": {
            "TT": {
                "status": "light",
                "desc": "Lighter eyes, freckles, premature graying - inhibits tyrosinase",
                "magnitude": 1,
            },
            "TC": {"status": "intermediate", "desc": "Intermediate effect on pigmentation", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate effect on pigmentation", "magnitude": 0},
            "CC": {"status": "dark", "desc": "Darker pigmentation, fewer freckles", "magnitude": 0},
        },
        "note": "Pleiotropic effects: eye color, freckles, and hair graying",
    },
    # Hair Color - Red hair check (epistatic)
    "rs1805007": {
        "gene": "MC1R",
        "category": "Hair Color",
        "variants": {
            "TT": {
                "status": "red_hair",
                "desc": "Red hair allele (Arg151Cys) - two copies likely produces red/ginger hair",
                "magnitude": 2,
            },
            "TC": {
                "status": "carrier",
                "desc": "Red hair carrier - may have auburn highlights or reddish beard",
                "magnitude": 1,
            },
            "CT": {
                "status": "carrier",
                "desc": "Red hair carrier - may have auburn highlights or reddish beard",
                "magnitude": 1,
            },
            "CC": {"status": "normal", "desc": "No red hair variant at this locus", "magnitude": 0},
        },
        "note": "R allele - strong effect. Check epistatically BEFORE other hair color genes",
    },
    "rs1805008": {
        "gene": "MC1R",
        "category": "Hair Color",
        "variants": {
            "TT": {
                "status": "red_hair",
                "desc": "Red hair allele (Arg160Trp) - strong red hair effect",
                "magnitude": 2,
            },
            "TC": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "CT": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "CC": {"status": "normal", "desc": "No red hair variant at this locus", "magnitude": 0},
        },
        "note": "R allele - strong effect",
    },
    "rs1805009": {
        "gene": "MC1R",
        "category": "Hair Color",
        "variants": {
            "TT": {
                "status": "red_hair",
                "desc": "Red hair allele (Asp294His) - strong red hair effect",
                "magnitude": 2,
            },
            "TC": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "CT": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "CC": {"status": "normal", "desc": "No red hair variant at this locus", "magnitude": 0},
        },
        "note": "R allele - strong effect. Third major MC1R variant",
    },
    "rs11547464": {
        "gene": "MC1R",
        "category": "Hair Color",
        "variants": {
            "AA": {"status": "red_hair", "desc": "Red hair allele - contributes to red/ginger hair", "magnitude": 2},
            "AG": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "GA": {"status": "carrier", "desc": "Red hair carrier", "magnitude": 1},
            "GG": {"status": "normal", "desc": "No red hair variant at this locus", "magnitude": 0},
        },
        "note": "Additional MC1R variant",
    },
    # Hair Color - Blonde/Dark spectrum (only if MC1R is normal)
    "rs12821256": {
        "gene": "KITLG",
        "category": "Hair Color",
        "variants": {
            "AA": {
                "status": "blonde",
                "desc": "Strong blonde driver - AA + light SLC45A2 = platinum/ash blonde",
                "magnitude": 1,
            },
            "AG": {"status": "light_brown", "desc": "Light brown / dirty blonde tendency", "magnitude": 0},
            "GA": {"status": "light_brown", "desc": "Light brown / dirty blonde tendency", "magnitude": 0},
            "GG": {"status": "dark", "desc": "Darker hair color", "magnitude": 0},
        },
        "note": "KIT ligand - major blonde hair driver in Europeans",
    },
    # Skin Tone
    "rs1426654": {
        "gene": "SLC24A5",
        "category": "Skin Tone",
        "variants": {
            "AA": {
                "status": "pale",
                "desc": "Light skin (A111T) - nearly fixed in Europeans, major depigmentation allele",
                "magnitude": 0,
            },
            "AG": {"status": "intermediate", "desc": "Intermediate skin tone", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate skin tone", "magnitude": 0},
            "GG": {"status": "dark", "desc": "Dark skin - ancestral allele, high melanin", "magnitude": 0},
        },
        "note": "The 'golden mutation' - strongest skin color gene, ~25-38% of European-African difference",
    },
    "rs1126809": {
        "gene": "TYR",
        "category": "Skin Tone",
        "variants": {
            "AA": {"status": "lighter", "desc": "Lighter skin tone - reduced tyrosinase activity", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate skin tone", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate skin tone", "magnitude": 0},
            "GG": {"status": "darker", "desc": "Darker skin tone", "magnitude": 0},
        },
        "note": "Tyrosinase affects both skin and eye pigmentation",
    },
    "rs6119471": {
        "gene": "ASIP",
        "category": "Skin Tone",
        "variants": {
            "AA": {
                "status": "lighter",
                "desc": "Lighter skin - agouti signaling increases pheomelanin",
                "magnitude": 0,
            },
            "AG": {"status": "intermediate", "desc": "Intermediate effect", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate effect", "magnitude": 0},
            "GG": {"status": "darker", "desc": "Darker skin tone", "magnitude": 0},
        },
        "note": "Agouti signaling protein - affects skin undertone",
    },
    # =========================================================================
    # SECTION B: CHEMOSENSORY (TASTE & SMELL)
    # =========================================================================
    # Bitter Taste - TAS2R38 haplotype (3 SNPs)
    "rs713598": {
        "gene": "TAS2R38",
        "category": "Bitter Taste",
        "variants": {
            "CC": {
                "status": "taster_PAV",
                "desc": "PAV haplotype component - can taste PTC/PROP bitterness",
                "magnitude": 1,
            },
            "CG": {"status": "heterozygous", "desc": "PAV/AVI heterozygous - medium taster", "magnitude": 1},
            "GC": {"status": "heterozygous", "desc": "PAV/AVI heterozygous - medium taster", "magnitude": 1},
            "GG": {"status": "nontaster_AVI", "desc": "AVI haplotype component - reduced bitter taste", "magnitude": 1},
        },
        "note": "Part of PAV/AVI haplotype (position 49: Ala vs Pro). Combine with rs1726866 and rs10246939",
    },
    "rs1726866": {
        "gene": "TAS2R38",
        "category": "Bitter Taste",
        "variants": {
            "TT": {"status": "taster_PAV", "desc": "PAV haplotype component", "magnitude": 1},
            "TC": {"status": "heterozygous", "desc": "PAV/AVI heterozygous", "magnitude": 1},
            "CT": {"status": "heterozygous", "desc": "PAV/AVI heterozygous", "magnitude": 1},
            "CC": {"status": "nontaster_AVI", "desc": "AVI haplotype component", "magnitude": 1},
        },
        "note": "Part of PAV/AVI haplotype (position 262: Val vs Ala)",
    },
    "rs10246939": {
        "gene": "TAS2R38",
        "category": "Bitter Taste",
        "variants": {
            "GG": {"status": "taster_PAV", "desc": "PAV haplotype component", "magnitude": 1},
            "GA": {"status": "heterozygous", "desc": "PAV/AVI heterozygous", "magnitude": 1},
            "AG": {"status": "heterozygous", "desc": "PAV/AVI heterozygous", "magnitude": 1},
            "AA": {"status": "nontaster_AVI", "desc": "AVI haplotype component", "magnitude": 1},
        },
        "note": "Part of PAV/AVI haplotype (position 296: Val vs Ile)",
    },
    # Cilantro
    "rs72921001": {
        "gene": "OR6A2",
        "category": "Cilantro Aversion",
        "variants": {
            "CC": {
                "status": "aversion",
                "desc": "High cilantro aversion - perceives soapy/chemical taste from aldehydes",
                "magnitude": 1,
            },
            "CA": {"status": "moderate", "desc": "Moderate - may detect soapy notes but tolerable", "magnitude": 1},
            "AC": {"status": "moderate", "desc": "Moderate - may detect soapy notes but tolerable", "magnitude": 1},
            "AA": {"status": "enjoys", "desc": "Likely enjoys cilantro - perceives fresh/herbal notes", "magnitude": 0},
        },
        "note": "OR6A2 detects (E)-2-decenal aldehydes in cilantro leaves",
    },
    # Asparagus Smell
    "rs1332938": {
        "gene": "OR2M7",
        "category": "Asparagus Smell",
        "variants": {
            "AA": {
                "status": "cannot_smell",
                "desc": "Asparagus anosmia - cannot smell methanethiol in urine",
                "magnitude": 0,
            },
            "AG": {"status": "can_smell", "desc": "Can smell asparagus urine odor", "magnitude": 0},
            "GA": {"status": "can_smell", "desc": "Can smell asparagus urine odor", "magnitude": 0},
            "GG": {"status": "can_smell", "desc": "Can smell asparagus urine odor", "magnitude": 0},
        },
        "note": "Specific anosmia for sulfurous volatiles. Ability to smell is dominant.",
    },
    # Sweet Preference
    "rs35744813": {
        "gene": "TAS1R3",
        "category": "Sweet Preference",
        "variants": {
            "CC": {
                "status": "higher",
                "desc": "Lower sweet receptor sensitivity - may prefer higher sugar concentrations",
                "magnitude": 1,
            },
            "CT": {"status": "moderate", "desc": "Moderate sweet sensitivity", "magnitude": 0},
            "TC": {"status": "moderate", "desc": "Moderate sweet sensitivity", "magnitude": 0},
            "TT": {"status": "normal", "desc": "Normal sweet receptor sensitivity", "magnitude": 0},
        },
        "note": "TAS1R3 forms sweet taste receptor (T1R2/T1R3 heterodimer)",
    },
    "rs307355": {
        "gene": "TAS1R3",
        "category": "Sweet Preference",
        "variants": {
            "CC": {"status": "lower_sensitivity", "desc": "Reduced sweet receptor sensitivity", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate sweet sensitivity", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate sweet sensitivity", "magnitude": 0},
            "TT": {"status": "normal", "desc": "Normal sweet sensitivity", "magnitude": 0},
        },
        "note": "Linked to rs35744813 - affects sweet taste receptor",
    },
    "rs12878143": {
        "gene": "SLC2A2",
        "category": "Sweet Preference",
        "variants": {
            "TT": {
                "status": "sweet_tooth",
                "desc": "Sweet tooth - impaired glucose sensing may drive higher sugar intake",
                "magnitude": 1,
            },
            "TC": {"status": "moderate", "desc": "Moderate sweet preference", "magnitude": 0},
            "CT": {"status": "moderate", "desc": "Moderate sweet preference", "magnitude": 0},
            "CC": {
                "status": "low_preference",
                "desc": "Lower sweet preference - may prefer savory flavors",
                "magnitude": 0,
            },
        },
        "note": "GLUT2 glucose sensor in hypothalamus affects satiety signaling",
    },
    "rs80115239": {
        "gene": "SLC2A2",
        "category": "Sweet Preference",
        "variants": {
            "AA": {"status": "sweet_preference", "desc": "Higher sweet preference", "magnitude": 1},
            "AG": {"status": "moderate", "desc": "Moderate sweet preference", "magnitude": 0},
            "GA": {"status": "moderate", "desc": "Moderate sweet preference", "magnitude": 0},
            "GG": {"status": "lower", "desc": "Lower sweet preference", "magnitude": 0},
        },
        "note": "Linked to rs12878143 - glucose sensing affects sweet/savory preference",
    },
    # =========================================================================
    # SECTION C: METABOLIC TRAITS (Overlap with health database)
    # =========================================================================
    # Alcohol Flush (already in comprehensive_snp_database as rs671 ALDH2)
    # Caffeine Metabolism (already in comprehensive_snp_database as rs762551 CYP1A2)
    # Lactose Tolerance (already in comprehensive_snp_database as rs4988235)
    # Lactose Tolerance - East African variants
    "rs41380347": {
        "gene": "MCM6",
        "category": "Lactose Tolerance",
        "variants": {
            "GG": {
                "status": "tolerant",
                "desc": "Lactose persistent (East African variant) - can digest lactose in adulthood",
                "magnitude": 0,
            },
            "GT": {"status": "tolerant", "desc": "Lactose persistent (heterozygous)", "magnitude": 0},
            "TG": {"status": "tolerant", "desc": "Lactose persistent (heterozygous)", "magnitude": 0},
            "TT": {
                "status": "intolerant",
                "desc": "Lactose non-persistent - reduced lactase after weaning",
                "magnitude": 0,
            },
        },
        "note": "East African lactase persistence allele - evolved independently from European rs4988235",
    },
    "rs41525747": {
        "gene": "MCM6",
        "category": "Lactose Tolerance",
        "variants": {
            "GG": {"status": "tolerant", "desc": "Lactose persistent (East African variant)", "magnitude": 0},
            "GC": {"status": "tolerant", "desc": "Lactose persistent (heterozygous)", "magnitude": 0},
            "CG": {"status": "tolerant", "desc": "Lactose persistent (heterozygous)", "magnitude": 0},
            "CC": {"status": "intolerant", "desc": "Lactose non-persistent", "magnitude": 0},
        },
        "note": "Another East African lactase persistence variant",
    },
    # =========================================================================
    # SECTION D: DERMATOLOGICAL / MORPHOLOGICAL
    # =========================================================================
    # Hair Texture
    "rs11803731": {
        "gene": "TCHH",
        "category": "Hair Texture",
        "variants": {
            "TT": {
                "status": "straight",
                "desc": "Straight hair - trichohyalin structure favors straight shaft",
                "magnitude": 0,
            },
            "TA": {"status": "wavy", "desc": "Wavy hair", "magnitude": 0},
            "AT": {"status": "wavy", "desc": "Wavy hair", "magnitude": 0},
            "AA": {"status": "curly", "desc": "Curly hair - altered trichohyalin allows shaft to curl", "magnitude": 0},
        },
        "note": "Trichohyalin in hair follicle inner root sheath - primary European hair texture determinant",
    },
    "rs3827760": {
        "gene": "EDAR",
        "category": "Hair Texture",
        "variants": {
            "GG": {
                "status": "thick_straight",
                "desc": "Thick, coarse, straight hair - V370A gain-of-function (East Asian)",
                "magnitude": 0,
            },
            "GA": {"status": "intermediate", "desc": "Intermediate hair thickness", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate hair thickness", "magnitude": 0},
            "AA": {"status": "normal", "desc": "Normal hair thickness and texture", "magnitude": 0},
        },
        "note": "Pleiotropic: thick hair, shovel-shaped incisors, increased sweat glands, facial features",
    },
    # Earwax Type
    "rs17822931": {
        "gene": "ABCC11",
        "category": "Earwax Type",
        "variants": {
            "GG": {
                "status": "wet",
                "desc": "Wet, sticky earwax - functional transporter, typical body odor",
                "magnitude": 0,
            },
            "GA": {"status": "wet", "desc": "Wet earwax - dominant trait", "magnitude": 0},
            "AG": {"status": "wet", "desc": "Wet earwax - dominant trait", "magnitude": 0},
            "AA": {
                "status": "dry",
                "desc": "Dry, flaky earwax - non-functional transporter, minimal body odor",
                "magnitude": 0,
            },
        },
        "note": "Pleiotropic: earwax type AND body odor (apocrine sweat lipid content). AA = natural deodorant",
    },
    # Male Pattern Baldness
    "rs6152": {
        "gene": "AR",
        "category": "Male Pattern Baldness",
        "variants": {
            "GG": {
                "status": "high_risk",
                "desc": "High risk - androgen receptor more sensitive to DHT",
                "magnitude": 2,
            },
            "GA": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "AG": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "AA": {"status": "lower_risk", "desc": "Lower risk of male pattern baldness", "magnitude": 0},
        },
        "note": "X-chromosome marker - males hemizygous. Age-dependent penetrance.",
    },
    "rs1160312": {
        "gene": "chromosome 20p11",
        "category": "Male Pattern Baldness",
        "variants": {
            "AA": {
                "status": "high_risk",
                "desc": "High risk - 1.6x increased risk, 7x when combined with AR risk",
                "magnitude": 2,
            },
            "AT": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "TA": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "TT": {"status": "lower_risk", "desc": "Lower risk", "magnitude": 0},
        },
        "note": "Autosomal locus - synergizes with AR (rs6152) for baldness risk",
    },
    # Stretch Marks
    "rs7787362": {
        "gene": "ELN",
        "category": "Stretch Marks",
        "variants": {
            "CC": {
                "status": "high_risk",
                "desc": "Higher risk - reduced elastin, less skin elasticity",
                "magnitude": 1,
            },
            "CT": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "TC": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 1},
            "TT": {"status": "lower_risk", "desc": "Lower risk - better elastic fiber formation", "magnitude": 0},
        },
        "note": "Elastin gene - affects skin's ability to stretch without tearing (striae distensae)",
    },
    # =========================================================================
    # SECTION E: FACIAL MORPHOLOGY
    # =========================================================================
    # Nose Shape
    "rs2045323": {
        "gene": "DCHS2",
        "category": "Nose Shape",
        "variants": {
            "AA": {
                "status": "upturned",
                "desc": "More upturned nasal tip - greater columella inclination",
                "magnitude": 0,
            },
            "AG": {"status": "intermediate", "desc": "Intermediate nasal tip angle", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate nasal tip angle", "magnitude": 0},
            "GG": {"status": "hooked", "desc": "More hooked/aquiline nose", "magnitude": 0},
        },
        "note": "DCHS2 regulates cartilage growth - affects nasal tip angle (celestial vs aquiline)",
    },
    "rs11170678": {
        "gene": "DCHS2",
        "category": "Nose Shape",
        "variants": {
            "CC": {"status": "pointed", "desc": "More pointed/sharp nasal tip", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate nasal tip definition", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate nasal tip definition", "magnitude": 0},
            "TT": {"status": "rounded", "desc": "More rounded nasal tip", "magnitude": 0},
        },
        "note": "DCHS2 - affects nasal tip sharpness/definition",
    },
    "rs1852985": {
        "gene": "RUNX2",
        "category": "Nose Shape",
        "variants": {
            "TT": {"status": "wide_bridge", "desc": "Wider nasal bridge - RUNX2 drives bone formation", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate nasal bridge width", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate nasal bridge width", "magnitude": 0},
            "CC": {"status": "narrow_bridge", "desc": "Narrower nasal bridge", "magnitude": 0},
        },
        "note": "RUNX2 master regulator of osteoblasts - affects bony nasal bridge width",
    },
    "rs11175967": {
        "gene": "PAX3",
        "category": "Nose Shape",
        "variants": {
            "AA": {"status": "high_bridge", "desc": "High, prominent nasal root/bridge", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate nasal bridge height", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate nasal bridge height", "magnitude": 0},
            "GG": {"status": "low_bridge", "desc": "Lower/flatter nasal root", "magnitude": 0},
        },
        "note": "PAX3 affects nasal root height at nasion (bridge between eyes)",
    },
    "rs17421627": {
        "gene": "PAX1",
        "category": "Nose Shape",
        "variants": {
            "TT": {"status": "wide_nostrils", "desc": "Wider nostril breadth (nasal alae)", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate nostril width", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate nostril width", "magnitude": 0},
            "CC": {"status": "narrow_nostrils", "desc": "Narrower nostrils", "magnitude": 0},
        },
        "note": "PAX1 controls nasal alae proliferation - shows climate adaptation signature",
    },
    # Chin/Jaw
    "rs6184": {
        "gene": "GHR",
        "category": "Chin/Jaw",
        "variants": {
            "AA": {
                "status": "prominent",
                "desc": "Prominent chin/prognathism - growth hormone receptor variant",
                "magnitude": 0,
            },
            "AC": {"status": "intermediate", "desc": "Intermediate chin projection", "magnitude": 0},
            "CA": {"status": "intermediate", "desc": "Intermediate chin projection", "magnitude": 0},
            "CC": {"status": "normal", "desc": "Normal chin projection", "magnitude": 0},
        },
        "note": "Growth hormone receptor - affects mandibular prognathism (lantern jaw)",
    },
    "rs6180": {
        "gene": "GHR",
        "category": "Chin/Jaw",
        "variants": {
            "AA": {"status": "prominent", "desc": "Prominent mandible", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GG": {"status": "normal", "desc": "Normal mandible", "magnitude": 0},
        },
        "note": "Additional GHR variant affecting jaw structure",
    },
    "rs6182": {
        "gene": "GHR",
        "category": "Chin/Jaw",
        "variants": {
            "AA": {"status": "prominent", "desc": "Prominent jaw", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GG": {"status": "normal", "desc": "Normal jaw", "magnitude": 0},
        },
        "note": "Additional GHR variant",
    },
    # Earlobes
    "rs2080401": {
        "gene": "GPR126",
        "category": "Earlobes",
        "variants": {
            "CC": {"status": "detached", "desc": "Free/detached earlobes - dominant-like effect", "magnitude": 0},
            "CT": {"status": "detached", "desc": "Free/detached earlobes", "magnitude": 0},
            "TC": {"status": "detached", "desc": "Free/detached earlobes", "magnitude": 0},
            "TT": {"status": "attached", "desc": "Attached earlobes", "magnitude": 0},
        },
        "note": "GPR126 involved in earlobe morphology - relevant for side profile",
    },
    # Unibrow
    "rs9852899": {
        "gene": "PAX3",
        "category": "Unibrow",
        "variants": {
            "TT": {
                "status": "likely",
                "desc": "Higher likelihood of synophrys (unibrow) - melanocytes migrate to nasal bridge",
                "magnitude": 0,
            },
            "TC": {"status": "moderate", "desc": "Moderate likelihood", "magnitude": 0},
            "CT": {"status": "moderate", "desc": "Moderate likelihood", "magnitude": 0},
            "CC": {"status": "unlikely", "desc": "Lower likelihood of unibrow", "magnitude": 0},
        },
        "note": "PAX3 controls neural crest cell migration - determines melanocyte distribution on forehead",
    },
    # Cleft Chin
    "rs2013162": {
        "gene": "near MYH16",
        "category": "Cleft Chin",
        "variants": {
            "AA": {"status": "likely", "desc": "Higher likelihood of cleft chin (chin dimple)", "magnitude": 0},
            "AG": {"status": "moderate", "desc": "Moderate likelihood", "magnitude": 0},
            "GA": {"status": "moderate", "desc": "Moderate likelihood", "magnitude": 0},
            "GG": {"status": "unlikely", "desc": "Lower likelihood of cleft chin", "magnitude": 0},
        },
        "note": "Threshold trait - related to fusion of mental protuberance",
    },
    # =========================================================================
    # SECTION F: ANTHROPOMETRICS
    # =========================================================================
    # Height - top SNPs (highly polygenic, these are strongest signals)
    "rs1042725": {
        "gene": "HMGA2",
        "category": "Height",
        "variants": {
            "CC": {"status": "taller", "desc": "Taller tendency - ~0.8cm effect for CC vs TT", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate height effect (~0.4cm)", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate height effect (~0.4cm)", "magnitude": 0},
            "TT": {"status": "shorter", "desc": "Shorter tendency", "magnitude": 0},
        },
        "note": "HMGA2 chromatin remodeling - strongest known common height variant",
    },
    "rs6060373": {
        "gene": "GDF5",
        "category": "Height",
        "variants": {
            "GG": {
                "status": "shorter",
                "desc": "Shorter tendency - GDF5 affects cartilage in limb joints",
                "magnitude": 1,
            },
            "GA": {"status": "intermediate", "desc": "Intermediate (~0.19cm effect)", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate (~0.19cm effect)", "magnitude": 0},
            "AA": {"status": "taller", "desc": "Taller tendency (~0.37cm for AA vs GG)", "magnitude": 0},
        },
        "note": "Growth differentiation factor 5 - joint cartilage development",
    },
    "rs6440003": {
        "gene": "ZBTB38",
        "category": "Height",
        "variants": {
            "AA": {"status": "taller", "desc": "Taller tendency (~0.44cm effect)", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Intermediate height", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate height", "magnitude": 0},
            "GG": {"status": "shorter", "desc": "Shorter tendency", "magnitude": 0},
        },
        "note": "Zinc finger transcriptional repressor - skeletal growth regulation",
    },
    "rs16896068": {
        "gene": "LCORL",
        "category": "Height",
        "variants": {
            "AA": {"status": "taller", "desc": "Taller tendency (~0.28cm effect)", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GG": {"status": "shorter", "desc": "Shorter tendency", "magnitude": 0},
        },
        "note": "Ligand dependent nuclear receptor corepressor - skeletal length",
    },
    "rs2282978": {
        "gene": "CDK6",
        "category": "Height",
        "variants": {
            "CC": {"status": "taller", "desc": "Taller tendency (~0.31cm effect)", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "TT": {"status": "shorter", "desc": "Shorter tendency", "magnitude": 0},
        },
        "note": "Cell cycle regulator - replication timing affects growth",
    },
    "rs64399": {
        "gene": "HHIP",
        "category": "Height",
        "variants": {
            "GG": {"status": "shorter", "desc": "Shorter tendency - HHIP regulates bone formation", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "AA": {"status": "taller", "desc": "Taller tendency (~0.30cm)", "magnitude": 0},
        },
        "note": "Hedgehog interacting protein - bone formation regulator",
    },
    # BMI/Weight (rs9939609 FTO already in comprehensive_snp_database)
    "rs1421085": {
        "gene": "FTO",
        "category": "BMI/Weight",
        "variants": {
            "TT": {
                "status": "obesity_risk",
                "desc": "Higher BMI risk - FTO variant, similar effect to rs9939609",
                "magnitude": 2,
            },
            "TC": {"status": "moderate_risk", "desc": "Moderate BMI risk", "magnitude": 1},
            "CT": {"status": "moderate_risk", "desc": "Moderate BMI risk", "magnitude": 1},
            "CC": {"status": "lower_risk", "desc": "Lower BMI risk", "magnitude": 0},
        },
        "note": "FTO intron variant (proxy for rs9939609) - affects hypothalamic satiety",
    },
    "rs17782313": {
        "gene": "MC4R",
        "category": "BMI/Weight",
        "variants": {
            "CC": {"status": "obesity_risk", "desc": "Higher BMI risk - MC4R appetite dysregulation", "magnitude": 2},
            "CT": {"status": "moderate_risk", "desc": "Moderate BMI risk", "magnitude": 1},
            "TC": {"status": "moderate_risk", "desc": "Moderate BMI risk", "magnitude": 1},
            "TT": {"status": "lower_risk", "desc": "Lower BMI risk", "magnitude": 0},
        },
        "note": "Melanocortin 4 receptor - controls energy balance and appetite",
    },
    # Finger Length Ratio (2D:4D)
    "rs314277": {
        "gene": "LIN28B",
        "category": "Finger Ratio",
        "variants": {
            "AA": {
                "status": "higher_ratio",
                "desc": "Higher 2D:4D ratio (longer index) - lower prenatal testosterone",
                "magnitude": 0,
            },
            "AG": {"status": "intermediate", "desc": "Intermediate 2D:4D ratio", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate 2D:4D ratio", "magnitude": 0},
            "GG": {
                "status": "lower_ratio",
                "desc": "Lower 2D:4D ratio (longer ring) - higher prenatal testosterone",
                "magnitude": 0,
            },
        },
        "note": "Biomarker for prenatal androgen exposure - correlates with spatial ability, athletic potential",
    },
    # =========================================================================
    # SECTION G: NEUROLOGICAL / BEHAVIORAL
    # =========================================================================
    # Photic Sneeze (ACHOO Syndrome)
    "rs10427255": {
        "gene": "ZEB2",
        "category": "Photic Sneeze",
        "variants": {
            "CC": {
                "status": "likely",
                "desc": "Photic sneeze reflex likely - sneezes from bright light (ACHOO syndrome)",
                "magnitude": 1,
            },
            "CT": {"status": "moderate", "desc": "Moderate likelihood of photic sneeze", "magnitude": 0},
            "TC": {"status": "moderate", "desc": "Moderate likelihood of photic sneeze", "magnitude": 0},
            "TT": {"status": "unlikely", "desc": "Unlikely to have photic sneeze reflex", "magnitude": 0},
        },
        "note": "Optic-trigeminal summation - light stimulus triggers sneeze reflex",
    },
    # Misophonia
    "rs1868790": {
        "gene": "TENM2",
        "category": "Misophonia",
        "variants": {
            "AA": {
                "status": "high_risk",
                "desc": "Higher risk of misophonia - rage at repetitive sounds (chewing, breathing)",
                "magnitude": 1,
            },
            "AG": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 0},
            "GA": {"status": "moderate_risk", "desc": "Moderate risk", "magnitude": 0},
            "GG": {"status": "lower_risk", "desc": "Lower risk of misophonia", "magnitude": 0},
        },
        "note": "TENM2 axon guidance - altered auditory cortex-limbic connectivity (sensory gating failure)",
    },
    # Motion Sickness
    "rs3758987": {
        "gene": "near PVRL3",
        "category": "Motion Sickness",
        "variants": {
            "CC": {"status": "susceptible", "desc": "Higher motion sickness susceptibility", "magnitude": 1},
            "CT": {"status": "moderate", "desc": "Moderate susceptibility", "magnitude": 0},
            "TC": {"status": "moderate", "desc": "Moderate susceptibility", "magnitude": 0},
            "TT": {"status": "resistant", "desc": "Lower susceptibility to motion sickness", "magnitude": 0},
        },
        "note": "Inner ear vestibular system development - ~70% heritability",
    },
    "rs1800544": {
        "gene": "ADRA2A",
        "category": "Motion Sickness",
        "variants": {
            "GG": {
                "status": "susceptible",
                "desc": "High motion sickness susceptibility - nausea and vomiting during motion",
                "magnitude": 2,
            },
            "GC": {"status": "moderate", "desc": "Moderate susceptibility", "magnitude": 1},
            "CG": {"status": "moderate", "desc": "Moderate susceptibility", "magnitude": 1},
            "CC": {"status": "resistant", "desc": "Lower susceptibility", "magnitude": 0},
        },
        "note": "Alpha-2A adrenergic receptor - sympathetic nervous system response to vestibular conflict",
    },
    # Perfect Pitch
    "rs3057": {
        "gene": "ASAP1",
        "category": "Perfect Pitch",
        "variants": {
            "CT": {
                "status": "potential",
                "desc": "Genetic potential for absolute pitch (requires early musical training ages 3-6)",
                "magnitude": 1,
            },
            "TC": {
                "status": "potential",
                "desc": "Genetic potential for absolute pitch (requires early musical training ages 3-6)",
                "magnitude": 1,
            },
            "CC": {"status": "lower_potential", "desc": "Lower genetic potential for absolute pitch", "magnitude": 0},
            "TT": {"status": "lower_potential", "desc": "Lower genetic potential for absolute pitch", "magnitude": 0},
        },
        "note": "Nature via nurture - genetic predisposition + critical period training required",
    },
    # Mosquito Attractiveness
    "rs5750339": {
        "gene": "HLA region",
        "category": "Mosquito Attractiveness",
        "variants": {
            "AA": {"status": "more_attractive", "desc": "May be more attractive to mosquitoes", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Intermediate mosquito attraction", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate mosquito attraction", "magnitude": 0},
            "GG": {"status": "less_attractive", "desc": "May be less attractive to mosquitoes", "magnitude": 0},
        },
        "note": "HLA affects skin microbiome → volatile compounds. Trait is 67% heritable, highly polygenic.",
    },
    "rs11751172": {
        "gene": "unknown",
        "category": "Mosquito Attractiveness",
        "variants": {
            "AA": {"status": "more_attractive", "desc": "Higher mosquito attraction", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate", "magnitude": 0},
            "GG": {"status": "less_attractive", "desc": "Lower mosquito attraction", "magnitude": 0},
        },
        "note": "Full model uses 285+ markers - these are top signals",
    },
    # =========================================================================
    # SECTION H: BLOOD TYPE
    # Note: Requires two-step derivation logic, not simple lookup
    # =========================================================================
    "rs8176719": {
        "gene": "ABO",
        "category": "Blood Type",
        "variants": {
            "DD": {
                "status": "O_deletion",
                "desc": "Type O - frameshift deletion, no functional transferase",
                "magnitude": 0,
            },
            "DI": {
                "status": "one_functional",
                "desc": "One functional ABO allele (A or B determined by rs8176746)",
                "magnitude": 0,
            },
            "ID": {
                "status": "one_functional",
                "desc": "One functional ABO allele (A or B determined by rs8176746)",
                "magnitude": 0,
            },
            "II": {
                "status": "both_functional",
                "desc": "Both alleles functional (A, B, or AB determined by rs8176746)",
                "magnitude": 0,
            },
            # Alternative notations
            "--": {"status": "O_deletion", "desc": "Type O (alternative notation)", "magnitude": 0},
            "-I": {"status": "one_functional", "desc": "One functional allele", "magnitude": 0},
            "I-": {"status": "one_functional", "desc": "One functional allele", "magnitude": 0},
            "GG": {
                "status": "both_functional",
                "desc": "Both alleles functional (alternative notation)",
                "magnitude": 0,
            },
            "G-": {"status": "one_functional", "desc": "One functional allele (alternative notation)", "magnitude": 0},
            "-G": {"status": "one_functional", "desc": "One functional allele (alternative notation)", "magnitude": 0},
        },
        "note": "Step 1 of blood type derivation - checks for O deletion. Multiple notations possible for indels.",
    },
    "rs8176746": {
        "gene": "ABO",
        "category": "Blood Type",
        "variants": {
            "GG": {"status": "type_A", "desc": "Type A transferase (adds N-acetylgalactosamine)", "magnitude": 0},
            "GT": {
                "status": "type_AB_or_A_B",
                "desc": "A/B heterozygous - Type AB if both functional, A or B if one O",
                "magnitude": 0,
            },
            "TG": {
                "status": "type_AB_or_A_B",
                "desc": "A/B heterozygous - Type AB if both functional, A or B if one O",
                "magnitude": 0,
            },
            "TT": {"status": "type_B", "desc": "Type B transferase (adds galactose)", "magnitude": 0},
        },
        "note": "Step 2 of blood type derivation - determines A vs B. Only interpret if rs8176719 shows functional alleles.",
    },
    # =========================================================================
    # SECTION I: VISION / REFRACTIVE ERRORS
    # =========================================================================
    # Myopia
    "rs524952": {
        "gene": "GJD2",
        "category": "Myopia",
        "variants": {
            "AA": {
                "status": "myopia_risk",
                "desc": "Higher myopia (nearsightedness) risk - longer axial eye length",
                "magnitude": 2,
            },
            "AT": {"status": "moderate_risk", "desc": "Moderate myopia risk", "magnitude": 1},
            "TA": {"status": "moderate_risk", "desc": "Moderate myopia risk", "magnitude": 1},
            "TT": {
                "status": "hyperopia_tendency",
                "desc": "Lower myopia risk / hyperopia (farsightedness) tendency",
                "magnitude": 0,
            },
        },
        "note": "Connexin-36 affects axial eye length. TT associated with shorter axial length (hyperopia direction).",
    },
    "rs8027411": {
        "gene": "RASGRF1",
        "category": "Myopia",
        "variants": {
            "TT": {
                "status": "high_myopia_risk",
                "desc": "High myopia risk - strong association with severe nearsightedness",
                "magnitude": 2,
            },
            "TG": {"status": "moderate_risk", "desc": "Moderate myopia risk", "magnitude": 1},
            "GT": {"status": "moderate_risk", "desc": "Moderate myopia risk", "magnitude": 1},
            "GG": {"status": "lower_risk", "desc": "Lower myopia risk", "magnitude": 0},
        },
        "note": "RASGRF1 - associated with high myopia in multiple GWAS",
    },
    # Astigmatism
    "rs7677751": {
        "gene": "PDGFRA",
        "category": "Astigmatism",
        "variants": {
            "TT": {"status": "higher_risk", "desc": "Higher astigmatism risk - 1.26x increased odds", "magnitude": 1},
            "TC": {"status": "moderate_risk", "desc": "Moderate astigmatism risk", "magnitude": 1},
            "CT": {"status": "moderate_risk", "desc": "Moderate astigmatism risk", "magnitude": 1},
            "CC": {"status": "lower_risk", "desc": "Lower astigmatism risk", "magnitude": 0},
        },
        "note": "PDGFRA lead SNP from GWAS meta-analysis - regulates corneal tissue growth",
    },
    "rs3771395": {
        "gene": "VAX2",
        "category": "Astigmatism",
        "variants": {
            "AA": {"status": "risk", "desc": "Astigmatism risk - VAX2 affects dorsoventral eye axis", "magnitude": 1},
            "AG": {"status": "moderate", "desc": "Moderate risk", "magnitude": 0},
            "GA": {"status": "moderate", "desc": "Moderate risk", "magnitude": 0},
            "GG": {"status": "lower_risk", "desc": "Lower risk", "magnitude": 0},
        },
        "note": "VAX2 dorsoventral eye axis development - gradient in astigmatism along vertical plane",
    },
    # Age-Related Macular Degeneration (AMD)
    "rs1061170": {
        "gene": "CFH",
        "category": "AMD Risk",
        "variants": {
            "CC": {
                "status": "high_risk",
                "desc": "High AMD risk - 7.4x increased risk, His402 impairs complement regulation",
                "magnitude": 3,
            },
            "CT": {"status": "moderate_risk", "desc": "Moderate AMD risk (~3x)", "magnitude": 2},
            "TC": {"status": "moderate_risk", "desc": "Moderate AMD risk (~3x)", "magnitude": 2},
            "TT": {
                "status": "protective",
                "desc": "Protective - Tyr402, normal complement factor H function",
                "magnitude": 0,
            },
        },
        "note": "Complement Factor H - alters binding to C-reactive protein, leads to retinal inflammation (drusen)",
    },
    "rs10490924": {
        "gene": "ARMS2",
        "category": "AMD Risk",
        "variants": {
            "TT": {"status": "high_risk", "desc": "High AMD risk - independent risk factor", "magnitude": 2},
            "TG": {"status": "moderate_risk", "desc": "Moderate AMD risk", "magnitude": 1},
            "GT": {"status": "moderate_risk", "desc": "Moderate AMD risk", "magnitude": 1},
            "GG": {"status": "lower_risk", "desc": "Lower AMD risk", "magnitude": 0},
        },
        "note": "ARMS2 (age-related maculopathy susceptibility 2) - strong independent AMD risk",
    },
    # Glaucoma
    "rs4656461": {
        "gene": "TMCO1",
        "category": "Glaucoma Risk",
        "variants": {
            "GG": {
                "status": "high_risk",
                "desc": "Higher glaucoma risk - elevated intraocular pressure (IOP)",
                "magnitude": 2,
            },
            "GA": {"status": "moderate_risk", "desc": "Moderate glaucoma risk", "magnitude": 1},
            "AG": {"status": "moderate_risk", "desc": "Moderate glaucoma risk", "magnitude": 1},
            "AA": {"status": "lower_risk", "desc": "Lower glaucoma risk", "magnitude": 0},
        },
        "note": "Near TMCO1 - associated with primary open-angle glaucoma (POAG) and elevated IOP",
    },
}


# Eye color MLR coefficients for probability prediction
# Based on IrisPlex 6-SNP model (Walsh et al. 2011, Liu et al. 2009).
# Brown is the reference category (logit=0). Positive betas push toward blue/intermediate.
# Effect alleles are the LIGHT alleles on the 23andMe + strand (GRCh37).
# Intercepts are negative so that with no light alleles, brown is predicted (~85%).
EYE_COLOR_MLR: dict[str, dict[str, Any]] = {
    "intercept": {"blue": -4.07, "inter": -1.83},
    "rs12913832": {"allele": "G", "blue": 3.94, "inter": 1.18},  # HERC2 master switch (~74% variance)
    "rs1800407": {"allele": "A", "blue": 0.87, "inter": 0.72},  # OCA2 Arg419Gln
    "rs16891982": {"allele": "G", "blue": 0.65, "inter": 0.38},  # SLC45A2 L374F (G=derived/light)
    "rs1393350": {"allele": "A", "blue": 0.36, "inter": 0.21},  # TYR (A=reduced activity/light)
    "rs12896399": {"allele": "T", "blue": 0.19, "inter": 0.14},  # SLC24A4
    "rs12203592": {"allele": "T", "blue": 0.12, "inter": 0.08},  # IRF4
}
