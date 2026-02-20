import importlib.util
import io
import json
from pathlib import Path


def load_generate_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "api" / "generate.py"

    spec = importlib.util.spec_from_file_location("api_generate", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DummyHandler:
    def __init__(self, body):
        encoded = body.encode("utf-8")
        self.headers = {"Content-Length": str(len(encoded))}
        self.rfile = io.BytesIO(encoded)
        self.wfile = io.BytesIO()
        self.status_code = None
        self.sent_headers = []

    def send_response(self, code):
        self.status_code = code

    def send_header(self, key, value):
        self.sent_headers.append((key, value))

    def end_headers(self):
        return None

    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        payload = json.dumps({"error": message, "status": status_code})
        self.wfile.write(payload.encode("utf-8"))



def test_post_rejects_invalid_json():
    module = load_generate_module()
    handler = DummyHandler("{invalid json")

    module.handler.do_POST(handler)

    assert handler.status_code == 400
    body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert body["error"] == "Invalid JSON in request body"



def test_post_rejects_empty_prefix():
    module = load_generate_module()
    handler = DummyHandler(json.dumps({"prefix": "  "}))

    module.handler.do_POST(handler)

    assert handler.status_code == 400
    body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert body["error"] == "Missing or empty 'prefix' field"



def test_post_returns_story_on_success(monkeypatch):
    module = load_generate_module()

    monkeypatch.setattr(
        module,
        "load_models",
        lambda: ({"tok": 1}, [("a", "b")], {"u": 1}, {("u", "v"): 1}, {("u", "v", "w"): 1}),
    )
    monkeypatch.setattr(module, "encode", lambda prefix, merges: ["tok1", "tok2"])
    monkeypatch.setattr(module, "generate_story", lambda **kwargs: "یہ ایک ٹیسٹ کہانی ہے")

    handler = DummyHandler(json.dumps({"prefix": "ایک دن", "max_length": 50}, ensure_ascii=False))

    module.handler.do_POST(handler)

    assert handler.status_code == 200
    body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert body["story"] == "یہ ایک ٹیسٹ کہانی ہے"
    assert body["prefix"] == "ایک دن"
