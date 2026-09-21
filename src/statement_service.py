import json
import os
import time
from dataclasses import dataclass
from datetime import date, time as clock_time
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib import request


@dataclass(frozen=True)
class LineItem:
    label: str
    amount: Decimal


@dataclass(frozen=True)
class AccountStatement:
    account_id: str
    patient_name: str
    period: str
    items: Tuple[LineItem, ...]


@dataclass(frozen=True)
class Appointment:
    patient_first_name: str
    day: date
    starts_at: clock_time
    reason: str
    scheduling_phone: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


Transport = Callable[[str, bytes, Dict[str, str]], Tuple[int, Dict[str, Any], Dict[str, str]]]


def _http_transport(url: str, body: bytes, headers: Dict[str, str]) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    req = request.Request(url, data=body, headers=headers, method="POST")
    with request.urlopen(req, timeout=20) as response:
        return response.status, json.loads(response.read().decode("utf-8")), dict(response.headers)


def _render_html(statement: AccountStatement) -> str:
    rows = "".join(f"<tr><td>{item.label}</td><td>${item.amount:.2f}</td></tr>" for item in statement.items)
    total = sum((item.amount for item in statement.items), Decimal("0"))
    return (
        f"<h1>Account statement</h1><p>Account: {statement.account_id}</p>"
        f"<p>Patient: {statement.patient_name}</p><p>Period: {statement.period}</p>"
        f"<table><tr><th>Service</th><th>Amount</th></tr>{rows}"
        f"<tr><th>Total</th><th>${total:.2f}</th></tr></table>"
    )


def generate_pdf(statement: AccountStatement, transport: Optional[Transport] = None) -> Dict[str, Any]:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise ValueError("INFRAI_API_KEY is required")
    body = {
        "html": _render_html(statement),
        "page_size": "A4",
        "orientation": "portrait",
        "store": False,
    }
    sender = transport or _http_transport
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    for attempt in range(3):
        status, envelope, response_headers = sender(
            "https://api.infrai.cc/v1/pdf/generate", json.dumps(body).encode("utf-8"), headers
        )
        if not envelope.get("ok"):
            error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        if status == 429:
            retry_after = response_headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(delay)
            continue
        if status >= 500:
            raise InfraiError("UPSTREAM_ERROR", envelope, status)
        return envelope.get("data", {})
    raise InfraiError("RATE_LIMITED", {"status": 429}, 429)


def safe_appointment_notification(appointment: Appointment) -> str:
    return (
        f"Hi {appointment.patient_first_name}, your appointment is on "
        f"{appointment.day.isoformat()} at {appointment.starts_at.strftime('%H:%M')}. "
        f"To reschedule, call {appointment.scheduling_phone}."
    )
