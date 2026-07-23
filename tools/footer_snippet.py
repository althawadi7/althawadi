#!/usr/bin/env python3
"""Shared site footer markup (Arabic defaults for existing builders)."""

from site_chrome import footer_contact_col as _footer_contact_col
from site_chrome import footer_nav_cols as _footer_nav_cols

BASE = ""


def footer_nav_cols(base: str = BASE) -> str:
    return _footer_nav_cols("ar", base)


def footer_contact_col() -> str:
    return _footer_contact_col("ar", "")
