"""FastAPI HTTP layer for the WhatsApp gateway service."""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from wa_gateway.client import WhatsAppClient, WhatsAppError

app = FastAPI(title="WhatsApp Gateway")

logger = logging.getLogger("wa_gateway")
logging.basicConfig(level=logging.INFO)


class SendTextRequest(BaseModel):
    to: str
    text: str


class SendTemplateRequest(BaseModel):
    to: str
    template_name: str
    vars: dict


def _client() -> WhatsAppClient:
    return WhatsAppClient()


@app.post("/api/send-text")
async def send_text(payload: SendTextRequest):
    client = _client()
    try:
        provider_response = await client.send_message(to=payload.to, text=payload.text)
        logger.info("Sent WhatsApp text to %s", payload.to)
        return {"status": "sent", "provider_response": provider_response}
    except WhatsAppError as exc:  # pragma: no cover - simple pass through
        logger.exception("Failed to send WhatsApp text to %s", payload.to)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/send-template")
async def send_template(payload: SendTemplateRequest):
    client = _client()
    try:
        provider_response = await client.send_template(
            to=payload.to, template_name=payload.template_name, vars=payload.vars
        )
        logger.info("Sent WhatsApp template %s to %s", payload.template_name, payload.to)
        return {"status": "sent", "provider_response": provider_response}
    except WhatsAppError as exc:  # pragma: no cover - simple pass through
        logger.exception("Failed to send WhatsApp template %s to %s", payload.template_name, payload.to)
        raise HTTPException(status_code=400, detail=str(exc))


# Docker deployment hint:
# Service name: wa-gateway
# Expose port: 9000
# Required environment variables: WA_PROVIDER, WA_API_BASE_URL, WA_API_TOKEN, WA_DEFAULT_FROM

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("wa_gateway.http_api:app", host="0.0.0.0", port=9000, reload=True)
