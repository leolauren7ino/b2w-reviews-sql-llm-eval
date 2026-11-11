"""Adaptador: faz um endpoint compatível com OpenAI (Gemini, Ollama...) imitar o
client.messages.create do SDK da Anthropic, para o llm.py funcionar sem mudanças."""
import os, threading, time
from types import SimpleNamespace as NS

class OpenAICompat:
    def __init__(self, base_url, api_key, min_interval=0.0):
        from openai import OpenAI
        self._c = OpenAI(base_url=base_url, api_key=api_key)
        self._lock, self._last, self._gap = threading.Lock(), 0.0, min_interval
        self.messages = self

    def create(self, *, model, max_tokens, system, messages, **_ignorado):
        with self._lock:  # espaça as chamadas para respeitar o limite por minuto
            espera = self._last + self._gap - time.monotonic()
            if espera > 0:
                time.sleep(espera)
            self._last = time.monotonic()
        r = self._c.chat.completions.create(
            model=model, max_tokens=max(max_tokens, 4096),
            messages=[{"role": "system", "content": system}, *messages])
        ch = r.choices[0]
        stop = {"length": "max_tokens", "content_filter": "refusal"}.get(ch.finish_reason, "end_turn")
        return NS(content=[NS(type="text", text=ch.message.content or "")], stop_reason=stop)

def make_client():
    if os.getenv("LLM_PROVIDER", "anthropic") == "anthropic":
        import anthropic
        return anthropic.Anthropic()
    return OpenAICompat(os.environ["LLM_BASE_URL"], os.getenv("LLM_API_KEY", "x"),
                        float(os.getenv("LLM_MIN_INTERVAL", "0")))