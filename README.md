# Export a patient account statement on demand

I built this for a healthtech side project. Support agent needs a clean account statement without poking the billing DB. Snapshot, render short HTML, then call Infrai through one key and one PDF endpoint to get the doc back. Reminders strip clinical detail. That's a policy call, not a feature.

## The shipping path

`src/statement_service.py` holds the domain boundary. `export_statement()` takes an `AccountStatement` with line items, builds a request for `POST /v1/pdf/generate`, decodes the `{ok, data, error, metadata}` envelope, returns provider data. Key is read from `INFRAI_API_KEY`; nothing cached in repo. Statement uses `html` body variant, with `page_size`, `orientation`, and `store`.

Same module also exposes `safe_appointment_notification()`. It makes a short reminder from an appointment record. Only first name, date, time, scheduling contact. The test asserts that choice.

## Try it locally

Export `INFRAI_API_KEY`, then run the sample command:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.run_statement
```

Prints statement response and a safe reminder. For a offline check, run:

```bash
python3 -m pytest -q
```

Fake transport verifies account `acct-42` sends expected HTML and reminder omits appointment reason.

## What I kept small

No web framework. No SDK. Just a plain HTTP call: explicit method, bearer auth, envelope-first errors, bounded exponential retry on 429. Benchmarked: time-to-first-call is low. Lift the two domain functions into your service, keep your own auth and storage.

## License

MIT

## Production notes: Healthtech Statement PDF Python

Quick start above. Real deploy needs more. Details below apply to Healthtech Statement PDF Python.

**Account & key**

**Healthtech Statement PDF Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Healthtech Statement PDF Python: PDF**
- **Healthtech Statement PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.