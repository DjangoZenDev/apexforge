"""
Management command: python manage.py seed_demo
Creates demo data for all modules.
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed the database with demo data for ApexForge"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing data first")

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        self.stdout.write(self.style.WARNING("Seeding demo data..."))

        branding = self._seed_branding()
        users    = self._seed_users()
        seasons  = self._seed_seasons()
        divisions = self._seed_divisions()
        teams    = self._seed_teams(seasons, divisions, users)
        players  = self._seed_players()
        self._seed_rosters(teams, players, seasons)
        events   = self._seed_events(teams, users)
        self._seed_tickets(events)
        self._seed_finance(teams, seasons, users)
        self._seed_marketing(users)
        self._seed_scouting(players, users)

        self.stdout.write(self.style.SUCCESS("[OK] Demo data seeded successfully!"))
        self.stdout.write("")
        self.stdout.write("Default login credentials:")
        self.stdout.write("  Super Admin:  admin@apexforge.com   / admin123")
        self.stdout.write("  Club Owner:   owner@apexforge.com   / demo123")
        self.stdout.write("  Manager:      manager@apexforge.com / demo123")
        self.stdout.write("  Coach:        coach@apexforge.com   / demo123")
        self.stdout.write("  Player:       player@apexforge.com  / demo123")
        self.stdout.write("  Scout:        scout@apexforge.com   / demo123")
        self.stdout.write("  Fan (Silver): fan@apexforge.com     / demo123")

    def _clear_data(self):
        from accounts.models import User
        from teams.models import Team, Season, Division, Roster
        from players.models import Player, PlayerStats, InjuryLog
        from events.models import Event
        from finance.models import Transaction, Budget, Sponsorship, Product
        from marketing.models import NewsPost
        from scouting.models import ScoutReport, TalentProfile

        models_to_clear = [
            ScoutReport, TalentProfile, NewsPost, Transaction, Budget,
            Sponsorship, Product, Event, Roster, Player, Team, Division, Season,
        ]
        for model in models_to_clear:
            model.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Cleared existing data.")

    def _seed_branding(self):
        from core.models import ClubBranding
        branding = ClubBranding.get_solo()
        branding.name = "ApexForge FC"
        branding.tagline = "Forge Champions, Build Legacies"
        branding.founded_year = 1985
        branding.city = "Amsterdam"
        branding.country = "Netherlands"
        branding.website = "https://apexforge.example.com"
        branding.email = "info@apexforge.example.com"
        branding.twitter = "@ApexForgeFC"
        branding.instagram = "@apexforgefc"
        branding.save()
        return branding

    def _seed_users(self):
        from accounts.models import User
        users = {}
        user_data = [
            ("admin@apexforge.com",   "Admin",   "User",    User.Role.SUPER_ADMIN,  True,  True,  "admin123"),
            ("owner@apexforge.com",   "James",   "Sterling",User.Role.CLUB_OWNER,   False, False, "demo123"),
            ("manager@apexforge.com", "Thomas",  "Wright",  User.Role.MANAGER,      False, False, "demo123"),
            ("coach@apexforge.com",   "Carlos",  "Santos",  User.Role.COACH,        False, False, "demo123"),
            ("player@apexforge.com",  "Marcus",  "Johnson", User.Role.ATHLETE,      False, False, "demo123"),
            ("scout@apexforge.com",   "Elena",   "Fischer", User.Role.SCOUT,        False, False, "demo123"),
            ("fan@apexforge.com",     "Sophie",  "Laurent", User.Role.FAN_INVESTOR, False, False, "demo123"),
        ]
        for email, first, last, role, is_superuser, is_staff, pwd in user_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first, "last_name": last, "role": role,
                    "is_superuser": is_superuser, "is_staff": is_staff or is_superuser,
                },
            )
            if created:
                user.set_password(pwd)
                user.save()
            users[role] = user

        # Ensure FanProfile exists for the fan user so they can skip the edit form
        from fans.models import FanProfile, MembershipTier
        fan_user = users.get(User.Role.FAN_INVESTOR)
        if fan_user:
            FanProfile.objects.get_or_create(
                user=fan_user,
                defaults={
                    "phone": "+31 6 12345678",
                    "bio": "Die-hard ApexForge supporter since day one!",
                    "loyalty_points": 750,
                    "tier": MembershipTier.SILVER,
                    "newsletter_opt_in": True,
                },
            )

        self.stdout.write("  [OK] Users")
        return users

    def _seed_seasons(self):
        from teams.models import Season
        seasons = []
        for name, start, end, current in [
            ("2024/25", date(2024, 8, 1), date(2025, 5, 31), True),
            ("2023/24", date(2023, 8, 1), date(2024, 5, 31), False),
            ("2022/23", date(2022, 8, 1), date(2023, 5, 31), False),
        ]:
            s, _ = Season.objects.get_or_create(name=name, defaults={"start_date": start, "end_date": end, "is_current": current})
            seasons.append(s)
        self.stdout.write("  [OK] Seasons")
        return seasons

    def _seed_divisions(self):
        from teams.models import Division
        divs = []
        for name, level, sport in [
            ("Premier League", 1, "football"),
            ("Championship",   2, "football"),
            ("League One",     3, "football"),
            ("NBA",            1, "basketball"),
            ("D-League",       2, "basketball"),
        ]:
            d, _ = Division.objects.get_or_create(name=name, defaults={"level": level, "sport": sport})
            divs.append(d)
        self.stdout.write("  [OK] Divisions")
        return divs

    def _seed_teams(self, seasons, divisions, users):
        from teams.models import Team
        team_data = [
            ("ApexForge FC",    "AFC",  "football", 0, 0),
            ("Forge Youth",     "FYC",  "football", 0, 2),
            ("ApexForge Women", "AFW",  "football", 0, 1),
            ("Apex Ballers",    "AB",   "basketball", 3, 3),
        ]
        teams = []
        for name, short, sport, div_idx, season_idx in team_data:
            t, _ = Team.objects.get_or_create(
                name=name,
                defaults={
                    "short_name": short, "sport": sport,
                    "division": divisions[div_idx] if div_idx < len(divisions) else None,
                    "season": seasons[season_idx] if season_idx < len(seasons) else None,
                    "home_venue": "Apex Arena", "city": "Amsterdam", "country": "Netherlands",
                    "founded_year": 1985 + len(teams) * 5,
                    "manager": users.get("manager"),
                    "coach": users.get("coach"),
                    "status": Team.Status.ACTIVE,
                    "colors": "Emerald/Amber",
                },
            )
            teams.append(t)
        self.stdout.write("  [OK] Teams")
        return teams

    def _seed_players(self):
        from players.models import Player
        player_data = [
            ("Marcus Johnson",    "Forward",    "American",  date(1998, 3, 15), "football", 75, 180, 78, Decimal("2500000")),
            ("Lucas Silva",       "Midfielder", "Brazilian", date(1999, 7, 22), "football", 8,  175, 72, Decimal("1800000")),
            ("Johan Berg",        "Defender",   "Swedish",   date(1997, 11, 5), "football", 4,  185, 82, Decimal("1200000")),
            ("Antoine Dubois",    "Goalkeeper", "French",    date(1996, 1, 30), "football", 1,  190, 87, Decimal("900000")),
            ("Diego Ramirez",     "Midfielder", "Spanish",   date(2000, 6, 18), "football", 10, 172, 68, Decimal("3000000")),
            ("Kai Müller",        "Defender",   "German",    date(1998, 9, 12), "football", 5,  183, 80, Decimal("1500000")),
            ("Oliver Thompson",   "Forward",    "English",   date(2001, 4, 25), "football", 9,  177, 74, Decimal("4000000")),
            ("Alessandro Rossi",  "Midfielder", "Italian",   date(1999, 8, 3),  "football", 7,  174, 70, Decimal("2200000")),
            ("Arjun Patel",       "Forward",    "Indian",    date(2002, 2, 14), "football", 11, 170, 67, Decimal("800000")),
            ("Ryan O'Brien",      "Defender",   "Irish",     date(1997, 5, 28), "football", 3,  182, 79, Decimal("1100000")),
            ("Yusuf Özkan",       "Midfielder", "Turkish",   date(2000, 12, 8), "football", 6,  176, 73, Decimal("1600000")),
            ("Hiroshi Tanaka",    "Forward",    "Japanese",  date(2001, 10, 19),"football", 22, 168, 65, Decimal("700000")),
        ]
        players = []
        for name, pos, nat, dob, sport, jersey, height, weight, value in player_data:
            p, _ = Player.objects.get_or_create(
                full_name=name,
                defaults={
                    "position": pos, "nationality": nat, "date_of_birth": dob,
                    "sport": sport, "jersey_number": jersey,
                    "height_cm": height, "weight_kg": weight,
                    "market_value": value, "status": Player.Status.ACTIVE,
                    "contract_until": date(2026, 6, 30),
                    "preferred_foot": random.choice(["left", "right"]),
                },
            )
            players.append(p)
        self.stdout.write("  [OK] Players")
        return players

    def _seed_rosters(self, teams, players, seasons):
        from teams.models import Roster
        main_team = teams[0]
        season = seasons[0]
        for i, player in enumerate(players):
            Roster.objects.get_or_create(
                team=main_team, player=player, season=season,
                defaults={
                    "jersey_number": player.jersey_number,
                    "position": player.position,
                    "is_captain": i == 0,
                    "is_active": True,
                    "joined_date": date(2024, 7, 1),
                },
            )
        self.stdout.write("  [OK] Rosters")

    def _seed_events(self, teams, users):
        from events.models import Event, Fixture
        today = timezone.now().date()
        team = teams[0]
        created_by = users.get("manager")

        event_data = [
            (f"vs FC Amsterdam", "fixture", today + timedelta(days=7), True, "FC Amsterdam"),
            (f"Training Session", "training", today + timedelta(days=2), True, ""),
            (f"vs Rotterdam FC", "fixture", today + timedelta(days=14), False, "Rotterdam FC"),
            (f"Pre-season friendly", "fixture", today - timedelta(days=10), True, "Ajax Youth"),
            (f"Cup Match — Quarter Final", "fixture", today + timedelta(days=21), True, "PSV"),
            (f"Tactical Training", "training", today + timedelta(days=4), True, ""),
            (f"Team Meeting", "meeting", today + timedelta(days=1), True, ""),
            (f"Summer Cup 2024", "tournament", today + timedelta(days=30), True, ""),
        ]
        events = []
        for title, etype, edate, is_home, opponent in event_data:
            ev, _ = Event.objects.get_or_create(
                title=title, team=team,
                defaults={
                    "event_type": etype, "start_date": edate, "is_home": is_home,
                    "opponent": opponent, "venue": "Apex Arena" if is_home else f"{opponent} Stadium",
                    "status": Event.Status.COMPLETED if edate < today else Event.Status.SCHEDULED,
                    "created_by": created_by,
                },
            )
            if etype == "fixture":
                Fixture.objects.get_or_create(
                    event=ev,
                    defaults={
                        "home_score": random.randint(0, 4) if ev.status == "completed" else None,
                        "away_score": random.randint(0, 3) if ev.status == "completed" else None,
                        "competition": "Premier League",
                    },
                )
            events.append(ev)
        self.stdout.write("  [OK] Events")
        return events

    def _seed_tickets(self, events):
        from fans.models import TicketCategory, Ticket

        # Ticket categories
        categories_data = [
            ("General Admission", Decimal("29.99"), "blue",   ""),
            ("VIP",               Decimal("89.99"), "amber",  "Lounge access\nPre-match buffet\nExclusive programme"),
            ("Platinum",          Decimal("149.99"), "violet", "Lounge access\nPre-match buffet\nMeet the players\nSigned shirt"),
        ]
        cats = {}
        for name, price, color, perks in categories_data:
            cat, _ = TicketCategory.objects.get_or_create(
                name=name,
                defaults={"base_price": price, "color": color, "perks": perks, "is_active": True},
            )
            cats[name] = cat

        # Only create tickets for upcoming fixture events
        upcoming = [ev for ev in events if ev.status == "scheduled" and ev.event_type == "fixture"]
        for event in upcoming[:3]:  # cap at 3 events
            for cat_name, qty, row_prefix in [
                ("General Admission", 10, "GA"),
                ("VIP", 4, "VIP"),
                ("Platinum", 2, "PLAT"),
            ]:
                cat = cats[cat_name]
                existing = Ticket.objects.filter(event=event, category=cat).count()
                needed = qty - existing
                if needed > 0:
                    Ticket.objects.bulk_create([
                        Ticket(
                            event=event, category=cat,
                            seat_row=row_prefix,
                            seat_number=str(existing + i + 1),
                            status=Ticket.Status.AVAILABLE,
                        )
                        for i in range(needed)
                    ])
        self.stdout.write("  [OK] Ticket categories & tickets")

    def _seed_finance(self, teams, seasons, users):
        from finance.models import BudgetCategory, Budget, Transaction, Sponsorship, Investment, Product
        from django.utils.text import slugify

        # Categories
        cats = {}
        for name, color in [
            ("Player Wages", "#ef4444"), ("Operations", "#f59e0b"),
            ("Transfer Fees", "#8b5cf6"), ("Equipment", "#3b82f6"),
            ("Marketing", "#06b6d4"), ("Ticket Sales", "#10b981"),
            ("Merchandise", "#f97316"), ("Sponsorship", "#6366f1"),
        ]:
            c, _ = BudgetCategory.objects.get_or_create(name=name, defaults={"color": color})
            cats[name] = c

        # Budget
        Budget.objects.get_or_create(
            name="Main Budget 2024/25",
            defaults={
                "season": seasons[0], "team": teams[0],
                "category": cats["Operations"], "amount": Decimal("5000000"),
                "created_by": users.get("club_owner"),
            },
        )

        # Transactions
        today = timezone.now().date()
        tx_data = [
            ("Match Day Revenue", "income", 125000, -7, "Ticket Sales"),
            ("Player Wages — March", "expense", 210000, -30, "Player Wages"),
            ("Kit Deal", "income", 50000, -14, "Merchandise"),
            ("Away Travel", "expense", 8500, -5, "Operations"),
            ("Training Equipment", "expense", 12000, -20, "Equipment"),
            ("Shirt Sales", "income", 35000, -10, "Merchandise"),
            ("Stadium Maintenance", "expense", 18000, -25, "Operations"),
            ("Transfer Fee — Silva", "expense", 1500000, -60, "Transfer Fees"),
            ("TV Rights Q1", "income", 450000, -45, "Marketing"),
            ("Staff Payroll", "expense", 95000, -15, "Player Wages"),
            ("Corporate Event", "income", 22000, -3, "Marketing"),
            ("Medical Costs", "expense", 7500, -8, "Operations"),
        ]
        for title, ttype, amount, days_ago, cat_name in tx_data:
            Transaction.objects.get_or_create(
                title=title,
                defaults={
                    "transaction_type": ttype,
                    "amount": Decimal(str(amount)),
                    "date": today + timedelta(days=days_ago),
                    "status": "completed",
                    "category": cats.get(cat_name),
                    "team": teams[0],
                    "created_by": users.get("manager"),
                },
            )

        # Sponsorships
        sponsor_data = [
            ("NexTech Solutions", "shirt", 500000),
            ("GreenEnergy Corp", "kit", 250000),
            ("SportsPro Media", "digital", 180000),
            ("City Bank Amsterdam", "official", 320000),
        ]
        for company, stype, amount in sponsor_data:
            Sponsorship.objects.get_or_create(
                company_name=company,
                defaults={
                    "sponsor_type": stype, "amount": Decimal(str(amount)),
                    "start_date": date(2024, 8, 1), "end_date": date(2025, 7, 31),
                    "status": "active",
                },
            )

        # Investments
        Investment.objects.get_or_create(
            investor_name="Premier Ventures",
            defaults={
                "investor_type": "equity", "amount": Decimal("2000000"),
                "date": date(2024, 1, 15), "equity_percentage": Decimal("15.0"),
                "is_active": True,
            },
        )

        # Products
        product_data = [
            ("Home Jersey 2024/25", "jersey", Decimal("79.99"), 200),
            ("Away Jersey 2024/25", "jersey", Decimal("74.99"), 150),
            ("Training Hoodie",     "training", Decimal("49.99"), 100),
            ("Club Scarf",          "accessories", Decimal("19.99"), 300),
            ("Signed Ball",         "memorabilia", Decimal("149.99"), 20),
            ("Club Cap",            "accessories", Decimal("24.99"), 180),
        ]
        for name, cat, price, stock in product_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "category": cat, "price": price, "stock": stock,
                    "is_active": True, "description": f"Official {name} from ApexForge FC.",
                },
            )

        self.stdout.write("  [OK] Finance data")

    def _seed_marketing(self, users):
        from marketing.models import NewsPost, Announcement
        from django.utils import timezone

        author = users.get("manager")
        posts = [
            ("ApexForge FC wins 3-1 in Season Opener", "match", True, True, "An incredible performance in our opening match."),
            ("New Signing: Diego Ramirez Joins the Club", "transfer", True, True, "We are delighted to welcome Diego Ramirez."),
            ("Youth Academy Launches New Programme", "youth", True, False, "Investing in the next generation of talent."),
            ("NexTech Solutions Renews Shirt Sponsorship", "sponsor", True, False, "Proud to announce a renewed partnership."),
            ("Community Day This Weekend", "community", True, False, "Join us for a fantastic community event."),
        ]
        for title, cat, published, featured, content in posts:
            NewsPost.objects.get_or_create(
                slug=slugify(title)[:300],
                defaults={
                    "title": title, "category": cat, "content": content,
                    "excerpt": content, "is_published": published,
                    "is_featured": featured, "author": author,
                    "published_at": timezone.now() if published else None,
                },
            )

        Announcement.objects.get_or_create(
            title="Welcome to ApexForge Platform!",
            defaults={
                "message": "Explore the full sports management platform. Check your dashboard for quick actions.",
                "level": "info", "is_active": True, "created_by": author,
            },
        )
        self.stdout.write("  [OK] Marketing data")

    def _seed_scouting(self, players, users):
        from scouting.models import ScoutReport, TalentProfile, Watchlist
        from django.core.validators import MaxValueValidator

        scout = users.get("scout")

        # Scouting reports for a few players
        for player in players[:4]:
            ScoutReport.objects.get_or_create(
                player=player, scout=scout, match_date=date(2024, 10, 15),
                defaults={
                    "venue": "Apex Arena", "opponent": "FC Amsterdam",
                    "technical": random.randint(6, 9),
                    "tactical": random.randint(5, 9),
                    "physical": random.randint(6, 9),
                    "mental": random.randint(6, 9),
                    "overall": round(Decimal(str(random.uniform(6.5, 9.0))), 1),
                    "strengths": "Strong positioning, excellent passing range.",
                    "weaknesses": "Needs improvement in aerial duels.",
                    "summary": "Outstanding performance. A key player to watch.",
                    "recommendation": "monitor",
                },
            )

        # Talent profiles
        talents = [
            ("Felix Andersson", date(2003, 5, 12), "Swedish", "Winger", "Malmö FF"),
            ("Nico Fernandez",  date(2004, 9, 3),  "Argentine", "Striker", "CA Talleres"),
            ("Ismail Traore",   date(2002, 11, 18), "Ivorian", "Midfielder", "Sporting Abidjan"),
            ("Chen Wei",        date(2003, 7, 7),   "Chinese", "Defender", "Shanghai FC"),
            ("Pedro Alves",     date(2002, 3, 25),  "Portuguese", "Forward", "Benfica B"),
        ]
        for name, dob, nat, pos, club in talents:
            TalentProfile.objects.get_or_create(
                full_name=name,
                defaults={
                    "date_of_birth": dob, "nationality": nat, "position": pos,
                    "current_club": club, "rating": random.randint(6, 9),
                    "status": random.choice(["prospect", "contacted", "monitor"]),
                    "notes": "Highly promising talent, recommend close monitoring.",
                    "added_by": scout,
                },
            )

        # Watchlist
        Watchlist.objects.get_or_create(
            owner=scout, name="Priority Targets",
            defaults={"notes": "Top targets for January window"},
        )
        self.stdout.write("  [OK] Scouting data")
