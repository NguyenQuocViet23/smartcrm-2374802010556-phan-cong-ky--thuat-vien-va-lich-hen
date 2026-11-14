# Security Checklist – Smart CRM (BT3, tag v1.0)

Seven items. Status is one of `ĐÃ LÀM` (done), `CHƯA LÀM` (not done) or `KHÔNG ÁP DỤNG` (not applicable); each
row has one line of evidence. The static checks (items 1, 2, 3, 5, 6, 7) were re-run on 15/11/2026; the test
results (TC-xx) come from the BT3 run of 10/11/2026 ([test-report.md](test-report.md)). OWASP references follow the
OWASP Top 10:2025 items used in the Session 13 guide. Longer explanations are under "Details" below.

| # | Item | Status | Evidence (one line) |
|---|---|---|---|
| 1 | No secret in the repository or its history | ĐÃ LÀM | `git log --all --oneline -- .env` → empty; no `…PASSWORD=` / `SECRET_KEY=` line with a value was ever added in code or config (only throw-away CI values). |
| 2 | Configuration through environment variables; example file without real values | ĐÃ LÀM | Settings are read with `os.getenv` in `app/core/config.py` and `${VAR}` in `docker-compose.yml`; `.env.example` holds placeholders only. |
| 3 | Passwords stored as salted hashes (A04) | ĐÃ LÀM | `data/processed/demo_accounts.json` (git-ignored): 41 accounts, all `pbkdf2_sha256$310000$<salt>$<hash>`, no plain-text field. |
| 4 | Authentication on every business endpoint; tokens cannot be forged or reused after expiry (A07) | ĐÃ LÀM | Only `/`, `/db-check`, `/api/auth/login` are public; TC-10: no token, expired token, altered token → 401 ×3, original token → 200. |
| 5 | Access control by role, center and technician (A01) | ĐÃ LÀM | `check_ticket_scope` runs in every ticket and appointment use case; TC-09: other technician's ticket → 403, other center's ticket → 403, data unchanged. |
| 6 | Input validation and injection (A05) | ĐÃ LÀM | SQL values are bound parameters (f-strings only join fixed fragments); TC-11: `' OR 1=1 --` → 400 / 0 rows, `<script>` shown as text; TC-07: blank fields → 400. |
| 7 | Safe error handling and configuration (A02) | ĐÃ LÀM | Errors return `{"error","message"}` with no traceback (unexpected → 500 `INTERNAL_ERROR`, logged); CORS allows only `http://localhost:5173` (TC-11). |

## Details

1. **Secrets.** `.env` is the first entry of `.gitignore` and was never committed. Scanning `git log --all -p` over
   code, scripts, tests, SQL, Dockerfile, compose file, requirements and README for added `…PASSWORD=` or `SECRET_KEY=`
   lines with a value returns 0 matches. The values in the local `.env` do not appear in any tracked file. The CI
   workflow uses throw-away values for its own temporary database only.
2. **Configuration.** The Deployment Guide (section 3) says to replace `DB_PASSWORD`, `SECRET_KEY` and
   `DEMO_PASSWORD` for any shared deployment, and shows how to generate random values.
3. **Passwords.** The system has no users table (TD-02). Demo accounts are generated from `DEMO_PASSWORD` by
   `scripts/generate_demo_accounts.py`; password comparison uses `hmac.compare_digest`.
4. **Authentication.** Every `/api/tickets`, `/api/appointments`, `/api/technicians` and `/api/auth/me` route
   depends on `current_user`. Tokens are HMAC-signed with `SECRET_KEY` (at least 32 characters) and expire after 8 hours.
5. **Access control.** A manager sees only tickets of their own center; a technician sees only their own tickets,
   with the customer phone masked (QT-14, QT-15; TC13 of Session 10).
6. **Validation.** Required text fields that contain only spaces are rejected with 400 `REQUIRED_FIELD_BLANK`
   (BUG-08, fixed in `224fd69`). React renders ticket text as text, so markup in a description does not run.
7. **Errors and deployment.** PostgreSQL is published only on `127.0.0.1`; the backend container runs as the
   non-root user `app`; dependencies are pinned (`requirements*.txt`, `package-lock.json`).

## Known limits (accepted for a demo environment, to address before production)

- Swagger UI `/docs` is enabled and the frontend runs the Vite development server (Deployment Guide, appendix).
- The login endpoint has no rate limiting or lockout, so passwords can be guessed repeatedly.
- The token is kept in the browser's `localStorage`, readable by any script that runs on the page. Item 6 keeps
  XSS out today, but an `HttpOnly` cookie would be safer.
- The IDE's Docker scanner reports 2 high-severity vulnerabilities in the `python:3.12-slim` base image; rebuild on
  a newer patch image before production.
- A full security review and penetration test are out of scope (Specialized Graduation Topic 2).
