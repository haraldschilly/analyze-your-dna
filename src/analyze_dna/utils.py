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

"""Shared utilities for the genetic analysis pipeline."""

import csv
import gzip
import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from typing_extensions import NotRequired


class VariantInfo(TypedDict):
    """
    Type definition for variant information.

    Attributes:
        status (str): Short status descriptor (e.g., 'normal', 'carrier', 'affected')
        desc (str): Detailed user-facing description
        magnitude (int): Impact score (0-5), where 0 is neutral and 5 is critical
    """

    status: str
    desc: str
    magnitude: int


class SnpInfo(TypedDict):
    """
    Type definition for SNP entry.

    Attributes:
        gene (str): Gene symbol
        category (str): Health category
        variants (dict[str, VariantInfo]): Map of genotype (e.g., 'AA') to variant info
        note (NotRequired[str]): Optional scientific context or mechanism details
    """

    gene: str
    category: str
    variants: dict[str, VariantInfo]
    note: NotRequired[str]


# Type alias for the database structure
SnpDatabase = dict[str, SnpInfo]


def load_genome(genome_path: Path) -> dict:
    """Load 23andMe genome file into a dictionary."""
    genome = {}
    with open(genome_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
                if genotype != "--":
                    genome[rsid] = {"chromosome": chrom, "position": pos, "genotype": genotype}
    return genome


def load_pharmgkb(annotations_path: Path, alleles_path: Path) -> dict:
    """Load PharmGKB drug-gene annotations."""
    pharmgkb = {}
    annotations = {}

    with open(annotations_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ann_id = row.get("Clinical Annotation ID", "")
            variant = row.get("Variant/Haplotypes", "")
            if variant.startswith("rs"):
                annotations[ann_id] = {
                    "rsid": variant,
                    "gene": row.get("Gene", ""),
                    "drugs": row.get("Drug(s)", ""),
                    "phenotype": row.get("Phenotype(s)", ""),
                    "level": row.get("Level of Evidence", ""),
                    "category": row.get("Phenotype Category", ""),
                }

    with open(alleles_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ann_id = row.get("Clinical Annotation ID", "")
            if ann_id in annotations:
                rsid = annotations[ann_id]["rsid"]
                genotype = row.get("Genotype/Allele", "")
                if rsid not in pharmgkb:
                    pharmgkb[rsid] = {
                        "gene": annotations[ann_id]["gene"],
                        "drugs": annotations[ann_id]["drugs"],
                        "phenotype": annotations[ann_id]["phenotype"],
                        "level": annotations[ann_id]["level"],
                        "category": annotations[ann_id]["category"],
                        "genotypes": {},
                    }
                pharmgkb[rsid]["genotypes"][genotype] = row.get("Annotation Text", "")

    return pharmgkb


def ensure_clinvar(data_dir):
    """Decompress clinvar_alleles.tsv.gz if the uncompressed file is missing.

    Args:
        data_dir: Path to the data directory (str or Path).

    Returns:
        Path to clinvar_alleles.tsv (str).
    """
    tsv = os.path.join(str(data_dir), "clinvar_alleles.tsv")
    gz = os.path.join(str(data_dir), "clinvar_alleles.tsv.gz")

    if not os.path.exists(tsv) and os.path.exists(gz):
        print("  Decompressing clinvar_alleles.tsv.gz ...")
        with gzip.open(gz, "rb") as f_in, open(tsv, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        print("  Done.")

    return tsv


def snp_database_stats():
    """Print SNP coverage stats for all curated databases.

    Used to regenerate the README.md 'What It Analyzes' tables.
    Run: uv run python3 -c "from analyze_dna.utils import snp_database_stats; snp_database_stats()"
    """
    from .analyze_genome import CURATED_SNPS
    from .comprehensive_snp_database import COMPREHENSIVE_SNPS
    from .traits_snp_database import TRAITS_SNPS

    for name, db in [
        ("COMPREHENSIVE_SNPS", COMPREHENSIVE_SNPS),
        ("CURATED_SNPS", CURATED_SNPS),
        ("TRAITS_SNPS", TRAITS_SNPS),
    ]:
        cats = defaultdict(lambda: {"snps": set(), "genes": set()})
        for rsid, info in db.items():
            cat = info["category"]
            cats[cat]["snps"].add(rsid)
            cats[cat]["genes"].add(info["gene"])
        print(f"=== {name} ({len(db)} total SNPs) ===")
        for cat in sorted(cats.keys(), key=lambda c: -len(cats[c]["snps"])):
            genes = sorted(cats[cat]["genes"])
            print(f"| {cat} | {len(cats[cat]['snps'])} | {len(genes)} | {', '.join(genes)} |")
        print()
