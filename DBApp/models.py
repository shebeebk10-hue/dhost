from django.db import models

from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=100)
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
   


class Invoice(models.Model):

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    invoice_number = models.CharField(max_length=100)

    date = models.DateField()

    item_name = models.CharField(max_length=200)

    qty = models.IntegerField()

    weight = models.DecimalField(max_digits=10, decimal_places=2)

    rate = models.DecimalField(max_digits=10, decimal_places=2)

    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # NEW
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # NEW
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # FINAL BALANCE
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.invoice_number


        


