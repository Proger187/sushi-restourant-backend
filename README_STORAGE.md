Product/category images are stored on Cloudinary via `django-cloudinary-storage`
(see `STORAGES["default"]` in `config/settings.py`).

Setup:
1. Set `CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>` in `.env`.
2. One-time backfill of any pre-existing local files in `./media/` into Cloudinary:
   `python manage.py migrate_images_to_cloudinary`
   (safe to re-run; skips instances that no longer point at a local file)

`MEDIA_ROOT`/`MEDIA_URL` are kept only so any still-local files under `./media/`
stay servable until migrated. New uploads (admin product/category image field)
go straight to Cloudinary - no code path writes to local disk anymore.
