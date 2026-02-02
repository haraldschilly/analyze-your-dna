"""Shared utilities for the genetic analysis pipeline."""

import gzip
import os
import shutil
from collections import defaultdict


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
        with gzip.open(gz, 'rb') as f_in, open(tsv, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        print("  Done.")

    return tsv


def snp_database_stats():
    """Print SNP coverage stats for both curated databases.

    Used to regenerate the README.md 'What It Analyzes' tables.
    Run: uv run python3 -c "from scripts.utils import snp_database_stats; snp_database_stats()"
    """
    from comprehensive_snp_database import COMPREHENSIVE_SNPS
    from analyze_genome import CURATED_SNPS

    for name, db in [("COMPREHENSIVE_SNPS", COMPREHENSIVE_SNPS), ("CURATED_SNPS", CURATED_SNPS)]:
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
