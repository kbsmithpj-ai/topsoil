# Phase 1 -- Foundation

## Goals

- Establish the Flask application factory and project layout.
- Define the core data models: Topsoil, Order, and WorkOrder.
- Configure extensions (SQLAlchemy, Flask-Mail) via an extensions module.
- Provide a seed script to populate initial product data.
- Verify the app boots and the database initializes correctly.

## Files created

| File | Purpose |
|------|---------|
| `config.py` | Configuration class reading from `.env` |
| `app/__init__.py` | Application factory (`create_app`) |
| `app/extensions.py` | Unbound SQLAlchemy and Mail instances |
| `app/models/__init__.py` | Model package; imports all models |
| `app/models/topsoil.py` | Topsoil product model |
| `app/models/order.py` | Customer order model |
| `app/models/work_order.py` | Fulfillment work-order model |
| `app/routes/__init__.py` | Routes package placeholder |
| `app/services/__init__.py` | Services package placeholder |
| `run.py` | Dev server entry point |
| `seed.py` | Database seeder for initial products |

## Verification steps

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python seed.py
# Expected output: "Seeded 2 topsoil products."

# 4. Start the dev server
python run.py
# Server should start on http://127.0.0.1:5000 with no errors.
```
