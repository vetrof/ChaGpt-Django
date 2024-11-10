from django.db import models

from django.db import models

class Shoe(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)  # Например, доступность товара

    def __str__(self):
        return self.name

