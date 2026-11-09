import socket
import pytest
from src.services.browser_service.security import validate_url


def mock_public_dns(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("93.184.216.34", 80),
            )
        ]

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        fake_getaddrinfo,
    )


def test_validate_https_url(monkeypatch):
    mock_public_dns(monkeypatch)

    url = "https://example.com"

    assert validate_url(url) == url


def test_validate_http_url(monkeypatch):
    mock_public_dns(monkeypatch)

    url = "http://example.com"

    assert validate_url(url) == url


def test_validate_url_strips_whitespace(monkeypatch):
    mock_public_dns(monkeypatch)

    assert validate_url("  https://example.com  ") == "https://example.com"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "ftp://example.com",
        "file:///etc/passwd",
        "example.com",
        "http:///missing-host",
    ],
)
def test_validate_url_rejects_invalid_urls(url):
    with pytest.raises(ValueError):
        validate_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://192.168.1.1",
        "http://10.0.0.1",
        "http://172.16.0.1",
    ],
)
def test_validate_url_rejects_local_addresses(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_validate_url_rejects_credentials():
    with pytest.raises(ValueError):
        validate_url("https://user:password@example.com")


def test_validate_url_accepts_public_ip():
    url = "http://93.184.216.34"

    assert validate_url(url) == url


def test_validate_url_rejects_private_dns_result(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("192.168.1.10", 80),
            )
        ]

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        fake_getaddrinfo,
    )

    with pytest.raises(ValueError):
        validate_url("http://example.com")


def test_validate_url_rejects_dns_failure(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        raise socket.gaierror("DNS resolution failed")

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        fake_getaddrinfo,
    )

    with pytest.raises(ValueError):
        validate_url("https://example.com")