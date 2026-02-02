#!/usr/bin/env python3
"""
Fast data loading utilities using polars when available.

Falls back to standard library csv for pure-Python operation.

Performance comparison (typical 23andMe genome ~600K SNPs, ClinVar ~341K variants):
- Standard csv: ~15-25 seconds
- Polars: ~2-4 seconds

Usage:
    from fast_loader import load_genome_fast, load_clinvar_fast, USING_POLARS
"""

import csv
from pathlib import Path
from typing import Tuple, Dict, Optional

# Try to import polars for fast parsing
try:
    import polars as pl
    USING_POLARS = True
except ImportError:
    USING_POLARS = False
    pl = None


def load_genome_fast(genome_path: Path) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Load 23andMe genome file into dictionaries.

    Uses polars for ~5-10x speedup when available.

    Returns:
        Tuple of (genome_by_rsid, genome_by_position) dictionaries
    """
    if USING_POLARS:
        return _load_genome_polars(genome_path)
    else:
        return _load_genome_stdlib(genome_path)


def _load_genome_polars(genome_path: Path) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Load genome using polars (fast path)."""
    # Read TSV, skip comment lines
    df = pl.read_csv(
        genome_path,
        separator='\t',
        has_header=False,
        comment_prefix='#',
        new_columns=['rsid', 'chromosome', 'position', 'genotype'],
        dtypes={
            'rsid': pl.Utf8,
            'chromosome': pl.Utf8,
            'position': pl.Utf8,
            'genotype': pl.Utf8,
        },
    )

    # Filter out no-calls
    df = df.filter(pl.col('genotype') != '--')

    # Build dictionaries
    genome_by_rsid = {}
    genome_by_position = {}

    for row in df.iter_rows(named=True):
        rsid = row['rsid']
        chrom = row['chromosome']
        pos = row['position']
        genotype = row['genotype']

        genome_by_rsid[rsid] = {
            'chromosome': chrom,
            'position': pos,
            'genotype': genotype,
        }

        pos_key = f"{chrom}:{pos}"
        genome_by_position[pos_key] = {
            'rsid': rsid,
            'genotype': genotype,
        }

    return genome_by_rsid, genome_by_position


def _load_genome_stdlib(genome_path: Path) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Load genome using standard library (fallback)."""
    genome_by_rsid = {}
    genome_by_position = {}

    with open(genome_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
                if genotype != '--':
                    genome_by_rsid[rsid] = {
                        'chromosome': chrom,
                        'position': pos,
                        'genotype': genotype,
                    }
                    pos_key = f"{chrom}:{pos}"
                    genome_by_position[pos_key] = {
                        'rsid': rsid,
                        'genotype': genotype,
                    }

    return genome_by_rsid, genome_by_position


def load_clinvar_fast(
    clinvar_path: Path,
    genome_by_position: Dict[str, Dict],
    progress_callback: Optional[callable] = None,
) -> Tuple[Dict[str, list], Dict[str, int]]:
    """
    Load ClinVar and analyze for disease variants.

    Uses polars for ~10x speedup when available.
    Only processes variants that match positions in the genome.

    Args:
        clinvar_path: Path to clinvar_alleles.tsv
        genome_by_position: Dict of position -> genome data
        progress_callback: Optional callback(current, total) for progress

    Returns:
        Tuple of (findings dict, stats dict)
    """
    if USING_POLARS:
        return _load_clinvar_polars(clinvar_path, genome_by_position, progress_callback)
    else:
        return _load_clinvar_stdlib(clinvar_path, genome_by_position, progress_callback)


def _load_clinvar_polars(
    clinvar_path: Path,
    genome_by_position: Dict[str, Dict],
    progress_callback: Optional[callable] = None,
) -> Tuple[Dict[str, list], Dict[str, int]]:
    """Load ClinVar using polars (fast path)."""

    # Get set of positions we care about for fast filtering
    genome_positions = set(genome_by_position.keys())

    # Read ClinVar - polars is very fast for this
    df = pl.read_csv(
        clinvar_path,
        separator='\t',
        infer_schema_length=10000,
    )

    total_rows = len(df)

    # Create position key column for filtering
    df = df.with_columns(
        (pl.col('chrom').cast(pl.Utf8) + pl.lit(':') + pl.col('pos').cast(pl.Utf8)).alias('pos_key')
    )

    # Filter to only positions in genome (huge speedup)
    df_filtered = df.filter(pl.col('pos_key').is_in(genome_positions))

    findings = {
        'pathogenic': [],
        'likely_pathogenic': [],
        'risk_factor': [],
        'drug_response': [],
        'protective': [],
        'other_significant': [],
    }

    stats = {
        'total_clinvar': total_rows,
        'matched': len(df_filtered),
        'pathogenic_matched': 0,
        'likely_pathogenic_matched': 0,
    }

    # Process filtered rows
    for i, row in enumerate(df_filtered.iter_rows(named=True)):
        if progress_callback and i % 1000 == 0:
            progress_callback(i, len(df_filtered))

        pos_key = row['pos_key']
        user_data = genome_by_position[pos_key]
        user_genotype = user_data['genotype']

        ref_allele = str(row['ref'])
        alt_allele = str(row['alt'])
        clinical_sig = str(row['clinical_significance']).lower()

        # Only process true SNPs (not indels)
        if len(ref_allele) != 1 or len(alt_allele) != 1:
            continue

        has_variant = alt_allele in user_genotype
        is_homozygous = user_genotype == alt_allele + alt_allele
        is_heterozygous = has_variant and not is_homozygous
        has_ref_only = user_genotype == ref_allele + ref_allele

        if has_ref_only or not has_variant:
            continue

        finding = {
            'chromosome': str(row['chrom']),
            'position': str(row['pos']),
            'rsid': user_data['rsid'],
            'gene': str(row.get('symbol', '')),
            'ref': ref_allele,
            'alt': alt_allele,
            'user_genotype': user_genotype,
            'is_homozygous': is_homozygous,
            'is_heterozygous': is_heterozygous,
            'clinical_significance': str(row['clinical_significance']),
            'review_status': str(row.get('review_status', '')),
            'gold_stars': int(row.get('gold_stars', 0)) if row.get('gold_stars') else 0,
            'traits': str(row.get('all_traits', '')),
            'inheritance': str(row.get('inheritance_modes', '')),
            'hgvs_p': str(row.get('hgvs_p', '')),
            'hgvs_c': str(row.get('hgvs_c', '')),
            'molecular_consequence': str(row.get('molecular_consequence', '')),
            'xrefs': str(row.get('xrefs', '')),
        }

        # Classify by clinical significance
        if 'pathogenic' in clinical_sig and 'likely' not in clinical_sig and 'conflict' not in clinical_sig:
            findings['pathogenic'].append(finding)
            stats['pathogenic_matched'] += 1
        elif 'likely pathogenic' in clinical_sig or 'likely_pathogenic' in clinical_sig:
            findings['likely_pathogenic'].append(finding)
            stats['likely_pathogenic_matched'] += 1
        elif 'risk factor' in clinical_sig or 'risk_factor' in clinical_sig:
            findings['risk_factor'].append(finding)
        elif 'drug response' in clinical_sig or 'drug_response' in clinical_sig:
            findings['drug_response'].append(finding)
        elif 'protective' in clinical_sig:
            findings['protective'].append(finding)
        elif 'association' in clinical_sig or 'affects' in clinical_sig:
            findings['other_significant'].append(finding)

    return findings, stats


def _load_clinvar_stdlib(
    clinvar_path: Path,
    genome_by_position: Dict[str, Dict],
    progress_callback: Optional[callable] = None,
) -> Tuple[Dict[str, list], Dict[str, int]]:
    """Load ClinVar using standard library (fallback)."""

    findings = {
        'pathogenic': [],
        'likely_pathogenic': [],
        'risk_factor': [],
        'drug_response': [],
        'protective': [],
        'other_significant': [],
    }

    stats = {
        'total_clinvar': 0,
        'matched': 0,
        'pathogenic_matched': 0,
        'likely_pathogenic_matched': 0,
    }

    with open(clinvar_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            stats['total_clinvar'] += 1

            if progress_callback and stats['total_clinvar'] % 50000 == 0:
                progress_callback(stats['total_clinvar'], 341000)  # Approximate total

            chrom = row['chrom']
            pos = row['pos']
            pos_key = f"{chrom}:{pos}"

            if pos_key not in genome_by_position:
                continue

            stats['matched'] += 1

            user_data = genome_by_position[pos_key]
            user_genotype = user_data['genotype']
            ref_allele = row['ref']
            alt_allele = row['alt']
            clinical_sig = row['clinical_significance'].lower()

            # Only process true SNPs
            if len(ref_allele) != 1 or len(alt_allele) != 1:
                continue

            has_variant = alt_allele in user_genotype
            is_homozygous = user_genotype == alt_allele + alt_allele
            is_heterozygous = has_variant and not is_homozygous
            has_ref_only = user_genotype == ref_allele + ref_allele

            if has_ref_only or not has_variant:
                continue

            finding = {
                'chromosome': chrom,
                'position': pos,
                'rsid': user_data['rsid'],
                'gene': row['symbol'],
                'ref': ref_allele,
                'alt': alt_allele,
                'user_genotype': user_genotype,
                'is_homozygous': is_homozygous,
                'is_heterozygous': is_heterozygous,
                'clinical_significance': row['clinical_significance'],
                'review_status': row['review_status'],
                'gold_stars': int(row['gold_stars']) if row['gold_stars'] else 0,
                'traits': row['all_traits'],
                'inheritance': row.get('inheritance_modes', ''),
                'hgvs_p': row.get('hgvs_p', ''),
                'hgvs_c': row.get('hgvs_c', ''),
                'molecular_consequence': row.get('molecular_consequence', ''),
                'xrefs': row.get('xrefs', ''),
            }

            if 'pathogenic' in clinical_sig and 'likely' not in clinical_sig and 'conflict' not in clinical_sig:
                findings['pathogenic'].append(finding)
                stats['pathogenic_matched'] += 1
            elif 'likely pathogenic' in clinical_sig or 'likely_pathogenic' in clinical_sig:
                findings['likely_pathogenic'].append(finding)
                stats['likely_pathogenic_matched'] += 1
            elif 'risk factor' in clinical_sig or 'risk_factor' in clinical_sig:
                findings['risk_factor'].append(finding)
            elif 'drug response' in clinical_sig or 'drug_response' in clinical_sig:
                findings['drug_response'].append(finding)
            elif 'protective' in clinical_sig:
                findings['protective'].append(finding)
            elif 'association' in clinical_sig or 'affects' in clinical_sig:
                findings['other_significant'].append(finding)

    return findings, stats


def get_loader_info() -> str:
    """Return info about which loader is being used."""
    if USING_POLARS:
        return f"Using polars {pl.__version__} (fast mode)"
    else:
        return "Using standard library csv (install polars for 5-10x speedup)"
