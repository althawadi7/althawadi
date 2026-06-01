"""Site URL prefix — root domain uses '' (paths like /css/). GitHub subpath used '/althawadi'."""

SITE_PREFIX = ""
SITE_HOME = "/"
SITE_ORIGIN = "https://althawadi.org"


def asset(path: str) -> str:
    """Absolute path for static assets. path: 'css/styles.css' or '/css/styles.css'."""
    path = path.lstrip("/")
    if SITE_PREFIX:
        return f"{SITE_PREFIX}/{path}"
    return f"/{path}"


def page(path: str = "") -> str:
    """Absolute path for internal pages. path: 'about/' or 'about'."""
    path = path.strip("/")
    if not path:
        return SITE_HOME
    if SITE_PREFIX:
        return f"{SITE_PREFIX}/{path}/"
    return f"/{path}/"
