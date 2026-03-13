# Add to seed.py after Topsoil seeding:
# from app.models.site_settings import SiteSettings
# if not SiteSettings.query.first():
#     settings = SiteSettings(
#         banner_text="Spring Special: Book your tandem loads early for guaranteed availability!",
#         banner_active=True,
#     )
#     db.session.add(settings)
#     db.session.commit()
#     print("Default site settings created.")
