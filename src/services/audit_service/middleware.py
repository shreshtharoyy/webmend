MAX_REQUEST_BODY_BYTES = 4 * 1024 * 1024


class RequestBodySizeLimitMiddleware:
    def __init__(self, app, max_body_bytes: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if not (
            scope["type"] == "http"
            and scope["method"] == "POST"
            and scope["path"] == "/audit"
        ):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")

        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    await self._reject_request(send)
                    return
            except ValueError:
                pass

        body = bytearray()

        while True:
            message = await receive()

            if message["type"] == "http.disconnect":
                return

            if message["type"] != "http.request":
                continue

            body.extend(message.get("body", b""))

            if len(body) > self.max_body_bytes:
                await self._reject_request(send)
                return

            if not message.get("more_body", False):
                break

        body_bytes = bytes(body)
        body_sent = False

        async def replay_receive():
            nonlocal body_sent

            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": body_bytes,
                    "more_body": False,
                }

            return await receive()

        await self.app(scope, replay_receive, send)

    async def _reject_request(self, send):
        body = b'{"detail":"Request body too large."}'

        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        })

        await send({
            "type": "http.response.body",
            "body": body,
        })