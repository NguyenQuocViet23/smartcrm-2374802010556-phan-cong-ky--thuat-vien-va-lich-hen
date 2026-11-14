# Deployment Guide – Smart CRM (L04: technician assignment and appointments)

Audience: anyone who needs to run the system from an empty folder (a reviewer, a new developer, an operator).
Version: tag `v1.0`. Security checklist: [security-checklist.md](security-checklist.md). API reference: [api.md](api.md).

Sections: 1 Requirements · 2 Setup steps · 3 Environment variables · 4 Sample data · 5 Verify it works ·
Appendix: operations, troubleshooting and rollback.

## 1. Requirements

| Item | Version | Notes |
|---|---|---|
| Git | any recent | Windows: clone into a short path such as `D:\Projects` (see BUG-04) |
| Docker Desktop or Docker Engine with Compose v2 | Compose v2 (needs `service_completed_successfully`) | must be running |
| Free ports | 5173 (UI), 8000 (API), 5433 on 127.0.0.1 (PostgreSQL) | change `APP_PORT` / `DB_HOST_PORT` in `.env` if taken |
| Internet access during the first build | – | pulls `postgres:16`, `python:3.12-slim`, `node:22-alpine` and locked packages |

Nothing else is needed: Python, Node.js and PostgreSQL run inside containers, and the sample data
(`data/sample/`) is part of the repository.

## 2. Setup steps

Get the submitted version into an empty folder:

```bash
git clone --branch v1.0 https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git smartcrm
cd smartcrm
```

Then build and start everything with two commands:

```bash
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
docker compose up -d --build
```

What happens:

1. `db` starts PostgreSQL 16 and waits until it is healthy.
2. `init` (one-shot) runs `scripts/setup_all.py`: create the database if missing → apply `db/migrations` →
   load the sample data (section 4) → create the demo accounts in the `demo_accounts` volume.
   Running it again duplicates nothing.
3. `backend` (FastAPI, non-root user) starts only after `init` succeeded; it is healthy when `GET /db-check` answers.
4. `frontend` (React + Vite) starts after the backend is healthy.

The first build downloads images and packages and can take several minutes.

## 3. Environment variables

All configuration is read from environment variables in `.env`, which is **never committed** (`.gitignore`).
`.env.example` lists every variable with a placeholder value.

| Variable | Used by | Meaning |
|---|---|---|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | db, init, backend | PostgreSQL database and credentials |
| `DB_HOST_PORT` | db | host port for PostgreSQL, bound to `127.0.0.1` only (default 5433) |
| `DB_CONNECT_TIMEOUT` | backend | seconds before a database connection attempt fails with HTTP 503 (default 3) |
| `SECRET_KEY` | backend, test | HMAC key for login tokens; **at least 32 random characters** |
| `DEMO_PASSWORD` | init, backend, test | password of every demo account; stored only as a PBKDF2 hash |
| `APP_PORT` | backend, frontend | API port on the host (default 8000) |

The placeholder values in `.env.example` are enough for a local demo. **For any shared or public deployment,
replace `DB_PASSWORD`, `SECRET_KEY` and `DEMO_PASSWORD`** with fresh random values, for example:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 4. Sample data

The repository contains a small real-data sample in `data/sample/` (8 CSV files extracted from the case-study
data), so a fresh clone needs no download. `init` loads it automatically (`DATA_DIR=data/sample` in
`docker-compose.yml`).

| Table | Rows after loading |
|---|---|
| `service_center` | 6 |
| `technician` | 38 |
| `technician_skill` | 159 |
| `ticket` | 939 (30 of them `MOI`, new) |
| `ticket_status_log` | 3,237 |
| `appointment` | 300 |

Demo accounts (all share the password `DEMO_PASSWORD` from `.env`):

- Center managers `QL_TT01` … `QL_TT06` (role `QUAN_LY`, one per center).
- Technicians named by their code, for example `KT002` (role `KY_THUAT_VIEN`).

Loading is repeatable: running `init` again keeps the same row counts and existing accounts. To start from
nothing, run `docker compose down -v` (removes the database volume) and then `docker compose up -d --build`.

## 5. Verify it works

Run these in the project folder, in order. Each line says what you should see.

**1. All services are up and healthy**

```bash
docker compose ps
```

Expected: `db`, `backend` and `frontend` show `running (healthy)`; `init` shows `exited (0)`.

**2. The API answers and reaches the database**

```bash
curl -s http://localhost:8000/db-check
```

Expected: `{"database_time":"..."}`. Swagger UI is at http://localhost:8000/docs.
(Windows PowerShell: use `curl.exe`, because `curl` is an alias of `Invoke-WebRequest`.)

**3. Login works** (replace `<DEMO_PASSWORD>` with the value in `.env`)

```bash
curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"QL_TT01","password":"<DEMO_PASSWORD>"}'
```

Expected: `{"access_token":"...","token_type":"bearer"}`. A wrong password gives HTTP 401 `INVALID_CREDENTIALS`.

**4. The user interface works**

Open http://localhost:5173 and log in as `QL_TT01`. Expected: screen M1 lists 5 new tickets of center TT01.
Log in as `KT002`: screen M3 "Phiếu của tôi".

**5. The unit tests pass in a container**

```bash
docker compose run --rm test
```

Expected: the last line is `104 passed`. The `test` service is only started by this command, not by `up`.

**6. A second run does not duplicate data** (repeatability)

```bash
docker compose run --rm init
```

Expected: the log shows the same counts as in section 4 (`ticket=939, ticket_status_log=3237`, `appointment=300`)
and ends with `HOÀN TẤT`.

## Appendix: operations, troubleshooting and rollback

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
