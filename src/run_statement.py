from decimal import Decimal

from .statement_service import AccountStatement, Appointment, LineItem, generate_pdf, safe_appointment_notification


def main() -> None:
    statement = AccountStatement(
        account_id="acct-42",
        patient_name="Maya Chen",
        period="2026-08",
        items=(LineItem("Consultation", Decimal("120.00")), LineItem("Lab review", Decimal("35.00"))),
    )
    print(generate_pdf(statement))
    appointment = Appointment("Maya", __import__("datetime").date(2026, 9, 18), __import__("datetime").time(9, 30), "follow-up", "555-0100")
    print(safe_appointment_notification(appointment))


if __name__ == "__main__":
    main()
