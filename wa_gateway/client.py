"""HTTP client for interacting with the configured WhatsApp provider."""
from typing import Any, Dict
import httpx

from wa_gateway.config import get_settings


class WhatsAppError(Exception):
    """Raised when the WhatsApp provider returns an error response."""


class WhatsAppClient:
    """Client for sending WhatsApp messages via the configured provider."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send a plain text message."""
        payload = self._build_text_payload(to=to, text=text)
        return await self._post_message(payload)

    async def send_template(self, to: str, template_name: str, vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send a template-based message."""
        payload = self._build_template_payload(to=to, template_name=template_name, vars=vars)
        return await self._post_message(payload)

    def _build_text_payload(self, to: str, text: str) -> Dict[str, Any]:
        if self.settings.wa_provider == "cloud_api":
            return {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            }
        if self.settings.wa_provider == "twilio":
            # Twilio WhatsApp uses the Messages resource under /Accounts/{AccountSid}/Messages.json
            # with form-encoded body containing "From", "To", and "Body" fields.
            return {
                "From": self.settings.wa_default_from,
                "To": to,
                "Body": text,
            }
        raise WhatsAppError(f"Unsupported provider: {self.settings.wa_provider}")

    def _build_template_payload(self, to: str, template_name: str, vars: Dict[str, Any]) -> Dict[str, Any]:
        if self.settings.wa_provider == "cloud_api":
            components = []
            if vars:
                components.append(
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": str(value)} for value in vars.values()],
                    }
                )
            return {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {"name": template_name, "language": {"code": "en_US"}, "components": components},
            }
        if self.settings.wa_provider == "twilio":
            # Twilio templates (HSM) would be sent using the same Messages API with the template body composed server-side.
            # Implementers should expand the template with provided vars before sending in the Body field.
            body = template_name.format(**vars)
            return {
                "From": self.settings.wa_default_from,
                "To": to,
                "Body": body,
            }
        raise WhatsAppError(f"Unsupported provider: {self.settings.wa_provider}")

    async def _post_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        auth = None
        url = self._build_url()

        if self.settings.wa_provider == "cloud_api":
            headers["Authorization"] = f"Bearer {self.settings.wa_api_token}"
        elif self.settings.wa_provider == "twilio":
            # Twilio expects HTTP Basic auth with Account SID as username and auth token as password.
            auth = httpx.BasicAuth(username=self.settings.wa_default_from, password=self.settings.wa_api_token)
        else:
            raise WhatsAppError(f"Unsupported provider: {self.settings.wa_provider}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload if self.settings.wa_provider == "cloud_api" else None,
                                         data=payload if self.settings.wa_provider == "twilio" else None,
                                         headers=headers, auth=auth)
            if response.is_success:
                return response.json()

        raise WhatsAppError(f"WhatsApp API error {response.status_code}: {response.text}")

    def _build_url(self) -> str:
        if self.settings.wa_provider == "cloud_api":
            return f"{self.settings.wa_api_base_url.rstrip('/')}/messages"
        if self.settings.wa_provider == "twilio":
            # Example: https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json
            return f"{self.settings.wa_api_base_url.rstrip('/')}/Messages.json"
        raise WhatsAppError(f"Unsupported provider: {self.settings.wa_provider}")
