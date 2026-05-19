"""Local static web server for the controlled mini-web."""

from __future__ import annotations

import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class LocalWebServer:
    """Serve local_web pages from a background thread."""

    def __init__(self, root_dir: Path, host: str = "127.0.0.1", port: int = 0) -> None:
        self.root_dir = Path(root_dir)
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("Local web server has not been started")
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def start(self) -> str:
        if self._server is not None:
            return self.base_url

        handler = functools.partial(
            SimpleHTTPRequestHandler,
            directory=str(self.root_dir),
        )
        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="market-research-local-web",
            daemon=True,
        )
        self._thread.start()
        return self.base_url

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        self._thread = None
