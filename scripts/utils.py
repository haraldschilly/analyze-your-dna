"""Shared utilities for the genetic analysis pipeline."""

import gzip
import os
import shutil


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
