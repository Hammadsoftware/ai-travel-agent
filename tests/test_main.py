from fastapi.testclient import TestClient

import app.main as main


def test_search_accepts_query(monkeypatch):
    def fake_invoke(payload):
        assert payload["query"] == "test"
        return "stubbed-result"

    monkeypatch.setattr(main.web_search, "invoke", fake_invoke)

    client = TestClient(main.app)
    response = client.post("/search", json={"query": "test"})

    assert response.status_code == 200
    assert response.json() == {"query": "test", "result": "stubbed-result"}
