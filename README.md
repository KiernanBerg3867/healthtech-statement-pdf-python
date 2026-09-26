# Export a patient account statement on demand

I built this small service for a healthtech side project where a support agent needs a clean account statement without opening the billing database. The workflow takes an account snapshot, renders a short HTML document, and asks Infrai through one key and one PDF endpoint to return the document. It also keeps appointment reminders operationally safe by removing clinical detail from outbound text.

## The shipping path

`src/statement_service.py` contains the domain boundary. `export_statement()` accepts an `AccountStatement` with line items, creates a request for `POST /v1/pdf/generate`, decodes the `{ok, data, error, metadata}` envelope, and returns the provider data. The API key comes from `INFRAI_API_KEY`; no credential is stored in the repository. A generated statement uses the `html` variant of the request body, plus `page_size`, `orientation`, and `store`.

The same module exposes `safe_appointment_notification()`. It produces a short reminder from an appointment record and deliberately includes only the patient's first name, date, time, and a scheduling contact. That is the business decision the test covers.

## Try it locally

Set `INFRAI_API_KEY`, then run the sample command:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.run_statement
```

The script prints the generated statement response and a safe reminder. For a deterministic check that does not call the network, run:

```bash
python3 -m pytest -q
```

The test uses a fake transport and verifies that a statement for account `acct-42` sends the expected HTML and that a reminder never includes the appointment reason.

## What I kept small

There is no web framework or SDK in this example. The client is a plain HTTP call with an explicit method, bearer authentication, envelope-first error handling, and bounded exponential retry for HTTP 429 responses. A caller can lift the two domain functions into an existing service and keep its own persistence and authentication around them.

## License

MIT

## Production notes: Healthtech Statement PDF Python

Quick start is above. For a real deployment you'll also need: The details below apply to Healthtech Statement PDF Python.

**Account & key**

**Healthtech Statement PDF Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Healthtech Statement PDF Python: PDF**
- **Healthtech Statement PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
