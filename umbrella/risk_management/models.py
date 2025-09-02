from django.db import models

class VARComputation(models.Model):
    date = models.DateField(unique=True)
    var_95_1day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)  
    var_95_1day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    var_99_1day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True) 
    var_99_1day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True) 
    expected_shortfall_95_1day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    expected_shortfall_95_1day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True) 
    expected_shortfall_99_1day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    expected_shortfall_99_1day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    var_95_5day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)  
    var_95_5day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    var_99_5day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)  
    var_99_5day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expected_shortfall_95_5day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True) 
    expected_shortfall_95_5day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expected_shortfall_99_5day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    expected_shortfall_99_5day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    var_95_10day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)  
    var_95_10day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    var_99_10day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)  
    var_99_10day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expected_shortfall_95_10day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True) 
    expected_shortfall_95_10day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expected_shortfall_99_10day = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    expected_shortfall_99_10day_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"VAR Computation for {self.date}"
