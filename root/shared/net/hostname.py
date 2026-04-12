# Хост из URL и нормализация строки хоста - одна точка в net.

from urllib.parse import urlparse


def normalize_hostname(host: str) -> str:
    # lower, strip, без ведущего www - ключ для реестров и сравнения
    key = host.strip().lower()
    if key.startswith("www."):
        key = key[4:]
    return key


def get_hostname(url: str) -> str | None:
    # Hostname из URL - схема опциональна, затем normalize_hostname
    if not isinstance(url, str) or not url:
        return None
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            parsed = urlparse("http://" + url)
        raw = parsed.hostname
        if not raw:
            return None
        result = normalize_hostname(raw)
        if not result:
            return None
        return result
    except Exception:
        return None
