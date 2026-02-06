from pathlib import Path

import click

from .fast_loader import load_genome_fast
from .generate_portrait_prompt import format_prompt_output, generate_portrait_prompt
from .generate_traits_report import run_traits_report
from .run_full_analysis import run_full_analysis
from .update_clinvar import run_update_clinvar


@click.group()
def cli():
    """Genetic Health Analysis Pipeline CLI."""


@cli.command(name="full-analysis")
@click.argument("genome", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--name", "-n", help="Subject name to include in reports")
def full_analysis(genome, name):
    """Run full genetic health analysis pipeline.

    GENOME is the path to your 23andMe genome file (default: data/genome.txt).
    """
    run_full_analysis(genome, name)


@cli.command()
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@click.option("--name", "-n", default="Subject", help="Subject name")
def traits(genome, name):
    """Generate genetic traits report.

    GENOME is the path to your 23andMe genome file.
    """
    run_traits_report(genome, name)


@cli.command()
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@click.option("--birth-year", required=True, type=int, help="Year of birth (e.g., 1980)")
@click.option(
    "--sex",
    required=True,
    type=click.Choice(["male", "female", "man", "woman", "m", "f"], case_sensitive=False),
    help="Biological sex",
)
@click.option("--hair-style", default="natural", help="Hair style preference")
@click.option("--target-age", type=int, help="Optional: target age for rendering")
@click.option("--glasses", help="Optional: glasses description")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file")
def portrait(genome, birth_year, sex, hair_style, target_age, glasses, output):  # pylint: disable=too-many-positional-arguments
    """Generate AI portrait prompts from genetic data.

    GENOME is the path to your 23andMe genome file.
    """
    click.echo(f"Loading genome from {genome}...", err=True)
    genome_by_rsid, _ = load_genome_fast(genome)
    click.echo(f"✓ Loaded {len(genome_by_rsid):,} SNPs", err=True)

    click.echo("Generating portrait prompt...", err=True)
    prompt_data = generate_portrait_prompt(genome_by_rsid, birth_year, sex, hair_style, target_age, glasses)

    output_text = format_prompt_output(prompt_data)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_text)
        click.echo(f"\n✅ Portrait prompt written to {output}", err=True)
    else:
        click.echo(output_text)

    click.echo(f"\n✓ Eye color: {prompt_data['subject']}", err=True)


@cli.command(name="update-clinvar")
@click.option("--keep-download", is_flag=True, help="Keep the downloaded variant_summary.txt.gz file")
@click.option("--no-gzip", is_flag=True, help="Don't compress the output TSV file")
@click.option("--skip-download", is_flag=True, help="Skip download if variant_summary.txt.gz already exists")
@click.option("--include-all", is_flag=True, help="Include all variants (default: only clinically actionable)")
def update_clinvar_cmd(keep_download, no_gzip, skip_download, include_all):
    """Download and convert NCBI ClinVar database."""
    run_update_clinvar(keep_download, no_gzip, skip_download, include_all)


if __name__ == "__main__":
    cli()
