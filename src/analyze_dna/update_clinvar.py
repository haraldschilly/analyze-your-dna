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
Download and convert NCBI ClinVar variant_summary to clinvar_alleles.tsv format.

This script downloads the latest variant_summary.txt.gz from NCBI's ClinVar FTP
and converts it to the format expected by the analysis pipeline.

The original clinvar_alleles.tsv format came from macarthur-lab/clinvar (now deprecated).
This script recreates that format from NCBI's official data, including computing
the gold_stars field from ReviewStatus.

Usage:
    uv run python scripts/update_clinvar.py
    uv run python scripts/update_clinvar.py --keep-download  # Keep variant_summary.txt.gz
    uv run python scripts/update_clinvar.py --no-gzip        # Don't compress output
"""

import argparse
import csv
import gzip
import hashlib
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# URLs and paths
CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
DOWNLOAD_FILE = DATA_DIR / "variant_summary.txt.gz"
OUTPUT_FILE = DATA_DIR / "clinvar_alleles.tsv"
OUTPUT_GZ = DATA_DIR / "clinvar_alleles.tsv.gz"

# Output column order (matches original clinvar_alleles.tsv format)
OUTPUT_COLUMNS = [
    "chrom",
    "pos",
    "ref",
    "alt",
    "start",
    "stop",
    "strand",
    "variation_type",
    "variation_id",
    "rcv",
    "scv",
    "allele_id",
    "symbol",
    "hgvs_c",
    "hgvs_p",
    "molecular_consequence",
    "clinical_significance",
    "clinical_significance_ordered",
    "pathogenic",
    "likely_pathogenic",
    "uncertain_significance",
    "likely_benign",
    "benign",
    "review_status",
    "review_status_ordered",
    "last_evaluated",
    "all_submitters",
    "submitters_ordered",
    "all_traits",
    "all_pmids",
    "inheritance_modes",
    "age_of_onset",
    "prevalence",
    "disease_mechanism",
    "origin",
    "xrefs",
    "dates_ordered",
    "gold_stars",
    "conflicted",
]

# Gold stars mapping from ClinVar's official review status
# See: https://www.ncbi.nlm.nih.gov/clinvar/docs/review_status/
GOLD_STARS_MAP = {
    "practice guideline": 4,
    "reviewed by expert panel": 3,
    "criteria provided, multiple submitters, no conflicts": 2,
    "criteria provided, conflicting classifications": 1,
    "criteria provided, single submitter": 1,
    "criteria provided, conflicting interpretations": 1,  # older terminology
}


def compute_gold_stars(review_status: str) -> int:
    """Convert ReviewStatus to gold stars (0-4).

    ClinVar uses a star rating system to indicate the level of review:
    - 4 stars: Practice guideline
    - 3 stars: Reviewed by expert panel
    - 2 stars: Multiple submitters, no conflicts
    - 1 star: Single submitter with criteria, or conflicting
    - 0 stars: No assertion criteria provided
    """
    rs_lower = review_status.lower().strip()
    for pattern, stars in GOLD_STARS_MAP.items():
        if pattern in rs_lower:
            return stars
    return 0


def compute_significance_flags(clinical_sig: str) -> dict:
    """Compute boolean flags for clinical significance categories."""
    sig_lower = clinical_sig.lower()
    return {
        "pathogenic": 1 if ("pathogenic" in sig_lower and "likely" not in sig_lower) else 0,
        "likely_pathogenic": 1 if "likely pathogenic" in sig_lower or "likely_pathogenic" in sig_lower else 0,
        "uncertain_significance": 1 if "uncertain" in sig_lower else 0,
        "likely_benign": 1 if "likely benign" in sig_lower or "likely_benign" in sig_lower else 0,
        "benign": 1 if ("benign" in sig_lower and "likely" not in sig_lower) else 0,
    }


def calculate_md5(file_path: Path) -> str:
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def download_clinvar(url: str, dest: Path, show_progress: bool = True) -> None:
    """Download ClinVar variant_summary.txt.gz and verify its MD5 checksum."""
    md5_url = url + ".md5"
    md5_dest = dest.with_suffix(dest.suffix + ".md5")

    print(f"Downloading checksum from {md5_url}")
    urllib.request.urlretrieve(md5_url, md5_dest)

    print(f"Downloading from {url}")
    print(f"  Destination: {dest}")

    def progress_hook(block_num, block_size, total_size):
        if show_progress and total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest, progress_hook)
    if show_progress:
        print()  # newline after progress

    file_size = dest.stat().st_size / (1024 * 1024)
    print(f"  Downloaded: {file_size:.1f} MB")

    # Verify checksum
    print("  Verifying MD5 checksum...")
    with open(md5_dest, "r", encoding="utf-8") as f:
        # NCBI MD5 format is typically: "hash  filename"
        expected_md5 = f.read().split()[0]

    actual_md5 = calculate_md5(dest)
    if actual_md5 != expected_md5:
        if dest.exists():
            dest.unlink()
        if md5_dest.exists():
            md5_dest.unlink()
        raise ValueError(f"Checksum mismatch! Expected {expected_md5}, got {actual_md5}")

    print("  Checksum verified successfully.")
    # Clean up md5 file
    if md5_dest.exists():
        md5_dest.unlink()


def convert_clinvar(input_gz: Path, output_tsv: Path, include_all: bool = False) -> dict:
    """Convert variant_summary.txt.gz to clinvar_alleles.tsv format.

    Filters for GRCh37 assembly (used by 23andMe) and maps columns to the
    expected format.

    Returns statistics about the conversion.
    """
    stats = {
        "total_rows": 0,
        "grch37_rows": 0,
        "valid_vcf_rows": 0,
        "filtered_out": 0,
        "written_rows": 0,
    }

    print(f"Converting {input_gz.name} to {output_tsv.name}")
    print("  Filtering for GRCh37 assembly (23andMe uses GRCh37)")

    with (
        gzip.open(input_gz, "rt", encoding="utf-8") as f_in,
        open(output_tsv, "w", newline="", encoding="utf-8") as f_out,
    ):
        reader = csv.DictReader(f_in, delimiter="\t")
        writer = csv.DictWriter(f_out, fieldnames=OUTPUT_COLUMNS, delimiter="\t")
        writer.writeheader()

        for row in reader:
            stats["total_rows"] += 1

            # Progress indicator every 500k rows
            if stats["total_rows"] % 500000 == 0:
                print(f"  Processed {stats['total_rows']:,} rows...")

            # Filter for GRCh37 (23andMe uses GRCh37 coordinates)
            if row.get("Assembly") != "GRCh37":
                continue
            stats["grch37_rows"] += 1

            # Use VCF-style positions (left-shifted, matches 23andMe)
            # Skip rows without valid VCF data
            pos_vcf = row.get("PositionVCF", "")
            ref_vcf = row.get("ReferenceAlleleVCF", "")
            alt_vcf = row.get("AlternateAlleleVCF", "")

            if not pos_vcf or pos_vcf == "-1" or not ref_vcf or not alt_vcf:
                continue
            stats["valid_vcf_rows"] += 1

            # Extract fields from variant_summary
            clinical_sig = row.get("ClinicalSignificance", "")
            review_status = row.get("ReviewStatus", "")

            # Compute derived fields
            gold_stars = compute_gold_stars(review_status)
            sig_flags = compute_significance_flags(clinical_sig)

            # Check for conflicting interpretations
            conflicted = 1 if "conflicting" in clinical_sig.lower() else 0

            # Filter to only clinically actionable variants (unless --include-all)
            if not include_all:
                sig_lower = clinical_sig.lower()
                is_actionable = (
                    ("pathogenic" in sig_lower and "conflict" not in sig_lower)
                    or "likely pathogenic" in sig_lower
                    or "risk factor" in sig_lower
                    or "drug response" in sig_lower
                )
                if not is_actionable:
                    stats["filtered_out"] += 1
                    continue

            # Build output row
            out_row = {
                "chrom": row.get("Chromosome", ""),
                "pos": pos_vcf,
                "ref": ref_vcf,
                "alt": alt_vcf,
                "start": row.get("Start", ""),
                "stop": row.get("Stop", ""),
                "strand": "+",  # ClinVar variants are on forward strand
                "variation_type": row.get("Type", ""),
                "variation_id": row.get("VariationID", ""),
                "rcv": row.get("RCVaccession", ""),
                "scv": row.get("SCVsForAggregateGermlineClassification", ""),
                "allele_id": row.get("AlleleID", ""),
                "symbol": row.get("GeneSymbol", ""),
                "hgvs_c": row.get("Name", ""),  # Name often contains HGVS
                "hgvs_p": "",  # Not directly in variant_summary
                "molecular_consequence": "",  # Not in variant_summary
                "clinical_significance": clinical_sig,
                "clinical_significance_ordered": clinical_sig.lower().replace(" ", "_"),
                "pathogenic": sig_flags["pathogenic"],
                "likely_pathogenic": sig_flags["likely_pathogenic"],
                "uncertain_significance": sig_flags["uncertain_significance"],
                "likely_benign": sig_flags["likely_benign"],
                "benign": sig_flags["benign"],
                "review_status": review_status,
                "review_status_ordered": review_status.lower().replace(" ", "_").replace(",", ""),
                "last_evaluated": row.get("LastEvaluated", ""),
                "all_submitters": row.get("NumberSubmitters", ""),
                "submitters_ordered": "",
                "all_traits": row.get("PhenotypeList", ""),
                "all_pmids": "",  # Not directly in variant_summary
                "inheritance_modes": "",  # Not in variant_summary
                "age_of_onset": "",  # Not in variant_summary
                "prevalence": "",  # Not in variant_summary
                "disease_mechanism": "",  # Not in variant_summary
                "origin": row.get("Origin", ""),
                "xrefs": row.get("OtherIDs", ""),
                "dates_ordered": "",
                "gold_stars": gold_stars,
                "conflicted": conflicted,
            }

            writer.writerow(out_row)
            stats["written_rows"] += 1

    return stats


def compress_output(tsv_path: Path, gz_path: Path) -> None:
    """Compress the TSV file to .gz format."""
    print(f"Compressing to {gz_path.name}")

    with open(tsv_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        while chunk := f_in.read(1024 * 1024):  # 1MB chunks
            f_out.write(chunk)

    original_size = tsv_path.stat().st_size / (1024 * 1024)
    compressed_size = gz_path.stat().st_size / (1024 * 1024)
    ratio = compressed_size / original_size * 100

    print(f"  Original: {original_size:.1f} MB")
    print(f"  Compressed: {compressed_size:.1f} MB ({ratio:.1f}%)")


def run_update_clinvar(keep_download=False, no_gzip=False, skip_download=False, include_all=False):
    """Run the ClinVar update process."""
    print("=" * 60)
    print("ClinVar Database Updater")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Download
    if skip_download and DOWNLOAD_FILE.exists():
        print(f"Using existing download: {DOWNLOAD_FILE}")
    else:
        try:
            download_clinvar(CLINVAR_URL, DOWNLOAD_FILE)
        except Exception as e:
            print(f"\nError downloading ClinVar data: {e}", file=sys.stderr)
            sys.exit(1)
    print()

    # Step 2: Convert
    if include_all:
        print("Including ALL variants (benign, VUS, etc.)")
    else:
        print("Filtering to clinically actionable variants only")
        print("  (pathogenic, likely pathogenic, risk factor, drug response)")
        print("  Use --include-all to include benign/VUS variants")
    stats = convert_clinvar(DOWNLOAD_FILE, OUTPUT_FILE, include_all=include_all)
    print()

    # Step 3: Report statistics
    print("Conversion Statistics:")
    print(f"  Total rows in variant_summary: {stats['total_rows']:,}")
    print(f"  GRCh37 rows: {stats['grch37_rows']:,}")
    print(f"  Rows with valid VCF data: {stats['valid_vcf_rows']:,}")
    if stats["filtered_out"] > 0:
        print(f"  Filtered out (benign/VUS): {stats['filtered_out']:,}")
    print(f"  Rows written: {stats['written_rows']:,}")

    output_size = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"  Output file size: {output_size:.1f} MB")
    print()

    # Step 4: Compress if requested
    if not no_gzip:
        compress_output(OUTPUT_FILE, OUTPUT_GZ)
        print()

    # Step 5: Cleanup download
    if not keep_download and DOWNLOAD_FILE.exists():
        print(f"Removing downloaded file: {DOWNLOAD_FILE.name}")
        DOWNLOAD_FILE.unlink()

    print()
    print("=" * 60)
    print("Update complete!")
    print(f"Output: {OUTPUT_FILE}")
    if not no_gzip:
        print(f"Compressed: {OUTPUT_GZ}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Download and convert NCBI ClinVar to clinvar_alleles.tsv format")
    parser.add_argument("--keep-download", action="store_true", help="Keep the downloaded variant_summary.txt.gz file")
    parser.add_argument("--no-gzip", action="store_true", help="Don't compress the output TSV file")
    parser.add_argument(
        "--skip-download", action="store_true", help="Skip download if variant_summary.txt.gz already exists"
    )
    parser.add_argument(
        "--include-all", action="store_true", help="Include all variants (default: only clinically actionable)"
    )
    args = parser.parse_args()

    run_update_clinvar(args.keep_download, args.no_gzip, args.skip_download, args.include_all)


if __name__ == "__main__":
    main()
