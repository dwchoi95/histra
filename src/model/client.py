"""Minimal Ollama client (the only backend the PoC needs): POST /api/generate."""
import json, os, urllib.error, urllib.request
from dataclasses import dataclass


@dataclass
class GenerationResult:
    text: str


class ModelClient:
    def __init__(self, model, *, mode="preflight", endpoint=None, timeout=300.0):
        self.model = model
        self.mode = mode                  # only "preflight" (Ollama) is implemented
        self.endpoint = endpoint
        self.timeout = timeout

    def generate(self, prompt, *, temperature=0.2, max_tokens=-1, think=None, num_ctx=8192) -> GenerationResult:
        base = self.endpoint or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        url = base.rstrip("/") + "/api/generate"
        # num_ctx bounds the KV cache: the model's default 131072 makes every call
        # ~8x slower; our prompts fit easily in 8192.
        payload = {"model": self.model, "prompt": prompt, "stream": False,
                   "options": {"temperature": temperature, "num_predict": max_tokens,
                               "num_ctx": num_ctx}}
        if think is not None:              # thinking models: False skips the (slow) reasoning trace
            payload["think"] = think
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"ollama call failed: {exc}") from exc
        return GenerationResult(text=data.get("response", ""))
