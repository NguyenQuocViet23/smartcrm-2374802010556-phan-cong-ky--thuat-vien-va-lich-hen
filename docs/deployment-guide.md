# Deployment Guide – Smart CRM (L04: technician assignment and appointments)

Audience: anyone who needs to run the system from an empty folder (a reviewer, a new developer, an operator).
Version: tag `v1.0`. Security checklist: [security-checklist.md](security-checklist.md). API reference: [api.md](api.md).

## 1. Prerequisites

| Item | Version | Notes |
|---|---|---|
| Git | any recent | Windows: clone into a short path such as `D:\Projects` (see BUG-04) |
| Docker Desktop or Docker Engine with Compose v2 | Compose v2 (needs `service_completed_successfully`) | must be running |
| Free ports | 5173 (UI), 8000 (API), 5433 on 127.0.0.1 (PostgreSQL) | change `APP_PORT` / `DB_HOST_PORT` in `.env` if taken |
| Internet access during the first build | – | pulls `postgres:16`, `python:3.12-slim`, `node:22-alpine` and locked packages |

Nothing else is needed: Python, Node.js and PostgreSQL run inside containers, and the sample data
(`data/sample/`, extracted from the real case-study data) is part of the repository.

## 2. Configuration

All configuration is read from environment variables in `.env`, which is **never committed** (`.gitignore`).
`.env.example` lists every variable with a placeholder value.

| Variable | Used by | Meaning |
|---|---|---|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | db, init, backend | PostgreSQL database and credentials |
| `DB_HOST_PORT` | db | host port for PostgreSQL, bound to `127.0.0.1` only (default 5433) |
| `DB_CONNECT_TIMEOUT` | backend | seconds before a database connection attempt fails with HTTP 503 (default 3) |
| `SECRET_KEY` | backend | HMAC key for login tokens; **at least 32 random characters** |
| `DEMO_PASSWORD` | init, backend | password of every demo account; stored only as a PBKDF2 hash |
| `APP_PORT` | backend, frontend | API port on the host (default 8000) |

The placeholder values in `.env.example` are enough for a local demo. **For any shared or public deployment,
replace `DB_PASSWORD`, `SECRET_KEY` and `DEMO_PASSWORD`** with fresh random values, for example:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 3. Build and run (two commands)

From an empty folder:

```bash
git clone --branch v1.0 https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git smartcrm
cd smartcrm
```

Then:

```bash
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
docker compose up -d --build
```

What happens:

1. `db` starts PostgreSQL 16 and waits until it is healthy.
2. `init` (one-shot) runs `scripts/setup_all.py`: create the database if missing → apply `db/migrations` →
   load the sample data (939 tickets, 3,237 status-log rows, 300 appointments, 38 technicians, 6 centers) →
   create the demo accounts in the `demo_accounts` volume. Running it again duplicates nothing.
3. `backend` (FastAPI, non-root user) starts only after `init` succeeded; it is healthy when `GET /db-check` answers.
4. `frontend` (React + Vite) starts after the backend is healthy.

## 4. Verify

```bash
docker compose ps
```

Expected: `db`, `backend` and `frontend` show `running (healthy)`; `init` shows `exited (0)`.

| Check | How | Expected |
|---|---|---|
| Database reachable from the API | open http://localhost:8000/db-check | `{"database_time": "..."}` |
| API documentation | open http://localhost:8000/docs | Swagger UI lists the endpoints |
| Login | http://localhost:5173 → user `QL_TT01`, password = `DEMO_PASSWORD` | screen M1 lists 5 new tickets of center TT01 |
| Technician view | log in as `KT002` | screen M3 "Phiếu của tôi" |
| Data loaded | `docker compose logs init` | shows `ticket=939, ticket_status_log=3237`, `appointment=300` and ends with `HOÀN TẤT` |

## 5. Operations, troubleshooting and rollback

| Situation | Action |
|---|---|
| Stop | `docker compose down` (data is kept in the `postgres_data` volume) |
| Reset everything (fresh data and accounts) | `docker compose down -v` then `docker compose up -d --build` |
| Logs | `docker compose logs -f backend` (errors are logged without being sent to clients) |
| `init` exited with an error | `docker compose logs init`; usually wrong `DB_USER`/`DB_PASSWORD` after the volume was created with other values → `docker compose down -v` |
| Port already in use | change `APP_PORT` or `DB_HOST_PORT` in `.env`, or stop the other service |
| Login answers 503 `AUTH_CONFIGURATION_ERROR` | `SECRET_KEY` is shorter than 32 characters |
| API answers 503 `DATABASE_UNAVAILABLE` | the database is down or unreachable; the API fails after `DB_CONNECT_TIMEOUT` seconds instead of hanging (BUG-07) |
| Roll back to an earlier version | `docker compose down`, `git checkout <tag>` (for example `v0.2`), `docker compose up -d --build`; use `down -v` if the schema differs |

Limits of this setup: the frontend runs the Vite development server and Swagger UI is enabled, which suits a
demo or review environment. A production deployment would serve a static build (`npm run build`) behind HTTPS,
disable `/docs`, and keep PostgreSQL unreachable from outside the Docker network.
