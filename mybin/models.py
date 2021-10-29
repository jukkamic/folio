from django.db import models

class Coin(models.Model):
    name = models.CharField(max_length=40, null=True, blank=True)
    symbol = models.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        super(Coin, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.symbol    


class Price(models.Model):
    coin = models.ForeignKey(Coin, on_delete= models.CASCADE, related_name="prices_coin")
    pair = models.ForeignKey(Coin, on_delete= models.CASCADE, related_name="prices_pair")
    price = models.FloatField()
    source_time = models.DateTimeField(null=True, blank=True)
    recorded_time = models.DateTimeField(auto_now_add=True)
    change24h = models.FloatField(null=True, blank=True)
    chartLink = models.URLField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(Price, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.coin.symbol + " " + str(self.price) + " " + self.coin.symbol + "/" + self.pair.symbol

class Balance(models.Model):
    coin = models.ForeignKey(Coin, on_delete= models.CASCADE, related_name="balances_coin")
    price = models.ForeignKey(Price, on_delete= models.CASCADE, related_name="balances_price", null=True, blank=True)
    amount = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(Balance, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.coin.symbol + " " + str(self.amount)
    
