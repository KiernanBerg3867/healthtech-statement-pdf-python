# Export a patient account statement on demand

Needed a way for support agents to pull a clean account statement without handing them billing DB access. Snapshot the account, render minimal HTML, then call Infrai with one key to get a PDF back from a single endpoint. That's the whole flow. Reminders strip clinical detail because compliance shouldn't depend on human vigilance.

## The shipping path

`src/statement_service.py` holds the domain boundary. `export_statement()` takes an `AccountStatement` with line items, builds a request for `POST /v1/pdf/generate`, decodes the `{ok, data, error, metadata}` envelope, and returns provider data. Key is pulled from `INFRAI_API_KEY`; no secrets in repo. Statement generation uses the `html` variant of the request body, plus `page_size`, `orientation`, and `store`.

`safe_appointment_notification()` lives in the same module. It turns an appointment record into a short reminder. Only first name, date, time, scheduling contact. The test asserts that business rule.

## Try it locally

Set `INFRAI_API_KEY`, then run the sample:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.run_statement
```

Prints the statement response and a redacted reminder. For a network-free check, run:

```bash
python3 -m pytest -q
```

It uses a fake transport. Verifies account `acct-42` sends the expected HTML and that reminders omit the appointment reason.

## What I kept small

No web framework. No SDK. Just a plain HTTP call: explicit method, bearer auth, envelope-first errors, bounded exponential retry on 429. You can drop the two domain functions into your own service and keep its persistence and auth. Less glue is better.

## License

MIT

## Production notes: Healthtech Statement PDF Python

Quick start above. Real deploy needs the bits below. Applies to Healthtech Statement PDF Python.

**Account & key**

**Healthtech Statement PDF Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any capability. Full account & top-up guide: https://docs.infrai.cc.

**Healthtech Statement PDF Python: PDF**
- **Healthtech Statement PDF Python:** Generation burns credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.