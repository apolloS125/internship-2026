from fastapi import HTTPException, Request
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app.config import Settings

# documentation https://github.com/line/line-bot-sdk-python
async def parse_line_events(request: Request, settings: Settings):
    parser = WebhookParser(settings.line_channel_secret)
    signature = request.headers.get("x-line-signature", "")
    body = await request.body()
    pass