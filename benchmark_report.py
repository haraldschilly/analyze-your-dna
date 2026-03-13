import time
import sys
import os
import statistics

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from analyze_dna.disease_risk_analyzer import generate_report

def create_fake_finding(i, category="pathogenic", zygosity="AFFECTED"):
    return {
        "rsid": f"rs{i}",
        "gene": f"GENE{i}",
        "chromosome": "1",
        "position": str(i),
        "user_genotype": "AA",
        "ref": "G",
        "alt": "A",
        "is_homozygous": True,
        "is_heterozygous": False,
        "clinical_significance": "Pathogenic",
        "gold_stars": 2,
        "review_status": "criteria",
        "traits": f"Disease {i};Trait {i}",
        "inheritance": "Autosomal Dominant",
        "hgvs_p": "p.Arg123His",
        "hgvs_c": "c.368G>A",
        "molecular_consequence": "missense variant",
        "pmids": "12345678",
        "xrefs": "ClinVar:123",
        "age_of_onset": "Adult",
        "prevalence": "1/10000",
        "zygosity_status": zygosity,
        "zygosity_description": "Homozygous for variant allele"
    }

def run_benchmark(n_findings):
    # Distribute findings across categories
    findings = {
        "pathogenic": [create_fake_finding(i, zygosity="AFFECTED") for i in range(n_findings // 4)],
        "likely_pathogenic": [create_fake_finding(i, zygosity="HETEROZYGOUS") for i in range(n_findings // 4)],
        "risk_factor": [create_fake_finding(i) for i in range(n_findings // 8)],
        "drug_response": [create_fake_finding(i) for i in range(n_findings // 8)],
        "protective": [create_fake_finding(i) for i in range(n_findings // 8)],
        "other_significant": [create_fake_finding(i) for i in range(n_findings // 8)],
        "uncertain_but_notable": [],
    }
    # Special case for carrier
    findings["pathogenic"].extend([create_fake_finding(i + 1000000, zygosity="CARRIER") for i in range(n_findings // 8)])

    stats = {"total_clinvar": 1000000, "matched": n_findings, "pathogenic_matched": n_findings, "likely_pathogenic_matched": 0}
    genome_by_rsid = {f"rs{i}": {} for i in range(n_findings)}

    # Mock open to avoid writing to disk
    import unittest.mock as mock
    durations = []
    for _ in range(5):
        with mock.patch("builtins.open", mock.mock_open()):
            start_time = time.perf_counter()
            generate_report(findings, stats, genome_by_rsid)
            end_time = time.perf_counter()
        durations.append(end_time - start_time)

    return min(durations)

if __name__ == "__main__":
    print("Running benchmark (best of 5)...")
    for n in [100, 1000, 5000, 10000]:
        duration = run_benchmark(n)
        print(f"n={n}: {duration:.4f}s")
