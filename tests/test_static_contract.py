from pathlib import Path


def test_browser_does_not_call_opinet_directly():
    app = Path("public/app.js").read_text(encoding="utf-8")
    assert "opinet.co.kr" not in app
    assert "data.json" in app


def test_workflow_uses_secret_without_printing_it():
    workflow = Path(".github/workflows/refresh-opinet.yml").read_text(encoding="utf-8")
    assert "OPINET_API_KEY" in workflow
    assert "workflow_dispatch" in workflow
    assert "allow_partial" in workflow
