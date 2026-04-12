# Нормализованный hostname из URL: lower, без ведущего www, поддержка URL без схемы.

from urllib.parse import urlparse


def get_hostname(url: str) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            parsed = urlparse("http://" + url)
        host = parsed.hostname
        if not host:
            return None
        host = host.lower().strip()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return None
