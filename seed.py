"""Seed the database with initial topsoil products and site settings."""

from app import create_app
from app.extensions import db
from app.models.topsoil import Topsoil
from app.models.site_settings import SiteSettings

PRODUCTS = [
    {
        "name": "Premium Pulverized & Screened Topsoil",
        "soil_type": "Screened",
        "price_per_load": 350.00,
        "inventory_count": 50,
        "description": (
            "Rich, dark soil that has been pulverized and screened to remove "
            "rocks, roots, and debris. Perfect for gardens, lawns, and raised "
            "beds. Delivers excellent drainage and nutrient retention."
        ),
    },
    {
        "name": "Raw Fill Soil",
        "soil_type": "Raw",
        "price_per_load": 200.00,
        "inventory_count": 100,
        "description": (
            "Unprocessed fill soil suitable for grading, backfill, and land "
            "leveling projects. Sold by the truckload."
        ),
    },
]


def seed():
    app = create_app()

    with app.app_context():
        db.create_all()

        # Remove existing products so the seed is idempotent
        Topsoil.query.delete()
        db.session.commit()

        for product_data in PRODUCTS:
            db.session.add(Topsoil(**product_data))

        db.session.commit()
        print(f"Seeded {len(PRODUCTS)} topsoil products.")

        # Seed default site settings if not present
        if not db.session.get(SiteSettings, 1):
            settings = SiteSettings(
                id=1,
                banner_text="Spring Special: Book your tandem loads early for guaranteed availability!",
                banner_active=True,
            )
            db.session.add(settings)
            db.session.commit()
            print("Default site settings created.")
        else:
            print("Site settings already exist, skipping.")


if __name__ == "__main__":
    seed()
