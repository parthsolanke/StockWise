from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'timestamp'], name='unique_stock_price')
        ]

    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"

