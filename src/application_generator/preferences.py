"""
User preference loading, saving, and merging.

Preferences are stored as structured JSON files — NOT in vector memory.

File layout:
  data/preferences/default_preferences.json   <- shipped defaults
  data/preferences/<user_id>.json             <- per-user overrides (created on save)

Merge priority (lowest to highest):
  defaults  <  per-user file  <  session overrides passed at call time
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Resolve the data/preferences directory relative to this file's package root
_PACKAGE_ROOT = Path(__file__).parent.parent.parent   # src/application_generator -> repo root
_PREFS_DIR = _PACKAGE_ROOT / "data" / "preferences"
_DEFAULT_PREFS_PATH = _PREFS_DIR / "default_preferences.json"


def load_default_preferences() -> Dict[str, Any]:
    """
    Load the shipped default preference profile from data/preferences/default_preferences.json.

    Returns:
        Dict of default preference key/value pairs.

    Raises:
        FileNotFoundError: if default_preferences.json is missing from the repo.
    """
    if not _DEFAULT_PREFS_PATH.exists():
        raise FileNotFoundError(
            f"Default preferences file not found at {_DEFAULT_PREFS_PATH}. "
            "Ensure data/preferences/default_preferences.json is committed to the repo."
        )
    with open(_DEFAULT_PREFS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Load per-user preference overrides from data/preferences/<user_id>.json.

    Args:
        user_id: Identifier for the user (e.g. a username or session token).

    Returns:
        Dict of user-specific preference overrides, or empty dict if no file exists.

    TODO: Consider encrypting or hashing user_id in the filename for privacy.
    TODO: Add validation against a known preference schema before returning.
    """
    user_prefs_path = _PREFS_DIR / f"{user_id}.json"
    if not user_prefs_path.exists():
        return {}
    with open(user_prefs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_preferences(user_id: str, preferences: Dict[str, Any]) -> None:
    """
    Persist user-specific preferences to data/preferences/<user_id>.json.

    Args:
        user_id:     Identifier for the user.
        preferences: Full preference dict to save (will overwrite any existing file).

    TODO: Validate preferences against known keys before saving to avoid silently
          storing unknown fields.
    TODO: Consider atomic write (write to .tmp then rename) to avoid corrupt files.
    """
    _PREFS_DIR.mkdir(parents=True, exist_ok=True)
    user_prefs_path = _PREFS_DIR / f"{user_id}.json"
    with open(user_prefs_path, "w", encoding="utf-8") as f:
        json.dump(preferences, f, indent=2)


def merge_preferences(
    defaults: Dict[str, Any],
    user_prefs: Dict[str, Any],
    session_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Merge preference layers in priority order: defaults < user_prefs < session_overrides.

    Args:
        defaults:          Output of load_default_preferences().
        user_prefs:        Output of load_user_preferences().
        session_overrides: Optional per-request overrides (e.g. from Streamlit UI sliders).

    Returns:
        Merged preference dict with higher-priority values winning on key conflicts.

    TODO: Support nested dict merging (deep merge) if preferences grow hierarchical.
    """
    merged = {**defaults, **user_prefs}
    if session_overrides:
        merged = {**merged, **session_overrides}
    return merged


def get_preferences(
    user_id: Optional[str] = None,
    session_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function: load and merge all preference layers in one call.

    Args:
        user_id:          Optional user identifier. If None, only defaults are used.
        session_overrides: Optional per-request overrides.

    Returns:
        Fully merged preference dict ready to pass into generation functions.
    """
    defaults = load_default_preferences()
    user_prefs = load_user_preferences(user_id) if user_id else {}
    return merge_preferences(defaults, user_prefs, session_overrides)
