"""Seed Season records up to 2027/28 and mark 2026/27 as current."""
import datetime
from django.db import migrations


SEASONS = [
    # (name, start_date, end_date, is_current)
    ("2025/26", datetime.date(2025, 7, 1), datetime.date(2026, 6, 30), False),
    ("2026/27", datetime.date(2026, 7, 1), datetime.date(2027, 6, 30), True),
    ("2027/28", datetime.date(2027, 7, 1), datetime.date(2028, 6, 30), False),
]


def seed_seasons(apps, schema_editor):
    Season = apps.get_model("teams", "Season")
    # Un-mark any previously current season
    Season.objects.filter(is_current=True).update(is_current=False)
    for name, start, end, current in SEASONS:
        Season.objects.get_or_create(
            name=name,
            defaults={"start_date": start, "end_date": end, "is_current": current},
        )
    # Ensure exactly one is marked current
    Season.objects.filter(name="2026/27").update(is_current=True)


def reverse_seed(apps, schema_editor):
    pass  # leave the data in place on rollback


class Migration(migrations.Migration):
    dependencies = [
        ("teams", "0002_add_club_fk"),
    ]

    operations = [
        migrations.RunPython(seed_seasons, reverse_seed),
    ]
