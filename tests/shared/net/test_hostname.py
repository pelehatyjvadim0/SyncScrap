# Тесты нормализации хоста - основа для одного ключа в реестре профилей и стратегий парсера.
# Anti-fraud цепочка начинается с одинакового hostname для URL с www и без.

import pytest

from root.shared.net.hostname import get_hostname, normalize_hostname


def test_normalize_hostname_strips_www_and_lowercase():
    # Один сайт - один ключ avito.ru независимо от регистра и www
    assert normalize_hostname("WWW.Avito.RU") == "avito.ru"
    assert normalize_hostname("  www.avito.ru  ") == "avito.ru"
    assert normalize_hostname("avito.ru") == "avito.ru"


def test_get_hostname_from_https_url_with_www():
    # URL как в браузере - на выходе тот же ключ что и у короткой формы хоста
    assert get_hostname("https://www.avito.ru/moskva") == "avito.ru"


def test_get_hostname_without_scheme():
    # Поддержка строки host/path без схемы - как в части пайплайнов
    assert get_hostname("books.toscrape.com/catalogue/") == "books.toscrape.com"


def test_get_hostname_invalid_returns_none():
    # Пустая строка - без hostname
    assert get_hostname("") is None
    assert get_hostname("   ") is None


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com:8443/path", "example.com"),
        ("http://sub.example.com", "sub.example.com"),
    ],
)
def test_get_hostname_is_parsed_hostname_not_netloc(url: str, expected: str):
    # Берём parsed.hostname - порт не попадает в ключ стратегии
    assert get_hostname(url) == expected
