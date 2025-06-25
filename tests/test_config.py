import os
import pytest

from bot.config import BotConfig

def test_valid_config(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "123456789000000001")
    cfg = BotConfig()
    assert cfg.get_token() == "test-token"
    assert cfg.get_channel_id() == 123456789000000001

def test_missing_token(monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "123")
    with pytest.raises(ValueError):
        BotConfig()

def test_missing_channel(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.delenv("DISCORD_CHANNEL_ID", raising=False)
    with pytest.raises(ValueError):
        BotConfig()

def test_non_numeric_channel(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "notanumber")
    with pytest.raises(ValueError):
        BotConfig()