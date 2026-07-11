import httpx
from fastapi import HTTPException, Request
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app.config import Settings

# References:
# https://developers.line.biz/en/docs/messaging-api/verify-webhook-signature/
# https://developers.line.biz/en/reference/messaging-api/#send-reply-message
async def parse_line_events(request: Request, settings: Settings):
    if not settings.line_channel_secret:
        raise HTTPException(status_code=503, detail="LINE channel secret is not set")

    parser = WebhookParser(settings.line_channel_secret)
    signature = request.headers.get("x-line-signature", "")
    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError as error:
        raise HTTPException(status_code=400, detail="Invalid LINE signature") from error

    return [
        event
        for event in events
        if isinstance(event, MessageEvent)
        and isinstance(event.message, TextMessageContent)
    ]


async def reply_to_line(reply_token: str, text: str, settings: Settings) -> None:
    if not settings.line_channel_access_token:
        raise HTTPException(status_code=503,detail="LINE channel access token is not set",)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={
                    "Authorization": (
                        f"Bearer {settings.line_channel_access_token}"
                    ),
                    "Content-Type": "application/json",
                },
                json={
                    "replyToken": reply_token,
                    "messages": [
                        {
                            "type": "text",
                            "text": text[:5000],
                        }
                    ],
                },
                timeout=10,
            )
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise RuntimeError(f"LINE reply failed: {error}") from error
