from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from src.services.browser_service.browser import inspect_webpage


HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>WebMend Test Page</title>
</head>
<body>
    <h1>Welcome to WebMend</h1>
    <p>Testing browser automation.</p>
</body>
</html>
"""


class WebMendPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        content = HTML_CONTENT.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def local_webpage():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        WebMendPageHandler,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    host = server.server_address[0]
    port = server.server_address[1]
    url = f"http://{host}:{port}"

    yield url

    server.shutdown()
    server.server_close()
    thread.join(timeout=5)

def test_inspect_webpage_returns_title(allow_local_test_url):
    result = inspect_webpage(allow_local_test_url)
    assert result["title"] == "WebMend Test Page"


def test_inspect_webpage_returns_html(allow_local_test_url):
    result = inspect_webpage(allow_local_test_url)
    assert "<h1>Welcome to WebMend</h1>" in result["html"]


def test_inspect_webpage_returns_url(allow_local_test_url):
    result = inspect_webpage(allow_local_test_url)
    assert result["url"] == f"{allow_local_test_url}/"

def test_inspect_webpage_rejects_localhost():
    with pytest.raises(ValueError):
        inspect_webpage("http://localhost:8000")


def test_inspect_webpage_rejects_private_ip():
    with pytest.raises(ValueError):
        inspect_webpage("http://192.168.1.1")

@pytest.fixture
def allow_local_test_url(monkeypatch, local_webpage):
    def test_url_validator(url):
        if url != local_webpage:
            raise ValueError("Only the test server URL is allowed.")
        return url

    monkeypatch.setattr(
        "src.services.browser_service.browser.validate_url",
        test_url_validator,
    )

    return local_webpage