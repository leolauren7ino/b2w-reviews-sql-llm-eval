"""Chamada ao LLM com saída JSON validada, retry e log.

Falhas tratadas (cada uma vira um registro, nunca uma exceção silenciosa):
  - texto com cercas ```json ou prosa em volta do JSON  -> extrai o objeto
  - JSON quebrado / campos fora da taxonomia            -> reenvia com a mensagem de erro
  - stop_reason == refusal / max_tokens                 -> conta como tentativa falha
  - erros de API                                        -> backoff exponencial (o SDK já faz retry de 429/5xx)
"""
import json, logging, re, time
from dataclasses import dataclass, field
from pydantic import ValidationError
from schema import Prediction

log = logging.getLogger("classificador")
DEFAULT_MODEL = "claude-opus-5-5"   # trocável via --model; ver README
MAX_TENTATIVAS = 3

@dataclass
class Result:
    prediction: Prediction | None
    attempts: int
    raw: str
    error: str | None
    latency_ms: int
    errors_seen: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.prediction is not None

def extract_json(text: str) -> dict:
    """Aceita JSON puro, JSON dentro de cercas de código, ou com prosa em volta."""
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    else:
        i, j = t.find("{"), t.rfind("}")
        if i != -1 and j > i:
            t = t[i:j + 1]
    return json.loads(t)

def _text_of(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

def classify(client, review: str, system: str, model: str = DEFAULT_MODEL,
             max_attempts: int = MAX_TENTATIVAS, sleep=time.sleep) -> Result:
    messages = [{"role": "user", "content": f"Avaliação:\n\"\"\"\n{review}\n\"\"\""}]
    t0 = time.monotonic()
    errors: list[str] = []
    raw = ""
    for attempt in range(1, max_attempts + 1):
        try:
            resp = client.messages.create(
                model=model, max_tokens=1024, system=system, messages=messages,
                output_config={"effort": "low"},
            )
        except Exception as e:  # erros de API além dos retries do SDK
            errors.append(f"api:{type(e).__name__}")
            log.warning("tentativa %d: erro de API %s", attempt, e)
            sleep(2 ** attempt)
            continue
        raw = _text_of(resp)
        stop = getattr(resp, "stop_reason", None)
        if stop in ("refusal", "max_tokens"):
            errors.append(f"stop:{stop}")
            log.warning("tentativa %d: stop_reason=%s", attempt, stop)
            continue
        try:
            pred = Prediction.model_validate(extract_json(raw))
            return Result(pred, attempt, raw, None, int((time.monotonic() - t0) * 1000), errors)
        except (json.JSONDecodeError, ValidationError) as e:
            kind = "json_quebrado" if isinstance(e, json.JSONDecodeError) else "fora_do_esquema"
            errors.append(kind)
            log.warning("tentativa %d: %s | resposta=%r", attempt, kind, raw[:200])
            # devolve o erro ao modelo para ele corrigir
            messages += [{"role": "assistant", "content": raw or "(vazio)"},
                         {"role": "user", "content": f"Resposta inválida ({kind}). "
                          "Responda só com o JSON no formato pedido, usando exatamente os valores permitidos."}]
    return Result(None, max_attempts, raw, ";".join(errors) or "desconhecido",
                  int((time.monotonic() - t0) * 1000), errors)
