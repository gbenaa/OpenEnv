from market_research_env.server.local_web_server import LocalWebServer


def test_local_web_server_starts_and_stops(tmp_path):
    (tmp_path / "index.html").write_text("<html><body>Hello</body></html>", encoding="utf-8")
    server = LocalWebServer(tmp_path)
    base_url = server.start()

    try:
        assert base_url.startswith("http://127.0.0.1:")
    finally:
        server.stop()
