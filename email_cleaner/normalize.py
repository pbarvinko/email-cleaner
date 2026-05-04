from __future__ import annotations

import re
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime

from bs4 import BeautifulSoup

from .models import NormalizedEmail

HEADER_NAMES = ("List-Unsubscribe", "Precedence", "X-Mailer", "X-Priority")


def normalize_email(raw_message: bytes, message_id: str, snippet_length: int) -> NormalizedEmail:
    message = BytesParser(policy=policy.default).parsebytes(raw_message)
    sender_name, sender_email = _parse_sender(message.get("From"))
    date_value = message.get("Date")
    normalized_date = None
    if date_value:
        try:
            normalized_date = parsedate_to_datetime(date_value).isoformat()
        except Exception:
            normalized_date = date_value

    headers = {name: _decode_header_value(message.get(name)) for name in HEADER_NAMES if message.get(name)}
    return NormalizedEmail(
        message_id=message.get("Message-ID") or message_id,
        from_name=sender_name,
        from_email=sender_email,
        subject=_decode_header_value(message.get("Subject")),
        date=normalized_date,
        snippet=_build_snippet(message, snippet_length),
        headers=headers,
    )


def _decode_header_value(value: str | None) -> str | None:
    if value is None:
        return None
    return str(make_header(decode_header(value))).strip()


def _parse_sender(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    parsed = getaddresses([value])
    if not parsed:
        return None, None
    name, email_address = parsed[0]
    return name or None, email_address or None


def _build_snippet(message, snippet_length: int) -> str:
    text_parts: list[str] = []
    html_parts: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            content_type = part.get_content_type()
            payload = _part_text(part)
            if not payload:
                continue
            if content_type == "text/plain":
                text_parts.append(payload)
            elif content_type == "text/html":
                html_parts.append(payload)
    else:
        payload = _part_text(message)
        if message.get_content_type() == "text/html":
            html_parts.append(payload)
        else:
            text_parts.append(payload)

    text = "\n".join(text_parts).strip()
    if not text and html_parts:
        text = "\n".join(_html_to_text(part) for part in html_parts)

    collapsed = re.sub(r"\s+", " ", text).strip()
    if not collapsed:
        collapsed = "(No readable content extracted)"
    return collapsed[:snippet_length]


def _part_text(part) -> str:
    try:
        return part.get_content()
    except Exception:
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="ignore")


def _html_to_text(value: str) -> str:
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(" ", strip=True)
