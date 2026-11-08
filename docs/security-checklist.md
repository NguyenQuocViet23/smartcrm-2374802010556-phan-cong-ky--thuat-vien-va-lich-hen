# Security Checklist – Smart CRM (BT3, tag v1.0)

Seven items, each with the evidence that was actually checked on 08/11/2026. OWASP references follow the
OWASP Top 10:2025 items used in the Session 13 guide. Related test cases are in [test-report.md](test-report.md).

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | **No secret in the repository or its history** | Pass | `git log --all -- .env` is empty: `.env` was never committed (first line of `.gitignore`). Scanning `git log --all -p` for added `…PASSWORD=` / `SECRET_KEY=` lines with a value (excluding `.env.example`) returns 0 matches. CI uses throw-away values only for its own database. |
| 2 | **Configuration through environment variables; example file without real values** | Pass | Every setting is read from the environment (`app/core/config.py`, `docker-compose.yml`). `.env.example` contains placeholders only (`doi-mat-khau-…`, `thay-bang-chuoi-…`); the Deployment Guide §2 says to replace them for any shared deployment. |
| 3 | **Passwords stored as salted hashes (A04)** | Pass | The system has no users table (TD-02); demo accounts live in `data/processed/demo_accounts.json` (git-ignored). Checked: 41 accounts, all `pbkdf2_sha256$310000$<salt>$<hash>`, no plain `password` field. Comparison uses `hmac.compare_digest`. |
| 4 | **Authentication on every business endpoint; tokens cannot be forged or reused after expiry (A07)** | Pass | All `/api/tickets`, `/api/appointments`, `/api/technicians`, `/api/auth/me` routes depend on `current_user`. Only `/`, `/db-check`, `/api/auth/login` and `/docs` are public. TC-10: no token, expired token, token with one altered character → 401 ×3; the original token → 200. |
| 5 | **Access control by role, center and technician (A01)** | Pass | `check_ticket_scope` (QT-14) is called by every ticket/appointment use case. TC-09: a technician changing another technician's ticket → 403, ticket unchanged; a manager editing another center's ticket → 403, data unchanged. Technicians see masked phone numbers (QT-15, TC13 of Session 10). |
| 6 | **Input validation and injection (A05)** | Pass | All SQL uses bound parameters (`text(... :name)`); the few f-strings only join fixed column lists. TC-11: `' OR 1=1 --` as a filter → 400 or 0 rows; `<script>` in a ticket description is shown as text by React, no dialog fires. TC-07 / BUG-08: blank required fields are now rejected with 400. |
| 7 | **Safe error handling and configuration (A02)** | Pass, with known limits | Errors return `{"error", "message"}` only; unexpected errors give 500 `INTERNAL_ERROR` and are logged server-side, no traceback (TC-11 checks the body). CORS allows only `http://localhost:5173` (TC-11: no `Access-Control-Allow-Origin` for `http://evil.example`). Docker: PostgreSQL bound to `127.0.0.1`, backend runs as a non-root user, dependencies pinned (`requirements*.txt`, `package-lock.json`). |

## Known limits (accepted for a demo environment, to address before production)

- Swagger UI `/docs` is enabled and the frontend runs the Vite development server (Deployment Guide §5).
- The login endpoint has no rate limiting or lockout, so passwords can be guessed repeatedly.
- The token is kept in the browser's `localStorage`, readable by any script that runs on the page. Item 6 keeps
  XSS out today, but an `HttpOnly` cookie would be safer.
- The IDE's Docker scanner reports 2 high-severity vulnerabilities in the `python:3.12-slim` base image; rebuild on
  a newer patch image before production.
- A full security review and penetration test are out of scope (Specialized Graduation Topic 2).
