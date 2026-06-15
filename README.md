# AMS - Artist Management System

AMS is a small full-stack Artist Management System built for an advanced RBAC interview task. The project intentionally avoids a large backend framework so the request lifecycle, routing, validation, sessions, permissions, and SQL behavior are visible in the code.

## Live Demo

The app is deployed at:

```txt
https://ams.koiralasushil.com.np/
```

## Tech Stack

- Backend: Python 3.12, standard-library `http.server`, SQLite
- Frontend: React, Vite, Redux Toolkit, Axios, Tailwind CSS
- Deployment/runtime: Docker Compose and Nginx

## Project Structure

```txt
AMS/
├── backend/
│   ├── auth/              # users, login/logout, sessions, permissions
│   ├── artists/           # artist CRUD and artist-user linking
│   ├── songs/             # song CRUD and artist ownership checks
│   ├── core/              # router, request handler, middleware, serializers
│   ├── config.py          # environment-backed settings
│   ├── database.py        # SQLite schema setup
│   └── server.py          # app entry point
├── frontend/
│   ├── src/app/           # Redux store
│   ├── src/components/    # reusable UI pieces
│   ├── src/features/      # auth, dashboard, users, artists, songs
│   ├── src/lib/api.js     # Axios client and API wrappers
│   └── src/utils/         # frontend helpers
├── nginx/conf.d/          # Nginx reverse proxy config
├── scripts/               # helper scripts
├── artists.csv            # small CSV import sample
├── sample_artists.csv     # larger CSV import sample
└── docker-compose.yml
```

## Backend Decisions

The backend uses a custom `http.server`-based request handler instead of Django/FastAPI/Flask. This keeps the RBAC implementation explicit and easy to explain in an interview: every request passes through the custom router, middleware, serializer validation, and permission checks.

Routing is handled through the `@route(...)` decorator in `backend/core/router.py`. A route can define:

- path
- HTTP method
- whether authentication is required
- allowed roles

The request lifecycle is centralized in `backend/core/request_handler.py`. It parses the request, resolves sessions, checks route permissions, handles JSON responses, supports multipart CSV uploads, supports file download responses, and maps errors such as unauthorized or permission denied into consistent API responses.

Authentication is session-cookie based. Login creates a session row in SQLite and returns/sets a `session_id` cookie. Authenticated requests resolve the user through middleware in `backend/core/middleware.py`.

SQLite is used because this task is focused on API design, RBAC, and data relationships rather than database infrastructure. The schema is created on server startup in `backend/database.py`.

The important schema decisions are:

- `users.role` controls system access.
- `artists.user_id` links an artist profile to a user account.
- `songs.artist_id` links songs to artists.
- `artists.user_id` is unique so one artist user maps to one artist profile.
- deleting an artist cascades to songs through the song foreign key.

This ownership link matters for RBAC. Without `artists.user_id`, an `artist` user could potentially act on any `artist_id`. With the link, song create/update/delete operations can verify that the current user owns the target artist profile.

## Roles And Permissions

Supported roles:

- `super_admin`
- `artist_manager`
- `artist`

Current permission model:

| Area | Super Admin | Artist Manager | Artist |
| --- | --- | --- | --- |
| Users | Read/Create | No access | No access |
| Artists | Read | Create/Read/Update/Delete | No access |
| Songs | Read all | Read all | Create/Read own/Update own/Delete own |

Artist managers can create artist records and link them to available users with role `artist`. The `/artists/available-users` endpoint returns artist-role users that are not already linked to an artist row.

Song mutations are intentionally limited to users with role `artist`. Admin and artist manager users receive read-only song access.

## Backend Endpoints

The default API prefix is:

```txt
/api/v1
```

Main endpoints:

```txt
GET  /api/v1/
POST /api/v1/register
POST /api/v1/login
POST /api/v1/logout
GET  /api/v1/me

GET  /api/v1/users

GET  /api/v1/artists
GET  /api/v1/artists/available-users
POST /api/v1/artists/create
POST /api/v1/artists/update
POST /api/v1/artists/delete
POST /api/v1/artists/import
GET  /api/v1/artists/export

GET  /api/v1/songs
GET  /api/v1/songs/available-artists
POST /api/v1/songs/create
POST /api/v1/songs/update
POST /api/v1/songs/delete
```

List endpoints support pagination through query parameters:

```txt
GET /api/v1/users?page=1&limit=10
GET /api/v1/artists?page=1&limit=10
GET /api/v1/songs?page=1&limit=10
```

Paginated responses include a `pagination` object with `total`, `next`, and `previous`.

## Bulk Artist CSV Operations

Artist managers can import and export artist data as CSV.

### Import

```txt
POST /api/v1/artists/import
Content-Type: multipart/form-data
```

The request must include a file field named `file`.

Expected CSV columns:

```csv
user_id,name,dob,gender,address,first_release_year,no_of_albums_released
```

`user_id` may be blank when importing artists without linking them to existing artist-role users.

Import responses include row counts:

```json
{
  "total": 50,
  "success": 48,
  "error": 2
}
```

### Export

```txt
GET /api/v1/artists/export
```

The backend returns a downloadable `text/csv` response with a timestamped filename.

Sample CSV files are available in the repository root:

```txt
artists.csv
sample_artists.csv
```

## Frontend Decisions

The frontend is split by feature rather than keeping all code in `App.jsx`. This keeps the RBAC UI easier to reason about:

- `auth`: login, register, session state
- `users`: super-admin user management
- `artists`: artist-manager artist management
- `songs`: role-aware song listing and artist-owned song CRUD
- `dashboard`: tab visibility based on current user role

Axios is centralized in `frontend/src/lib/api.js`. It sets the API base URL, enables cookies with `withCredentials: true`, and normalizes backend error responses into frontend-friendly messages. The client does not force a global JSON content type, which lets browser `FormData` requests generate the correct multipart boundary for CSV uploads.

Redux Toolkit is used for authentication state because the current user affects the entire app: available tabs, protected actions, and artist ownership behavior.

The UI intentionally feels like an admin tool rather than a marketing page. It uses dense tables, simple modal forms, typeahead dropdowns for foreign-key selection, and role-specific actions.

Important frontend behavior:

- Super admin can access Users, Artists, and Songs.
- Artist manager can access Artists and Songs.
- Artist can access Songs only.
- Artist creation uses `/artists/available-users` as a typeahead dropdown for linking an artist user.
- Artist managers can import artists from CSV through a file picker and export existing artists as a downloaded CSV.
- Users and artists tables use backend pagination controls with previous/next navigation.
- Song listing is role-aware:
  - admin/manager users see all songs grouped by artist
  - artist users see only their own songs
- Song create/update/delete buttons are only shown for artist users.

## Environment Variables

Backend settings are read in `backend/config.py`.

Create a backend env file from the example:

```bash
cp backend/.env.example backend/.env
```

Useful backend variables:

```env
APP_NAME=AMS
API_VERSION=/api/v1
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DB_NAME=backend/ams.db
SESSION_TTL_HOURS=24
CORS_ALLOWED_ORIGIN=http://localhost:5173,http://localhost:8000
```

For local frontend development, create `frontend/.env` if needed:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

When using Docker Compose, `env_file` passes variables into the container at runtime. Compose interpolation such as `${SERVER_PORT}` only reads from your shell or a root-level `.env`, not automatically from `backend/.env`.

## Running With Docker Compose

From the project root:

```bash
docker compose up --build
```

Expected services:

- backend Python server
- frontend Vite build container
- Nginx serving `frontend/dist` and proxying API requests

Open:

```txt
http://localhost:8000
```

Nginx proxies:

```txt
/api/v1/* -> backend
```

Important: make sure the backend port used in `backend/.env`, the backend healthcheck, and `nginx/conf.d/default.conf` all agree. For example, if the backend runs on `SERVER_PORT=8000`, Nginx should proxy to:

```nginx
proxy_pass http://backend:8000;
```

and the backend healthcheck should call:

```txt
http://127.0.0.1:8000/api/v1/
```

## Production Deployment

Production is served at:

```txt
https://ams.koiralasushil.com.np/
```

The GitHub Actions workflow in `.github/workflows/deploy.yml` deploys pushes to `main`. It connects to the server through Tailscale, pulls the latest `main`, rebuilds the Docker Compose stack, removes orphaned containers, and prunes unused Docker images.

Required deployment secrets:

```txt
TS_OAUTH_CLIENT_ID
TS_OAUTH_SECRET
DEPLOY_HOST
DEPLOY_USER
DEPLOY_SSH_KEY
DEPLOY_PORT
DEPLOY_PATH
```

## Running Locally Without Docker

### Backend

From the project root:

```bash
cp backend/.env.example backend/.env
```

Set local backend values, for example:

```env
SERVER_HOST=127.0.0.1
SERVER_PORT=8500
DB_NAME=backend/ams.db
CORS_ALLOWED_ORIGIN=http://localhost:5173
```

Start the backend:

```bash
python3 -m backend.server
```

The server creates the SQLite tables automatically on startup.

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```txt
http://localhost:5173
```

If the backend is not running on the default frontend API URL, set:

```env
VITE_API_BASE_URL=http://127.0.0.1:8500/api/v1
```

## Development Commands

Backend syntax check:

```bash
python3 -m py_compile backend/server.py backend/database.py backend/auth/views.py backend/artists/views.py backend/songs/views.py
```

Frontend build:

```bash
cd frontend
npm run build
```

Frontend lint:

```bash
cd frontend
npm run lint
```

## Data Flow

1. A user logs in through `/login`.
2. The backend creates a session and sets a `session_id` cookie.
3. The frontend calls `/me` to resolve the current user.
4. Dashboard tabs are shown based on the user role.
5. Requests to protected endpoints pass through route-level role checks.
6. Artist-owned song mutations also verify ownership using `artists.user_id`.

## Notes For Reviewers

This project intentionally keeps the backend mechanics visible. In production, a framework would usually provide routing, middleware, serializers, migrations, password policy, CSRF protection, and tested auth primitives. Here, those parts are implemented directly to demonstrate the underlying RBAC decisions for the interview task.
