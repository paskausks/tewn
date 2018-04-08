#!/usr/bin/env python3
import pytest
from click.testing import CliRunner
from tewn import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    result = runner.invoke(cli.main)
    if result.exit_code == 0:
        assert 'Input initialized.' in result.output
    else:
        # Travis CI test runner doesn't have a default audio input device set.
        assert result.exit_code == 1
        assert 'Couldn\'t get default' in result.output

    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
