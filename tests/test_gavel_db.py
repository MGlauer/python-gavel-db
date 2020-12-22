from click.testing import CliRunner

from gavel.cli import cli


def test_main():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
