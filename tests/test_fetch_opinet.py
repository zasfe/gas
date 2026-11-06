from scripts import fetch_opinet


def test_request_uses_current_code_parameter(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"RESULT":{"OIL":[]}}'

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        return FakeResponse()

    monkeypatch.setenv("OPINET_API_KEY", "test-secret")
    monkeypatch.setattr(fetch_opinet.urllib.request, "urlopen", fake_urlopen)
    fetch_opinet._request("areaCode.do", {"area": "02"})

    assert "code=test-secret" in captured["url"]
    assert "certkey=" not in captured["url"]
