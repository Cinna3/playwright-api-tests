# Playwright API Automation — Python

**38 tests: 34 passing, 4 documenting real defects** in the API under test.
Covers status codes, response contracts, pagination, filtering, negative input,
and latency budgets.

Tested against [dummyjson.com](https://dummyjson.com), a free public API with no
key required. Playwright's `APIRequestContext` sends the HTTP requests
directly, so **no browser is launched** and the whole suite runs in about 8
seconds.

## What this repo demonstrates

- **API client layer** — endpoint knowledge lives in `clients/`, not in tests
- **Contract testing** — verifying the response still contains what it promises
- **Negative testing** — verifying bad input fails cleanly instead of 500ing
- **Boundary testing** — pagination limits, clamping, and default values
- **Performance budgets** — asserting latency against a configurable threshold
- **Documented defects** — 4 `xfail` tests that record requirements the API
  does not yet meet
- **CI matrix** — Ubuntu and Windows, Python 3.11 and 3.12

## Project structure

```
playwright-api-tests/
├── conftest.py               # fixtures: shared HTTP client
├── pytest.ini                # settings, markers, xfail policy
├── requirements.txt
├── clients/
│   └── product_api.py        # typed wrapper around the product endpoints
├── tests/
│   ├── test_status_codes.py            # status codes and headers
│   ├── test_schema_contract.py         # response shape guarantees
│   ├── test_data_operations.py         # pagination, filtering, CRUD
│   └── test_negative_and_validation.py # bad input, and the defect log
└── .github/workflows/ci.yml
```

## Running the tests

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                             # all tests
pytest -m contract                 # only contract tests
pytest -m negative                 # only bad-input tests
pytest -v                          # verbose
```

The report is written to `reports/report.html`.

## The defects this suite found

While building these tests, four genuine problems were found in the API. They
are recorded as `xfail` tests — they state the correct behaviour, are skipped
because the API does not implement it, and would start passing the day someone
fixed the endpoint.

| # | Requirement | Actual behaviour |
| --- | --- | --- |
| 1 | `POST /products/add` with an empty body → 400 | 201, returns an object with only an `id` |
| 2 | `POST` without a title → 400 | 201, creates the product anyway |
| 3 | `POST` with `price: "abc"` → 400 | 201, stores `"abc"` as a string |
| 4 | `POST` with a negative price → 400 | 201, accepts it |

That third one is the most serious: a string lands in a numeric field, so every
downstream calculation that trusts the type is now wrong.

To see them:

```bash
pytest -m negative -v
```

## Known limitation: this API does not persist writes

`POST /products/add` returns `id: 195`, but fetching `/products/195` returns
404. The same applies to `PUT` and `DELETE`. Because of this the suite
deliberately **does not** assert read-after-write:

- `create` tests assert the status code and that the payload is echoed back
- `delete` accepts either 200 or 404, so the suite still passes on a re-run
  after the resource is already gone

A full create → read → update → delete chain needs a database-backed API. This
is a property of the public test API, not of the tests.

## Key concepts explained

**`APIRequestContext`.** Playwright can make HTTP calls without a browser. It
speaks the same API as the browser layer, so one tool and one report covers
both UI and API testing, and API tests are an order of magnitude faster.

**Contract tests.** These assert the *shape* of a response: required fields
present, correct types, correct nesting. They catch the most common API
regression — a field quietly renamed or turned from a number into a string —
long before a UI breaks.

**Negative tests.** "What happens when input is wrong?" A 500 is a defect; a
400 with a message explaining the problem is a well-behaved endpoint.

**`xfail`.** A test that is expected to fail, and marked as such. It keeps a
known defect visible and tracked in code without turning the build red. Here
`xfail_strict = false` means that when the API is fixed, the test simply reports
an unexpected pass instead of breaking the pipeline.
