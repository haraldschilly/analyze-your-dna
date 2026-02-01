#!/usr/bin/env python3
"""
Comprehensive Genome Analyzer
Cross-references personal genome against ClinVar, PharmGKB, and curated high-impact SNPs.
"""

import csv
import json
import gzip
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

@dataclass
class SNPInfo:
    rsid: str
    chromosome: str
    position: str
    genotype: str
    category: str = ""
    significance: str = ""
    description: str = ""
    recommendation: str = ""
    source: str = ""
    magnitude: int = 0

# =============================================================================
# CURATED HIGH-IMPACT SNPS DATABASE
# These are the most actionable, well-researched SNPs with clear implications
# =============================================================================

CURATED_SNPS = {
    # =========================================================================
    # PHARMACOGENOMICS - Drug Response (Critical for medication safety)
    # =========================================================================

    # CYP2D6 - Metabolizes ~25% of all drugs
    "rs3892097": {
        "gene": "CYP2D6",
        "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal CYP2D6 metabolizer", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate CYP2D6 metabolizer - may need dose adjustments for codeine, tramadol, tamoxifen, many antidepressants", "magnitude": 3},
            "AA": {"status": "poor", "desc": "Poor CYP2D6 metabolizer (*4/*4) - codeine ineffective, risk of adverse effects with standard doses of many drugs", "magnitude": 4},
        }
    },
    "rs1065852": {
        "gene": "CYP2D6",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2D6 function", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Reduced CYP2D6 function", "magnitude": 2},
            "TT": {"status": "poor", "desc": "Poor CYP2D6 metabolizer (*10) - common in Asian populations", "magnitude": 3},
        }
    },

    # CYP2C19 - PPIs, clopidogrel, antidepressants
    "rs4244285": {
        "gene": "CYP2C19",
        "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal CYP2C19 metabolizer", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate CYP2C19 metabolizer (*1/*2) - clopidogrel may be less effective", "magnitude": 3},
            "AA": {"status": "poor", "desc": "Poor CYP2C19 metabolizer (*2/*2) - clopidogrel significantly less effective, consider alternative antiplatelet", "magnitude": 4},
        }
    },
    "rs12248560": {
        "gene": "CYP2C19",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2C19 metabolizer", "magnitude": 0},
            "CT": {"status": "rapid", "desc": "Rapid CYP2C19 metabolizer (*17) - may need higher doses of PPIs, some antidepressants", "magnitude": 2},
            "TT": {"status": "ultrarapid", "desc": "Ultrarapid CYP2C19 metabolizer (*17/*17) - drugs metabolized faster, may need dose increases", "magnitude": 3},
        }
    },

    # CYP2C9 - Warfarin, NSAIDs
    "rs1799853": {
        "gene": "CYP2C9",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2C9 metabolizer", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate CYP2C9 metabolizer (*2) - warfarin dose reduction recommended", "magnitude": 3},
            "TT": {"status": "poor", "desc": "Poor CYP2C9 metabolizer (*2/*2) - significant warfarin dose reduction needed", "magnitude": 4},
        }
    },
    "rs1057910": {
        "gene": "CYP2C9",
        "category": "Drug Metabolism",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal CYP2C9 metabolizer", "magnitude": 0},
            "AC": {"status": "intermediate", "desc": "Intermediate CYP2C9 metabolizer (*3) - warfarin dose reduction recommended", "magnitude": 3},
            "CC": {"status": "poor", "desc": "Poor CYP2C9 metabolizer (*3/*3) - significant warfarin dose reduction, increased bleeding risk", "magnitude": 4},
        }
    },

    # CYP1A2 - Caffeine
    "rs762551": {
        "gene": "CYP1A2",
        "category": "Drug Metabolism",
        "variants": {
            "AA": {"status": "fast", "desc": "Fast caffeine metabolizer - can tolerate caffeine well", "magnitude": 1},
            "AC": {"status": "intermediate", "desc": "Intermediate caffeine metabolizer - moderate caffeine clearance", "magnitude": 2},
            "CC": {"status": "slow", "desc": "Slow caffeine metabolizer - caffeine lingers longer, higher cardiovascular risk with high intake", "magnitude": 3},
        }
    },

    # CYP3A4/5 - Metabolizes ~50% of drugs
    "rs776746": {
        "gene": "CYP3A5",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "non-expressor", "desc": "CYP3A5 non-expressor (*3/*3) - most common in Caucasians, affects tacrolimus dosing", "magnitude": 2},
            "CT": {"status": "intermediate", "desc": "CYP3A5 intermediate expressor", "magnitude": 1},
            "TT": {"status": "expressor", "desc": "CYP3A5 expressor - may need higher tacrolimus doses", "magnitude": 2},
        }
    },

    # VKORC1 - Warfarin sensitivity
    "rs9923231": {
        "gene": "VKORC1",
        "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal warfarin sensitivity", "magnitude": 0},
            "GA": {"status": "sensitive", "desc": "Increased warfarin sensitivity - lower doses needed", "magnitude": 3},
            "AA": {"status": "highly_sensitive", "desc": "Highly sensitive to warfarin - significantly lower doses required", "magnitude": 4},
        }
    },

    # SLCO1B1 - Statin myopathy
    "rs4149056": {
        "gene": "SLCO1B1",
        "category": "Drug Metabolism",
        "variants": {
            "TT": {"status": "normal", "desc": "Normal statin metabolism", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate statin transporter - 4x increased myopathy risk with simvastatin", "magnitude": 3},
            "CC": {"status": "poor", "desc": "Poor statin transporter - 17x increased myopathy risk with simvastatin, consider alternative statin", "magnitude": 4},
        }
    },

    # DPYD - Fluoropyrimidine toxicity (5-FU, capecitabine)
    "rs3918290": {
        "gene": "DPYD",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal DPYD function", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Reduced DPYD function - 50% dose reduction for 5-FU/capecitabine", "magnitude": 5},
            "TT": {"status": "deficient", "desc": "DPYD deficient - 5-FU/capecitabine contraindicated, can be fatal", "magnitude": 6},
        }
    },

    # TPMT - Thiopurine toxicity (azathioprine, 6-MP)
    "rs1800460": {
        "gene": "TPMT",
        "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal TPMT activity", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate TPMT activity - thiopurine dose reduction recommended", "magnitude": 4},
            "TT": {"status": "poor", "desc": "Poor TPMT activity - thiopurines can cause severe myelosuppression", "magnitude": 5},
        }
    },

    # HLA-B*5701 - Abacavir hypersensitivity
    "rs2395029": {
        "gene": "HLA-B",
        "category": "Drug Metabolism",
        "variants": {
            "TT": {"status": "normal", "desc": "Low risk of abacavir hypersensitivity", "magnitude": 0},
            "TG": {"status": "carrier", "desc": "HLA-B*5701 carrier - abacavir contraindicated, risk of severe hypersensitivity", "magnitude": 5},
            "GG": {"status": "positive", "desc": "HLA-B*5701 positive - abacavir contraindicated", "magnitude": 5},
        }
    },

    # =========================================================================
    # METHYLATION & DETOXIFICATION
    # =========================================================================

    # MTHFR - Methylation
    "rs1801133": {
        "gene": "MTHFR",
        "category": "Methylation",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal MTHFR function (C677C)", "magnitude": 0},
            "AG": {"status": "reduced", "desc": "Reduced MTHFR function (C677T heterozygous) - ~35% reduced activity", "magnitude": 2},
            "AA": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR (C677T homozygous) - ~70% reduced activity, consider methylfolate", "magnitude": 3},
        }
    },
    "rs1801131": {
        "gene": "MTHFR",
        "category": "Methylation",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal MTHFR A1298C function", "magnitude": 0},
            "AC": {"status": "reduced", "desc": "Reduced MTHFR A1298C function (heterozygous)", "magnitude": 1},
            "CC": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR A1298C function (homozygous)", "magnitude": 2},
            # 23andMe reports on opposite strand
            "TT": {"status": "normal", "desc": "Normal MTHFR A1298C function", "magnitude": 0},
            "TG": {"status": "reduced", "desc": "Reduced MTHFR A1298C function (heterozygous)", "magnitude": 1},
            "GG": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR A1298C function (homozygous)", "magnitude": 2},
        }
    },

    # COMT - Catecholamine metabolism
    "rs4680": {
        "gene": "COMT",
        "category": "Neurotransmitters",
        "variants": {
            "GG": {"status": "fast", "desc": "Fast COMT (Val/Val) - clears dopamine/norepinephrine quickly, better stress resilience but lower baseline dopamine", "magnitude": 2},
            "AG": {"status": "intermediate", "desc": "Intermediate COMT (Val/Met) - balanced catecholamine metabolism", "magnitude": 1},
            "AA": {"status": "slow", "desc": "Slow COMT (Met/Met) - higher baseline dopamine, better cognitive performance but more stress-sensitive, stimulants hit harder", "magnitude": 3},
        }
    },

    # NAT2 - Acetylation
    "rs1801280": {
        "gene": "NAT2",
        "category": "Detoxification",
        "variants": {
            "TT": {"status": "fast", "desc": "Fast NAT2 acetylator", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate NAT2 acetylator", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate NAT2 acetylator", "magnitude": 1},
            "CC": {"status": "slow", "desc": "Slow NAT2 acetylator - increased sensitivity to certain drugs and chemicals", "magnitude": 2},
        }
    },
    "rs1799930": {
        "gene": "NAT2",
        "category": "Detoxification",
        "variants": {
            "GG": {"status": "fast", "desc": "Fast NAT2 acetylator at this locus", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate NAT2 acetylator", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Intermediate NAT2 acetylator", "magnitude": 1},
            "AA": {"status": "slow", "desc": "Slow NAT2 acetylator at this locus", "magnitude": 2},
        }
    },

    # GSTP1 - Glutathione conjugation
    "rs1695": {
        "gene": "GSTP1",
        "category": "Detoxification",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal GSTP1 function (Ile105)", "magnitude": 0},
            "AG": {"status": "reduced", "desc": "Reduced GSTP1 function (Ile/Val) - may have reduced detox capacity", "magnitude": 1},
            "GG": {"status": "significantly_reduced", "desc": "Significantly reduced GSTP1 (Val/Val) - reduced glutathione conjugation", "magnitude": 2},
        }
    },

    # =========================================================================
    # ADENOSINE & CAFFEINE RESPONSE
    # =========================================================================

    "rs5751876": {
        "gene": "ADORA2A",
        "category": "Caffeine Response",
        "variants": {
            "CC": {"status": "lower_sensitivity", "desc": "Lower caffeine sensitivity - less likely to have caffeine-induced anxiety", "magnitude": 1},
            "CT": {"status": "normal", "desc": "Normal caffeine sensitivity", "magnitude": 0},
            "TT": {"status": "high_sensitivity", "desc": "High caffeine sensitivity - more prone to caffeine-induced anxiety and sleep disruption", "magnitude": 2},
        }
    },
    "rs2298383": {
        "gene": "ADORA2A",
        "category": "Caffeine Response",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal anxiety response to caffeine", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate anxiety response to caffeine", "magnitude": 1},
            "TT": {"status": "anxiety_prone", "desc": "Increased anxiety response to caffeine", "magnitude": 2},
        }
    },

    # =========================================================================
    # CARDIOVASCULAR
    # =========================================================================

    # APOE - Cardiovascular and Alzheimer's risk
    "rs429358": {
        "gene": "APOE",
        "category": "Cardiovascular/Neuro",
        "note": "Combine with rs7412 to determine APOE type",
        "variants": {
            "TT": {"status": "e2_or_e3", "desc": "APOE component - combine with rs7412 for full genotype", "magnitude": 0},
            "TC": {"status": "e4_carrier", "desc": "APOE e4 carrier (one copy) - increased cardiovascular and Alzheimer's risk", "magnitude": 3},
            "CT": {"status": "e4_carrier", "desc": "APOE e4 carrier (one copy) - increased cardiovascular and Alzheimer's risk", "magnitude": 3},
            "CC": {"status": "e4_homozygous", "desc": "APOE e4/e4 - significantly increased Alzheimer's risk (10-15x)", "magnitude": 5},
        }
    },
    "rs7412": {
        "gene": "APOE",
        "category": "Cardiovascular/Neuro",
        "note": "Combine with rs429358 to determine APOE type",
        "variants": {
            "CC": {"status": "e3_or_e4", "desc": "APOE component - combine with rs429358", "magnitude": 0},
            "CT": {"status": "e2_carrier", "desc": "APOE e2 carrier - may be protective against Alzheimer's", "magnitude": 1},
            "TT": {"status": "e2_homozygous", "desc": "APOE e2/e2 - protective against Alzheimer's but increased Type III hyperlipoproteinemia risk", "magnitude": 2},
        }
    },

    # Factor V Leiden
    "rs6025": {
        "gene": "F5",
        "category": "Blood Clotting",
        "variants": {
            "CC": {"status": "normal", "desc": "No Factor V Leiden mutation", "magnitude": 0},
            "CT": {"status": "heterozygous", "desc": "Factor V Leiden heterozygous - 5-10x increased blood clot risk, avoid estrogen-containing contraceptives", "magnitude": 4},
            "TT": {"status": "homozygous", "desc": "Factor V Leiden homozygous - 50-100x increased blood clot risk", "magnitude": 5},
        }
    },

    # Prothrombin mutation
    "rs1799963": {
        "gene": "F2",
        "category": "Blood Clotting",
        "variants": {
            "GG": {"status": "normal", "desc": "No prothrombin mutation", "magnitude": 0},
            "GA": {"status": "heterozygous", "desc": "Prothrombin G20210A heterozygous - 3x increased blood clot risk", "magnitude": 3},
            "AA": {"status": "homozygous", "desc": "Prothrombin G20210A homozygous - significantly increased blood clot risk", "magnitude": 4},
        }
    },

    # =========================================================================
    # NUTRITION & METABOLISM
    # =========================================================================

    # Lactose intolerance
    "rs4988235": {
        "gene": "MCM6/LCT",
        "category": "Nutrition",
        "variants": {
            "AA": {"status": "lactose_intolerant", "desc": "Lactose intolerant - lactase non-persistence in adulthood", "magnitude": 2},
            "AG": {"status": "likely_tolerant", "desc": "Likely lactose tolerant", "magnitude": 0},
            "GA": {"status": "likely_tolerant", "desc": "Likely lactose tolerant", "magnitude": 0},
            "GG": {"status": "lactose_tolerant", "desc": "Lactose tolerant - lactase persistence", "magnitude": 0},
        }
    },

    # Celiac disease risk
    "rs2187668": {
        "gene": "HLA-DQA1",
        "category": "Autoimmune",
        "variants": {
            "CC": {"status": "low_risk", "desc": "Lower celiac disease risk", "magnitude": 0},
            "CT": {"status": "increased_risk", "desc": "Increased celiac disease risk (HLA-DQ2.5)", "magnitude": 2},
            "TT": {"status": "high_risk", "desc": "High celiac disease risk (HLA-DQ2.5 homozygous)", "magnitude": 3},
        }
    },

    # Vitamin D metabolism
    "rs2282679": {
        "gene": "GC",
        "category": "Nutrition",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal vitamin D binding protein", "magnitude": 0},
            "GT": {"status": "reduced", "desc": "Reduced vitamin D levels - may need more sun/supplementation", "magnitude": 1},
            "TG": {"status": "reduced", "desc": "Reduced vitamin D levels - may need more sun/supplementation", "magnitude": 1},
            "TT": {"status": "low", "desc": "Likely lower vitamin D levels - supplementation often needed", "magnitude": 2},
        }
    },

    # FTO - Obesity risk
    "rs9939609": {
        "gene": "FTO",
        "category": "Metabolism",
        "variants": {
            "TT": {"status": "normal", "desc": "Normal obesity risk from FTO", "magnitude": 0},
            "TA": {"status": "increased", "desc": "Slightly increased obesity risk - 1.3x per A allele", "magnitude": 1},
            "AT": {"status": "increased", "desc": "Slightly increased obesity risk - 1.3x per A allele", "magnitude": 1},
            "AA": {"status": "elevated", "desc": "Elevated obesity risk from FTO - 1.7x, may benefit from high-protein diet", "magnitude": 2},
        }
    },

    # =========================================================================
    # DISEASE RISK - High Impact
    # =========================================================================

    # BRCA1
    "rs80357906": {
        "gene": "BRCA1",
        "category": "Cancer Risk",
        "variants": {
            "GG": {"status": "normal", "desc": "No 5382insC BRCA1 mutation", "magnitude": 0},
            "G-": {"status": "carrier", "desc": "BRCA1 5382insC carrier - significantly increased breast/ovarian cancer risk", "magnitude": 6},
            "--": {"status": "homozygous", "desc": "BRCA1 5382insC mutation", "magnitude": 6},
        }
    },

    # Hereditary hemochromatosis
    "rs1800562": {
        "gene": "HFE",
        "category": "Iron Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "No C282Y HFE mutation", "magnitude": 0},
            "GA": {"status": "carrier", "desc": "HFE C282Y carrier - monitor iron levels", "magnitude": 2},
            "AG": {"status": "carrier", "desc": "HFE C282Y carrier - monitor iron levels", "magnitude": 2},
            "AA": {"status": "at_risk", "desc": "HFE C282Y homozygous - hereditary hemochromatosis risk, regular iron monitoring recommended", "magnitude": 4},
        }
    },
    "rs1799945": {
        "gene": "HFE",
        "category": "Iron Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "No H63D HFE mutation", "magnitude": 0},
            "CG": {"status": "carrier", "desc": "HFE H63D carrier - mild iron accumulation possible", "magnitude": 1},
            "GC": {"status": "carrier", "desc": "HFE H63D carrier - mild iron accumulation possible", "magnitude": 1},
            "GG": {"status": "homozygous", "desc": "HFE H63D homozygous - may have elevated iron, especially if combined with C282Y", "magnitude": 2},
        }
    },

    # Alpha-1 antitrypsin deficiency
    "rs28929474": {
        "gene": "SERPINA1",
        "category": "Lung/Liver",
        "variants": {
            "CC": {"status": "normal", "desc": "No Pi*Z mutation", "magnitude": 0},
            "CT": {"status": "carrier", "desc": "Alpha-1 antitrypsin Pi*Z carrier - avoid smoking, monitor lung function", "magnitude": 3},
            "TT": {"status": "deficient", "desc": "Alpha-1 antitrypsin deficiency (Pi*ZZ) - significantly increased COPD/liver disease risk", "magnitude": 5},
        }
    },

    # G6PD deficiency markers
    "rs1050828": {
        "gene": "G6PD",
        "category": "Drug Safety",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal G6PD function", "magnitude": 0},
            "CT": {"status": "carrier_female", "desc": "G6PD A- carrier (female) - some antimalarials and sulfa drugs may cause hemolysis", "magnitude": 3},
            "TT": {"status": "deficient", "desc": "G6PD deficient - avoid primaquine, sulfa drugs, fava beans", "magnitude": 4},
        }
    },
}


def load_genome(genome_path: Path) -> dict:
    """Load 23andMe genome file into a dictionary."""
    genome = {}
    with open(genome_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
                if genotype != '--':  # Skip no-calls
                    genome[rsid] = {
                        'chromosome': chrom,
                        'position': pos,
                        'genotype': genotype
                    }
    return genome


def load_clinvar(clinvar_path: Path) -> dict:
    """Load ClinVar pathogenic variants."""
    clinvar = {}
    with open(clinvar_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Focus on pathogenic/likely pathogenic variants
            if row.get('pathogenic') == '1' or row.get('likely_pathogenic') == '1':
                chrom = row.get('chrom', '')
                pos = row.get('pos', '')
                key = f"chr{chrom}:{pos}"
                clinvar[key] = {
                    'gene': row.get('symbol', ''),
                    'significance': row.get('clinical_significance', ''),
                    'traits': row.get('all_traits', ''),
                    'review_status': row.get('review_status', ''),
                    'gold_stars': row.get('gold_stars', '0'),
                }
    return clinvar


def load_pharmgkb(annotations_path: Path, alleles_path: Path) -> dict:
    """Load PharmGKB drug-gene annotations."""
    pharmgkb = {}

    # Load main annotations
    annotations = {}
    with open(annotations_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            ann_id = row.get('Clinical Annotation ID', '')
            variant = row.get('Variant/Haplotypes', '')
            if variant.startswith('rs'):
                annotations[ann_id] = {
                    'rsid': variant,
                    'gene': row.get('Gene', ''),
                    'drugs': row.get('Drug(s)', ''),
                    'phenotype': row.get('Phenotype(s)', ''),
                    'level': row.get('Level of Evidence', ''),
                    'category': row.get('Phenotype Category', ''),
                }

    # Load allele-specific info
    with open(alleles_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            ann_id = row.get('Clinical Annotation ID', '')
            if ann_id in annotations:
                rsid = annotations[ann_id]['rsid']
                genotype = row.get('Genotype/Allele', '')
                if rsid not in pharmgkb:
                    pharmgkb[rsid] = {
                        'gene': annotations[ann_id]['gene'],
                        'drugs': annotations[ann_id]['drugs'],
                        'phenotype': annotations[ann_id]['phenotype'],
                        'level': annotations[ann_id]['level'],
                        'category': annotations[ann_id]['category'],
                        'genotypes': {}
                    }
                pharmgkb[rsid]['genotypes'][genotype] = row.get('Annotation Text', '')

    return pharmgkb


def analyze_genome(genome: dict, clinvar: dict, pharmgkb: dict) -> dict:
    """Analyze genome against all databases."""
    results = {
        'curated_findings': [],
        'pharmgkb_findings': [],
        'clinvar_findings': [],
        'summary': {
            'total_snps': len(genome),
            'curated_matches': 0,
            'pharmgkb_matches': 0,
            'clinvar_matches': 0,
            'high_impact': 0,
        }
    }

    # Check curated SNPs
    for rsid, info in CURATED_SNPS.items():
        if rsid in genome:
            genotype = genome[rsid]['genotype']
            # Try both orientations
            genotype_rev = genotype[::-1] if len(genotype) == 2 else genotype

            variant_info = info['variants'].get(genotype) or info['variants'].get(genotype_rev)

            if variant_info:
                finding = {
                    'rsid': rsid,
                    'gene': info['gene'],
                    'category': info['category'],
                    'genotype': genotype,
                    'status': variant_info['status'],
                    'description': variant_info['desc'],
                    'magnitude': variant_info['magnitude'],
                }
                results['curated_findings'].append(finding)
                results['summary']['curated_matches'] += 1
                if variant_info['magnitude'] >= 3:
                    results['summary']['high_impact'] += 1

    # Check PharmGKB
    for rsid, info in pharmgkb.items():
        if rsid in genome:
            genotype = genome[rsid]['genotype']
            genotype_rev = genotype[::-1] if len(genotype) == 2 else genotype

            annotation = info['genotypes'].get(genotype) or info['genotypes'].get(genotype_rev)

            if annotation:
                finding = {
                    'rsid': rsid,
                    'gene': info['gene'],
                    'drugs': info['drugs'],
                    'genotype': genotype,
                    'annotation': annotation,
                    'level': info['level'],
                    'category': info['category'],
                }
                results['pharmgkb_findings'].append(finding)
                results['summary']['pharmgkb_matches'] += 1

    # Check ClinVar (by position)
    for rsid, snp_info in genome.items():
        chrom = snp_info['chromosome']
        pos = snp_info['position']
        key = f"chr{chrom}:{pos}"

        if key in clinvar:
            cv_info = clinvar[key]
            # Only include higher confidence findings
            if int(cv_info.get('gold_stars', 0)) >= 1:
                finding = {
                    'rsid': rsid,
                    'gene': cv_info['gene'],
                    'significance': cv_info['significance'],
                    'traits': cv_info['traits'],
                    'review_status': cv_info['review_status'],
                    'genotype': snp_info['genotype'],
                }
                results['clinvar_findings'].append(finding)
                results['summary']['clinvar_matches'] += 1

    # Sort findings by magnitude/importance
    results['curated_findings'].sort(key=lambda x: -x['magnitude'])
    results['pharmgkb_findings'].sort(key=lambda x: x['level'])

    return results


def generate_report(results: dict, output_path: Path):
    """Generate comprehensive markdown report."""

    with open(output_path, 'w') as f:
        f.write("# Comprehensive Genetic Analysis Report\n\n")
        f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total SNPs in genome**: {results['summary']['total_snps']:,}\n")
        f.write(f"- **Curated high-impact SNPs found**: {results['summary']['curated_matches']}\n")
        f.write(f"- **PharmGKB drug interactions found**: {results['summary']['pharmgkb_matches']}\n")
        f.write(f"- **High-impact findings (magnitude ≥3)**: {results['summary']['high_impact']}\n\n")

        # High Impact Findings
        f.write("---\n\n")
        f.write("## High-Impact Findings (Magnitude ≥ 3)\n\n")
        f.write("These findings have significant clinical or lifestyle implications.\n\n")

        high_impact = [x for x in results['curated_findings'] if x['magnitude'] >= 3]
        if high_impact:
            for finding in high_impact:
                f.write(f"### {finding['gene']} - {finding['rsid']}\n\n")
                f.write(f"- **Category**: {finding['category']}\n")
                f.write(f"- **Your Genotype**: {finding['genotype']}\n")
                f.write(f"- **Status**: {finding['status']}\n")
                f.write(f"- **Magnitude**: {finding['magnitude']}/6\n")
                f.write(f"- **Interpretation**: {finding['description']}\n\n")
        else:
            f.write("No high-impact findings detected.\n\n")

        # All Curated Findings by Category
        f.write("---\n\n")
        f.write("## All Findings by Category\n\n")

        categories = defaultdict(list)
        for finding in results['curated_findings']:
            categories[finding['category']].append(finding)

        for category, findings in sorted(categories.items()):
            f.write(f"### {category}\n\n")
            f.write("| Gene | SNP | Genotype | Status | Magnitude | Interpretation |\n")
            f.write("|------|-----|----------|--------|-----------|----------------|\n")
            for finding in findings:
                desc = finding['description'][:80] + "..." if len(finding['description']) > 80 else finding['description']
                f.write(f"| {finding['gene']} | {finding['rsid']} | {finding['genotype']} | {finding['status']} | {finding['magnitude']} | {desc} |\n")
            f.write("\n")

        # PharmGKB Drug Interactions
        f.write("---\n\n")
        f.write("## Drug-Gene Interactions (PharmGKB)\n\n")
        f.write("These are clinically annotated drug-gene interactions.\n\n")

        if results['pharmgkb_findings']:
            for finding in results['pharmgkb_findings'][:30]:  # Top 30
                f.write(f"### {finding['gene']} - {finding['rsid']}\n\n")
                f.write(f"- **Drugs**: {finding['drugs']}\n")
                f.write(f"- **Your Genotype**: {finding['genotype']}\n")
                f.write(f"- **Evidence Level**: {finding['level']}\n")
                f.write(f"- **Category**: {finding['category']}\n")
                f.write(f"- **Clinical Annotation**: {finding['annotation']}\n\n")
        else:
            f.write("No PharmGKB drug interactions found for your genotypes.\n\n")

        # Recommendations
        f.write("---\n\n")
        f.write("## Actionable Recommendations\n\n")

        recommendations = generate_recommendations(results)
        for rec in recommendations:
            f.write(f"### {rec['title']}\n\n")
            f.write(f"{rec['description']}\n\n")
            if rec.get('actions'):
                f.write("**Actions:**\n")
                for action in rec['actions']:
                    f.write(f"- {action}\n")
                f.write("\n")

        f.write("---\n\n")
        f.write("## Disclaimer\n\n")
        f.write("This report is for informational purposes only and should not be used for medical ")
        f.write("diagnosis or treatment. Consult a healthcare provider or genetic counselor before ")
        f.write("making any medical decisions based on this information. Genetic associations are ")
        f.write("probabilistic, not deterministic.\n")

    print(f"Report generated: {output_path}")


def generate_recommendations(results: dict) -> list:
    """Generate actionable recommendations based on findings."""
    recommendations = []

    findings_by_gene = {f['gene']: f for f in results['curated_findings']}

    # MTHFR recommendations
    if 'MTHFR' in findings_by_gene:
        finding = findings_by_gene['MTHFR']
        if finding['magnitude'] >= 2:
            recommendations.append({
                'title': 'Methylation Support',
                'description': f"Your MTHFR status ({finding['genotype']}) indicates reduced methylation capacity.",
                'actions': [
                    'Consider methylfolate instead of folic acid',
                    'Consider methylcobalamin (B12) supplementation',
                    'Get homocysteine levels tested',
                    'Discuss with a healthcare provider familiar with MTHFR variants',
                ]
            })

    # COMT recommendations
    if 'COMT' in findings_by_gene:
        finding = findings_by_gene['COMT']
        if finding['status'] == 'slow':
            recommendations.append({
                'title': 'Slow COMT Management',
                'description': "You have slow COMT (Met/Met), meaning catecholamines linger longer.",
                'actions': [
                    'Be cautious with stimulants (caffeine, medications)',
                    'Stress management is particularly important for you',
                    'Magnesium may support COMT function',
                    'Consider adaptogens over stimulants for energy',
                ]
            })

    # CYP1A2/ADORA2A - Caffeine
    caffeine_findings = [f for f in results['curated_findings'] if f['category'] in ['Drug Metabolism', 'Caffeine Response'] and 'caffeine' in f['description'].lower()]
    if caffeine_findings:
        recommendations.append({
            'title': 'Caffeine Metabolism',
            'description': "Based on your CYP1A2 and ADORA2A variants:",
            'actions': [
                'Limit caffeine to morning hours',
                'Start with lower doses than typical',
                'Monitor for anxiety with caffeine intake',
                'Consider caffeine alternatives if sensitive',
            ]
        })

    # Statin warning
    slco1b1 = next((f for f in results['curated_findings'] if f['gene'] == 'SLCO1B1'), None)
    if slco1b1 and slco1b1['magnitude'] >= 3:
        recommendations.append({
            'title': 'Statin Consideration',
            'description': "You have an SLCO1B1 variant associated with increased statin myopathy risk.",
            'actions': [
                'If prescribed statins, discuss alternatives with your doctor',
                'Pravastatin or rosuvastatin may be safer alternatives to simvastatin',
                'Report any muscle pain immediately',
            ]
        })

    # Blood clotting
    clotting = [f for f in results['curated_findings'] if f['category'] == 'Blood Clotting' and f['magnitude'] >= 3]
    if clotting:
        recommendations.append({
            'title': 'Blood Clotting Risk',
            'description': "You have genetic variants associated with increased clotting risk.",
            'actions': [
                'Inform doctors before surgery or prolonged immobilization',
                'Discuss estrogen-containing medications (birth control, HRT) with doctor',
                'Stay hydrated and mobile during long flights',
                'Know the signs of blood clots (leg pain/swelling, shortness of breath)',
            ]
        })

    # Warfarin
    warfarin_genes = ['VKORC1', 'CYP2C9']
    warfarin_findings = [f for f in results['curated_findings'] if f['gene'] in warfarin_genes and f['magnitude'] >= 2]
    if warfarin_findings:
        recommendations.append({
            'title': 'Warfarin Sensitivity',
            'description': "You have variants affecting warfarin metabolism.",
            'actions': [
                'If ever prescribed warfarin, inform your doctor of these variants',
                'You may need a lower starting dose',
                'More frequent INR monitoring may be needed initially',
            ]
        })

    return recommendations


def main():
    print("=" * 60)
    print("COMPREHENSIVE GENOME ANALYZER")
    print("=" * 60)

    # Load genome
    genome_path = DATA_DIR / "genome.txt"
    print(f"\nLoading genome from {genome_path}...")
    genome = load_genome(genome_path)
    print(f"Loaded {len(genome):,} SNPs")

    # Load ClinVar
    clinvar_path = DATA_DIR / "clinvar_alleles.tsv"
    print(f"\nLoading ClinVar data from {clinvar_path}...")
    clinvar = load_clinvar(clinvar_path)
    print(f"Loaded {len(clinvar):,} pathogenic variants")

    # Load PharmGKB
    pharmgkb_annotations = DATA_DIR / "clinical_annotations.tsv"
    pharmgkb_alleles = DATA_DIR / "clinical_ann_alleles.tsv"
    print(f"\nLoading PharmGKB data...")
    pharmgkb = load_pharmgkb(pharmgkb_annotations, pharmgkb_alleles)
    print(f"Loaded {len(pharmgkb):,} drug-gene interactions")

    # Analyze
    print("\nAnalyzing genome...")
    results = analyze_genome(genome, clinvar, pharmgkb)

    # Save raw results
    results_path = REPORTS_DIR / "analysis_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw results saved to {results_path}")

    # Generate report
    report_path = REPORTS_DIR / "genetic_report.md"
    generate_report(results, report_path)

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nHigh-Impact Findings ({results['summary']['high_impact']}):")
    for finding in [f for f in results['curated_findings'] if f['magnitude'] >= 3]:
        print(f"  - {finding['gene']} ({finding['rsid']}): {finding['status']} - Magnitude {finding['magnitude']}")

    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
