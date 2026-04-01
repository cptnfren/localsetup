"""
Purpose: Tests for Scrapling adapter parser and refresh flow.
Created: 2026-03-16
Last Updated: 2026-03-16
"""

from __future__ import annotations

from _localsetup.tools.scrapling_helper import adapter_parser
from _localsetup.tools.scrapling_helper import config as scrapling_config
from _localsetup.tools.scrapling_helper import main as scrapling_main


def test_parse_current_features_uses_help_output(monkeypatch) -> None:
    cfg = scrapling_config.load_config()

    def fake_run_help(_cfg, args):
        if args == ["--help"]:
            return "--help output\n--flag-x (deprecated)\n"
        if args == ["extract", "--help"]:
            return "extract help\n--extract-flag (experimental)\n"
        return "spider help\n"

    monkeypatch.setattr(adapter_parser, "_run_scrapling_help", fake_run_help)
    state = adapter_parser.parse_current_features(cfg)
    assert "top" in state.cli_commands
    assert "--flag-x" in state.flags
    assert "deprecated" in state.flags["--flag-x"]["tags"]
    assert "--extract-flag" in state.flags
    assert "experimental" in state.flags["--extract-flag"]["tags"]


def test_refresh_adapters_dry_run_does_not_write(monkeypatch) -> None:
    cfg = scrapling_config.load_config()

    def fake_parse(_cfg):
        return adapter_parser.AdapterState(
            supported_versions=[],
            cli_commands={"top": {"help": "help"}},
            fetch_modes={},
            spiders={},
            mcp_features={},
            flags={"--flag-x": {"description": "", "tags": []}},
        )

    monkeypatch.setattr(scrapling_main, "parse_current_features", fake_parse, raising=False)
    result = scrapling_main.refresh_adapters(dry_run=True)
    assert result["applied"] is False
    assert "diff" in result

