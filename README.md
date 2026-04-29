# ApexForge — Free / Community Edition

**Sport management platform for clubs, academies, and teams**
**Vendor:** [DjangoZen](https://djangozen.com)  ·  **Version:** 1.0.0

![ApexForge — Sport Management Platform](docs/images/0_hero.png)

---

## About

ApexForge is a Django-based sport management platform for clubs, coaches, athletes, scouts, and sport entrepreneurs. This is the **Free / Community Edition** — a fully working application you can run locally to evaluate, learn from, or use for non-commercial purposes.

For commercial use, multi-club deployment, the **Fan Portal**, white-label rights, and priority support, see the **[Pro Edition on djangozen.com →](https://djangozen.com/saas/product/apexforge-pro/)**.

---

## Demo

The repository ships with a pre-populated `db.sqlite3` so you can log in immediately after starting the server:

| Role | Email | Password |
|---|---|---|
| Manager | `manager@apexforge.com` | `demo123` |

---

## Quick Start

```bash
git clone https://github.com/DjangoZenDev/apexforge.git
cd apexforge
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver
```

Then open **http://127.0.0.1:8000** and log in with the credentials above. Full step-by-step in [INSTALLATION.md](INSTALLATION.md).

---

## What's Included (18 Modules)

| Module | Purpose |
|---|---|
| `core` | Branding, dashboard, notifications, global search |
| `accounts` | Custom user model, roles, profiles |
| `teams` | Teams, rosters, seasons, divisions |
| `players` | Athlete profiles, stats, performance |
| `events` | Calendar, fixtures, training |
| `scouting` | Talent database, watchlist |
| `finance` | Budget, shop, Stripe checkout |
| `marketing` | News, sponsor portal |
| `medical` | Injuries, medical records |
| `contracts` | Contract management |
| `staff` | Staff profiles, tasks |
| `tournaments` | Tournament brackets |
| `academy` | Youth and academy teams |
| `inventory` | Equipment management |
| `videos` | Video uploads |
| `organizations` | Club structure |
| `insights` | Analytics, KPIs |
| `admin` | Enhanced Django admin |

---

## Screenshots

### Dashboard
![Dashboard](docs/images/1_dashboard.png)

### Players
![Players](docs/images/2_players.png)

### Finance
![Finance](docs/images/3_finance.png)

### Fan Portal & Tickets *(Pro Edition only)*
![Fan tickets](docs/images/7_tickets.png)

---

## What's in Pro (not in this edition)

- 🎟️ **Fan Portal** — ticketing, loyalty points, fan engagement
- 🏢 **Multi-tenant / multi-club** support
- 🎨 **White-label rights** — sell as your own SaaS
- 📊 **Advanced analytics + PDF / Excel exports**
- 🔧 **Priority email support** (24–48h)
- 🚀 **Lifetime updates**

[See full feature comparison and pricing →](https://djangozen.com/saas/product/apexforge-pro/)

---

## Tech Stack

Django 5.2 LTS · Python 3.12+ · Tailwind CSS · HTMX · Alpine.js · SQLite (dev) / PostgreSQL (prod) · Stripe · Chart.js

---

## License

This edition is released under a **source-available licence** — see [LICENSE.md](LICENSE.md).

In short: free for evaluation, learning, and non-commercial self-hosting. Commercial / SaaS / multi-deployment use requires a Pro license.

---

## Support

| Channel | Where |
|---|---|
| Bug reports | [GitHub Issues](https://github.com/DjangoZenDev/apexforge/issues) |
| Pro purchase & sales | https://djangozen.com/saas/product/apexforge-pro/ |
| Documentation | https://djangozen.com/docs/apexforge/ |

---

**© 2026 DjangoZen** — Built for champions.
