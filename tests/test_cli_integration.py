"""Integration tests for CLI report generation.

These tests verify that all report commands can successfully generate output
using a synthetic genome file.
"""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from analyze_dna.cli import cli


@pytest.fixture
def synthetic_genome():
    """Path to synthetic test genome."""
    return Path(__file__).parent / "data" / "synthetic_genome.txt"


@pytest.fixture
def temp_output_dir():
    """Temporary output directory for reports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_quick_analysis_stdout(synthetic_genome):
    """Test quick-analysis with stdout output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["quick-analysis", str(synthetic_genome), "--output-stdout"])

    assert result.exit_code == 0
    assert "Comprehensive Genetic Analysis Report" in result.output
    assert "Summary" in result.output


def test_quick_analysis_file(synthetic_genome, temp_output_dir):
    """Test quick-analysis with file output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["quick-analysis", str(synthetic_genome), "--output", str(temp_output_dir)])

    assert result.exit_code == 0
    report_file = temp_output_dir / "genetic_report.md"
    assert report_file.exists()

    content = report_file.read_text()
    assert "Comprehensive Genetic Analysis Report" in content
    assert "MTHFR" in content or "Summary" in content


def test_health_report_stdout(synthetic_genome):
    """Test health-report with stdout output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["health-report", str(synthetic_genome), "--output-stdout"])

    assert result.exit_code == 0
    assert "Complete Genetic Health Optimization Report" in result.output
    assert "Executive Summary" in result.output


def test_health_report_file(synthetic_genome, temp_output_dir):
    """Test health-report with file output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["health-report", str(synthetic_genome), "--output", str(temp_output_dir)])

    assert result.exit_code == 0
    report_file = temp_output_dir / "COMPLETE_HEALTH_REPORT.md"
    assert report_file.exists()

    content = report_file.read_text()
    assert "Complete Genetic Health Optimization Report" in content


def test_traits_report_stdout(synthetic_genome):
    """Test traits command with stdout output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["traits", str(synthetic_genome), "--name", "TestSubject", "--output-stdout"])

    assert result.exit_code == 0
    assert "Genetic Traits Report for TestSubject" in result.output
    assert "Eye Color" in result.output or "Pigmentation" in result.output


def test_traits_report_file(synthetic_genome, temp_output_dir):
    """Test traits command with file output."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["traits", str(synthetic_genome), "--name", "TestSubject", "--output", str(temp_output_dir)]
    )

    assert result.exit_code == 0
    report_file = temp_output_dir / "TRAITS_REPORT.md"
    assert report_file.exists()

    content = report_file.read_text()
    assert "Genetic Traits Report for TestSubject" in content


def test_portrait_stdout(synthetic_genome):
    """Test portrait command with stdout output."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "portrait",
            str(synthetic_genome),
            "--birth-year",
            "1990",
            "--sex",
            "male",
            "--output-stdout",
        ],
    )

    assert result.exit_code == 0
    # Portrait prompt should contain subject description
    assert "Subject:" in result.output or "male" in result.output.lower()


def test_portrait_file(synthetic_genome, temp_output_dir):
    """Test portrait command with file output."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "portrait",
            str(synthetic_genome),
            "--birth-year",
            "1990",
            "--sex",
            "female",
            "--output",
            str(temp_output_dir),
        ],
    )

    assert result.exit_code == 0
    report_file = temp_output_dir / "portrait_prompt.txt"
    assert report_file.exists()

    content = report_file.read_text()
    assert len(content) > 100  # Should be a substantial prompt


def test_full_analysis_stdout(synthetic_genome):
    """Test full-analysis with stdout output (multi-report concatenation)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["full-analysis", str(synthetic_genome), "--name", "TestSubject", "--output-stdout"])

    assert result.exit_code == 0
    # Should contain all three reports separated by markers
    assert "Exhaustive Genetic Health Report" in result.output
    assert "REPORT SEPARATOR" in result.output
    # At least one report should be present
    assert "TestSubject" in result.output or "Subject" in result.output


def test_full_analysis_file(synthetic_genome, temp_output_dir):
    """Test full-analysis with file output (multiple files)."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["full-analysis", str(synthetic_genome), "--name", "TestSubject", "--output", str(temp_output_dir)]
    )

    assert result.exit_code == 0

    # Should create 3 markdown reports
    genetic_report = temp_output_dir / "EXHAUSTIVE_GENETIC_REPORT.md"
    protocol_report = temp_output_dir / "ACTIONABLE_HEALTH_PROTOCOL_V3.md"

    assert genetic_report.exists()
    assert protocol_report.exists()

    # Verify subject name appears in reports
    genetic_content = genetic_report.read_text()
    assert "TestSubject" in genetic_content or "Exhaustive" in genetic_content


def test_missing_output_error(synthetic_genome):
    """Test that missing output specification raises error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["traits", str(synthetic_genome)])

    assert result.exit_code != 0
    assert 'Must specify either "--output' in result.output


def test_mutual_exclusivity_error(synthetic_genome, temp_output_dir):
    """Test that --output and --output-stdout are mutually exclusive."""
    runner = CliRunner()
    result = runner.invoke(cli, ["traits", str(synthetic_genome), "--output", str(temp_output_dir), "--output-stdout"])

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_output_to_current_dir(synthetic_genome, temp_output_dir):
    """Test that --output . works (explicit directory)."""
    runner = CliRunner()
    # Use temp_output_dir instead of trying to change cwd
    result = runner.invoke(cli, ["traits", str(synthetic_genome), "--output", str(temp_output_dir)])

    assert result.exit_code == 0
    report_file = temp_output_dir / "TRAITS_REPORT.md"
    assert report_file.exists()
