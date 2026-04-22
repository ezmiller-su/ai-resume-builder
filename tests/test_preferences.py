"""
Placeholder tests for preferences.py.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.application_generator.preferences import (
    load_default_preferences,
    merge_preferences,
    get_preferences,
)


def test_load_default_preferences_returns_dict():
    prefs = load_default_preferences()
    assert isinstance(prefs, dict)
    assert len(prefs) > 0


def test_load_default_preferences_has_tone():
    prefs = load_default_preferences()
    assert "tone" in prefs


def test_merge_preferences_user_overrides_default():
    defaults = {"tone": "professional", "max_bullets": 5}
    user = {"max_bullets": 3}
    merged = merge_preferences(defaults, user)
    assert merged["max_bullets"] == 3
    assert merged["tone"] == "professional"


def test_merge_preferences_session_overrides_user():
    defaults = {"tone": "professional"}
    user = {"tone": "casual"}
    session = {"tone": "formal"}
    merged = merge_preferences(defaults, user, session_overrides=session)
    assert merged["tone"] == "formal"


def test_merge_preferences_no_overrides():
    defaults = {"tone": "professional"}
    merged = merge_preferences(defaults, {})
    assert merged == defaults


def test_get_preferences_no_user_returns_defaults():
    prefs = get_preferences()
    assert isinstance(prefs, dict)
    assert "tone" in prefs
