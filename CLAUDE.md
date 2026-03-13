# CLAUDE.md -- Topsoil Marketplace

## Project Overview

Web application for a Missouri-based nursery near Washington, MO selling pulverized/screened and raw topsoil by the tandem load. Targets landscapers and homeowners in the Washington, MO area (Union, Labadie, Pacific, etc.).

## Tech Stack

- **Backend:** Python 3.9+, Flask 3.1, Flask-SQLAlchemy (SQLite), Flask-Mail, Flask-WTF (CSRF)
- **Frontend:** Jinja2 templates, Tailwind CSS (CDN), vanilla JavaScript
- **Config:** python-dotenv, `.env` file (gitignored)

## Running the App

```bash
cd topsoil
source venv/bin/activate
python seed.py        # Create tables + seed data (idempotent)
python run.py         # Dev server on http://127.0.0.1:5000
```

Admin login: credentials from `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env` (defaults: admin / changeme).

## Architecture

### Application Factory

`app/__init__.py` defines `create_app()` which loads config, initializes extensions, registers blueprints, and creates tables. Extensions are instantiated unbound in `app/extensions.py` to avoid circular imports.

**Known gotcha:** Do NOT use `import app.models` inside `create_app()` -- it shadows the local `app` Flask variable with the `app` package. Use `from app import models` instead.

### Blueprints

| Blueprint | Prefix | File |
|-----------|--------|------|
| `main` | `/` | `app/routes/main.py` |
| `inventory` | `/inventory` | `app/routes/inventory.py` |
| `checkout` | `/checkout` | `app/routes/checkout.py` |
| `admin` | `/admin` | `app/routes/admin.py` |

Registered in `app/routes/__init__.py:register_blueprints()`.

### Models

All in `app/models/`, imported in `app/models/__init__.py` so SQLAlchemy discovers them:
- `Topsoil` -- product catalog (name, soil_type, price_per_load, inventory_count)
- `Order` -- customer orders with delivery address, quantity, total price, status
- `WorkOrder` -- one-to-one with Order, tracks assignment and notification status
- `SiteSettings` -- singleton row (id=1) for banner text and active toggle

### Services

- `app/services/order_service.py` -- `place_order()`: creates Order + WorkOrder, decrements inventory in a single transaction
- `app/services/mail_service.py` -- `send_work_order_email()`: notifies manager via Flask-Mail, fails gracefully

### Templates

Extend `app/templates/base.html` which provides Tailwind CDN, nav, flash messages, and footer. Admin templates use a shared nav partial at `app/templates/admin/_nav.html`.

## Conventions

- **No emoji** in code, templates, or commit messages
- **CSS custom properties** for all colors -- defined in `app/static/css/custom.css` on `:root`, mapped to Tailwind color names in the CDN config script in `base.html`
- Color palette: `--color-primary` (brown #5C4033), `--color-secondary` (green #2D5A27), `--color-accent` (wheat #D4A843), `--color-bg` (cream #FAF6F1), `--color-text` (charcoal #2C2C2C), `--color-error` (red #b91c1c)
- Never hardcode hex values in templates -- use Tailwind extended colors or `var()` references
- Use `datetime.now(timezone.utc)` -- never the deprecated `datetime.utcnow()`
- All forms must include a CSRF token: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- Server-side validation returns error dicts keyed by field name (see `checkout.py` pattern)
- Flash messages use categories: `"success"`, `"error"`, `"info"`

## Security

- CSRF protection via Flask-WTF on all POST forms
- Session-based admin auth with `@admin_required` decorator
- Timing-safe password comparison (`hmac.compare_digest`)
- Order confirmation URLs require session token (not publicly enumerable)
- Logout is POST-only to prevent accidental logouts

## Environment Variables

Defined in `.env` (gitignored):

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Flask session signing | `fallback-dev-key` |
| `ADMIN_USERNAME` | Admin login | `admin` |
| `ADMIN_PASSWORD` | Admin login | `changeme` |
| `MANAGER_EMAIL` | Work order notification recipient | None |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Enable TLS | `true` |
| `MAIL_USERNAME` | SMTP auth username | None |
| `MAIL_PASSWORD` | SMTP auth password | None |
| `MAIL_DEFAULT_SENDER` | From address | `noreply@nursery.com` |

## Database

SQLite at `instance/topsoil.db` (auto-created by `create_app()`). Run `python seed.py` to populate with default products and site settings. The seeder is idempotent -- safe to run multiple times.
