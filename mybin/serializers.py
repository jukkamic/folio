from rest_framework import serializers
from mybin.models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('id', 'value_usdt', 'value_btc', 'btc_usdt', 'time')
