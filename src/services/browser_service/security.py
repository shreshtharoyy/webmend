import ipaddress
import socket
from urllib.parse import urlsplit

def validate_url(url:str):
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")

    try:
        parsed_url = urlsplit(url.strip())
    except ValueError as exc:
        raise ValueError("Invalid URL format.") from exc

    if parsed_url.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed_url.hostname:
        raise ValueError("URL must contain a hostname.")

    if parsed_url.username or parsed_url.password:
        raise ValueError("URLs containing credentials are not allowed.")

    hostname = parsed_url.hostname.rstrip(".").lower()

    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed.")

    try:
        ipaddress.ip_address(hostname)
        addresses = [hostname]
    except ValueError:
        try:
            results = socket.getaddrinfo(
                hostname,
                parsed_url.port or (443 if parsed_url.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
            addresses = list({result[4][0] for result in results})
        except OSError as exc:
            raise ValueError("Hostname could not be resolved.") from exc

    if not addresses:
        raise ValueError("Hostname did not resolve to an IP address.")

    for address in addresses:
        ip = ipaddress.ip_address(address)

        if not ip.is_global:
            raise ValueError("URLs resolving to non-public IP addresses are not allowed.")

    return url.strip()

    