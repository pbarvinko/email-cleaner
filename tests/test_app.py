from email_cleaner.app import run_app


def test_run_app_binds_to_fixed_host(monkeypatch):
    recorded = {}

    class FakeApp:
        config = {"SETTINGS": type("Settings", (), {"server_port": 4321})()}

        def run(self, *, host, port):
            recorded["host"] = host
            recorded["port"] = port

    monkeypatch.setattr("email_cleaner.app.create_app", lambda: FakeApp())

    run_app()

    assert recorded == {"host": "0.0.0.0", "port": 4321}
