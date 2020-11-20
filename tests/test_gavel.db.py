from click.testing import CliRunner

from gavel_db.cli import cli


def test_main():
    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.output == "()\n"
    assert result.exit_code == 0
