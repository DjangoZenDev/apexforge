# ApexForge — Installation Guide

**Version:** 1.0.0 &nbsp;|&nbsp; **Vendor:** DjangoZen &nbsp;|&nbsp; **Support:** https://djangozen.com/support/

---

## System Requirements

| Requirement | Minimum Version |
|---|---|
| Python | 3.12+ |
| pip | 23+ |
| Node.js *(optional — Tailwind build only)* | 18+ |
| PostgreSQL *(production)* | 14+ |
| Operating System | Windows 10+, macOS 12+, Ubuntu 20.04+ |

---

## Step 1 — Get the Code

```bash
git clone https://github.com/djangozen/apexforge.git
cd apexforge
```

Or download and extract the ZIP from your DjangoZen purchase.

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — macOS / Linux
source .venv/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

| Package | Purpose |
|---|---|
| Django 5.2 LTS | Core web framework |
| django-environ | .env file configuration |
| Pillow | Image processing and avatar uploads |
| django-htmx | HTMX server-side integration |
| django-widget-tweaks | Template-level form rendering |
| django-simple-history | Model audit log and change history |
| django-filter | Advanced queryset filtering |
| django-q2 | Background task queue |
| django-extensions | Extra management commands |
| django-cleanup | Auto-delete orphaned media files |
| crispy-tailwind | Tailwind-styled Django forms |
| openpyxl | Excel (.xlsx) export |
| reportlab | PDF generation |
| whitenoise | Static file serving without a CDN |
| gunicorn | Production WSGI server |
| psycopg2-binary | PostgreSQL database adapter |

---

## Step 4 — Configure Environment

```bash
cp .env.example .env
```

Open `.env` and configure the following:

```env
# Core
DEBUG=True
SECRET_KEY=your-strong-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
# SQLite (development default)
DATABASE_URL=sqlite:///db.sqlite3
# PostgreSQL (recommended for production)
# DATABASE_URL=postgres://user:password@localhost:5432/apexforge

# Email
# Use console backend for development — no real emails sent
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=ApexForge <your@gmail.com>

# Stripe Payments
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_CURRENCY=eur

# Media & Static
MEDIA_URL=/media/
MEDIA_ROOT=media
STATIC_URL=/static/
STATIC_ROOT=staticfiles

# Localisation
LANGUAGE_CODE=en
TIME_ZONE=UTC
```

> **Generate a SECRET_KEY:**
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## Step 5 — Run Migrations

```bash
python manage.py migrate
```

---

## Step 6 — Create Superuser

```bash
python manage.py createsuperuser
```

Or use the demo accounts listed in [README.md](README.md#demo-accounts).

---

## Step 7 — Collect Static Files

```bash
python manage.py collectstatic --no-input
```

---

## Step 8 — Start the Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Step 9 — Start Background Tasks *(optional)*

The task queue handles daily digest emails and contract expiry alerts:

```bash
python manage.py qcluster
```

Run in a **separate terminal** alongside `runserver`.

---

## Tailwind CSS

ApexForge loads Tailwind via CDN by default — no build step needed for development.

For production, build a minified CSS file:

```bash
npm install
npx tailwindcss -i static/css/input.css -o static/css/output.css --minify
```

Then update `base.html` to load `output.css` instead of the CDN `<script>` tag.

---

## Production Deployment

### 1. Environment Settings

```env
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/apexforge
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### 2. PostgreSQL Setup

```bash
psql -U postgres
CREATE DATABASE apexforge;
CREATE USER apexforge_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE apexforge TO apexforge_user;
\q

python manage.py migrate
python manage.py collectstatic --no-input
```

### 3. Run with Gunicorn

```bash
gunicorn apexforge.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

### 4. Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /path/to/apexforge/staticfiles/;
    }

    location /media/ {
        alias /path/to/apexforge/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5. SSL — Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Translations

ApexForge supports **6 languages**: English, Dutch, German, French, Spanish, Italian.

```bash
# Compile translation files
python manage.py compilemessages

# Regenerate after adding new translatable strings
python manage.py makemessages -l nl -l de -l fr -l es -l it
python manage.py compilemessages
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Activate `.venv` — run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` |
| Static files not loading | Run `python manage.py collectstatic` |
| Database errors on start | Run `python manage.py migrate` |
| Email bounce notifications | Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in development |
| Stripe webhook failures | Check `STRIPE_WEBHOOK_SECRET` matches your Stripe dashboard |
| Media files not serving | Ensure `MEDIA_ROOT` directory exists and is writable |
| Tailwind styles missing | Run `npx tailwindcss -i static/css/input.css -o static/css/output.css` |

---

## Support

If you encounter issues not covered here:

| Channel | Details |
|---|---|
| **Support** | https://djangozen.com/support/ |
| **Documentation** | https://docs.djangozen.com/apexforge |
| **Bug Reports** | https://github.com/djangozen/apexforge/issues |
| **Business Hours** | Monday – Friday, 09:00 – 18:00 CET |

Response times are based on your licence tier — see [LICENSE.md](LICENSE.md) for details.

---

**© 2026 DjangoZen. All rights reserved.**
