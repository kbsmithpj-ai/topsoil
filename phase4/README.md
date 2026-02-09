# Phase 4 -- Admin Dashboard

## Goals

- Provide a session-based admin login protecting all management routes.
- Build a work-order dashboard showing every order with status, customer, and product details.
- Allow admins to mark orders as completed directly from the dashboard.
- Add an inventory management view where price and stock levels can be edited per product.
- Introduce a SiteSettings model and admin UI for controlling a promotional banner on the public site.

## Files created

| File | Purpose |
|------|---------|
| `app/models/site_settings.py` | SiteSettings model (banner_text, banner_active) |
| `app/routes/admin.py` | Admin blueprint with login, dashboard, inventory, settings routes |
| `app/templates/admin/login.html` | Admin login form |
| `app/templates/admin/dashboard.html` | Work-order table with status badges and complete action |
| `app/templates/admin/inventory.html` | Product cards with editable price and stock fields |
| `app/templates/admin/settings.html` | Banner text and active-toggle form |
| `phase4/models_init_patch.py` | Patch note: add SiteSettings import to models __init__ |
| `phase4/seed_patch.py` | Patch note: seed default SiteSettings row |
| `phase4/home_banner_patch.html` | Patch note: wire dynamic banner into home.html |
| `phase4/README.md` | This file |

## Integration patches

The following files must be updated during the integration step (they are owned by other phases that are being built in parallel):

1. **`app/models/__init__.py`** -- import `SiteSettings` so SQLAlchemy discovers it.
2. **`app/routes/__init__.py`** -- register `admin_bp` via `register_blueprints`.
3. **`seed.py`** -- add a default SiteSettings row after product seeding.
4. **`app/routes/main.py`** -- pass `settings=SiteSettings.query.first()` to the home template.
5. **`app/templates/home.html`** -- replace any hardcoded banner div with a dynamic Jinja block.

## Verification steps

```bash
cd topsoil

# 1. Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 2. After integration patches are applied, seed the database
python seed.py

# 3. Start the dev server
python run.py

# 4. Visit http://127.0.0.1:5000/admin/login
#    Log in with ADMIN_USERNAME / ADMIN_PASSWORD from .env (default: admin / changeme)

# 5. Verify dashboard loads at /admin/ with work-order table (may be empty initially)

# 6. Visit /admin/inventory -- confirm product cards with editable fields appear

# 7. Visit /admin/settings -- toggle the banner, save, and verify the home page reflects changes

# 8. Log out via /admin/logout and confirm redirect to public home page
```
