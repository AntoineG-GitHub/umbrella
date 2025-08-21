from django.test import TestCase
from datetime import date
from decimal import Decimal
import datetime
from transactions.models import Transaction, CustomUser
from django.contrib.auth import get_user_model
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot
from portfolio_valuation.src.valuation_service import ValuationService
from data_ingestion.models import HistoricalPrice


class ValuationServiceTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username="user1", password="pass")
        self.user2 = CustomUser.objects.create_user(username="user2", password="pass")

        # Day 1: user1 deposits 1000
        Transaction.objects.create(
            type="deposit",
            user=self.user1,
            date=date(2025, 4, 7),
            amount=Decimal("1000.00"),
        )

        # Day 2: user2 deposits 500
        Transaction.objects.create(
            type="deposit",
            user=self.user2,
            date=date(2025, 4, 8),
            amount=Decimal("500.00"),
        )

        # Day 3: user1 deposits another 250
        Transaction.objects.create(
            type="deposit",
            user=self.user1,
            date=date(2025, 4, 9),
            amount=Decimal("250.00"),
        )

    def test_total_units_across_days(self):
        dates = [date(2025, 4, 7), date(2025, 4, 8), date(2025, 4, 9)]

        for d in dates:
            service = ValuationService(d)
            service.compute()

        # Day 1: user1 deposits 1000 → 1000 units at NAV=1
        snap1 = DailyPortfolioSnapshot.objects.get(date=date(2025, 4, 7))
        self.assertEqual(snap1.total_units, Decimal("1000.00000000"))

        # Day 2: user2 deposits 500 → NAV=1 → +500 units = 1500
        snap2 = DailyPortfolioSnapshot.objects.get(date=dates[1])
        self.assertEqual(snap2.total_units, Decimal("1500.00000000"))

        # Day 3: user1 deposits 250 → NAV=1 → +250 units = 1750
        snap3 = DailyPortfolioSnapshot.objects.get(date=dates[2])
        self.assertEqual(snap3.total_units, Decimal("1750.00000000"))


User = get_user_model()


class NAVComputationTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create(username="testuser")

        # Set base date
        self.day1 = datetime.date(2025, 4, 21)
        self.day2 = datetime.date(2025, 4, 22)

        # Day 1: User deposits 1000 EUR
        Transaction.objects.create(
            type="deposit",
            user=self.user,
            date=self.day1,
            amount=Decimal("1000.00"),
        )

        # Set portfolio price (say portfolio buys 10 shares of AAPL at 100 EUR each)
        Transaction.objects.create(
            type="buy",
            user=None,
            date=self.day1,
            amount=Decimal("1000.00"),
            ticker="AAPL",
            shares=Decimal("10"),
        )

        HistoricalPrice.objects.create(
            ticker="AAPL",
            date=self.day1,
            close_euro=Decimal("100.00")
        )

        # Day 2: No new deposit, price of AAPL rises to 120 EUR
        HistoricalPrice.objects.create(
            ticker="AAPL",
            date=self.day2,
            close_euro=Decimal("120.00")
        )

    def test_nav_per_unit_computation(self):
        # Compute NAV for Day 1
        ValuationService(self.day1).compute()
        snapshot_day1 = DailyPortfolioSnapshot.objects.get(date=self.day1)

        self.assertEqual(snapshot_day1.total_value, Decimal("1000.00"))
        self.assertEqual(snapshot_day1.nav_per_unit, Decimal("1.0"))
        self.assertEqual(snapshot_day1.total_units, Decimal("1000.00000000"))

        # Compute NAV for Day 2
        ValuationService(self.day2).compute()
        snapshot_day2 = DailyPortfolioSnapshot.objects.get(date=self.day2)

        self.assertEqual(snapshot_day2.total_value, Decimal("1200.00"))
        self.assertEqual(snapshot_day2.total_units, Decimal("1000.00000000"))
        self.assertEqual(snapshot_day2.nav_per_unit, Decimal("1.20000000"))


class FeeHandlingTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = CustomUser.objects.create_user(username="user1", password="pass")
        self.user2 = CustomUser.objects.create_user(username="user2", password="pass")
        
        # Set base dates
        self.day1 = date(2025, 4, 21)
        self.day2 = date(2025, 4, 22)
        self.day3 = date(2025, 4, 23)
        
        # Day 1: Initial deposits
        Transaction.objects.create(
            type="deposit",
            user=self.user1,
            date=self.day1,
            amount=Decimal("1000.00"),
        )
        Transaction.objects.create(
            type="deposit",
            user=self.user2,
            date=self.day1,
            amount=Decimal("1000.00"),
        )
        
        # Day 1: Buy AAPL shares
        Transaction.objects.create(
            type="buy",
            user=None,
            date=self.day1,
            amount=Decimal("1800.00"),
            ticker="AAPL",
            shares=Decimal("10"),
        )
        
        # Set up historical prices
        HistoricalPrice.objects.create(
            ticker="AAPL",
            date=self.day1,
            close_euro=Decimal("100.00")
        )
        HistoricalPrice.objects.create(
            ticker="AAPL",
            date=self.day2,
            close_euro=Decimal("100.00")
        )
        HistoricalPrice.objects.create(
            ticker="AAPL",
            date=self.day3,
            close_euro=Decimal("100.00")
        )

    def test_fee_impact_on_portfolio(self):
        # Day 1: Initial setup
        ValuationService(self.day1).compute()
        snapshot_day1 = DailyPortfolioSnapshot.objects.get(date=self.day1)
        
        # Verify initial state
        self.assertEqual(snapshot_day1.total_value, Decimal("1000.00"))
        self.assertEqual(snapshot_day1.total_units, Decimal("2000.00000000"))
        self.assertEqual(snapshot_day1.nav_per_unit, Decimal("1.0"))
        
        # Day 2: Add a fee
        Transaction.objects.create(
            type="fee",
            user=None,
            date=self.day2,
            amount=Decimal("50.00"),
            description="Management fee"
        )
        
        ValuationService(self.day2).compute()
        snapshot_day2 = DailyPortfolioSnapshot.objects.get(date=self.day2)
        
        # Verify fee impact
        self.assertEqual(snapshot_day2.total_value, Decimal("950.00"))  # 1000 - 50 fee
        self.assertEqual(snapshot_day2.total_units, Decimal("2000.00000000"))  # Units unchanged
        self.assertEqual(snapshot_day2.nav_per_unit, Decimal("0.47500000"))  # 950/2000
        
        # Verify user share snapshots
        user1_snapshot = UserShareSnapshot.objects.get(date=self.day2, user_id=self.user1.id)
        user2_snapshot = UserShareSnapshot.objects.get(date=self.day2, user_id=self.user2.id)
        
        # Each user should have 1000 units, worth 475 EUR each (950/2)
        self.assertEqual(user1_snapshot.units_held, Decimal("1000.00000000"))
        self.assertEqual(user2_snapshot.units_held, Decimal("1000.00000000"))
        self.assertEqual(user1_snapshot.value_held, Decimal("475.00"))
        self.assertEqual(user2_snapshot.value_held, Decimal("475.00"))
        
        # Day 3: Add another fee and verify cumulative impact
        Transaction.objects.create(
            type="fee",
            user=None,
            date=self.day3,
            amount=Decimal("25.00"),
            description="Performance fee"
        )
        
        ValuationService(self.day3).compute()
        snapshot_day3 = DailyPortfolioSnapshot.objects.get(date=self.day3)
        
        # Verify cumulative fee impact
        self.assertEqual(snapshot_day3.total_value, Decimal("925.00"))  # 1000 - 50 - 25 fees
        self.assertEqual(snapshot_day3.total_units, Decimal("2000.00000000"))  # Units still unchanged
        self.assertEqual(snapshot_day3.nav_per_unit, Decimal("0.46250000"))  # 925/2000
        
        # Verify final user positions
        user1_snapshot = UserShareSnapshot.objects.get(date=self.day3, user_id=self.user1.id)
        user2_snapshot = UserShareSnapshot.objects.get(date=self.day3, user_id=self.user2.id)
        
        # Each user should have 1000 units, worth 462.50 EUR each (925/2)
        self.assertEqual(user1_snapshot.units_held, Decimal("1000.00000000"))
        self.assertEqual(user2_snapshot.units_held, Decimal("1000.00000000"))
        self.assertEqual(user1_snapshot.value_held, Decimal("462.50"))
        self.assertEqual(user2_snapshot.value_held, Decimal("462.50"))
 