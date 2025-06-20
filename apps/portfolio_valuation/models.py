from django.db import models
from decimal import Decimal

class DailyPortfolioSnapshot(models.Model):
    date = models.DateField(unique=True)
    total_value = models.DecimalField(max_digits=20, decimal_places=2)  # in EUR
    total_units = models.DecimalField(max_digits=20, decimal_places=8)  # shares outstanding
    nav_per_unit = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("1.0"))
    gain_or_loss = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.0"))
    cash = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.0"))
    portfolio_total_value = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.0"))
    net_inflows = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.0"))


    def calculate_nav_per_unit(self):
        """
        Calculate the Net Asset Value (NAV) per unit.
        This method computes the NAV per unit by dividing the total value of the 
        portfolio by the total number of units. If the total number of units is zero, 
        the method returns 0 to avoid division by zero.
        Returns:
            float: The NAV per unit, or 0 if total_units is zero.
        """

        return self.total_value / self.total_units if self.total_units else 0


class UserShareSnapshot(models.Model):
    date = models.DateField()
    user_id = models.IntegerField()
    units_held = models.DecimalField(max_digits=20, decimal_places=8)
    value_held = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal("0.0"))

    class Meta:
        unique_together = ("date", "user_id")
