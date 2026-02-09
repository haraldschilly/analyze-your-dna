import functools
import sys
from pathlib import Path

import click

from . import __version__
from .analyze_genome import run_analyze_genome
from .fast_loader import load_genome_fast
from .full_health_analysis import run_health_analysis
from .generate_portrait_prompt import format_prompt_output, generate_portrait_prompt
from .generate_traits_report import run_traits_report
from .run_full_analysis import run_full_analysis
from .update_clinvar import run_update_clinvar


def write_report(output_dir: Path | None, content: str, filename: str) -> None:
    """Write report content to file or stdout.

    Args:
        output_dir: Directory to write to, or None for stdout
        content: Report content to write
        filename: Filename to use (ignored if output_dir is None)
    """
    if output_dir is None:
        click.echo(content)
    else:
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        click.echo(f"  Written: {path}", err=True)


def output_options(func):
    """Decorator that adds --output and --output-stdout options.

    Commands decorated with this receive an output_dir parameter (Path | None).
    None means stdout mode.
    """

    @click.option(
        "--output-stdout",
        is_flag=True,
        default=False,
        help="Write report to stdout (for piping/LLM consumption).",
    )
    @click.option(
        "--output",
        "-o",
        type=click.Path(path_type=Path),
        default=None,
        help='Directory to save reports (use "." for current dir).',
    )
    @functools.wraps(func)
    def wrapper(*args, output, output_stdout, **kwargs):
        if not output and not output_stdout:
            raise click.UsageError('Must specify either "--output <path>" or "--output-stdout".')
        if output and output_stdout:
            raise click.UsageError('"--output" and "--output-stdout" are mutually exclusive.')

        output_dir = None
        if output:
            output_dir = output.resolve()
            output_dir.mkdir(parents=True, exist_ok=True)

        kwargs["output_dir"] = output_dir
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="analyze-dna")
def cli():
    """Genetic Health Analysis Pipeline CLI."""


@cli.command(name="full-analysis")
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@click.option("--name", "-n", help="Subject name to include in reports")
@output_options
def full_analysis(genome, name, output_dir):
    """Run full genetic health analysis pipeline.

    GENOME is the path to your 23andMe genome file.
    Requires --output <dir> or --output-stdout.
    """
    run_full_analysis(genome, name, output_dir)


@cli.command()
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@click.option("--name", "-n", default="Subject", help="Subject name")
@output_options
def traits(genome, name, output_dir):
    """Generate genetic traits report.

    GENOME is the path to your 23andMe genome file.
    Requires --output <dir> or --output-stdout.
    """
    run_traits_report(genome, name, output_dir)


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
@output_options
def portrait(genome, birth_year, sex, hair_style, target_age, glasses, output_dir):  # pylint: disable=too-many-positional-arguments
    """Generate AI portrait prompts from genetic data.

    GENOME is the path to your 23andMe genome file.
    Requires --output <dir> or --output-stdout.
    """
    click.echo(f"Loading genome from {genome}...", err=True)
    genome_by_rsid, _ = load_genome_fast(genome)
    click.echo(f"✓ Loaded {len(genome_by_rsid):,} SNPs", err=True)

    click.echo("Generating portrait prompt...", err=True)
    prompt_data = generate_portrait_prompt(genome_by_rsid, birth_year, sex, hair_style, target_age, glasses)

    output_text = format_prompt_output(prompt_data)
    write_report(output_dir, output_text, "portrait_prompt.txt")

    click.echo(f"\n✓ Eye color: {prompt_data['subject']}", err=True)


@cli.command(name="quick-analysis")
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@output_options
def quick_analysis(genome, output_dir):
    """Run focused analysis with curated high-impact SNPs.

    GENOME is the path to your 23andMe genome file.
    Requires --output <dir> or --output-stdout.

    Analyzes against ~34 curated SNPs (drug metabolism, clotting, APOE, etc.)
    plus ClinVar and PharmGKB.
    """
    run_analyze_genome(genome, output_dir)


@cli.command(name="health-report")
@click.argument("genome", type=click.Path(exists=True, path_type=Path))
@output_options
def health_report(genome, output_dir):
    """Generate comprehensive health optimization report.

    GENOME is the path to your 23andMe genome file.
    Requires --output <dir> or --output-stdout.

    Analyzes against ~88 curated health SNPs plus PharmGKB drug interactions.
    """
    run_health_analysis(genome, output_dir)


@cli.command(name="update-clinvar")
@click.option("--keep-download", is_flag=True, help="Keep the downloaded variant_summary.txt.gz file")
@click.option("--no-gzip", is_flag=True, help="Don't compress the output TSV file")
@click.option("--skip-download", is_flag=True, help="Skip download if variant_summary.txt.gz already exists")
@click.option("--include-all", is_flag=True, help="Include all variants (default: only clinically actionable)")
def update_clinvar_cmd(keep_download, no_gzip, skip_download, include_all):
    """Download and convert NCBI ClinVar database."""
    run_update_clinvar(keep_download, no_gzip, skip_download, include_all)


def main():
    """Entry point with graceful error handling."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nInterrupted.", err=True)
        sys.exit(130)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
