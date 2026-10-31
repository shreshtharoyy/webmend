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

def test_inspect_webpage_returns_title(local_webpage):
    result = inspect_webpage(local_webpage)
    assert result["title"] == "WebMend Test Page"


def test_inspect_webpage_returns_html(local_webpage):
    result = inspect_webpage(local_webpage)
    assert "<h1>Welcome to WebMend</h1>" in result["html"]


def test_inspect_webpage_returns_url(local_webpage):
    result = inspect_webpage(local_webpage)
    assert result["url"] == f"{local_webpage}/"