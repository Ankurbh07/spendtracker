# Spec: Registration

## Overview
Implement working user registration so visitors can create a Spendly account.
The `/register` route currently only renders the template; this step wires up
the POST handler to validate input, hash the password, insert the user into
the database, create a Flask session, and redirect to the dashboard placeholder.
After this step a brand-new user can sign up and land on an authenticated page.

## Depends on
Step 01 — Database Setup (users table must exist; `get_db` must work).

## Routes
- `GET  /register` — render registration form — public (already exists, no change)
- `POST /register` — process form, create account, start session — public

## Database changes
No new tables or columns. The existing `users` table (id, name, email,
password_hash, created_at) covers everything needed.

Add one helper function to `database/db.py`:
- `create_user(name, email, password_hash)` — inserts a row and returns the
  new user's `id`. Raises `sqlite3.IntegrityError` if the email is already taken.

## Templates
- **Modify:** `templates/register.html`
  - The `{% if error %}` block already exists — no structural change needed.
  - Re-populate `name` and `email` fields with submitted values on error so the
    user does not have to retype them (add `value="{{ name or '' }}"` etc.).

## Files to change
- `app.py` — add POST handler logic inside the existing `/register` route;
  import `session` from flask; set `app.secret_key`; add `create_user` import.
- `database/db.py` — add `create_user(name, email, password_hash)` function.
- `templates/register.html` — preserve form field values on validation error.

## Files to create
No new files.

## New dependencies
No new dependencies. `flask` sessions and `werkzeug.security` are already
available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only.
- Parameterised queries only — never string-format SQL.
- Hash passwords with `werkzeug.security.generate_password_hash` before insert.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- `app.secret_key` must be set before session use; use a hard-coded dev string
  for now (e.g. `"spendly-dev-secret"`). Do NOT read from env yet.
- Session key for the logged-in user: `session["user_id"]` (integer).
- After successful registration redirect to `/dashboard` (the existing
  placeholder route is fine for now).
- Validation rules (server-side):
  - `name` — required, strip whitespace, 1–100 chars.
  - `email` — required, strip whitespace, must contain `@`.
  - `password` — required, minimum 8 characters.
  - Duplicate email → catch `sqlite3.IntegrityError`, show
    "An account with that email already exists."
- On validation failure re-render `register.html` with `error=`, `name=`, and
  `email=` so the user does not lose their input.
- Do not log passwords or password hashes anywhere.

## Definition of done
- [ ] Submitting valid name / email / password creates a row in `users` with a
      hashed password (not plaintext).
- [ ] After successful registration `session["user_id"]` is set and the browser
      is redirected to `/dashboard`.
- [ ] Submitting a blank name, email, or password shows a specific error message
      and keeps the other fields populated.
- [ ] Registering with an email that already exists shows
      "An account with that email already exists." without a 500 error.
- [ ] Registering with a password shorter than 8 characters shows an error.
- [ ] The `create_user` function in `db.py` uses a parameterised query and
      returns the new user id.
- [ ] `app.secret_key` is set so sessions persist across requests.
- [ ] The demo user (`demo@spendly.com`) created by `seed_db` is not broken —
      app still starts cleanly.
