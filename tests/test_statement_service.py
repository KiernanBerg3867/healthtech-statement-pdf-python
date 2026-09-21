import json
from datetime import date, time
from decimal import Decimal

from src.statement_service import AccountStatement, Appointment, LineItem, generate_pdf, safe_appointment_notification


def test_statement_request_and_safe_notification(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    seen = {}

    def transport(url, body, headers):
        seen.update(url=url, body=json.loads(body), headers=headers)
        return 200, {"ok": True, "data": {"pdf": "encoded"}, "error": None, "metadata": {}}, {}

    statement = AccountStatement("acct-42", "Maya Chen", "2026-08", (LineItem("Consultation", Decimal("120.00")),))
    assert generate_pdf(statement, transport) == {"pdf": "encoded"}
    assert seen["url"].endswith("/v1/pdf/generate")
    assert seen["body"]["page_size"] == "A4"
    assert seen["headers"]["Authorization"] == "Bearer test-key"

    appointment = Appointment("Maya", date(2026, 9, 18), time(9, 30), "sensitive detail", "555-0100")
    message = safe_appointment_notification(appointment)
    assert "Maya" in message and "sensitive detail" not in message
